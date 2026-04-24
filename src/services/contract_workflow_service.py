"""
Contract Workflow Service Module
Manages contract approval workflow and state transitions.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

from models.contract import Contract
from repositories.contract_repository import ContractRepository


class ContractStatus(Enum):
    """Contract status enumeration."""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    SIGNED = 'signed'
    PAID = 'paid'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class WorkflowResult:
    """Result wrapper for workflow operations."""

    def __init__(self, success: bool, message: str = None, data: Any = None):
        self.success = success
        self.message = message
        self.data = data

    @classmethod
    def ok(cls, message: str = None, data: Any = None) -> 'WorkflowResult':
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, data: Any = None) -> 'WorkflowResult':
        return cls(success=False, message=message, data=data)


class ContractWorkflowService:
    """Service for managing contract approval workflow."""

    # Valid state transitions: from_status -> [allowed_to_statuses]
    VALID_TRANSITIONS = {
        'draft': ['pending', 'cancelled'],
        'pending': ['approved', 'draft', 'cancelled'],  # draft = reject
        'approved': ['signed', 'cancelled'],
        'signed': ['paid', 'cancelled'],
        'paid': ['delivered'],
        'delivered': [],  # Terminal state
        'cancelled': ['draft']  # Can resubmit from cancelled
    }

    # Required permissions for each transition
    # Format: (from, to) -> [allowed_roles]
    TRANSITION_PERMISSIONS = {
        ('draft', 'pending'): ['sales', 'admin', 'manager'],
        ('pending', 'approved'): ['manager', 'admin'],
        ('pending', 'draft'): ['manager', 'admin'],  # Reject
        ('approved', 'signed'): ['sales', 'admin', 'manager'],
        ('signed', 'paid'): ['sales', 'accountant', 'admin', 'manager'],
        ('paid', 'delivered'): ['sales', 'admin', 'manager'],
        ('draft', 'cancelled'): ['sales', 'admin', 'manager'],
        ('pending', 'cancelled'): ['admin', 'manager'],
        ('approved', 'cancelled'): ['admin', 'manager'],
        ('signed', 'cancelled'): ['admin'],
        ('cancelled', 'draft'): ['manager', 'admin']  # Resubmit
    }

    # Required fields before transition
    REQUIRED_FIELDS = {
        'pending': ['customer_name', 'car_brand', 'car_model', 'car_price', 'total_amount'],
        'approved': ['customer_name', 'car_brand', 'car_model',
                     'car_price', 'total_amount', 'final_amount'],
        'signed': [],  # Signature check handled separately in mark_signed
        'paid': [],  # Checked via paid_amount >= final_amount
        'delivered': []  # actual_delivery_date is set by mark_delivered
    }

    def __init__(
        self,
        contract_repo: ContractRepository,
        notification_service=None,
        user_repo=None
    ):
        """Initialize workflow service.

        Args:
            contract_repo: Contract repository instance
            notification_service: Optional notification service
            user_repo: Optional user repository for permission checks
        """
        self.contract_repo = contract_repo
        self.notification_service = notification_service
        self.user_repo = user_repo

    def can_transition(
        self,
        from_status: str,
        to_status: str,
        user_role: str = None
    ) -> bool:
        """Check if state transition is valid.

        Args:
            from_status: Current status
            to_status: Target status
            user_role: Optional user role to check permission

        Returns:
            True if transition is allowed
        """
        if from_status not in self.VALID_TRANSITIONS:
            return False

        if to_status not in self.VALID_TRANSITIONS[from_status]:
            return False

        if user_role:
            allowed_roles = self.TRANSITION_PERMISSIONS.get(
                (from_status, to_status), []
            )
            if user_role not in allowed_roles:
                return False

        return True

    def _get_user_role(self, user_id: int) -> Optional[str]:
        """Get user role from user repository.

        Args:
            user_id: User ID

        Returns:
            User role or None
        """
        if not self.user_repo:
            return 'admin'  # Default for testing

        user = self.user_repo.get_by_id(user_id)
        return getattr(user, 'role', None) if user else None

    def _validate_transition(
        self,
        contract: Contract,
        to_status: str,
        user_id: int
    ) -> WorkflowResult:
        """Validate transition before execution.

        Args:
            contract: Contract instance
            to_status: Target status
            user_id: User requesting transition

        Returns:
            WorkflowResult
        """
        from_status = contract.status

        # Check transition validity
        user_role = self._get_user_role(user_id)
        if not self.can_transition(from_status, to_status, user_role):
            return WorkflowResult.fail(
                f"Không thể chuyển từ '{from_status}' sang '{to_status}' "
                f"với quyền '{user_role}'"
            )

        # Check required fields
        if to_status in self.REQUIRED_FIELDS:
            missing = []
            for field in self.REQUIRED_FIELDS[to_status]:
                value = getattr(contract, field, None)
                if not value:
                    missing.append(field)

            if missing:
                return WorkflowResult.fail(
                    f"Thiếu thông tin bắt buộc: {', '.join(missing)}"
                )

        # Special validations
        if to_status == 'paid':
            if contract.remaining_amount > 0:
                return WorkflowResult.fail(
                    f"Chưa thanh toán đủ. Còn thiếu: {contract.remaining_amount:,.0f} VNĐ"
                )

        return WorkflowResult.ok()

    def _record_transition(
        self,
        contract_id: int,
        from_status: str,
        to_status: str,
        user_id: int,
        notes: str = None
    ) -> bool:
        """Record status transition in history.

        Args:
            contract_id: Contract ID
            from_status: Previous status
            to_status: New status
            user_id: User making the change
            notes: Optional notes

        Returns:
            True if recorded successfully
        """
        try:
            self.contract_repo.update_status(
                contract_id,
                to_status,
                changed_by=user_id,
                notes=notes
            )
            return True
        except Exception as e:
            print(f"Failed to record transition: {e}")
            return False

    def submit_for_approval(
        self,
        contract_id: int,
        user_id: int,
        notes: str = None
    ) -> WorkflowResult:
        """Submit contract for approval (draft → pending).

        Args:
            contract_id: Contract ID
            user_id: User submitting
            notes: Optional submission notes

        Returns:
            WorkflowResult
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Validate
        validation = self._validate_transition(contract, 'pending', user_id)
        if not validation.success:
            return validation

        # Record transition
        if self._record_transition(
            contract_id, 'draft', 'pending', user_id, notes
        ):
            # Notify managers (async)
            if self.notification_service:
                self.notification_service.notify_approval_requested(
                    contract_id, contract.contract_code
                )

            return WorkflowResult.ok(
                "Hợp đồng đã được gửi phê duyệt",
                {'contract_id': contract_id, 'new_status': 'pending'}
            )

        return WorkflowResult.fail("Không thể gửi phê duyệt")

    def approve(
        self,
        contract_id: int,
        approver_id: int,
        notes: str = None
    ) -> WorkflowResult:
        """Approve contract (pending → approved).

        Args:
            contract_id: Contract ID
            approver_id: Approver user ID
            notes: Optional approval notes

        Returns:
            WorkflowResult
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Validate
        validation = self._validate_transition(contract, 'approved', approver_id)
        if not validation.success:
            return validation

        # Update approval info
        update_data = {
            'approval_status': 'approved',
            'approved_by': approver_id,
            'approved_at': datetime.now(),
            'approval_notes': notes
        }

        try:
            self.contract_repo.update(contract_id, update_data)

            if self._record_transition(
                contract_id, 'pending', 'approved', approver_id, notes
            ):
                # Notify creator
                if self.notification_service:
                    self.notification_service.notify_contract_approved(
                        contract_id, contract.created_by
                    )

                return WorkflowResult.ok(
                    "Hợp đồng đã được phê duyệt",
                    {'contract_id': contract_id, 'new_status': 'approved'}
                )
        except Exception as e:
            return WorkflowResult.fail(f"Không thể phê duyệt: {str(e)}")

        return WorkflowResult.fail("Phê duyệt thất bại")

    def reject(
        self,
        contract_id: int,
        approver_id: int,
        reason: str
    ) -> WorkflowResult:
        """Reject contract (pending → draft).

        Args:
            contract_id: Contract ID
            approver_id: Rejector user ID
            reason: Rejection reason (required)

        Returns:
            WorkflowResult
        """
        if not reason or not reason.strip():
            return WorkflowResult.fail("Vui lòng nhập lý do từ chối")

        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Validate
        validation = self._validate_transition(contract, 'draft', approver_id)
        if not validation.success:
            return validation

        # Update approval status
        update_data = {
            'approval_status': 'rejected',
            'approval_notes': reason
        }

        try:
            self.contract_repo.update(contract_id, update_data)

            if self._record_transition(
                contract_id, 'pending', 'draft', approver_id,
                f"Từ chối: {reason}"
            ):
                # Notify creator
                if self.notification_service:
                    self.notification_service.notify_contract_rejected(
                        contract_id, contract.created_by, reason
                    )

                return WorkflowResult.ok(
                    "Hợp đồng đã bị từ chối",
                    {'contract_id': contract_id, 'new_status': 'draft', 'reason': reason}
                )
        except Exception as e:
            return WorkflowResult.fail(f"Không thể từ chối: {str(e)}")

        return WorkflowResult.fail("Từ chối thất bại")

    def mark_signed(
        self,
        contract_id: int,
        user_id: int,
        signed_by_customer: bool = False,
        signed_by_representative: bool = False,
        notes: str = None
    ) -> WorkflowResult:
        """Mark contract as signed (approved → signed).

        Args:
            contract_id: Contract ID
            user_id: User recording signatures
            signed_by_customer: Whether customer signed
            signed_by_representative: Whether representative signed
            notes: Optional notes

        Returns:
            WorkflowResult
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Validate
        validation = self._validate_transition(contract, 'signed', user_id)
        if not validation.success:
            return validation

        # Update signature info
        update_data = {
            'signed_by_customer': signed_by_customer,
            'signed_by_representative': signed_by_representative,
            'signed_at': datetime.now()
        }

        # Require both signatures
        if not (signed_by_customer and signed_by_representative):
            # Just update signature info but don't transition yet
            self.contract_repo.update(contract_id, update_data)
            return WorkflowResult.ok(
                "Đã cập nhật chữ ký. Cần đủ cả 2 chữ ký để hoàn tất.",
                {'contract_id': contract_id, 'signatures_complete': False}
            )

        try:
            self.contract_repo.update(contract_id, update_data)

            if self._record_transition(
                contract_id, 'approved', 'signed', user_id, notes
            ):
                return WorkflowResult.ok(
                    "Hợp đồng đã được ký",
                    {'contract_id': contract_id, 'new_status': 'signed'}
                )
        except Exception as e:
            return WorkflowResult.fail(f"Không thể ký hợp đồng: {str(e)}")

        return WorkflowResult.fail("Ký hợp đồng thất bại")

    def record_payment(
        self,
        contract_id: int,
        user_id: int,
        amount: float,
        payment_method: str = 'cash',
        notes: str = None
    ) -> WorkflowResult:
        """Record payment for contract.

        Args:
            contract_id: Contract ID
            user_id: User recording payment
            amount: Payment amount
            payment_method: Payment method
            notes: Optional notes

        Returns:
            WorkflowResult
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        if amount <= 0:
            return WorkflowResult.fail("Số tiền thanh toán phải lớn hơn 0")

        # Add payment record
        try:
            payment_data = {
                'amount': amount,
                'payment_type': 'installment' if contract.is_installment else 'final',
                'payment_method': payment_method,
                'received_by': user_id,
                'notes': notes
            }
            self.contract_repo.add_payment(contract_id, payment_data)

            # Update paid amounts
            new_paid = contract.paid_amount + amount
            new_remaining = contract.final_amount - new_paid

            self.contract_repo.update(contract_id, {
                'paid_amount': new_paid,
                'remaining_amount': max(0, new_remaining)
            })

            # Check if fully paid
            if new_remaining <= 0:
                # Auto-transition to paid if signed
                if contract.status == 'signed':
                    self._record_transition(
                        contract_id, 'signed', 'paid', user_id,
                        f"Thanh toán đủ: {amount:,.0f} VNĐ"
                    )
                    return WorkflowResult.ok(
                        "Thanh toán hoàn tất. Hợp đồng đã được đánh dấu đã thanh toán.",
                        {
                            'contract_id': contract_id,
                            'new_status': 'paid',
                            'paid_amount': new_paid,
                            'remaining': 0
                        }
                    )

            return WorkflowResult.ok(
                f"Đã ghi nhận thanh toán: {amount:,.0f} VNĐ",
                {
                    'contract_id': contract_id,
                    'paid_amount': new_paid,
                    'remaining': max(0, new_remaining)
                }
            )

        except Exception as e:
            return WorkflowResult.fail(f"Không thể ghi nhận thanh toán: {str(e)}")

    def mark_delivered(
        self,
        contract_id: int,
        user_id: int,
        delivery_date: datetime = None,
        notes: str = None
    ) -> WorkflowResult:
        """Mark contract as delivered (paid → delivered).

        Args:
            contract_id: Contract ID
            user_id: User confirming delivery
            delivery_date: Optional delivery date (default now)
            notes: Optional delivery notes

        Returns:
            WorkflowResult
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Validate
        validation = self._validate_transition(contract, 'delivered', user_id)
        if not validation.success:
            return validation

        # Check if paid
        if contract.status != 'paid':
            return WorkflowResult.fail(
                f"Hợp đồng phải ở trạng thái 'paid' trước khi giao. Hiện tại: {contract.status}"
            )

        # Update delivery info
        actual_date = delivery_date or datetime.now()
        update_data = {
            'actual_delivery_date': actual_date
        }

        try:
            self.contract_repo.update(contract_id, update_data)

            if self._record_transition(
                contract_id, 'paid', 'delivered', user_id, notes
            ):
                # TODO: Update car status to 'sold'

                return WorkflowResult.ok(
                    "Hợp đồng đã hoàn tất (giao xe)",
                    {
                        'contract_id': contract_id,
                        'new_status': 'delivered',
                        'delivery_date': actual_date
                    }
                )
        except Exception as e:
            return WorkflowResult.fail(f"Không thể xác nhận giao xe: {str(e)}")

        return WorkflowResult.fail("Xác nhận giao xe thất bại")

    def cancel(
        self,
        contract_id: int,
        user_id: int,
        reason: str
    ) -> WorkflowResult:
        """Cancel contract.

        Args:
            contract_id: Contract ID
            user_id: User cancelling
            reason: Cancellation reason (required)

        Returns:
            WorkflowResult
        """
        if not reason or not reason.strip():
            return WorkflowResult.fail("Vui lòng nhập lý do hủy")

        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return WorkflowResult.fail("Hợp đồng không tồn tại")

        # Cannot cancel delivered contracts
        if contract.status == 'delivered':
            return WorkflowResult.fail("Không thể hủy hợp đồng đã giao xe")

        # Check permission
        user_role = self._get_user_role(user_id)
        if contract.status in ['signed', 'paid'] and user_role != 'admin':
            return WorkflowResult.fail(
                "Chỉ admin mới có quyền hủy hợp đồng đã ký hoặc đã thanh toán"
            )

        try:
            if self._record_transition(
                contract_id, contract.status, 'cancelled', user_id,
                f"Hủy hợp đồng: {reason}"
            ):
                # TODO: Update car status back to 'available' if reserved

                return WorkflowResult.ok(
                    "Hợp đồng đã bị hủy",
                    {
                        'contract_id': contract_id,
                        'new_status': 'cancelled',
                        'reason': reason
                    }
                )
        except Exception as e:
            return WorkflowResult.fail(f"Không thể hủy hợp đồng: {str(e)}")

        return WorkflowResult.fail("Hủy hợp đồng thất bại")

    def get_workflow_history(self, contract_id: int) -> List[Dict[str, Any]]:
        """Get workflow history for contract.

        Args:
            contract_id: Contract ID

        Returns:
            List of history records
        """
        return self.contract_repo.get_status_history(contract_id)

    def get_pending_approvals(
        self,
        user_id: int = None,
        user_role: str = None
    ) -> List[Contract]:
        """Get contracts awaiting approval.

        Args:
            user_id: Optional user ID to filter
            user_role: User role for permission check

        Returns:
            List of pending contracts
        """
        contracts = self.contract_repo.get_all(status='pending')

        # Filter by role if needed
        if user_role and user_role not in ['admin', 'manager']:
            # Non-managers only see their own contracts
            if user_id:
                contracts = [c for c in contracts if c.created_by == user_id]

        return contracts

    def get_allowed_actions(self, contract: Contract, user_id: int, user_role: str) -> List[str]:
        """Get list of allowed actions for user on contract.

        Args:
            contract: Contract instance
            user_id: Current user ID
            user_role: Current user role

        Returns:
            List of action names
        """
        actions = []
        current_status = contract.status

        # Check creator
        is_creator = contract.created_by == user_id
        is_manager = user_role in ['manager', 'admin']

        if current_status == 'draft':
            if is_creator or is_manager:
                actions.extend(['edit', 'submit', 'cancel', 'delete'])

        elif current_status == 'pending':
            if is_manager:
                actions.extend(['approve', 'reject'])
            if is_creator:
                actions.append('view')

        elif current_status == 'approved':
            actions.extend(['sign', 'cancel'])

        elif current_status == 'signed':
            actions.extend(['record_payment', 'cancel'])

        elif current_status == 'paid':
            actions.extend(['deliver'])

        elif current_status == 'cancelled':
            if is_manager:
                actions.append('resubmit')

        # Everyone can view
        if 'view' not in actions:
            actions.insert(0, 'view')

        return actions
