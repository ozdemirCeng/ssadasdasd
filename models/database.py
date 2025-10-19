"""
Database Connection Manager
Thread-safe connection pooling with psycopg2
"""

import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton database connection manager with pooling"""

    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, config: Dict[str, Any]):
        """Initialize connection pool"""
        if self._pool is None:
            try:
                self._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=config.get('pool_size', 10),
                    host=config['host'],
                    port=config['port'],
                    database=config['database'],
                    user=config['user'],
                    password=config['password']
                )
                logger.info("[OK] Database connection pool initialized")
            except Exception as e:
                logger.error(f"[ERROR] Database initialization failed: {e}")
                raise

    @contextmanager
    def get_connection(self):
        """Get connection from pool (context manager)"""
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)

    def execute_query(self, query: str, params: Tuple = None, fetch_one: bool = False) -> Optional[Any]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch_one:
                    return cursor.fetchone()
                return cursor.fetchall()

    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount

    def execute_procedure(self, procedure_name: str, params: List = None) -> Any:
        """Execute stored procedure/function"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(procedure_name, params or [])
                try:
                    return cursor.fetchall()
                except:
                    return None

    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return cursor.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close_all(self):
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("[OK] All database connections closed")


# Global database instance
db = DatabaseManager()