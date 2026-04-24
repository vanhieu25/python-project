"""
Customer Service Module
Business logic for customer management.
"""

from typing import List, Optional, Dict, Any

from ..repositories.customer_repository import CustomerRepository
from ..repositories.customer_history_repository import CustomerHistoryRepository
from ..validators.customer_validator import CustomerValidator, CustomerValidationResult
from ..models.customer import Customer


class CustomerServiceError(Exception):
    """Base exception for customer service."""
    pass


class DuplicateCustomerError(CustomerServiceError):
    """Duplicate customer data."""
    pass


class CustomerNotFoundError(CustomerServiceError):
    """Customer not found."""
    pass


class CustomerInContractError(CustomerServiceError):
    """Customer has active contracts."""
    pass


class CustomerValidationServiceError(CustomerServiceError):
    """Validation error from service."""
    def __init__(self, message: str, errors: List[Dict] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(message)


class CustomerService:
    """Service layer for customer operations."""

    def __init__(self, customer_repository: CustomerRepository,
                 history_repository: CustomerHistoryRepository):
        """Initialize customer service.

        Args:
            customer_repository: Customer repository instance
            history_repository: History repository instance
        """
        self.customer_repo = customer_repository
        self.history_repo = history_repository
        self.validator = CustomerValidator()

    def create_customer(self, customer_data: Dict[str, Any],
                       created_by: int) -> Customer:
        """Create new customer with validation.

        Args:
            customer_data: Dictionary containing customer data
            created_by: User ID who creates the customer

        Returns:
            Created Customer instance

        Raises:
            CustomerValidationServiceError: If data is invalid
            DuplicateCustomerError: If duplicate data found
        """
        # Validate
        result = self.validator.validate_all(customer_data, is_update=False)
        if not result.is_valid:
            errors = [{'field': e.field, 'message': e.message, 'code': e.code}
                     for e in result.errors]
            raise CustomerValidationServiceError(
                f"Validation failed with {len(errors)} error(s)",
                errors
            )

        # Check duplicates
        self._check_duplicates(customer_data, result)
        if not result.is_valid:
            errors = [{'field': e.field, 'message': e.message, 'code': e.code}
                     for e in result.errors]
            raise DuplicateCustomerError("Duplicate data found")

        # Set creator
        customer_data['created_by'] = created_by

        try:
            # Create
            customer_id = self.customer_repo.create(customer_data)
            customer = self.customer_repo.get_by_id(customer_id)

            # Record history
            self.history_repo.record_create(customer_id, created_by)

            return customer
        except Exception as e:
            raise CustomerServiceError(f"Không thể tạo khách hàng: {str(e)}")

    def update_customer(self, customer_id: int, customer_data: Dict[str, Any],
                     updated_by: int) -> Customer:
        """Update customer with validation.

        Args:
            customer_id: Customer ID
            customer_data: Dictionary containing updated data
            updated_by: User ID who updates

        Returns:
            Updated Customer instance

        Raises:
            CustomerNotFoundError: If customer not found
            CustomerValidationServiceError: If data is invalid
            DuplicateCustomerError: If duplicate data found
        """
        # Check exists
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Không tìm thấy khách hàng {customer_id}")

        # Validate
        result = self.validator.validate_all(customer_data, is_update=True)
        if not result.is_valid:
            errors = [{'field': e.field, 'message': e.message, 'code': e.code}
                     for e in result.errors]
            raise CustomerValidationServiceError(
                f"Validation failed with {len(errors)} error(s)",
                errors
            )

        # Check duplicates (exclude current customer)
        self._check_duplicates(customer_data, result, exclude_id=customer_id)
        if not result.is_valid:
            errors = [{'field': e.field, 'message': e.message, 'code': e.code}
                     for e in result.errors]
            raise DuplicateCustomerError("Duplicate data found")

        # Track changes for history
        changes = self._get_changes(customer, customer_data)

        try:
            # Update
            success = self.customer_repo.update(customer_id, customer_data)
            if not success:
                raise CustomerServiceError("Cập nhật thất bại")

            # Record history
            for change in changes:
                self.history_repo.record_update(
                    customer_id, change['field'],
                    change['old_value'], change['new_value'],
                    updated_by
                )

            return self.customer_repo.get_by_id(customer_id)
        except Exception as e:
            raise CustomerServiceError(f"Không thể cập nhật khách hàng: {str(e)}")

    def delete_customer(self, customer_id: int, deleted_by: int,
                       reason: Optional[str] = None,
                       permanent: bool = False) -> bool:
        """Delete customer (soft or permanent).

        Args:
            customer_id: Customer ID
            deleted_by: User ID who deletes
            reason: Reason for deletion
            permanent: Whether to permanently delete

        Returns:
            True if successful

        Raises:
            CustomerNotFoundError: If customer not found
            CustomerInContractError: If customer has active contracts
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Không tìm thấy khách hàng {customer_id}")

        # Check active contracts
        if self._has_active_contracts(customer_id):
            raise CustomerInContractError(
                "Không thể xóa khách hàng đang có hợp đồng active"
            )

        try:
            if permanent:
                # Record history before permanent delete
                self.history_repo.record_delete(customer_id, deleted_by, reason)
                success = self.customer_repo.delete_permanently(customer_id)
            else:
                success = self.customer_repo.soft_delete(customer_id, deleted_by, reason)
                if success:
                    self.history_repo.record_delete(customer_id, deleted_by, reason)

            return success
        except Exception as e:
            raise CustomerServiceError(f"Không thể xóa khách hàng: {str(e)}")

    def restore_customer(self, customer_id: int, restored_by: int) -> Customer:
        """Restore soft-deleted customer.

        Args:
            customer_id: Customer ID
            restored_by: User ID who restores

        Returns:
            Restored Customer instance

        Raises:
            CustomerNotFoundError: If customer not found
            CustomerServiceError: If customer not deleted
        """
        customer = self.customer_repo.get_by_id(customer_id, include_deleted=True)
        if not customer:
            raise CustomerNotFoundError(f"Không tìm thấy khách hàng {customer_id}")

        if not customer.is_deleted:
            raise CustomerServiceError("Khách hàng chưa bị xóa")

        try:
            success = self.customer_repo.restore(customer_id)
            if not success:
                raise CustomerServiceError("Khôi phục thất bại")

            # Record history
            self.history_repo.record_restore(customer_id, restored_by)

            return self.customer_repo.get_by_id(customer_id)
        except Exception as e:
            raise CustomerServiceError(f"Không thể khôi phục khách hàng: {str(e)}")

    def get_customer(self, customer_id: int) -> Customer:
        """Get customer by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer instance

        Raises:
            CustomerNotFoundError: If customer not found
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Không tìm thấy khách hàng {customer_id}")
        return customer

    def list_customers(self, customer_type: Optional[str] = None,
                      customer_class: Optional[str] = None,
                      include_deleted: bool = False) -> List[Customer]:
        """List all customers.

        Args:
            customer_type: Filter by type
            customer_class: Filter by class
            include_deleted: Whether to include soft-deleted

        Returns:
            List of Customer instances
        """
        return self.customer_repo.get_all(customer_type, customer_class, None, include_deleted)

    def get_customer_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get history for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of history records
        """
        return self.history_repo.get_history(customer_id)

    def _check_duplicates(self, data: Dict[str, Any],
                         result: CustomerValidationResult,
                         exclude_id: Optional[int] = None):
        """Check for duplicate phone, email, id_card."""
        phone = data.get('phone')
        email = data.get('email')
        id_card = data.get('id_card')

        if phone and self.customer_repo.exists(phone=phone, exclude_id=exclude_id):
            result.add_error("Số điện thoại đã tồn tại", 'phone', 'duplicate')

        if email and self.customer_repo.exists(email=email, exclude_id=exclude_id):
            result.add_error("Email đã tồn tại", 'email', 'duplicate')

        if id_card and self.customer_repo.exists(id_card=id_card, exclude_id=exclude_id):
            result.add_error("CMND/CCCD đã tồn tại", 'id_card', 'duplicate')

    def _get_changes(self, customer: Customer,
                    new_data: Dict[str, Any]) -> List[Dict]:
        """Get list of changes for history tracking."""
        changes = []
        for field, new_value in new_data.items():
            old_value = getattr(customer, field, None)

            # Normalize values for comparison
            if old_value != new_value:
                # Skip None vs empty string
                if old_value is None and new_value == '':
                    continue
                if old_value == '' and new_value is None:
                    continue

                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value
                })

        return changes

    def _has_active_contracts(self, customer_id: int) -> bool:
        """Check if customer has active contracts.

        Note: Will be implemented when contract module is ready.
        For now, return False.
        """
        return False

    def validate_field(self, field_name: str, value: Any) -> Optional[str]:
        """Validate a single field.

        Args:
            field_name: Field name
            value: Field value

        Returns:
            Error message or None if valid
        """
        try:
            if field_name == 'phone':
                CustomerValidator.validate_phone(value)
            elif field_name == 'email':
                CustomerValidator.validate_email(value)
            elif field_name == 'id_card':
                CustomerValidator.validate_id_card(value)
            return None
        except Exception as e:
            return str(e)
