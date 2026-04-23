# Hướng Dẫn Chạy Tests

Tài liệu này hướng dẫn cách chạy các file test và kiểm tra giao diện thực tế của Car Management System.

---

## 📋 Mục Lục

- [Cấu trúc Tests](#cấu-trúc-tests)
- [Chạy Tests Command Line](#chạy-tests-command-line)
- [Chạy Tests trong IDE](#chạy-tests-trong-ide)
- [Test Giao Diện Thực Tế](#test-giao-diện-thực-tế)
- [Xử Lý Lỗi](#xử-lý-lỗi)

---

## 🧪 Cấu Trúc Tests

```
tests/
├── test_user_repository.py       # Test Repository (Sprint 0.1)
├── test_auth_service.py          # Test Authentication (Sprint 0.2)
├── test_authorization_service.py # Test Authorization (Sprint 0.3)
└── test_kpi_service.py          # Test KPI (Sprint 0.4)
```

### Tổng Số Tests

| File | Số Tests | Sprint |
|------|----------|--------|
| test_user_repository.py | 13 | 0.1 |
| test_auth_service.py | 21 | 0.2 |
| test_authorization_service.py | 31 | 0.3 |
| test_kpi_service.py | 25 | 0.4 |
| **Tổng** | **90** | - |

---

## 💻 Chạy Tests Command Line

### Yêu Cầu

- Python 3.10+
- Đã cài đặt dependencies: `pip install -r requirements.txt`

### Chạy Tất Cả Tests

```bash
# Từ thư mục gốc của project
python -m unittest discover tests/ -v
```

### Chạy Từng File Test

```bash
# Sprint 0.1: Employee Management
python -m unittest tests.test_user_repository -v

# Sprint 0.2: Authentication
python -m unittest tests.test_auth_service -v

# Sprint 0.3: Authorization
python -m unittest tests.test_authorization_service -v

# Sprint 0.4: KPI
python -m unittest tests.test_kpi_service -v
```

### Chạy Test Cụ Thể

```bash
# Chạy một test class cụ thể
python -m unittest tests.test_auth_service.TestAuthService -v

# Chạy một test method cụ thể
python -m unittest tests.test_auth_service.TestAuthService.test_login_success -v
```

### Chạy Với Coverage (Nếu có pytest)

```bash
# Cài đặt pytest và coverage
pip install pytest pytest-cov

# Chạy với coverage
pytest tests/ -v --cov=src --cov-report=html

# Xem báo cáo coverage
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

---

## 🏗️ Chạy Tests Trong IDE

### VS Code

1. Cài đặt extension **Python**
2. Mở file test (vd: `tests/test_auth_service.py`)
3. Click vào `Run Test` hoặc `Debug Test` trên đầu class/function
4. Hoặc nhấn `Ctrl+Shift+P` → `Python: Run All Tests`

### PyCharm

1. Chuột phải vào thư mục `tests/`
2. Chọn **Run 'Unittests in tests'**
3. Hoặc chạy từng file test riêng lẻ

---

## 🎨 Test Giao Diện Thực Tế

### Cách 1: Chạy Ứng Dụng Chính

```bash
# Chạy ứng dụng chính
python src/main.py
```

**Tài khoản mặc định:**
- Username: `admin`
- Password: `admin123`

### Cách 2: Chạy Script Test Giao Diện

Tạo file `run_ui_tests.py`:

```python
"""
Script chạy test giao diện thực tế.
Test các dialog và screen chính.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from src.database.db_helper import DatabaseHelper
from src.repositories.user_repository import UserRepository, RoleRepository
from src.repositories.auth_repository import AuthRepository
from src.repositories.permission_repository import PermissionRepository, RolePermissionRepository
from src.repositories.kpi_repository import KPIRepository, KPITargetRepository
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.authorization_service import AuthorizationService
from src.services.kpi_service import KPIService
from src.views.dialogs.login_dialog import LoginDialog
from src.views.dialogs.employee_dialog import EmployeeDialog
from src.views.dialogs.role_permission_dialog import RolePermissionDialog, PermissionMatrixDialog
from src.views.dialogs.kpi_dashboard import KPIDashboardScreen
from src.views.dialogs.kpi_target_dialog import TargetSettingDialog
from src.views.widgets.employee_list_widget import EmployeeListWidget


def test_login_dialog():
    """Test Login Dialog."""
    print("\n=== Testing Login Dialog ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    user_repo = UserRepository(db)
    auth_repo = AuthRepository(db)
    role_repo = RoleRepository(db)

    user_service = UserService(user_repo, role_repo)
    auth_service = AuthService(user_repo, auth_repo)

    dialog = LoginDialog(auth_service)
    dialog.show()

    print("Login Dialog shown. Close window to continue...")
    return app.exec()


def test_employee_list():
    """Test Employee List Widget."""
    print("\n=== Testing Employee List Widget ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user_service = UserService(user_repo, role_repo)

    widget = EmployeeListWidget(user_service)
    widget.show()

    print("Employee List Widget shown. Close window to continue...")
    return app.exec()


def test_employee_dialog():
    """Test Employee Dialog (Add/Edit)."""
    print("\n=== Testing Employee Dialog ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user_service = UserService(user_repo, role_repo)

    # Test Add dialog
    dialog = EmployeeDialog(user_service)
    result = dialog.exec()
    print(f"Add Dialog result: {result}")

    # Test Edit dialog (if user exists)
    users = user_repo.get_all()
    if users:
        dialog = EmployeeDialog(user_service, users[0])
        result = dialog.exec()
        print(f"Edit Dialog result: {result}")

    return 0


def test_role_permission_dialog():
    """Test Role Permission Dialog."""
    print("\n=== Testing Role Permission Dialog ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    perm_repo = PermissionRepository(db)
    role_perm_repo = RolePermissionRepository(db)
    role_repo = RoleRepository(db)

    # Get first non-admin role
    roles = role_repo.get_all()
    if len(roles) > 1:
        dialog = RolePermissionDialog(
            roles[1], perm_repo, role_perm_repo, role_repo
        )
        dialog.show()
        print("Role Permission Dialog shown. Close window to continue...")
        return app.exec()
    else:
        print("No roles available to test")
        return 0


def test_permission_matrix():
    """Test Permission Matrix Dialog."""
    print("\n=== Testing Permission Matrix Dialog ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    perm_repo = PermissionRepository(db)
    role_perm_repo = RolePermissionRepository(db)
    role_repo = RoleRepository(db)

    dialog = PermissionMatrixDialog(perm_repo, role_perm_repo, role_repo)
    dialog.show()

    print("Permission Matrix Dialog shown. Close window to continue...")
    return app.exec()


def test_kpi_dashboard():
    """Test KPI Dashboard Screen."""
    print("\n=== Testing KPI Dashboard ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    user_repo = UserRepository(db)
    kpi_repo = KPIRepository(db)
    target_repo = KPITargetRepository(db)

    kpi_service = KPIService(kpi_repo, target_repo, user_repo)

    # Get first user
    users = user_repo.get_all()
    if users:
        screen = KPIDashboardScreen(kpi_service, user_repo, users[0].id)
        screen.show()
        print("KPI Dashboard shown. Close window to continue...")
        return app.exec()
    else:
        print("No users available to test")
        return 0


def test_kpi_target_dialog():
    """Test KPI Target Setting Dialog."""
    print("\n=== Testing KPI Target Dialog ===")
    app = QApplication.instance() or QApplication(sys.argv)

    db = DatabaseHelper("data/test_ui.db")
    user_repo = UserRepository(db)
    kpi_repo = KPIRepository(db)
    target_repo = KPITargetRepository(db)

    kpi_service = KPIService(kpi_repo, target_repo, user_repo)

    # Get first user as current user
    users = user_repo.get_all()
    if users:
        dialog = TargetSettingDialog(
            kpi_service, user_repo, target_repo, users[0].id
        )
        dialog.show()
        print("KPI Target Dialog shown. Close window to continue...")
        return app.exec()
    else:
        print("No users available to test")
        return 0


def run_all_tests():
    """Run all UI tests sequentially."""
    tests = [
        ("Login Dialog", test_login_dialog),
        ("Employee List", test_employee_list),
        ("Employee Dialog", test_employee_dialog),
        ("Role Permission Dialog", test_role_permission_dialog),
        ("Permission Matrix", test_permission_matrix),
        ("KPI Dashboard", test_kpi_dashboard),
        ("KPI Target Dialog", test_kpi_target_dialog),
    ]

    print("=" * 50)
    print("CAR MANAGEMENT SYSTEM - UI TEST SUITE")
    print("=" * 50)

    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print('='*50)
        try:
            result = test_func()
            print(f"✓ {name} completed")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("All UI tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UI Test Runner")
    parser.add_argument(
        "--test",
        choices=[
            "login", "employee_list", "employee_dialog",
            "role_permission", "permission_matrix",
            "kpi_dashboard", "kpi_target", "all"
        ],
        default="all",
        help="Which test to run"
    )

    args = parser.parse_args()

    if args.test == "login":
        test_login_dialog()
    elif args.test == "employee_list":
        test_employee_list()
    elif args.test == "employee_dialog":
        test_employee_dialog()
    elif args.test == "role_permission":
        test_role_permission_dialog()
    elif args.test == "permission_matrix":
        test_permission_matrix()
    elif args.test == "kpi_dashboard":
        test_kpi_dashboard()
    elif args.test == "kpi_target":
        test_kpi_target_dialog()
    else:
        run_all_tests()
```

### Chạy Script Test Giao Diện

```bash
# Chạy tất cả UI tests
python run_ui_tests.py

# Chạy từng test riêng
python run_ui_tests.py --test login
python run_ui_tests.py --test employee_list
python run_ui_tests.py --test employee_dialog
python run_ui_tests.py --test role_permission
python run_ui_tests.py --test permission_matrix
python run_ui_tests.py --test kpi_dashboard
python run_ui_tests.py --test kpi_target
```

---

## 🔧 Xử Lý Lỗi

### Lỗi ImportError: No module named 'src'

**Nguyên nhân:** Python không tìm thấy module `src`

**Giải pháp:**
```bash
# Thêm PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%\src          # Windows

# Hoặc chạy với -m
python -m pytest tests/
```

### Lỗi ModuleNotFoundError: No module named 'PyQt6'

**Giải pháp:**
```bash
pip install PyQt6
```

### Lỗi Database Locked

**Nguyên nhân:** Có process khác đang sử dụng database

**Giải pháp:**
```bash
# Đóng tất cả ứng dụng đang chạy
# Xóa file database test (nếu là test database)
rm data/test.db
```

### Lỗi bcrypt Not Found

**Giải pháp:**
```bash
pip install bcrypt
```

### Lỗi Permission Denied trên Windows

**Giải pháp:**
```bash
# Chạy Command Prompt hoặc PowerShell với quyền Administrator
# Hoặc di chuyển project sang thư mục không bị giới hạn quyền
```

---

## 📊 Expected Output

### Khi Chạy Tests Thành Công

```
test_login_success (tests.test_auth_service.TestAuthService.test_login_success)
Test successful login. ... ok
test_login_wrong_password (tests.test_auth_service.TestAuthService.test_login_wrong_password)
Test login with wrong password. ... ok
...
----------------------------------------------------------------------
Ran 90 tests in X.XXXs
OK
```

### Khi Chạy UI Tests

```
==================================================
CAR MANAGEMENT SYSTEM - UI TEST SUITE
==================================================

==================================================
Running: Login Dialog
==================================================
=== Testing Login Dialog ===
Login Dialog shown. Close window to continue...
✓ Login Dialog completed

...

==================================================
All UI tests completed!
==================================================
```

---

## 📝 Ghi Chú

1. **Tests độc lập:** Mỗi test tạo database riêng trong thư mục tạm, không ảnh hưởng database chính
2. **Clean up:** Test tự động xóa database tạm sau khi chạy
3. **UI Tests:** Yêu cầu môi trường desktop (không chạy được trên server headless)
4. **Coverage:** Mục tiêu coverage >= 80% cho unit tests

---

## 🔗 Liên Kết

- [README.md](README.md) - Tài liệu chính
- [Database Design](docs/DATABASE_DESIGN.md) - Thiết kế database
- [Sprint 0.1](sprints/sprint-0.1.md) - Employee Management
- [Sprint 0.2](sprints/sprint-0.2.md) - Authentication
- [Sprint 0.3](sprints/sprint-0.3.md) - Authorization
- [Sprint 0.4](sprints/sprint-0.4.md) - Employee KPI
