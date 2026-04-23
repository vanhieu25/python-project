"""
User Service - Business logic for user management.
"""

import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

import bcrypt

from ..repositories.user_repository import UserRepository, RoleRepository
from ..models.user import User, Role


logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Base exception for user service."""
    pass


class ValidationError(UserServiceError):
    """Validation error."""
    pass


class DuplicateUserError(UserServiceError):
    """Duplicate user error."""
    pass


class UserNotFoundError(UserServiceError):
    """User not found error."""
    pass


class UserService:
    """Service layer for user operations."""

    # Validation constants
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    PASSWORD_MIN_LENGTH = 8
    PHONE_PATTERN = re.compile(r'^[0-9]{10,15}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __init__(self, user_repository: UserRepository,
                 role_repository: RoleRepository):
        """Initialize user service.

        Args:
            user_repository: User repository instance
            role_repository: Role repository instance
        """
        self.user_repo = user_repository
        self.role_repo = role_repository
        self.logger = logging.getLogger(__name__)

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
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def _validate_username(self, username: str) -> None:
        """Validate username.

        Args:
            username: Username to validate

        Raises:
            ValidationError: If invalid
        """
        if not username:
            raise ValidationError("Username không được để trống")

        if len(username) < self.USERNAME_MIN_LENGTH:
            raise ValidationError(
                f"Username phải có ít nhất {self.USERNAME_MIN_LENGTH} ký tự"
            )

        if len(username) > self.USERNAME_MAX_LENGTH:
            raise ValidationError(
                f"Username không được quá {self.USERNAME_MAX_LENGTH} ký tự"
            )

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError(
                "Username chỉ được chứa chữ cái, số và dấu gạch dưới"
            )

    def _validate_password(self, password: str) -> None:
        """Validate password.

        Args:
            password: Password to validate

        Raises:
            ValidationError: If invalid
        """
        if not password:
            raise ValidationError("Mật khẩu không được để trống")

        if len(password) < self.PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"Mật khẩu phải có ít nhất {self.PASSWORD_MIN_LENGTH} ký tự"
            )

        # Check for at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Mật khẩu phải chứa ít nhất một chữ hoa")

        if not re.search(r'[a-z]', password):
            raise ValidationError("Mật khẩu phải chứa ít nhất một chữ thường")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Mật khẩu phải chứa ít nhất một chữ số")

    def _validate_email(self, email: Optional[str]) -> None:
        """Validate email.

        Args:
            email: Email to validate

        Raises:
            ValidationError: If invalid
        """
        if email and not self.EMAIL_PATTERN.match(email):
            raise ValidationError("Email không hợp lệ")

    def _validate_phone(self, phone: Optional[str]) -> None:
        """Validate phone number.

        Args:
            phone: Phone number to validate

        Raises:
            ValidationError: If invalid
        """
        if phone and not self.PHONE_PATTERN.match(phone):
            raise ValidationError("Số điện thoại không hợp lệ (10-15 số)")

    def create_user(self, user_data: Dict[str, Any],
                    password: Optional[str] = None) -> User:
        """Create new user.

        Args:
            user_data: Dictionary containing user data
            password: Plain text password (if None, will be auto-generated)

        Returns:
            User: Created user instance

        Raises:
            ValidationError: If data is invalid
            DuplicateUserError: If username/email already exists
        """
        # Validate required fields
        if not user_data.get('full_name'):
            raise ValidationError("Họ tên không được để trống")

        # Validate username
        username = user_data.get('username')
        self._validate_username(username)

        # Check for existing username
        if self.user_repo.exists(username=username):
            raise DuplicateUserError(f"Username '{username}' đã tồn tại")

        # Validate email
        email = user_data.get('email')
        if email:
            self._validate_email(email)
            if self.user_repo.exists(email=email):
                raise DuplicateUserError(f"Email '{email}' đã được sử dụng")

        # Validate phone
        self._validate_phone(user_data.get('phone'))

        # Hash password
        if password:
            self._validate_password(password)
            user_data['password_hash'] = self._hash_password(password)
        else:
            # Generate default password and hash it
            default_password = "User@1234"
            user_data['password_hash'] = self._hash_password(default_password)

        try:
            user_id = self.user_repo.create(user_data)
            user = self.user_repo.get_by_id(user_id)

            if not user:
                raise UserServiceError("Không thể tạo người dùng")

            self.logger.info(f"User created: {user.username} (ID: {user.id})")
            return user

        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            raise UserServiceError(f"Lỗi khi tạo người dùng: {str(e)}")

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user.

        Args:
            user_id: User ID
            user_data: Dictionary containing updated data

        Returns:
            User: Updated user instance

        Raises:
            UserNotFoundError: If user not found
            ValidationError: If data is invalid
            DuplicateUserError: If username/email conflict
        """
        # Check user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")

        # Validate new username if provided
        new_username = user_data.get('username')
        if new_username and new_username != user.username:
            self._validate_username(new_username)
            if self.user_repo.exists(username=new_username, exclude_id=user_id):
                raise DuplicateUserError(f"Username '{new_username}' đã tồn tại")

        # Validate new email if provided
        new_email = user_data.get('email')
        if new_email and new_email != user.email:
            self._validate_email(new_email)
            if self.user_repo.exists(email=new_email, exclude_id=user_id):
                raise DuplicateUserError(f"Email '{new_email}' đã được sử dụng")

        # Validate phone if provided
        if 'phone' in user_data:
            self._validate_phone(user_data['phone'])

        try:
            success = self.user_repo.update(user_id, user_data)
            if not success:
                raise UserServiceError("Cập nhật thất bại")

            updated_user = self.user_repo.get_by_id(user_id)
            self.logger.info(f"User updated: {updated_user.username} (ID: {user_id})")
            return updated_user

        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            raise UserServiceError(f"Lỗi khi cập nhật người dùng: {str(e)}")

    def delete_user(self, user_id: int, permanent: bool = False) -> bool:
        """Delete user.

        Args:
            user_id: User ID
            permanent: Whether to permanently delete

        Returns:
            bool: True if successful

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")

        # Prevent deleting the last admin
        if user.role_id == 1:  # Admin role
            admin_count = self.user_repo.count(status='active')
            if admin_count <= 1:
                raise UserServiceError("Không thể xóa người dùng admin cuối cùng")

        try:
            if permanent:
                success = self.user_repo.delete_permanently(user_id)
            else:
                success = self.user_repo.soft_delete(user_id)

            if success:
                self.logger.info(f"User deleted: {user.username} (ID: {user_id})")
            return success

        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            raise UserServiceError(f"Lỗi khi xóa người dùng: {str(e)}")

    def restore_user(self, user_id: int) -> User:
        """Restore soft-deleted user.

        Args:
            user_id: User ID

        Returns:
            User: Restored user instance

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")

        if not user.is_deleted:
            raise UserServiceError("Người dùng chưa bị xóa")

        try:
            success = self.user_repo.restore(user_id)
            if not success:
                raise UserServiceError("Khôi phục thất bại")

            restored = self.user_repo.get_by_id(user_id)
            self.logger.info(f"User restored: {restored.username} (ID: {user_id})")
            return restored

        except Exception as e:
            self.logger.error(f"Error restoring user: {e}")
            raise UserServiceError(f"Lỗi khi khôi phục người dùng: {str(e)}")

    def get_user(self, user_id: int) -> User:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User: User instance

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")
        return user

    def get_user_by_username(self, username: str) -> User:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User: User instance

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng '{username}'")
        return user

    def get_all_users(self, include_deleted: bool = False) -> List[User]:
        """Get all users.

        Args:
            include_deleted: Whether to include soft-deleted users

        Returns:
            List[User]: List of user instances
        """
        return self.user_repo.get_all(include_deleted=include_deleted)

    def search_users(self, keyword: str, role_id: Optional[int] = None,
                     status: Optional[str] = None) -> List[User]:
        """Search users.

        Args:
            keyword: Search keyword
            role_id: Filter by role
            status: Filter by status

        Returns:
            List[User]: List of matching users
        """
        return self.user_repo.search(keyword, role_id=role_id, status=status)

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
            UserNotFoundError: If user not found
            ValidationError: If password invalid
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")

        # Verify old password
        if not self._verify_password(old_password, user.password_hash):
            raise ValidationError("Mật khẩu hiện tại không đúng")

        # Validate new password
        self._validate_password(new_password)

        # Update password
        new_hash = self._hash_password(new_password)
        return self.user_repo.update_password(user_id, new_hash)

    def reset_password(self, user_id: int) -> str:
        """Reset user password to default.

        Args:
            user_id: User ID

        Returns:
            str: New password

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")

        # Generate default password
        default_password = f"User@{user_id}123"
        new_hash = self._hash_password(default_password)

        if self.user_repo.update_password(user_id, new_hash):
            self.logger.info(f"Password reset for user: {user.username}")
            return default_password

        raise UserServiceError("Không thể đặt lại mật khẩu")

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics.

        Returns:
            Dictionary with statistics
        """
        total = self.user_repo.count()
        active = self.user_repo.count(status='active')
        inactive = self.user_repo.count(status='inactive')

        return {
            'total': total,
            'active': active,
            'inactive': inactive
        }

    # Role operations
    def get_all_roles(self) -> List[Role]:
        """Get all roles.

        Returns:
            List[Role]: List of role instances
        """
        return self.role_repo.get_all()

    def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role or None
        """
        return self.role_repo.get_by_id(role_id)
