import time
import json
import psycopg
from uuid import uuid4
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.postgres import get_postgres_connection
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


def _get_db() -> psycopg.Connection:
    """
    Returns a PostgreSQL connection set to search_path supportflow, public.
    """
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO supportflow, public;")
    conn.commit()
    return conn


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def link_contact_company_customer(contact_id: str, company_customer_id: str) -> None:
    conn = _get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE supportflow.customers SET company_customer_id = %s WHERE id = %s",
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
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, company_customer_id FROM supportflow.customers WHERE id = %s", (contact_id,))
            existing = cur.fetchone()

            if existing:
                contact_id = existing['id']
                email = existing['email'] or email
                company_cust_id = existing['company_customer_id']
                cur.execute(
                    "UPDATE supportflow.customers SET last_interaction = %s WHERE id = %s",
                    (datetime.utcnow().isoformat(), contact_id)
                )
            else:
                cur.execute("SELECT id, email, company_customer_id FROM supportflow.customers WHERE LOWER(email) = LOWER(%s)", (email,))
                existing_email = cur.fetchone()
                if existing_email:
                    contact_id = existing_email['id']
                    company_cust_id = existing_email['company_customer_id']
                    cur.execute(
                        "UPDATE supportflow.customers SET last_interaction = %s WHERE id = %s",
                        (datetime.utcnow().isoformat(), contact_id)
                    )
                else:
                    now = datetime.utcnow().isoformat()
                    cur.execute("""
                        INSERT INTO supportflow.customers (id, name, email, tier, sentiment, joined_date, last_interaction, total_conversations, resolved_conversations)
                        VALUES (%s, %s, %s, 'standard', 'neutral', %s, %s, 0, 0)
                        ON CONFLICT (id) DO UPDATE SET last_interaction = EXCLUDED.last_interaction
                    """, (contact_id, name or contact_id, email, now, now))

            channel_id = f"{channel}:{contact_id}"
            cur.execute("""
                INSERT INTO supportflow.contact_channels (contact_id, channel_type, channel_identifier, verified, created_at)
                VALUES (%s, %s, %s, FALSE, %s)
                ON CONFLICT (contact_id, channel_type, channel_identifier) DO NOTHING
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
        with conn.cursor() as cur:
            # 1. Try finding active conversation by contact_id (Customer/Contact Priority)
            cur.execute("""
                SELECT id FROM supportflow.conversations
                WHERE contact_id = %s AND status NOT IN ('closed', 'archived')
                ORDER BY updated_at DESC LIMIT 1
            """, (contact_id,))
            existing = cur.fetchone()

            if existing:
                cur.execute(
                    "UPDATE supportflow.conversations SET session_token = %s, updated_at = %s WHERE id = %s",
                    (session_token, datetime.utcnow().isoformat(), existing['id'])
                )
                conn.commit()
                return existing['id']

            # 2. Fallback: try finding active conversation by session_token
            if session_token:
                cur.execute("""
                    SELECT id FROM supportflow.conversations
                    WHERE session_token = %s AND status NOT IN ('closed', 'archived')
                    ORDER BY updated_at DESC LIMIT 1
                """, (session_token,))
                existing_sess = cur.fetchone()

                if existing_sess:
                    conn.commit()
                    return existing_sess['id']

            conv_id = _gen_id("conv")
            now = datetime.utcnow().isoformat()
            cur.execute("""
                INSERT INTO supportflow.conversations (id, contact_id, channel, status, started_at, updated_at, session_token)
                VALUES (%s, %s, %s, 'active', %s, %s, %s)
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
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO supportflow.messages (id, conversation_id, role, content, timestamp)
                VALUES (%s, %s, 'user', %s, %s)
            """, (msg_id, conversation_id, content, now))
            cur.execute(
                "UPDATE supportflow.conversations SET updated_at = %s WHERE id = %s",
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
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO supportflow.messages (id, conversation_id, role, content, timestamp, execution_id)
                VALUES (%s, %s, 'assistant', %s, %s, %s)
            """, (msg_id, conversation_id, content, now, execution_id))
            cur.execute(
                "UPDATE supportflow.conversations SET updated_at = %s WHERE id = %s",
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
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO supportflow.executions (id, message_id, conversation_id, status, started_at)
                VALUES (%s, %s, %s, 'running', %s)
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
        escalated = True if result.get("escalate") else False
        status = "completed"
        if result.get("_error"):
            status = "failed"

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE supportflow.executions SET
                    status = %s,
                    completed_at = %s,
                    total_duration = %s,
                    confidence = %s,
                    intent = %s,
                    sentiment = %s,
                    priority = %s,
                    escalated = %s
                WHERE id = %s
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
            ("intent_agent", "Intent Agent", json.dumps({
                "intent": result.get("intent"),
                "sentiment": result.get("sentiment"),
                "confidence": result.get("confidence")
            })),
            ("customer_intelligence_agent", "Customer Intelligence Agent", json.dumps({
                "context": str(result.get("customer_context", ""))[:200]
            })),
            ("priority_agent", "Priority Agent", json.dumps({
                "priority": result.get("priority")
            })),
        ]

        knowledge_was_used = bool(result.get("retrieved_context"))
        if knowledge_was_used:
            agent_sequence.append((
                "knowledge_agent", "Knowledge Agent",
                str(result.get("retrieved_context", ""))[:500]
            ))

        agent_sequence.append((
            "resolution_agent", "Resolution Agent",
            (result.get("final_response", ""))[:200]
        ))
        agent_sequence.append((
            "escalation_agent", "Escalation Agent",
            json.dumps({"escalate": result.get("escalate", False)})
        ))

        n = len(agent_sequence)
        if knowledge_was_used:
            weights = [0.12, 0.10, 0.06, 0.18, 0.40, 0.14]
        else:
            weights = [0.14, 0.12, 0.07, 0.47, 0.20]

        if len(weights) != n:
            weights = [1.0 / n] * n

        now_ts = datetime.utcnow()

        with conn.cursor() as cur:
            for order, ((agent_id, agent_name, output), weight) in enumerate(zip(agent_sequence, weights), 1):
                step_latency = round(duration * weight, 3)
                step_started = now_ts.isoformat()
                step_completed = now_ts.isoformat()
                step_id = f"{execution_id}_step{order}"
                cur.execute("""
                    INSERT INTO supportflow.execution_steps
                    (id, execution_id, agent_id, agent_name, sequence_order, status,
                     input_data, output_data, latency, cost, started_at, completed_at)
                    VALUES (%s, %s, %s, %s, %s, 'success', %s, %s, %s, 0.0, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    step_id, execution_id, agent_id, agent_name, order,
                    message[:200], output, step_latency, step_started, step_completed
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM supportflow.tickets WHERE conversation_id = %s AND status != 'resolved'",
                (conversation_id,)
            )
            existing = cur.fetchone()

            if existing:
                return existing['id']

            ticket_id = _gen_id("TKT")
            now = datetime.utcnow().isoformat()
            subject = (result.get("customer_message") or result.get("intent") or "Escalated conversation")[:100]

            cur.execute("""
                INSERT INTO supportflow.tickets (id, conversation_id, contact_id, subject, priority, status, created_at, updated_at, escalation_reason)
                VALUES (%s, %s, %s, %s, %s, 'open', %s, %s, %s)
            """, (
                ticket_id, conversation_id, contact_id, subject,
                result.get("priority", "medium"), now, now,
                f"AI escalated: intent={result.get('intent')}, confidence={result.get('confidence')}"
            ))

            cur.execute("""
                UPDATE supportflow.conversations SET status = 'escalated', updated_at = %s WHERE id = %s
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
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE supportflow.customers SET
                    sentiment = COALESCE(%s, sentiment),
                    last_interaction = %s,
                    total_conversations = total_conversations + 1,
                    resolved_conversations = resolved_conversations + %s
                WHERE id = %s
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
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO supportflow.activity_logs (type, level, message, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s)
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
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE supportflow.conversations SET status = 'resolved', resolved_at = %s, updated_at = %s WHERE id = %s
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
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE supportflow.conversations SET status = 'closed', closed_at = %s, updated_at = %s WHERE id = %s
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
        with conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM supportflow.messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """, (conversation_id,))
            rows = cur.fetchall()
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
