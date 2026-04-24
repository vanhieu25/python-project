"""
Customer History Service Module
Provides business logic for customer history and transaction tracking.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..repositories.customer_history_repository import CustomerHistoryRepository
from ..repositories.customer_repository import CustomerRepository


class CustomerHistoryService:
    """Service for customer history and transaction tracking."""

    def __init__(self, history_repo: CustomerHistoryRepository,
                 customer_repo: CustomerRepository,
                 contract_repo=None):  # Will be injected later
        """Initialize service.

        Args:
            history_repo: CustomerHistoryRepository instance
            customer_repo: CustomerRepository instance
            contract_repo: Contract repository (optional, for future use)
        """
        self.history_repo = history_repo
        self.customer_repo = customer_repo
        self.contract_repo = contract_repo

    def get_full_history(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get complete customer history.

        Returns:
            Dictionary containing:
            - profile_changes: List of profile edit history
            - contracts: List of contracts
            - timeline: Combined timeline of all activities
            - summary: Transaction summary
            or None if customer not found
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return None

        # Get profile history
        profile_changes = self.history_repo.get_history(customer_id)

        # Get contracts (if contract repo available)
        contracts = []
        if self.contract_repo:
            try:
                contracts = self.contract_repo.get_by_customer(customer_id)
            except Exception:
                contracts = []
        else:
            # Use customer_repo.get_contracts as fallback
            try:
                contracts = self.customer_repo.get_contracts(customer_id)
            except Exception:
                contracts = []

        # Build timeline
        timeline = self._build_timeline(profile_changes, contracts)

        # Get summary
        try:
            summary = self._get_transaction_summary(customer_id, contracts)
        except Exception:
            summary = {
                'total_contracts': 0,
                'total_value': 0,
                'average_value': 0,
                'status_breakdown': {},
                'last_transaction_date': None
            }

        return {
            'customer': customer,
            'profile_changes': profile_changes,
            'contracts': contracts,
            'timeline': timeline,
            'summary': summary
        }

    def _build_timeline(self, profile_changes: List[Dict],
                       contracts: List[Any]) -> List[Dict]:
        """Build unified timeline from all activities.

        Args:
            profile_changes: List of profile change records
            contracts: List of contracts

        Returns:
            Sorted timeline of activities
        """
        timeline = []

        # Add profile changes
        for change in profile_changes:
            timeline.append({
                'type': 'profile',
                'action': change['action'],
                'description': self._format_profile_change(change),
                'timestamp': change['changed_at'],
                'user': change.get('changed_by_name', 'Unknown'),
                'icon': self._get_action_icon(change['action'])
            })

        # Add contracts
        for contract in contracts:
            contract_code = contract.get('contract_code', 'N/A')
            total_amount = contract.get('total_amount', 0)
            created_at = contract.get('created_at')
            created_by = contract.get('created_by_name', 'Unknown')

            timeline.append({
                'type': 'contract',
                'action': 'contract_created',
                'description': f"Tạo hợp đồng {contract_code}",
                'timestamp': created_at,
                'user': created_by,
                'amount': total_amount,
                'icon': '📄'
            })

        # Sort by timestamp (newest first)
        timeline.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)

        return timeline

    def _format_profile_change(self, change: Dict) -> str:
        """Format profile change for display.

        Args:
            change: History change record

        Returns:
            Formatted description string
        """
        action = change['action']
        field = change.get('field_name', '')
        old = change.get('old_value', '')
        new = change.get('new_value', '')

        action_map = {
            'create': 'Tạo mới khách hàng',
            'delete': f"Xóa khách hàng (lý do: {old or 'Không có'})",
            'restore': 'Khôi phục khách hàng'
        }

        if action in action_map:
            return action_map[action]

        if action == 'update' and field:
            field_names = {
                'full_name': 'Họ tên',
                'phone': 'Số điện thoại',
                'email': 'Email',
                'address': 'Địa chỉ',
                'customer_class': 'Phân loại',
                'notes': 'Ghi chú'
            }
            field_name = field_names.get(field, field)
            return f"Cập nhật {field_name}: {old or '(trống)'} → {new or '(trống)'}"

        return f"Thao tác: {action}"

    def _get_action_icon(self, action: str) -> str:
        """Get icon for action type.

        Args:
            action: Action type string

        Returns:
            Icon emoji string
        """
        icons = {
            'create': '👤',
            'update': '✏️',
            'delete': '🗑️',
            'restore': '↩️'
        }
        return icons.get(action, '📝')

    def _get_transaction_summary(self, customer_id: int,
                                contracts: List[Dict]) -> Dict[str, Any]:
        """Calculate transaction summary.

        Args:
            customer_id: Customer ID
            contracts: List of contracts

        Returns:
            Summary dictionary
        """
        total_contracts = len(contracts)
        total_value = sum(c.get('total_amount', 0) or 0 for c in contracts)

        # Calculate by status
        status_counts = {}
        for contract in contracts:
            status = contract.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Last transaction
        last_transaction = None
        if contracts:
            sorted_contracts = sorted(
                contracts,
                key=lambda x: x.get('created_at') or datetime.min,
                reverse=True
            )
            last_transaction = sorted_contracts[0].get('created_at') if sorted_contracts else None

        return {
            'total_contracts': total_contracts,
            'total_value': total_value,
            'average_value': total_value / total_contracts if total_contracts > 0 else 0,
            'status_breakdown': status_counts,
            'last_transaction_date': last_transaction
        }

    def export_history(self, customer_id: int,
                      format: str = 'csv') -> Optional[str]:
        """Export customer history to file.

        Args:
            customer_id: Customer ID
            format: 'csv' or 'json'

        Returns:
            File path of exported file or None if failed
        """
        import csv
        import json
        import os
        import tempfile

        history = self.get_full_history(customer_id)
        if not history:
            return None

        customer = history['customer']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create exports directory if not exists
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)

        filename = f"customer_{customer.customer_code}_{timestamp}.{format}"
        filepath = os.path.join(exports_dir, filename)

        if format == 'csv':
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Thời gian', 'Loại', 'Hành động', 'Mô tả', 'Người thực hiện'])
                for item in history['timeline']:
                    writer.writerow([
                        item['timestamp'],
                        item['type'],
                        item['action'],
                        item['description'],
                        item['user']
                    ])
        else:  # json
            # Convert customer to dict for serialization
            history_dict = {
                'profile_changes': history['profile_changes'],
                'contracts': history['contracts'],
                'timeline': history['timeline'],
                'summary': history['summary']
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_dict, f, indent=2, default=str, ensure_ascii=False)

        return filepath

    def get_customer_statistics(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer transaction statistics.

        Args:
            customer_id: Customer ID

        Returns:
            Statistics dictionary or None if customer not found
        """
        history = self.get_full_history(customer_id)
        if not history:
            return None

        summary = history['summary']

        # Calculate VIP score
        total_value = summary.get('total_value', 0) or 0
        total_contracts = summary.get('total_contracts', 0) or 0

        vip_score = 0
        if total_value >= 2000000000:  # 2 tỷ
            vip_score += 50
        elif total_value >= 1000000000:  # 1 tỷ
            vip_score += 30
        elif total_value >= 500000000:  # 500 triệu
            vip_score += 15

        vip_score += min(total_contracts * 10, 50)  # Max 50 points from contracts

        return {
            'total_contracts': total_contracts,
            'total_value': total_value,
            'vip_score': vip_score,
            'tier': 'VIP' if vip_score >= 60 else 'Regular' if vip_score >= 30 else 'Potential'
        }
