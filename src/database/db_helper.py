"""
Database Helper Module
Provides DatabaseHelper class for database operations with context managers.
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple


class DatabaseHelper:
    """Helper class for database operations."""

    def __init__(self, db_path: str):
        """Initialize database helper.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT, UPDATE, DELETE query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            int: Last row id for INSERT, affected rows for UPDATE/DELETE
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Dictionary representing row or None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries representing rows
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            int: Number of affected rows
        """
        conn = self._get_connection()
        try:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
