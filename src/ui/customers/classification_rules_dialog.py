"""
Classification Rules Dialog Module
Dialog for managing customer classification rules.
"""

from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt


class RuleEditDialog(QDialog):
    """Dialog for editing a classification rule."""

    CLASS_OPTIONS = [
        ('vip', 'VIP'),
        ('regular', 'Regular'),
        ('potential', 'Potential')
    ]

    def __init__(self, rule_data: Optional[Dict] = None, parent=None):
        """Initialize dialog.

        Args:
            rule_data: Existing rule data for editing
            parent: Parent widget
        """
        super().__init__(parent)
        self.rule_data = rule_data
        self.is_edit = rule_data is not None

        self._setup_ui()

        if rule_data:
            self._load_data()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Sửa quy tắc" if self.is_edit else "Thêm quy tắc")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Rule name
        layout.addWidget(QLabel("Tên quy tắc:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ví dụ: VIP - High Value")
        layout.addWidget(self.name_input)

        # Customer class
        layout.addWidget(QLabel("Phân loại:"))
        self.class_combo = QComboBox()
        for value, label in self.CLASS_OPTIONS:
            self.class_combo.addItem(label, value)
        layout.addWidget(self.class_combo)

        # Min contracts
        layout.addWidget(QLabel("Số hợp đồng tối thiểu:"))
        self.contracts_spin = QSpinBox()
        self.contracts_spin.setMinimum(0)
        self.contracts_spin.setMaximum(100)
        self.contracts_spin.setValue(0)
        layout.addWidget(self.contracts_spin)

        # Min total value
        layout.addWidget(QLabel("Tổng giá trị tối thiểu (triệu VNĐ):"))
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setMinimum(0)
        self.value_spin.setMaximum(10000)
        self.value_spin.setDecimals(0)
        self.value_spin.setValue(0)
        self.value_spin.setSingleStep(100)
        layout.addWidget(self.value_spin)

        # Active
        self.active_check = QCheckBox("Kích hoạt")
        self.active_check.setChecked(True)
        layout.addWidget(self.active_check)

        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _load_data(self):
        """Load existing rule data."""
        self.name_input.setText(self.rule_data.get('rule_name', ''))

        class_value = self.rule_data.get('customer_class', 'potential')
        for i, (value, _) in enumerate(self.CLASS_OPTIONS):
            if value == class_value:
                self.class_combo.setCurrentIndex(i)
                break

        self.contracts_spin.setValue(self.rule_data.get('min_contracts', 0))

        value = self.rule_data.get('min_total_value', 0)
        self.value_spin.setValue(value / 1000000)  # Convert to millions

        self.active_check.setChecked(self.rule_data.get('is_active', True))

    def get_data(self) -> Dict[str, Any]:
        """Get rule data from form.

        Returns:
            Rule data dictionary
        """
        return {
            'rule_name': self.name_input.text().strip(),
            'customer_class': self.class_combo.currentData(),
            'min_contracts': self.contracts_spin.value(),
            'min_total_value': int(self.value_spin.value() * 1000000),  # Convert to VNĐ
            'is_active': self.active_check.isChecked()
        }


class ClassificationRulesDialog(QDialog):
    """Dialog for managing classification rules."""

    def __init__(self, parent=None, db_helper=None):
        """Initialize dialog.

        Args:
            parent: Parent widget
            db_helper: Database helper instance
        """
        super().__init__(parent)
        self.db_helper = db_helper

        # Initialize services
        if db_helper:
            from ..repositories.customer_classification_repository import CustomerClassificationRepository
            from ..services.customer_classification_service import ClassificationRuleManager

            classification_repo = CustomerClassificationRepository(db_helper)
            self.rule_manager = ClassificationRuleManager(classification_repo)
        else:
            self.rule_manager = None

        self._setup_ui()
        self._load_rules()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("⚙️ Quản lý quy tắc phân loại")
        self.setMinimumSize(700, 500)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("⚙️ Quản lý quy tắc phân loại")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Ưu tiên", "Tên quy tắc", "Phân loại", "Điều kiện", "Trạng thái"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.rules_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f7;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #d1d1d6;
            }
        """)
        layout.addWidget(self.rules_table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Thêm quy tắc")
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Sửa")
        self.edit_btn.clicked.connect(self._on_edit)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ Xóa")
        self.delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.run_btn = QPushButton("🔄 Chạy phân loại")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #34c759;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        self.run_btn.clicked.connect(self._on_run_classification)
        btn_layout.addWidget(self.run_btn)

        self.close_btn = QPushButton("Đóng")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)

    def _load_rules(self):
        """Load classification rules."""
        if not self.rule_manager:
            return

        rules = self.rule_manager.get_rules()

        self.rules_table.setRowCount(len(rules))

        for i, rule in enumerate(rules):
            # Priority
            priority_item = QTableWidgetItem(str(rule.priority))
            priority_item.setData(Qt.ItemDataRole.UserRole, rule.id)
            priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rules_table.setItem(i, 0, priority_item)

            # Rule name
            self.rules_table.setItem(i, 1, QTableWidgetItem(rule.rule_name))

            # Customer class
            class_display = {
                'vip': '⭐ VIP',
                'regular': '● Regular',
                'potential': '○ Potential'
            }.get(rule.customer_class, rule.customer_class)
            self.rules_table.setItem(i, 2, QTableWidgetItem(class_display))

            # Condition
            condition = self._format_condition(rule)
            self.rules_table.setItem(i, 3, QTableWidgetItem(condition))

            # Status
            status = "Kích hoạt" if getattr(rule, 'is_active', True) else "Vô hiệu"
            self.rules_table.setItem(i, 4, QTableWidgetItem(status))

    def _format_condition(self, rule) -> str:
        """Format rule condition.

        Args:
            rule: Classification rule

        Returns:
            Formatted condition string
        """
        parts = []

        if rule.min_contracts > 0:
            parts.append(f"≥{rule.min_contracts} hợp đồng")

        if rule.min_total_value > 0:
            value = rule.min_total_value / 1000000
            parts.append(f"≥{value:.0f} triệu")

        if not parts:
            return "Mặc định"

        return " HOẶC ".join(parts)

    def _get_selected_rule_id(self) -> Optional[int]:
        """Get selected rule ID.

        Returns:
            Rule ID or None
        """
        selected = self.rules_table.selectedItems()
        if not selected:
            return None

        row = selected[0].row()
        return self.rules_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _on_add(self):
        """Handle add button."""
        dialog = RuleEditDialog(parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            if not data['rule_name']:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên quy tắc")
                return

            try:
                self.rule_manager.create_rule(data)
                self._load_rules()
                QMessageBox.information(self, "Thành công", "Đã thêm quy tắc mới")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm quy tắc: {str(e)}")

    def _on_edit(self):
        """Handle edit button."""
        rule_id = self._get_selected_rule_id()
        if not rule_id:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn quy tắc để sửa")
            return

        rule = self.rule_manager.get_rule_by_id(rule_id)
        if not rule:
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy quy tắc")
            return

        dialog = RuleEditDialog(rule_data={
            'rule_name': rule.rule_name,
            'customer_class': rule.customer_class,
            'min_contracts': rule.min_contracts,
            'min_total_value': rule.min_total_value,
            'is_active': getattr(rule, 'is_active', True)
        }, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            if not data['rule_name']:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên quy tắc")
                return

            try:
                self.rule_manager.update_rule(rule_id, data)
                self._load_rules()
                QMessageBox.information(self, "Thành công", "Đã cập nhật quy tắc")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật: {str(e)}")

    def _on_delete(self):
        """Handle delete button."""
        rule_id = self._get_selected_rule_id()
        if not rule_id:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn quy tắc để xóa")
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa quy tắc này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.rule_manager.delete_rule(rule_id)
                self._load_rules()
                QMessageBox.information(self, "Thành công", "Đã xóa quy tắc")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {str(e)}")

    def _on_run_classification(self):
        """Handle run classification button."""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Chạy phân loại cho tất cả khách hàng?\n\n"
            "Thao tác này có thể thay đổi phân loại của nhiều khách hàng.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                from ..repositories.customer_repository import CustomerRepository
                from ..repositories.customer_classification_repository import CustomerClassificationRepository
                from ..services.customer_classification_service import CustomerClassificationService

                customer_repo = CustomerRepository(self.db_helper)
                classification_repo = CustomerClassificationRepository(self.db_helper)
                service = CustomerClassificationService(customer_repo, classification_repo)

                stats = service.classify_all_customers()

                QMessageBox.information(
                    self,
                    "Hoàn thành",
                    f"Đã phân loại {sum(stats.values()) - stats['changed']} khách hàng\n"
                    f"Thay đổi: {stats['changed']}\n\n"
                    f"VIP: {stats['vip']}\n"
                    f"Regular: {stats['regular']}\n"
                    f"Potential: {stats['potential']}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể chạy phân loại: {str(e)}")
