"""
Car History Repository Module
Provides data access for car history tracking.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper


class CarHistoryRepository:
    """Repository for car history tracking."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def record_create(self, car_id: int, user_id: int) -> int:
        """Record car creation.

        Args:
            car_id: Car ID
            user_id: User ID who created

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO car_history (car_id, action, changed_by, changed_at)
            VALUES (?, 'create', ?, ?)
        """
        return self.db.execute(query, (car_id, user_id, datetime.now()))

    def record_update(self, car_id: int, field_name: str,
                      old_value: Any, new_value: Any,
                      user_id: int) -> int:
        """Record field update.

        Args:
            car_id: Car ID
            field_name: Field name that changed
            old_value: Old value
            new_value: New value
            user_id: User ID who made the change

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO car_history (car_id, action, field_name,
                                   old_value, new_value, changed_by, changed_at)
            VALUES (?, 'update', ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            car_id, field_name,
            str(old_value) if old_value is not None else None,
            str(new_value) if new_value is not None else None,
            user_id, datetime.now()
        ))

    def record_delete(self, car_id: int, user_id: int) -> int:
        """Record car deletion.

        Args:
            car_id: Car ID
            user_id: User ID who deleted

        Returns:
            int: History record ID
        """
        query = """
            INSERT INTO car_history (car_id, action, changed_by, changed_at)
            VALUES (?, 'delete', ?, ?)
        """
        return self.db.execute(query, (car_id, user_id, datetime.now()))

    def get_history(self, car_id: int) -> List[Dict[str, Any]]:
        """Get history for a car.

        Args:
            car_id: Car ID

        Returns:
            List of history records
        """
        query = """
            SELECT h.*, u.full_name as changed_by_name
            FROM car_history h
            LEFT JOIN users u ON h.changed_by = u.id
            WHERE h.car_id = ?
            ORDER BY h.changed_at DESC
        """
        return self.db.fetch_all(query, (car_id,))

    def get_recent_changes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent changes across all cars.

        Args:
            limit: Maximum number of records

        Returns:
            List of history records
        """
        query = f"""
            SELECT h.*, u.full_name as changed_by_name,
                   c.vin, c.brand, c.model
            FROM car_history h
            LEFT JOIN users u ON h.changed_by = u.id
            JOIN cars c ON h.car_id = c.id
            ORDER BY h.changed_at DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (limit,))