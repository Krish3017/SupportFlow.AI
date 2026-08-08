import time
import json
import sqlite3
from uuid import uuid4
from datetime import datetime
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAMES = {
    "intent_agent": "Intent Agent",
    "customer_intelligence_agent": "Customer Intelligence Agent",
    "priority_agent": "Priority Agent",
    "knowledge_agent": "Knowledge Agent",
    "resolution_agent": "Resolution Agent",
    "escalation_agent": "Escalation Agent",
}


def _get_db():
    import os
    db_path = os.getenv("DATABASE_PATH", "supportflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def link_contact_company_customer(contact_id: str, company_customer_id: str) -> None:
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE customers SET company_customer_id = ? WHERE id = ?",
            (company_customer_id, contact_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to link company customer {company_customer_id} to contact {contact_id}: {e}")
        conn.rollback()
    finally:
        conn.close()


def ensure_contact(contact_id: str, channel: str, name: Optional[str] = None) -> str:
    if not contact_id or contact_id == "anonymous":
        contact_id = f"anon_{channel}_{uuid4().hex[:6]}"

    if "@" in contact_id:
        email = contact_id
    else:
        email = f"{contact_id}@{channel}.supportflow"

    conn = _get_db()
    company_cust_id = None
    try:
        existing = conn.execute("SELECT id, email, company_customer_id FROM customers WHERE id = ?", (contact_id,)).fetchone()

        if existing:
            contact_id = existing['id']
            email = existing['email'] or email
            company_cust_id = existing['company_customer_id']
            conn.execute(
                "UPDATE customers SET last_interaction = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), contact_id)
            )
        else:
            existing_email = conn.execute("SELECT id, email, company_customer_id FROM customers WHERE email = ?", (email,)).fetchone()
            if existing_email:
                contact_id = existing_email['id']
                company_cust_id = existing_email['company_customer_id']
                conn.execute(
                    "UPDATE customers SET last_interaction = ? WHERE id = ?",
                    (datetime.utcnow().isoformat(), contact_id)
                )
            else:
                now = datetime.utcnow().isoformat()
                conn.execute("""
                    INSERT INTO customers (id, name, email, tier, sentiment, joined_date, last_interaction, total_conversations, resolved_conversations)
                    VALUES (?, ?, ?, 'standard', 'neutral', ?, ?, 0, 0)
                """, (contact_id, name or contact_id, email, now, now))

        channel_id = f"{channel}:{contact_id}"
        conn.execute("""
            INSERT OR IGNORE INTO contact_channels (contact_id, channel_type, channel_identifier, verified, created_at)
            VALUES (?, ?, ?, 0, ?)
        """, (contact_id, channel, channel_id, datetime.utcnow().isoformat()))

        conn.commit()
    except Exception as e:
        logger.error(f"Contact persist failed: {e}")
        conn.rollback()
    finally:
        conn.close()

    # Attempt exact email company DB lookup if company_customer_id not linked
    if not company_cust_id and "@" in email and not email.endswith(".supportflow"):
        try:
            from company_data.service import CompanyDataService
            comp_res = CompanyDataService().get_customer_by_email(email)
            if comp_res.get("found") and comp_res.get("customer"):
                matched_id = comp_res["customer"]["customer_id"]
                link_contact_company_customer(contact_id, matched_id)
        except Exception as ex:
            logger.debug(f"Company customer lookup during ensure_contact skipped: {ex}")

    return contact_id


def get_or_create_conversation(contact_id: str, channel: str, session_token: str) -> str:
    conn = _get_db()
    try:
        existing = conn.execute("""
            SELECT id FROM conversations
            WHERE session_token = ? AND status NOT IN ('closed', 'archived')
            ORDER BY updated_at DESC LIMIT 1
        """, (session_token,)).fetchone()

        if existing:
            conn.close()
            return existing['id']

        conv_id = _gen_id("conv")
        now = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO conversations (id, contact_id, channel, status, started_at, updated_at, session_token)
            VALUES (?, ?, ?, 'active', ?, ?, ?)
        """, (conv_id, contact_id, channel, now, now, session_token))
        conn.commit()
        return conv_id
    except Exception as e:
        logger.error(f"Conversation creation failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def store_user_message(conversation_id: str, content: str) -> str:
    msg_id = _gen_id("msg")
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO messages (id, conversation_id, role, content, timestamp)
            VALUES (?, ?, 'user', ?, ?)
        """, (msg_id, conversation_id, content, now))
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"User message store failed: {e}")
        conn.rollback()
    finally:
        conn.close()
    return msg_id


def store_assistant_message(conversation_id: str, content: str, execution_id: str) -> str:
    msg_id = _gen_id("msg")
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO messages (id, conversation_id, role, content, timestamp, execution_id)
            VALUES (?, ?, 'assistant', ?, ?, ?)
        """, (msg_id, conversation_id, content, now, execution_id))
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Assistant message store failed: {e}")
        conn.rollback()
    finally:
        conn.close()
    return msg_id


def create_execution(message_id: str, conversation_id: str) -> str:
    exec_id = _gen_id("exec")
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO executions (id, message_id, conversation_id, status, started_at)
            VALUES (?, ?, ?, 'running', ?)
        """, (exec_id, message_id, conversation_id, now))
        conn.commit()
    except Exception as e:
        logger.error(f"Execution creation failed: {e}")
        conn.rollback()
    finally:
        conn.close()
    return exec_id


