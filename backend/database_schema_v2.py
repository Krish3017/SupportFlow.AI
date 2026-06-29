"""
SupportFlow AI - Enhanced Database Schema (Phase 3)
Extends existing schema with admin panel requirements
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional

def get_connection():
    db_path = os.getenv("DATABASE_PATH", "supportflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_enhanced_tables():
    """
    Create enhanced schema for Phase 3.
    Safe to run on existing database - uses IF NOT EXISTS.
    Preserves existing conversations and email_tickets tables.
    """
    conn = get_connection()

    # ═══════════════════════════════════════════════════════════════
    # EXISTING TABLES (from Phase 1/2 - preserved)
    # ═══════════════════════════════════════════════════════════════

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_message TEXT,
            intent TEXT,
            sub_intent TEXT,
            sentiment TEXT,
            confidence REAL,
            final_response TEXT,
            escalated BOOLEAN,
            priority TEXT,
            timestamp TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail_message_id TEXT UNIQUE,
            sender_email TEXT,
            subject TEXT,
            body TEXT,
            status TEXT DEFAULT 'pending',
            ai_response TEXT,
            created_at TEXT
        )
    """)

    # ═══════════════════════════════════════════════════════════════
    # NEW TABLES (Phase 3)
    # ═══════════════════════════════════════════════════════════════

    # ── Unified Tickets Table ──────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            channel TEXT NOT NULL,
            sentiment TEXT,
            intent TEXT,
            sub_intent TEXT,
            confidence REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            escalated_at TEXT,
            current_agent TEXT,
            time_elapsed INTEGER DEFAULT 0,
            assignee TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at)")

    # ── Customers Table ────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'standard',
            sentiment TEXT DEFAULT 'neutral',
            total_tickets INTEGER DEFAULT 0,
            resolved_tickets INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0.0,
            interaction_frequency TEXT,
            last_interaction TEXT,
            joined_date TEXT NOT NULL,
            risk_score INTEGER DEFAULT 0,
            lifetime_value REAL DEFAULT 0.0,
            tags TEXT
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier)")

    # ── Agent Executions Table ─────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_executions (
            id TEXT PRIMARY KEY,
            ticket_id TEXT NOT NULL,
            session_id TEXT,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            status TEXT NOT NULL,
            input_data TEXT,
            output_data TEXT,
            latency REAL,
            cost REAL,
            error TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            sequence_order INTEGER,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_ticket ON agent_executions(ticket_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_agent ON agent_executions(agent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON agent_executions(status)")

    # ── Activity Logs Table ────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_type ON activity_logs(type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_level ON activity_logs(level)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp)")

    # ── Knowledge Documents Table ──────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            chunks INTEGER DEFAULT 0,
            retrieval_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL,
            size_bytes INTEGER,
            file_path TEXT,
            chroma_collection TEXT
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_documents(status)")

    # ── Messages Table (for conversations/tickets) ─────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            agent_type TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_ticket ON messages(ticket_id)")

    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════
# REPOSITORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

# ── Tickets ─────────────────────────────────────────────────────

def create_ticket(ticket_data: dict) -> str:
    """Create a new ticket and return its ID"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO tickets (
            id, subject, customer_id, priority, status, channel,
            sentiment, intent, sub_intent, confidence, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_data['id'],
        ticket_data['subject'],
        ticket_data['customer_id'],
        ticket_data['priority'],
        ticket_data['status'],
        ticket_data['channel'],
        ticket_data.get('sentiment'),
        ticket_data.get('intent'),
        ticket_data.get('sub_intent'),
        ticket_data.get('confidence'),
        ticket_data['created_at'],
        ticket_data['updated_at']
    ))
    conn.commit()
    conn.close()
    return ticket_data['id']

def get_ticket(ticket_id: str) -> Optional[dict]:
    """Get ticket by ID"""
    conn = get_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return dict(ticket) if ticket else None

def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list:
    """List tickets with filters"""
    conn = get_connection()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if channel:
        query += " AND channel = ?"
        params.append(channel)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    tickets = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(t) for t in tickets]

def update_ticket_status(ticket_id: str, status: str, **kwargs):
    """Update ticket status and optional fields"""
    conn = get_connection()
    updates = ["status = ?", "updated_at = ?"]
    params = [status, datetime.now().isoformat()]

    if 'resolved_at' in kwargs:
        updates.append("resolved_at = ?")
        params.append(kwargs['resolved_at'])
    if 'escalated_at' in kwargs:
        updates.append("escalated_at = ?")
        params.append(kwargs['escalated_at'])
    if 'current_agent' in kwargs:
        updates.append("current_agent = ?")
        params.append(kwargs['current_agent'])

    params.append(ticket_id)
    query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    conn.close()

# ── Customers ───────────────────────────────────────────────────

def upsert_customer(customer_data: dict) -> str:
    """Create or update customer"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO customers (
            id, name, email, tier, sentiment, joined_date, last_interaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name = excluded.name,
            tier = excluded.tier,
            sentiment = excluded.sentiment,
            last_interaction = excluded.last_interaction
    """, (
        customer_data['id'],
        customer_data.get('name'),
        customer_data['email'],
        customer_data.get('tier', 'standard'),
        customer_data.get('sentiment', 'neutral'),
        customer_data.get('joined_date', datetime.now().isoformat()),
        customer_data.get('last_interaction', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()
    return customer_data['id']

def get_customer_by_email(email: str) -> Optional[dict]:
    """Get customer by email"""
    conn = get_connection()
    customer = conn.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(customer) if customer else None

def list_customers(limit: int = 100, offset: int = 0) -> list:
    """List all customers"""
    conn = get_connection()
    customers = conn.execute(
        "SELECT * FROM customers ORDER BY last_interaction DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(c) for c in customers]

# ── Agent Executions ────────────────────────────────────────────

def create_execution(execution_data: dict) -> str:
    """Log agent execution"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO agent_executions (
            id, ticket_id, session_id, agent_id, agent_name, status,
            input_data, output_data, latency, cost, error,
            started_at, completed_at, sequence_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        execution_data['id'],
        execution_data['ticket_id'],
        execution_data.get('session_id'),
        execution_data['agent_id'],
        execution_data['agent_name'],
        execution_data['status'],
        execution_data.get('input_data'),
        execution_data.get('output_data'),
        execution_data.get('latency'),
        execution_data.get('cost', 0.0),
        execution_data.get('error'),
        execution_data['started_at'],
        execution_data.get('completed_at'),
        execution_data.get('sequence_order', 0)
    ))
    conn.commit()
    conn.close()
    return execution_data['id']

