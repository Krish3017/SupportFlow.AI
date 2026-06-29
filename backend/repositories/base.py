import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from core.config import settings
from core.errors import DatabaseError
from core.logging_config import get_logger

logger = get_logger(__name__)


class BaseRepository:

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
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
            logger.error(f"Query execution failed: {query[:100]} | Error: {e}")
            raise DatabaseError(operation="query", details={"query": query[:100], "error": str(e)})

    def _count(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        query = f"SELECT COUNT(*) as count FROM {table}"
        params = []

        if conditions:
            where_clauses = [f"{k} = ?" for k in conditions.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params = list(conditions.values())

        result = self._execute_query(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0

    def _exists(self, table: str, conditions: Dict[str, Any]) -> bool:
        return self._count(table, conditions) > 0
