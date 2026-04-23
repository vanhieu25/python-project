"""
Database Repository Layer
Provides data access operations for models.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper
from ..models.user import User, Role


class RoleRepository:
    """Repository for Role data access."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def create(self, role_data: Dict[str, Any]) -> int:
        """Create a new role.

        Args:
            role_data: Dictionary containing role data

        Returns:
            int: ID of created role
        """
        query = """
            INSERT INTO roles (role_name, role_code, description, level)
            VALUES (?, ?, ?, ?)
        """
        params = (
            role_data['role_name'],
            role_data['role_code'],
            role_data.get('description'),
            role_data.get('level', 1)
        )
        return self.db.execute(query, params)

    def get_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role instance or None
        """
        query = "SELECT * FROM roles WHERE id = ?"
        row = self.db.fetch_one(query, (role_id,))
        return Role.from_dict(row) if row else None

    def get_by_code(self, role_code: str) -> Optional[Role]:
        """Get role by code.

        Args:
            role_code: Role code string

        Returns:
            Role instance or None
        """
        query = "SELECT * FROM roles WHERE role_code = ?"
        row = self.db.fetch_one(query, (role_code,))
        return Role.from_dict(row) if row else None

    def get_all(self) -> List[Role]:
        """Get all roles.

        Returns:
            List of Role instances
        """
        query = "SELECT * FROM roles ORDER BY level, role_name"
        rows = self.db.fetch_all(query)
        return [Role.from_dict(row) for row in rows if row]

    def update(self, role_id: int, role_data: Dict[str, Any]) -> bool:
        """Update role.

        Args:
            role_id: Role ID
            role_data: Dictionary containing updated data

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE roles SET
                role_name = ?,
                role_code = ?,
                description = ?,
                level = ?
            WHERE id = ?
        """
        params = (
            role_data['role_name'],
            role_data['role_code'],
            role_data.get('description'),
            role_data.get('level', 1),
            role_id
        )
        try:
            self.db.execute(query, params)
            return True
        except Exception:
            return False

    def delete(self, role_id: int) -> bool:
        """Delete role.

        Args:
            role_id: Role ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM roles WHERE id = ?"
        try:
            self.db.execute(query, (role_id,))
            return True
        except Exception:
            return False


class UserRepository:
    """Repository for User data access."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def create(self, user_data: Dict[str, Any]) -> int:
        """Create a new user.

        Args:
            user_data: Dictionary containing user data

        Returns:
            int: ID of created user
        """
        query = """
            INSERT INTO users (
                username, password_hash, full_name, email, phone,
                role_id, department, position, hire_date, base_salary,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_data['username'],
            user_data['password_hash'],
            user_data['full_name'],
            user_data.get('email'),
            user_data.get('phone'),
            user_data.get('role_id'),
            user_data.get('department'),
            user_data.get('position'),
            user_data.get('hire_date'),
            user_data.get('base_salary'),
            user_data.get('status', 'active')
        )
        return self.db.execute(query, params)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        query = """
            SELECT u.*, r.role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = ? AND u.is_deleted = 0
        """
        row = self.db.fetch_one(query, (user_id,))
        return User.from_dict(row) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username string

        Returns:
            User instance or None
        """
        query = """
            SELECT u.*, r.role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.username = ? AND u.is_deleted = 0
        """
        row = self.db.fetch_one(query, (username,))
        return User.from_dict(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email string

        Returns:
            User instance or None
        """
        query = """
            SELECT u.*, r.role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.email = ? AND u.is_deleted = 0
        """
        row = self.db.fetch_one(query, (email,))
        return User.from_dict(row) if row else None

    def get_all(self, include_deleted: bool = False) -> List[User]:
        """Get all users.

        Args:
            include_deleted: Whether to include soft-deleted users

        Returns:
            List of User instances
        """
        if include_deleted:
            query = """
                SELECT u.*, r.role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                ORDER BY u.created_at DESC
            """
            rows = self.db.fetch_all(query)
        else:
            query = """
                SELECT u.*, r.role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.is_deleted = 0
                ORDER BY u.created_at DESC
            """
            rows = self.db.fetch_all(query)

        return [User.from_dict(row) for row in rows if row]

    def search(self, keyword: str, role_id: Optional[int] = None,
               status: Optional[str] = None) -> List[User]:
        """Search users with filters.

        Args:
            keyword: Search keyword for username/full_name/email
            role_id: Filter by role ID
            status: Filter by status

        Returns:
            List of User instances
        """
        query = """
            SELECT u.*, r.role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.is_deleted = 0
            AND (u.username LIKE ? OR u.full_name LIKE ? OR u.email LIKE ?)
        """
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]

        if role_id:
            query += " AND u.role_id = ?"
            params.append(role_id)

        if status:
            query += " AND u.status = ?"
            params.append(status)

        query += " ORDER BY u.created_at DESC"

        rows = self.db.fetch_all(query, tuple(params))
        return [User.from_dict(row) for row in rows if row]

    def update(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Update user.

        Args:
            user_id: User ID
            user_data: Dictionary containing updated data

        Returns:
            bool: True if successful
        """
        # Build dynamic query based on provided fields
        allowed_fields = [
            'username', 'full_name', 'email', 'phone', 'role_id',
            'department', 'position', 'hire_date', 'base_salary', 'status'
        ]

        fields = []
        params = []

        for field in allowed_fields:
            if field in user_data:
                fields.append(f"{field} = ?")
                params.append(user_data[field])

        if not fields:
            return False

        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        params.append(user_id)

        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password.

        Args:
            user_id: User ID
            password_hash: New hashed password

        Returns:
            bool: True if successful
        """
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        try:
            self.db.execute(query, (password_hash, user_id))
            return True
        except Exception:
            return False

    def soft_delete(self, user_id: int) -> bool:
        """Soft delete user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users SET
                is_deleted = 1,
                deleted_at = ?,
                status = 'inactive'
            WHERE id = ?
        """
        try:
            self.db.execute(query, (datetime.now(), user_id))
            return True
        except Exception:
            return False

    def restore(self, user_id: int) -> bool:
        """Restore soft-deleted user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users SET
                is_deleted = 0,
                deleted_at = NULL,
                status = 'active'
            WHERE id = ?
        """
        try:
            self.db.execute(query, (user_id,))
            return True
        except Exception:
            return False

    def delete_permanently(self, user_id: int) -> bool:
        """Permanently delete user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM users WHERE id = ?"
        try:
            self.db.execute(query, (user_id,))
            return True
        except Exception:
            return False

    def exists(self, username: Optional[str] = None,
               email: Optional[str] = None,
               exclude_id: Optional[int] = None) -> bool:
        """Check if user exists by username or email.

        Args:
            username: Username to check
            email: Email to check
            exclude_id: User ID to exclude from check

        Returns:
            bool: True if exists
        """
        conditions = []
        params = []

        if username:
            conditions.append("username = ?")
            params.append(username)

        if email:
            conditions.append("email = ?")
            params.append(email)

        if not conditions:
            return False

        query = f"SELECT 1 FROM users WHERE ({' OR '.join(conditions)}) AND is_deleted = 0"

        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)

        result = self.db.fetch_one(query, tuple(params))
        return result is not None

    def count(self, status: Optional[str] = None) -> int:
        """Count users.

        Args:
            status: Filter by status

        Returns:
            int: Number of users
        """
        query = "SELECT COUNT(*) as count FROM users WHERE is_deleted = 0"
        params = ()

        if status:
            query += " AND status = ?"
            params = (status,)

        result = self.db.fetch_one(query, params)
        return result['count'] if result else 0
