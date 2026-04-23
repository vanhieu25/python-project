"""
Login Dialog - User authentication dialog.
Sprint 0.2: Authentication
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QCheckBox,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...services.auth_service import (
    AuthService, InvalidCredentialsError,
    AccountLockedError, AccountInactiveError
)


class LoginDialog(QDialog):
    """Dialog for user login."""

    # Signals
    login_successful = pyqtSignal(dict)  # Emits user data on success

    def __init__(self, auth_service: AuthService, parent=None):
        """Initialize login dialog.

        Args:
            auth_service: Authentication service instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.auth_service = auth_service

        self.setWindowTitle("Đăng nhập hệ thống")
        self.setFixedSize(450, 500)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )

        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        """Setup UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title_label = QLabel("Car Management System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1d1d1f; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Đăng nhập để tiếp tục")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #86868b; margin-bottom: 20px;")
        main_layout.addWidget(subtitle_label)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        ))

        # Username
        username_label = QLabel("Tên đăng nhập")
        username_label.setStyleSheet("font-weight: bold; color: #1d1d1f;")
        main_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0071e3;
            }
        """)
        main_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Mật khẩu")
        password_label.setStyleSheet("font-weight: bold; color: #1d1d1f;")
        main_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0071e3;
            }
        """)
        main_layout.addWidget(self.password_input)

        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Hiển thị mật khẩu")
        self.show_password_checkbox.setStyleSheet("color: #86868b;")
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        main_layout.addWidget(self.show_password_checkbox)

        # Remember me checkbox
        self.remember_me_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_me_checkbox.setStyleSheet("color: #86868b;")
        main_layout.addWidget(self.remember_me_checkbox)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        ))

        # Login button
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setMinimumHeight(45)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QPushButton:pressed {
                background-color: #005bb5;
            }
            QPushButton:disabled {
                background-color: #d2d2d7;
                color: #86868b;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        main_layout.addWidget(self.login_button)

        # Default login info
        info_label = QLabel("Mặc định: admin / admin123")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #86868b; font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(info_label)

        # Set tab order
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.login_button)

        # Connect enter key
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.attempt_login)

        # Focus username on start
        self.username_input.setFocus()

    def center_on_screen(self):
        """Center dialog on screen."""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )

    def toggle_password_visibility(self, checked: bool):
        """Toggle password visibility.

        Args:
            checked: Whether checkbox is checked
        """
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def attempt_login(self):
        """Attempt to login."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validation
        if not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập")
            self.username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu")
            self.password_input.setFocus()
            return

        # Disable button while processing
        self.login_button.setEnabled(False)
        self.login_button.setText("Đang đăng nhập...")

        try:
            # Attempt login
            result = self.auth_service.login(username, password)

            # Success
            self.login_successful.emit({
                'session_token': result['session_token'],
                'user': result['user'],
                'expires_at': result['expires_at'],
                'remember_me': self.remember_me_checkbox.isChecked()
            })

            self.accept()

        except AccountLockedError as e:
            QMessageBox.warning(self, "Tài khoản bị khóa", str(e))

        except AccountInactiveError as e:
            QMessageBox.warning(self, "Tài khoản không hoạt động", str(e))

        except InvalidCredentialsError:
            QMessageBox.warning(
                self, "Đăng nhập thất bại",
                "Tên đăng nhập hoặc mật khẩu không đúng"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi",
                f"Không thể đăng nhập: {e}"
            )

        finally:
            # Re-enable button
            self.login_button.setEnabled(True)
            self.login_button.setText("Đăng nhập")

    def get_login_result(self) -> dict:
        """Get login result after successful login.

        Returns:
            Dictionary with login result
        """
        # This is used after exec() returns Accepted
        # The result should be stored from the signal
        return getattr(self, '_login_result', None)

    def closeEvent(self, event):
        """Handle close event.

        Args:
            event: Close event
        """
        # Allow closing
        event.accept()
