"""
Permission models for Role-Based Access Control (RBAC).
Sprint 0.3: Authorization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Permission:
    """Permission dataclass representing a system permission."""
    id: int
    permission_name: str
    permission_code: str
    module: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"{self.permission_name} ({self.permission_code})"

    def __hash__(self) -> int:
        return hash(self.permission_code)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Permission):
            return False
        return self.permission_code == other.permission_code

    @classmethod
    def from_dict(cls, data: dict) -> 'Permission':
        """Create Permission from dictionary."""
        if not data:
            raise ValueError("Cannot create Permission from empty data")

        return cls(
            id=data['id'],
            permission_name=data['permission_name'],
            permission_code=data['permission_code'],
            module=data.get('module'),
            action=data.get('action'),
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at'])
            if isinstance(data.get('created_at'), str)
            else data.get('created_at', datetime.now())
        )

    def to_dict(self) -> dict:
        """Convert Permission to dictionary."""
        return {
            'id': self.id,
            'permission_name': self.permission_name,
            'permission_code': self.permission_code,
            'module': self.module,
            'action': self.action,
            'description': self.description,
            'created_at': self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else self.created_at
        }


@dataclass
class RolePermission:
    """RolePermission dataclass linking roles to permissions."""
    id: int
    role_id: int
    permission_id: int
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict) -> 'RolePermission':
        """Create RolePermission from dictionary."""
        if not data:
            raise ValueError("Cannot create RolePermission from empty data")

        return cls(
            id=data['id'],
            role_id=data['role_id'],
            permission_id=data['permission_id'],
            created_at=datetime.fromisoformat(data['created_at'])
            if isinstance(data.get('created_at'), str)
            else data.get('created_at', datetime.now())
        )

    def to_dict(self) -> dict:
        """Convert RolePermission to dictionary."""
        return {
            'id': self.id,
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'created_at': self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else self.created_at
        }
