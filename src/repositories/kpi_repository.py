"""
KPI Repository for managing KPI records and targets.
Sprint 0.4: Employee KPI
"""

from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from src.database.db_helper import DatabaseHelper
from src.models.kpi import KPIRecord, KPITarget


class KPIRepository:
    """Repository for KPI record operations."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def get_by_id(self, kpi_id: int) -> Optional[KPIRecord]:
        """Get KPI record by ID."""
        query = "SELECT * FROM kpi_records WHERE id = ?"
        result = self.db.fetch_one(query, (kpi_id,))
        return KPIRecord.from_dict(result) if result else None

    def get_by_user_and_period(self, user_id: int, period_type: str,
                               period_value: str) -> Optional[dict]:
        """Get KPI record by user and period."""
        query = """
            SELECT * FROM kpi_records
            WHERE user_id = ? AND period_type = ? AND period_value = ?
        """
        return self.db.fetch_one(query, (user_id, period_type, period_value))

    def get_by_user(self, user_id: int, period_type: str = None,
                    limit: int = 12) -> List[dict]:
        """Get KPI records for a user."""
        if period_type:
            query = """
                SELECT * FROM kpi_records
                WHERE user_id = ? AND period_type = ?
                ORDER BY period_value DESC
                LIMIT ?
            """
            results = self.db.fetch_all(query, (user_id, period_type, limit))
        else:
            query = """
                SELECT * FROM kpi_records
                WHERE user_id = ?
                ORDER BY period_value DESC
                LIMIT ?
            """
            results = self.db.fetch_all(query, (user_id, limit))
        return results

    def get_by_date_range(self, user_id: int, start_date: date,
                          end_date: date) -> List[dict]:
        """Get KPI records within a date range.

        Converts dates to period_value format (YYYY-MM) for comparison.
        """
        # Convert dates to period_value format (YYYY-MM)
        start_period = start_date.strftime('%Y-%m')
        end_period = end_date.strftime('%Y-%m')

        query = """
            SELECT * FROM kpi_records
            WHERE user_id = ?
            AND period_value >= ? AND period_value <= ?
            ORDER BY period_value ASC
        """
        return self.db.fetch_all(query, (user_id, start_period, end_period))

    def get_all_by_period(self, period_type: str,
                          period_value: str) -> List[dict]:
        """Get all KPI records for a specific period."""
        query = """
            SELECT * FROM kpi_records
            WHERE period_type = ? AND period_value = ?
            ORDER BY overall_score DESC
        """
        return self.db.fetch_all(query, (period_type, period_value))

    def get_top_performers(self, period_type: str, period_value: str,
                           limit: int = 10) -> List[dict]:
        """Get top performers for a period."""
        query = """
            SELECT k.*, u.full_name, u.username
            FROM kpi_records k
            JOIN users u ON k.user_id = u.id
            WHERE k.period_type = ? AND k.period_value = ?
            ORDER BY k.overall_score DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (period_type, period_value, limit))

    def get_team_average(self, period_type: str,
                         period_value: str) -> Dict[str, float]:
        """Get team average metrics for a period."""
        query = """
            SELECT
                AVG(cars_sold) as avg_cars,
                AVG(revenue_generated) as avg_revenue,
                AVG(overall_score) as avg_score,
                COUNT(*) as total_staff
            FROM kpi_records
            WHERE period_type = ? AND period_value = ?
        """
        result = self.db.fetch_one(query, (period_type, period_value))
        if not result:
            return {'avg_cars': 0, 'avg_revenue': 0, 'avg_score': 0, 'total_staff': 0}
        return {
            'avg_cars': result['avg_cars'] or 0,
            'avg_revenue': float(result['avg_revenue'] or 0),
            'avg_score': result['avg_score'] or 0,
            'total_staff': result['total_staff'] or 0
        }

    def create(self, data: dict) -> int:
        """Create a new KPI record."""
        query = """
            INSERT INTO kpi_records (
                user_id, period_type, period_value,
                cars_sold, revenue_generated, new_customers, contracts_signed,
                target_cars, target_revenue,
                cars_achievement_rate, revenue_achievement_rate, overall_score,
                period_rank, total_staff, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            data['user_id'],
            data.get('period_type', 'monthly'),
            data['period_value'],
            data.get('cars_sold', 0),
            float(data.get('revenue_generated', 0)),
            data.get('new_customers', 0),
            data.get('contracts_signed', 0),
            data.get('target_cars', 0),
            float(data.get('target_revenue', 0)),
            data.get('cars_achievement_rate', 0),
            data.get('revenue_achievement_rate', 0),
            data.get('overall_score', 0),
            data.get('period_rank'),
            data.get('total_staff'),
            data.get('notes')
        ))

    def update(self, kpi_id: int, data: dict) -> bool:
        """Update a KPI record."""
        query = """
            UPDATE kpi_records
            SET cars_sold = ?,
                revenue_generated = ?,
                new_customers = ?,
                contracts_signed = ?,
                target_cars = ?,
                target_revenue = ?,
                cars_achievement_rate = ?,
                revenue_achievement_rate = ?,
                overall_score = ?,
                period_rank = ?,
                total_staff = ?,
                notes = ?
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (
                data.get('cars_sold', 0),
                float(data.get('revenue_generated', 0)),
                data.get('new_customers', 0),
                data.get('contracts_signed', 0),
                data.get('target_cars', 0),
                float(data.get('target_revenue', 0)),
                data.get('cars_achievement_rate', 0),
                data.get('revenue_achievement_rate', 0),
                data.get('overall_score', 0),
                data.get('period_rank'),
                data.get('total_staff'),
                data.get('notes'),
                kpi_id
            ))
            return cursor.rowcount > 0

    def update_rank(self, kpi_id: int, rank: int, total_staff: int) -> bool:
        """Update the rank for a KPI record."""
        query = """
            UPDATE kpi_records
            SET period_rank = ?, total_staff = ?
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (rank, total_staff, kpi_id))
            return cursor.rowcount > 0

    def delete(self, kpi_id: int) -> bool:
        """Delete a KPI record."""
        query = "DELETE FROM kpi_records WHERE id = ?"
        rows = self.db.execute(query, (kpi_id,))
        return rows > 0


class KPITargetRepository:
    """Repository for KPI target operations."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def get_by_id(self, target_id: int) -> Optional[KPITarget]:
        """Get target by ID."""
        query = "SELECT * FROM kpi_targets WHERE id = ?"
        result = self.db.fetch_one(query, (target_id,))
        return KPITarget.from_dict(result) if result else None

    def get_by_user_and_period(self, user_id: int, period_type: str,
                               target_period: str) -> Optional[dict]:
        """Get target for a user and period."""
        query = """
            SELECT * FROM kpi_targets
            WHERE user_id = ? AND period_type = ? AND target_period = ?
        """
        return self.db.fetch_one(query, (user_id, period_type, target_period))

    def get_by_user(self, user_id: int, period_type: str = None) -> List[dict]:
        """Get all targets for a user."""
        if period_type:
            query = """
                SELECT * FROM kpi_targets
                WHERE user_id = ? AND period_type = ?
                ORDER BY target_period DESC
            """
            return self.db.fetch_all(query, (user_id, period_type))
        else:
            query = """
                SELECT * FROM kpi_targets
                WHERE user_id = ?
                ORDER BY target_period DESC
            """
            return self.db.fetch_all(query, (user_id,))

    def get_all_targets(self, period_type: str = 'monthly',
                        target_period: str = None) -> List[dict]:
        """Get all targets with user info."""
        if target_period:
            query = """
                SELECT t.*, u.full_name, u.username
                FROM kpi_targets t
                JOIN users u ON t.user_id = u.id
                WHERE t.period_type = ? AND t.target_period = ?
                ORDER BY u.full_name
            """
            return self.db.fetch_all(query, (period_type, target_period))
        else:
            query = """
                SELECT t.*, u.full_name, u.username
                FROM kpi_targets t
                JOIN users u ON t.user_id = u.id
                WHERE t.period_type = ?
                ORDER BY t.target_period DESC, u.full_name
            """
            return self.db.fetch_all(query, (period_type,))

    def create(self, data: dict) -> int:
        """Create a new KPI target."""
        query = """
            INSERT INTO kpi_targets (
                user_id, period_type, target_period,
                sales_target, revenue_target, new_customer_target,
                description, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            data['user_id'],
            data.get('period_type', 'monthly'),
            data['target_period'],
            data.get('sales_target', 0),
            float(data.get('revenue_target', 0)),
            data.get('new_customer_target', 0),
            data.get('description'),
            data.get('created_by')
        ))

    def update(self, target_id: int, data: dict) -> bool:
        """Update a KPI target."""
        query = """
            UPDATE kpi_targets
            SET sales_target = ?,
                revenue_target = ?,
                new_customer_target = ?,
                description = ?
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (
                data.get('sales_target', 0),
                float(data.get('revenue_target', 0)),
                data.get('new_customer_target', 0),
                data.get('description'),
                target_id
            ))
            return cursor.rowcount > 0

    def delete(self, target_id: int) -> bool:
        """Delete a KPI target."""
        query = "DELETE FROM kpi_targets WHERE id = ?"
        rows = self.db.execute(query, (target_id,))
        return rows > 0

    def set_bulk_targets(self, user_ids: List[int], data: dict) -> int:
        """Set targets for multiple users."""
        query = """
            INSERT INTO kpi_targets (
                user_id, period_type, target_period,
                sales_target, revenue_target, new_customer_target,
                description, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, period_type, target_period) DO UPDATE SET
                sales_target = excluded.sales_target,
                revenue_target = excluded.revenue_target,
                new_customer_target = excluded.new_customer_target,
                description = excluded.description
        """
        params = [
            (uid, data['period_type'], data['target_period'],
             data['sales_target'], float(data['revenue_target']),
             data['new_customer_target'], data.get('description'),
             data.get('created_by'))
            for uid in user_ids
        ]
        self.db.execute_many(query, params)
        return len(user_ids)
