"""
Customer History Dialog Module
Dialog for viewing customer history and transaction information.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QMessageBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from .timeline_component import TimelineComponent
from ..services.customer_history_service import CustomerHistoryService
from ..repositories.customer_history_repository import CustomerHistoryRepository
from ..repositories.customer_repository import CustomerRepository


class CustomerHistoryDialog(QDialog):
    """Dialog for viewing customer history."""

    def __init__(self, customer_id: int, parent=None,
                 db_helper=None):
        """Initialize dialog.

        Args:
            customer_id: Customer ID to view history
            parent: Parent widget
            db_helper: Database helper instance
        """
        super().__init__(parent)
        self.customer_id = customer_id
        self.db_helper = db_helper

        # Initialize service
        if db_helper:
            history_repo = CustomerHistoryRepository(db_helper)
            customer_repo = CustomerRepository(db_helper)
            self.history_service = CustomerHistoryService(history_repo, customer_repo)
        else:
            self.history_service = None

        self.history_data = None

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Lịch sử khách hàng")
        self.setMinimumSize(1000, 700)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with customer info
        self._setup_header(layout)

        # Splitter for summary and timeline
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Summary
        left_panel = self._setup_summary_panel()
        splitter.addWidget(left_panel)

        # Right panel - Timeline
        right_panel = self._setup_timeline_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([350, 650])
        layout.addWidget(splitter)

        # Bottom buttons
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
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    def _setup_header(self, parent_layout):
        """Setup header with customer info.

        Args:
            parent_layout: Parent layout to add to
        """
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)

        self.title_label = QLabel("📋 Lịch sử khách hàng")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1d1d1f;
            }
        """)
        header_layout.addWidget(self.title_label)

        self.customer_info_label = QLabel()
        self.customer_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
            }
        """)
        header_layout.addWidget(self.customer_info_label)
        header_layout.addStretch()

        parent_layout.addWidget(header_widget)

    def _setup_summary_panel(self) -> QWidget:
        """Setup left panel with summary info.

        Returns:
            Summary panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 10, 0)

        # Overview group
        overview_group = QGroupBox("📊 Tổng quan")
        overview_layout = QGridLayout(overview_group)
        overview_layout.setSpacing(10)
        overview_layout.setContentsMargins(15, 20, 15, 15)

        # Summary labels
        self.contracts_label = QLabel("0")
        self.contracts_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #0071e3;")
        overview_layout.addWidget(QLabel("Tổng hợp đồng:"), 0, 0)
        overview_layout.addWidget(self.contracts_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.value_label = QLabel("0 VNĐ")
        self.value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #34c759;")
        overview_layout.addWidget(QLabel("Tổng giá trị:"), 1, 0)
        overview_layout.addWidget(self.value_label, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.last_transaction_label = QLabel("Chưa có")
        self.last_transaction_label.setStyleSheet("color: #666666;")
        overview_layout.addWidget(QLabel("Giao dịch cuối:"), 2, 0)
        overview_layout.addWidget(self.last_transaction_label, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.tier_label = QLabel("⭐ Potential")
        self.tier_label.setStyleSheet("font-weight: bold; color: #ff9500;")
        overview_layout.addWidget(QLabel("Phân loại:"), 3, 0)
        overview_layout.addWidget(self.tier_label, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addWidget(overview_group)

        # VIP Score group
        vip_group = QGroupBox("💎 VIP Score")
        vip_layout = QVBoxLayout(vip_group)
        vip_layout.setContentsMargins(15, 20, 15, 15)

        self.vip_score_label = QLabel("0")
        self.vip_score_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #0071e3;")
        self.vip_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vip_layout.addWidget(self.vip_score_label)

        self.vip_progress_label = QLabel("/100")
        self.vip_progress_label.setStyleSheet("color: #666666;")
        self.vip_progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vip_layout.addWidget(self.vip_progress_label)

        layout.addWidget(vip_group)

        # Export button
        self.export_btn = QPushButton("📥 Export")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        self.export_btn.clicked.connect(self._on_export)
        layout.addWidget(self.export_btn)

        layout.addStretch()
        return panel

    def _setup_timeline_panel(self) -> QWidget:
        """Setup right panel with timeline.

        Returns:
            Timeline panel widget
        """
        self.timeline_component = TimelineComponent("🕐 Timeline hoạt động")
        return self.timeline_component

    def _setup_buttons(self, parent_layout):
        """Setup bottom buttons.

        Args:
            parent_layout: Parent layout to add to
        """
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_data)
        btn_layout.addWidget(self.refresh_btn)

        self.close_btn = QPushButton("Đóng")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        parent_layout.addLayout(btn_layout)

    def _load_data(self):
        """Load customer history data."""
        if not self.history_service:
            self._show_error("History service not initialized")
            return

        self.history_data = self.history_service.get_full_history(self.customer_id)

        if not self.history_data:
            self._show_error("Không tìm thấy thông tin khách hàng")
            return

        self._update_ui()

    def _update_ui(self):
        """Update UI with loaded data."""
        customer = self.history_data['customer']
        summary = self.history_data['summary']
        timeline = self.history_data['timeline']

        # Update header
        self.customer_info_label.setText(
            f"{customer.full_name} ({customer.customer_code})"
        )

        # Update summary
        self.contracts_label.setText(str(summary['total_contracts']))
        self.value_label.setText(self._format_amount(summary['total_value']))

        if summary['last_transaction_date']:
            last_tx = summary['last_transaction_date']
            if isinstance(last_tx, str):
                self.last_transaction_label.setText(last_tx)
            else:
                self.last_transaction_label.setText(last_tx.strftime('%Y-%m-%d'))
        else:
            self.last_transaction_label.setText("Chưa có")

        # Get statistics
        stats = self.history_service.get_customer_statistics(self.customer_id)
        if stats:
            self.vip_score_label.setText(str(stats['vip_score']))
            tier = stats['tier']
            tier_emoji = '⭐' if tier == 'VIP' else '🔷' if tier == 'Regular' else '⚪'
            self.tier_label.setText(f"{tier_emoji} {tier}")

        # Update timeline
        self.timeline_component.set_items(timeline)

    def _format_amount(self, amount: float) -> str:
        """Format amount to Vietnamese currency.

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

    def _on_export(self):
        """Handle export button click."""
        if not self.history_service:
            self._show_error("History service not initialized")
            return

        # Show format selection dialog
        reply = QMessageBox.question(
            self,
            "Export",
            "Chọn định dạng export:\n\n"
            "Nhấn Yes để export CSV\n"
            "Nhấn No để export JSON",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        format_type = 'csv' if reply == QMessageBox.StandardButton.Yes else 'json'

        try:
            filepath = self.history_service.export_history(self.customer_id, format_type)
            if filepath:
                QMessageBox.information(
                    self,
                    "Export thành công",
                    f"File đã được lưu tại:\n{filepath}"
                )
            else:
                self._show_error("Export thất bại")
        except Exception as e:
            self._show_error(f"Lỗi export: {str(e)}")

    def _show_error(self, message: str):
        """Show error message.

        Args:
            message: Error message
        """
        QMessageBox.critical(self, "Lỗi", message)
