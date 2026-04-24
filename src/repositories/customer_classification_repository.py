"""
Customer Classification Repository Module
Provides data access operations for customer classification.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper


class CustomerClassificationRepository:
    """Repository for customer classification data."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def get_active_rules(self) -> List[Any]:
        """Get active classification rules sorted by priority.

        Returns:
            List of classification rules
        """
        query = """
            SELECT * FROM customer_classification_rules
            WHERE is_active = 1
            ORDER BY priority ASC
        """
        rows = self.db.fetch_all(query)
        return [self._row_to_rule(row) for row in rows if row]

    def get_rules(self, customer_class: Optional[str] = None) -> List[Any]:
        """Get classification rules.

        Args:
            customer_class: Filter by customer class

        Returns:
            List of classification rules
        """
        if customer_class:
            query = """
                SELECT * FROM customer_classification_rules
                WHERE customer_class = ?
                ORDER BY priority ASC
            """
            rows = self.db.fetch_all(query, (customer_class,))
        else:
            query = "SELECT * FROM customer_classification_rules ORDER BY priority ASC"
            rows = self.db.fetch_all(query)

        return [self._row_to_rule(row) for row in rows if row]

    def get_rule_by_id(self, rule_id: int) -> Optional[Any]:
        """Get a rule by ID.

        Args:
            rule_id: Rule ID

        Returns:
            Classification rule or None
        """
        query = "SELECT * FROM customer_classification_rules WHERE id = ?"
        row = self.db.fetch_one(query, (rule_id,))
        return self._row_to_rule(row) if row else None

    def create_rule(self, rule_data: Dict[str, Any]) -> int:
        """Create a new rule.

        Args:
            rule_data: Rule data dictionary

        Returns:
            ID of created rule
        """
        query = """
            INSERT INTO customer_classification_rules
            (rule_name, customer_class, min_contracts, min_total_value,
             min_avg_value, min_frequency_months, priority, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            rule_data['rule_name'],
            rule_data['customer_class'],
            rule_data.get('min_contracts', 0),
            rule_data.get('min_total_value', 0),
            rule_data.get('min_avg_value', 0),
            rule_data.get('min_frequency_months'),
            rule_data.get('priority', 0),
            rule_data.get('is_active', True)
        )
        return self.db.execute(query, params)

    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Update a rule.

        Args:
            rule_id: Rule ID
            rule_data: Updated rule data

        Returns:
            True if successful
        """
        allowed = ['rule_name', 'customer_class', 'min_contracts',
                   'min_total_value', 'min_avg_value', 'min_frequency_months',
                   'priority', 'is_active']

        fields = []
        params = []
        for field in allowed:
            if field in rule_data:
                fields.append(f"{field} = ?")
                params.append(rule_data[field])

        if not fields:
            return False

        fields.append("updated_at = ?")
        params.append(datetime.now())
        params.append(rule_id)

        query = f"UPDATE customer_classification_rules SET {', '.join(fields)} WHERE id = ?"
        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule.

        Args:
            rule_id: Rule ID

        Returns:
            True if successful
        """
        query = "DELETE FROM customer_classification_rules WHERE id = ?"
        try:
            self.db.execute(query, (rule_id,))
            return True
        except Exception:
            return False

    def record_classification_change(self, customer_id: int,
                                    old_class: Optional[str],
                                    new_class: str,
                                    reason: str,
                                    changed_by: Optional[int],
                                    rule_id: Optional[int]) -> int:
        """Record classification change.

        Args:
            customer_id: Customer ID
            old_class: Old classification
            new_class: New classification
            reason: Reason for change
            changed_by: User ID who made the change
            rule_id: Triggering rule ID

        Returns:
            ID of history record
        """
        query = """
            INSERT INTO customer_classification_history
            (customer_id, old_class, new_class, reason, changed_by,
             triggered_by_rule_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            customer_id, old_class, new_class, reason, changed_by,
            rule_id, datetime.now()
        ))

    def get_last_classification_date(self, customer_id: int) -> Optional[datetime]:
        """Get last classification date for customer.

        Args:
            customer_id: Customer ID

        Returns:
            Last classification date or None
        """
        query = """
            SELECT MAX(created_at) as last_date
            FROM customer_classification_history
            WHERE customer_id = ?
        """
        result = self.db.fetch_one(query, (customer_id,))
        return result['last_date'] if result and result['last_date'] else None

    def get_benefits(self, customer_class: str) -> List[Dict]:
        """Get benefits for customer class.

        Args:
            customer_class: Customer class (vip, regular, potential)

        Returns:
            List of benefits
        """
        query = """
            SELECT * FROM vip_benefits
            WHERE customer_class = ? AND is_active = 1
            ORDER BY benefit_name
        """
        return self.db.fetch_all(query, (customer_class,)) or []

    def reorder_rules(self, rule_ids: List[int]) -> bool:
        """Reorder rules by updating priority.

        Args:
            rule_ids: List of rule IDs in new order

        Returns:
            True if successful
        """
        try:
            for i, rule_id in enumerate(rule_ids):
                query = "UPDATE customer_classification_rules SET priority = ? WHERE id = ?"
                self.db.execute(query, (i + 1, rule_id))
            return True
        except Exception:
            return False

    def _row_to_rule(self, row: Dict) -> Any:
        """Convert database row to ClassificationRule.

        Args:
            row: Database row

        Returns:
            ClassificationRule instance
        """
        from ..services.customer_classification_service import ClassificationRule
        return ClassificationRule(
            id=row['id'],
            rule_name=row['rule_name'],
            customer_class=row['customer_class'],
            min_contracts=row['min_contracts'],
            min_total_value=row['min_total_value'],
            min_avg_value=row.get('min_avg_value', 0),
            min_frequency_months=row.get('min_frequency_months'),
            priority=row['priority']
        )
