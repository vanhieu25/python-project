"""
Classification Report Module
Dialog for displaying customer classification statistics.
"""

from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt


class ClassificationReportDialog(QDialog):
    """Dialog for displaying classification report."""

    def __init__(self, parent=None, db_helper=None):
        """Initialize dialog.

        Args:
            parent: Parent widget
            db_helper: Database helper instance
        """
        super().__init__(parent)
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

        self.report_data = None

        self._setup_ui()
        self._load_report()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("📊 Báo cáo phân loại khách hàng")
        self.setMinimumSize(600, 500)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header = QLabel("📊 Báo cáo phân loại khách hàng")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1d1d1f;")
        layout.addWidget(header)

        # Summary cards
        self._setup_summary_cards(layout)

        # Details table
        self._setup_details_table(layout)

        # Average values
        self._setup_avg_section(layout)

        # Buttons
        self._setup_buttons(layout)

        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
            }
            QLabel {
                color: #1d1d1f;
            }
            QTableWidget {
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f7;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #d1d1d6;
            }
        """)

    def _setup_summary_cards(self, parent_layout):
        """Setup summary cards.

        Args:
            parent_layout: Parent layout
        """
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # VIP card
        self.vip_card = self._create_summary_card("⭐ VIP", "0", "#ff9500")
        cards_layout.addWidget(self.vip_card)

        # Regular card
        self.regular_card = self._create_summary_card("● Regular", "0", "#0071e3")
        cards_layout.addWidget(self.regular_card)

        # Potential card
        self.potential_card = self._create_summary_card("○ Potential", "0", "#8e8e93")
        cards_layout.addWidget(self.potential_card)

        parent_layout.addLayout(cards_layout)

    def _create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card.

        Args:
            title: Card title
            value: Card value
            color: Accent color

        Returns:
            Card frame
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666666;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        setattr(self, f"{title.replace(' ', '_').lower()}_count", value_label)
        layout.addWidget(value_label)

        return card

    def _setup_details_table(self, parent_layout):
        """Setup details table.

        Args:
            parent_layout: Parent layout
        """
        group = QLabel("📋 Chi tiết phân loại")
        group.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(group)

        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels([
            "Phân loại", "Số lượng", "Tỷ lệ", "Tổng giá trị"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.details_table.setMaximumHeight(150)
        parent_layout.addWidget(self.details_table)

    def _setup_avg_section(self, parent_layout):
        """Setup average values section.

        Args:
            parent_layout: Parent layout
        """
        self.avg_label = QLabel("📈 Giá trị trung bình theo phân loại:")
        self.avg_label.setStyleSheet("font-size: 14px; color: #666666; margin-top: 10px;")
        parent_layout.addWidget(self.avg_label)

        avg_widget = QFrame()
        avg_layout = QHBoxLayout(avg_widget)
        avg_layout.setSpacing(30)

        self.vip_avg = QLabel("VIP: -")
        self.vip_avg.setStyleSheet("font-size: 14px; color: #ff9500;")
        avg_layout.addWidget(self.vip_avg)

        self.regular_avg = QLabel("Regular: -")
        self.regular_avg.setStyleSheet("font-size: 14px; color: #0071e3;")
        avg_layout.addWidget(self.regular_avg)

        self.potential_avg = QLabel("Potential: -")
        self.potential_avg.setStyleSheet("font-size: 14px; color: #8e8e93;")
        avg_layout.addWidget(self.potential_avg)

        avg_layout.addStretch()
        parent_layout.addWidget(avg_widget)

    def _setup_buttons(self, parent_layout):
        """Setup buttons.

        Args:
            parent_layout: Parent layout
        """
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Làm mới")
        self.refresh_btn.clicked.connect(self._load_report)
        btn_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("📥 Export")
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)

        self.close_btn = QPushButton("Đóng")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        parent_layout.addLayout(btn_layout)

    def _load_report(self):
        """Load classification report."""
        if not self.classification_service:
            return

        self.report_data = self.classification_service.get_classification_report()
        self._update_ui()

    def _update_ui(self):
        """Update UI with report data."""
        if not self.report_data:
            return

        summary = self.report_data['summary']
        total = self.report_data['total_customers']

        # Update cards
        self._update_card_value(self.vip_card, summary['vip']['count'])
        self._update_card_value(self.regular_card, summary['regular']['count'])
        self._update_card_value(self.potential_card, summary['potential']['count'])

        # Update details table
        self._update_details_table(summary, total)

        # Update averages
        self.vip_avg.setText(f"VIP: {self._format_amount(summary['vip']['avg_value'])}")
        self.regular_avg.setText(f"Regular: {self._format_amount(summary['regular']['avg_value'])}")
        self.potential_avg.setText(f"Potential: {self._format_amount(summary['potential']['avg_value'])}")

    def _update_card_value(self, card: QFrame, value: int):
        """Update card value.

        Args:
            card: Card frame
            value: New value
        """
        layout = card.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.styleSheet().startswith("font-size: 36px"):
                widget.setText(str(value))
                break

    def _update_details_table(self, summary: Dict, total: int):
        """Update details table.

        Args:
            summary: Summary data
            total: Total customers
        """
        self.details_table.setRowCount(3)

        classes = [
            ('vip', '⭐ VIP'),
            ('regular', '● Regular'),
            ('potential', '○ Potential')
        ]

        for i, (key, display) in enumerate(classes):
            # Class
            self.details_table.setItem(i, 0, QTableWidgetItem(display))

            # Count
            count = summary[key]['count']
            self.details_table.setItem(i, 1, QTableWidgetItem(str(count)))

            # Percentage
            pct = (count / total * 100) if total > 0 else 0
            self.details_table.setItem(i, 2, QTableWidgetItem(f"{pct:.1f}%"))

            # Total value
            value = summary[key]['total_value']
            self.details_table.setItem(i, 3, QTableWidgetItem(self._format_amount(value)))

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
        elif amount == 0:
            return "0"
        else:
            return f"{amount:,.0f}"

    def _on_export(self):
        """Handle export button."""
        if not self.report_data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để export")
            return

        # Simple text export for now
        import os
        from datetime import datetime

        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(exports_dir, f'classification_report_{timestamp}.txt')

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("BÁO CÁO PHÂN LOẠI KHÁCH HÀNG\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Tổng số khách hàng: {self.report_data['total_customers']}\n\n")

                f.write("Chi tiết:\n")
                f.write("-" * 40 + "\n")

                summary = self.report_data['summary']
                for key, name in [('vip', 'VIP'), ('regular', 'Regular'), ('potential', 'Potential')]:
                    data = summary[key]
                    f.write(f"\n{name}:\n")
                    f.write(f"  Số lượng: {data['count']}\n")
                    f.write(f"  Tổng giá trị: {self._format_amount(data['total_value'])}\n")
                    f.write(f"  Giá trị TB: {self._format_amount(data['avg_value'])}\n")

            QMessageBox.information(
                self,
                "Export thành công",
                f"Báo cáo đã được lưu tại:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể export: {str(e)}")
