"""
Contract Repository Module
Provides data access operations for Contract model.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from database.db_helper import DatabaseHelper
from models.contract import Contract, ContractItem, ContractPayment


class ContractRepository:
    """Repository for Contract data access."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def _generate_contract_code(self) -> str:
        """Generate next contract code (HD000001, HD000002, ...).

        Returns:
            str: Next contract code
        """
        result = self.db.fetch_one(
            "SELECT contract_code FROM contracts WHERE contract_code LIKE 'HD%' "
            "ORDER BY contract_code DESC LIMIT 1"
        )
        if result and result['contract_code']:
            last_num = int(result['contract_code'][2:])
            return f"HD{last_num + 1:06d}"
        return "HD000001"

    def create(self, contract_data: Dict[str, Any]) -> int:
        """Create new contract.

        Args:
            contract_data: Dictionary containing contract data

        Returns:
            int: ID of created contract
        """
        # Auto-generate contract code if not provided
        if not contract_data.get('contract_code'):
            contract_data['contract_code'] = self._generate_contract_code()

        query = """
            INSERT INTO contracts (
                contract_code, customer_id, customer_name, customer_phone,
                customer_id_card, customer_address, car_id, car_vin,
                car_license_plate, car_brand, car_model, car_year, car_color,
                car_price, discount_amount, discount_reason, total_amount,
                vat_amount, final_amount, payment_method, deposit_amount,
                paid_amount, remaining_amount, is_installment,
                installment_down_payment, installment_months, installment_monthly_amount,
                delivery_date, delivery_location, status, approval_status,
                created_by, notes, contract_template_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            contract_data['contract_code'],
            contract_data['customer_id'],
            contract_data.get('customer_name'),
            contract_data.get('customer_phone'),
            contract_data.get('customer_id_card'),
            contract_data.get('customer_address'),
            contract_data['car_id'],
            contract_data.get('car_vin'),
            contract_data.get('car_license_plate'),
            contract_data.get('car_brand'),
            contract_data.get('car_model'),
            contract_data.get('car_year'),
            contract_data.get('car_color'),
            contract_data.get('car_price', 0),
            contract_data.get('discount_amount', 0),
            contract_data.get('discount_reason'),
            contract_data.get('total_amount', 0),
            contract_data.get('vat_amount', 0),
            contract_data.get('final_amount', 0),
            contract_data.get('payment_method'),
            contract_data.get('deposit_amount', 0),
            contract_data.get('paid_amount', 0),
            contract_data.get('remaining_amount', 0),
            contract_data.get('is_installment', False),
            contract_data.get('installment_down_payment'),
            contract_data.get('installment_months'),
            contract_data.get('installment_monthly_amount'),
            contract_data.get('delivery_date'),
            contract_data.get('delivery_location'),
            contract_data.get('status', 'draft'),
            contract_data.get('approval_status', 'pending'),
            contract_data.get('created_by'),
            contract_data.get('notes'),
            contract_data.get('contract_template_id')
        )
        return self.db.execute(query, params)

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID.

        Args:
            contract_id: Contract ID

        Returns:
            Contract instance or None
        """
        query = "SELECT * FROM contracts WHERE id = ?"
        row = self.db.fetch_one(query, (contract_id,))
        return Contract.from_dict(row) if row else None

    def get_by_code(self, contract_code: str) -> Optional[Contract]:
        """Get contract by code.

        Args:
            contract_code: Contract code (e.g., "HD000001")

        Returns:
            Contract instance or None
        """
        query = "SELECT * FROM contracts WHERE contract_code = ?"
        row = self.db.fetch_one(query, (contract_code,))
        return Contract.from_dict(row) if row else None

    def get_all(self, status: Optional[str] = None,
                customer_id: Optional[int] = None,
                car_id: Optional[int] = None) -> List[Contract]:
        """Get contracts with optional filters.

        Args:
            status: Filter by status
            customer_id: Filter by customer ID
            car_id: Filter by car ID

        Returns:
            List of Contract instances
        """
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if customer_id:
            conditions.append("customer_id = ?")
            params.append(customer_id)
        if car_id:
            conditions.append("car_id = ?")
            params.append(car_id)

        query = "SELECT * FROM contracts"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"

        rows = self.db.fetch_all(query, tuple(params) if params else ())
        return [Contract.from_dict(row) for row in rows if row]

    def get_by_customer(self, customer_id: int) -> List[Contract]:
        """Get all contracts for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of Contract instances
        """
        return self.get_all(customer_id=customer_id)

    def update(self, contract_id: int, contract_data: Dict[str, Any]) -> bool:
        """Update contract.

        Args:
            contract_id: Contract ID
            contract_data: Dictionary containing updated data

        Returns:
            bool: True if successful
        """
        allowed_fields = [
            'customer_name', 'customer_phone', 'customer_id_card', 'customer_address',
            'car_vin', 'car_license_plate', 'car_brand', 'car_model', 'car_year', 'car_color',
            'car_price', 'discount_amount', 'discount_reason', 'total_amount',
            'vat_amount', 'final_amount', 'payment_method', 'deposit_amount',
            'paid_amount', 'remaining_amount', 'is_installment',
            'installment_down_payment', 'installment_months', 'installment_monthly_amount',
            'delivery_date', 'delivery_location', 'status', 'approval_status',
            'approved_by', 'approved_at', 'approval_notes',
            'signed_at', 'signed_by_customer', 'signed_by_representative',
            'actual_delivery_date', 'notes', 'contract_template_id'
        ]

        fields = []
        params = []
        for field in allowed_fields:
            if field in contract_data:
                fields.append(f"{field} = ?")
                params.append(contract_data[field])

        if not fields:
            return False

        query = f"UPDATE contracts SET {', '.join(fields)} WHERE id = ?"
        params.append(contract_id)

        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def update_status(self, contract_id: int, new_status: str,
                     changed_by: Optional[int] = None,
                     notes: Optional[str] = None) -> bool:
        """Update contract status and record history.

        Args:
            contract_id: Contract ID
            new_status: New status
            changed_by: User ID who changed status
            notes: Optional notes

        Returns:
            bool: True if successful
        """
        # Get current status
        contract = self.get_by_id(contract_id)
        if not contract:
            return False

        old_status = contract.status

        # Update status
        query = "UPDATE contracts SET status = ? WHERE id = ?"
        try:
            self.db.execute(query, (new_status, contract_id))

            # Record history
            history_query = """
                INSERT INTO contract_status_history
                (contract_id, old_status, new_status, changed_by, notes)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(history_query, (contract_id, old_status, new_status,
                                           changed_by, notes))
            return True
        except Exception:
            return False

    def delete(self, contract_id: int) -> bool:
        """Delete contract permanently.

        Args:
            contract_id: Contract ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM contracts WHERE id = ?"
        try:
            self.db.execute(query, (contract_id,))
            return True
        except Exception:
            return False

    def add_item(self, contract_id: int, item_data: Dict[str, Any]) -> int:
        """Add item to contract.

        Args:
            contract_id: Contract ID
            item_data: Item data dictionary

        Returns:
            int: Item ID
        """
        query = """
            INSERT INTO contract_items
            (contract_id, item_type, item_name, item_description, quantity,
             unit_price, total_price, is_optional, is_selected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            contract_id,
            item_data['item_type'],
            item_data['item_name'],
            item_data.get('item_description'),
            item_data.get('quantity', 1),
            item_data['unit_price'],
            item_data.get('total_price', item_data['unit_price'] * item_data.get('quantity', 1)),
            item_data.get('is_optional', False),
            item_data.get('is_selected', True)
        )
        return self.db.execute(query, params)

    def get_items(self, contract_id: int) -> List[ContractItem]:
        """Get all items for a contract.

        Args:
            contract_id: Contract ID

        Returns:
            List of ContractItem instances
        """
        query = "SELECT * FROM contract_items WHERE contract_id = ? ORDER BY id"
        rows = self.db.fetch_all(query, (contract_id,))
        return [ContractItem.from_dict(row) for row in rows if row]

    def delete_all_items(self, contract_id: int) -> bool:
        """Delete all items for a contract.

        Args:
            contract_id: Contract ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM contract_items WHERE contract_id = ?"
        try:
            self.db.execute(query, (contract_id,))
            return True
        except Exception:
            return False

    def add_payment(self, contract_id: int, payment_data: Dict[str, Any]) -> int:
        """Add payment to contract.

        Args:
            contract_id: Contract ID
            payment_data: Payment data dictionary

        Returns:
            int: Payment ID
        """
        query = """
            INSERT INTO contract_payments
            (contract_id, payment_code, payment_type, amount, payment_method,
             received_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            contract_id,
            payment_data.get('payment_code'),
            payment_data.get('payment_type'),
            payment_data['amount'],
            payment_data.get('payment_method'),
            payment_data.get('received_by'),
            payment_data.get('notes')
        )
        return self.db.execute(query, params)

    def get_payments(self, contract_id: int) -> List[ContractPayment]:
        """Get all payments for a contract.

        Args:
            contract_id: Contract ID

        Returns:
            List of ContractPayment instances
        """
        query = """
            SELECT * FROM contract_payments
            WHERE contract_id = ?
            ORDER BY payment_date DESC
        """
        rows = self.db.fetch_all(query, (contract_id,))
        return [ContractPayment.from_dict(row) for row in rows if row]

    def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID.

        Args:
            payment_id: Payment ID

        Returns:
            Payment dictionary or None
        """
        query = "SELECT * FROM contract_payments WHERE id = ?"
        return self.db.fetch_one(query, (payment_id,))

    def get_status_history(self, contract_id: int) -> List[Dict[str, Any]]:
        """Get status change history for a contract.

        Args:
            contract_id: Contract ID

        Returns:
            List of status history records
        """
        query = """
            SELECT h.*, u.full_name as changed_by_name
            FROM contract_status_history h
            LEFT JOIN users u ON h.changed_by = u.id
            WHERE h.contract_id = ?
            ORDER BY h.changed_at DESC
        """
        return self.db.fetch_all(query, (contract_id,)) or []

    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get contract template by ID.

        Args:
            template_id: Template ID

        Returns:
            Template dictionary or None
        """
        query = "SELECT * FROM contract_templates WHERE id = ?"
        return self.db.fetch_one(query, (template_id,))

    def get_default_template(self) -> Optional[Dict[str, Any]]:
        """Get default contract template.

        Returns:
            Template dictionary or None
        """
        query = "SELECT * FROM contract_templates WHERE is_default = 1 AND is_active = 1 LIMIT 1"
        return self.db.fetch_one(query)

    def get_template_by_code(self, template_code: str) -> Optional[Dict[str, Any]]:
        """Get contract template by code.

        Args:
            template_code: Template code

        Returns:
            Template dictionary or None
        """
        query = "SELECT * FROM contract_templates WHERE template_code = ?"
        return self.db.fetch_one(query, (template_code,))

    def record_print(self, contract_id: int, pdf_path: str,
                    printed_by: Optional[int] = None) -> int:
        """Record contract print.

        Args:
            contract_id: Contract ID
            pdf_path: Path to PDF file
            printed_by: User ID who printed

        Returns:
            int: Print record ID
        """
        # Get next version number
        version_query = """
            SELECT COALESCE(MAX(print_version), 0) + 1 as next_version
            FROM printed_contracts WHERE contract_id = ?
        """
        result = self.db.fetch_one(version_query, (contract_id,))
        version = result['next_version'] if result else 1

        query = """
            INSERT INTO printed_contracts
            (contract_id, print_version, printed_by, pdf_path)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute(query, (contract_id, version, printed_by, pdf_path))
