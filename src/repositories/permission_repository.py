"""
Permission Repository for managing permissions and role-permissions.
Sprint 0.3: Authorization
"""

from typing import List, Optional, Set
from src.database.db_helper import DatabaseHelper
from src.models.permission import Permission, RolePermission


class PermissionRepository:
    """Repository for permission operations."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        query = "SELECT * FROM permissions WHERE id = ?"
        result = self.db.fetch_one(query, (permission_id,))
        return Permission.from_dict(result) if result else None

    def get_by_code(self, permission_code: str) -> Optional[Permission]:
        """Get permission by code."""
        query = "SELECT * FROM permissions WHERE permission_code = ?"
        result = self.db.fetch_one(query, (permission_code,))
        return Permission.from_dict(result) if result else None

    def get_all(self) -> List[Permission]:
        """Get all permissions."""
        query = "SELECT * FROM permissions ORDER BY module, action"
        results = self.db.fetch_all(query)
        return [Permission.from_dict(r) for r in results]

    def get_by_module(self, module: str) -> List[Permission]:
        """Get permissions by module."""
        query = "SELECT * FROM permissions WHERE module = ? ORDER BY action"
        results = self.db.fetch_all(query, (module,))
        return [Permission.from_dict(r) for r in results]

    def get_by_role(self, role_id: int) -> List[Permission]:
        """Get all permissions assigned to a role."""
        query = """
            SELECT p.* FROM permissions p
            INNER JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
            ORDER BY p.module, p.action
        """
        results = self.db.fetch_all(query, (role_id,))
        return [Permission.from_dict(r) for r in results]

    def get_permission_codes_by_role(self, role_id: int) -> Set[str]:
        """Get permission codes for a role."""
        query = """
            SELECT p.permission_code FROM permissions p
            INNER JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
        """
        results = self.db.fetch_all(query, (role_id,))
        return {r['permission_code'] for r in results}

    def create(self, permission: Permission) -> int:
        """Create a new permission."""
        query = """
            INSERT INTO permissions (permission_name, permission_code, module, action, description)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            permission.permission_name,
            permission.permission_code,
            permission.module,
            permission.action,
            permission.description
        ))

    def update(self, permission: Permission) -> bool:
        """Update a permission."""
        query = """
            UPDATE permissions
            SET permission_name = ?, module = ?, action = ?, description = ?
            WHERE id = ?
        """
        rows = self.db.execute(query, (
            permission.permission_name,
            permission.module,
            permission.action,
            permission.description,
            permission.id
        ))
        return rows > 0

    def delete(self, permission_id: int) -> bool:
        """Delete a permission (also removes from role_permissions)."""
        # Delete from role_permissions first (cascade handled by FK)
        query = "DELETE FROM permissions WHERE id = ?"
        rows = self.db.execute(query, (permission_id,))
        return rows > 0

    def get_modules(self) -> List[str]:
        """Get all unique modules."""
        query = "SELECT DISTINCT module FROM permissions WHERE module IS NOT NULL ORDER BY module"
        results = self.db.fetch_all(query)
        return [r['module'] for r in results]


class RolePermissionRepository:
    """Repository for role-permission assignment operations."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def assign_permission(self, role_id: int, permission_id: int) -> int:
        """Assign a permission to a role."""
        query = """
            INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
            VALUES (?, ?)
        """
        return self.db.execute(query, (role_id, permission_id))

    def revoke_permission(self, role_id: int, permission_id: int) -> bool:
        """Revoke a permission from a role."""
        query = """
            DELETE FROM role_permissions
            WHERE role_id = ? AND permission_id = ?
        """
        rows = self.db.execute(query, (role_id, permission_id))
        return rows > 0

    def revoke_all_permissions(self, role_id: int) -> bool:
        """Revoke all permissions from a role."""
        query = "DELETE FROM role_permissions WHERE role_id = ?"
        self.db.execute(query, (role_id,))
        return True

    def has_permission(self, role_id: int, permission_code: str) -> bool:
        """Check if role has a specific permission."""
        query = """
            SELECT 1 FROM role_permissions rp
            INNER JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role_id = ? AND p.permission_code = ?
            LIMIT 1
        """
        result = self.db.fetch_one(query, (role_id, permission_code))
        return result is not None

    def has_any_permission(self, role_id: int, permission_codes: List[str]) -> bool:
        """Check if role has any of the given permissions."""
        if not permission_codes:
            return False

        placeholders = ','.join('?' * len(permission_codes))
        query = f"""
            SELECT 1 FROM role_permissions rp
            INNER JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role_id = ? AND p.permission_code IN ({placeholders})
            LIMIT 1
        """
        result = self.db.fetch_one(query, (role_id, *permission_codes))
        return result is not None

    def has_all_permissions(self, role_id: int, permission_codes: List[str]) -> bool:
        """Check if role has all of the given permissions."""
        if not permission_codes:
            return True

        placeholders = ','.join('?' * len(permission_codes))
        query = f"""
            SELECT COUNT(DISTINCT p.permission_code) as count
            FROM role_permissions rp
            INNER JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role_id = ? AND p.permission_code IN ({placeholders})
        """
        result = self.db.fetch_one(query, (role_id, *permission_codes))
        return result['count'] == len(permission_codes)

    def get_role_permissions(self, role_id: int) -> List[RolePermission]:
        """Get all role-permission assignments for a role."""
        query = "SELECT * FROM role_permissions WHERE role_id = ?"
        results = self.db.fetch_all(query, (role_id,))
        return [RolePermission.from_dict(r) for r in results]

    def set_role_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """Set permissions for a role (replaces all existing)."""
        # Remove all existing
        self.revoke_all_permissions(role_id)

        # Add new permissions
        if permission_ids:
            query = """
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            """
            self.db.execute_many(query, [(role_id, pid) for pid in permission_ids])

        return True

    def get_roles_with_permission(self, permission_id: int) -> List[int]:
        """Get all role IDs that have a specific permission."""
        query = "SELECT role_id FROM role_permissions WHERE permission_id = ?"
        results = self.db.fetch_all(query, (permission_id,))
        return [r['role_id'] for r in results]
