import sqlite3
import os
from datetime import datetime

from database_schema_v3 import create_schema_v3


def get_connection():
    db_path = os.getenv("DATABASE_PATH", "supportflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_customer(customer_id: str):
    conn = get_connection()
    customer = conn.execute(
        "SELECT * FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    return dict(customer) if customer else None


def create_tables():
    create_schema_v3()


def save_conversation(state: dict):
    pass


def is_email_processed(gmail_message_id: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM email_tickets WHERE gmail_message_id = ?",
        (gmail_message_id,)
    ).fetchone()
    conn.close()
    return row is not None


def save_email_ticket(email: dict) -> int:
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO email_tickets (gmail_message_id, sender_email, subject, body, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    """, (
        email["id"],
        email["sender"],
        email["subject"],
        email["body"],
        datetime.utcnow().isoformat()
    ))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def update_email_ticket(ticket_id: int, status: str, ai_response: str):
    conn = get_connection()
    conn.execute("""
        UPDATE email_tickets
        SET status = ?, ai_response = ?
        WHERE id = ?
    """, (status, ai_response, ticket_id))
    conn.commit()
    conn.close()
