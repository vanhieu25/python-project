"""
Script chạy test giao diện thực tế.
Test các dialog và screen chính của Car Management System.

Usage:
    python run_ui_tests.py                    # Chạy tất cả tests
    python run_ui_tests.py --test login       # Chạy test login dialog
    python run_ui_tests.py --test kpi_dashboard  # Chạy test KPI dashboard
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

    print("✓ Login Dialog shown")
    print("  - Username: admin")
    print("  - Password: admin123")
    print("  - Close window to continue...")
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

    print("✓ Employee List Widget shown")
    print("  - Features: Search, Filter, Add/Edit/Delete")
    print("  - Close window to continue...")
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
    print("  Showing Add Employee Dialog...")
    dialog = EmployeeDialog(user_service)
    result = dialog.exec()
    print(f"  ✓ Add Dialog closed (result: {result})")

    # Test Edit dialog (if user exists)
    users = user_repo.get_all()
    if users:
        print(f"  Showing Edit Dialog for: {users[0].full_name}")
        dialog = EmployeeDialog(user_service, users[0])
        result = dialog.exec()
        print(f"  ✓ Edit Dialog closed (result: {result})")

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
        role = roles[1]
        print(f"  Editing permissions for role: {role.role_name}")
        dialog = RolePermissionDialog(
            role, perm_repo, role_perm_repo, role_repo
        )
        dialog.show()
        print("  ✓ Role Permission Dialog shown")
        print("  - Check/uncheck permissions to assign")
        print("  - Close window to continue...")
        return app.exec()
    else:
        print("  ! No roles available to test")
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

    print("  ✓ Permission Matrix Dialog shown")
    print("  - View all role permissions at a glance")
    print("  - Close window to continue...")
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
        user = users[0]
        print(f"  Showing KPI Dashboard for: {user.full_name}")

        # Create sample KPI data if none exists
        from datetime import date
        today = date.today()
        existing = kpi_repo.get_by_user_and_period(
            user.id, 'monthly', f"{today.year}-{today.month:02d}"
        )
        if not existing:
            print("  Creating sample KPI data...")
            kpi_service.calculate_monthly_kpi(
                user.id, today.year, today.month,
                cars_sold=15,
                revenue_generated=1500000000,  # 1.5 tỷ
                new_customers=8,
                contracts_signed=15
            )
            print("  ✓ Sample data created")

        screen = KPIDashboardScreen(kpi_service, user_repo, user.id)
        screen.show()
        print("  ✓ KPI Dashboard shown")
        print("  - View performance score, cars sold, revenue")
        print("  - Top performers list")
        print("  - KPI history")
        print("  - Close window to continue...")
        return app.exec()
    else:
        print("  ! No users available to test")
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
        print("  ✓ KPI Target Dialog shown")
        print("  - Set targets for sales, revenue, new customers")
        print("  - Apply to all employees or individual")
        print("  - Close window to continue...")
        return app.exec()
    else:
        print("  ! No users available to test")
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

    print("=" * 60)
    print("  CAR MANAGEMENT SYSTEM - UI TEST SUITE")
    print("=" * 60)
    print("\n  This script will open each UI component for manual testing.")
    print("  Close each window to proceed to the next test.\n")

    input("  Press Enter to start testing...")

    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"  Running: {name}")
        print('='*60)
        try:
            result = test_func()
            print(f"  ✓ {name} completed")
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("  All UI tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="UI Test Runner for Car Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ui_tests.py                    # Run all tests
  python run_ui_tests.py --test login       # Test login dialog
  python run_ui_tests.py --test kpi_dashboard  # Test KPI dashboard
        """
    )
    parser.add_argument(
        "--test",
        choices=[
            "login", "employee_list", "employee_dialog",
            "role_permission", "permission_matrix",
            "kpi_dashboard", "kpi_target", "all"
        ],
        default="all",
        help="Which test to run (default: all)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tests"
    )

    args = parser.parse_args()

    if args.list:
        print("""
Available UI Tests:
  login              - Login Dialog
  employee_list      - Employee List Widget
  employee_dialog    - Employee Add/Edit Dialog
  role_permission    - Role Permission Assignment
  permission_matrix  - Permission Matrix View
  kpi_dashboard      - KPI Dashboard Screen
  kpi_target         - KPI Target Setting Dialog
  all                - Run all tests sequentially
        """)
        sys.exit(0)

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
