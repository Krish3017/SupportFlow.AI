import psycopg
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from core.postgres import get_postgres_connection
from core.errors import DatabaseError
from core.logging_config import get_logger

logger = get_logger(__name__)


class BaseRepository:

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = get_postgres_connection()
            with conn.cursor() as cur:
                cur.execute("SET search_path TO supportflow, public;")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"PostgreSQL connection error: {e}")
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
            # Convert positional ? parameters to PostgreSQL %s format if present
            pg_query = query.replace("?", "%s")
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(pg_query, params)

                    if fetch_one:
                        row = cur.fetchone()
                        return dict(row) if row else None

                    if fetch_all:
                        rows = cur.fetchall()
                        return [dict(row) for row in rows]

                    return cur.rowcount

        except Exception as e:
            logger.error(f"Query execution failed: {query[:100]} | Error: {e}")
            raise DatabaseError(operation="query", details={"query": query[:100], "error": str(e)})

    def _count(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        table_name = table if "." in table else f"supportflow.{table}"
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        params = []

        if conditions:
            where_clauses = [f"{k} = %s" for k in conditions.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params = list(conditions.values())

        result = self._execute_query(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0

    def _exists(self, table: str, conditions: Dict[str, Any]) -> bool:
        return self._count(table, conditions) > 0

