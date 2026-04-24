"""
Unit tests for ContractRepository.
Tests CRUD operations for contract management.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import sqlite3
import tempfile
from datetime import date, datetime

from database.db_helper import DatabaseHelper
from repositories.contract_repository import ContractRepository
from models.contract import Contract, ContractItem, ContractPayment


class TestContractRepository(unittest.TestCase):
    """Test cases for ContractRepository."""

    def setUp(self):
        """Set up test database and repository."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        # Initialize database with schema
        self.db = DatabaseHelper(self.db_path)
        self._init_schema()

        # Create repository
        self.repo = ContractRepository(self.db)

        # Insert test data (customers, cars, users)
        self._insert_test_data()

    def tearDown(self):
        """Clean up test database."""
        import time
        time.sleep(0.1)  # Give Windows time to release file handles
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except PermissionError:
            pass  # Ignore Windows file lock issues

    def _init_schema(self):
        """Initialize database schema from schema.sql."""
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        # Execute schema (SQLite accepts multiple statements)
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()

    def _insert_test_data(self):
        """Insert test customers, cars, and users."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert test user
        cursor.execute("""
            INSERT INTO users (id, username, full_name, password_hash, role)
            VALUES (1, 'testuser', 'Test User', 'hash123', 'sales')
        """)

        # Insert test customer
        cursor.execute("""
            INSERT INTO customers (id, full_name, phone, id_card, address)
            VALUES (1, 'Nguyen Van A', '0909123456', '123456789', 'Ha Noi')
        """)

        # Insert test car
        cursor.execute("""
            INSERT INTO cars (id, vin, brand, model, year, color, price, status)
            VALUES (1, 'VIN12345678901234', 'Toyota', 'Camry', 2024, 'Black', 1000000000, 'available')
        """)

        conn.commit()
        conn.close()

    def test_create_contract(self):
        """Test creating a new contract with auto-generated code."""
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'customer_phone': '0909123456',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_model': 'Camry',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,  # Including VAT
            'created_by': 1
        }

        contract_id = self.repo.create(contract_data)

        # Verify contract was created
        self.assertIsNotNone(contract_id)
        self.assertIsInstance(contract_id, int)

        # Verify contract code format (HD000001)
        contract = self.repo.get_by_id(contract_id)
        self.assertIsNotNone(contract)
        self.assertEqual(contract.contract_code, 'HD000001')
        self.assertEqual(contract.customer_id, 1)
        self.assertEqual(contract.car_id, 1)

    def test_create_contract_with_custom_code(self):
        """Test creating a contract with custom contract code."""
        contract_data = {
            'contract_code': 'HD999999',
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }

        contract_id = self.repo.create(contract_data)
        contract = self.repo.get_by_id(contract_id)

        self.assertEqual(contract.contract_code, 'HD999999')

    def test_get_by_customer(self):
        """Test retrieving contracts by customer ID."""
        # Create multiple contracts for customer 1
        contract_data_1 = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }
        contract_data_2 = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Honda',
            'car_price': 800000000,
            'total_amount': 800000000,
            'final_amount': 880000000,
            'created_by': 1
        }

        self.repo.create(contract_data_1)
        self.repo.create(contract_data_2)

        # Get contracts by customer
        contracts = self.repo.get_by_customer(1)

        self.assertEqual(len(contracts), 2)
        self.assertEqual(contracts[0].customer_id, 1)
        self.assertEqual(contracts[1].customer_id, 1)

    def test_get_by_customer_empty(self):
        """Test retrieving contracts for customer with no contracts."""
        contracts = self.repo.get_by_customer(999)
        self.assertEqual(len(contracts), 0)

    def test_get_by_code(self):
        """Test retrieving contract by contract code."""
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }

        contract_id = self.repo.create(contract_data)

        # Get by code
        contract = self.repo.get_by_code('HD000001')

        self.assertIsNotNone(contract)
        self.assertEqual(contract.id, contract_id)
        self.assertEqual(contract.customer_name, 'Nguyen Van A')

    def test_get_by_code_not_found(self):
        """Test retrieving non-existent contract code."""
        contract = self.repo.get_by_code('HD999999')
        self.assertIsNone(contract)

    def test_update_contract(self):
        """Test updating contract fields."""
        # Create contract
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }
        contract_id = self.repo.create(contract_data)

        # Update contract
        update_data = {
            'customer_name': 'Nguyen Van B',
            'notes': 'Updated notes',
            'discount_amount': 50000000
        }
        result = self.repo.update(contract_id, update_data)

        self.assertTrue(result)

        # Verify update
        contract = self.repo.get_by_id(contract_id)
        self.assertEqual(contract.customer_name, 'Nguyen Van B')
        self.assertEqual(contract.notes, 'Updated notes')
        self.assertEqual(contract.discount_amount, 50000000)

    def test_update_status(self):
        """Test updating contract status with history."""
        # Create contract
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1,
            'status': 'draft'
        }
        contract_id = self.repo.create(contract_data)

        # Update status
        result = self.repo.update_status(
            contract_id, 'pending', changed_by=1, notes='Sent for approval'
        )

        self.assertTrue(result)

        # Verify status change
        contract = self.repo.get_by_id(contract_id)
        self.assertEqual(contract.status, 'pending')

        # Verify history recorded
        history = self.repo.get_status_history(contract_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['old_status'], 'draft')
        self.assertEqual(history[0]['new_status'], 'pending')

    def test_add_and_get_items(self):
        """Test adding items to contract."""
        # Create contract
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }
        contract_id = self.repo.create(contract_data)

        # Add item
        item_data = {
            'item_type': 'accessory',
            'item_name': 'Floor Mats',
            'quantity': 1,
            'unit_price': 500000,
            'total_price': 500000
        }
        item_id = self.repo.add_item(contract_id, item_data)

        self.assertIsNotNone(item_id)

        # Get items
        items = self.repo.get_items(contract_id)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].item_name, 'Floor Mats')
        self.assertEqual(items[0].unit_price, 500000)

    def test_add_and_get_payments(self):
        """Test adding payments to contract."""
        # Create contract
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Nguyen Van A',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }
        contract_id = self.repo.create(contract_data)

        # Add payment
        payment_data = {
            'payment_code': 'PT000001',
            'payment_type': 'deposit',
            'amount': 100000000,
            'payment_method': 'cash',
            'received_by': 1
        }
        payment_id = self.repo.add_payment(contract_id, payment_data)

        self.assertIsNotNone(payment_id)

        # Get payments
        payments = self.repo.get_payments(contract_id)
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].amount, 100000000)
        self.assertEqual(payments[0].payment_type, 'deposit')

    def test_get_template(self):
        """Test retrieving default contract template."""
        template = self.repo.get_default_template()

        self.assertIsNotNone(template)
        self.assertEqual(template['id'], 1)
        self.assertEqual(template['template_code'], 'CONTRACT_DEFAULT')

    def test_generate_contract_code_sequence(self):
        """Test auto-incrementing contract code generation."""
        contract_data = {
            'customer_id': 1,
            'customer_name': 'Test',
            'car_id': 1,
            'car_brand': 'Toyota',
            'car_price': 1000000000,
            'total_amount': 1000000000,
            'final_amount': 1100000000,
            'created_by': 1
        }

        # Create first contract
        id1 = self.repo.create(contract_data.copy())
        contract1 = self.repo.get_by_id(id1)

        # Create second contract
        id2 = self.repo.create(contract_data.copy())
        contract2 = self.repo.get_by_id(id2)

        # Verify sequential codes
        self.assertEqual(contract1.contract_code, 'HD000001')
        self.assertEqual(contract2.contract_code, 'HD000002')


if __name__ == '__main__':
    unittest.main()
