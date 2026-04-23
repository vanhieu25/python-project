"""
Unit tests for Authorization Service and Repository.
Sprint 0.3: Authorization
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime

from src.database.db_helper import DatabaseHelper
from src.repositories.user_repository import UserRepository, RoleRepository
from src.repositories.permission_repository import PermissionRepository, RolePermissionRepository
from src.services.authorization_service import (
    AuthorizationService,
    PermissionDeniedError,
    NotAuthenticatedError,
    require_permission,
    require_any_permission,
    require_all_permissions
)
from src.models.permission import Permission


class TestPermissionRepository(unittest.TestCase):
    """Test cases for PermissionRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.permission_repo = PermissionRepository(self.db)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_get_by_code(self):
        """Test getting permission by code."""
        perm = self.permission_repo.get_by_code('car.view')
        self.assertIsNotNone(perm)
        self.assertEqual(perm.permission_code, 'car.view')

    def test_get_by_module(self):
        """Test getting permissions by module."""
        perms = self.permission_repo.get_by_module('cars')
        self.assertGreater(len(perms), 0)
        for p in perms:
            self.assertEqual(p.module, 'cars')

    def test_get_by_role(self):
        """Test getting permissions for a role."""
        # Admin role (id=1) should have all permissions
        perms = self.permission_repo.get_by_role(1)
        self.assertGreater(len(perms), 0)

        # Check for car.view permission
        perm_codes = {p.permission_code for p in perms}
        self.assertIn('car.view', perm_codes)

    def test_get_permission_codes_by_role(self):
        """Test getting permission codes as a set."""
        codes = self.permission_repo.get_permission_codes_by_role(1)
        self.assertIsInstance(codes, set)
        self.assertIn('car.view', codes)
        self.assertIn('user.view', codes)

    def test_get_all(self):
        """Test getting all permissions."""
        perms = self.permission_repo.get_all()
        self.assertGreater(len(perms), 0)

    def test_get_modules(self):
        """Test getting unique modules."""
        modules = self.permission_repo.get_modules()
        self.assertIn('cars', modules)
        self.assertIn('users', modules)


