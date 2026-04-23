"""
KPI models for Employee Performance Tracking.
Sprint 0.4: Employee KPI
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class KPIRecord:
    """KPI Record dataclass for tracking employee performance."""
    id: int
    user_id: int
    period_type: str  # monthly, quarterly, yearly
    period_value: str  # '2024-01', '2024-Q1', '2024'

    # Actual metrics
    cars_sold: int = 0
    revenue_generated: Decimal = field(default_factory=lambda: Decimal('0'))
    new_customers: int = 0
    contracts_signed: int = 0

    # Targets
    target_cars: int = 0
    target_revenue: Decimal = field(default_factory=lambda: Decimal('0'))

    # Achievement rates
    cars_achievement_rate: float = 0.0
    revenue_achievement_rate: float = 0.0
    overall_score: float = 0.0

    # Ranking
    period_rank: Optional[int] = None
    total_staff: Optional[int] = None

    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict) -> 'KPIRecord':
        """Create KPIRecord from dictionary."""
        if not data:
            raise ValueError("Cannot create KPIRecord from empty data")

        return cls(
            id=data['id'],
            user_id=data['user_id'],
            period_type=data.get('period_type', 'monthly'),
            period_value=data['period_value'],
            cars_sold=data.get('cars_sold', 0),
            revenue_generated=Decimal(str(data.get('revenue_generated', 0))),
            new_customers=data.get('new_customers', 0),
            contracts_signed=data.get('contracts_signed', 0),
            target_cars=data.get('target_cars', 0),
            target_revenue=Decimal(str(data.get('target_revenue', 0))),
            cars_achievement_rate=data.get('cars_achievement_rate', 0.0),
            revenue_achievement_rate=data.get('revenue_achievement_rate', 0.0),
            overall_score=data.get('overall_score', 0.0),
            period_rank=data.get('period_rank'),
            total_staff=data.get('total_staff'),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data['created_at'])
            if isinstance(data.get('created_at'), str)
            else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at'])
            if isinstance(data.get('updated_at'), str)
            else data.get('updated_at', datetime.now())
        )

    def to_dict(self) -> dict:
        """Convert KPIRecord to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period_type': self.period_type,
            'period_value': self.period_value,
            'cars_sold': self.cars_sold,
            'revenue_generated': float(self.revenue_generated),
            'new_customers': self.new_customers,
            'contracts_signed': self.contracts_signed,
            'target_cars': self.target_cars,
            'target_revenue': float(self.target_revenue),
            'cars_achievement_rate': self.cars_achievement_rate,
            'revenue_achievement_rate': self.revenue_achievement_rate,
            'overall_score': self.overall_score,
            'period_rank': self.period_rank,
            'total_staff': self.total_staff,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else self.created_at,
            'updated_at': self.updated_at.isoformat()
            if isinstance(self.updated_at, datetime)
            else self.updated_at
        }

    @property
    def performance_rating(self) -> str:
        """Get performance rating based on overall score."""
        if self.overall_score >= 120:
            return "Xuất sắc"  # Excellent
        elif self.overall_score >= 100:
            return "Tốt"  # Good
        elif self.overall_score >= 80:
            return "Đạt"  # Average
        elif self.overall_score >= 60:
            return "Cần cải thiện"  # Below Average
        else:
            return "Kém"  # Poor


@dataclass
class KPITarget:
    """KPI Target dataclass for setting performance targets."""
    id: int
    user_id: int
    period_type: str  # monthly, quarterly, yearly
    target_period: str  # '2024-01', '2024-Q1', '2024'

    sales_target: int = 0
    revenue_target: Decimal = field(default_factory=lambda: Decimal('0'))
    new_customer_target: int = 0

    description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict) -> 'KPITarget':
        """Create KPITarget from dictionary."""
        if not data:
            raise ValueError("Cannot create KPITarget from empty data")

        return cls(
            id=data['id'],
            user_id=data['user_id'],
            period_type=data.get('period_type', 'monthly'),
            target_period=data['target_period'],
            sales_target=data.get('sales_target', 0),
            revenue_target=Decimal(str(data.get('revenue_target', 0))),
            new_customer_target=data.get('new_customer_target', 0),
            description=data.get('description'),
            created_by=data.get('created_by'),
            created_at=datetime.fromisoformat(data['created_at'])
            if isinstance(data.get('created_at'), str)
            else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at'])
            if isinstance(data.get('updated_at'), str)
            else data.get('updated_at', datetime.now())
        )

    def to_dict(self) -> dict:
        """Convert KPITarget to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period_type': self.period_type,
            'target_period': self.target_period,
            'sales_target': self.sales_target,
            'revenue_target': float(self.revenue_target),
            'new_customer_target': self.new_customer_target,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else self.created_at,
            'updated_at': self.updated_at.isoformat()
            if isinstance(self.updated_at, datetime)
            else self.updated_at
        }


@dataclass
class PerformanceSummary:
    """Performance summary for ranking and comparison."""
    user_id: int
    user_name: str
    period: str
    cars_sold: int
    target_cars: int
    cars_achievement: float
    revenue: Decimal
    target_revenue: Decimal
    revenue_achievement: float
    overall_score: float
    rank: int
    trend: str  # up, down, stable

    @classmethod
    def from_kpi_record(cls, kpi: KPIRecord, user_name: str, trend: str = 'stable') -> 'PerformanceSummary':
        """Create PerformanceSummary from KPIRecord."""
        return cls(
            user_id=kpi.user_id,
            user_name=user_name,
            period=kpi.period_value,
            cars_sold=kpi.cars_sold,
            target_cars=kpi.target_cars,
            cars_achievement=kpi.cars_achievement_rate,
            revenue=kpi.revenue_generated,
            target_revenue=kpi.target_revenue,
            revenue_achievement=kpi.revenue_achievement_rate,
            overall_score=kpi.overall_score,
            rank=kpi.period_rank or 0,
            trend=trend
        )

    def to_dict(self) -> dict:
        """Convert PerformanceSummary to dictionary."""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'period': self.period,
            'cars_sold': self.cars_sold,
            'target_cars': self.target_cars,
            'cars_achievement': self.cars_achievement,
            'revenue': float(self.revenue),
            'target_revenue': float(self.target_revenue),
            'revenue_achievement': self.revenue_achievement,
            'overall_score': self.overall_score,
            'rank': self.rank,
            'trend': self.trend
        }
