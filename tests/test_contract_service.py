"""
Unit tests for ContractService.
Tests business logic and validation for contract management.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import sqlite3
import tempfile
from datetime import date

from database.db_helper import DatabaseHelper
from repositories.contract_repository import ContractRepository
from services.contract_service import ContractService, Result


class MockCustomer:
    """Mock customer for testing."""
    def __init__(self, id, full_name, phone, id_card=None, address=None):
        self.id = id
        self.full_name = full_name
        self.phone = phone
        self.id_card = id_card
        self.address = address


class MockCar:
    """Mock car for testing."""
    def __init__(self, id, vin, brand, model, year, color, price, status='available'):
        self.id = id
        self.vin = vin
        self.brand = brand
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.status = status


class MockRepository:
    """Mock repository for testing."""
    def __init__(self, data=None):
        self.data = data or {}

    def get_by_id(self, id):
        return self.data.get(id)


class TestContractService(unittest.TestCase):
    """Test cases for ContractService."""

    def setUp(self):
        """Set up test database and service."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        self.db = DatabaseHelper(self.db_path)
        self._init_schema()

        self.contract_repo = ContractRepository(self.db)
        self.service = ContractService(self.contract_repo)

        # Mock repositories
        self.customer_repo = MockRepository({
            1: MockCustomer(1, "Nguyen Van A", "0909123456", "123456789", "Ha Noi"),
            2: MockCustomer(2, "Tran Van B", "0912345678", "987654321", "TP.HCM")
        })
        self.car_repo = MockRepository({
            1: MockCar(1, "VIN123456", "Toyota", "Camry", 2024, "Black", 1000000000),
            2: MockCar(2, "VIN654321", "Honda", "Civic", 2024, "White", 800000000, 'sold')
        })

        self.service_with_deps = ContractService(
            self.contract_repo,
            self.customer_repo,
            self.car_repo
        )

        self._insert_test_data()

    def tearDown(self):
        """Clean up test database."""
        import time
        time.sleep(0.1)
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except PermissionError:
            pass

    def _init_schema(self):
        """Initialize database schema."""
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()

    def _insert_test_data(self):
        """Insert test data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (id, username, full_name, password_hash, role)
            VALUES (1, 'testuser', 'Test User', 'hash', 'sales')
        """)

        cursor.execute("""
            INSERT INTO contracts (contract_code, customer_id, customer_name, car_id,
                                   car_brand, car_model, car_price, total_amount,
                                   final_amount, created_by, status)
            VALUES ('HD001', 1, 'Nguyen Van A', 1, 'Toyota', 'Camry', 1000000000,
                    1000000000, 1100000000, 1, 'draft')
        """)

        cursor.execute("""
            INSERT INTO contracts (contract_code, customer_id, customer_name, car_id,
                                   car_brand, car_model, car_price, total_amount,
                                   final_amount, created_by, status)
            VALUES ('HD002', 2, 'Tran Van B', 2, 'Honda', 'Civic', 800000000,
                    800000000, 880000000, 1, 'approved')
        """)

        conn.commit()
        conn.close()

    def test_create_contract_success(self):
        """Test creating contract with valid data."""
        data = {
            'customer_id': 1,
            'car_id': 1,
            'car_price': 1200000000,  # User can override car price
            'discount_amount': 100000000
        }

        result = self.service_with_deps.create_contract(data, created_by=1)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        contract = result.data
        self.assertEqual(contract.customer_name, "Nguyen Van A")
        self.assertEqual(contract.car_brand, "Toyota")
        # car_price from input is used (user can override)
        self.assertEqual(contract.car_price, 1200000000)
        self.assertEqual(contract.discount_amount, 100000000)
        self.assertEqual(contract.total_amount, 1100000000)  # 1200M - 100M
        self.assertEqual(contract.vat_amount, 110000000)  # 10%
        self.assertEqual(contract.final_amount, 1210000000)  # 1100M + 110M
        self.assertEqual(contract.status, 'draft')

    def test_create_contract_missing_customer_id(self):
        """Test creating contract without customer_id."""
        data = {
            'car_id': 1,
            'car_price': 1000000000
        }

        result = self.service.create_contract(data, created_by=1)

        self.assertFalse(result.success)
        self.assertIn('customer_id', result.error)

    def test_create_contract_missing_car_id(self):
        """Test creating contract without car_id."""
        data = {
            'customer_id': 1,
            'car_price': 1000000000
        }

        result = self.service.create_contract(data, created_by=1)

        self.assertFalse(result.success)
        self.assertIn('car_id', result.error)

    def test_create_contract_customer_not_found(self):
        """Test creating contract with non-existent customer."""
        data = {
            'customer_id': 999,
            'car_id': 1,
            'car_price': 1000000000
        }

        result = self.service_with_deps.create_contract(data, created_by=1)

        self.assertFalse(result.success)
        self.assertIn('Customer not found', result.error)

    def test_create_contract_car_not_available(self):
        """Test creating contract with unavailable car."""
        data = {
            'customer_id': 1,
            'car_id': 2,  # Car with status 'sold'
            'car_price': 800000000
        }

        result = self.service_with_deps.create_contract(data, created_by=1)

        self.assertFalse(result.success)
        self.assertIn('not available', result.error)

    def test_get_contract_detail(self):
        """Test getting contract detail with related data."""
        # Create contract with items and payments
        data = {
            'customer_id': 1,
            'car_id': 1,
            'car_price': 1000000000
        }
        create_result = self.service.create_contract(data, created_by=1)
        contract_id = create_result.data.id

        # Add item
        self.contract_repo.add_item(contract_id, {
            'item_type': 'accessory',
            'item_name': 'Floor Mats',
            'quantity': 1,
            'unit_price': 500000,
            'total_price': 500000
        })

        # Get detail
        contract = self.service.get_contract_detail(contract_id)

        self.assertIsNotNone(contract)
        self.assertEqual(len(contract.items), 1)
        self.assertEqual(contract.items[0].item_name, 'Floor Mats')

    def test_get_contract_by_code(self):
        """Test getting contract by code."""
        contract = self.service.get_contract_by_code('HD001')

        self.assertIsNotNone(contract)
        self.assertEqual(contract.customer_name, 'Nguyen Van A')

    def test_search_contracts_by_status(self):
        """Test searching contracts by status."""
        result = self.service.search_contracts(filters={'status': 'draft'})

        self.assertEqual(result.total, 1)
        self.assertEqual(result.items[0].status, 'draft')

    def test_search_contracts_by_customer_name(self):
        """Test searching contracts by customer name."""
        result = self.service.search_contracts(filters={'customer_name': 'Nguyen'})

        self.assertEqual(result.total, 1)
        self.assertEqual(result.items[0].customer_name, 'Nguyen Van A')

    def test_search_contracts_pagination(self):
        """Test search pagination."""
        result = self.service.search_contracts(page=1, per_page=1)

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.total, 2)
        self.assertEqual(result.total_pages, 2)

    def test_update_contract_success(self):
        """Test updating draft contract."""
        # Get the draft contract
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.update_contract(
            contract.id,
            {'notes': 'Updated note', 'discount_amount': 50000000},
            updated_by=1
        )

        self.assertTrue(result.success)

        # Verify update
        updated = self.service.get_contract_by_code('HD001')
        self.assertEqual(updated.notes, 'Updated note')

    def test_update_contract_not_draft(self):
        """Test updating non-draft contract."""
        # Get the approved contract
        contract = self.service.get_contract_by_code('HD002')

        result = self.service.update_contract(
            contract.id,
            {'notes': 'Updated note'},
            updated_by=1
        )

        self.assertFalse(result.success)
        self.assertIn('Cannot update', result.error)

    def test_update_contract_wrong_user(self):
        """Test updating contract by non-creator."""
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.update_contract(
            contract.id,
            {'notes': 'Updated note'},
            updated_by=999  # Different user
        )

        self.assertFalse(result.success)
        self.assertIn('Permission denied', result.error)

    def test_delete_contract_success(self):
        """Test deleting draft contract."""
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.delete_contract(contract.id, deleted_by=1)

        self.assertTrue(result.success)

        # Verify deleted
        deleted = self.service.get_contract_by_code('HD001')
        self.assertIsNone(deleted)

    def test_delete_contract_not_draft(self):
        """Test deleting non-draft contract."""
        contract = self.service.get_contract_by_code('HD002')

        result = self.service.delete_contract(contract.id, deleted_by=1)

        self.assertFalse(result.success)
        self.assertIn('Cannot delete', result.error)

    def test_add_item_to_contract(self):
        """Test adding item to contract."""
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.add_item_to_contract(contract.id, {
            'item_type': 'service',
            'item_name': 'Insurance Package',
            'quantity': 1,
            'unit_price': 20000000
        })

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, int)  # Returns item_id

    def test_add_item_to_non_draft_contract(self):
        """Test adding item to non-draft contract."""
        contract = self.service.get_contract_by_code('HD002')

        result = self.service.add_item_to_contract(contract.id, {
            'item_type': 'service',
            'item_name': 'Insurance',
            'quantity': 1,
            'unit_price': 1000000
        })

        self.assertFalse(result.success)
        self.assertIn('submitted', result.error)

    def test_calculate_totals(self):
        """Test calculating contract totals."""
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.calculate_totals(contract.id)

        self.assertTrue(result.success)
        totals = result.data
        self.assertEqual(totals['car_price'], 1000000000)
        self.assertIn('items_total', totals)

    def test_cancel_contract(self):
        """Test cancelling contract."""
        contract = self.service.get_contract_by_code('HD001')

        result = self.service.cancel_contract(contract.id, cancelled_by=1, reason="Test cancellation")

        self.assertTrue(result.success)

        # Verify cancelled
        cancelled = self.service.get_contract_by_code('HD001')
        self.assertEqual(cancelled.status, 'cancelled')

    def test_get_contract_statistics(self):
        """Test getting contract statistics."""
        stats = self.service.get_contract_statistics()

        self.assertEqual(stats['total_contracts'], 2)
        self.assertIn('draft', stats['by_status'])
        self.assertIn('approved', stats['by_status'])

    def test_get_recent_contracts(self):
        """Test getting recent contracts."""
        recent = self.service.get_recent_contracts(limit=5)

        self.assertEqual(len(recent), 2)
        # Should be sorted by created_at DESC
        self.assertEqual(recent[0].contract_code, 'HD002')


if __name__ == '__main__':
    unittest.main()
