"""
Migration script: v2 schema → v3 schema

Migrates data from old ticket-centric model to conversation-centric model.
Safe to run multiple times (idempotent).

Usage:
    cd backend
    python migrate_to_v3.py
"""
import os
import sqlite3
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "supportflow.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def migrate():
    from database_schema_v3 import create_schema_v3
    create_schema_v3()

    conn = get_conn()

    existing_tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    if "tickets" not in existing_tables:
        print("No old tickets table found. Fresh database — schema created.")
        conn.close()
        return

    cols = [r[1] for r in conn.execute("PRAGMA table_info(tickets)").fetchall()]
    if "conversation_id" in cols:
        print("Already migrated (tickets table has conversation_id). Skipping data migration.")
        conn.close()
        return

    print(f"Migrating database at: {DB_PATH}")

    old_tickets = conn.execute("SELECT * FROM tickets").fetchall()
    print(f"Found {len(old_tickets)} old tickets to migrate.")

    old_messages = conn.execute("SELECT * FROM messages").fetchall()
    print(f"Found {len(old_messages)} old messages to migrate.")

    old_executions = conn.execute("SELECT * FROM agent_executions").fetchall()
    print(f"Found {len(old_executions)} old execution steps to migrate.")

    conn.execute("ALTER TABLE tickets RENAME TO tickets_old")
    conn.execute("ALTER TABLE messages RENAME TO messages_old")
    conn.execute("ALTER TABLE agent_executions RENAME TO agent_executions_old")
    conn.commit()

    from database_schema_v3 import create_schema_v3
    create_schema_v3()

    ticket_to_conversation = {}

    for ticket in old_tickets:
        ticket = dict(ticket)
        ticket_id = ticket['id']
        customer_id = ticket['customer_id']
        channel = ticket.get('channel', 'chat')

        conv_id = f"conv_{uuid4().hex[:12]}"
        now = ticket.get('created_at', datetime.utcnow().isoformat())
        updated = ticket.get('updated_at', now)

        status_map = {
            'new': 'active',
            'in_progress': 'active',
            'resolved': 'resolved',
            'escalated': 'escalated',
        }
        conv_status = status_map.get(ticket.get('status', 'new'), 'active')

        conn.execute("""
            INSERT OR IGNORE INTO conversations (id, contact_id, channel, status, subject, started_at, updated_at, session_token)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (conv_id, customer_id, channel, conv_status, ticket.get('subject', ''), now, updated, f"migrated_{ticket_id}"))

        ticket_to_conversation[ticket_id] = conv_id

        if ticket.get('status') == 'escalated':
            new_ticket_id = f"TKT_{uuid4().hex[:12]}"
            conn.execute("""
                INSERT OR IGNORE INTO tickets (id, conversation_id, contact_id, subject, priority, status, created_at, updated_at, escalation_reason)
                VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?)
            """, (
                new_ticket_id, conv_id, customer_id,
                ticket.get('subject', 'Escalated'),
                ticket.get('priority', 'medium'),
                now, updated,
                f"Migrated from old ticket {ticket_id}"
            ))

    print(f"Created {len(ticket_to_conversation)} conversations.")

    msg_count = 0
    for msg in old_messages:
        msg = dict(msg)
        old_ticket_id = msg.get('ticket_id')
        conv_id = ticket_to_conversation.get(old_ticket_id)
        if not conv_id:
            continue

        msg_id = f"msg_{uuid4().hex[:12]}"
        conn.execute("""
            INSERT OR IGNORE INTO messages (id, conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (msg_id, conv_id, msg['role'], msg['content'], msg['timestamp']))
        msg_count += 1

    print(f"Migrated {msg_count} messages.")

    exec_groups = {}
    for step in old_executions:
        step = dict(step)
        old_ticket_id = step.get('ticket_id')
        conv_id = ticket_to_conversation.get(old_ticket_id)
        if not conv_id:
            continue

        group_key = f"{old_ticket_id}_{step.get('session_id', '')}"
        if group_key not in exec_groups:
            exec_groups[group_key] = {
                'conv_id': conv_id,
                'steps': [],
                'started_at': step['started_at'],
            }
        exec_groups[group_key]['steps'].append(step)

    exec_count = 0
    for group_key, group in exec_groups.items():
        exec_id = f"exec_{uuid4().hex[:12]}"
        msg_id = f"msg_{uuid4().hex[:12]}"

        conn.execute("""
            INSERT OR IGNORE INTO executions (id, message_id, conversation_id, status, started_at, completed_at)
            VALUES (?, ?, ?, 'completed', ?, ?)
        """, (exec_id, msg_id, group['conv_id'], group['started_at'], group['started_at']))

        for step in group['steps']:
            step_id = f"{exec_id}_step{step.get('sequence_order', 0)}"
            conn.execute("""
                INSERT OR IGNORE INTO execution_steps (id, execution_id, agent_id, agent_name, sequence_order, status, input_data, output_data, latency, cost, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step_id, exec_id,
                step['agent_id'], step['agent_name'],
                step.get('sequence_order', 0),
                step['status'],
                step.get('input_data'), step.get('output_data'),
                step.get('latency'), step.get('cost', 0),
                step['started_at'], step.get('completed_at')
            ))

        exec_count += 1

    print(f"Migrated {exec_count} executions with steps.")

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
