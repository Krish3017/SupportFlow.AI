"""
PostgreSQL Connection Helper (Supabase)
Provides production-safe PostgreSQL connection management via psycopg v3.
"""
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


def get_postgres_connection() -> psycopg.Connection:
    """
    Establish and return a new connection to Supabase PostgreSQL.
    Raises ValueError if DATABASE_URL is not configured.
    """
    db_url = settings.DATABASE_URL
    if not db_url:
        raise ValueError("DATABASE_URL is not set in environment configuration.")

    try:
        from urllib.parse import urlparse, unquote
        clean_url = db_url.strip().replace("[", "").replace("]", "")
        parsed = urlparse(clean_url)
        
        user = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else ""
        host = unquote(parsed.hostname) if parsed.hostname else ""
        port = parsed.port or 5432
        dbname = parsed.path.lstrip("/") or "postgres"

        conn = psycopg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
            row_factory=dict_row,
            autocommit=False
        )
        return conn
    except Exception as e:
        logger.error("Failed to connect to Supabase PostgreSQL database.")
        raise RuntimeError(f"PostgreSQL connection failed: {e}") from e
