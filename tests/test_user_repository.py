"""
Unit tests for User Repository and User Service.
Sprint 0.1: Employee Management
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime

import bcrypt

from src.database.db_helper import DatabaseHelper
from src.repositories.user_repository import UserRepository, RoleRepository
from src.services.user_service import UserService, ValidationError, DuplicateUserError, UserNotFoundError
from src.models.user import User, Role


class TestDatabaseHelper(unittest.TestCase):
    """Test cases for DatabaseHelper."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

    def tearDown(self):
        """Clean up test database."""
        shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test database is initialized with schema."""
        self.assertTrue(self.db.table_exists("users"))
        self.assertTrue(self.db.table_exists("roles"))

    def test_execute_and_fetch(self):
        """Test execute and fetch operations."""
        # Insert test data
        user_id = self.db.execute(
            "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
            ("testuser", "hash123", "Test User")
        )
        self.assertGreater(user_id, 0)

        # Fetch
        result = self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "testuser")

    def test_fetch_all(self):
        """Test fetch all operation."""
        # Insert multiple records
        self.db.execute(
            "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
            ("user1", "hash1", "User 1")
        )
        self.db.execute(
            "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
            ("user2", "hash2", "User 2")
        )

        results = self.db.fetch_all("SELECT * FROM users WHERE is_deleted = 0")
        self.assertEqual(len(results), 2)


class TestRoleRepository(unittest.TestCase):
    """Test cases for RoleRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.role_repo = RoleRepository(self.db)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_role(self):
        """Test creating a new role."""
        role_data = {
            "role_name": "Test Role",
            "role_code": "test_role",
            "description": "Test role description",
            "level": 5
        }

        role_id = self.role_repo.create(role_data)
        self.assertGreater(role_id, 0)

        # Verify
        role = self.role_repo.get_by_id(role_id)
        self.assertIsNotNone(role)
        self.assertEqual(role.role_name, "Test Role")
        self.assertEqual(role.role_code, "test_role")

    def test_get_role_by_code(self):
        """Test getting role by code."""
        # Create role
        role_data = {
            "role_name": "Manager",
            "role_code": "manager",
            "level": 2
        }
        self.role_repo.create(role_data)

        # Get by code
        role = self.role_repo.get_by_code("manager")
        self.assertIsNotNone(role)
        self.assertEqual(role.role_name, "Manager")

    def test_get_all_roles(self):
        """Test getting all roles."""
        # Create multiple roles
        self.role_repo.create({
            "role_name": "Role 1",
            "role_code": "role1",
            "level": 1
        })
        self.role_repo.create({
            "role_name": "Role 2",
            "role_code": "role2",
            "level": 2
        })

        roles = self.role_repo.get_all()
        self.assertEqual(len(roles), 2)

    def test_update_role(self):
        """Test updating a role."""
        # Create role
        role_id = self.role_repo.create({
            "role_name": "Old Name",
            "role_code": "old_code",
            "level": 1
        })

        # Update
        result = self.role_repo.update(role_id, {
            "role_name": "New Name",
            "role_code": "new_code",
            "level": 2
        })
        self.assertTrue(result)

        # Verify
        role = self.role_repo.get_by_id(role_id)
        self.assertEqual(role.role_name, "New Name")

    def test_delete_role(self):
        """Test deleting a role."""
        # Create role
        role_id = self.role_repo.create({
            "role_name": "To Delete",
            "role_code": "delete_me",
            "level": 1
        })

        # Delete
        result = self.role_repo.delete(role_id)
        self.assertTrue(result)

        # Verify
        role = self.role_repo.get_by_id(role_id)
        self.assertIsNone(role)


