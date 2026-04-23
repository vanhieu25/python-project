"""
Authorization Service for Role-Based Access Control (RBAC).
Sprint 0.3: Authorization
"""

from functools import wraps
from typing import List, Optional, Set, Callable, Any
from src.repositories.permission_repository import PermissionRepository, RolePermissionRepository
from src.repositories.user_repository import UserRepository
from src.models.permission import Permission


class AuthorizationError(Exception):
    """Base exception for authorization errors."""
    pass


class PermissionDeniedError(AuthorizationError):
    """Raised when user doesn't have required permission."""
    pass


class NotAuthenticatedError(AuthorizationError):
    """Raised when user is not authenticated."""
    pass


class AuthorizationService:
    """Service for handling authorization and permission checking."""

    def __init__(
        self,
        permission_repo: PermissionRepository,
        role_permission_repo: RolePermissionRepository,
        user_repo: UserRepository
    ):
        self.permission_repo = permission_repo
        self.role_permission_repo = role_permission_repo
        self.user_repo = user_repo
        # Cache permissions per user session
        self._permission_cache: dict[int, Set[str]] = {}

    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permission codes for a user."""
        # Check cache first
        if user_id in self._permission_cache:
            return self._permission_cache[user_id]

        # Get user's role
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.role_id:
            return set()

        # Get permissions for the role
        permissions = self.permission_repo.get_permission_codes_by_role(user.role_id)
        self._permission_cache[user_id] = permissions
        return permissions

    def has_permission(self, user_id: int, permission_code: str) -> bool:
        """Check if user has a specific permission."""
        permissions = self.get_user_permissions(user_id)
        return permission_code in permissions

    def has_any_permission(self, user_id: int, permission_codes: List[str]) -> bool:
        """Check if user has any of the given permissions."""
        if not permission_codes:
            return True
        permissions = self.get_user_permissions(user_id)
        return any(code in permissions for code in permission_codes)

    def has_all_permissions(self, user_id: int, permission_codes: List[str]) -> bool:
        """Check if user has all of the given permissions."""
        if not permission_codes:
            return True
        permissions = self.get_user_permissions(user_id)
        return all(code in permissions for code in permission_codes)

    def can_view(self, user_id: int, resource_owner_id: Optional[int] = None) -> bool:
        """
        Check if user can view a resource.
        Admin/Manager can view all, others can only view their own.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Check if user has admin role (level 1)
        if user.role_id == 1:
            return True

        # Check if user has manager role (level 2)
        if user.role_id == 2:
            return True

        # Check for view permission
        if self.has_permission(user_id, 'user.view'):
            return True

        # Others can only view their own
        if resource_owner_id is not None:
            return user_id == resource_owner_id

        return False

    def can_edit(self, user_id: int, resource_owner_id: Optional[int] = None) -> bool:
        """
        Check if user can edit a resource.
        Admin/Manager can edit all, others can only edit their own.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Admin and Manager can edit all
        if user.role_id in [1, 2]:
            return True

        # Check for edit permission
        if self.has_permission(user_id, 'user.edit'):
            return True

        # Others can only edit their own
        if resource_owner_id is not None:
            return user_id == resource_owner_id

        return False

    def can_delete(self, user_id: int, resource_owner_id: Optional[int] = None) -> bool:
        """
        Check if user can delete a resource.
        Only Admin can delete others' resources.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Only Admin can delete
        if user.role_id == 1:
            return True

        # Check for delete permission
        if self.has_permission(user_id, 'user.delete'):
            return True

        return False

    def get_user_permission_objects(self, user_id: int) -> List[Permission]:
        """Get full permission objects for a user."""
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.role_id:
            return []

        return self.permission_repo.get_by_role(user.role_id)

    def clear_cache(self, user_id: int = None):
        """Clear permission cache for a user or all users."""
        if user_id:
            self._permission_cache.pop(user_id, None)
        else:
            self._permission_cache.clear()

    def get_permission_matrix(self) -> dict:
        """
        Get permission matrix showing what each role has access to.
        Returns a dict with role names as keys and permission sets as values.
        """
        from src.repositories.user_repository import RoleRepository

        role_repo = RoleRepository(self.user_repo.db)
        roles = role_repo.get_all()

        matrix = {}
        for role in roles:
            permissions = self.permission_repo.get_permission_codes_by_role(role.id)
            matrix[role.role_code] = {
                'name': role.role_name,
                'permissions': permissions
            }

        return matrix

    def check_permission(self, user_id: int, permission_code: str):
        """Check permission and raise exception if denied."""
        if not self.has_permission(user_id, permission_code):
            raise PermissionDeniedError(
                f"Permission denied: {permission_code}"
            )


# ============================================================================
# Permission Decorators
# ============================================================================

def require_permission(permission_code: str):
    """
    Decorator to require a specific permission.

    The decorated class must have:
    - current_user_id attribute
    - auth_service attribute (AuthorizationService instance)

    Usage:
        @require_permission('car.create')
        def create_car(self, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get current user from context
            user_id = getattr(self, 'current_user_id', None)
            if user_id is None:
                raise NotAuthenticatedError("User not authenticated")

            # Get auth service
            auth_service = getattr(self, 'auth_service', None)
            if auth_service is None:
                raise RuntimeError("Authorization service not available")

            # Check permission
            if not auth_service.has_permission(user_id, permission_code):
                raise PermissionDeniedError(
                    f"Permission denied: {permission_code}"
                )

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permission_codes: List[str]):
    """
    Decorator to require any of the given permissions.

    Usage:
        @require_any_permission(['car.edit', 'car.delete'])
        def modify_car(self, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_id = getattr(self, 'current_user_id', None)
            if user_id is None:
                raise NotAuthenticatedError("User not authenticated")

            auth_service = getattr(self, 'auth_service', None)
            if auth_service is None:
                raise RuntimeError("Authorization service not available")

            if not auth_service.has_any_permission(user_id, permission_codes):
                codes_str = ', '.join(permission_codes)
                raise PermissionDeniedError(
                    f"Permission denied. Required any of: {codes_str}"
                )

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """
    Decorator to require all of the given permissions.

    Usage:
        @require_all_permissions(['car.view', 'car.edit'])
        def view_and_edit_car(self, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_id = getattr(self, 'current_user_id', None)
            if user_id is None:
                raise NotAuthenticatedError("User not authenticated")

            auth_service = getattr(self, 'auth_service', None)
            if auth_service is None:
                raise RuntimeError("Authorization service not available")

            if not auth_service.has_all_permissions(user_id, permission_codes):
                codes_str = ', '.join(permission_codes)
                raise PermissionDeniedError(
                    f"Permission denied. Required all of: {codes_str}"
                )

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def check_permission_silent(auth_service: AuthorizationService, user_id: int,
                            permission_code: str) -> bool:
    """Silent permission check that returns boolean instead of raising."""
    try:
        return auth_service.has_permission(user_id, permission_code)
    except Exception:
        return False
