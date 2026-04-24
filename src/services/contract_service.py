"""
Contract Service Module
Business logic layer for contract management.
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date

from models.contract import Contract, ContractItem, ContractPayment
from repositories.contract_repository import ContractRepository


@dataclass
class Result:
    """Result wrapper for service operations."""
    success: bool
    data: Any = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: Any = None) -> 'Result':
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> 'Result':
        return cls(success=False, error=error)


@dataclass
class PaginatedResult:
    """Paginated result wrapper."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


class ContractService:
    """Service layer for contract business logic."""

    def __init__(
        self,
        contract_repo: ContractRepository,
        customer_repo=None,
        car_repo=None,
        user_repo=None
    ):
        """Initialize service with repositories.

        Args:
            contract_repo: ContractRepository instance
            customer_repo: Optional customer repository
            car_repo: Optional car repository
            user_repo: Optional user repository
        """
        self.contract_repo = contract_repo
        self.customer_repo = customer_repo
        self.car_repo = car_repo
        self.user_repo = user_repo

    def create_contract(self, data: Dict[str, Any], created_by: int) -> Result:
        """Create new contract with validation.

        Args:
            data: Contract data dictionary
            created_by: User ID creating the contract

        Returns:
            Result with Contract or error message
        """
        # Validate required fields
        required = ['customer_id', 'car_id']
        for field in required:
            if field not in data or not data[field]:
                return Result.fail(f"Missing required field: {field}")

        # Validate customer exists (if customer_repo available)
        if self.customer_repo:
            customer = self.customer_repo.get_by_id(data['customer_id'])
            if not customer:
                return Result.fail("Customer not found")

            # Copy customer info to contract data
            data['customer_name'] = customer.full_name
            data['customer_phone'] = customer.phone
            data['customer_id_card'] = getattr(customer, 'id_card', None)
            data['customer_address'] = getattr(customer, 'address', None)

        # Validate car exists and is available (if car_repo available)
        if self.car_repo:
            car = self.car_repo.get_by_id(data['car_id'])
            if not car:
                return Result.fail("Car not found")
            if getattr(car, 'status', None) != 'available':
                return Result.fail("Car is not available for sale")

            # Copy car info to contract data
            data['car_vin'] = getattr(car, 'vin', None)
            data['car_license_plate'] = getattr(car, 'license_plate', None)
            data['car_brand'] = car.brand
            data['car_model'] = car.model
            data['car_year'] = getattr(car, 'year', None)
            data['car_color'] = getattr(car, 'color', None)
            # Only set car_price from repo if not provided by user
            if 'car_price' not in data or not data['car_price']:
                data['car_price'] = car.price

        # Calculate amounts
        car_price = data.get('car_price', 0) or 0
        discount_amount = data.get('discount_amount', 0) or 0
        vat_rate = data.get('vat_rate', 0.1)  # Default 10% VAT

        total_amount = car_price - discount_amount
        vat_amount = total_amount * vat_rate
        final_amount = total_amount + vat_amount

        # Set calculated values
        data['total_amount'] = total_amount
        data['vat_amount'] = vat_amount
        data['final_amount'] = final_amount
        data['remaining_amount'] = final_amount

        # Set metadata
        data['created_by'] = created_by
        data['status'] = 'draft'
        data['approval_status'] = 'pending'

        try:
            contract_id = self.contract_repo.create(data)
            contract = self.contract_repo.get_by_id(contract_id)
            return Result.ok(contract)
        except Exception as e:
            return Result.fail(f"Failed to create contract: {str(e)}")

    def get_contract_detail(self, contract_id: int) -> Optional[Contract]:
        """Get contract with all related data.

        Args:
            contract_id: Contract ID

        Returns:
            Contract with items and payments loaded, or None
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return None

        # Load related data
        contract.items = self.contract_repo.get_items(contract_id)
        contract.payments = self.contract_repo.get_payments(contract_id)

        return contract

    def get_contract_by_code(self, contract_code: str) -> Optional[Contract]:
        """Get contract by code with related data.

        Args:
            contract_code: Contract code (e.g., "HD000001")

        Returns:
            Contract with items and payments loaded, or None
        """
        contract = self.contract_repo.get_by_code(contract_code)
        if not contract:
            return None

        contract.items = self.contract_repo.get_items(contract.id)
        contract.payments = self.contract_repo.get_payments(contract.id)

        return contract

    def search_contracts(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResult:
        """Search contracts with filters and pagination.

        Args:
            filters: Dictionary of filter conditions
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            PaginatedResult with contracts
        """
        filters = filters or {}

        # Get all contracts and apply filters in memory
        # (for production, this should be done in SQL)
        contracts = self.contract_repo.get_all()

        # Apply filters
        if 'status' in filters:
            contracts = [c for c in contracts if c.status == filters['status']]

        if 'customer_name' in filters:
            name_filter = filters['customer_name'].lower()
            contracts = [
                c for c in contracts
                if c.customer_name and name_filter in c.customer_name.lower()
            ]

        if 'customer_phone' in filters:
            phone_filter = filters['customer_phone']
            contracts = [
                c for c in contracts
                if c.customer_phone and phone_filter in c.customer_phone
            ]

        if 'car_brand' in filters:
            contracts = [
                c for c in contracts
                if c.car_brand == filters['car_brand']
            ]

        if 'car_model' in filters:
            contracts = [
                c for c in contracts
                if c.car_model == filters['car_model']
            ]

        if 'customer_id' in filters:
            contracts = [
                c for c in contracts
                if c.customer_id == filters['customer_id']
            ]

        if 'created_by' in filters:
            contracts = [
                c for c in contracts
                if c.created_by == filters['created_by']
            ]

        if 'date_from' in filters:
            from_date = filters['date_from']
            contracts = [
                c for c in contracts
                if c.created_at and c.created_at.date() >= from_date
            ]

        if 'date_to' in filters:
            to_date = filters['date_to']
            contracts = [
                c for c in contracts
                if c.created_at and c.created_at.date() <= to_date
            ]

        if 'min_amount' in filters:
            contracts = [
                c for c in contracts
                if c.final_amount >= filters['min_amount']
            ]

        if 'max_amount' in filters:
            contracts = [
                c for c in contracts
                if c.final_amount <= filters['max_amount']
            ]

        # Sort by created_at DESC
        contracts.sort(key=lambda c: c.created_at or '', reverse=True)

        # Calculate pagination
        total = len(contracts)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page

        return PaginatedResult(
            items=contracts[start:end],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def update_contract(
        self,
        contract_id: int,
        data: Dict[str, Any],
        updated_by: int
    ) -> Result:
        """Update contract (only if status is 'draft').

        Args:
            contract_id: Contract ID
            data: Updated data dictionary
            updated_by: User ID making the update

        Returns:
            Result with success status
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        # Only allow updates to draft contracts
        if contract.status != 'draft':
            return Result.fail(f"Cannot update contract with status: {contract.status}")

        # Check permission (creator or admin)
        if contract.created_by != updated_by:
            # TODO: Check if updated_by is admin
            return Result.fail("Permission denied: only creator can update")

        # Prevent updating protected fields
        protected = ['customer_id', 'car_id', 'contract_code', 'created_by']
        for field in protected:
            if field in data:
                del data[field]

        # Recalculate amounts if price fields changed
        if any(f in data for f in ['car_price', 'discount_amount', 'vat_amount']):
            car_price = data.get('car_price', contract.car_price)
            discount = data.get('discount_amount', contract.discount_amount)
            total = car_price - discount
            vat = total * 0.1  # 10% VAT
            final = total + vat

            data['total_amount'] = total
            data['vat_amount'] = vat
            data['final_amount'] = final

            # Update remaining amount based on paid amount
            data['remaining_amount'] = final - contract.paid_amount

        try:
            success = self.contract_repo.update(contract_id, data)
            if success:
                return Result.ok(True)
            return Result.fail("Update failed")
        except Exception as e:
            return Result.fail(f"Failed to update contract: {str(e)}")

    def delete_contract(self, contract_id: int, deleted_by: int) -> Result:
        """Delete contract (only if status is 'draft').

        Args:
            contract_id: Contract ID
            deleted_by: User ID requesting deletion

        Returns:
            Result with success status
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        # Only allow deleting draft contracts
        if contract.status != 'draft':
            return Result.fail(f"Cannot delete contract with status: {contract.status}")

        # Check permission (creator or admin)
        if contract.created_by != deleted_by:
            # TODO: Check if deleted_by is admin
            return Result.fail("Permission denied: only creator can delete")

        try:
            success = self.contract_repo.delete(contract_id)
            if success:
                return Result.ok(True)
            return Result.fail("Delete failed")
        except Exception as e:
            return Result.fail(f"Failed to delete contract: {str(e)}")

    def add_item_to_contract(
        self,
        contract_id: int,
        item_data: Dict[str, Any]
    ) -> Result:
        """Add item to contract.

        Args:
            contract_id: Contract ID
            item_data: Item data dictionary

        Returns:
            Result with item ID
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        # Only allow adding items to draft contracts
        if contract.status != 'draft':
            return Result.fail("Cannot modify items after contract is submitted")

        # Validate item data
        if 'item_type' not in item_data or 'item_name' not in item_data:
            return Result.fail("Missing required fields: item_type, item_name")

        if 'unit_price' not in item_data:
            return Result.fail("Missing required field: unit_price")

        # Calculate total price
        quantity = item_data.get('quantity', 1)
        unit_price = item_data['unit_price']
        item_data['total_price'] = quantity * unit_price

        try:
            item_id = self.contract_repo.add_item(contract_id, item_data)

            # Recalculate contract totals
            self._recalculate_contract_totals(contract_id)

            return Result.ok(item_id)
        except Exception as e:
            return Result.fail(f"Failed to add item: {str(e)}")

    def remove_item_from_contract(
        self,
        contract_id: int,
        item_id: int
    ) -> Result:
        """Remove item from contract.

        Args:
            contract_id: Contract ID
            item_id: Item ID to remove

        Returns:
            Result with success status
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        # Only allow removing items from draft contracts
        if contract.status != 'draft':
            return Result.fail("Cannot modify items after contract is submitted")

        try:
            # Get current items
            items = self.contract_repo.get_items(contract_id)

            # Filter out the item to remove
            item_to_remove = None
            for item in items:
                if item.id == item_id:
                    item_to_remove = item
                    break

            if not item_to_remove:
                return Result.fail("Item not found")

            # Delete all items and re-add remaining ones
            # (simple approach - in production use individual delete)
            self.contract_repo.delete_all_items(contract_id)

            for item in items:
                if item.id != item_id:
                    self.contract_repo.add_item(contract_id, {
                        'item_type': item.item_type,
                        'item_name': item.item_name,
                        'item_description': item.item_description,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'is_optional': item.is_optional,
                        'is_selected': item.is_selected
                    })

            # Recalculate contract totals
            self._recalculate_contract_totals(contract_id)

            return Result.ok(True)
        except Exception as e:
            return Result.fail(f"Failed to remove item: {str(e)}")

    def _recalculate_contract_totals(self, contract_id: int) -> None:
        """Recalculate all monetary values for contract.

        Args:
            contract_id: Contract ID
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return

        # Calculate items total
        items = self.contract_repo.get_items(contract_id)
        items_total = sum(item.total_price for item in items if item.is_selected)

        # Base calculation on car price + items
        base_amount = contract.car_price + items_total
        discount = contract.discount_amount
        total = base_amount - discount
        vat = total * 0.1  # 10% VAT
        final = total + vat

        # Update contract
        self.contract_repo.update(contract_id, {
            'total_amount': total,
            'vat_amount': vat,
            'final_amount': final,
            'remaining_amount': final - contract.paid_amount
        })

    def calculate_totals(self, contract_id: int) -> Result:
        """Calculate and return all monetary values.

        Args:
            contract_id: Contract ID

        Returns:
            Result with totals dictionary
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        items = self.contract_repo.get_items(contract_id)
        items_total = sum(item.total_price for item in items if item.is_selected)

        totals = {
            'car_price': contract.car_price,
            'items_total': items_total,
            'discount_amount': contract.discount_amount,
            'total_amount': contract.total_amount,
            'vat_amount': contract.vat_amount,
            'final_amount': contract.final_amount,
            'paid_amount': contract.paid_amount,
            'remaining_amount': contract.remaining_amount
        }

        return Result.ok(totals)

    def cancel_contract(self, contract_id: int, cancelled_by: int, reason: str = None) -> Result:
        """Cancel contract.

        Args:
            contract_id: Contract ID
            cancelled_by: User ID cancelling
            reason: Optional cancellation reason

        Returns:
            Result with success status
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return Result.fail("Contract not found")

        # Cannot cancel delivered contracts
        if contract.status == 'delivered':
            return Result.fail("Cannot cancel a delivered contract")

        try:
            success = self.contract_repo.update_status(
                contract_id,
                'cancelled',
                changed_by=cancelled_by,
                notes=reason or "Contract cancelled"
            )
            if success:
                return Result.ok(True)
            return Result.fail("Cancel failed")
        except Exception as e:
            return Result.fail(f"Failed to cancel contract: {str(e)}")

    def get_contract_statistics(self) -> Dict[str, Any]:
        """Get contract statistics for dashboard.

        Returns:
            Dictionary with statistics
        """
        all_contracts = self.contract_repo.get_all()

        stats = {
            'total_contracts': len(all_contracts),
            'by_status': {},
            'total_value': 0.0,
            'paid_amount': 0.0,
            'remaining_amount': 0.0
        }

        for contract in all_contracts:
            # Count by status
            status = contract.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            # Sum amounts
            stats['total_value'] += contract.final_amount
            stats['paid_amount'] += contract.paid_amount
            stats['remaining_amount'] += contract.remaining_amount

        return stats

    def get_recent_contracts(self, limit: int = 5) -> List[Contract]:
        """Get recent contracts for dashboard.

        Args:
            limit: Number of contracts to return

        Returns:
            List of recent contracts
        """
        contracts = self.contract_repo.get_all()
        contracts.sort(key=lambda c: c.created_at or '', reverse=True)
        return contracts[:limit]
