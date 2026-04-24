"""
Customer History Repository Module
Provides data access operations for customer history tracking.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper


class CustomerHistoryRepository:
    """Repository for customer history tracking."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def record_create(self, customer_id: int, user_id: int) -> int:
        """Record customer creation.

        Args:
            customer_id: Customer ID
            user_id: User ID who created

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO customer_history (customer_id, action, changed_by, changed_at)
            VALUES (?, 'create', ?, ?)
        """
        return self.db.execute(query, (customer_id, user_id, datetime.now()))

    def record_update(self, customer_id: int, field_name: str,
                     old_value: Any, new_value: Any,
                     user_id: int) -> int:
        """Record field update.

        Args:
            customer_id: Customer ID
            field_name: Field name
            old_value: Old value
            new_value: New value
            user_id: User ID who updated

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO customer_history
            (customer_id, action, field_name, old_value, new_value, changed_by, changed_at)
            VALUES (?, 'update', ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            customer_id, field_name,
            str(old_value) if old_value is not None else None,
            str(new_value) if new_value is not None else None,
            user_id, datetime.now()
        ))

    def record_delete(self, customer_id: int, user_id: int,
                     reason: Optional[str] = None) -> int:
        """Record customer deletion.

        Args:
            customer_id: Customer ID
            user_id: User ID who deleted
            reason: Reason for deletion

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO customer_history
            (customer_id, action, field_name, old_value, changed_by, changed_at)
            VALUES (?, 'delete', 'delete_reason', ?, ?, ?)
        """
        return self.db.execute(query, (
            customer_id, reason, user_id, datetime.now()
        ))

    def record_restore(self, customer_id: int, user_id: int) -> int:
        """Record customer restore.

        Args:
            customer_id: Customer ID
            user_id: User ID who restored

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO customer_history (customer_id, action, changed_by, changed_at)
            VALUES (?, 'restore', ?, ?)
        """
        return self.db.execute(query, (customer_id, user_id, datetime.now()))

    def get_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get history for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of history records
        """
        query = """
            SELECT h.*, u.full_name as changed_by_name
            FROM customer_history h
            LEFT JOIN users u ON h.changed_by = u.id
            WHERE h.customer_id = ?
            ORDER BY h.changed_at DESC
        """
        return self.db.fetch_all(query, (customer_id,))

    def get_history_by_action(self, customer_id: int,
                               action: str) -> List[Dict[str, Any]]:
        """Get history filtered by action.

        Args:
            customer_id: Customer ID
            action: Action type ('create', 'update', 'delete', 'restore')

        Returns:
            List of history records
        """
        query = """
            SELECT h.*, u.full_name as changed_by_name
            FROM customer_history h
            LEFT JOIN users u ON h.changed_by = u.id
            WHERE h.customer_id = ? AND h.action = ?
            ORDER BY h.changed_at DESC
        """
        return self.db.fetch_all(query, (customer_id, action))