class TestRolePermissionRepository(unittest.TestCase):
    """Test cases for RolePermissionRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.role_perm_repo = RolePermissionRepository(self.db)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_has_permission(self):
        """Test checking if role has permission."""
        # Admin should have car.view
        self.assertTrue(self.role_perm_repo.has_permission(1, 'car.view'))

        # Admin should have settings.manage
        self.assertTrue(self.role_perm_repo.has_permission(1, 'settings.manage'))

    def test_has_any_permission(self):
        """Test checking if role has any of the permissions."""
        # Admin should have any of these
        self.assertTrue(
            self.role_perm_repo.has_any_permission(1, ['car.view', 'car.create'])
        )

        # Check empty list
        self.assertFalse(self.role_perm_repo.has_any_permission(1, []))

    def test_has_all_permissions(self):
        """Test checking if role has all permissions."""
        # Admin should have all permissions
        self.assertTrue(
            self.role_perm_repo.has_all_permissions(
                1, ['car.view', 'car.create', 'car.edit', 'car.delete']
            )
        )

        # Empty list should return True
        self.assertTrue(self.role_perm_repo.has_all_permissions(1, []))

    def test_assign_and_revoke_permission(self):
        """Test assigning and revoking permissions."""
        # First revoke
        self.role_perm_repo.revoke_permission(3, 1)  # Sales, car.view

        # Then assign
        self.role_perm_repo.assign_permission(3, 1)

        # Check
        self.assertTrue(self.role_perm_repo.has_permission(3, 'car.view'))

        # Revoke again
        self.role_perm_repo.revoke_permission(3, 1)

    def test_set_role_permissions(self):
        """Test setting all permissions for a role."""
        # Set permissions for Sales (role_id=3)
        permission_ids = [1, 6, 10]  # car.view, customer.view, contract.view
        self.role_perm_repo.set_role_permissions(3, permission_ids)

        # Verify
        self.assertTrue(self.role_perm_repo.has_permission(3, 'car.view'))
        self.assertTrue(self.role_perm_repo.has_permission(3, 'customer.view'))
        self.assertTrue(self.role_perm_repo.has_permission(3, 'contract.view'))


class TestAuthorizationService(unittest.TestCase):
    """Test cases for AuthorizationService."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.user_repo = UserRepository(self.db)
        self.permission_repo = PermissionRepository(self.db)
        self.role_perm_repo = RolePermissionRepository(self.db)

        self.auth_service = AuthorizationService(
            self.permission_repo,
            self.role_perm_repo,
            self.user_repo
        )

        # Create a test user with admin role
        from src.services.user_service import UserService
        from src.repositories.user_repository import RoleRepository

        role_repo = RoleRepository(self.db)
        self.user_service = UserService(self.user_repo, role_repo)

        self.admin_user = self.user_service.create_user({
            "username": "admin_test",
            "full_name": "Admin Test",
            "email": "admin@test.com",
            "role_id": 1  # Admin role
        }, password="AdminPass123")

        # Create a test user with sales role
        self.sales_user = self.user_service.create_user({
            "username": "sales_test",
            "full_name": "Sales Test",
            "email": "sales@test.com",
            "role_id": 3  # Sales role
        }, password="SalesPass123")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_get_user_permissions(self):
        """Test getting user permissions."""
        perms = self.auth_service.get_user_permissions(self.admin_user.id)
        self.assertIsInstance(perms, set)
        self.assertIn('car.view', perms)
        self.assertIn('settings.manage', perms)

    def test_has_permission_admin(self):
        """Test admin has all permissions."""
        self.assertTrue(
            self.auth_service.has_permission(self.admin_user.id, 'car.view')
        )
        self.assertTrue(
            self.auth_service.has_permission(self.admin_user.id, 'settings.manage')
        )

    def test_has_permission_sales(self):
        """Test sales has limited permissions."""
        # Sales should have car.view
        self.assertTrue(
            self.auth_service.has_permission(self.sales_user.id, 'car.view')
        )

        # Sales should NOT have settings.manage
        self.assertFalse(
            self.auth_service.has_permission(self.sales_user.id, 'settings.manage')
        )

    def test_has_any_permission(self):
        """Test has_any_permission method."""
        # Sales should have at least car.view
        self.assertTrue(
            self.auth_service.has_any_permission(
                self.sales_user.id, ['car.view', 'settings.manage']
            )
        )

    def test_has_all_permissions(self):
        """Test has_all_permissions method."""
        # Admin should have all
        self.assertTrue(
            self.auth_service.has_all_permissions(
                self.admin_user.id, ['car.view', 'car.create', 'car.edit']
            )
        )

        # Sales should NOT have all
        self.assertFalse(
            self.auth_service.has_all_permissions(
                self.sales_user.id, ['car.view', 'car.create', 'car.delete']
            )
        )

    def test_can_view(self):
        """Test can_view permission check."""
        # Admin can view everything
        self.assertTrue(self.auth_service.can_view(self.admin_user.id, 999))

        # Sales can view their own
        self.assertTrue(
            self.auth_service.can_view(self.sales_user.id, self.sales_user.id)
        )

    def test_can_edit(self):
        """Test can_edit permission check."""
        # Admin can edit everything
        self.assertTrue(self.auth_service.can_edit(self.admin_user.id, 999))

    def test_can_delete(self):
        """Test can_delete permission check."""
        # Only admin can delete
        self.assertTrue(self.auth_service.can_delete(self.admin_user.id, 999))

    def test_clear_cache(self):
        """Test clearing permission cache."""
        # Load permissions (caches them)
        self.auth_service.get_user_permissions(self.admin_user.id)

        # Clear specific user cache
        self.auth_service.clear_cache(self.admin_user.id)

        # Clear all cache
        self.auth_service.clear_cache()

    def test_get_permission_matrix(self):
        """Test getting permission matrix."""
        matrix = self.auth_service.get_permission_matrix()
        self.assertIn('admin', matrix)
        self.assertIn('sales', matrix)
        self.assertIn('car.view', matrix['admin']['permissions'])

    def test_check_permission_raises(self):
        """Test check_permission raises exception."""
        # Should raise for missing permission
        with self.assertRaises(PermissionDeniedError):
            self.auth_service.check_permission(
                self.sales_user.id, 'settings.manage'
            )

        # Should not raise for existing permission
        self.auth_service.check_permission(self.sales_user.id, 'car.view')