def get_executions_for_ticket(ticket_id: str) -> list:
    """Get all executions for a ticket"""
    conn = get_connection()
    executions = conn.execute(
        "SELECT * FROM agent_executions WHERE ticket_id = ? ORDER BY sequence_order",
        (ticket_id,)
    ).fetchall()
    conn.close()
    return [dict(e) for e in executions]

# ── Activity Logs ───────────────────────────────────────────────

def log_activity(type: str, level: str, message: str, metadata: Optional[dict] = None):
    """Log system activity"""
    import json
    conn = get_connection()
    conn.execute("""
        INSERT INTO activity_logs (type, level, message, timestamp, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (
        type,
        level,
        message,
        datetime.now().isoformat(),
        json.dumps(metadata) if metadata else None
    ))
    conn.commit()
    conn.close()

def get_activity_logs(
    type: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
) -> list:
    """Get activity logs with filters"""
    conn = get_connection()
    query = "SELECT * FROM activity_logs WHERE 1=1"
    params = []

    if type:
        query += " AND type = ?"
        params.append(type)
    if level:
        query += " AND level = ?"
        params.append(level)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    logs = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(log) for log in logs]

# ── Messages ────────────────────────────────────────────────────

def create_message(message_data: dict):
    """Add message to ticket conversation"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO messages (ticket_id, role, content, timestamp, agent_type)
        VALUES (?, ?, ?, ?, ?)
    """, (
        message_data['ticket_id'],
        message_data['role'],
        message_data['content'],
        message_data['timestamp'],
        message_data.get('agent_type')
    ))
    conn.commit()
    conn.close()

def get_messages_for_ticket(ticket_id: str) -> list:
    """Get all messages for a ticket"""
    conn = get_connection()
    messages = conn.execute(
        "SELECT * FROM messages WHERE ticket_id = ? ORDER BY timestamp",
        (ticket_id,)
    ).fetchall()
    conn.close()
    return [dict(m) for m in messages]
