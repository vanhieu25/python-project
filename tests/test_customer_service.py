"""
Unit tests for CustomerService
"""

import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.repositories.customer_history_repository import CustomerHistoryRepository
from src.services.customer_service import (
    CustomerService, DuplicateCustomerError, CustomerNotFoundError,
    CustomerValidationServiceError
)


class TestCustomerService(unittest.TestCase):
    """Tests for customer service."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.customer_repo = CustomerRepository(self.db)
        self.history_repo = CustomerHistoryRepository(self.db)
        self.service = CustomerService(self.customer_repo, self.history_repo)

        self.user_id = 1

        # Clear existing data
        self.db.execute("DELETE FROM customers")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_individual_customer(self):
        """Test creating individual customer."""
        customer = self.service.create_customer({
            'customer_type': 'individual',
            'full_name': 'Nguyễn Văn Test',
            'phone': '0901234567',
            'email': 'test@email.com',
            'id_card': '012345678901'
        }, self.user_id)

        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Nguyễn Văn Test')
        self.assertEqual(customer.customer_type, 'individual')
        self.assertTrue(customer.customer_code.startswith('KH'))

    def test_create_business_customer(self):
        """Test creating business customer."""
        customer = self.service.create_customer({
            'customer_type': 'business',
            'full_name': 'Người đại diện',
            'company_name': 'Công ty Test',
            'tax_code': '0123456789',
            'phone': '0901234568'
        }, self.user_id)

        self.assertIsNotNone(customer)
        self.assertEqual(customer.customer_type, 'business')
        self.assertEqual(customer.company_name, 'Công ty Test')

    def test_create_customer_validation_error(self):
        """Test validation error on create."""
        with self.assertRaises(CustomerValidationServiceError):
            self.service.create_customer({
                'customer_type': 'individual',
                'full_name': '',  # Empty name
                'phone': '0901234567'
            }, self.user_id)

    def test_duplicate_phone(self):
        """Test cannot create with duplicate phone."""
        self.service.create_customer({
            'full_name': 'Customer 1',
            'phone': '0901234567'
        }, self.user_id)

        with self.assertRaises(DuplicateCustomerError):
            self.service.create_customer({
                'full_name': 'Customer 2',
                'phone': '0901234567'
            }, self.user_id)

    def test_duplicate_email(self):
        """Test cannot create with duplicate email."""
        self.service.create_customer({
            'full_name': 'Customer 1',
            'phone': '0901111111',
            'email': 'test@example.com'
        }, self.user_id)

        with self.assertRaises(DuplicateCustomerError):
            self.service.create_customer({
                'full_name': 'Customer 2',
                'phone': '0902222222',
                'email': 'test@example.com'
            }, self.user_id)

    def test_duplicate_id_card(self):
        """Test cannot create with duplicate ID card."""
        self.service.create_customer({
            'full_name': 'Customer 1',
            'phone': '0901111111',
            'id_card': '012345678901'
        }, self.user_id)

        with self.assertRaises(DuplicateCustomerError):
            self.service.create_customer({
                'full_name': 'Customer 2',
                'phone': '0902222222',
                'id_card': '012345678901'
            }, self.user_id)

    def test_update_customer(self):
        """Test updating customer."""
        customer = self.service.create_customer({
            'full_name': 'Original Name',
            'phone': '0901111111'
        }, self.user_id)

        updated = self.service.update_customer(
            customer.id,
            {'full_name': 'Updated Name'},
            self.user_id
        )

        self.assertEqual(updated.full_name, 'Updated Name')

        # Check history
        history = self.history_repo.get_history(customer.id)
        self.assertEqual(len(history), 2)  # create + update

    def test_update_nonexistent_customer(self):
        """Test updating nonexistent customer."""
        with self.assertRaises(CustomerNotFoundError):
            self.service.update_customer(99999, {'full_name': 'New Name'}, self.user_id)

    def test_update_with_duplicate_phone(self):
        """Test update with duplicate phone."""
        customer1 = self.service.create_customer({
            'full_name': 'Customer 1',
            'phone': '0901111111'
        }, self.user_id)

        customer2 = self.service.create_customer({
            'full_name': 'Customer 2',
            'phone': '0902222222'
        }, self.user_id)

        with self.assertRaises(DuplicateCustomerError):
            self.service.update_customer(
                customer2.id,
                {'phone': '0901111111'},  # Phone of customer1
                self.user_id
            )

    def test_soft_delete(self):
        """Test soft delete."""
        customer = self.service.create_customer({
            'full_name': 'To Delete',
            'phone': '0902222222'
        }, self.user_id)

        self.service.delete_customer(customer.id, self.user_id,
                                    reason="Khách hàng yêu cầu")

        # Should not be found in normal query
        deleted = self.customer_repo.get_by_id(customer.id)
        self.assertIsNone(deleted)

        # Should exist with include_deleted
        exists = self.customer_repo.get_by_id(customer.id, include_deleted=True)
        self.assertIsNotNone(exists)
        self.assertTrue(exists.is_deleted)

        # Check history
        history = self.history_repo.get_history(customer.id)
        delete_records = [h for h in history if h['action'] == 'delete']
        self.assertEqual(len(delete_records), 1)

    def test_restore_customer(self):
        """Test restoring deleted customer."""
        customer = self.service.create_customer({
            'full_name': 'To Restore',
            'phone': '0903333333'
        }, self.user_id)

        self.service.delete_customer(customer.id, self.user_id)
        restored = self.service.restore_customer(customer.id, self.user_id)

        self.assertFalse(restored.is_deleted)
        self.assertIsNone(restored.deleted_at)

        # Check history
        history = self.history_repo.get_history(customer.id)
        restore_records = [h for h in history if h['action'] == 'restore']
        self.assertEqual(len(restore_records), 1)

    def test_restore_not_deleted_customer(self):
        """Test restoring customer that wasn't deleted."""
        customer = self.service.create_customer({
            'full_name': 'Not Deleted',
            'phone': '0904444444'
        }, self.user_id)

        from src.services.customer_service import CustomerServiceError
        with self.assertRaises(CustomerServiceError):
            self.service.restore_customer(customer.id, self.user_id)

    def test_delete_nonexistent_customer(self):
        """Test deleting nonexistent customer."""
        with self.assertRaises(CustomerNotFoundError):
            self.service.delete_customer(99999, self.user_id)

    def test_get_customer(self):
        """Test getting customer."""
        customer = self.service.create_customer({
            'full_name': 'Test Customer',
            'phone': '0905555555'
        }, self.user_id)

        fetched = self.service.get_customer(customer.id)
        self.assertEqual(fetched.id, customer.id)
        self.assertEqual(fetched.full_name, 'Test Customer')

    def test_get_nonexistent_customer(self):
        """Test getting nonexistent customer."""
        with self.assertRaises(CustomerNotFoundError):
            self.service.get_customer(99999)

    def test_list_customers(self):
        """Test listing customers."""
        self.service.create_customer({
            'full_name': 'VIP Customer',
            'phone': '0901111111',
            'customer_class': 'vip'
        }, self.user_id)

        self.service.create_customer({
            'full_name': 'Regular Customer',
            'phone': '0902222222',
            'customer_class': 'regular'
        }, self.user_id)

        customers = self.service.list_customers()
        self.assertEqual(len(customers), 2)

        vip_customers = self.service.list_customers(customer_class='vip')
        self.assertEqual(len(vip_customers), 1)

    def test_get_customer_history(self):
        """Test getting customer history."""
        customer = self.service.create_customer({
            'full_name': 'History Test',
            'phone': '0906666666'
        }, self.user_id)

        self.service.update_customer(customer.id, {'full_name': 'Updated'}, self.user_id)

        history = self.service.get_customer_history(customer.id)
        self.assertEqual(len(history), 2)  # create + update

    def test_permanent_delete(self):
        """Test permanent delete."""
        customer = self.service.create_customer({
            'full_name': 'To Delete Permanently',
            'phone': '0907777777'
        }, self.user_id)

        self.service.delete_customer(customer.id, self.user_id, permanent=True)

        # Should not exist at all
        exists = self.customer_repo.get_by_id(customer.id, include_deleted=True)
        self.assertIsNone(exists)


if __name__ == '__main__':
    unittest.main()
