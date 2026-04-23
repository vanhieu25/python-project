# Sprint 0.3: Authorization

> **Module**: 0. FOUNDATION — Employee & Auth  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 2 ngày  
> **Blocked by**: Sprint-0.2 (Authentication)  
> **Git Commit**: `feat: authorization system`

---

## Mục Tiêu

Xây dựng hệ thống phân quyền (Authorization) dựa trên vai trò (Role-Based Access Control - RBAC), cho phép kiểm soát truy cập vào các chức năng của hệ thống.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define requirements
- [ ] Identify dependencies: Sprint-0.2
- [ ] Plan database schema (permissions, role_permissions)
- [ ] Assign cho developer

### 2. Database

- [ ] Tạo bảng `permissions` (danh sách quyền)
  - id, permission_name, permission_code
  - module, action, description
- [ ] Tạo bảng `role_permissions` (gán quyền cho vai trò)
  - id, role_id, permission_id
- [ ] Seed data cho permissions
  - car.view, car.create, car.edit, car.delete
  - customer.view, customer.create, etc.
  - contract.view, contract.create, etc.
- [ ] Seed data cho role_permissions
  - Admin: tất cả quyền
  - Manager: quyền quản lý
  - Sales: quyền bán hàng
  - Accountant: quyền kế toán
- [ ] Add indexes
  - INDEX on role_permissions.role_id
  - INDEX on role_permissions.permission_id
  - UNIQUE(role_id, permission_id)
- [ ] Test schema integrity

### 3. Backend Logic

- [ ] **Permission Model**
  - `Permission` dataclass
- [ ] **Role-Permission Repository**
  - `RolePermissionRepository`:
    - `get_permissions_by_role(role_id)`
    - `assign_permission(role_id, permission_id)`
    - `revoke_permission(role_id, permission_id)`
    - `has_permission(role_id, permission_code)`
- [ ] **Authorization Service**
  - `AuthorizationService`:
    - `check_permission(user_id, permission_code)`
    - `get_user_permissions(user_id)`
    - `can_view(user, resource)`
    - `can_edit(user, resource)`
    - `can_delete(user, resource)`
- [ ] **Permission Middleware/Decorator**
  - `@require_permission(permission_code)` decorator
  - `@require_any_permission([codes])` decorator
  - `@require_all_permissions([codes])` decorator
  - Kiểm tra quyền trước khi thực thi
- [ ] **Data Ownership**
  - Sales chỉ xem được khách hàng của mình
  - Admin/Manager xem được tất cả
- [ ] Handle errors appropriately

### 4. UI Design

- [ ] **Wireframes**
  - Role Management Screen
  - Permission Assignment UI
  - Access Denied Page
- [ ] **Implementation**
  - `RoleManagementScreen`
    - List các roles
    - Add/Edit role
    - Assign permissions (checkbox tree)
  - `PermissionAssignmentDialog`
    - Hiển thị tất cả permissions theo module
    - Cho phép check/uncheck
  - Hide/Disable buttons based on permissions
    - Nút "Delete" ẩn nếu không có `car.delete`
    - Nút "Edit" disabled nếu không có `car.edit`
- [ ] **Access Denied UI**
  - Thông báo khi không có quyền
  - Gợi ý liên hệ admin
- [ ] **Responsiveness**
  - Permission tree hiển thị tốt trên mọi kích thước

### 5. Testing

- [ ] **Unit Tests (≥ 80% coverage)**
  - Test `has_permission` logic
  - Test permission assignment
  - Test permission revocation
- [ ] **Integration Tests**
  - Test decorator blocking unauthorized access
  - Test decorator allowing authorized access
  - Test data ownership (sales chỉ xem của mình)
- [ ] **Permission Matrix Test**
  - Admin có tất cả quyền
  - Sales không có quyền xóa xe đã bán
  - Accountant không có quyền tạo hợp đồng
- [ ] **Edge Cases**
  - User không có role
  - Role không có permission nào
  - Permission code không tồn tại
  - Thay đổi permission giữa phiên làm việc

