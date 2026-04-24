"""
Contract List View Module
Table view for displaying and managing contracts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.contract import Contract
from services.contract_service import ContractService, PaginatedResult


class ContractListView(tk.Frame):
    """Contract list view with table display."""

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: ContractService,
        on_create: Optional[Callable] = None,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None
    ):
        """Initialize contract list view.

        Args:
            parent: Parent widget
            contract_service: ContractService instance
            on_create: Callback for create button
            on_view: Callback for view action (contract_id)
            on_edit: Callback for edit action (contract_id)
            on_delete: Callback for delete action (contract_id)
        """
        super().__init__(parent)
        self.contract_service = contract_service
        self.on_create = on_create
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.current_page = 1
        self.per_page = 20
        self.total_pages = 1
        self.current_filters = {}

        self._create_widgets()
        self._load_contracts()

    def _create_widgets(self):
        """Create UI widgets."""
        # Title
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            title_frame,
            text="Quản lý hợp đồng",
            font=('Arial', 16, 'bold')
        ).pack(side=tk.LEFT)

        # Create button
        tk.Button(
            title_frame,
            text="+ Tạo hợp đồng mới",
            command=self._on_create_click,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.RIGHT)

        # Filter frame
        filter_frame = tk.LabelFrame(self, text="Bộ lọc", padx=10, pady=5)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Status filter
        tk.Label(filter_frame, text="Trạng thái:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value='')
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=['', 'draft', 'pending', 'approved', 'signed', 'paid', 'delivered', 'cancelled'],
            width=15,
            state='readonly'
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filters())

        # Search box
        tk.Label(filter_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=(20, 0))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            filter_frame,
            text="Tìm",
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            filter_frame,
            text="Xóa bộ lọc",
            command=self._clear_filters
        ).pack(side=tk.LEFT, padx=5)

        # Table frame
        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview with scrollbar
        columns = (
            'contract_code', 'customer_name', 'car_info',
            'final_amount', 'status', 'created_at', 'actions'
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        # Define headings
        self.tree.heading('contract_code', text='Mã HĐ')
        self.tree.heading('customer_name', text='Khách hàng')
        self.tree.heading('car_info', text='Xe')
        self.tree.heading('final_amount', text='Tổng tiền')
        self.tree.heading('status', text='Trạng thái')
        self.tree.heading('created_at', text='Ngày tạo')
        self.tree.heading('actions', text='Thao tác')

        # Define columns
        self.tree.column('contract_code', width=100)
        self.tree.column('customer_name', width=150)
        self.tree.column('car_info', width=150)
        self.tree.column('final_amount', width=120, anchor='e')
        self.tree.column('status', width=100)
        self.tree.column('created_at', width=120)
        self.tree.column('actions', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Double click to view
        self.tree.bind('<Double-1>', self._on_double_click)

        # Pagination frame
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)

        self.page_label = tk.Label(pagination_frame, text="Trang 1 / 1")
        self.page_label.pack(side=tk.LEFT)

        tk.Button(
            pagination_frame,
            text="< Trước",
            command=self._prev_page
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            pagination_frame,
            text="Sau >",
            command=self._next_page
        ).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(self, text="Tổng: 0 hợp đồng")
        self.status_label.pack(anchor='w', padx=10, pady=5)

    def _load_contracts(self):
        """Load contracts with current filters and pagination."""
        result = self.contract_service.search_contracts(
            filters=self.current_filters,
            page=self.current_page,
            per_page=self.per_page
        )

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add contracts to table
        status_labels = {
            'draft': 'Nháp',
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'signed': 'Đã ký',
            'paid': 'Đã thanh toán',
            'delivered': 'Đã giao',
            'cancelled': 'Đã hủy'
        }

        for contract in result.items:
            car_info = f"{contract.car_brand or ''} {contract.car_model or ''}".strip()

            self.tree.insert('', 'end', values=(
                contract.contract_code,
                contract.customer_name or '',
                car_info,
                f"{contract.final_amount:,.0f}",
                status_labels.get(contract.status, contract.status),
                contract.created_at.strftime('%d/%m/%Y') if contract.created_at else '',
                'Xem | Sửa | Xóa'
            ))

        # Update pagination
        self.total_pages = result.total_pages
        self.page_label.config(text=f"Trang {self.current_page} / {max(1, self.total_pages)}")
        self.status_label.config(text=f"Tổng: {result.total} hợp đồng")

    def _apply_filters(self):
        """Apply current filters and reload."""
        self.current_filters = {}

        status = self.status_var.get()
        if status:
            self.current_filters['status'] = status

        search = self.search_var.get().strip()
        if search:
            # Try to search by code first, then by customer name
            if search.upper().startswith('HD'):
                self.current_filters['contract_code'] = search.upper()
            else:
                self.current_filters['customer_name'] = search

        self.current_page = 1
        self._load_contracts()

    def _clear_filters(self):
        """Clear all filters."""
        self.status_var.set('')
        self.search_var.set('')
        self.current_filters = {}
        self.current_page = 1
        self._load_contracts()

    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_contracts()

    def _next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_contracts()

    def _on_create_click(self):
        """Handle create button click."""
        if self.on_create:
            self.on_create()

    def _on_double_click(self, event):
        """Handle double click on table row."""
        selected = self.tree.selection()
        if not selected:
            return

        # Get contract code from selected row
        values = self.tree.item(selected[0])['values']
        contract_code = values[0]

        # Find contract by code
        contract = self.contract_service.get_contract_by_code(contract_code)
        if contract and self.on_view:
            self.on_view(contract.id)

    def refresh(self):
        """Refresh the list."""
        self._load_contracts()

    def get_selected_contract(self) -> Optional[Contract]:
        """Get currently selected contract.

        Returns:
            Selected contract or None
        """
        selected = self.tree.selection()
        if not selected:
            return None

        values = self.tree.item(selected[0])['values']
        contract_code = values[0]

        return self.contract_service.get_contract_by_code(contract_code)
