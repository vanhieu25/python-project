"""
Role Permission Dialog for managing role-permission assignments.
Sprint 0.3: Authorization
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QDialogButtonBox, QGroupBox,
    QSplitter, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.repositories.permission_repository import PermissionRepository, RolePermissionRepository
from src.repositories.user_repository import RoleRepository
from src.models.permission import Permission
from src.models.user import Role


class RolePermissionDialog(QDialog):
    """Dialog for managing role permissions."""

    permissions_updated = pyqtSignal(int)  # Emits role_id when permissions change

    def __init__(
        self,
        role: Role,
        permission_repo: PermissionRepository,
        role_permission_repo: RolePermissionRepository,
        role_repo: RoleRepository,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.role = role
        self.permission_repo = permission_repo
        self.role_permission_repo = role_permission_repo
        self.role_repo = role_repo
        self.current_permissions: set = set()

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(f"Phân quyền: {self.role.role_name}")
        self.setMinimumSize(700, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel(f"Quản lý quyền cho: <b>{self.role.role_name}</b>")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(f"Mô tả: {self.role.description or 'Không có mô tả'}")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Permission tree
        self.permission_tree = QTreeWidget()
        self.permission_tree.setHeaderLabels([
            "Quyền", "Mã", "Module", "Action", "Mô tả"
        ])
        self.permission_tree.setColumnWidth(0, 200)
        self.permission_tree.setColumnWidth(1, 150)
        self.permission_tree.setColumnWidth(2, 100)
        self.permission_tree.setColumnWidth(3, 80)
        self.permission_tree.setColumnWidth(4, 200)
        self.permission_tree.setSortingEnabled(True)

        # Enable checkboxes
        self.permission_tree.setItemDelegateForColumn(0, None)

        layout.addWidget(self.permission_tree)

        # Stats
        self.stats_label = QLabel("Đã chọn: 0 / 0 quyền")
        self.stats_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()

        # Select/Deselect all buttons
        self.select_all_btn = QPushButton("Chọn tất cả")
        self.select_all_btn.setObjectName("secondaryButton")
        self.select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Bỏ chọn tất cả")
        self.deselect_all_btn.setObjectName("secondaryButton")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(self.deselect_all_btn)

        button_layout.addStretch()

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._save_permissions)
        self.button_box.rejected.connect(self.reject)
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)

        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                padding: 8px;
            }
            QTreeWidget::header {
                background-color: #f5f5f7;
                padding: 8px;
                border-bottom: 1px solid #d1d1d6;
            }
            QTreeWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e5e5e5;
            }
            QTreeWidget::item:selected {
                background-color: #007aff;
                color: white;
            }
            QPushButton#secondaryButton {
                background-color: #e5e5e5;
                color: #333;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton#secondaryButton:hover {
                background-color: #d1d1d6;
            }
        """)

    def _load_data(self):
        """Load permissions and current role permissions."""
        # Get all permissions grouped by module
        all_permissions = self.permission_repo.get_all()

        # Get current role permissions
        self.current_permissions = self.permission_repo.get_permission_codes_by_role(
            self.role.id
        )

        # Group by module
        modules: dict = {}
        for perm in all_permissions:
            module = perm.module or "Khác"
            if module not in modules:
                modules[module] = []
            modules[module].append(perm)

        # Create tree items
        self.permission_tree.clear()

        for module_name, permissions in sorted(modules.items()):
            # Module node
            module_item = QTreeWidgetItem(self.permission_tree)
            module_item.setText(0, module_name.upper())
            module_item.setFlags(
                module_item.flags() | Qt.ItemFlag.ItemIsAutoTristate
            )
            module_item.setCheckState(0, Qt.CheckState.Unchecked)

            # Module display name mapping
            module_display_names = {
                'cars': 'Quản lý xe',
                'customers': 'Quản lý khách hàng',
                'contracts': 'Quản lý hợp đồng',
                'inventory': 'Quản lý kho',
                'reports': 'Báo cáo',
                'users': 'Quản lý nhân viên',
                'settings': 'Cài đặt',
                'backup': 'Sao lưu'
            }
            display_name = module_display_names.get(module_name.lower(), module_name.upper())
            module_item.setText(0, display_name)

            # Permission items
            for perm in permissions:
                perm_item = QTreeWidgetItem(module_item)
                perm_item.setText(0, perm.permission_name)
                perm_item.setText(1, perm.permission_code)
                perm_item.setText(2, perm.module or "")
                perm_item.setText(3, perm.action or "")
                perm_item.setText(4, perm.description or "")

                # Check if already assigned
                is_checked = perm.permission_code in self.current_permissions
                perm_item.setCheckState(
                    0,
                    Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
                )

                # Store permission code for saving
                perm_item.setData(0, Qt.ItemDataRole.UserRole, perm.permission_code)

            # Expand module
            module_item.setExpanded(True)

        self._update_stats()

    def _update_stats(self):
        """Update permission count statistics."""
        total = 0
        checked = 0

        root = self.permission_tree.invisibleRootItem()
        for i in range(root.childCount()):
            module_item = root.child(i)
            for j in range(module_item.childCount()):
                perm_item = module_item.child(j)
                total += 1
                if perm_item.checkState(0) == Qt.CheckState.Checked:
                    checked += 1

        self.stats_label.setText(f"Đã chọn: {checked} / {total} quyền")

    def _select_all(self):
        """Select all permissions."""
        self._set_all_checkboxes(True)
        self._update_stats()

    def _deselect_all(self):
        """Deselect all permissions."""
        self._set_all_checkboxes(False)
        self._update_stats()

    def _set_all_checkboxes(self, checked: bool):
        """Set all checkboxes to a state."""
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked

        root = self.permission_tree.invisibleRootItem()
        for i in range(root.childCount()):
            module_item = root.child(i)
            module_item.setCheckState(0, state)
            for j in range(module_item.childCount()):
                perm_item = module_item.child(j)
                perm_item.setCheckState(0, state)

    def _save_permissions(self):
        """Save the selected permissions."""
        # Collect selected permission codes
        selected_codes: set = set()

        root = self.permission_tree.invisibleRootItem()
        for i in range(root.childCount()):
            module_item = root.child(i)
            for j in range(module_item.childCount()):
                perm_item = module_item.child(j)
                if perm_item.checkState(0) == Qt.CheckState.Checked:
                    code = perm_item.data(0, Qt.ItemDataRole.UserRole)
                    if code:
                        selected_codes.add(code)

        # Get permission IDs from codes
        all_permissions = self.permission_repo.get_all()
        selected_ids = [
            p.id for p in all_permissions
            if p.permission_code in selected_codes
        ]

        try:
            # Save to database
            self.role_permission_repo.set_role_permissions(self.role.id, selected_ids)

            # Emit signal
            self.permissions_updated.emit(self.role.id)

            QMessageBox.information(
                self,
                "Thành công",
                f"Đã cập nhật quyền cho vai trò '{self.role.role_name}'"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lưu quyền: {str(e)}"
            )