class MockController:
    """Mock controller class for testing decorators."""

    def __init__(self, user_id, auth_service):
        self.current_user_id = user_id
        self.auth_service = auth_service

    @require_permission('car.view')
    def view_car(self, car_id):
        return f"Viewed car {car_id}"

    @require_permission('settings.manage')
    def manage_settings(self):
        return "Settings managed"

    @require_any_permission(['car.edit', 'car.delete'])
    def modify_car(self, car_id):
        return f"Modified car {car_id}"

    @require_all_permissions(['car.view', 'car.edit'])
    def view_and_edit(self, car_id):
        return f"Viewed and edited car {car_id}"


class TestPermissionDecorators(unittest.TestCase):
    """Test cases for permission decorators."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.user_repo = UserRepository(self.db)
        self.permission_repo = PermissionRepository(self.db)
        self.role_perm_repo = RolePermissionRepository(self.db)

        self.auth_service = AuthorizationService(
            self.permission_repo,
            self.role_perm_repo,
            self.user_repo
        )

        # Create users
        from src.services.user_service import UserService
        from src.repositories.user_repository import RoleRepository

        role_repo = RoleRepository(self.db)
        self.user_service = UserService(self.user_repo, role_repo)

        self.admin_user = self.user_service.create_user({
            "username": "admin_test",
            "full_name": "Admin Test",
            "email": "admin@test.com",
            "role_id": 1
        }, password="AdminPass123")

        self.sales_user = self.user_service.create_user({
            "username": "sales_test",
            "full_name": "Sales Test",
            "email": "sales@test.com",
            "role_id": 3
        }, password="SalesPass123")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_require_permission_success(self):
        """Test successful permission check."""
        controller = MockController(self.admin_user.id, self.auth_service)
        result = controller.view_car(123)
        self.assertEqual(result, "Viewed car 123")

    def test_require_permission_denied(self):
        """Test permission denied."""
        # Sales doesn't have settings.manage
        controller = MockController(self.sales_user.id, self.auth_service)
        with self.assertRaises(PermissionDeniedError):
            controller.manage_settings()

    def test_require_any_permission(self):
        """Test any permission decorator."""
        # Admin should have car.edit or car.delete
        controller = MockController(self.admin_user.id, self.auth_service)
        result = controller.modify_car(123)
        self.assertEqual(result, "Modified car 123")

    def test_require_all_permissions(self):
        """Test all permissions decorator."""
        # Admin has both car.view and car.edit
        controller = MockController(self.admin_user.id, self.auth_service)
        result = controller.view_and_edit(123)
        self.assertEqual(result, "Viewed and edited car 123")

    def test_not_authenticated(self):
        """Test not authenticated error."""
        controller = MockController(None, self.auth_service)
        with self.assertRaises(NotAuthenticatedError):
            controller.view_car(123)


class TestPermissionMatrix(unittest.TestCase):
    """Test permission matrix according to sprint requirements."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.permission_repo = PermissionRepository(self.db)
        self.role_perm_repo = RolePermissionRepository(self.db)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_admin_has_all_permissions(self):
        """Test Admin has all permissions."""
        codes = self.permission_repo.get_permission_codes_by_role(1)
        all_perms = self.permission_repo.get_all()

        for perm in all_perms:
            self.assertIn(
                perm.permission_code, codes,
                f"Admin should have {perm.permission_code}"
            )

    def test_manager_no_delete_permissions(self):
        """Test Manager has no delete permissions."""
        codes = self.permission_repo.get_permission_codes_by_role(2)

        for code in codes:
            self.assertNotIn(
                'delete', code,
                f"Manager should not have delete permission: {code}"
            )

    def test_sales_limited_permissions(self):
        """Test Sales has limited permissions."""
        codes = self.permission_repo.get_permission_codes_by_role(3)

        # Sales should have cars, customers, contracts
        self.assertIn('car.view', codes)
        self.assertIn('customer.view', codes)
        self.assertIn('contract.view', codes)

        # Sales should NOT have settings or backup
        for code in codes:
            self.assertNotIn('settings', code)
            self.assertNotIn('backup', code)

    def test_accountant_view_only(self):
        """Test Accountant has view and export only."""
        codes = self.permission_repo.get_permission_codes_by_role(4)

        # Accountant should only have view and export
        for code in codes:
            action = code.split('.')[-1]
            self.assertIn(
                action, ['view', 'export'],
                f"Accountant should only have view/export: {code}"
            )


if __name__ == "__main__":
    unittest.main()
