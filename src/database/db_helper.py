"""
Database Helper Module
Provides database connection and query execution utilities.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DatabaseHelper:
    """Helper class for SQLite database operations."""

    def __init__(self, db_path: str = "data/car_management.db"):
        """Initialize database helper with database path.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connection.

        Yields:
            sqlite3.Connection: Database connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Initialize database with schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()

            with self.get_connection() as conn:
                conn.executescript(schema)

    def execute(self, query: str, params: Tuple = ()) -> int:
        """Execute a query that doesn't return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            int: Last row id
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return all results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries representing rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute query and return first result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Dictionary representing row or None
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute query multiple times with different parameters.

        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        with self.get_connection() as conn:
            conn.executemany(query, params_list)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            bool: True if table exists
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        result = self.fetch_one(query, (table_name,))
        return result is not None
