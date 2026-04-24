"""
Data Models for Car Management System
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Role:
    """Role model for user permissions."""

    id: int
    role_name: str
    role_code: str
    description: Optional[str] = None
    level: int = 1
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Role':
        """Create Role instance from dictionary.

        Args:
            data: Dictionary containing role data

        Returns:
            Role instance
        """
        if not data:
            return None

        return cls(
            id=data.get('id'),
            role_name=data.get('role_name'),
            role_code=data.get('role_code'),
            description=data.get('description'),
            level=data.get('level', 1),
            created_at=cls._parse_datetime(data.get('created_at'))
        )

    def to_dict(self) -> dict:
        """Convert Role to dictionary.

        Returns:
            Dictionary representation of Role
        """
        return {
            'id': self.id,
            'role_name': self.role_name,
            'role_code': self.role_code,
            'description': self.description,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return None


@dataclass
class User:
    """User model for employee management."""

    id: int
    username: str
    password_hash: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_path: Optional[str] = None
    role_id: Optional[int] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    base_salary: Optional[float] = None
    status: str = 'active'
    last_login: Optional[datetime] = None
    login_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    # Non-database fields
    role_name: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> Optional['User']:
        """Create User instance from dictionary.

        Args:
            data: Dictionary containing user data

        Returns:
            User instance or None
        """
        if not data:
            return None

        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            avatar_path=data.get('avatar_path'),
            role_id=data.get('role_id'),
            department=data.get('department'),
            position=data.get('position'),
            hire_date=data.get('hire_date'),
            base_salary=data.get('base_salary'),
            status=data.get('status', 'active'),
            last_login=cls._parse_datetime(data.get('last_login')),
            login_count=data.get('login_count', 0),
            created_at=cls._parse_datetime(data.get('created_at')),
            updated_at=cls._parse_datetime(data.get('updated_at')),
            is_deleted=bool(data.get('is_deleted', 0)),
            deleted_at=cls._parse_datetime(data.get('deleted_at')),
            role_name=data.get('role_name')
        )

    def to_dict(self, include_password: bool = False) -> dict:
        """Convert User to dictionary.

        Args:
            include_password: Whether to include password_hash

        Returns:
            Dictionary representation of User
        """
        result = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'avatar_path': self.avatar_path,
            'role_id': self.role_id,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date,
            'base_salary': self.base_salary,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'role_name': self.role_name
        }

        if include_password:
            result['password_hash'] = self.password_hash

        return result

    def to_db_dict(self) -> dict:
        """Convert User to dictionary for database operations.

        Returns:
            Dictionary with database-compatible values
        """
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'avatar_path': self.avatar_path,
            'role_id': self.role_id,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date,
            'base_salary': self.base_salary,
            'status': self.status,
            'last_login': self.last_login,
            'login_count': self.login_count,
            'is_deleted': 1 if self.is_deleted else 0,
            'deleted_at': self.deleted_at
        }

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Handle ISO format
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                # Try common SQLite format
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        return None

    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == 'active' and not self.is_deleted

    def __str__(self) -> str:
        """String representation of User."""
        return f"User(id={self.id}, username={self.username}, full_name={self.full_name})"
