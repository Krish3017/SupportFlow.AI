import sqlite3
import os
from datetime import datetime
from typing import Optional


def get_connection():
    db_path = os.getenv("DATABASE_PATH", "supportflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_schema_v3():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            company_customer_id TEXT,
            tier TEXT DEFAULT 'standard',
            sentiment TEXT DEFAULT 'neutral',
            total_conversations INTEGER DEFAULT 0,
            resolved_conversations INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0.0,
            interaction_frequency TEXT,
            last_interaction TEXT,
            joined_date TEXT NOT NULL,
            risk_score INTEGER DEFAULT 0,
            lifetime_value REAL DEFAULT 0.0,
            tags TEXT
        )
    """)

    # Migrations for existing database
    try:
        conn.execute("ALTER TABLE customers ADD COLUMN password_hash TEXT")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE customers ADD COLUMN company_customer_id TEXT")
    except Exception:
        pass

    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_company_id ON customers(company_customer_id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customer_sessions (
            session_token TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_sessions_token ON customer_sessions(session_token)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id TEXT NOT NULL,
            channel_type TEXT NOT NULL,
            channel_identifier TEXT NOT NULL,
            verified INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES customers(id),
            UNIQUE(channel_type, channel_identifier)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_contact_channels_contact ON contact_channels(contact_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contact_channels_lookup ON contact_channels(channel_type, channel_identifier)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            contact_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            subject TEXT,
            started_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            closed_at TEXT,
            session_token TEXT,
            metadata TEXT,
            FOREIGN KEY (contact_id) REFERENCES customers(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_contact ON conversations(contact_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            execution_id TEXT,
            metadata TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_execution ON messages(execution_id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS executions (
            id TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_duration REAL,
            confidence REAL,
            intent TEXT,
            sentiment TEXT,
            priority TEXT,
            escalated INTEGER DEFAULT 0,
            error TEXT,
            metadata TEXT,
            FOREIGN KEY (message_id) REFERENCES messages(id),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_message ON executions(message_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_conversation ON executions(conversation_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_started ON executions(started_at)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS execution_steps (
            id TEXT PRIMARY KEY,
            execution_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            sequence_order INTEGER NOT NULL,
            status TEXT NOT NULL,
            input_data TEXT,
            output_data TEXT,
            latency REAL,
            cost REAL DEFAULT 0.0,
            error TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (execution_id) REFERENCES executions(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_exec_steps_execution ON execution_steps(execution_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_exec_steps_agent ON execution_steps(agent_id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            contact_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium',
            status TEXT NOT NULL DEFAULT 'open',
            assignee TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            escalation_reason TEXT,
            metadata TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (contact_id) REFERENCES customers(id)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_conversation ON tickets(conversation_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_contact ON tickets(contact_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)")

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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp)")

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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail_message_id TEXT UNIQUE,
            sender_email TEXT,
            subject TEXT,
            body TEXT,
            status TEXT DEFAULT 'pending',
            ai_response TEXT,
            conversation_id TEXT,
            created_at TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()
