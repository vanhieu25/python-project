"""
Car Management Views - PyQt6 Implementation
============================================
Module quản lý xe với PyQt6 (chuyển đổi từ tkinter)
Sprint 1: Car Management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QGroupBox, QSplitter, QTextEdit, QMenu,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from typing import Optional, List

from ...models.car import Car
from ...repositories.car_repository import CarRepository
from ...database.db_helper import DatabaseHelper


class CarDialog(QDialog):
    """Dialog for adding/editing car."""

    car_saved = pyqtSignal()

    def __init__(self, db_helper: DatabaseHelper, car: Optional[Car] = None, parent=None):
        super().__init__(parent)
        self.db_helper = db_helper
        self.car_repo = CarRepository(db_helper)
        self.car = car

        self.setWindowTitle("Thêm xe mới" if car is None else "Chỉnh sửa xe")
        self.setMinimumWidth(500)
        self.setup_ui()

        if car:
            self.load_car_data()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form
        form_group = QGroupBox("Thông tin xe")
        form_layout = QFormLayout(form_group)

        # VIN
        self.vin_input = QLineEdit()
        self.vin_input.setMaxLength(17)
        self.vin_input.setPlaceholderText("VD: 1HGCM82633A123456")
        form_layout.addRow("VIN *:", self.vin_input)

        # License Plate
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("VD: 51A-12345")
        form_layout.addRow("Biển số:", self.plate_input)

        # Brand
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("VD: Toyota, Honda, BMW...")
        form_layout.addRow("Hãng xe *:", self.brand_input)

        # Model
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("VD: Camry, Civic, X5...")
        form_layout.addRow("Model *:", self.model_input)

        # Year
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2030)
        self.year_input.setValue(2024)
        form_layout.addRow("Năm SX *:", self.year_input)

        # Color
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("VD: Đen, Trắng, Đỏ...")
        form_layout.addRow("Màu sắc:", self.color_input)

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999999999)
        self.price_input.setDecimals(2)
        self.price_input.setGroupSeparatorShown(True)
        self.price_input.setSuffix(" VNĐ")
        form_layout.addRow("Giá bán *:", self.price_input)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItem("Còn hàng", "available")
        self.status_combo.addItem("Đã bán", "sold")
        self.status_combo.addItem("Đã đặt cọc", "reserved")
        self.status_combo.addItem("Bảo dưỡng", "maintenance")
        form_layout.addRow("Trạng thái:", self.status_combo)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Ghi chú thêm về xe...")
        form_layout.addRow("Ghi chú:", self.notes_input)

        layout.addWidget(form_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Lưu")
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        save_btn.clicked.connect(self.save_car)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def load_car_data(self):
        """Load existing car data for editing."""
        if not self.car:
            return

        self.vin_input.setText(self.car.vin or "")
        self.plate_input.setText(self.car.license_plate or "")
        self.brand_input.setText(self.car.brand or "")
        self.model_input.setText(self.car.model or "")
        self.year_input.setValue(self.car.year or 2024)
        self.color_input.setText(self.car.color or "")
        self.price_input.setValue(float(self.car.selling_price or 0))

        # Set status
        status_map = {
            'available': 0, 'sold': 1, 'reserved': 2, 'maintenance': 3
        }
        self.status_combo.setCurrentIndex(status_map.get(self.car.status, 0))

        self.notes_input.setPlainText(self.car.description or "")

        # Disable VIN for editing
        self.vin_input.setEnabled(False)

    def validate(self) -> bool:
        """Validate form data."""
        if not self.vin_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập VIN")
            self.vin_input.setFocus()
            return False

        if len(self.vin_input.text()) != 17:
            QMessageBox.warning(self, "Lỗi", "VIN phải có đúng 17 ký tự")
            self.vin_input.setFocus()
            return False

        if not self.brand_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập hãng xe")
            self.brand_input.setFocus()
            return False

        if not self.model_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập model xe")
            self.model_input.setFocus()
            return False

        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá bán hợp lệ")
            self.price_input.setFocus()
            return False

        return True

    def save_car(self):
        """Save car data."""
        if not self.validate():
            return

        car_data = {
            'vin': self.vin_input.text().strip().upper(),
            'license_plate': self.plate_input.text().strip() or None,
            'brand': self.brand_input.text().strip(),
            'model': self.model_input.text().strip(),
            'year': self.year_input.value(),
            'color': self.color_input.text().strip() or None,
            'purchase_price': self.price_input.value(),
            'selling_price': self.price_input.value(),
            'status': self.status_combo.currentData(),
            'description': self.notes_input.toPlainText().strip() or None
        }

        try:
            if self.car:
                # Update existing
                self.car_repo.update(self.car.id, car_data)
                QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin xe!")
            else:
                # Create new
                self.car_repo.create(car_data)
                QMessageBox.information(self, "Thành công", "Đã thêm xe mới!")

            self.car_saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu xe:\n{str(e)}")


class CarListWidget(QWidget):
    """Car list view with PyQt6."""

    def __init__(self, db_helper: DatabaseHelper, parent=None):
        super().__init__(parent)
        self.db_helper = db_helper
        self.car_repo = CarRepository(db_helper)

        self.setup_ui()
        self.load_cars()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("🚗 Quản Lý Xe")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Add button
        add_btn = QPushButton("➕ Thêm xe")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        add_btn.clicked.connect(self.add_car)
        header_layout.addWidget(add_btn)

        # Refresh button
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.load_cars)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Filter section
        filter_group = QGroupBox("Bộ lọc")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập VIN, biển số, hãng xe...")
        self.search_input.returnPressed.connect(self.load_cars)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Trạng thái:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tất cả", "all")
        self.status_filter.addItem("Còn hàng", "available")
        self.status_filter.addItem("Đã bán", "sold")
        self.status_filter.addItem("Đã đặt cọc", "reserved")
        self.status_filter.addItem("Bảo dưỡng", "maintenance")
        self.status_filter.currentIndexChanged.connect(self.load_cars)
        filter_layout.addWidget(self.status_filter)

        search_btn = QPushButton("🔍 Tìm kiếm")
        search_btn.clicked.connect(self.load_cars)
        filter_layout.addWidget(search_btn)

        layout.addWidget(filter_group)

        # Car table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "VIN", "Biển số", "Hãng xe", "Model",
            "Năm SX", "Màu sắc", "Giá bán", "Trạng thái"
        ])

        # Table settings
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Status bar
        self.status_label = QLabel("Sẵn sàng")
        layout.addWidget(self.status_label)

    def load_cars(self):
        """Load cars into table."""
        try:
            status = self.status_filter.currentData()
            search = self.search_input.text().strip()

            if status == "all":
                cars = self.car_repo.get_all()
            else:
                cars = self.car_repo.search_by_status(status)

            # Filter by search text
            if search:
                search_lower = search.lower()
                cars = [c for c in cars if (
                    search_lower in (c.vin or "").lower() or
                    search_lower in (c.license_plate or "").lower() or
                    search_lower in (c.brand or "").lower() or
                    search_lower in (c.model or "").lower()
                )]

            self.populate_table(cars)
            self.status_label.setText(f"Tổng số xe: {len(cars)}")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách xe:\n{str(e)}")

    def populate_table(self, cars: List[Car]):
        """Populate table with car data."""
        self.table.setRowCount(len(cars))

        status_map = {
            'available': ('🟢 Còn hàng', '#4caf50'),
            'sold': ('🔴 Đã bán', '#f44336'),
            'reserved': ('🟡 Đã đặt cọc', '#ff9800'),
            'maintenance': ('🔵 Bảo dưỡng', '#2196f3')
        }

        for row, car in enumerate(cars):
            self.table.setItem(row, 0, QTableWidgetItem(str(car.id)))
            self.table.setItem(row, 1, QTableWidgetItem(car.vin or ""))
            self.table.setItem(row, 2, QTableWidgetItem(car.license_plate or ""))
            self.table.setItem(row, 3, QTableWidgetItem(car.brand or ""))
            self.table.setItem(row, 4, QTableWidgetItem(car.model or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(car.year) if car.year else ""))
            self.table.setItem(row, 6, QTableWidgetItem(car.color or ""))

            price_item = QTableWidgetItem(
                f"{car.selling_price:,.0f} VNĐ" if car.selling_price else ""
            )
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 7, price_item)

            status_text, _ = status_map.get(car.status, (car.status, '#666'))
            self.table.setItem(row, 8, QTableWidgetItem(status_text))

        # Resize columns
        self.table.resizeColumnsToContents()

    def add_car(self):
        """Open dialog to add new car."""
        dialog = CarDialog(self.db_helper, parent=self)
        dialog.car_saved.connect(self.load_cars)
        dialog.exec()

    def edit_car(self, car_id: int):
        """Open dialog to edit car."""
        car = self.car_repo.get_by_id(car_id)
        if not car:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy xe!")
            return

        dialog = CarDialog(self.db_helper, car=car, parent=self)
        dialog.car_saved.connect(self.load_cars)
        dialog.exec()

    def delete_car(self, car_id: int):
        """Delete car after confirmation."""
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            "Bạn có chắc muốn xóa xe này?\nHành động này không thể hoàn tác.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.car_repo.soft_delete(car_id)
                QMessageBox.information(self, "Thành công", "Đã xóa xe!")
                self.load_cars()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa xe:\n{str(e)}")

    def show_context_menu(self, position):
        """Show context menu for table."""
        row = self.table.rowAt(position.y())
        if row < 0:
            return

        car_id = int(self.table.item(row, 0).text())

        menu = QMenu(self)

        edit_action = QAction("✏️ Chỉnh sửa", self)
        edit_action.triggered.connect(lambda: self.edit_car(car_id))
        menu.addAction(edit_action)

        delete_action = QAction("🗑️ Xóa", self)
        delete_action.triggered.connect(lambda: self.delete_car(car_id))
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))
