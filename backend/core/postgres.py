"""
PostgreSQL Connection Helper (Supabase)
Provides production-safe PostgreSQL connection management via psycopg v3 and psycopg_pool.
"""
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

import threading

_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def parse_db_url(db_url: str):
    clean_url = db_url.strip()
    if clean_url.startswith("postgresql://") or clean_url.startswith("postgres://"):
        scheme_rest = clean_url.split("://", 1)[1]
        userpass, hostportdb = scheme_rest.rsplit("@", 1)

        if ":" in userpass:
            user, password = userpass.split(":", 1)
        else:
            user, password = userpass, ""

        password = password.strip("[").strip("]")

        if "/" in hostportdb:
            hostport, dbname = hostportdb.split("/", 1)
        else:
            hostport, dbname = hostportdb, "postgres"

        if "?" in dbname:
            dbname = dbname.split("?", 1)[0]

        if ":" in hostport:
            host, port_str = hostport.split(":", 1)
            port = int(port_str)
        else:
            host, port = hostport, 5432

        return user, password, host, port, dbname
    raise ValueError("Invalid PostgreSQL URL format.")


def init_postgres_pool() -> Optional[ConnectionPool]:
    """
    Initialize global ConnectionPool for PostgreSQL connections in a thread-safe manner.
    """
    global _pool
    if _pool is not None:
        return _pool

    with _pool_lock:
        if _pool is not None:
            return _pool

        db_url = settings.DATABASE_URL
        if not db_url:
            logger.warning("DATABASE_URL is not set in environment configuration.")
            return None

        try:
            user, password, host, port, dbname = parse_db_url(db_url)
            conninfo = f"user={user} password={password} host={host} port={port} dbname={dbname} sslmode=require"

            _pool = ConnectionPool(
                conninfo=conninfo,
                min_size=5,
                max_size=20,
                kwargs={"row_factory": dict_row, "autocommit": True},
                open=True,
            )
            logger.info("PostgreSQL ConnectionPool initialized successfully (min_size=5, max_size=20).")
            return _pool
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL ConnectionPool: {e}")
            return None



def close_postgres_pool():
    """
    Close global ConnectionPool cleanly during application shutdown.
    """
    global _pool
    if _pool is not None:
        try:
            _pool.close()
            logger.info("PostgreSQL ConnectionPool closed successfully.")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL ConnectionPool: {e}")
        finally:
            _pool = None


class PooledConnProxy:
    """
    Proxy wrapper around a psycopg connection acquired from ConnectionPool.
    Interceptor method close() returns the underlying connection back to the pool via putconn().
    """

    def __init__(self, conn: psycopg.Connection, pool: ConnectionPool):
        self._conn = conn
        self._pool = pool
        self._returned = False

    def close(self):
        if not self._returned:
            self._returned = True
            try:
                self._pool.putconn(self._conn)
            except Exception as e:
                logger.warning(f"Error returning connection to pool: {e}")

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_postgres_connection(timeout: float = 10.0) -> psycopg.Connection:

    """
    Acquire a connection from the global ConnectionPool wrapped in PooledConnProxy.
    Calls init_postgres_pool() lazily if pool is not yet initialized.
    Calling conn.close() on the returned object safely returns it to the pool.
    """
    global _pool
    if _pool is None:
        init_postgres_pool()

    if _pool is None:
        raise RuntimeError("PostgreSQL ConnectionPool is not initialized.")

    try:
        raw_conn = _pool.getconn(timeout=timeout)
        return PooledConnProxy(raw_conn, _pool)
    except Exception as e:
        logger.error(f"Failed to acquire connection from PostgreSQL pool: {e}")
        raise RuntimeError(f"PostgreSQL pool connection error: {e}") from e



