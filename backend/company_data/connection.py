import os
from typing import Generator
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from core.postgres import get_postgres_connection

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "company_data.db")


def get_company_db_path() -> str:
    """
    Returns the legacy path to the company business SQLite database.
    Retained for backward compatibility.
    """
    path = os.getenv("COMPANY_DATABASE_PATH", DEFAULT_DB_PATH)
    return os.path.abspath(path)


def get_company_db_connection() -> psycopg.Connection:
    """
    Creates and returns a connection to the Supabase PostgreSQL company schema.
    """
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO company, public;")
    conn.commit()
    return conn


@contextmanager
def get_company_db() -> Generator[psycopg.Connection, None, None]:
    """
    Context manager for managing PostgreSQL company database connections and transactions.
    """
    conn = get_company_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
