# Sprint 0.1: Employee Management

> **Module**: 0. FOUNDATION — Employee & Auth  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 2 ngày  
> **Blocked by**: — (Không có)  
> **Git Commit**: `feat: employee management`  
> **Branch**: `feature/0-foundation-auth`

---

## Mục Tiêu

Xây dựng hệ thống quản lý nhân viên cơ bản, bao gồm tạo bảng users/employees, models, và giao diện list view nhân viên.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define requirements
- [ ] Identify dependencies (Blocked by sprint nào?)
- [ ] Plan database schema
- [ ] Assign cho developer

### 2. Database

- [ ] Tạo bảng `users` (nhân viên)
  - id, username, password_hash, full_name, email, phone
  - avatar_path, role_id, department, position
  - hire_date, base_salary, status
  - last_login, login_count
  - created_at, updated_at, is_deleted, deleted_at
- [ ] Tạo bảng `roles` (vai trò)
  - id, role_name, role_code, description, level
- [ ] Define relationships
- [ ] Add indexes/constraints
  - UNIQUE(username), UNIQUE(email)
  - INDEX on role_id, status
- [ ] Test schema integrity

### 3. Backend Logic

- [ ] **Models**
  - `User` dataclass
  - `Role` dataclass
- [ ] **Repository Layer**
  - `UserRepository` với các phương thức:
    - `create(user_data)`
    - `get_by_id(user_id)`
    - `get_by_username(username)`
    - `get_all()`
    - `update(user_id, user_data)`
    - `delete(user_id)` (soft delete)
  - `RoleRepository` với các phương thức CRUD
- [ ] **Service Layer**
  - `UserService` với business logic
  - Validation cho username, email, phone
  - Password hashing (bcrypt) setup
- [ ] **Controllers**
  - `UserController` kết nối UI và Service
- [ ] Handle errors appropriately

### 4. UI Design

- [ ] **Wireframes**
  - Employee List View
  - Add/Edit Employee Dialog
  - Employee Detail View
- [ ] **Implementation**
  - `EmployeeListWidget` (bảng danh sách)
  - `EmployeeDialog` (form thêm/sửa)
  - Search & Filter toolbar
  - Action buttons: Add, Edit, Delete, View
- [ ] **Interactions**
  - Double-click để xem chi tiết
  - Right-click context menu
  - Confirmation dialog khi xóa
- [ ] **Responsiveness**
  - Đảm bảo hiển thị tốt ≥ 768px

### 5. Testing

- [ ] **Unit Tests (≥ 80% coverage)**
  - Test `UserRepository` CRUD
  - Test `UserService` validation
  - Test edge cases (duplicate username, email)
- [ ] **Integration Tests**
  - Test flow: Create → Read → Update → Delete
  - Test soft delete (is_deleted flag)
- [ ] **UI Acceptance Tests**
  - Test trên Chrome, Firefox (nếu web)
  - Hoặc test trên Windows/Linux (desktop)
- [ ] **Edge Cases**
  - Username/email trùng
  - Phone number không hợp lệ
  - Xóa user đã có hoạt động

### 6. Definition of Done

- [ ] Unit test coverage ≥ 80%
- [ ] Tất cả integration test pass
- [ ] Code review ≥ 1 người approve
- [ ] Không còn bug Critical/Blocker
- [ ] Deploy lên staging thành công
- [ ] README / comment cập nhật

### 7. Git Commit

> **Lưu ý**: Tất cả commit của Sprint 0 phải được thực hiện trên branch `feature/0-foundation-auth`

```bash
# 1. Đảm bảo đang ở đúng branch
git branch
# Output: * feature/0-foundation-auth

# 2. Add và commit changes
git add .
git commit -m "feat: employee management

- Add users and roles tables
- Implement UserRepository and RoleRepository
- Create EmployeeListWidget and EmployeeDialog
- Add unit tests for CRUD operations

Closes sprint-0.1"

# 3. Push lên remote branch
git push origin feature/0-foundation-auth
```

**Checklist:**
- [ ] Đang ở branch `feature/0-foundation-auth`
- [ ] Commit message đúng convention: `feat: employee management`
- [ ] Commit có description chi tiết (có thể có nhiều dòng)
- [ ] Push lên remote branch `origin feature/0-foundation-auth`
- [ ] **KHÔNG push lên `main`** - Sprint 0 chưa cần merge ngay

---

## Chi Tiết Kỹ Thuật

### Database Schema

```sql
-- Bảng roles
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_code VARCHAR(30) UNIQUE NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    avatar_path VARCHAR(255),
    role_id INTEGER,
    department VARCHAR(50),
    position VARCHAR(50),
    hire_date DATE,
    base_salary DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'active',
    last_login DATETIME,
    login_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at DATETIME,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_status ON users(status);
```

### Data Model (Python)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Role:
    id: int
    role_name: str
    role_code: str
    description: Optional[str] = None
    level: int = 1
    created_at: datetime = None

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: str = "active"
    created_at: datetime = None
    updated_at: datetime = None
```

---

## Ghi Chú

- **Seed Data**: Tạo tài khoản admin mặc định
  - Username: `admin`
  - Password: `admin123` (hash bằng bcrypt)
  - Role: Administrator
- **Soft Delete**: Không xóa hard, chỉ đánh dấu `is_deleted = 1`
- **Validation**:
  - Username: 3-50 ký tự, alphanumeric + underscore
  - Email: Đúng định dạng email
  - Phone: 10-15 số

---

## Liên Kết

- [Yêu cầu chức năng](../docs/YEU_CAU_CHUC_NANG.md)
- [Task List](../docs/TASK_LIST.md)
- [Database Design](../docs/DATABASE_DESIGN.md)
