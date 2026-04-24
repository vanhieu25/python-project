"""
Customer Classification Service Module
Provides business logic for customer classification.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..repositories.customer_repository import CustomerRepository
from ..repositories.customer_classification_repository import CustomerClassificationRepository


@dataclass
class ClassificationRule:
    """Customer classification rule."""
    id: int
    rule_name: str
    customer_class: str
    min_contracts: int
    min_total_value: float
    min_avg_value: float
    min_frequency_months: Optional[int]
    priority: int


@dataclass
class CustomerMetrics:
    """Customer transaction metrics."""
    total_contracts: int
    total_value: float
    avg_value: float
    first_contract_date: Optional[datetime]
    last_contract_date: Optional[datetime]
    frequency_months: Optional[float]


class CustomerClassificationService:
    """Service for customer classification."""

    def __init__(self, customer_repo: CustomerRepository,
                 classification_repo: CustomerClassificationRepository):
        """Initialize service.

        Args:
            customer_repo: CustomerRepository instance
            classification_repo: CustomerClassificationRepository instance
        """
        self.customer_repo = customer_repo
        self.classification_repo = classification_repo

    def classify_customer(self, customer_id: int,
                         changed_by: Optional[int] = None,
                         reason: str = 'auto') -> str:
        """Classify a single customer.

        Args:
            customer_id: Customer ID
            changed_by: User ID who made the change (None for auto)
            reason: Reason for classification

        Returns:
            New classification ('vip', 'regular', 'potential')
        """
        # Get customer metrics
        metrics = self._calculate_metrics(customer_id)

        # Get active rules sorted by priority
        rules = self.classification_repo.get_active_rules()

        # Apply rules
        new_class = 'potential'  # Default
        matched_rule = None

        for rule in rules:
            if self._matches_rule(metrics, rule):
                new_class = rule.customer_class
                matched_rule = rule
                break  # Apply first matching rule (highest priority)

        # Update if changed
        customer = self.customer_repo.get_by_id(customer_id)
        if customer and customer.customer_class != new_class:
            self._update_classification(
                customer_id,
                customer.customer_class,
                new_class,
                reason,
                changed_by,
                matched_rule.id if matched_rule else None
            )

        return new_class

    def classify_all_customers(self) -> Dict[str, int]:
        """Classify all customers and return statistics.

        Returns:
            Dict with counts for each class
        """
        customers = self.customer_repo.get_all()
        stats = {'vip': 0, 'regular': 0, 'potential': 0, 'changed': 0}

        for customer in customers:
            old_class = customer.customer_class
            new_class = self.classify_customer(customer.id, reason='auto_batch')

            stats[new_class] += 1
            if old_class != new_class:
                stats['changed'] += 1

        return stats

    def manual_classify(self, customer_id: int, new_class: str,
                       changed_by: int, reason: str) -> bool:
        """Manually classify a customer.

        Args:
            customer_id: Customer ID
            new_class: New classification
            changed_by: User ID
            reason: Reason for manual classification

        Returns:
            True if successful

        Raises:
            ValueError: If invalid class
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return False

        if new_class not in ['vip', 'regular', 'potential']:
            raise ValueError(f"Invalid class: {new_class}")

        if customer.customer_class == new_class:
            return True  # No change needed

        self._update_classification(
            customer_id,
            customer.customer_class,
            new_class,
            f'manual: {reason}',
            changed_by,
            None
        )

        return True

    def _calculate_metrics(self, customer_id: int) -> CustomerMetrics:
        """Calculate customer transaction metrics.

        Args:
            customer_id: Customer ID

        Returns:
            CustomerMetrics instance
        """
        summary = self.customer_repo.get_transaction_summary(customer_id)
        contracts = self.customer_repo.get_contracts(customer_id)

        total_contracts = summary.get('total_contracts', 0) or 0
        total_value = summary.get('total_value', 0) or 0
        avg_value = total_value / total_contracts if total_contracts > 0 else 0

        # Calculate dates
        first_date = None
        last_date = None
        if contracts:
            dates = []
            for c in contracts:
                if c.get('created_at'):
                    d = c['created_at']
                    if isinstance(d, str):
                        try:
                            d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            continue
                    dates.append(d)
            if dates:
                first_date = min(dates)
                last_date = max(dates)

        # Calculate frequency
        frequency = None
        if total_contracts > 1 and first_date and last_date:
            days = (last_date - first_date).days
            months = days / 30.0
            frequency = months / (total_contracts - 1) if total_contracts > 1 else None

        return CustomerMetrics(
            total_contracts=total_contracts,
            total_value=total_value,
            avg_value=avg_value,
            first_contract_date=first_date,
            last_contract_date=last_date,
            frequency_months=frequency
        )

    def _matches_rule(self, metrics: CustomerMetrics,
                     rule: ClassificationRule) -> bool:
        """Check if customer matches a classification rule.

        Args:
            metrics: Customer metrics
            rule: Classification rule

        Returns:
            True if matches
        """
        # Check minimum contracts
        if metrics.total_contracts < rule.min_contracts:
            return False

        # Check minimum total value
        if metrics.total_value < rule.min_total_value:
            return False

        # Check minimum average value
        if rule.min_avg_value > 0 and metrics.avg_value < rule.min_avg_value:
            return False

        # Check frequency (if specified)
        if rule.min_frequency_months is not None:
            if metrics.frequency_months is None:
                return False
            if metrics.frequency_months > rule.min_frequency_months:
                return False

        return True

    def _update_classification(self, customer_id: int, old_class: str,
                              new_class: str, reason: str,
                              changed_by: Optional[int],
                              rule_id: Optional[int]):
        """Update customer classification.

        Args:
            customer_id: Customer ID
            old_class: Old classification
            new_class: New classification
            reason: Reason for change
            changed_by: User ID who made the change
            rule_id: Triggering rule ID
        """
        # Update customer
        self.customer_repo.update(customer_id, {
            'customer_class': new_class
        })

        # Record history
        self.classification_repo.record_classification_change(
            customer_id, old_class, new_class, reason, changed_by, rule_id
        )

        # Check if should notify (upgraded to VIP)
        if new_class == 'vip' and old_class != 'vip':
            self._notify_vip_upgrade(customer_id)

    def _notify_vip_upgrade(self, customer_id: int):
        """Notify when customer is upgraded to VIP.

        Args:
            customer_id: Customer ID
        """
        # Implementation depends on notification system
        # For now, just log
        customer = self.customer_repo.get_by_id(customer_id)
        if customer:
            print(f"Customer {customer.full_name} ({customer.customer_code}) upgraded to VIP!")

    def get_classification_report(self) -> Dict[str, Any]:
        """Get classification report.

        Returns:
            Report dictionary with statistics
        """
        customers = self.customer_repo.get_all()

        stats = {
            'vip': {'count': 0, 'total_value': 0, 'avg_value': 0},
            'regular': {'count': 0, 'total_value': 0, 'avg_value': 0},
            'potential': {'count': 0, 'total_value': 0, 'avg_value': 0}
        }

        for customer in customers:
            c_class = customer.customer_class or 'potential'
            if c_class not in stats:
                c_class = 'potential'
            summary = self.customer_repo.get_transaction_summary(customer.id)
            total_value = summary.get('total_value', 0) or 0

            stats[c_class]['count'] += 1
            stats[c_class]['total_value'] += total_value

        # Calculate averages
        for c_class in stats:
            count = stats[c_class]['count']
            if count > 0:
                stats[c_class]['avg_value'] = stats[c_class]['total_value'] / count

        return {
            'summary': stats,
            'total_customers': len(customers),
            'classification_distribution': {
                c: stats[c]['count'] for c in stats
            }
        }

    def get_vip_benefits(self, customer_class: str) -> List[Dict]:
        """Get benefits for a customer class.

        Args:
            customer_class: Customer class

        Returns:
            List of benefits
        """
        return self.classification_repo.get_benefits(customer_class)

    def should_check_classification(self, customer_id: int) -> bool:
        """Check if customer classification should be re-evaluated.

        Returns True if:
        - No classification history
        - Last classification was more than 30 days ago
        - Customer had new transaction since last classification

        Args:
            customer_id: Customer ID

        Returns:
            True if should re-evaluate
        """
        last_check = self.classification_repo.get_last_classification_date(customer_id)

        if not last_check:
            return True

        days_since = (datetime.now() - last_check).days
        return days_since >= 30

    def get_customer_classification_info(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get full classification info for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            Classification info dictionary or None
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return None

        metrics = self._calculate_metrics(customer_id)
        benefits = self.get_vip_benefits(customer.customer_class)

        return {
            'customer': customer,
            'current_class': customer.customer_class,
            'metrics': {
                'total_contracts': metrics.total_contracts,
                'total_value': metrics.total_value,
                'avg_value': metrics.avg_value,
                'frequency_months': metrics.frequency_months
            },
            'benefits': benefits
        }


class ClassificationRuleManager:
    """Manager for classification rules."""

    def __init__(self, classification_repo: CustomerClassificationRepository):
        """Initialize manager.

        Args:
            classification_repo: Classification repository
        """
        self.repo = classification_repo

    def create_rule(self, rule_data: Dict[str, Any]) -> int:
        """Create a new classification rule.

        Args:
            rule_data: Rule data dictionary

        Returns:
            ID of created rule
        """
        return self.repo.create_rule(rule_data)

    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Update a classification rule.

        Args:
            rule_id: Rule ID
            rule_data: Updated rule data

        Returns:
            True if successful
        """
        return self.repo.update_rule(rule_id, rule_data)

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a classification rule.

        Args:
            rule_id: Rule ID

        Returns:
            True if successful
        """
        return self.repo.delete_rule(rule_id)

    def get_rules(self, customer_class: Optional[str] = None) -> List[ClassificationRule]:
        """Get classification rules.

        Args:
            customer_class: Filter by customer class

        Returns:
            List of classification rules
        """
        return self.repo.get_rules(customer_class)

    def get_rule_by_id(self, rule_id: int) -> Optional[ClassificationRule]:
        """Get a rule by ID.

        Args:
            rule_id: Rule ID

        Returns:
            Classification rule or None
        """
        return self.repo.get_rule_by_id(rule_id)

    def reorder_rules(self, rule_ids: List[int]) -> bool:
        """Reorder rules by priority.

        Args:
            rule_ids: List of rule IDs in new order

        Returns:
            True if successful
        """
        return self.repo.reorder_rules(rule_ids)
