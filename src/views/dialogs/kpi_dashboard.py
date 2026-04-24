"""
KPI Dashboard Screen for employee performance tracking.
Sprint 0.4: Employee KPI
"""

from typing import Optional, List
from datetime import date
from decimal import Decimal

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget, QGroupBox, QSplitter,
    QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.repositories.kpi_repository import KPIRepository, KPITargetRepository
from src.repositories.user_repository import UserRepository
from src.services.kpi_service import KPIService
from src.services.authorization_service import require_permission
from src.models.kpi import KPIRecord, PerformanceSummary


class KPICard(QFrame):
    """Card widget for displaying KPI metric."""

    def __init__(self, title: str, value: str, subtitle: str = "",
                 color: str = "#007aff", parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setStyleSheet(f"""
            QFrame#kpiCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(self.title_label)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: {color};
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setStyleSheet("color: #999; font-size: 12px;")
            layout.addWidget(self.subtitle_label)

    def set_value(self, value: str):
        """Update card value."""
        self.value_label.setText(value)


class KPIDashboardScreen(QWidget):
    """Main KPI Dashboard screen."""

    def __init__(
        self,
        kpi_service: KPIService,
        user_repo: UserRepository,
        current_user_id: int,
        parent=None
    ):
        super().__init__(parent)
        self.kpi_service = kpi_service
        self.user_repo = user_repo
        self.current_user_id = current_user_id

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup the dashboard UI."""
        self.setObjectName("kpiDashboard")
        self.setStyleSheet("""
            QWidget#kpiDashboard {
                background-color: #f5f5f7;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("KPI Dashboard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Period selector
        header_layout.addWidget(QLabel("Kỳ:"))
        self.period_combo = QComboBox()
        self._populate_periods()
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        header_layout.addWidget(self.period_combo)

        # Refresh button
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self._load_data)
        header_layout.addWidget(refresh_btn)

        # Export button
        export_btn = QPushButton("Xuất báo cáo")
        export_btn.setObjectName("primaryButton")
        export_btn.clicked.connect(self._export_report)
        header_layout.addWidget(export_btn)

        main_layout.addLayout(header_layout)

        # Overview Cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.performance_card = KPICard(
            "Điểm hiệu suất",
            "--",
            color="#007aff"
        )
        cards_layout.addWidget(self.performance_card, 0, 0)

        self.cars_card = KPICard(
            "Xe bán được",
            "--",
            "Mục tiêu: --",
            color="#34c759"
        )
        cards_layout.addWidget(self.cars_card, 0, 1)

        self.revenue_card = KPICard(
            "Doanh thu",
            "--",
            "Mục tiêu: --",
            color="#ff9500"
        )
        cards_layout.addWidget(self.revenue_card, 0, 2)

        self.rank_card = KPICard(
            "Xếp hạng",
            "--",
            "Trong đội",
            color="#af52de"
        )
        cards_layout.addWidget(self.rank_card, 0, 3)

        main_layout.addLayout(cards_layout)

        # Content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Top Performers
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        performers_group = QGroupBox("Top Performers")
        performers_layout = QVBoxLayout(performers_group)

        self.performers_table = QTableWidget()
        self.performers_table.setColumnCount(5)
        self.performers_table.setHorizontalHeaderLabels([
            "Hạng", "Nhân viên", "Xe bán", "Doanh thu", "Điểm"
        ])
        self.performers_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.performers_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.performers_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
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
        """)

        performers_layout.addWidget(self.performers_table)
        left_layout.addWidget(performers_group)

        content_splitter.addWidget(left_widget)

        # Right: My KPI History
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        history_group = QGroupBox("Lịch sử KPI của tôi")
        history_layout = QVBoxLayout(history_group)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Kỳ", "Xe bán", "Tỷ lệ", "Doanh thu", "Tỷ lệ", "Điểm"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.history_table.setStyleSheet(self.performers_table.styleSheet())

        history_layout.addWidget(self.history_table)
        right_layout.addWidget(history_group)

        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([500, 500])

        main_layout.addWidget(content_splitter)

        # Apply button styles
        self.setStyleSheet(self.styleSheet() + """
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
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #007aff;
            }
        """)

    def _populate_periods(self):
        """Populate period selector with recent months."""
        today = date.today()
        for i in range(12):
            year = today.year
            month = today.month - i
            if month <= 0:
                year -= 1
                month += 12
            self.period_combo.addItem(f"{year}-{month:02d}")

    def _on_period_changed(self, period_text: str):
        """Handle period selection change."""
        self._load_data()

    def _load_data(self):
        """Load KPI data for the selected period."""
        period_value = self.period_combo.currentText()
        if not period_value:
            return

        try:
            # Load my KPI
            my_kpi = self.kpi_service.kpi_repo.get_by_user_and_period(
                self.current_user_id, 'monthly', period_value
            )

            if my_kpi:
                self._update_cards(my_kpi)
            else:
                self._clear_cards()

            # Load top performers
            self._load_top_performers(period_value)

            # Load my history
            self._load_my_history()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu KPI: {str(e)}")

    def _update_cards(self, kpi: dict):
        """Update KPI cards with data."""
        # Performance score
        score = kpi.get('overall_score', 0)
        rating = self.kpi_service.get_performance_rating(score)
        self.performance_card.set_value(f"{score:.1f}")
        self.performance_card.subtitle_label.setText(f"{rating}")

        # Cars sold
        cars = kpi.get('cars_sold', 0)
        target_cars = kpi.get('target_cars', 0)
        self.cars_card.set_value(str(cars))
        self.cars_card.subtitle_label.setText(f"Mục tiêu: {target_cars}")

        # Revenue
        revenue = kpi.get('revenue_generated', 0)
        target_revenue = kpi.get('target_revenue', 0)
        self.revenue_card.set_value(f"{revenue:,.0f}")
        self.revenue_card.subtitle_label.setText(f"Mục tiêu: {target_revenue:,.0f}")

        # Rank
        rank = kpi.get('period_rank')
        total = kpi.get('total_staff', 0)
        if rank:
            self.rank_card.set_value(f"#{rank}")
            self.rank_card.subtitle_label.setText(f"Trong {total} nhân viên")
        else:
            self.rank_card.set_value("--")
            self.rank_card.subtitle_label.setText("Chưa xếp hạng")

    def _clear_cards(self):
        """Clear all KPI cards."""
        self.performance_card.set_value("--")
        self.performance_card.subtitle_label.setText("Chưa có dữ liệu")
        self.cars_card.set_value("--")
        self.cars_card.subtitle_label.setText("Mục tiêu: --")
        self.revenue_card.set_value("--")
        self.revenue_card.subtitle_label.setText("Mục tiêu: --")
        self.rank_card.set_value("--")
        self.rank_card.subtitle_label.setText("Chưa xếp hạng")

    def _load_top_performers(self, period_value: str):
        """Load top performers table."""
        performers = self.kpi_service.get_performance_ranking(
            'monthly', period_value, limit=10
        )

        self.performers_table.setRowCount(len(performers))

        for row, p in enumerate(performers):
            # Rank with medal for top 3
            rank_text = f"#{p.rank}"
            if p.rank == 1:
                rank_text = "🥇"
            elif p.rank == 2:
                rank_text = "🥈"
            elif p.rank == 3:
                rank_text = "🥉"

            self.performers_table.setItem(row, 0, QTableWidgetItem(rank_text))
            self.performers_table.setItem(row, 1, QTableWidgetItem(p.user_name))
            self.performers_table.setItem(row, 2, QTableWidgetItem(str(p.cars_sold)))
            self.performers_table.setItem(row, 3, QTableWidgetItem(f"{p.revenue:,.0f}"))
            self.performers_table.setItem(row, 4, QTableWidgetItem(f"{p.overall_score:.1f}"))

            # Highlight current user
            if p.user_id == self.current_user_id:
                for col in range(5):
                    item = self.performers_table.item(row, col)
                    item.setBackground(QColor("#e3f2fd"))

    def _load_my_history(self):
        """Load my KPI history."""
        history = self.kpi_service.get_kpi_trend(self.current_user_id, months=6)

        self.history_table.setRowCount(len(history))

        for row, record in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(record['period_value']))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(record['cars_sold'])))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{record['cars_achievement_rate']:.1f}%"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{record['revenue_generated']:,.0f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{record['revenue_achievement_rate']:.1f}%"))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{record['overall_score']:.1f}"))

    def _export_report(self):
        """Export KPI report."""
        period_value = self.period_combo.currentText()

        # Get date range for the period
        year, month = map(int, period_value.split('-'))
        from datetime import datetime
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        report = self.kpi_service.generate_kpi_report(
            self.current_user_id, start_date, end_date
        )

        if report:
            QMessageBox.information(
                self,
                "Báo cáo KPI",
                f"Báo cáo KPI {period_value}:\n\n"
                f"Tổng xe bán: {report['summary']['total_cars_sold']}\n"
                f"Tổng doanh thu: {report['summary']['total_revenue']:,.0f}\n"
                f"Điểm trung bình: {report['summary']['average_score']}\n"
                f"Xu hướng: {report['summary']['trend']}"
            )
        else:
            QMessageBox.information(
                self,
                "Báo cáo KPI",
                "Chưa có dữ liệu KPI cho kỳ này."
            )
