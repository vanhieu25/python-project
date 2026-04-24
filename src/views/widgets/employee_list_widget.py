"""
Employee List Widget - Display and manage employee list.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
    QLabel, QMessageBox, QHeaderView, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from ...models.user import User
from ...services.user_service import UserService, UserNotFoundError
from .employee_dialog import EmployeeDialog


class EmployeeListWidget(QWidget):
    """Widget for displaying and managing employee list."""

    # Signals
    employee_selected = pyqtSignal(int)  # Emits user_id when employee selected

    def __init__(self, user_service: UserService, parent=None):
        """Initialize widget.

        Args:
            user_service: User service instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.user_service = user_service
        self.current_employees = []

        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm theo tên, username, email...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_input)

        # Status filter
        toolbar.addWidget(QLabel("Trạng thái:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tất cả", None)
        self.status_filter.addItem("Đang hoạt động", "active")
        self.status_filter.addItem("Ngừng hoạt động", "inactive")
        self.status_filter.currentIndexChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.status_filter)

        toolbar.addStretch()

        # Add button
        self.add_button = QPushButton("+ Thêm nhân viên")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        self.add_button.clicked.connect(self.on_add)
        toolbar.addWidget(self.add_button)

        layout.addLayout(toolbar)

        # Employee table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Họ tên", "Email", "Phòng ban", "Vai trò", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0071e3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f7;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

        layout.addWidget(self.table)

        # Status bar
        self.status_label = QLabel("Tổng: 0 nhân viên")
        layout.addWidget(self.status_label)

    def load_employees(self):
        """Load employees into table."""
        try:
            keyword = self.search_input.text().strip()
            status = self.status_filter.currentData()

            if keyword:
                self.current_employees = self.user_service.search_users(
                    keyword, status=status
                )
            else:
                self.current_employees = self.user_service.get_all_users()
                if status:
                    self.current_employees = [
                        u for u in self.current_employees if u.status == status
                    ]

            self.populate_table()
            self.update_status()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách: {e}")

    def populate_table(self):
        """Populate table with employee data."""
        self.table.setRowCount(len(self.current_employees))

        for row, user in enumerate(self.current_employees):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))

            # Username
            self.table.setItem(row, 1, QTableWidgetItem(user.username))

            # Full name
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name))

            # Email
            self.table.setItem(row, 3, QTableWidgetItem(user.email or ""))

            # Department
            self.table.setItem(row, 4, QTableWidgetItem(user.department or ""))

            # Role
            role_name = user.role_name or ""
            self.table.setItem(row, 5, QTableWidgetItem(role_name))

            # Status
            status_text = "Đang hoạt động" if user.status == 'active' else "Ngừng hoạt động"
            status_item = QTableWidgetItem(status_text)
            if user.status == 'active':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 6, status_item)

            # Store user ID in first column
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user.id)

    def update_status(self):
        """Update status label."""
        total = len(self.current_employees)
        active = sum(1 for u in self.current_employees if u.status == 'active')
        self.status_label.setText(f"Tổng: {total} nhân viên | Đang hoạt động: {active}")

    def get_selected_user_id(self) -> int:
        """Get selected user ID.

        Returns:
            int: User ID or -1 if none selected
        """
        selected = self.table.selectedItems()
        if not selected:
            return -1
        row = selected[0].row()
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def on_search(self):
        """Handle search input change."""
        self.load_employees()

    def on_filter_changed(self):
        """Handle filter change."""
        self.load_employees()

    def on_add(self):
        """Handle add button click."""
        dialog = EmployeeDialog(self.user_service, parent=self)
        if dialog.exec() == EmployeeDialog.DialogCode.Accepted:
            self.load_employees()

    def on_edit(self, user_id: int = None):
        """Handle edit action.

        Args:
            user_id: User ID to edit (if None, uses selected)
        """
        if user_id is None:
            user_id = self.get_selected_user_id()

        if user_id < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên cần sửa")
            return

        try:
            user = self.user_service.get_user(user_id)
            dialog = EmployeeDialog(self.user_service, user=user, parent=self)
            if dialog.exec() == EmployeeDialog.DialogCode.Accepted:
                self.load_employees()
        except UserNotFoundError:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy nhân viên")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa: {e}")

    def on_delete(self, user_id: int = None):
        """Handle delete action.

        Args:
            user_id: User ID to delete (if None, uses selected)
        """
        if user_id is None:
            user_id = self.get_selected_user_id()

        if user_id < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên cần xóa")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc muốn xóa nhân viên này?\n\n"
            "(Nhân viên sẽ bị ẩn khỏi hệ thống nhưng dữ liệu vẫn được lưu)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.user_service.delete_user(user_id, permanent=False)
            QMessageBox.information(self, "Thành công", "Đã xóa nhân viên")
            self.load_employees()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")

    def on_double_click(self):
        """Handle double click on table."""
        self.on_edit()

    def show_context_menu(self, position):
        """Show context menu.

        Args:
            position: Mouse position
        """
        user_id = self.get_selected_user_id()
        if user_id < 0:
            return

        menu = QMenu(self)

        edit_action = QAction("Chỉnh sửa", self)
        edit_action.triggered.connect(lambda: self.on_edit(user_id))
        menu.addAction(edit_action)

        delete_action = QAction("Xóa", self)
        delete_action.triggered.connect(lambda: self.on_delete(user_id))
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def refresh(self):
        """Refresh employee list."""
        self.load_employees()
