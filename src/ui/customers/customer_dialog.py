"""
Customer Dialog Module
Add/Edit dialog for customers with validation.
"""

from typing import Optional, Dict, Any, Callable
from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QGroupBox, QGridLayout,
    QRadioButton, QButtonGroup, QMessageBox, QDateEdit, QFormLayout,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class CustomerDialog(QDialog):
    """Dialog for adding/editing customers."""

    # Customer sources
    SOURCES = [
        'Facebook', 'Website', 'Referral', 'Walk-in',
        'Phone Inquiry', 'Email', 'Other'
    ]

    # Customer classes
    CUSTOMER_CLASSES = [
        ('regular', 'Regular'),
        ('potential', 'Potential'),
        ('vip', 'VIP')
    ]

    def __init__(self, parent=None, customer_data: Optional[Dict] = None,
                 customer_service=None, current_user_id: int = 1):
        """Initialize dialog.

        Args:
            parent: Parent widget
            customer_data: Existing customer data for editing
            customer_service: Customer service instance
            current_user_id: Current user ID
        """
        super().__init__(parent)
        self.customer_data = customer_data
        self.customer_service = customer_service
        self.current_user_id = current_user_id
        self.is_edit_mode = customer_data is not None

        self._setup_ui()
        self._load_data() if customer_data else self._set_defaults()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Thêm khách hàng mới" if not self.is_edit_mode else "Sửa thông tin khách hàng")
        self.setMinimumSize(700, 800)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Customer type selection
        self._setup_type_section(content_layout)

        # Personal info section
        self._setup_personal_section(content_layout)

        # Business info section (hidden by default)
        self._setup_business_section(content_layout)

        # Contact info section
        self._setup_contact_section(content_layout)

        # Classification section
        self._setup_classification_section(content_layout)

        # Notes section
        self._setup_notes_section(content_layout)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Buttons
        self._setup_buttons(layout)

    def _setup_type_section(self, parent_layout):
        """Setup customer type selection."""
        group = QGroupBox("Loại khách hàng")
        layout = QHBoxLayout(group)

        self.type_group = QButtonGroup(self)

        self.individual_radio = QRadioButton("Cá nhân")
        self.business_radio = QRadioButton("Doanh nghiệp")
        self.individual_radio.setChecked(True)

        self.type_group.addButton(self.individual_radio)
        self.type_group.addButton(self.business_radio)

        layout.addWidget(self.individual_radio)
        layout.addWidget(self.business_radio)
        layout.addStretch()

        parent_layout.addWidget(group)

        # Connect toggle
        self.individual_radio.toggled.connect(self._on_type_changed)

    def _setup_personal_section(self, parent_layout):
        """Setup personal info section."""
        self.personal_group = QGroupBox("Thông tin cá nhân")
        layout = QFormLayout(self.personal_group)
        layout.setSpacing(10)

        # Full name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Họ và tên đầy đủ")
        layout.addRow("Họ tên *:", self.full_name_input)

        # ID Card
        self.id_card_input = QLineEdit()
        self.id_card_input.setPlaceholderText("Số CMND/CCCD")
        layout.addRow("CMND/CCCD:", self.id_card_input)

        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate().addYears(-25))
        self.dob_input.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Ngày sinh:", self.dob_input)

        # Gender
        gender_layout = QHBoxLayout()
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['Nam', 'Nữ', 'Khác'])
        gender_layout.addWidget(self.gender_combo)
        gender_layout.addStretch()
        layout.addRow("Giới tính:", gender_layout)

        parent_layout.addWidget(self.personal_group)

    def _setup_business_section(self, parent_layout):
        """Setup business info section."""
        self.business_group = QGroupBox("Thông tin doanh nghiệp")
        layout = QFormLayout(self.business_group)
        layout.setSpacing(10)

        # Company name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Tên công ty")
        layout.addRow("Tên công ty *:", self.company_name_input)

        # Tax code
        self.tax_code_input = QLineEdit()
        self.tax_code_input.setPlaceholderText("Mã số thuế (10 hoặc 13 số)")
        layout.addRow("Mã số thuế:", self.tax_code_input)

        # Business registration
        self.business_reg_input = QLineEdit()
        self.business_reg_input.setPlaceholderText("Số đăng ký kinh doanh")
        layout.addRow("Số ĐKKD:", self.business_reg_input)

        self.business_group.setVisible(False)
        parent_layout.addWidget(self.business_group)

    def _setup_contact_section(self, parent_layout):
        """Setup contact info section."""
        group = QGroupBox("Thông tin liên hệ")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Số điện thoại chính")
        layout.addRow("Điện thoại *:", self.phone_input)

        # Phone 2
        self.phone2_input = QLineEdit()
        self.phone2_input.setPlaceholderText("Số điện thoại phụ (không bắt buộc)")
        layout.addRow("Điện thoại 2:", self.phone2_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        layout.addRow("Email:", self.email_input)

        # Address
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Địa chỉ đầy đủ")
        layout.addRow("Địa chỉ:", self.address_input)

        # Province/District/Ward
        location_layout = QHBoxLayout()
        self.province_input = QLineEdit()
        self.province_input.setPlaceholderText("Tỉnh/TP")
        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("Quận/Huyện")
        self.ward_input = QLineEdit()
        self.ward_input.setPlaceholderText("Phường/Xã")

        location_layout.addWidget(self.province_input)
        location_layout.addWidget(self.district_input)
        location_layout.addWidget(self.ward_input)

        layout.addRow("Tỉnh/Quận/Phường:", location_layout)

        parent_layout.addWidget(group)

    def _setup_classification_section(self, parent_layout):
        """Setup classification section."""
        group = QGroupBox("Phân loại")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Customer class
        self.class_combo = QComboBox()
        for code, name in self.CUSTOMER_CLASSES:
            self.class_combo.addItem(name, code)
        layout.addRow("Phân loại:", self.class_combo)

        # Source
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.SOURCES)
        self.source_combo.setEditable(True)
        layout.addRow("Nguồn:", self.source_combo)

        parent_layout.addWidget(group)

    def _setup_notes_section(self, parent_layout):
        """Setup notes section."""
        group = QGroupBox("Ghi chú")
        layout = QVBoxLayout(group)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Nhập ghi chú về khách hàng...")
        self.notes_input.setMaximumHeight(100)
        layout.addWidget(self.notes_input)

        parent_layout.addWidget(group)

    def _setup_buttons(self, parent_layout):
        """Setup action buttons."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("💾 Lưu")
        self.save_btn.setDefault(True)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        parent_layout.addLayout(button_layout)

    def _on_type_changed(self, checked):
        """Handle customer type change."""
        is_business = not checked  # individual_radio toggled
        self.business_group.setVisible(is_business)
        self.personal_group.setTitle(
            "Thông tin người đại diện" if is_business else "Thông tin cá nhân"
        )

    def _set_defaults(self):
        """Set default values for new customer."""
        self.class_combo.setCurrentIndex(0)  # regular
        self.source_combo.setCurrentIndex(0)  # Facebook

    def _load_data(self):
        """Load existing customer data."""
        if not self.customer_data:
            return

        # Type
        if self.customer_data.get('customer_type') == 'business':
            self.business_radio.setChecked(True)
        else:
            self.individual_radio.setChecked(True)

        # Personal info
        self.full_name_input.setText(self.customer_data.get('full_name', ''))
        self.id_card_input.setText(self.customer_data.get('id_card', '') or '')

        if self.customer_data.get('date_of_birth'):
            try:
                dob = self.customer_data['date_of_birth']
                if isinstance(dob, str):
                    from datetime import datetime
                    dob = datetime.strptime(dob, '%Y-%m-%d').date()
                self.dob_input.setDate(QDate(dob.year, dob.month, dob.day))
            except:
                pass

        gender = self.customer_data.get('gender', 'Nam')
        self.gender_combo.setCurrentText(gender)

        # Business info
        self.company_name_input.setText(self.customer_data.get('company_name', '') or '')
        self.tax_code_input.setText(self.customer_data.get('tax_code', '') or '')
        self.business_reg_input.setText(self.customer_data.get('business_registration', '') or '')

        # Contact info
        self.phone_input.setText(self.customer_data.get('phone', '') or '')
        self.phone2_input.setText(self.customer_data.get('phone2', '') or '')
        self.email_input.setText(self.customer_data.get('email', '') or '')
        self.address_input.setText(self.customer_data.get('address', '') or '')
        self.province_input.setText(self.customer_data.get('province', '') or '')
        self.district_input.setText(self.customer_data.get('district', '') or '')
        self.ward_input.setText(self.customer_data.get('ward', '') or '')

        # Classification
        customer_class = self.customer_data.get('customer_class', 'regular')
        for i, (code, _) in enumerate(self.CUSTOMER_CLASSES):
            if code == customer_class:
                self.class_combo.setCurrentIndex(i)
                break

        source = self.customer_data.get('source', 'Facebook')
        self.source_combo.setCurrentText(source)

        # Notes
        self.notes_input.setText(self.customer_data.get('notes', '') or '')

    def _validate(self) -> bool:
        """Validate form data.

        Returns:
            bool: True if valid
        """
        errors = []

        # Required fields
        if not self.full_name_input.text().strip():
            errors.append("Họ tên không được để trống")

        if not self.phone_input.text().strip():
            errors.append("Số điện thoại không được để trống")

        # Business validation
        if self.business_radio.isChecked() and not self.company_name_input.text().strip():
            errors.append("Tên công ty không được để trống với khách hàng doanh nghiệp")

        if errors:
            QMessageBox.warning(self, "Lỗi validation", "\n".join(errors))
            return False

        return True

    def _on_save(self):
        """Handle save button click."""
        if not self._validate():
            return

        # Gather data
        data = {
            'customer_type': 'business' if self.business_radio.isChecked() else 'individual',
            'full_name': self.full_name_input.text().strip(),
            'id_card': self.id_card_input.text().strip() or None,
            'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
            'gender': self.gender_combo.currentText(),
            'company_name': self.company_name_input.text().strip() or None,
            'tax_code': self.tax_code_input.text().strip() or None,
            'business_registration': self.business_reg_input.text().strip() or None,
            'phone': self.phone_input.text().strip(),
            'phone2': self.phone2_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'address': self.address_input.text().strip() or None,
            'province': self.province_input.text().strip() or None,
            'district': self.district_input.text().strip() or None,
            'ward': self.ward_input.text().strip() or None,
            'customer_class': self.class_combo.currentData(),
            'source': self.source_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip() or None
        }

        # Remove None values for cleaner data
        data = {k: v for k, v in data.items() if v is not None}

        try:
            if self.is_edit_mode and self.customer_service:
                self.customer_service.update_customer(
                    self.customer_data['id'],
                    data,
                    self.current_user_id
                )
            elif self.customer_service:
                self.customer_service.create_customer(data, self.current_user_id)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def get_data(self) -> Dict[str, Any]:
        """Get form data.

        Returns:
            Dictionary of customer data
        """
        return {
            'customer_type': 'business' if self.business_radio.isChecked() else 'individual',
            'full_name': self.full_name_input.text().strip(),
            'id_card': self.id_card_input.text().strip() or None,
            'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
            'gender': self.gender_combo.currentText(),
            'company_name': self.company_name_input.text().strip() or None,
            'tax_code': self.tax_code_input.text().strip() or None,
            'business_registration': self.business_reg_input.text().strip() or None,
            'phone': self.phone_input.text().strip(),
            'phone2': self.phone2_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'address': self.address_input.text().strip() or None,
            'province': self.province_input.text().strip() or None,
            'district': self.district_input.text().strip() or None,
            'ward': self.ward_input.text().strip() or None,
            'customer_class': self.class_combo.currentData(),
            'source': self.source_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip() or None
        }
