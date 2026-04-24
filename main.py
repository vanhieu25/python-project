"""
Car Management System - Main Entry Point
=====================================

Hệ thống quản lý đại lý xe hơi với PyQt6
Sprint 0-3: Employee, Car, Customer, Contract Management
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QMessageBox, QMenuBar, QMenu,
    QStackedWidget, QFrame, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QAction, QIcon

from src.database.db_helper import DatabaseHelper
from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from src.repositories.auth_repository import AuthRepository
from src.views.dialogs.login_dialog import LoginDialog
from src.views.cars.car_list_view import CarListWidget


class PlaceholderWidget(QWidget):
    """Placeholder widget for modules under development."""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setup_ui(title, description)

    def setup_ui(self, title: str, description: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(14)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666;")
        layout.addWidget(desc_label)

        # Spacer
        layout.addSpacing(40)

        # Note
        note_label = QLabel("ℹ️ Module này đang sử dụng tkinter và cần được chuyển đổi sang PyQt6")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setStyleSheet("color: #ff9800; padding: 10px;")
        layout.addWidget(note_label)


class DashboardWidget(QWidget):
    """Dashboard showing system overview."""

    def __init__(self, db_helper: DatabaseHelper, parent=None):
        super().__init__(parent)
        self.db_helper = db_helper
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("Tổng quan hệ thống")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Welcome
        welcome = QLabel("Chào mừng đến với Car Management System")
        welcome.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(welcome)

        layout.addSpacing(20)

        # Modules grid
        modules_frame = QFrame()
        modules_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        modules_layout = QHBoxLayout(modules_frame)
        modules_layout.setSpacing(15)

        modules = [
            ("👥", "Quản lý nhân viên", "Sprint 0", "#4caf50"),
            ("🚗", "Quản lý xe", "Sprint 1", "#2196f3"),
            ("👤", "Quản lý khách hàng", "Sprint 2", "#9c27b0"),
            ("📝", "Quản lý hợp đồng", "Sprint 3", "#ff9800"),
        ]

        for icon, name, sprint, color in modules:
            card = self._create_module_card(icon, name, sprint, color)
            modules_layout.addWidget(card)

        layout.addWidget(modules_frame)
        layout.addStretch()

    def _create_module_card(self, icon: str, name: str, sprint: str, color: str) -> QFrame:
        """Create a module status card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 2px solid {color};
                padding: 15px;
                min-width: 180px;
                min-height: 120px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Icon
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Name
        name_label = QLabel(name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Sprint
        sprint_label = QLabel(sprint)
        sprint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sprint_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        layout.addWidget(sprint_label)

        # Status
        status = "✅ Hoàn thành" if sprint in ["Sprint 0", "Sprint 1", "Sprint 2", "Sprint 3"] else "⏳ Đang phát triển"
        status_label = QLabel(status)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        layout.addWidget(status_label)

        return card


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.db_helper = DatabaseHelper("data/car_management.db")

        # Initialize repositories
        user_repo = UserRepository(self.db_helper)
        auth_repo = AuthRepository(self.db_helper)
        self.auth_service = AuthService(user_repo, auth_repo)

        self.setWindowTitle("Car Management System")
        self.setMinimumSize(1200, 800)

        self.setup_ui()
        self.show_login()

    def setup_ui(self):
        """Setup main window UI."""
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget for content
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)

        # Create pages
        self.dashboard = DashboardWidget(self.db_helper)
        self.content_stack.addWidget(self.dashboard)

        # Car Management (PyQt6)
        self.car_widget = CarListWidget(self.db_helper)
        self.content_stack.addWidget(self.car_widget)

        # Add placeholder pages for other modules
        self.customer_placeholder = PlaceholderWidget(
            "👤 Quản lý khách hàng",
            "Module quản lý thông tin khách hàng, lịch sử giao dịch, và phân loại VIP\n\n"
            "Các chức năng:\n"
            "• Thêm mới khách hàng\n"
            "• Cập nhật thông tin\n"
            "• Xem lịch sử giao dịch\n"
            "• Phân loại khách hàng (VIP, Regular, Potential)"
        )
        self.content_stack.addWidget(self.customer_placeholder)

        self.contract_placeholder = PlaceholderWidget(
            "📝 Quản lý hợp đồng",
            "Module quản lý hợp đồng bán xe, approval workflow, và in ấn\n\n"
            "Các chức năng:\n"
            "• Tạo hợp đồng mới\n"
            "• Tính toán giá trị hợp đồng\n"
            "• Thêm phụ kiện vào hợp đồng\n"
            "• Approval workflow\n"
            "• In hợp đồng PDF"
        )
        self.content_stack.addWidget(self.contract_placeholder)

        # Setup menu
        self.setup_menu()

    def setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        logout_action = QAction("Đăng xuất", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        file_menu.addSeparator()

        exit_action = QAction("Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Modules menu
        modules_menu = menubar.addMenu("&Modules")

        dashboard_action = QAction("📊 Tổng quan", self)
        dashboard_action.triggered.connect(lambda: self.content_stack.setCurrentIndex(0))
        modules_menu.addAction(dashboard_action)

        modules_menu.addSeparator()

        car_action = QAction("🚗 Quản lý xe", self)
        car_action.triggered.connect(lambda: self.content_stack.setCurrentIndex(1))
        modules_menu.addAction(car_action)

        customer_action = QAction("👤 Quản lý khách hàng", self)
        customer_action.triggered.connect(lambda: self.content_stack.setCurrentIndex(2))
        modules_menu.addAction(customer_action)

        contract_action = QAction("📝 Quản lý hợp đồng", self)
        contract_action.triggered.connect(lambda: self.content_stack.setCurrentIndex(3))
        modules_menu.addAction(contract_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("Về phần mềm", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_login(self):
        """Show login dialog."""
        login_dialog = LoginDialog(self.auth_service, self)
        login_dialog.login_successful.connect(self.on_login_success)

        if not login_dialog.exec():
            # Login cancelled
            self.close()
            sys.exit(0)

    def on_login_success(self, user_data: dict):
        """Handle successful login."""
        self.current_user = user_data
        self.setWindowTitle(f"Car Management System - {user_data.get('full_name', 'User')}")

        # Update status bar
        self.statusBar().showMessage(
            f"Đăng nhập thành công: {user_data.get('full_name')} "
            f"({user_data.get('role_code', 'user')})"
        )

    def logout(self):
        """Logout current user."""
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            self.show_login()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "Về Car Management System",
            "<h2>Car Management System</h2>"
            "<p>Phiên bản: 1.0.0</p>"
            "<p>Hệ thống quản lý đại lý xe hơi</p>"
            "<hr>"
            "<p><b>Các module đã hoàn thành:</b></p>"
            "<ul>"
            "<li>✅ Sprint 0: Quản lý nhân viên & Phân quyền</li>"
            "<li>✅ Sprint 1: Quản lý xe</li>"
            "<li>✅ Sprint 2: Quản lý khách hàng</li>"
            "<li>✅ Sprint 3: Quản lý hợp đồng</li>"
            "</ul>"
        )


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Car Management System")
    app.setApplicationVersion("1.0.0")

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
