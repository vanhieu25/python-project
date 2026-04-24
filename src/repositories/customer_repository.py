"""
Customer Repository Module
Provides data access operations for Customer model.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper
from ..models.customer import Customer


class CustomerRepository:
    """Repository for Customer data access."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def _generate_customer_code(self) -> str:
        """Generate next customer code (KH000001, KH000002, ...).

        Returns:
            str: Next customer code
        """
        result = self.db.fetch_one(
            "SELECT customer_code FROM customers WHERE customer_code LIKE 'KH%' "
            "ORDER BY customer_code DESC LIMIT 1"
        )
        if result and result['customer_code']:
            last_num = int(result['customer_code'][2:])
            return f"KH{last_num + 1:06d}"
        return "KH000001"

    def create(self, customer_data: Dict[str, Any]) -> int:
        """Create new customer with auto-generated code.

        Args:
            customer_data: Dictionary containing customer data

        Returns:
            int: ID of created customer
        """
        # Auto-generate customer code if not provided
        if not customer_data.get('customer_code'):
            customer_data['customer_code'] = self._generate_customer_code()

        query = """
            INSERT INTO customers (
                customer_code, customer_type, full_name, id_card, date_of_birth, gender,
                company_name, tax_code, business_registration,
                phone, phone2, email, address, province, district, ward,
                customer_class, source, notes, assigned_to, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            customer_data['customer_code'],
            customer_data.get('customer_type', 'individual'),
            customer_data['full_name'],
            customer_data.get('id_card'),
            customer_data.get('date_of_birth'),
            customer_data.get('gender'),
            customer_data.get('company_name'),
            customer_data.get('tax_code'),
            customer_data.get('business_registration'),
            customer_data.get('phone'),
            customer_data.get('phone2'),
            customer_data.get('email'),
            customer_data.get('address'),
            customer_data.get('province'),
            customer_data.get('district'),
            customer_data.get('ward'),
            customer_data.get('customer_class', 'regular'),
            customer_data.get('source'),
            customer_data.get('notes'),
            customer_data.get('assigned_to'),
            customer_data.get('created_by')
        )
        return self.db.execute(query, params)

    def get_by_id(self, customer_id: int, include_deleted: bool = False) -> Optional[Customer]:
        """Get customer by ID.

        Args:
            customer_id: Customer ID
            include_deleted: Whether to include soft-deleted customers

        Returns:
            Customer instance or None
        """
        query = "SELECT * FROM customers WHERE id = ?"
        if not include_deleted:
            query += " AND is_deleted = 0"
        row = self.db.fetch_one(query, (customer_id,))
        return Customer.from_dict(row) if row else None

    def get_by_code(self, customer_code: str) -> Optional[Customer]:
        """Get customer by customer code.

        Args:
            customer_code: Customer code (e.g., "KH000001")

        Returns:
            Customer instance or None
        """
        query = "SELECT * FROM customers WHERE customer_code = ? AND is_deleted = 0"
        row = self.db.fetch_one(query, (customer_code,))
        return Customer.from_dict(row) if row else None

    def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number.

        Args:
            phone: Phone number

        Returns:
            Customer instance or None
        """
        query = """
            SELECT * FROM customers
            WHERE (phone = ? OR phone2 = ?) AND is_deleted = 0
        """
        row = self.db.fetch_one(query, (phone, phone))
        return Customer.from_dict(row) if row else None

    def get_all(self, customer_type: Optional[str] = None,
                customer_class: Optional[str] = None,
                assigned_to: Optional[int] = None,
                include_deleted: bool = False) -> List[Customer]:
        """Get all customers with optional filters.

        Args:
            customer_type: Filter by type ('individual' or 'business')
            customer_class: Filter by class ('regular', 'potential', 'vip')
            assigned_to: Filter by assigned staff ID
            include_deleted: Whether to include soft-deleted customers

        Returns:
            List of Customer instances
        """
        conditions = []
        params = []

        if not include_deleted:
            conditions.append("is_deleted = 0")
        if customer_type:
            conditions.append("customer_type = ?")
            params.append(customer_type)
        if customer_class:
            conditions.append("customer_class = ?")
            params.append(customer_class)
        if assigned_to:
            conditions.append("assigned_to = ?")
            params.append(assigned_to)

        query = "SELECT * FROM customers"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"

        rows = self.db.fetch_all(query, tuple(params) if params else ())
        return [Customer.from_dict(row) for row in rows if row]

    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Update customer.

        Args:
            customer_id: Customer ID
            customer_data: Dictionary containing updated data

        Returns:
            bool: True if successful
        """
        allowed_fields = [
            'full_name', 'id_card', 'date_of_birth', 'gender',
            'company_name', 'tax_code', 'business_registration',
            'phone', 'phone2', 'email', 'address', 'province', 'district', 'ward',
            'customer_class', 'source', 'notes', 'assigned_to'
        ]

        fields = []
        params = []
        for field in allowed_fields:
            if field in customer_data:
                fields.append(f"{field} = ?")
                params.append(customer_data[field])

        if not fields:
            return False

        query = f"UPDATE customers SET {', '.join(fields)} WHERE id = ?"
        params.append(customer_id)

        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def soft_delete(self, customer_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete customer.

        Args:
            customer_id: Customer ID
            deleted_by: User ID who deleted

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE customers SET
                is_deleted = 1,
                deleted_at = ?,
                deleted_by = ?
            WHERE id = ?
        """
        try:
            self.db.execute(query, (datetime.now(), deleted_by, customer_id))
            return True
        except Exception:
            return False

    def restore(self, customer_id: int) -> bool:
        """Restore soft-deleted customer.

        Args:
            customer_id: Customer ID

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE customers SET
                is_deleted = 0,
                deleted_at = NULL,
                deleted_by = NULL
            WHERE id = ? AND is_deleted = 1
        """
        try:
            self.db.execute(query, (customer_id,))
            return True
        except Exception:
            return False

    def delete_permanently(self, customer_id: int) -> bool:
        """Permanently delete customer.

        Args:
            customer_id: Customer ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM customers WHERE id = ?"
        try:
            self.db.execute(query, (customer_id,))
            return True
        except Exception:
            return False

    def exists(self, phone: Optional[str] = None,
               email: Optional[str] = None,
               id_card: Optional[str] = None,
               exclude_id: Optional[int] = None) -> bool:
        """Check if customer exists by phone, email, or id_card.

        Args:
            phone: Phone number to check
            email: Email to check
            id_card: ID card number to check
            exclude_id: Customer ID to exclude from check

        Returns:
            bool: True if exists
        """
        conditions = []
        params = []

        if phone:
            conditions.append("phone = ?")
            params.append(phone)
        if email:
            conditions.append("email = ?")
            params.append(email)
        if id_card:
            conditions.append("id_card = ?")
            params.append(id_card)

        if not conditions:
            return False

        query = f"SELECT 1 FROM customers WHERE ({' OR '.join(conditions)}) AND is_deleted = 0"
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)

        result = self.db.fetch_one(query, tuple(params))
        return result is not None

    def count(self, customer_type: Optional[str] = None,
              customer_class: Optional[str] = None) -> int:
        """Count customers.

        Args:
            customer_type: Filter by type
            customer_class: Filter by class

        Returns:
            int: Number of customers
        """
        query = "SELECT COUNT(*) as count FROM customers WHERE is_deleted = 0"
        params = []

        if customer_type:
            query += " AND customer_type = ?"
            params.append(customer_type)
        if customer_class:
            query += " AND customer_class = ?"
            params.append(customer_class)

        result = self.db.fetch_one(query, tuple(params) if params else ())
        return result['count'] if result else 0

    def search(self, keyword: str) -> List[Customer]:
        """Search customers by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List of matching customers
        """
        search_term = f"%{keyword}%"
        query = """
            SELECT * FROM customers
            WHERE is_deleted = 0 AND (
                full_name LIKE ? OR
                customer_code LIKE ? OR
                phone LIKE ? OR
                email LIKE ? OR
                company_name LIKE ? OR
                id_card LIKE ?
            )
            ORDER BY full_name ASC
        """
        rows = self.db.fetch_all(query, (search_term, search_term, search_term,
                                         search_term, search_term, search_term))
        return [Customer.from_dict(row) for row in rows if row]

    def get_vip_customers(self) -> List[Customer]:
        """Get all VIP customers.

        Returns:
            List of VIP customers
        """
        return self.get_all(customer_class='vip')

    def get_assigned_customers(self, user_id: int) -> List[Customer]:
        """Get customers assigned to a specific user.

        Args:
            user_id: User ID

        Returns:
            List of assigned customers
        """
        return self.get_all(assigned_to=user_id)
