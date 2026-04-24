"""
Unit tests for Authentication Service and Repository.
Sprint 0.2: Authentication
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import time

from src.database.db_helper import DatabaseHelper
from src.repositories.user_repository import UserRepository
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import (
    AuthService, InvalidCredentialsError,
    AccountLockedError, AccountInactiveError,
    SessionExpiredError, InvalidSessionError
)
from src.services.user_service import UserService


class TestAuthRepository(unittest.TestCase):
    """Test cases for AuthRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.auth_repo = AuthRepository(self.db)
        self.user_repo = UserRepository(self.db)

        # Create a test user
        self.user_id = self.user_repo.create({
            "username": "testuser",
            "password_hash": "hashedpass",
            "full_name": "Test User"
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_session(self):
        """Test creating a session."""
        expires_at = datetime.now() + timedelta(hours=1)
        token = self.auth_repo.create_session(
            user_id=self.user_id,
            expires_at=expires_at,
            ip_address="127.0.0.1"
        )

        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)

    def test_get_session_by_token(self):
        """Test getting session by token."""
        # Create session
        expires_at = datetime.now() + timedelta(hours=1)
        token = self.auth_repo.create_session(
            user_id=self.user_id,
            expires_at=expires_at,
            ip_address="127.0.0.1"
        )

        # Get session
        session = self.auth_repo.get_session_by_token(token)
        self.assertIsNotNone(session)
        self.assertEqual(session['user_id'], self.user_id)
        self.assertEqual(session['username'], "testuser")

    def test_deactivate_session(self):
        """Test deactivating a session."""
        # Create session
        expires_at = datetime.now() + timedelta(hours=1)
        token = self.auth_repo.create_session(
            user_id=self.user_id,
            expires_at=expires_at
        )

        # Deactivate
        result = self.auth_repo.deactivate_session(token, 'logout')
        self.assertTrue(result)

        # Should not be found
        session = self.auth_repo.get_session_by_token(token)
        self.assertIsNone(session)

    def test_update_session_activity(self):
        """Test updating session activity."""
        # Create session
        expires_at = datetime.now() + timedelta(hours=1)
        token = self.auth_repo.create_session(
            user_id=self.user_id,
            expires_at=expires_at
        )

        # Get original activity time
        session = self.auth_repo.get_session_by_token(token)
        original_activity = session['last_activity']

        # Wait a bit and update
        time.sleep(0.1)
        result = self.auth_repo.update_session_activity(token)
        self.assertTrue(result)

        # Verify updated
        session = self.auth_repo.get_session_by_token(token)
        self.assertNotEqual(session['last_activity'], original_activity)

    def test_record_login_attempt(self):
        """Test recording login attempt."""
        record_id = self.auth_repo.record_login_attempt(
            username="testuser",
            success=False,
            failure_reason="wrong_password",
            ip_address="127.0.0.1"
        )
        self.assertGreater(record_id, 0)

    def test_get_failed_attempts_count(self):
        """Test getting failed attempts count."""
        # Record some failed attempts
        for i in range(3):
            self.auth_repo.record_login_attempt(
                username="testuser",
                success=False,
                failure_reason="wrong_password"
            )

        # Record a successful attempt
        self.auth_repo.record_login_attempt(
            username="testuser",
            success=True
        )

        # Should be 3 failed attempts
        count = self.auth_repo.get_failed_attempts_count("testuser", minutes=30)
        self.assertEqual(count, 3)

    def test_is_account_locked(self):
        """Test checking if account is locked."""
        # Record max failed attempts
        max_attempts = 5
        for i in range(max_attempts):
            self.auth_repo.record_login_attempt(
                username="lockeduser",
                success=False,
                failure_reason="wrong_password"
            )

        # Should be locked
        is_locked = self.auth_repo.is_account_locked(
            "lockeduser",
            max_attempts=max_attempts,
            lockout_minutes=30
        )
        self.assertTrue(is_locked)

    def test_get_active_sessions_by_user(self):
        """Test getting active sessions for user."""
        # Create multiple sessions
        for i in range(3):
            expires_at = datetime.now() + timedelta(hours=1)
            self.auth_repo.create_session(
                user_id=self.user_id,
                expires_at=expires_at
            )

        sessions = self.auth_repo.get_active_sessions_by_user(self.user_id)
        self.assertEqual(len(sessions), 3)


class TestAuthService(unittest.TestCase):
    """Test cases for AuthService."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.user_repo = UserRepository(self.db)
        self.auth_repo = AuthRepository(self.db)
        self.auth_service = AuthService(self.user_repo, self.auth_repo)

        # Create user service to create test users with hashed passwords
        from src.repositories.user_repository import RoleRepository
        role_repo = RoleRepository(self.db)
        self.user_service = UserService(self.user_repo, role_repo)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_login_success(self):
        """Test successful login."""
        # Create user with known password
        user = self.user_service.create_user({
            "username": "logintest",
            "full_name": "Login Test",
            "email": "login@test.com"
        }, password="TestPass123")

        # Login
        result = self.auth_service.login("logintest", "TestPass123")

        self.assertIn('session_token', result)
        self.assertIn('user', result)
        self.assertEqual(result['user'].username, "logintest")

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        # Create user
        self.user_service.create_user({
            "username": "wrongpass",
            "full_name": "Wrong Pass"
        }, password="CorrectPass123")

        # Try login with wrong password
        with self.assertRaises(InvalidCredentialsError):
            self.auth_service.login("wrongpass", "WrongPass123")

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        with self.assertRaises(InvalidCredentialsError):
            self.auth_service.login("nonexistent", "SomePass123")

    def test_login_inactive_account(self):
        """Test login with inactive account."""
        # Create user and deactivate
        user = self.user_service.create_user({
            "username": "inactive",
            "full_name": "Inactive User"
        }, password="TestPass123")

        self.user_repo.update(user.id, {"status": "inactive"})

        with self.assertRaises(AccountInactiveError):
            self.auth_service.login("inactive", "TestPass123")

    def test_logout(self):
        """Test logout."""
        # Create user and login
        self.user_service.create_user({
            "username": "logouttest",
            "full_name": "Logout Test"
        }, password="TestPass123")

        result = self.auth_service.login("logouttest", "TestPass123")
        token = result['session_token']

        # Logout
        success = self.auth_service.logout(token)
        self.assertTrue(success)

        # Session should be invalid
        with self.assertRaises(InvalidSessionError):
            self.auth_service.validate_session(token)

    def test_validate_session_success(self):
        """Test validating a valid session."""
        # Create user and login
        self.user_service.create_user({
            "username": "validatesession",
            "full_name": "Validate Session"
        }, password="TestPass123")

        result = self.auth_service.login("validatesession", "TestPass123")
        token = result['session_token']

        # Validate
        user = self.auth_service.validate_session(token)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "validatesession")

    def test_validate_session_expired(self):
        """Test validating an expired session."""
        # Create user and login with very short timeout
        self.user_service.create_user({
            "username": "expiredsession",
            "full_name": "Expired Session"
        }, password="TestPass123")

        # Temporarily set short timeout
        original_timeout = self.auth_service.session_timeout_minutes
        self.auth_service.session_timeout_minutes = 0

        result = self.auth_service.login("expiredsession", "TestPass123")
        token = result['session_token']

        # Restore timeout
        self.auth_service.session_timeout_minutes = original_timeout

        # Session should be expired
        with self.assertRaises(SessionExpiredError):
            self.auth_service.validate_session(token)

    def test_validate_session_invalid_token(self):
        """Test validating an invalid session token."""
        with self.assertRaises(InvalidSessionError):
            self.auth_service.validate_session("invalid-token-12345")

    def test_change_password_success(self):
        """Test changing password."""
        # Create user
        user = self.user_service.create_user({
            "username": "changepass",
            "full_name": "Change Pass"
        }, password="OldPass123")

        # Change password
        success = self.auth_service.change_password(
            user.id, "OldPass123", "NewPass123"
        )
        self.assertTrue(success)

        # Can login with new password
        result = self.auth_service.login("changepass", "NewPass123")
        self.assertIsNotNone(result)

    def test_change_password_wrong_old(self):
        """Test changing password with wrong old password."""
        # Create user
        user = self.user_service.create_user({
            "username": "wrongold",
            "full_name": "Wrong Old"
        }, password="CorrectOld123")

        # Try change with wrong old password
        with self.assertRaises(InvalidCredentialsError):
            self.auth_service.change_password(
                user.id, "WrongOld123", "NewPass123"
            )

    def test_reset_password(self):
        """Test resetting password."""
        # Create user
        user = self.user_service.create_user({
            "username": "resetpass",
            "full_name": "Reset Pass"
        }, password="Original123")

        # Reset password
        new_password = self.auth_service.reset_password(user.id)
        self.assertIsNotNone(new_password)

        # Can login with new password
        result = self.auth_service.login("resetpass", new_password)
        self.assertIsNotNone(result)

    def test_get_session_info(self):
        """Test getting session info."""
        # Create user and login
        self.user_service.create_user({
            "username": "sessioninfo",
            "full_name": "Session Info"
        }, password="TestPass123")

        result = self.auth_service.login("sessioninfo", "TestPass123")
        token = result['session_token']

        # Get info
        info = self.auth_service.get_session_info(token)
        self.assertIsNotNone(info)
        self.assertEqual(info['username'], "sessioninfo")

    def test_logout_all_sessions(self):
        """Test logging out all sessions."""
        # Create user and login multiple times
        self.user_service.create_user({
            "username": "logoutall",
            "full_name": "Logout All"
        }, password="TestPass123")

        # Create multiple sessions
        result1 = self.auth_service.login("logoutall", "TestPass123")
        result2 = self.auth_service.login("logoutall", "TestPass123")

        # Should have 2 active sessions
        sessions = self.auth_service.get_active_sessions(
            result1['user'].id
        )
        self.assertEqual(len(sessions), 2)

        # Logout all
        success = self.auth_service.logout_all_sessions(result1['user'].id)
        self.assertTrue(success)

        # Sessions should be invalid
        with self.assertRaises(InvalidSessionError):
            self.auth_service.validate_session(result1['session_token'])

    def test_password_hashing(self):
        """Test password hashing."""
        password = "TestPassword123"

        # Hash password
        hashed = self.auth_service._hash_password(password)

        # Verify it's different from original
        self.assertNotEqual(hashed, password)

        # Verify password matches
        self.assertTrue(self.auth_service._verify_password(password, hashed))

        # Verify wrong password doesn't match
        self.assertFalse(self.auth_service._verify_password("WrongPass", hashed))


class TestIntegrationAuth(unittest.TestCase):
    """Integration tests for authentication flow."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.user_repo = UserRepository(self.db)
        self.auth_repo = AuthRepository(self.db)
        self.auth_service = AuthService(self.user_repo, self.auth_repo)

        from src.repositories.user_repository import RoleRepository
        role_repo = RoleRepository(self.db)
        self.user_service = UserService(self.user_repo, role_repo)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_full_login_logout_flow(self):
        """Test complete login-logout flow."""
        # Create user
        user = self.user_service.create_user({
            "username": "fullflow",
            "full_name": "Full Flow"
        }, password="TestPass123")

        # Login
        result = self.auth_service.login("fullflow", "TestPass123")
        token = result['session_token']
        self.assertIsNotNone(token)

        # Validate session
        validated_user = self.auth_service.validate_session(token)
        self.assertEqual(validated_user.id, user.id)

        # Logout
        success = self.auth_service.logout(token)
        self.assertTrue(success)

        # Session should be invalid
        with self.assertRaises(InvalidSessionError):
            self.auth_service.validate_session(token)

    def test_account_lockout(self):
        """Test account lockout after failed attempts."""
        # Create user
        self.user_service.create_user({
            "username": "lockout",
            "full_name": "Lockout Test"
        }, password="CorrectPass123")

        max_attempts = self.auth_service.max_login_attempts

        # Make failed login attempts
        for i in range(max_attempts):
            with self.assertRaises(InvalidCredentialsError):
                self.auth_service.login("lockout", "WrongPass123")

        # Next attempt should trigger lockout
        with self.assertRaises(AccountLockedError):
            self.auth_service.login("lockout", "CorrectPass123")

    def test_session_activity_update(self):
        """Test session activity is updated on validation."""
        # Create user and login
        self.user_service.create_user({
            "username": "activity",
            "full_name": "Activity Test"
        }, password="TestPass123")

        result = self.auth_service.login("activity", "TestPass123")
        token = result['session_token']

        # Get original activity time
        info = self.auth_service.get_session_info(token)
        original_activity = info['last_activity']

        # Wait and validate
        time.sleep(0.1)
        self.auth_service.validate_session(token)

        # Activity should be updated
        info = self.auth_service.get_session_info(token)
        self.assertNotEqual(info['last_activity'], original_activity)


if __name__ == "__main__":
    unittest.main()
