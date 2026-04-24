"""
Authentication Service - Business logic for login/logout and session management.
Sprint 0.2: Authentication
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from ..repositories.user_repository import UserRepository
from ..repositories.auth_repository import AuthRepository
from ..models.user import User


class AuthError(Exception):
    """Base authentication error."""
    pass


class InvalidCredentialsError(AuthError):
    """Invalid username or password."""
    pass


class AccountLockedError(AuthError):
    """Account is temporarily locked."""
    pass


class AccountInactiveError(AuthError):
    """Account is not active."""
    pass


class SessionExpiredError(AuthError):
    """Session has expired."""
    pass


class InvalidSessionError(AuthError):
    """Session token is invalid."""
    pass


class AuthService:
    """Service for authentication and session management."""

    def __init__(self, user_repository: UserRepository,
                 auth_repository: AuthRepository):
        """Initialize auth service.

        Args:
            user_repository: User repository instance
            auth_repository: Auth repository instance
        """
        self.user_repo = user_repository
        self.auth_repo = auth_repository

        # Configuration
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.session_timeout_minutes = 30

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            bool: True if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False

    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked.

        Args:
            username: Username to check

        Returns:
            bool: True if locked
        """
        return self.auth_repo.is_account_locked(
            username,
            self.max_login_attempts,
            self.lockout_duration_minutes
        )

    def _get_client_info(self) -> Dict[str, str]:
        """Get client information.

        Returns:
            Dictionary with client info
        """
        # In real implementation, get from request
        # For now, return empty/defaults
        return {
            'ip_address': None,
            'user_agent': None,
            'device_info': None
        }

    def login(self, username: str, password: str,
              ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user and create session.

        Args:
            username: Username
            password: Password
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Dictionary with session_token and user data

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AccountLockedError: If account is locked
            AccountInactiveError: If account is not active
        """
        # Check if account is locked
        if self._is_account_locked(username):
            self.auth_repo.record_login_attempt(
                username, False, 'account_locked',
                ip_address, user_agent
            )
            raise AccountLockedError(
                f"Tài khoản tạm thời bị khóa. "
                f"Vui lòng thử lại sau {self.lockout_duration_minutes} phút"
            )

        # Find user
        user = self.user_repo.get_by_username(username)

        if not user or user.is_deleted:
            # Record failed attempt
            self.auth_repo.record_login_attempt(
                username, False, 'user_not_found',
                ip_address, user_agent
            )
            raise InvalidCredentialsError("Tên đăng nhập hoặc mật khẩu không đúng")

        # Check account status
        if user.status != 'active':
            self.auth_repo.record_login_attempt(
                username, False, 'account_inactive',
                ip_address, user_agent
            )
            raise AccountInactiveError("Tài khoản không hoạt động. Vui lòng liên hệ quản trị viên")

        # Verify password
        if not self._verify_password(password, user.password_hash):
            # Record failed attempt
            self.auth_repo.record_login_attempt(
                username, False, 'wrong_password',
                ip_address, user_agent
            )
            raise InvalidCredentialsError("Tên đăng nhập hoặc mật khẩu không đúng")

        # Successful login - create session
        expires_at = datetime.now() + timedelta(minutes=self.session_timeout_minutes)

        session_token = self.auth_repo.create_session(
            user_id=user.id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=None
        )

        # Record successful attempt
        self.auth_repo.record_login_attempt(
            username, True, None,
            ip_address, user_agent
        )

        # Update user login info
        self.user_repo.update_login_info(user.id)

        return {
            'session_token': session_token,
            'user': user,
            'expires_at': expires_at
        }

    def logout(self, session_token: str) -> bool:
        """End session.

        Args:
            session_token: Session token

        Returns:
            bool: True if successful
        """
        return self.auth_repo.deactivate_session(session_token, 'logout')

    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate session and return user.

        Args:
            session_token: Session token

        Returns:
            User instance or None

        Raises:
            SessionExpiredError: If session has expired
            InvalidSessionError: If session is invalid
        """
        if not session_token:
            raise InvalidSessionError("Phiên đăng nhập không hợp lệ")

        session = self.auth_repo.get_session_by_token(session_token)

        if not session:
            raise InvalidSessionError("Phiên đăng nhập không hợp lệ")

        # Check if expired
        expires_at = session.get('expires_at')
        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() > expires_at:
                self.auth_repo.deactivate_session(session_token, 'expired')
                raise SessionExpiredError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại")

        # Update last activity
        self.auth_repo.update_session_activity(session_token)

        # Return user
        return User.from_dict({
            'id': session['user_id'],
            'username': session['username'],
            'full_name': session['full_name'],
            'role_id': session['role_id'],
            'role_name': session.get('role_code')
        })

    def change_password(self, user_id: int, old_password: str,
                        new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            bool: True if successful

        Raises:
            InvalidCredentialsError: If old password is wrong
            AuthError: If password change fails
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("Không tìm thấy người dùng")

        # Verify old password
        if not self._verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Mật khẩu hiện tại không đúng")

        # Hash new password
        new_hash = self._hash_password(new_password)

        # Update password
        if self.user_repo.update_password(user_id, new_hash):
            # Invalidate all sessions except current
            # (in real implementation, track current session)
            return True

        raise AuthError("Không thể đổi mật khẩu")

    def reset_password(self, user_id: int) -> str:
        """Reset user password to default.

        Args:
            user_id: User ID

        Returns:
            str: New password
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("Không tìm thấy người dùng")

        # Generate default password
        new_password = f"User@{user_id}123!"
        new_hash = self._hash_password(new_password)

        if self.user_repo.update_password(user_id, new_hash):
            return new_password

        raise AuthError("Không thể đặt lại mật khẩu")

    def get_session_info(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session information.

        Args:
            session_token: Session token

        Returns:
            Session information or None
        """
        session = self.auth_repo.get_session_by_token(session_token)
        if not session:
            return None

        return {
            'user_id': session['user_id'],
            'username': session['username'],
            'started_at': session['started_at'],
            'last_activity': session['last_activity'],
            'expires_at': session['expires_at'],
            'ip_address': session['ip_address'],
            'device_info': session['device_info']
        }

    def get_active_sessions(self, user_id: int) -> list:
        """Get active sessions for user.

        Args:
            user_id: User ID

        Returns:
            List of session information
        """
        return self.auth_repo.get_active_sessions_by_user(user_id)

    def logout_all_sessions(self, user_id: int) -> bool:
        """Logout all sessions for user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        return self.auth_repo.deactivate_all_user_sessions(user_id, 'forced')

    def clean_expired_sessions(self) -> int:
        """Clean expired sessions.

        Returns:
            int: Number of sessions cleaned
        """
        return self.auth_repo.clean_expired_sessions()

    def get_login_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get login statistics.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with statistics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.auth_repo.get_login_statistics(start_date, end_date)
