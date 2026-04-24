"""
KPI Service for calculating and managing employee performance metrics.
Sprint 0.4: Employee KPI
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from src.repositories.kpi_repository import KPIRepository, KPITargetRepository
from src.repositories.user_repository import UserRepository
from src.models.kpi import KPIRecord, PerformanceSummary


class KPIServiceError(Exception):
    """Base exception for KPI service errors."""
    pass


class InvalidPeriodError(KPIServiceError):
    """Raised when period format is invalid."""
    pass


class KPIService:
    """Service for managing KPI calculations and reports."""

    # Weights for overall score calculation
    CARS_WEIGHT = 0.4
    REVENUE_WEIGHT = 0.6

    def __init__(
        self,
        kpi_repo: KPIRepository,
        target_repo: KPITargetRepository,
        user_repo: UserRepository
    ):
        self.kpi_repo = kpi_repo
        self.target_repo = target_repo
        self.user_repo = user_repo

    def calculate_achievement_rate(self, actual: float, target: float) -> float:
        """
        Calculate achievement rate as percentage.

        Args:
            actual: Actual value achieved
            target: Target value

        Returns:
            Achievement rate as percentage (capped at 999.99%)
        """
        if target == 0:
            return 100.0 if actual > 0 else 0.0
        return min((actual / target) * 100, 999.99)

    def calculate_overall_score(self,
                                 cars_achievement: float,
                                 revenue_achievement: float) -> float:
        """
        Calculate weighted overall score.

        Args:
            cars_achievement: Cars achievement rate
            revenue_achievement: Revenue achievement rate

        Returns:
            Weighted overall score
        """
        return round(
            cars_achievement * self.CARS_WEIGHT +
            revenue_achievement * self.REVENUE_WEIGHT,
            2
        )

    def get_performance_rating(self, overall_score: float) -> str:
        """
        Get performance rating based on overall score.

        Args:
            overall_score: Overall performance score

        Returns:
            Performance rating string
        """
        if overall_score >= 120:
            return "Xuất sắc"
        elif overall_score >= 100:
            return "Tốt"
        elif overall_score >= 80:
            return "Đạt"
        elif overall_score >= 60:
            return "Cần cải thiện"
        else:
            return "Kém"

    def calculate_monthly_kpi(
        self,
        user_id: int,
        year: int,
        month: int,
        cars_sold: int = 0,
        revenue_generated: Decimal = Decimal('0'),
        new_customers: int = 0,
        contracts_signed: int = 0
    ) -> KPIRecord:
        """
        Calculate KPI for a specific month.

        Args:
            user_id: User ID
            year: Year
            month: Month (1-12)
            cars_sold: Number of cars sold
            revenue_generated: Total revenue generated
            new_customers: Number of new customers
            contracts_signed: Number of contracts signed

        Returns:
            KPIRecord with calculated metrics
        """
        period_value = f"{year}-{month:02d}"

        # Get targets for the period
        target = self.target_repo.get_by_user_and_period(
            user_id, 'monthly', period_value
        )

        target_cars = target['sales_target'] if target else 0
        target_revenue = Decimal(str(target['revenue_target'])) if target else Decimal('0')

        # Calculate achievement rates
        cars_achievement = self.calculate_achievement_rate(
            float(cars_sold), float(target_cars)
        )
        revenue_achievement = self.calculate_achievement_rate(
            float(revenue_generated), float(target_revenue)
        )

        # Calculate overall score
        overall_score = self.calculate_overall_score(
            cars_achievement, revenue_achievement
        )

        # Check if record exists
        existing = self.kpi_repo.get_by_user_and_period(
            user_id, 'monthly', period_value
        )

        kpi_data = {
            'user_id': user_id,
            'period_type': 'monthly',
            'period_value': period_value,
            'cars_sold': cars_sold,
            'revenue_generated': revenue_generated,
            'new_customers': new_customers,
            'contracts_signed': contracts_signed,
            'target_cars': target_cars,
            'target_revenue': target_revenue,
            'cars_achievement_rate': cars_achievement,
            'revenue_achievement_rate': revenue_achievement,
            'overall_score': overall_score
        }

        if existing:
            self.kpi_repo.update(existing['id'], kpi_data)
            kpi_data['id'] = existing['id']
        else:
            kpi_id = self.kpi_repo.create(kpi_data)
            kpi_data['id'] = kpi_id

        # Update user totals
        self._update_user_totals(user_id)

        # Recalculate rankings
        self._recalculate_rankings('monthly', period_value)

        return KPIRecord.from_dict(kpi_data)

    def _update_user_totals(self, user_id: int) -> None:
        """Update cumulative totals in users table."""
        # Get all KPI records for user
        kpi_records = self.kpi_repo.get_by_user(user_id, limit=1000)

        total_sales = sum(r['cars_sold'] for r in kpi_records)
        total_revenue = sum(Decimal(str(r['revenue_generated'])) for r in kpi_records)

        # Update user record (handle case where columns might not exist)
        query = """
            UPDATE users
            SET total_sales = ?,
                total_revenue = ?,
                last_kpi_update = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        try:
            self.kpi_repo.db.execute(query, (
                total_sales,
                float(total_revenue),
                user_id
            ))
        except Exception:
            # Columns might not exist in older databases
            pass

    def _recalculate_rankings(self, period_type: str, period_value: str) -> None:
        """Recalculate rankings for all staff in a period."""
        all_kpis = self.kpi_repo.get_all_by_period(period_type, period_value)

        # Sort by overall_score descending
        sorted_kpis = sorted(
            all_kpis,
            key=lambda x: x['overall_score'],
            reverse=True
        )

        # Assign ranks
        total_staff = len(sorted_kpis)
        for rank, kpi in enumerate(sorted_kpis, start=1):
            self.kpi_repo.update_rank(kpi['id'], rank, total_staff)

    def get_performance_ranking(
        self,
        period_type: str,
        period_value: str,
        limit: int = 10
    ) -> List[PerformanceSummary]:
        """
        Get top performers for a period.

        Args:
            period_type: 'monthly', 'quarterly', or 'yearly'
            period_value: Period value (e.g., '2024-01', '2024-Q1')
            limit: Maximum number of results

        Returns:
            List of PerformanceSummary objects
        """
        top_kpis = self.kpi_repo.get_top_performers(
            period_type, period_value, limit
        )

        results = []
        for kpi in top_kpis:
            user = self.user_repo.get_by_id(kpi['user_id'])
            if not user:
                continue

            # Determine trend
            prev_period = self._get_previous_period(period_type, period_value)
            prev_kpi = self.kpi_repo.get_by_user_and_period(
                kpi['user_id'], period_type, prev_period
            )

            trend = 'stable'
            if prev_kpi:
                prev_score = prev_kpi['overall_score']
                curr_score = kpi['overall_score']
                if curr_score > prev_score * 1.05:
                    trend = 'up'
                elif curr_score < prev_score * 0.95:
                    trend = 'down'

            results.append(PerformanceSummary(
                user_id=kpi['user_id'],
                user_name=user.full_name,
                period=period_value,
                cars_sold=kpi['cars_sold'],
                target_cars=kpi['target_cars'],
                cars_achievement=kpi['cars_achievement_rate'],
                revenue=Decimal(str(kpi['revenue_generated'])),
                target_revenue=Decimal(str(kpi['target_revenue'])),
                revenue_achievement=kpi['revenue_achievement_rate'],
                overall_score=kpi['overall_score'],
                rank=kpi['period_rank'] or 0,
                trend=trend
            ))

        return results

    def compare_with_peers(
        self,
        user_id: int,
        period_type: str,
        period_value: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare user's performance with team average.

        Args:
            user_id: User ID to compare
            period_type: Period type
            period_value: Period value

        Returns:
            Comparison dictionary or None if no data
        """
        user_kpi = self.kpi_repo.get_by_user_and_period(
            user_id, period_type, period_value
        )

        if not user_kpi:
            return None

        team_avg = self.kpi_repo.get_team_average(period_type, period_value)

        return {
            'user': {
                'cars_sold': user_kpi['cars_sold'],
                'revenue': float(user_kpi['revenue_generated']),
                'overall_score': user_kpi['overall_score'],
                'rank': user_kpi['period_rank'],
                'cars_achievement': user_kpi['cars_achievement_rate'],
                'revenue_achievement': user_kpi['revenue_achievement_rate']
            },
            'team_average': team_avg,
            'comparison': {
                'cars_vs_avg': (
                    (user_kpi['cars_sold'] / team_avg['avg_cars'] - 1) * 100
                    if team_avg['avg_cars'] > 0 else 0
                ),
                'revenue_vs_avg': (
                    (float(user_kpi['revenue_generated']) /
                     team_avg['avg_revenue'] - 1) * 100
                    if team_avg['avg_revenue'] > 0 else 0
                ),
                'score_vs_avg': (
                    (user_kpi['overall_score'] / team_avg['avg_score'] - 1) * 100
                    if team_avg['avg_score'] > 0 else 0
                )
            }
        }

    def generate_kpi_report(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Generate comprehensive KPI report.

        Args:
            user_id: User ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            Report dictionary or None if no data
        """
        records = self.kpi_repo.get_by_date_range(user_id, start_date, end_date)

        if not records:
            return None

        total_cars = sum(r['cars_sold'] for r in records)
        total_revenue = sum(Decimal(str(r['revenue_generated'])) for r in records)
        avg_score = sum(r['overall_score'] for r in records) / len(records)

        best_month = max(records, key=lambda r: r['overall_score'])
        worst_month = min(records, key=lambda r: r['overall_score'])

        # Calculate achievement trend
        scores = [r['overall_score'] for r in sorted(records, key=lambda x: x['period_value'])]
        trend = 'stable'
        if len(scores) >= 2:
            first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            if second_half > first_half * 1.05:
                trend = 'improving'
            elif second_half < first_half * 0.95:
                trend = 'declining'

        return {
            'period': f"{start_date} to {end_date}",
            'summary': {
                'total_cars_sold': total_cars,
                'total_revenue': float(total_revenue),
                'average_score': round(avg_score, 2),
                'months_count': len(records),
                'trend': trend
            },
            'best_performance': {
                'month': best_month['period_value'],
                'score': best_month['overall_score'],
                'cars': best_month['cars_sold'],
                'revenue': float(best_month['revenue_generated'])
            },
            'worst_performance': {
                'month': worst_month['period_value'],
                'score': worst_month['overall_score'],
                'cars': worst_month['cars_sold'],
                'revenue': float(worst_month['revenue_generated'])
            },
            'monthly_data': records
        }

    def get_kpi_trend(
        self,
        user_id: int,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get KPI trend over time.

        Args:
            user_id: User ID
            months: Number of months to include

        Returns:
            List of monthly KPI data
        """
        records = self.kpi_repo.get_by_user(user_id, 'monthly', limit=months)
        return sorted(records, key=lambda x: x['period_value'])

    def set_kpi_target(
        self,
        user_id: int,
        period_type: str,
        target_period: str,
        sales_target: int,
        revenue_target: Decimal,
        new_customer_target: int = 0,
        description: str = None,
        created_by: int = None
    ) -> int:
        """
        Set KPI target for a user.

        Args:
            user_id: User ID
            period_type: 'monthly', 'quarterly', or 'yearly'
            target_period: Target period value
            sales_target: Target number of cars
            revenue_target: Target revenue
            new_customer_target: Target new customers
            description: Optional description
            created_by: ID of user creating the target

        Returns:
            Target ID
        """
        # Check if target exists
        existing = self.target_repo.get_by_user_and_period(
            user_id, period_type, target_period
        )

        data = {
            'user_id': user_id,
            'period_type': period_type,
            'target_period': target_period,
            'sales_target': sales_target,
            'revenue_target': revenue_target,
            'new_customer_target': new_customer_target,
            'description': description,
            'created_by': created_by
        }

        if existing:
            self.target_repo.update(existing['id'], data)
            return existing['id']
        else:
            return self.target_repo.create(data)

    def _get_previous_period(self, period_type: str, period_value: str) -> str:
        """Get the previous period string."""
        if period_type == 'monthly':
            year, month = map(int, period_value.split('-'))
            if month == 1:
                return f"{year-1}-12"
            else:
                return f"{year}-{month-1:02d}"
        elif period_type == 'quarterly':
            year, quarter = period_value.split('-Q')
            year = int(year)
            quarter = int(quarter)
            if quarter == 1:
                return f"{year-1}-Q4"
            else:
                return f"{year}-Q{quarter-1}"
        elif period_type == 'yearly':
            year = int(period_value)
            return str(year - 1)
        return period_value

    def get_current_period(self, period_type: str = 'monthly') -> str:
        """Get current period string."""
        today = date.today()
        if period_type == 'monthly':
            return f"{today.year}-{today.month:02d}"
        elif period_type == 'quarterly':
            quarter = (today.month - 1) // 3 + 1
            return f"{today.year}-Q{quarter}"
        elif period_type == 'yearly':
            return str(today.year)
        return str(today)
