"""
Unit tests for TemplateService.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import sqlite3
import tempfile

from database.db_helper import DatabaseHelper
from repositories.template_repository import TemplateRepository
from repositories.contract_repository import ContractRepository
from services.template_service import TemplateService, TemplateResult
from models.contract_template import ContractTemplate, TemplateVariable


class MockUser:
    """Mock user for testing."""
    def __init__(self, id, full_name):
        self.id = id
        self.full_name = full_name


class MockUserRepository:
    """Mock user repository."""
    def __init__(self):
        self.users = {
            1: MockUser(1, "Test User"),
            2: MockUser(2, "Manager")
        }

    def get_by_id(self, user_id):
        return self.users.get(user_id)


class TestTemplateService(unittest.TestCase):
    """Test cases for TemplateService."""

    def setUp(self):
        """Set up test database and service."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        self.db = DatabaseHelper(self.db_path)
        self._init_schema()

        self.template_repo = TemplateRepository(self.db)
        self.contract_repo = ContractRepository(self.db)
        self.user_repo = MockUserRepository()

        self.service = TemplateService(
            self.template_repo,
            self.contract_repo,
            self.user_repo
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

        # Insert test template (let SQLite assign ID)
        cursor.execute("""
            INSERT INTO contract_templates
            (template_code, template_name, template_content, is_default, is_active, created_by)
            VALUES ('TEST_TEMPLATE', 'Test Template',
                    '<h1>Contract {{contract_code}}</h1><p>Customer: {{customer_name}}</p>', 1, 1, 1)
        """)
        self.test_template_id = cursor.lastrowid

        # Insert test contract
        cursor.execute("""
            INSERT INTO contracts
            (contract_code, customer_id, customer_name, car_id, car_brand, car_model,
             car_price, total_amount, final_amount, created_by, status)
            VALUES ('HD001', 1, 'Nguyen Van A', 1, 'Toyota', 'Camry',
                    1000000000, 1000000000, 1100000000, 1, 'draft')
        """)
        self.test_contract_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def test_get_available_variables(self):
        """Test getting available variables."""
        variables = self.service.get_available_variables()

        self.assertIsInstance(variables, list)
        self.assertGreater(len(variables), 0)

        # Check customer variables exist
        var_names = [v.name for v in variables]
        self.assertIn('customer_name', var_names)
        self.assertIn('car_brand', var_names)
        self.assertIn('contract_code', var_names)

    def test_validate_template_valid(self):
        """Test validating valid template."""
        content = "<h1>Contract {{contract_code}}</h1><p>{{customer_name}}</p>"
        result = self.service.validate_template(content)

        self.assertTrue(result.success)
        self.assertEqual(len(result.data['errors']), 0)

    def test_validate_template_unbalanced_braces(self):
        """Test validating template with unbalanced braces."""
        content = "<h1>Contract {{contract_code}</h1>"
        result = self.service.validate_template(content)

        self.assertFalse(result.success)
        self.assertIn('cú pháp', result.message.lower())

    def test_validate_template_warnings(self):
        """Test validating template with warnings."""
        content = "<h1>Contract</h1>"  # Missing recommended variables
        result = self.service.validate_template(content)

        self.assertTrue(result.success)
        self.assertGreater(len(result.data['warnings']), 0)

    def test_render_contract_success(self):
        """Test rendering contract with template."""
        result = self.service.render_contract(self.test_contract_id)

        self.assertTrue(result.success)
        self.assertIn('html', result.data)
        self.assertIn('HD001', result.data['html'])
        self.assertIn('Nguyen Van A', result.data['html'])

    def test_render_contract_not_found(self):
        """Test rendering non-existent contract."""
        result = self.service.render_contract(99999)

        self.assertFalse(result.success)
        self.assertIn('không tồn tại', result.message.lower())

    def test_preview_template(self):
        """Test previewing template with sample data."""
        result = self.service.preview_template(self.test_template_id)

        self.assertTrue(result.success)
        self.assertIn('html', result.data)

    def test_preview_template_not_found(self):
        """Test previewing non-existent template."""
        result = self.service.preview_template(99999)

        self.assertFalse(result.success)
        self.assertIn('không tồn tại', result.message.lower())

    def test_create_template_success(self):
        """Test creating new template."""
        data = {
            'template_code': 'NEW_TEMPLATE',
            'template_name': 'New Test Template',
            'template_content': '<h1>{{contract_code}}</h1><p>{{customer_name}}</p>',
            'description': 'Test template',
            'is_default': False,
            'is_active': True
        }

        result = self.service.create_template(data, created_by=1)

        self.assertTrue(result.success)
        self.assertIn('template_id', result.data)

    def test_create_template_duplicate_code(self):
        """Test creating template with duplicate code."""
        data = {
            'template_code': 'TEST_TEMPLATE',  # Already exists
            'template_name': 'Duplicate',
            'template_content': '<h1>Test</h1>',
            'is_default': False
        }

        result = self.service.create_template(data, created_by=1)

        self.assertFalse(result.success)
        self.assertIn('đã tồn tại', result.message.lower())

    def test_create_template_invalid_content(self):
        """Test creating template with invalid content."""
        data = {
            'template_code': 'INVALID',
            'template_name': 'Invalid',
            'template_content': '<h1>Contract {{unclosed</h1>',
            'is_default': False
        }

        result = self.service.create_template(data, created_by=1)

        self.assertFalse(result.success)

    def test_clone_template_success(self):
        """Test cloning template."""
        result = self.service.clone_template(self.test_template_id, 'CLONED_TEMPLATE', created_by=1)

        self.assertTrue(result.success)
        self.assertIn('template_id', result.data)

        # Verify clone
        cloned = self.template_repo.get_by_id(result.data['template_id'])
        self.assertIsNotNone(cloned)
        self.assertEqual(cloned.template_code, 'CLONED_TEMPLATE')

    def test_clone_template_duplicate_code(self):
        """Test cloning with existing code."""
        result = self.service.clone_template(self.test_template_id, 'TEST_TEMPLATE', created_by=1)

        self.assertFalse(result.success)
        self.assertIn('đã tồn tại', result.message.lower())

    def test_update_template_success(self):
        """Test updating template."""
        result = self.service.update_template(self.test_template_id, {
            'template_name': 'Updated Name'
        })

        self.assertTrue(result.success)

        # Verify update
        template = self.template_repo.get_by_id(self.test_template_id)
        self.assertEqual(template.template_name, 'Updated Name')

    def test_delete_template_success(self):
        """Test deleting template."""
        # Create non-default template first
        data = {
            'template_code': 'DELETE_ME',
            'template_name': 'To Delete',
            'template_content': '<h1>Test</h1>',
            'is_default': False
        }
        create_result = self.service.create_template(data, created_by=1)
        template_id = create_result.data['template_id']

        result = self.service.delete_template(template_id)

        self.assertTrue(result.success)

        # Verify soft delete
        template = self.template_repo.get_by_id(template_id)
        self.assertFalse(template.is_active)

    def test_delete_default_template(self):
        """Test deleting default template should fail."""
        result = self.service.delete_template(self.test_template_id)  # This template is default

        self.assertFalse(result.success)
        self.assertIn('mặc định', result.message.lower())

    def test_list_templates(self):
        """Test listing templates."""
        templates = self.service.list_templates(active_only=True)

        self.assertIsInstance(templates, list)
        # Should have 2 templates: the default from schema + our test template
        self.assertGreaterEqual(len(templates), 1)

    def test_get_sample_data(self):
        """Test getting sample data for preview."""
        data = self.service._get_sample_data()

        self.assertIn('customer_name', data)
        self.assertIn('car_brand', data)
        self.assertIn('contract_code', data)
        self.assertIn('company_name', data)

    def test_get_contract_data(self):
        """Test extracting template data from contract."""
        contract = self.contract_repo.get_by_id(self.test_contract_id)
        data = self.service._get_contract_data(contract)

        self.assertEqual(data['customer_name'], 'Nguyen Van A')
        self.assertEqual(data['car_brand'], 'Toyota')
        self.assertEqual(data['contract_code'], 'HD001')


if __name__ == '__main__':
    unittest.main()