### 6. Definition of Done

- [ ] Unit test coverage ≥ 80%
- [ ] Tất cả integration test pass
- [ ] Code review ≥ 1 người approve
- [ ] Không còn bug Critical/Blocker
- [ ] Deploy lên staging thành công
- [ ] README / comment cập nhật

### 7. Git Commit

- [ ] Commit message đúng convention: `feat: authorization system`
- [ ] Push lên remote branch
- [ ] Tạo Pull Request nếu làm theo nhánh

---

## Chi Tiết Kỹ Thuật

### Database Schema

```sql
-- Bảng permissions
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    permission_name VARCHAR(100) NOT NULL,
    permission_code VARCHAR(50) UNIQUE NOT NULL,
    module VARCHAR(50), -- cars, customers, contracts, etc.
    action VARCHAR(20), -- view, create, edit, delete, approve
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng role_permissions
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);

-- Indexes
CREATE INDEX idx_role_perm_role ON role_permissions(role_id);
CREATE INDEX idx_role_perm_permission ON role_permissions(permission_id);
```

### Seed Data - Permissions

```sql
-- Cars Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem danh sách xe', 'car.view', 'cars', 'view'),
('Thêm xe mới', 'car.create', 'cars', 'create'),
('Chỉnh sửa xe', 'car.edit', 'cars', 'edit'),
('Xóa xe', 'car.delete', 'cars', 'delete'),
('Xuất báo cáo xe', 'car.export', 'cars', 'export');

-- Customers Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem danh sách khách hàng', 'customer.view', 'customers', 'view'),
('Thêm khách hàng', 'customer.create', 'customers', 'create'),
('Chỉnh sửa khách hàng', 'customer.edit', 'customers', 'edit'),
('Xóa khách hàng', 'customer.delete', 'customers', 'delete');

-- Contracts Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem hợp đồng', 'contract.view', 'contracts', 'view'),
('Tạo hợp đồng', 'contract.create', 'contracts', 'create'),
('Chỉnh sửa hợp đồng', 'contract.edit', 'contracts', 'edit'),
('Xóa hợp đồng', 'contract.delete', 'contracts', 'delete'),
('Duyệt hợp đồng', 'contract.approve', 'contracts', 'approve'),
('In hợp đồng', 'contract.print', 'contracts', 'print');

-- Inventory Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem tồn kho', 'inventory.view', 'inventory', 'view'),
('Nhập kho', 'inventory.import', 'inventory', 'create'),
('Xuất kho', 'inventory.export', 'inventory', 'delete');

-- Reports Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem báo cáo', 'report.view', 'reports', 'view'),
('Tạo báo cáo', 'report.create', 'reports', 'create'),
('Xuất báo cáo', 'report.export', 'reports', 'export');

-- Users Module
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Xem nhân viên', 'user.view', 'users', 'view'),
('Thêm nhân viên', 'user.create', 'users', 'create'),
('Chỉnh sửa nhân viên', 'user.edit', 'users', 'edit'),
('Xóa nhân viên', 'user.delete', 'users', 'delete'),
('Phân quyền', 'user.assign_role', 'users', 'assign');

-- Settings Module (Admin only)
INSERT INTO permissions (permission_name, permission_code, module, action) VALUES
('Quản lý cài đặt', 'settings.manage', 'settings', 'manage'),
('Sao lưu dữ liệu', 'backup.manage', 'backup', 'manage');
```

### Seed Data - Role Permissions

```sql
-- Admin: Tất cả quyền
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions; -- role_id 1 = admin

-- Manager: Quản lý (không có xóa)
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions 
WHERE action IN ('view', 'create', 'edit', 'approve', 'export', 'print');

-- Sales: Bán hàng (không có xóa, không có settings)
INSERT INTO role_permissions (role_id, permission_id)
SELECT 3, id FROM permissions 
WHERE module IN ('cars', 'customers', 'contracts') 
  AND action IN ('view', 'create', 'edit', 'print');

-- Accountant: Kế toán (chỉ xem và báo cáo)
INSERT INTO role_permissions (role_id, permission_id)
SELECT 4, id FROM permissions 
WHERE module IN ('contracts', 'reports', 'inventory')
  AND action IN ('view', 'export');
```

