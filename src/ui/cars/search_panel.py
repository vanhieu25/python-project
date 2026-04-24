"""
Car Search Panel UI Module
Advanced search and filter panel for cars.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
import time

from ...services.car_search_service import CarSearchService


class SearchPanel(ttk.Frame):
    """Search panel with filters."""

    def __init__(self, parent, search_service: CarSearchService,
                 on_search: Optional[Callable] = None, **kwargs):
        """Initialize search panel.

        Args:
            parent: Parent widget
            search_service: Search service instance
            on_search: Callback when search changes
        """
        super().__init__(parent, **kwargs)
        self.search_service = search_service
        self.on_search = on_search

        # Debounce timer
        self._debounce_after_id = None

        self._create_widgets()
        self._load_filter_options()

    def _create_widgets(self):
        """Create UI widgets."""
        # Search box
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=5)

        self.keyword_var = tk.StringVar()
        self.keyword_var.trace('w', self._on_keyword_change)
        self.keyword_entry = ttk.Entry(search_frame, textvariable=self.keyword_var, width=40)
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(search_frame, text="Tìm kiếm", command=self._do_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Xóa bộ lọc", command=self._clear_filters).pack(side=tk.LEFT, padx=5)

        # Filters
        self.filters_frame = ttk.LabelFrame(self, text="Bộ lọc", padding=10)
        self.filters_frame.pack(fill=tk.X, pady=5)

        # Row 1: Brand, Model
        row1 = ttk.Frame(self.filters_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Hãng:").pack(side=tk.LEFT)
        self.brand_var = tk.StringVar(value="Tất cả")
        self.brand_combo = ttk.Combobox(row1, textvariable=self.brand_var,
                                        width=15, state="readonly")
        self.brand_combo.pack(side=tk.LEFT, padx=5)
        self.brand_combo.bind("<<ComboboxSelected>>", self._do_search)

        ttk.Label(row1, text="Model:").pack(side=tk.LEFT, padx=(20, 0))
        self.model_var = tk.StringVar(value="Tất cả")
        self.model_combo = ttk.Combobox(row1, textvariable=self.model_var,
                                        width=15, state="readonly")
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self._do_search)

        # Row 2: Year, Price
        row2 = ttk.Frame(self.filters_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="Năm:").pack(side=tk.LEFT)
        self.year_from_var = tk.StringVar()
        self.year_to_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.year_from_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(row2, text="-").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.year_to_var, width=8).pack(side=tk.LEFT, padx=2)

        ttk.Label(row2, text="Giá:").pack(side=tk.LEFT, padx=(20, 0))
        self.price_from_var = tk.StringVar()
        self.price_to_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.price_from_var, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Label(row2, text="-").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.price_to_var, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Label(row2, text="VNĐ").pack(side=tk.LEFT)

        # Row 3: Status, Color, Transmission, Fuel
        row3 = ttk.Frame(self.filters_frame)
        row3.pack(fill=tk.X, pady=2)

        ttk.Label(row3, text="Trạng thái:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Tất cả")
        self.status_combo = ttk.Combobox(row3, textvariable=self.status_var,
                                          width=12, state="readonly")
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self._do_search)

        ttk.Label(row3, text="Màu:"
).pack(side=tk.LEFT, padx=(10, 0))
        self.color_var = tk.StringVar(value="Tất cả")
        self.color_combo = ttk.Combobox(row3, textvariable=self.color_var,
                                           width=10, state="readonly")
        self.color_combo.pack(side=tk.LEFT, padx=5)
        self.color_combo.bind("<<ComboboxSelected>>", self._do_search)

        ttk.Label(row3, text="Hộp số:").pack(side=tk.LEFT, padx=(10, 0))
        self.trans_var = tk.StringVar(value="Tất cả")
        self.trans_combo = ttk.Combobox(row3, textvariable=self.trans_var,
                                         values=["Tất cả", "auto", "manual", "cvt"],
                                         width=10, state="readonly")
        self.trans_combo.pack(side=tk.LEFT, padx=5)
        self.trans_combo.bind("<<ComboboxSelected>>", self._do_search)

        # Row 4: Sort
        row4 = ttk.Frame(self.filters_frame)
        row4.pack(fill=tk.X, pady=2)

        ttk.Label(row4, text="Sắp xếp theo:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="created_at")
        self.sort_combo = ttk.Combobox(row4, textvariable=self.sort_var,
                                        values=[
                                            ("created_at", "Ngày nhập"),
                                            ("selling_price", "Giá bán"),
                                            ("year", "Năm SX"),
                                            ("brand", "Hãng xe")
                                        ],
                                        width=15, state="readonly")
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.bind("<<ComboboxSelected>>", self._do_search)

        self.sort_order_var = tk.StringVar(value="DESC")
        ttk.Radiobutton(row4, text="Giảm dần", variable=self.sort_order_var,
                        value="DESC", command=self._do_search).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(row4, text="Tăng dần", variable=self.sort_order_var,
                        value="ASC", command=self._do_search).pack(side=tk.LEFT)

    def _load_filter_options(self):
        """Load available filter options from database."""
        try:
            options = self.search_service.get_filter_options()

            # Update brand combo
            brands = ["Tất cả"] + options.get('brands', [])
            self.brand_combo['values'] = brands

            # Update model combo (will be filtered by brand selection)
            models = ["Tất cả"] + options.get('models', [])
            self.model_combo['values'] = models

            # Update color combo
            colors = ["Tất cả"] + options.get('colors', [])
            self.color_combo['values'] = colors

            # Update status combo
            statuses = [
                ("Tất cả", "Tất cả"),
                ("available", "Còn hàng"),
                ("sold", "Đã bán"),
                ("reserved", "Đã đặt"),
                ("maintenance", "Bảo dưỡng")
            ]
            self.status_combo['values'] = [s[0] for s in statuses]

        except Exception as e:
            print(f"Error loading filter options: {e}")

    def _on_keyword_change(self, *args):
        """Handle keyword change with debounce."""
        if self._debounce_after_id:
            self.after_cancel(self._debounce_after_id)
        self._debounce_after_id = self.after(300, self._do_search)

    def _do_search(self, event=None):
        """Execute search with current filters."""
        if self.on_search:
            filters = self.get_filters()
            self.on_search(filters)

    def _clear_filters(self):
        """Clear all filters."""
        self.keyword_var.set("")
        self.brand_var.set("Tất cả")
        self.model_var.set("Tất cả")
        self.year_from_var.set("")
        self.year_to_var.set("")
        self.price_from_var.set("")
        self.price_to_var.set("")
        self.status_var.set("Tất cả")
        self.color_var.set("Tất cả")
        self.trans_var.set("Tất cả")
        self.sort_var.set("created_at")
        self.sort_order_var.set("DESC")
        self._do_search()

    def get_filters(self) -> Dict[str, Any]:
        """Get current filter values.

        Returns:
            Dictionary of filter values
        """
        filters = {
            'keyword': self.keyword_var.get() or None,
            'brands': [self.brand_var.get()] if self.brand_var.get() != "Tất cả" else None,
            'models': [self.model_var.get()] if self.model_var.get() != "Tất cả" else None,
            'year_from': int(self.year_from_var.get()) if self.year_from_var.get() else None,
            'year_to': int(self.year_to_var.get()) if self.year_to_var.get() else None,
            'price_from': float(self.price_from_var.get()) if self.price_from_var.get() else None,
            'price_to': float(self.price_to_var.get()) if self.price_to_var.get() else None,
            'statuses': [self.status_var.get()] if self.status_var.get() != "Tất cả" else None,
            'colors': [self.color_var.get()] if self.color_var.get() != "Tất cả" else None,
            'transmissions': [self.trans_var.get()] if self.trans_var.get() != "Tất cả" else None,
            'sort_by': self.sort_var.get(),
            'sort_order': self.sort_order_var.get()
        }
        return filters


class PaginationFrame(ttk.Frame):
    """Pagination controls."""

    def __init__(self, parent, on_page_change: Optional[Callable] = None,
                 per_page_options: List[int] = None, **kwargs):
        """Initialize pagination frame.

        Args:
            parent: Parent widget
            on_page_change: Callback when page changes
            per_page_options: Options for items per page
        """
        super().__init__(parent, **kwargs)
        self.on_page_change = on_page_change
        self.current_page = 1
        self.total_pages = 1
        self.total_items = 0

        if per_page_options is None:
            per_page_options = [10, 20, 50, 100]
        self.per_page_options = per_page_options
        self.per_page = per_page_options[0]

        self._create_widgets()

    def _create_widgets(self):
        """Create pagination widgets."""
        # Info label
        self.info_label = ttk.Label(self, text="")
        self.info_label.pack(side=tk.LEFT, padx=5)

        # Per page selector
        ttk.Label(self, text="Hiển thị:").pack(side=tk.LEFT, padx=(20, 0))
        self.per_page_var = tk.IntVar(value=self.per_page)
        self.per_page_combo = ttk.Combobox(self, textvariable=self.per_page_var,
                                           values=self.per_page_options,
                                           width=5, state="readonly")
        self.per_page_combo.pack(side=tk.LEFT, padx=5)
        self.per_page_combo.bind("<<ComboboxSelected>>", self._on_per_page_change)

        # Navigation buttons
        ttk.Button(self, text="❮", width=3, command=self._prev_page).pack(side=tk.LEFT, padx=2)

        self.page_var = tk.StringVar(value="1")
        self.page_entry = ttk.Entry(self, textvariable=self.page_var, width=5, justify=tk.CENTER)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind("<Return>", self._on_page_entry)

        ttk.Label(self, text="/").pack(side=tk.LEFT)

        self.total_pages_label = ttk.Label(self, text="1")
        self.total_pages_label.pack(side=tk.LEFT, padx=2)

        ttk.Button(self, text="❯", width=3, command=self._next_page).pack(side=tk.LEFT, padx=2)

    def set_total(self, total: int):
        """Set total number of items."""
        self.total_items = total
        self.total_pages = max(1, (total + self.per_page - 1) // self.per_page)
        self.current_page = min(self.current_page, self.total_pages)

        self._update_display()

    def _update_display(self):
        """Update pagination display."""
        # Update info
        start = (self.current_page - 1) * self.per_page + 1
        end = min(self.current_page * self.per_page, self.total_items)
        self.info_label.config(text=f"{start}-{end} / {self.total_items}")

        # Update page entry
        self.page_var.set(str(self.current_page))
        self.total_pages_label.config(text=str(self.total_pages))

    def _on_per_page_change(self, event=None):
        """Handle per page change."""
        self.per_page = self.per_page_var.get()
        self.current_page = 1
        self._trigger_page_change()

    def _on_page_entry(self, event=None):
        """Handle manual page entry."""
        try:
            page = int(self.page_var.get())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self._trigger_page_change()
            else:
                self.page_var.set(str(self.current_page))
        except ValueError:
            self.page_var.set(str(self.current_page))

    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self._trigger_page_change()

    def _next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._trigger_page_change()

    def _trigger_page_change(self):
        """Trigger page change callback."""
        self._update_display()
        if self.on_page_change:
            self.on_page_change(self.current_page, self.per_page)

    def get_pagination(self) -> tuple:
        """Get current pagination settings.

        Returns:
            Tuple of (page, per_page)
        """
        return self.current_page, self.per_page

    def reset(self):
        """Reset to first page."""
        self.current_page = 1
        self._update_display()
