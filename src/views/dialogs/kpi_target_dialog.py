"""
KPI Target Setting Dialog for setting employee KPI targets.
Sprint 0.4: Employee KPI
"""

from typing import Optional, List
from decimal import Decimal

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QDialogButtonBox, QFormLayout, QGroupBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.repositories.kpi_repository import KPITargetRepository
from src.repositories.user_repository import UserRepository
from src.services.kpi_service import KPIService


class TargetSettingDialog(QDialog):
    """Dialog for setting KPI targets for employees."""

    targets_updated = pyqtSignal()  # Emitted when targets are updated

    def __init__(
        self,
        kpi_service: KPIService,
        user_repo: UserRepository,
        target_repo: KPITargetRepository,
        current_user_id: int,
        parent=None
    ):
        super().__init__(parent)
        self.kpi_service = kpi_service
        self.user_repo = user_repo
        self.target_repo = target_repo
        self.current_user_id = current_user_id

        self._setup_ui()
        self._load_employees()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Thiết lập mục tiêu KPI")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        title = QLabel("Thiết lập mục tiêu KPI")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Filter section
        filter_group = QGroupBox("Lọc")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Kỳ:"))
        self.period_combo = QComboBox()
        self._populate_periods()
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        filter_layout.addWidget(self.period_combo)

        filter_layout.addStretch()

        layout.addWidget(filter_group)

        # Split view: Employees list | Target form
        content_layout = QHBoxLayout()

        # Left: Employees table
        left_group = QGroupBox("Nhân viên")
        left_layout = QVBoxLayout(left_group)

        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(3)
        self.employees_table.setHorizontalHeaderLabels([
            "Nhân viên", "Mục tiêu xe", "Mục tiêu doanh thu"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.employees_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.employees_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.employees_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.employees_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f5f5f7;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e5e5e5;
            }
            QTableWidget::item:selected {
                background-color: #007aff;
                color: white;
            }
        """)

        left_layout.addWidget(self.employees_table)
        content_layout.addWidget(left_group, 2)

        # Right: Target form
        right_group = QGroupBox("Mục tiêu")
        self.target_form_layout = QFormLayout(right_group)
        self.target_form_layout.setSpacing(12)

        # Employee name (read-only)
        self.employee_label = QLabel("--")
        self.employee_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.target_form_layout.addRow("Nhân viên:", self.employee_label)

        # Period type
        self.period_type_combo = QComboBox()
        self.period_type_combo.addItem("Hàng tháng", "monthly")
        self.period_type_combo.addItem("Hàng quý", "quarterly")
        self.period_type_combo.addItem("Hàng năm", "yearly")
        self.target_form_layout.addRow("Loại kỳ:", self.period_type_combo)

        # Sales target
        self.sales_target_spin = QSpinBox()
        self.sales_target_spin.setRange(0, 9999)
        self.sales_target_spin.setSuffix(" xe")
        self.target_form_layout.addRow("Mục tiêu bán xe:", self.sales_target_spin)

        # Revenue target
        self.revenue_target_spin = QDoubleSpinBox()
        self.revenue_target_spin.setRange(0, 999999999999)
        self.revenue_target_spin.setDecimals(0)
        self.revenue_target_spin.setSuffix(" VNĐ")
        self.revenue_target_spin.setGroupSeparatorShown(True)
        self.target_form_layout.addRow("Mục tiêu doanh thu:", self.revenue_target_spin)

        # New customer target
        self.customer_target_spin = QSpinBox()
        self.customer_target_spin.setRange(0, 9999)
        self.customer_target_spin.setSuffix(" KH")
        self.target_form_layout.addRow("Mục tiêu KH mới:", self.customer_target_spin)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Mô tả thêm về mục tiêu...")
        self.description_edit.setMaximumHeight(80)
        self.target_form_layout.addRow("Mô tả:", self.description_edit)

        # Save button
        self.save_btn = QPushButton("Lưu mục tiêu")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.clicked.connect(self._save_target)
        self.target_form_layout.addRow(self.save_btn)

        # Apply to all button
        self.apply_all_btn = QPushButton("Áp dụng cho tất cả")
        self.apply_all_btn.setObjectName("secondaryButton")
        self.apply_all_btn.clicked.connect(self._apply_to_all)
        self.target_form_layout.addRow(self.apply_all_btn)

        content_layout.addWidget(right_group, 1)

        layout.addLayout(content_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignRight)

        # Styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#primaryButton {
                background-color: #007aff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton#primaryButton:hover {
                background-color: #0056cc;
            }
            QPushButton#secondaryButton {
                background-color: #e5e5e5;
                color: #333;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton#secondaryButton:hover {
                background-color: #d1d1d6;
            }
            QSpinBox, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                background-color: white;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                background-color: white;
            }
        """)

        # Initially disable form
        self._set_form_enabled(False)

    def _populate_periods(self):
        """Populate period dropdown."""
        from datetime import date
        today = date.today()
        for i in range(12):
            year = today.year
            month = today.month - i
            if month <= 0:
                year -= 1
                month += 12
            self.period_combo.addItem(f"{year}-{month:02d}")

    def _load_employees(self):
        """Load employees and their targets."""
        period = self.period_combo.currentText()

        # Get all employees with Sales role
        employees = self.user_repo.search(role_id=3)  # Sales role

        self.employees_table.setRowCount(len(employees))
        self.employee_targets = {}  # Cache targets

        for row, emp in enumerate(employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(emp.full_name))

            # Get target for this period
            target = self.target_repo.get_by_user_and_period(
                emp.id, 'monthly', period
            )

            if target:
                self.employees_table.setItem(
                    row, 1, QTableWidgetItem(str(target['sales_target']))
                )
                self.employees_table.setItem(
                    row, 2, QTableWidgetItem(f"{target['revenue_target']:,.0f}")
                )
                self.employee_targets[emp.id] = target
            else:
                self.employees_table.setItem(row, 1, QTableWidgetItem("--"))
                self.employees_table.setItem(row, 2, QTableWidgetItem("--"))

            # Store employee ID
            self.employees_table.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, emp.id
            )

    def _on_period_changed(self):
        """Handle period change."""
        self._load_employees()

    def _on_selection_changed(self):
        """Handle employee selection change."""
        selected = self.employees_table.selectedItems()
        if not selected:
            self._set_form_enabled(False)
            return

        # Get employee ID
        row = selected[0].row()
        emp_id = self.employees_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        emp_name = self.employees_table.item(row, 0).text()

        self.current_employee_id = emp_id
        self.employee_label.setText(emp_name)

        # Load existing target if any
        period = self.period_combo.currentText()
        target = self.target_repo.get_by_user_and_period(
            emp_id, 'monthly', period
        )

        if target:
            self.sales_target_spin.setValue(target['sales_target'])
            self.revenue_target_spin.setValue(float(target['revenue_target']))
            self.customer_target_spin.setValue(target.get('new_customer_target', 0))
            self.description_edit.setPlainText(target.get('description', ''))
        else:
            self.sales_target_spin.setValue(0)
            self.revenue_target_spin.setValue(0)
            self.customer_target_spin.setValue(0)
            self.description_edit.clear()

        self._set_form_enabled(True)

    def _set_form_enabled(self, enabled: bool):
        """Enable/disable form controls."""
        self.period_type_combo.setEnabled(enabled)
        self.sales_target_spin.setEnabled(enabled)
        self.revenue_target_spin.setEnabled(enabled)
        self.customer_target_spin.setEnabled(enabled)
        self.description_edit.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.apply_all_btn.setEnabled(enabled)

    def _save_target(self):
        """Save target for selected employee."""
        if not hasattr(self, 'current_employee_id'):
            return

        period_type = self.period_type_combo.currentData()
        target_period = self.period_combo.currentText()

        try:
            self.kpi_service.set_kpi_target(
                user_id=self.current_employee_id,
                period_type=period_type,
                target_period=target_period,
                sales_target=self.sales_target_spin.value(),
                revenue_target=Decimal(str(self.revenue_target_spin.value())),
                new_customer_target=self.customer_target_spin.value(),
                description=self.description_edit.toPlainText() or None,
                created_by=self.current_user_id
            )

            QMessageBox.information(self, "Thành công", "Đã lưu mục tiêu KPI")
            self._load_employees()  # Refresh
            self.targets_updated.emit()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu mục tiêu: {str(e)}")

    def _apply_to_all(self):
        """Apply current target settings to all employees."""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Áp dụng mục tiêu này cho tất cả nhân viên?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        period_type = self.period_type_combo.currentData()
        target_period = self.period_combo.currentText()

        # Get all employee IDs
        employee_ids = []
        for row in range(self.employees_table.rowCount()):
            emp_id = self.employees_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            employee_ids.append(emp_id)

        try:
            data = {
                'period_type': period_type,
                'target_period': target_period,
                'sales_target': self.sales_target_spin.value(),
                'revenue_target': Decimal(str(self.revenue_target_spin.value())),
                'new_customer_target': self.customer_target_spin.value(),
                'description': self.description_edit.toPlainText() or None
            }

            self.target_repo.set_bulk_targets(employee_ids, data)

            QMessageBox.information(
                self, "Thành công",
                f"Đã áp dụng mục tiêu cho {len(employee_ids)} nhân viên"
            )
            self._load_employees()
            self.targets_updated.emit()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể áp dụng: {str(e)}")