class TestUserRepository(unittest.TestCase):
    """Test cases for UserRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.user_repo = UserRepository(self.db)

        # Get admin role id (created by schema)
        result = self.db.fetch_one("SELECT id FROM roles WHERE role_code = 'admin'")
        self.admin_role_id = result["id"] if result else None

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_user(self):
        """Test creating a new user."""
        user_data = {
            "username": "newuser",
            "password_hash": "hashedpass",
            "full_name": "New User",
            "email": "new@example.com",
            "phone": "1234567890",
            "role_id": self.admin_role_id,
            "department": "IT",
            "position": "Developer"
        }

        user_id = self.user_repo.create(user_data)
        self.assertGreater(user_id, 0)

        # Verify
        user = self.user_repo.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.full_name, "New User")

    def test_get_by_username(self):
        """Test getting user by username."""
        # Create user
        self.user_repo.create({
            "username": "testuser",
            "password_hash": "hash",
            "full_name": "Test User"
        })

        # Get by username
        user = self.user_repo.get_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "Test User")

    def test_get_by_email(self):
        """Test getting user by email."""
        # Create user
        self.user_repo.create({
            "username": "emailuser",
            "password_hash": "hash",
            "full_name": "Email User",
            "email": "test@example.com"
        })

        # Get by email
        user = self.user_repo.get_by_email("test@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "emailuser")

    def test_search_users(self):
        """Test searching users."""
        # Create users
        self.user_repo.create({
            "username": "john_doe",
            "password_hash": "hash",
            "full_name": "John Doe",
            "email": "john@example.com"
        })
        self.user_repo.create({
            "username": "jane_doe",
            "password_hash": "hash",
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        })

        # Search
        results = self.user_repo.search("doe")
        self.assertEqual(len(results), 2)

        results = self.user_repo.search("john")
        self.assertEqual(len(results), 1)

    def test_update_user(self):
        """Test updating user."""
        # Create user
        user_id = self.user_repo.create({
            "username": "update_me",
            "password_hash": "hash",
            "full_name": "Old Name"
        })

        # Update
        result = self.user_repo.update(user_id, {
            "full_name": "New Name",
            "email": "new@example.com"
        })
        self.assertTrue(result)

        # Verify
        user = self.user_repo.get_by_id(user_id)
        self.assertEqual(user.full_name, "New Name")
        self.assertEqual(user.email, "new@example.com")

    def test_soft_delete(self):
        """Test soft delete."""
        # Create user
        user_id = self.user_repo.create({
            "username": "delete_me",
            "password_hash": "hash",
            "full_name": "To Delete"
        })

        # Soft delete
        result = self.user_repo.soft_delete(user_id)
        self.assertTrue(result)

        # Should not appear in get_all
        user = self.user_repo.get_by_id(user_id)
        self.assertIsNone(user)

        # But should appear with include_deleted
        all_users = self.user_repo.get_all(include_deleted=True)
        deleted_users = [u for u in all_users if u.id == user_id]
        self.assertEqual(len(deleted_users), 1)

    def test_restore_user(self):
        """Test restoring soft-deleted user."""
        # Create and delete user
        user_id = self.user_repo.create({
            "username": "restore_me",
            "password_hash": "hash",
            "full_name": "To Restore"
        })
        self.user_repo.soft_delete(user_id)

        # Restore
        result = self.user_repo.restore(user_id)
        self.assertTrue(result)

        # Should appear again
        user = self.user_repo.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertFalse(user.is_deleted)

    def test_exists(self):
        """Test checking user existence."""
        # Create user
        self.user_repo.create({
            "username": "exists_user",
            "password_hash": "hash",
            "full_name": "Exists",
            "email": "exists@example.com"
        })

        self.assertTrue(self.user_repo.exists(username="exists_user"))
        self.assertTrue(self.user_repo.exists(email="exists@example.com"))
        self.assertFalse(self.user_repo.exists(username="nonexistent"))

    def test_count(self):
        """Test counting users."""
        # Create users with different statuses
        self.user_repo.create({
            "username": "active1",
            "password_hash": "hash",
            "full_name": "Active 1",
            "status": "active"
        })
        self.user_repo.create({
            "username": "inactive1",
            "password_hash": "hash",
            "full_name": "Inactive 1",
            "status": "inactive"
        })

        self.assertEqual(self.user_repo.count(), 2)
        self.assertEqual(self.user_repo.count(status="active"), 1)


class TestUserService(unittest.TestCase):
    """Test cases for UserService."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.user_repo = UserRepository(self.db)
        self.role_repo = RoleRepository(self.db)
        self.user_service = UserService(self.user_repo, self.role_repo)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_user_success(self):
        """Test successful user creation."""
        user_data = {
            "username": "testuser",
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890"
        }
        password = "TestPass123"

        user = self.user_service.create_user(user_data, password)

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.full_name, "Test User")

    def test_create_user_validation_error(self):
        """Test user creation with invalid data."""
        # Empty username
        with self.assertRaises(ValidationError):
            self.user_service.create_user({
                "username": "",
                "full_name": "Test"
            }, "password123")

        # Short username
        with self.assertRaises(ValidationError):
            self.user_service.create_user({
                "username": "ab",
                "full_name": "Test"
            }, "password123")

        # Invalid email
        with self.assertRaises(ValidationError):
            self.user_service.create_user({
                "username": "test",
                "full_name": "Test",
                "email": "invalid-email"
            }, "password123")

    def test_create_user_duplicate(self):
        """Test creating duplicate user."""
        # Create first user
        self.user_service.create_user({
            "username": "duplicate",
            "full_name": "First"
        }, "TestPass123")

        # Try to create second with same username
        with self.assertRaises(DuplicateUserError):
            self.user_service.create_user({
                "username": "duplicate",
                "full_name": "Second"
            }, "TestPass123")

    def test_password_validation(self):
        """Test password validation."""
        # Too short
        with self.assertRaises(ValidationError):
            self.user_service._validate_password("short")

        # No uppercase
        with self.assertRaises(ValidationError):
            self.user_service._validate_password("lowercase123")

        # No lowercase
        with self.assertRaises(ValidationError):
            self.user_service._validate_password("UPPERCASE123")

        # No digit
        with self.assertRaises(ValidationError):
            self.user_service._validate_password("NoDigitsHere")

        # Valid password
        self.user_service._validate_password("ValidPass123")

    def test_update_user_success(self):
        """Test successful user update."""
        # Create user
        user = self.user_service.create_user({
            "username": "update_test",
            "full_name": "Old Name"
        }, "TestPass123")

        # Update
        updated = self.user_service.update_user(user.id, {
            "full_name": "New Name",
            "email": "new@example.com"
        })

        self.assertEqual(updated.full_name, "New Name")
        self.assertEqual(updated.email, "new@example.com")

    def test_update_user_not_found(self):
        """Test updating non-existent user."""
        with self.assertRaises(UserNotFoundError):
            self.user_service.update_user(99999, {
                "full_name": "New Name"
            })

    def test_delete_user_success(self):
        """Test successful user deletion."""
        # Create user
        user = self.user_service.create_user({
            "username": "delete_test",
            "full_name": "To Delete"
        }, "TestPass123")

        # Delete
        result = self.user_service.delete_user(user.id)
        self.assertTrue(result)

        # Should not be found
        with self.assertRaises(UserNotFoundError):
            self.user_service.get_user(user.id)

    def test_restore_user(self):
        """Test restoring deleted user."""
        # Create and delete
        user = self.user_service.create_user({
            "username": "restore_test",
            "full_name": "To Restore"
        }, "TestPass123")
        self.user_service.delete_user(user.id)

        # Restore
        restored = self.user_service.restore_user(user.id)
        self.assertIsNotNone(restored)
        self.assertFalse(restored.is_deleted)

    def test_search_users(self):
        """Test searching users."""
        # Create users
        self.user_service.create_user({
            "username": "john_smith",
            "full_name": "John Smith",
            "email": "john@example.com"
        }, "TestPass123")

        self.user_service.create_user({
            "username": "jane_doe",
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        }, "TestPass123")

        # Search
        results = self.user_service.search_users("john")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "John Smith")

    def test_get_user_statistics(self):
        """Test getting user statistics."""
        # Create users
        self.user_service.create_user({
            "username": "stat1",
            "full_name": "Stat 1"
        }, "TestPass123")
        self.user_service.create_user({
            "username": "stat2",
            "full_name": "Stat 2"
        }, "TestPass123")

        stats = self.user_service.get_user_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["active"], 2)

    def test_reset_password(self):
        """Test password reset."""
        # Create user
        user = self.user_service.create_user({
            "username": "reset_test",
            "full_name": "Reset Test"
        }, "TestPass123")

        # Reset password
        new_password = self.user_service.reset_password(user.id)
        self.assertIsNotNone(new_password)


if __name__ == "__main__":
    unittest.main()
