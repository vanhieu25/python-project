"""
Customer Classification Dialog Module
Dialog for viewing and changing customer classification.
"""

from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QMessageBox, QComboBox, QTextEdit,
    QFrame
)
from PyQt6.QtCore import Qt


class CustomerClassificationDialog(QDialog):
    """Dialog for viewing and editing customer classification."""

    CLASS_OPTIONS = [
        ('vip', '⭐ VIP'),
        ('regular', '● Regular'),
        ('potential', '○ Potential')
    ]

    def __init__(self, customer_id: int, parent=None,
                 db_helper=None, current_user_id: int = 1):
        """Initialize dialog.

        Args:
            customer_id: Customer ID
            parent: Parent widget
            db_helper: Database helper instance
            current_user_id: Current user ID
        """
        super().__init__(parent)
        self.customer_id = customer_id
        self.current_user_id = current_user_id
        self.db_helper = db_helper

        # Initialize service
        if db_helper:
            from ..repositories.customer_repository import CustomerRepository
            from ..repositories.customer_classification_repository import CustomerClassificationRepository
            from ..services.customer_classification_service import CustomerClassificationService

            customer_repo = CustomerRepository(db_helper)
            classification_repo = CustomerClassificationRepository(db_helper)
            self.classification_service = CustomerClassificationService(customer_repo, classification_repo)
        else:
            self.classification_service = None

        self.classification_info = None

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Phân loại khách hàng")
        self.setMinimumSize(600, 500)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Customer info
        self._setup_customer_info(layout)

        # Metrics section
        self._setup_metrics_section(layout)

        # Classification section
        self._setup_classification_section(layout)

        # Benefits section
        self._setup_benefits_section(layout)

        # Buttons
        self._setup_buttons(layout)

        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1d1d1f;
            }
            QLabel {
                color: #1d1d1f;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #0071e3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QTextEdit {
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
        """)

    def _setup_customer_info(self, parent_layout):
        """Setup customer info header.

        Args:
            parent_layout: Parent layout
        """
        header = QLabel("⭐ Phân loại khách hàng")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        parent_layout.addWidget(header)

        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)

        self.customer_label = QLabel()
        self.customer_label.setStyleSheet("font-size: 14px; color: #666666;")
        info_layout.addWidget(self.customer_label)
        info_layout.addStretch()

        parent_layout.addWidget(info_widget)

    def _setup_metrics_section(self, parent_layout):
        """Setup metrics section.

        Args:
            parent_layout: Parent layout
        """
        group = QGroupBox("📊 Chỉ số giao dịch")
        grid = QGridLayout(group)
        grid.setSpacing(15)
        grid.setContentsMargins(15, 20, 15, 15)

        # Total contracts
        grid.addWidget(QLabel("Tổng hợp đồng:"), 0, 0)
        self.contracts_value = QLabel("0")
        self.contracts_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #0071e3;")
        grid.addWidget(self.contracts_value, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        # Total value
        grid.addWidget(QLabel("Tổng giá trị:"), 0, 1)
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #34c759;")
        grid.addWidget(self.value_label, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Average value
        grid.addWidget(QLabel("Giá trị TB:"), 0, 2)
        self.avg_label = QLabel("0")
        self.avg_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff9500;")
        grid.addWidget(self.avg_label, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(group)

    def _setup_classification_section(self, parent_layout):
        """Setup classification section.

        Args:
            parent_layout: Parent layout
        """
        group = QGroupBox("🎯 Phân loại")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)

        # Current classification
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Phân loại hiện tại:"))

        self.class_combo = QComboBox()
        for value, label in self.CLASS_OPTIONS:
            self.class_combo.addItem(label, value)
        current_layout.addWidget(self.class_combo)
        current_layout.addStretch()

        layout.addLayout(current_layout)

        # Auto classification result
        self.auto_label = QLabel()
        self.auto_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.auto_label)

        # Note for manual classification
        layout.addWidget(QLabel("Ghi chú phân loại:"))
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        self.note_input.setPlaceholderText("Nhập lý do phân loại thủ công (nếu có)...")
        layout.addWidget(self.note_input)

        parent_layout.addWidget(group)

    def _setup_benefits_section(self, parent_layout):
        """Setup benefits section.

        Args:
            parent_layout: Parent layout
        """
        group = QGroupBox("🎁 Quyền lợi")
        self.benefits_layout = QVBoxLayout(group)
        self.benefits_layout.setSpacing(8)
        self.benefits_layout.setContentsMargins(15, 20, 15, 15)

        self.benefits_container = QWidget()
        self.benefits_inner_layout = QVBoxLayout(self.benefits_container)
        self.benefits_inner_layout.setSpacing(5)
        self.benefits_inner_layout.setContentsMargins(0, 0, 0, 0)

        self.benefits_layout.addWidget(self.benefits_container)
        self.benefits_layout.addStretch()

        parent_layout.addWidget(group)

    def _setup_buttons(self, parent_layout):
        """Setup buttons.

        Args:
            parent_layout: Parent layout
        """
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.auto_btn = QPushButton("🔄 Tự động phân loại")
        self.auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #5856d6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6664e0;
            }
        """)
        self.auto_btn.clicked.connect(self._on_auto_classify)
        btn_layout.addWidget(self.auto_btn)

        self.save_btn = QPushButton("💾 Lưu thay đổi")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        parent_layout.addLayout(btn_layout)

    def _load_data(self):
        """Load customer classification data."""
        if not self.classification_service:
            return

        self.classification_info = self.classification_service.get_customer_classification_info(self.customer_id)

        if not self.classification_info:
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thông tin khách hàng")
            return

        self._update_ui()

    def _update_ui(self):
        """Update UI with loaded data."""
        info = self.classification_info
        customer = info['customer']
        metrics = info['metrics']

        # Customer info
        self.customer_label.setText(f"{customer.full_name} ({customer.customer_code})")

        # Metrics
        self.contracts_value.setText(str(metrics['total_contracts']))
        self.value_label.setText(self._format_amount(metrics['total_value']))
        self.avg_label.setText(self._format_amount(metrics['avg_value']))

        # Current classification
        current_class = info['current_class']
        for i, (value, _) in enumerate(self.CLASS_OPTIONS):
            if value == current_class:
                self.class_combo.setCurrentIndex(i)
                break

        # Benefits
        self._update_benefits(info.get('benefits', []))

        # Auto classification
        try:
            auto_class = self.classification_service.classify_customer(self.customer_id, reason='preview')
            auto_text = self._get_class_display(auto_class)
            self.auto_label.setText(f"Phân loại tự động đề xuất: {auto_text}")
        except Exception:
            self.auto_label.setText("Không thể tính phân loại tự động")

    def _update_benefits(self, benefits: list):
        """Update benefits display.

        Args:
            benefits: List of benefits
        """
        # Clear existing
        while self.benefits_inner_layout.count():
            item = self.benefits_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not benefits:
            no_benefits = QLabel("Không có quyền lợi đặc biệt")
            no_benefits.setStyleSheet("color: #888888; font-style: italic;")
            self.benefits_inner_layout.addWidget(no_benefits)
        else:
            for benefit in benefits:
                benefit_label = QLabel(f"✓ {benefit.get('benefit_name', '')}")
                benefit_label.setStyleSheet("color: #1d1d1f; padding: 2px 0;")
                if benefit.get('description'):
                    benefit_label.setToolTip(benefit['description'])
                self.benefits_inner_layout.addWidget(benefit_label)

    def _format_amount(self, amount: float) -> str:
        """Format amount.

        Args:
            amount: Amount value

        Returns:
            Formatted string
        """
        if amount >= 1000000000:
            return f"{amount / 1000000000:.1f} tỷ"
        elif amount >= 1000000:
            return f"{amount / 1000000:.0f} triệu"
        else:
            return f"{amount:,.0f}"

    def _get_class_display(self, class_value: str) -> str:
        """Get display text for class.

        Args:
            class_value: Class value

        Returns:
            Display text
        """
        for value, label in self.CLASS_OPTIONS:
            if value == class_value:
                return label
        return class_value

    def _on_auto_classify(self):
        """Handle auto classify button."""
        if not self.classification_service:
            return

        try:
            new_class = self.classification_service.classify_customer(
                self.customer_id,
                changed_by=self.current_user_id,
                reason='manual_auto'
            )

            # Update combo box
            for i, (value, _) in enumerate(self.CLASS_OPTIONS):
                if value == new_class:
                    self.class_combo.setCurrentIndex(i)
                    break

            # Reload benefits
            self._load_data()

            QMessageBox.information(
                self,
                "Thành công",
                f"Đã phân loại tự động: {self._get_class_display(new_class)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể phân loại: {str(e)}")

    def _on_save(self):
        """Handle save button."""
        if not self.classification_service:
            return

        new_class = self.class_combo.currentData()
        current_class = self.classification_info['current_class']

        if new_class == current_class:
            self.accept()
            return

        reason = self.note_input.toPlainText().strip() or "Thay đổi thủ công"

        try:
            success = self.classification_service.manual_classify(
                self.customer_id,
                new_class,
                self.current_user_id,
                reason
            )

            if success:
                QMessageBox.information(
                    self,
                    "Thành công",
                    f"Đã cập nhật phân loại thành {self._get_class_display(new_class)}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể cập nhật phân loại")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")