def complete_execution(execution_id: str, result: dict, duration: float):
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        escalated = 1 if result.get("escalate") else 0
        status = "completed"
        if result.get("_error"):
            status = "failed"

        conn.execute("""
            UPDATE executions SET
                status = ?,
                completed_at = ?,
                total_duration = ?,
                confidence = ?,
                intent = ?,
                sentiment = ?,
                priority = ?,
                escalated = ?
            WHERE id = ?
        """, (
            status, now, round(duration, 3),
            result.get("confidence"),
            result.get("intent"),
            result.get("sentiment"),
            result.get("priority"),
            escalated,
            execution_id
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Execution complete failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def record_execution_steps(execution_id: str, result: dict, message: str, duration: float):
    conn = _get_db()
    try:
        agent_sequence = [
            ("intent_agent", "Intent Agent", json.dumps({"intent": result.get("intent"), "sentiment": result.get("sentiment"), "confidence": result.get("confidence")})),
            ("customer_intelligence_agent", "Customer Intelligence Agent", json.dumps({"context": str(result.get("customer_context", ""))[:200]})),
            ("priority_agent", "Priority Agent", json.dumps({"priority": result.get("priority")})),
        ]

        if result.get("retrieved_context"):
            agent_sequence.append(("knowledge_agent", "Knowledge Agent", str(result.get("retrieved_context", ""))[:500]))

        agent_sequence.append(("resolution_agent", "Resolution Agent", (result.get("final_response", ""))[:200]))
        agent_sequence.append(("escalation_agent", "Escalation Agent", json.dumps({"escalate": result.get("escalate", False)})))

        now = datetime.utcnow().isoformat()
        step_duration = duration / len(agent_sequence) if agent_sequence else 0

        for order, (agent_id, agent_name, output) in enumerate(agent_sequence, 1):
            step_id = f"{execution_id}_step{order}"
            conn.execute("""
                INSERT OR IGNORE INTO execution_steps
                (id, execution_id, agent_id, agent_name, sequence_order, status, input_data, output_data, latency, cost, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, 'success', ?, ?, ?, 0.0, ?, ?)
            """, (
                step_id, execution_id, agent_id, agent_name, order,
                message[:200], output, round(step_duration, 3), now, now
            ))

        conn.commit()
    except Exception as e:
        logger.error(f"Execution steps recording failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_ticket_on_escalation(conversation_id: str, contact_id: str, result: dict) -> Optional[str]:
    if not result.get("escalate"):
        return None

    conn = _get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM tickets WHERE conversation_id = ? AND status != 'resolved'",
            (conversation_id,)
        ).fetchone()

        if existing:
            conn.close()
            return existing['id']

        ticket_id = _gen_id("TKT")
        now = datetime.utcnow().isoformat()
        subject = (result.get("customer_message") or result.get("intent") or "Escalated conversation")[:100]

        conn.execute("""
            INSERT INTO tickets (id, conversation_id, contact_id, subject, priority, status, created_at, updated_at, escalation_reason)
            VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?)
        """, (
            ticket_id, conversation_id, contact_id, subject,
            result.get("priority", "medium"), now, now,
            f"AI escalated: intent={result.get('intent')}, confidence={result.get('confidence')}"
        ))

        conn.execute("""
            UPDATE conversations SET status = 'escalated', updated_at = ? WHERE id = ?
        """, (now, conversation_id))

        conn.commit()
        return ticket_id
    except Exception as e:
        logger.error(f"Ticket creation failed: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def update_contact_stats(contact_id: str, result: dict):
    conn = _get_db()
    try:
        escalated = result.get("escalate", False)
        conn.execute("""
            UPDATE customers SET
                sentiment = COALESCE(?, sentiment),
                last_interaction = ?,
                total_conversations = total_conversations + 1,
                resolved_conversations = resolved_conversations + ?
            WHERE id = ?
        """, (
            result.get("sentiment"),
            datetime.utcnow().isoformat(),
            0 if escalated else 1,
            contact_id,
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Contact stats update failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def emit_activity(event_type: str, message: str, level: str = "info", metadata: Optional[dict] = None):
    conn = _get_db()
    try:
        conn.execute("""
            INSERT INTO activity_logs (type, level, message, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event_type, level, message,
            datetime.utcnow().isoformat(),
            json.dumps(metadata) if metadata else None,
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Activity log failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def resolve_conversation(conversation_id: str):
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("""
            UPDATE conversations SET status = 'resolved', resolved_at = ?, updated_at = ? WHERE id = ?
        """, (now, now, conversation_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Conversation resolve failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def close_conversation(conversation_id: str):
    conn = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("""
            UPDATE conversations SET status = 'closed', closed_at = ?, updated_at = ? WHERE id = ?
        """, (now, now, conversation_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Conversation close failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_conversation_messages(conversation_id: str) -> list:
    conn = _get_db()
    try:
        rows = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,)).fetchall()
        return [{"role": r['role'], "content": r['content']} for r in rows]
    finally:
        conn.close()


def persist_workflow_result(
    customer_id: str,
    session_id: str,
    channel: str,
    message: str,
    result: dict,
) -> str:
    start_time = time.time()

    contact_id = ensure_contact(customer_id, channel)
    conversation_id = get_or_create_conversation(contact_id, channel, session_id)
    user_msg_id = store_user_message(conversation_id, message)
    execution_id = create_execution(user_msg_id, conversation_id)

    duration = time.time() - start_time
    record_execution_steps(execution_id, result, message, duration)
    complete_execution(execution_id, result, duration)

    final_response = result.get("final_response", "")
    if final_response:
        store_assistant_message(conversation_id, final_response, execution_id)

    create_ticket_on_escalation(conversation_id, contact_id, result)
    update_contact_stats(contact_id, result)

    emit_activity(
        "conversation",
        f"[{channel.upper()}] {result.get('intent', 'unknown')} from {contact_id}",
        metadata={
            "conversation_id": conversation_id,
            "execution_id": execution_id,
            "channel": channel,
            "intent": result.get("intent"),
            "escalated": result.get("escalate", False),
        }
    )

    return conversation_id