class PermissionMatrixDialog(QDialog):
    """Dialog showing the permission matrix for all roles."""

    def __init__(
        self,
        permission_repo: PermissionRepository,
        role_permission_repo: RolePermissionRepository,
        role_repo: RoleRepository,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.permission_repo = permission_repo
        self.role_permission_repo = role_permission_repo
        self.role_repo = role_repo

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Ma trận phân quyền")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Ma trận phân quyền")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel("Tổng quan các quyền được gán cho từng vai trò trong hệ thống")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Permission matrix tree
        self.matrix_tree = QTreeWidget()
        self.matrix_tree.setHeaderLabels([
            "Module / Quyền", "Admin", "Manager", "Sales", "Accountant"
        ])
        self.matrix_tree.setColumnWidth(0, 300)

        layout.addWidget(self.matrix_tree)

        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
            }
            QTreeWidget::header {
                background-color: #f5f5f7;
                padding: 8px;
                border-bottom: 1px solid #d1d1d6;
                font-weight: bold;
            }
            QPushButton {
                background-color: #007aff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0056cc;
            }
        """)

    def _load_data(self):
        """Load permission matrix."""
        # Get all roles
        roles = self.role_repo.get_all()
        role_permissions: dict = {}

        for role in roles:
            perms = self.permission_repo.get_permission_codes_by_role(role.id)
            role_permissions[role.role_code] = perms

        # Get all permissions grouped by module
        all_permissions = self.permission_repo.get_all()
        modules: dict = {}
        for perm in all_permissions:
            module = perm.module or "Khác"
            if module not in modules:
                modules[module] = []
            modules[module].append(perm)

        # Module display names
        module_display_names = {
            'cars': 'Quản lý xe',
            'customers': 'Quản lý khách hàng',
            'contracts': 'Quản lý hợp đồng',
            'inventory': 'Quản lý kho',
            'reports': 'Báo cáo',
            'users': 'Quản lý nhân viên',
            'settings': 'Cài đặt',
            'backup': 'Sao lưu'
        }

        # Build tree
        self.matrix_tree.clear()

        for module_name, permissions in sorted(modules.items()):
            # Module node
            module_item = QTreeWidgetItem(self.matrix_tree)
            display_name = module_display_names.get(module_name.lower(), module_name.upper())
            module_item.setText(0, display_name)
            module_item.setForeground(0, self.palette().color(self.foregroundRole()))

            # Check marks for each role
            for i, role_code in enumerate(['admin', 'manager', 'sales', 'accountant'], 1):
                has_any = any(
                    p.permission_code in role_permissions.get(role_code, set())
                    for p in permissions
                )
                module_item.setText(i, "✓" if has_any else "")
                module_item.setTextAlignment(i, Qt.AlignmentFlag.AlignCenter)

            # Permission items
            for perm in permissions:
                perm_item = QTreeWidgetItem(module_item)
                perm_item.setText(0, f"  {perm.permission_name}")

                for i, role_code in enumerate(['admin', 'manager', 'sales', 'accountant'], 1):
                    has_perm = perm.permission_code in role_permissions.get(role_code, set())
                    perm_item.setText(i, "✓" if has_perm else "")
                    perm_item.setTextAlignment(i, Qt.AlignmentFlag.AlignCenter)
                    if has_perm:
                        perm_item.setForeground(i, self.palette().color(self.foregroundRole()))

            module_item.setExpanded(True)
