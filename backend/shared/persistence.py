"""
Data Persistence Layer
Instruments the request lifecycle to persist all operational data.
Used by Chat, Telegram, and Email channels.
"""
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

# Track session→ticket mapping to avoid creating duplicates
_session_ticket_map: dict = {}


_schema_migrated = False

def _get_db():
    """Get database connection using same path as rest of app."""
    global _schema_migrated
    import os
    db_path = os.getenv("DATABASE_PATH", "supportflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    if not _schema_migrated:
        _ensure_schema(conn)
        _schema_migrated = True

    return conn

def _ensure_schema(conn):
    """Ensure all required columns exist. Safe to run multiple times."""
    # Add missing columns to customers table
    _add_column_if_missing(conn, "customers", "last_interaction", "TEXT")
    _add_column_if_missing(conn, "customers", "sentiment", "TEXT DEFAULT 'neutral'")
    _add_column_if_missing(conn, "customers", "total_tickets", "INTEGER DEFAULT 0")
    _add_column_if_missing(conn, "customers", "resolved_tickets", "INTEGER DEFAULT 0")
    _add_column_if_missing(conn, "customers", "avg_response_time", "REAL DEFAULT 0.0")
    _add_column_if_missing(conn, "customers", "interaction_frequency", "TEXT")
    _add_column_if_missing(conn, "customers", "joined_date", "TEXT")
    _add_column_if_missing(conn, "customers", "risk_score", "INTEGER DEFAULT 0")
    _add_column_if_missing(conn, "customers", "lifetime_value", "REAL DEFAULT 0.0")
    _add_column_if_missing(conn, "customers", "tags", "TEXT")
    _add_column_if_missing(conn, "customers", "tier", "TEXT DEFAULT 'standard'")
    _add_column_if_missing(conn, "customers", "name", "TEXT")
    conn.commit()

def _add_column_if_missing(conn, table: str, column: str, col_type: str):
    """Add column to table if it doesn't exist."""
    try:
        cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            logger.info(f"✓ Added column {table}.{column}")
    except Exception:
        pass


def ensure_customer(customer_id: str, channel: str, name: Optional[str] = None) -> str:
    """Find or create customer. Returns stable customer_id."""
    # For anonymous users, derive stable ID from channel
    if not customer_id or customer_id == "anonymous":
        customer_id = f"anon_{channel}"

    # Derive email from customer_id
    if "@" in customer_id:
        email = customer_id
    else:
        email = f"{customer_id}@{channel}.supportflow"

    conn = _get_db()
    try:
        # Check if customer exists by ID first
        existing = conn.execute("SELECT id FROM customers WHERE id = ?", (customer_id,)).fetchone()

        if existing:
            # Update last interaction
            conn.execute(
                "UPDATE customers SET last_interaction = ? WHERE id = ?",
                (datetime.now().isoformat(), customer_id)
            )
        else:
            # Check by email
            existing_email = conn.execute("SELECT id FROM customers WHERE email = ?", (email,)).fetchone()
            if existing_email:
                customer_id = existing_email['id']
                conn.execute(
                    "UPDATE customers SET last_interaction = ? WHERE id = ?",
                    (datetime.now().isoformat(), customer_id)
                )
            else:
                # Create new customer
                conn.execute("""
                    INSERT INTO customers (id, name, email, tier, sentiment, joined_date, last_interaction, total_tickets, resolved_tickets)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0)
                """, (
                    customer_id,
                    name or customer_id,
                    email,
                    'standard',
                    'neutral',
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ))

        conn.commit()
        logger.info(f"✓ Customer ensured: {customer_id}")
    except Exception as e:
        logger.error(f"✗ Customer persist failed: {e}")
        conn.rollback()
    finally:
        conn.close()

    return customer_id


def get_or_create_ticket(customer_id: str, channel: str, session_id: str, subject: str = "New conversation") -> str:
    """Get existing ticket for session or create new one."""
    # Check in-memory cache first
    if session_id in _session_ticket_map:
        return _session_ticket_map[session_id]

    ticket_id = f"TKT-{uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    conn = _get_db()
    try:
        conn.execute("""
            INSERT INTO tickets (id, subject, customer_id, priority, status, channel, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, subject[:100], customer_id, 'medium', 'new', channel, now, now))
        conn.commit()
        _session_ticket_map[session_id] = ticket_id
        logger.info(f"✓ Ticket created: {ticket_id}")
    except Exception as e:
        logger.error(f"✗ Ticket creation failed: {e}")
        conn.rollback()
    finally:
        conn.close()

    return ticket_id


def store_message(ticket_id: str, role: str, content: str, agent_type: Optional[str] = None):
    """Persist a message."""
    conn = _get_db()
    try:
        conn.execute("""
            INSERT INTO messages (ticket_id, role, content, timestamp, agent_type)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, role, content, datetime.now().isoformat(), agent_type))
        conn.commit()
        logger.info(f"✓ Message stored: {role} -> ticket {ticket_id}")
    except Exception as e:
        logger.error(f"✗ Message store failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def record_agent_steps(execution_id: str, ticket_id: str, session_id: str, result: dict, message: str, duration: float):
    """Record all agent execution steps from workflow result."""
    conn = _get_db()
    try:
        agent_sequence = [
            ("intent_agent", "Intent Agent", json.dumps({"intent": result.get("intent"), "sentiment": result.get("sentiment")})),
            ("customer_intelligence_agent", "Customer Intelligence Agent", json.dumps({"context": str(result.get("customer_context", ""))[:200]})),
            ("priority_agent", "Priority Agent", json.dumps({"priority": result.get("priority")})),
        ]

        if result.get("retrieved_context"):
            agent_sequence.append(("knowledge_agent", "Knowledge Agent", result.get("retrieved_context", "")[:200]))

        agent_sequence.append(("resolution_agent", "Resolution Agent", (result.get("final_response", ""))[:200]))
        agent_sequence.append(("escalation_agent", "Escalation Agent", json.dumps({"escalate": result.get("escalate", False)})))

        now = datetime.now().isoformat()
        step_duration = duration / len(agent_sequence) if agent_sequence else 0

        for order, (agent_id, agent_name, output) in enumerate(agent_sequence, 1):
            step_id = f"{execution_id}_{agent_id}"
            conn.execute("""
                INSERT OR IGNORE INTO agent_executions
                (id, ticket_id, session_id, agent_id, agent_name, status, input_data, output_data, latency, cost, error, started_at, completed_at, sequence_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step_id, ticket_id, session_id, agent_id, agent_name,
                'success', message[:200], output, round(step_duration, 3), 0.0, None,
                now, now, order
            ))

        conn.commit()
        logger.info(f"✓ {len(agent_sequence)} agent steps recorded for {ticket_id}")
    except Exception as e:
        logger.error(f"✗ Agent steps recording failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_ticket_from_result(ticket_id: str, result: dict):
    """Update ticket with workflow results."""
    conn = _get_db()
    try:
        status = "resolved"
        if result.get("escalate"):
            status = "escalated"

        conn.execute("""
            UPDATE tickets SET
                subject = COALESCE(?, subject),
                intent = ?,
                sub_intent = ?,
                sentiment = ?,
                confidence = ?,
                priority = COALESCE(?, priority),
                status = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            (result.get("customer_message", ""))[:100] or None,
            result.get("intent"),
            result.get("sub_intent"),
            result.get("sentiment"),
            result.get("confidence"),
            result.get("priority"),
            status,
            datetime.now().isoformat(),
            ticket_id,
        ))
        conn.commit()
        logger.info(f"✓ Ticket updated: {ticket_id} -> {status}")
    except Exception as e:
        logger.error(f"✗ Ticket update failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_customer_stats(customer_id: str, result: dict):
    """Update customer stats after workflow."""
    conn = _get_db()
    try:
        escalated = 1 if result.get("escalate") else 0
        conn.execute("""
            UPDATE customers SET
                sentiment = COALESCE(?, sentiment),
                last_interaction = ?,
                total_tickets = total_tickets + 1,
                resolved_tickets = resolved_tickets + ?
            WHERE id = ?
        """, (
            result.get("sentiment"),
            datetime.now().isoformat(),
            0 if escalated else 1,
            customer_id,
        ))
        conn.commit()
        logger.info(f"✓ Customer stats updated: {customer_id}")
    except Exception as e:
        logger.error(f"✗ Customer stats update failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def emit_activity(event_type: str, message: str, level: str = "info", metadata: Optional[dict] = None):
    """Create an activity log entry."""
    conn = _get_db()
    try:
        conn.execute("""
            INSERT INTO activity_logs (type, level, message, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event_type,
            level,
            message,
            datetime.now().isoformat(),
            json.dumps(metadata) if metadata else None,
        ))
        conn.commit()
        logger.info(f"✓ Activity logged: [{event_type}] {message[:60]}")
    except Exception as e:
        logger.error(f"✗ Activity log failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def persist_workflow_result(
    customer_id: str,
    session_id: str,
    channel: str,
    message: str,
    result: dict,
):
    """
    Full persistence pipeline after workflow completes.
    Called from chat, telegram, and email handlers.

    This is the SINGLE entry point for all data persistence.
    Every step logs success/failure explicitly.
    """
    start_time = time.time()
    logger.info(f"📝 PERSIST START: channel={channel} customer={customer_id} session={session_id}")

    # Step 1: Ensure customer
    customer_id = ensure_customer(customer_id, channel)

    # Step 2: Get or create ticket (deduplicated by session)
    ticket_id = get_or_create_ticket(customer_id, channel, session_id, message[:100])

    # Step 3: Store user message
    store_message(ticket_id, "user", message)

    # Step 4: Store assistant response
    final_response = result.get("final_response", "")
    if final_response:
        store_message(ticket_id, "assistant", final_response, agent_type="resolution")

    # Step 5: Record agent execution steps
    duration = time.time() - start_time
    execution_id = f"exec_{uuid4().hex[:8]}"
    record_agent_steps(execution_id, ticket_id, session_id, result, message, duration)

    # Step 6: Update ticket with results
    update_ticket_from_result(ticket_id, result)

    # Step 7: Update customer stats
    update_customer_stats(customer_id, result)

    # Step 8: Emit activity
    emit_activity(
        "system",
        f"[{channel.upper()}] {result.get('intent', 'unknown')} from {customer_id} — {result.get('priority', 'medium')} priority",
        metadata={"ticket_id": ticket_id, "channel": channel, "intent": result.get("intent")}
    )

    total_time = round(time.time() - start_time, 3)
    logger.info(f"📝 PERSIST COMPLETE: ticket={ticket_id} duration={total_time}s")

    return ticket_id
