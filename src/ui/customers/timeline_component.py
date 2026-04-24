"""
Timeline Component Module
Custom widget for displaying customer activity timeline.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor


class TimelineItem(QWidget):
    """Single timeline item widget."""

    def __init__(self, item_data: Dict[str, Any], parent=None):
        """Initialize timeline item.

        Args:
            item_data: Dictionary containing timeline item data
            parent: Parent widget
        """
        super().__init__(parent)
        self.item_data = item_data
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 8, 10, 8)

        # Icon label
        icon = self.item_data.get('icon', '📝')
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                min-width: 30px;
                max-width: 30px;
            }
        """)
        layout.addWidget(self.icon_label)

        # Content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header row (timestamp and user)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        timestamp = self.item_data.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                time_str = timestamp
            else:
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = 'Unknown'

        self.time_label = QLabel(time_str)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.time_label)
        header_layout.addStretch()

        user = self.item_data.get('user', 'Unknown')
        self.user_label = QLabel(f"bởi {user}")
        self.user_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
            }
        """)
        header_layout.addWidget(self.user_label)

        content_layout.addLayout(header_layout)

        # Description
        description = self.item_data.get('description', '')
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
            }
        """)
        self.desc_label.setWordWrap(True)
        content_layout.addWidget(self.desc_label)

        # Amount (for contracts)
        amount = self.item_data.get('amount')
        if amount:
            self.amount_label = QLabel(f"Giá trị: {self._format_amount(amount)} VNĐ")
            self.amount_label.setStyleSheet("""
                QLabel {
                    color: #0071e3;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            content_layout.addWidget(self.amount_label)

        layout.addWidget(content_widget, 1)

        # Separator line
        self.setStyleSheet("""
            TimelineItem {
                border-bottom: 1px solid #e5e5e5;
            }
        """)

    def _format_amount(self, amount: float) -> str:
        """Format amount to Vietnamese currency format.

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


class TimelineWidget(QWidget):
    """Timeline widget for displaying activities."""

    def __init__(self, parent=None):
        """Initialize timeline widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for timeline items
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(0)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def set_items(self, items: List[Dict[str, Any]]):
        """Set timeline items.

        Args:
            items: List of timeline item dictionaries
        """
        # Clear existing items
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add items
        if not items:
            empty_label = QLabel("Chưa có hoạt động nào")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 40px;
                }
            """)
            self.container_layout.addWidget(empty_label)
        else:
            for item_data in items:
                timeline_item = TimelineItem(item_data)
                self.container_layout.addWidget(timeline_item)

        self.container_layout.addStretch()

    def clear(self):
        """Clear all timeline items."""
        self.set_items([])


class TimelineComponent(QWidget):
    """Complete timeline component with header."""

    def __init__(self, title: str = "Lịch sử hoạt động", parent=None):
        """Initialize timeline component.

        Args:
            title: Component title
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        self.header = QLabel(self.title)
        self.header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1d1d1f;
                padding-bottom: 10px;
                border-bottom: 2px solid #0071e3;
            }
        """)
        layout.addWidget(self.header)

        # Timeline widget
        self.timeline = TimelineWidget()
        layout.addWidget(self.timeline)

        # Style
        self.setStyleSheet("""
            TimelineComponent {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e5e5e5;
            }
        """)

    def set_items(self, items: List[Dict[str, Any]]):
        """Set timeline items.

        Args:
            items: List of timeline item dictionaries
        """
        self.timeline.set_items(items)

    def clear(self):
        """Clear timeline."""
        self.timeline.clear()
