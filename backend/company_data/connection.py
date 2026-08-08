import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "company_data.db")


def get_company_db_path() -> str:
    """
    Returns the path to the company business SQLite database.
    Can be overridden via COMPANY_DATABASE_PATH environment variable.
    """
    path = os.getenv("COMPANY_DATABASE_PATH", DEFAULT_DB_PATH)
    return os.path.abspath(path)


def get_company_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the isolated company database.
    """
    db_path = get_company_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_company_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for managing company database connections and transactions.
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
