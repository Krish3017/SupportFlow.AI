"""
Base Repository Pattern
Abstract DB operations for testability and consistency
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from core.config import settings
from core.errors import DatabaseError
from core.logging_config import get_logger

logger = get_logger(__name__)

class BaseRepository:
    """Base repository with common DB operations"""

    _migrated = False

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    @contextmanager
    def get_connection(self):
        """Context manager for DB connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            if not BaseRepository._migrated:
                self._ensure_columns(conn)
                BaseRepository._migrated = True

            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(operation="connection", details={"error": str(e)})
        finally:
            if conn:
                conn.close()

    def _execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Optional[Any]:
        """
        Execute a query and return results

        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows

        Returns:
            Query result(s) or None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)

                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None

                if fetch_all:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]

                return cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {query} | Error: {e}")
            raise DatabaseError(operation="query", details={"query": query, "error": str(e)})

    def _count(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count rows in a table with optional filters"""
        query = f"SELECT COUNT(*) as count FROM {table}"
        params = []

        if conditions:
            where_clauses = [f"{k} = ?" for k in conditions.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params = list(conditions.values())

        result = self._execute_query(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0

    def _exists(self, table: str, conditions: Dict[str, Any]) -> bool:
        """Check if a row exists"""
        return self._count(table, conditions) > 0

    def _ensure_columns(self, conn):
        """Add missing columns to tables. Runs once on first connection."""
        migrations = [
            ("customers", "last_interaction", "TEXT"),
            ("customers", "sentiment", "TEXT DEFAULT 'neutral'"),
            ("customers", "total_tickets", "INTEGER DEFAULT 0"),
            ("customers", "resolved_tickets", "INTEGER DEFAULT 0"),
            ("customers", "avg_response_time", "REAL DEFAULT 0.0"),
            ("customers", "interaction_frequency", "TEXT"),
            ("customers", "joined_date", "TEXT"),
            ("customers", "risk_score", "INTEGER DEFAULT 0"),
            ("customers", "lifetime_value", "REAL DEFAULT 0.0"),
            ("customers", "tags", "TEXT"),
            ("customers", "tier", "TEXT DEFAULT 'standard'"),
            ("customers", "name", "TEXT"),
        ]

        for table, column, col_type in migrations:
            try:
                cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
                if column not in cols:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            except Exception:
                pass

        conn.commit()