### Authorization Service (Python)

```python
from functools import wraps
from typing import List, Optional, Set
from dataclasses import dataclass

@dataclass
class Permission:
    id: int
    permission_name: str
    permission_code: str
    module: str
    action: str

class AuthorizationService:
    def __init__(self, role_permission_repo, user_repo):
        self.repo = role_permission_repo
        self.user_repo = user_repo
        # Cache permissions per user session
        self._permission_cache = {}
    
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permission codes for a user"""
        if user_id in self._permission_cache:
            return self._permission_cache[user_id]
        
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.get('role_id'):
            return set()
        
        permissions = self.repo.get_permissions_by_role(user['role_id'])
        permission_codes = {p['permission_code'] for p in permissions}
        
        self._permission_cache[user_id] = permission_codes
        return permission_codes
    
    def has_permission(self, user_id: int, permission_code: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return permission_code in permissions
    
    def has_any_permission(self, user_id: int, permission_codes: List[str]) -> bool:
        """Check if user has any of the permissions"""
        permissions = self.get_user_permissions(user_id)
        return any(code in permissions for code in permission_codes)
    
    def has_all_permissions(self, user_id: int, permission_codes: List[str]) -> bool:
        """Check if user has all permissions"""
        permissions = self.get_user_permissions(user_id)
        return all(code in permissions for code in permission_codes)
    
    def can_access_resource(self, user_id: int, resource_type: str, 
                           resource_owner_id: int = None) -> bool:
        """
        Check if user can access specific resource
        Admin/Manager can access all
        Others can only access their own
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # Admin can access everything
        if user.get('role_code') == 'admin':
            return True
        
        # Manager can access everything in their department
        if user.get('role_code') == 'manager':
            return True
        
        # Others can only access their own resources
        if resource_owner_id is not None:
            return user_id == resource_owner_id
        
        return False
    
    def clear_cache(self, user_id: int = None):
        """Clear permission cache"""
        if user_id:
            self._permission_cache.pop(user_id, None)
        else:
            self._permission_cache.clear()


# Decorators for permission checking
def require_permission(permission_code: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get current user from context (stored in controller/app)
            user_id = getattr(self, 'current_user_id', None)
            if not user_id:
                raise PermissionError("User not authenticated")
            
            auth_service = getattr(self, 'auth_service', None)
            if not auth_service:
                raise RuntimeError("Auth service not available")
            
            if not auth_service.has_permission(user_id, permission_code):
                raise PermissionError(
                    f"Permission denied: {permission_code}"
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permission_codes: List[str]):
    """Decorator to require any of the permissions"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_id = getattr(self, 'current_user_id', None)
            if not user_id:
                raise PermissionError("User not authenticated")
            
            auth_service = getattr(self, 'auth_service', None)
            if not auth_service.has_any_permission(user_id, permission_codes):
                raise PermissionError(
                    f"Permission denied. Required any of: {permission_codes}"
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
```

### Permission Matrix

| Role | car.view | car.create | car.edit | car.delete | customer.view | contract.create | settings.manage |
|------|----------|------------|----------|------------|---------------|-----------------|-----------------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Sales | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Accountant | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

---

## Ghi Chú

- **Permission Cache**: Cache permissions trong memory để giảm truy vấn database
- **Real-time Updates**: Clear cache khi thay đổi role/permission
- **UI Integration**: Sử dụng decorator để ẩn/hiện buttons dựa trên quyền
- **Audit**: Log tất cả các lần check permission thất bại

---

## Liên Kết

- [Sprint 0.2: Authentication](./sprint-0.2.md)
- [Sprint 0.4: Employee KPI](./sprint-0.4.md)
- [Yêu cầu chức năng](../docs/YEU_CAU_CHUC_NANG.md)
- [Task List](../docs/TASK_LIST.md)
- [Database Design](../docs/DATABASE_DESIGN.md)
