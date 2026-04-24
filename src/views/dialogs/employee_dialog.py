"""
Employee Dialog - Add/Edit employee form.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QMessageBox,
    QFormLayout, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from ...models.user import User, Role
from ...services.user_service import UserService, ValidationError, DuplicateUserError


class EmployeeDialog(QDialog):
    """Dialog for adding or editing employees."""

    def __init__(self, user_service: UserService, user: User = None,
                 parent=None):
        """Initialize dialog.

        Args:
            user_service: User service instance
            user: User to edit (None for new user)
            parent: Parent widget
        """
        super().__init__(parent)
        self.user_service = user_service
        self.user = user
        self.roles = []

        self.setWindowTitle("Thêm nhân viên" if not user else "Chỉnh sửa nhân viên")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_roles()

        if user:
            self.load_user_data()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Form group
        form_group = QGroupBox("Thông tin nhân viên")
        form_layout = QFormLayout()

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập username (3-50 ký tự)")
        form_layout.addRow("Username *:", self.username_input)

        # Password (only for new user)
        if not self.user:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("Tối thiểu 8 ký tự, có chữ hoa, thường, số")
            form_layout.addRow("Mật khẩu *:", self.password_input)

            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Xác nhận mật khẩu *:", self.confirm_password_input)

        # Full name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Họ và tên đầy đủ")
        form_layout.addRow("Họ tên *:", self.full_name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Số điện thoại (10-15 số)")
        form_layout.addRow("Điện thoại:", self.phone_input)

        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItem("-- Chọn vai trò --", None)
        form_layout.addRow("Vai trò:", self.role_combo)

        # Department
        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Phòng ban")
        form_layout.addRow("Phòng ban:", self.department_input)

        # Position
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Chức vụ")
        form_layout.addRow("Chức vụ:", self.position_input)

        # Status (only for edit)
        if self.user:
            self.status_combo = QComboBox()
            self.status_combo.addItem("Đang hoạt động", "active")
            self.status_combo.addItem("Ngừng hoạt động", "inactive")
            form_layout.addRow("Trạng thái:", self.status_combo)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_roles(self):
        """Load roles into combo box."""
        try:
            self.roles = self.user_service.get_all_roles()
            for role in self.roles:
                self.role_combo.addItem(role.role_name, role.id)
        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Không thể tải danh sách vai trò: {e}")

    def load_user_data(self):
        """Load existing user data into form."""
        if not self.user:
            return

        self.username_input.setText(self.user.username)
        self.username_input.setEnabled(False)  # Cannot change username

        self.full_name_input.setText(self.user.full_name)
        self.email_input.setText(self.user.email or "")
        self.phone_input.setText(self.user.phone or "")
        self.department_input.setText(self.user.department or "")
        self.position_input.setText(self.user.position or "")

        # Set role
        if self.user.role_id:
            index = self.role_combo.findData(self.user.role_id)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)

        # Set status
        if hasattr(self, 'status_combo'):
            index = self.status_combo.findData(self.user.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

    def validate(self) -> bool:
        """Validate form data.

        Returns:
            bool: True if valid
        """
        # Required fields
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập username")
            self.username_input.setFocus()
            return False

        if not self.user and not self.password_input.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu")
            self.password_input.setFocus()
            return False

        if not self.full_name_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên")
            self.full_name_input.setFocus()
            return False

        # Password match (for new user)
        if not self.user:
            if self.password_input.text() != self.confirm_password_input.text():
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp")
                self.confirm_password_input.setFocus()
                return False

        return True

    def get_form_data(self) -> dict:
        """Get form data as dictionary.

        Returns:
            dict: Form data
        """
        data = {
            'username': self.username_input.text().strip(),
            'full_name': self.full_name_input.text().strip(),
            'email': self.email_input.text().strip() or None,
            'phone': self.phone_input.text().strip() or None,
            'role_id': self.role_combo.currentData(),
            'department': self.department_input.text().strip() or None,
            'position': self.position_input.text().strip() or None,
        }

        if not self.user:
            data['password'] = self.password_input.text()
        else:
            data['status'] = self.status_combo.currentData()

        return data

    def save(self):
        """Save user data."""
        if not self.validate():
            return

        try:
            data = self.get_form_data()

            if self.user:
                # Update existing user
                self.user_service.update_user(self.user.id, data)
                QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin nhân viên")
            else:
                # Create new user
                password = data.pop('password')
                self.user_service.create_user(data, password=password)
                QMessageBox.information(self, "Thành công", "Đã thêm nhân viên mới")

            self.accept()

        except ValidationError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except DuplicateUserError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")
