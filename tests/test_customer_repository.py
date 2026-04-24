"""
Unit tests for CustomerRepository
"""

import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.models.customer import Customer


class TestCustomerRepository(unittest.TestCase):
    """Tests for customer repository."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.repo = CustomerRepository(self.db)

        # Clear existing customers (from seed data) for clean tests
        self.db.execute("DELETE FROM customers")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_individual_customer(self):
        """Test creating individual customer."""
        customer_id = self.repo.create({
            'customer_type': 'individual',
            'full_name': 'Nguyễn Văn Test',
            'phone': '0901234567',
            'customer_class': 'regular'
        })
        self.assertIsNotNone(customer_id)

        customer = self.repo.get_by_id(customer_id)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Nguyễn Văn Test')
        self.assertEqual(customer.customer_type, 'individual')
        self.assertTrue(customer.customer_code.startswith('KH'))

    def test_create_business_customer(self):
        """Test creating business customer."""
        customer_id = self.repo.create({
            'customer_type': 'business',
            'full_name': 'Người đại diện',
            'company_name': 'Công ty Test',
            'tax_code': '0123456789',
            'phone': '0901234568'
        })
        self.assertIsNotNone(customer_id)

        customer = self.repo.get_by_id(customer_id)
        self.assertEqual(customer.customer_type, 'business')
        self.assertEqual(customer.company_name, 'Công ty Test')

    def test_customer_code_generation(self):
        """Test auto-generated customer codes."""
        id1 = self.repo.create({'full_name': 'KH 1', 'phone': '0911111111'})
        id2 = self.repo.create({'full_name': 'KH 2', 'phone': '0922222222'})

        customer1 = self.repo.get_by_id(id1)
        customer2 = self.repo.get_by_id(id2)

        self.assertEqual(customer1.customer_code, 'KH000001')
        self.assertEqual(customer2.customer_code, 'KH000002')

    def test_get_by_id(self):
        """Test getting customer by ID."""
        customer_id = self.repo.create({
            'full_name': 'Test Customer',
            'phone': '0909999999'
        })

        customer = self.repo.get_by_id(customer_id)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Test Customer')

        # Non-existent ID
        customer = self.repo.get_by_id(99999)
        self.assertIsNone(customer)

    def test_get_by_code(self):
        """Test getting customer by code."""
        customer_id = self.repo.create({
            'full_name': 'Test By Code',
            'phone': '0908888888'
        })

        customer = self.repo.get_by_code('KH000001')
        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Test By Code')

    def test_get_by_phone(self):
        """Test getting customer by phone."""
        self.repo.create({
            'full_name': 'Phone Test',
            'phone': '0907777777',
            'phone2': '0911111111'
        })

        customer = self.repo.get_by_phone('0907777777')
        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Phone Test')

        # Test phone2
        customer = self.repo.get_by_phone('0911111111')
        self.assertIsNotNone(customer)

    def test_get_all(self):
        """Test getting all customers."""
        self.repo.create({'full_name': 'A', 'phone': '0901111111'})
        self.repo.create({'full_name': 'B', 'phone': '0902222222'})
        self.repo.create({'full_name': 'C', 'phone': '0903333333'})

        customers = self.repo.get_all()
        self.assertEqual(len(customers), 3)

    def test_get_all_with_filters(self):
        """Test getting customers with filters."""
        self.repo.create({
            'full_name': 'VIP Customer',
            'phone': '0901111111',
            'customer_class': 'vip'
        })
        self.repo.create({
            'full_name': 'Regular Customer',
            'phone': '0902222222',
            'customer_class': 'regular'
        })
        self.repo.create({
            'full_name': 'Business Customer',
            'phone': '0903333333',
            'customer_type': 'business'
        })

        vip_customers = self.repo.get_all(customer_class='vip')
        self.assertEqual(len(vip_customers), 1)
        self.assertEqual(vip_customers[0].full_name, 'VIP Customer')

        business_customers = self.repo.get_all(customer_type='business')
        self.assertEqual(len(business_customers), 1)

    def test_update(self):
        """Test updating customer."""
        customer_id = self.repo.create({
            'full_name': 'Original Name',
            'phone': '0906666666'
        })

        success = self.repo.update(customer_id, {
            'full_name': 'Updated Name',
            'email': 'updated@email.com'
        })
        self.assertTrue(success)

        customer = self.repo.get_by_id(customer_id)
        self.assertEqual(customer.full_name, 'Updated Name')
        self.assertEqual(customer.email, 'updated@email.com')

    def test_exists_by_phone(self):
        """Test checking duplicate phone."""
        self.repo.create({'full_name': 'Test', 'phone': '0901234567'})
        self.assertTrue(self.repo.exists(phone='0901234567'))
        self.assertFalse(self.repo.exists(phone='0999999999'))

    def test_exists_by_email(self):
        """Test checking duplicate email."""
        self.repo.create({
            'full_name': 'Test',
            'phone': '0901111111',
            'email': 'test@example.com'
        })
        self.assertTrue(self.repo.exists(email='test@example.com'))
        self.assertFalse(self.repo.exists(email='notfound@example.com'))

    def test_exists_by_id_card(self):
        """Test checking duplicate ID card."""
        self.repo.create({
            'full_name': 'Test',
            'phone': '0901111111',
            'id_card': '012345678901'
        })
        self.assertTrue(self.repo.exists(id_card='012345678901'))
        self.assertFalse(self.repo.exists(id_card='999999999999'))

    def test_soft_delete(self):
        """Test soft delete."""
        customer_id = self.repo.create({
            'full_name': 'To Delete',
            'phone': '0905555555'
        })

        # Soft delete
        success = self.repo.soft_delete(customer_id, deleted_by=1)
        self.assertTrue(success)

        # Should not be found in normal query
        customer = self.repo.get_by_id(customer_id)
        self.assertIsNone(customer)

        # Should exist with include_deleted
        customer = self.repo.get_by_id(customer_id, include_deleted=True)
        self.assertIsNotNone(customer)
        self.assertTrue(customer.is_deleted)

    def test_restore(self):
        """Test restore soft-deleted customer."""
        customer_id = self.repo.create({
            'full_name': 'To Restore',
            'phone': '0904444444'
        })

        self.repo.soft_delete(customer_id, deleted_by=1)
        success = self.repo.restore(customer_id)
        self.assertTrue(success)

        customer = self.repo.get_by_id(customer_id)
        self.assertIsNotNone(customer)
        self.assertFalse(customer.is_deleted)

    def test_count(self):
        """Test counting customers."""
        self.repo.create({'full_name': 'A', 'phone': '0901111111', 'customer_class': 'vip'})
        self.repo.create({'full_name': 'B', 'phone': '0902222222', 'customer_class': 'regular'})
        self.repo.create({'full_name': 'C', 'phone': '0903333333', 'customer_type': 'business'})

        self.assertEqual(self.repo.count(), 3)
        self.assertEqual(self.repo.count(customer_class='vip'), 1)
        self.assertEqual(self.repo.count(customer_type='business'), 1)

    def test_search(self):
        """Test searching customers."""
        self.repo.create({'full_name': 'Nguyễn Văn A', 'phone': '0901111111'})
        self.repo.create({'full_name': 'Trần Thị B', 'phone': '0902222222', 'email': 'tran@test.com'})
        self.repo.create({'full_name': 'Lê Văn C', 'phone': '0903333333'})

        results = self.repo.search('Nguyễn')
        self.assertEqual(len(results), 1)

        results = self.repo.search('Văn')
        self.assertEqual(len(results), 2)

        results = self.repo.search('0902222222')
        self.assertEqual(len(results), 1)

        results = self.repo.search('tran@test.com')
        self.assertEqual(len(results), 1)

    def test_get_vip_customers(self):
        """Test getting VIP customers."""
        self.repo.create({'full_name': 'VIP1', 'phone': '0901111111', 'customer_class': 'vip'})
        self.repo.create({'full_name': 'Regular', 'phone': '0902222222', 'customer_class': 'regular'})
        self.repo.create({'full_name': 'VIP2', 'phone': '0903333333', 'customer_class': 'vip'})

        vip_customers = self.repo.get_vip_customers()
        self.assertEqual(len(vip_customers), 2)

    def test_customer_properties(self):
        """Test customer model properties."""
        individual = Customer(
            full_name='Individual Test',
            customer_type='individual',
            customer_class='vip'
        )
        self.assertFalse(individual.is_business)
        self.assertEqual(individual.display_name, 'Individual Test')
        self.assertTrue(individual.is_vip)

        business = Customer(
            full_name='Contact Person',
            customer_type='business',
            company_name='Test Company'
        )
        self.assertTrue(business.is_business)
        self.assertEqual(business.display_name, 'Test Company (Contact Person)')

    def test_customer_contact_info(self):
        """Test customer contact info methods."""
        customer = Customer(
            full_name='Test',
            phone='0901111111',
            email='test@example.com'
        )
        contact = customer.get_contact_info()
        self.assertIn('0901111111', contact)
        self.assertIn('test@example.com', contact)

    def test_customer_address_display(self):
        """Test customer address display."""
        customer = Customer(
            full_name='Test',
            address='123 Lê Lợi',
            ward='Phường Bến Nghé',
            district='Quận 1',
            province='Hồ Chí Minh'
        )
        address = customer.get_address_display()
        self.assertIn('123 Lê Lợi', address)
        self.assertIn('Hồ Chí Minh', address)

    def test_customer_class_display(self):
        """Test customer class display."""
        vip = Customer(full_name='VIP', customer_class='vip')
        regular = Customer(full_name='Regular', customer_class='regular')
        potential = Customer(full_name='Potential', customer_class='potential')

        self.assertIn('VIP', vip.get_class_display())
        self.assertIn('Regular', regular.get_class_display())
        self.assertIn('Potential', potential.get_class_display())


if __name__ == '__main__':
    unittest.main()
