"""
Contract Detail View Module
Detail view with tabs for contract information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.contract import Contract
from services.contract_service import ContractService, Result


class ContractDetailView(tk.Toplevel):
    """Contract detail view with tabs."""

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: ContractService,
        contract_id: int,
        current_user_id: int = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_approve: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ):
        """Initialize contract detail view.

        Args:
            parent: Parent widget
            contract_service: ContractService instance
            contract_id: Contract ID to display
            current_user_id: Current logged-in user ID
            on_edit: Callback when edit requested
            on_delete: Callback when delete requested
            on_approve: Callback when approve requested
            on_close: Callback when window closed
        """
        super().__init__(parent)
        self.title("Chi tiết hợp đồng")
        self.geometry("800x600")
        self.minsize(700, 500)

        self.contract_service = contract_service
        self.contract_id = contract_id
        self.current_user_id = current_user_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_approve = on_approve
        self.on_close = on_close

        self.contract = None

        self._create_widgets()
        self._load_contract()

        # Modal dialog
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Create UI widgets."""
        # Header
        header = tk.Frame(self, bg='#2196F3', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self.title_label = tk.Label(
            header,
            text="Hợp đồng #",
            font=('Arial', 16, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.status_label = tk.Label(
            header,
            text="Status",
            font=('Arial', 11),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=3
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)

        # Action buttons
        action_frame = tk.Frame(self, padx=10, pady=10)
        action_frame.pack(fill=tk.X)

        self.edit_btn = tk.Button(
            action_frame,
            text="Sửa",
            command=self._on_edit_click
        )
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(
            action_frame,
            text="Xóa",
            command=self._on_delete_click,
            fg='red'
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.approve_btn = tk.Button(
            action_frame,
            text="Phê duyệt",
            command=self._on_approve_click,
            bg='#4CAF50',
            fg='white'
        )
        self.approve_btn.pack(side=tk.LEFT, padx=5)

        self.print_btn = tk.Button(
            action_frame,
            text="In hợp đồng",
            command=self._on_print_click
        )
        self.print_btn.pack(side=tk.LEFT, padx=5)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: General Info
        self.info_tab = tk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="Thông tin chung")
        self._create_info_tab()

        # Tab 2: Items
        self.items_tab = tk.Frame(self.notebook)
        self.notebook.add(self.items_tab, text="Phụ kiện & Dịch vụ")
        self._create_items_tab()

        # Tab 3: Payments
        self.payments_tab = tk.Frame(self.notebook)
        self.notebook.add(self.payments_tab, text="Thanh toán")
        self._create_payments_tab()

        # Tab 4: History
        self.history_tab = tk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Lịch sử")
        self._create_history_tab()

        # Close button
        tk.Button(
            self,
            text="Đóng",
            command=self._on_close
        ).pack(pady=10)

    def _create_info_tab(self):
        """Create general info tab."""
        # Customer info frame
        customer_frame = tk.LabelFrame(self.info_tab, text="Thông tin khách hàng", padx=10, pady=10)
        customer_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(customer_frame, text="Họ tên:").grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.customer_name_label = tk.Label(customer_frame, text="", font=('Arial', 10, 'bold'))
        self.customer_name_label.grid(row=0, column=1, sticky='w', padx=5, pady=3)

        tk.Label(customer_frame, text="Số điện thoại:").grid(row=1, column=0, sticky='e', padx=5, pady=3)
        self.customer_phone_label = tk.Label(customer_frame, text="")
        self.customer_phone_label.grid(row=1, column=1, sticky='w', padx=5, pady=3)

        tk.Label(customer_frame, text="CMND/CCCD:").grid(row=2, column=0, sticky='e', padx=5, pady=3)
        self.customer_id_card_label = tk.Label(customer_frame, text="")
        self.customer_id_card_label.grid(row=2, column=1, sticky='w', padx=5, pady=3)

        tk.Label(customer_frame, text="Địa chỉ:").grid(row=3, column=0, sticky='e', padx=5, pady=3)
        self.customer_address_label = tk.Label(customer_frame, text="")
        self.customer_address_label.grid(row=3, column=1, sticky='w', padx=5, pady=3)

        # Car info frame
        car_frame = tk.LabelFrame(self.info_tab, text="Thông tin xe", padx=10, pady=10)
        car_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(car_frame, text="Hãng/Model:").grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.car_model_label = tk.Label(car_frame, text="", font=('Arial', 10, 'bold'))
        self.car_model_label.grid(row=0, column=1, sticky='w', padx=5, pady=3)

        tk.Label(car_frame, text="Năm SX:").grid(row=1, column=0, sticky='e', padx=5, pady=3)
        self.car_year_label = tk.Label(car_frame, text="")
        self.car_year_label.grid(row=1, column=1, sticky='w', padx=5, pady=3)

        tk.Label(car_frame, text="Màu sắc:").grid(row=2, column=0, sticky='e', padx=5, pady=3)
        self.car_color_label = tk.Label(car_frame, text="")
        self.car_color_label.grid(row=2, column=1, sticky='w', padx=5, pady=3)

        tk.Label(car_frame, text="Số khung (VIN):").grid(row=3, column=0, sticky='e', padx=5, pady=3)
        self.car_vin_label = tk.Label(car_frame, text="")
        self.car_vin_label.grid(row=3, column=1, sticky='w', padx=5, pady=3)

        tk.Label(car_frame, text="Biển số:").grid(row=4, column=0, sticky='e', padx=5, pady=3)
        self.car_plate_label = tk.Label(car_frame, text="")
        self.car_plate_label.grid(row=4, column=1, sticky='w', padx=5, pady=3)

        # Pricing frame
        pricing_frame = tk.LabelFrame(self.info_tab, text="Thông tin thanh toán", padx=10, pady=10)
        pricing_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(pricing_frame, text="Giá xe:").grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.car_price_label = tk.Label(pricing_frame, text="")
        self.car_price_label.grid(row=0, column=1, sticky='w', padx=5, pady=3)

        tk.Label(pricing_frame, text="Giảm giá:").grid(row=1, column=0, sticky='e', padx=5, pady=3)
        self.discount_label = tk.Label(pricing_frame, text="")
        self.discount_label.grid(row=1, column=1, sticky='w', padx=5, pady=3)

        tk.Label(pricing_frame, text="Tổng tiền:").grid(row=2, column=0, sticky='e', padx=5, pady=3)
        self.total_label = tk.Label(pricing_frame, text="")
        self.total_label.grid(row=2, column=1, sticky='w', padx=5, pady=3)

        tk.Label(pricing_frame, text="VAT (10%):").grid(row=3, column=0, sticky='e', padx=5, pady=3)
        self.vat_label = tk.Label(pricing_frame, text="")
        self.vat_label.grid(row=3, column=1, sticky='w', padx=5, pady=3)

        tk.Label(pricing_frame, text="TỔNG THANH TOÁN:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.final_label = tk.Label(pricing_frame, text="", font=('Arial', 12, 'bold'), fg='blue')
        self.final_label.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        tk.Label(pricing_frame, text="Đã thanh toán:").grid(row=5, column=0, sticky='e', padx=5, pady=3)
        self.paid_label = tk.Label(pricing_frame, text="", fg='green')
        self.paid_label.grid(row=5, column=1, sticky='w', padx=5, pady=3)

        tk.Label(pricing_frame, text="Còn lại:").grid(row=6, column=0, sticky='e', padx=5, pady=3)
        self.remaining_label = tk.Label(pricing_frame, text="", fg='red')
        self.remaining_label.grid(row=6, column=1, sticky='w', padx=5, pady=3)

    def _create_items_tab(self):
        """Create items tab."""
        # Items table
        columns = ('item_type', 'item_name', 'quantity', 'unit_price', 'total_price')
        self.items_tree = ttk.Treeview(
            self.items_tab,
            columns=columns,
            show='headings'
        )

        self.items_tree.heading('item_type', text='Loại')
        self.items_tree.heading('item_name', text='Tên')
        self.items_tree.heading('quantity', text='SL')
        self.items_tree.heading('unit_price', text='Đơn giá')
        self.items_tree.heading('total_price', text='Thành tiền')

        scrollbar = ttk.Scrollbar(self.items_tab, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def _create_payments_tab(self):
        """Create payments tab."""
        # Payments table
        columns = ('payment_code', 'payment_type', 'amount', 'payment_method', 'payment_date')
        self.payments_tree = ttk.Treeview(
            self.payments_tab,
            columns=columns,
            show='headings'
        )

        self.payments_tree.heading('payment_code', text='Mã PT')
        self.payments_tree.heading('payment_type', text='Loại')
        self.payments_tree.heading('amount', text='Số tiền')
        self.payments_tree.heading('payment_method', text='Phương thức')
        self.payments_tree.heading('payment_date', text='Ngày')

        scrollbar = ttk.Scrollbar(self.payments_tab, orient='vertical', command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)

        self.payments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Add payment button
        tk.Button(
            self.payments_tab,
            text="+ Thêm thanh toán",
            command=self._on_add_payment
        ).pack(anchor='w', padx=10, pady=5)

    def _create_history_tab(self):
        """Create history tab."""
        self.history_text = tk.Text(self.history_tab, state='disabled', padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.history_tab, orient='vertical', command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)

        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def _load_contract(self):
        """Load contract data."""
        self.contract = self.contract_service.get_contract_detail(self.contract_id)

        if not self.contract:
            messagebox.showerror("Lỗi", "Không tìm thấy hợp đồng")
            self.destroy()
            return

        self._update_ui()

    def _update_ui(self):
        """Update UI with contract data."""
        contract = self.contract

        # Update header
        self.title_label.config(text=f"Hợp đồng {contract.contract_code}")

        status_labels = {
            'draft': 'Nháp',
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'signed': 'Đã ký',
            'paid': 'Đã thanh toán',
            'delivered': 'Đã giao',
            'cancelled': 'Đã hủy'
        }
        status_colors = {
            'draft': '#9E9E9E',
            'pending': '#FFC107',
            'approved': '#2196F3',
            'signed': '#9C27B0',
            'paid': '#4CAF50',
            'delivered': '#009688',
            'cancelled': '#F44336'
        }

        self.status_label.config(
            text=status_labels.get(contract.status, contract.status),
            bg=status_colors.get(contract.status, '#9E9E9E')
        )

        # Update buttons based on status
        can_edit = contract.status == 'draft'
        can_delete = contract.status == 'draft'
        can_approve = contract.status == 'pending'

        self.edit_btn.config(state='normal' if can_edit else 'disabled')
        self.delete_btn.config(state='normal' if can_delete else 'disabled')
        self.approve_btn.config(state='normal' if can_approve else 'disabled')

        # Update customer info
        self.customer_name_label.config(text=contract.customer_name or 'N/A')
        self.customer_phone_label.config(text=contract.customer_phone or 'N/A')
        self.customer_id_card_label.config(text=contract.customer_id_card or 'N/A')
        self.customer_address_label.config(text=contract.customer_address or 'N/A')

        # Update car info
        car_model = f"{contract.car_brand or ''} {contract.car_model or ''}".strip()
        self.car_model_label.config(text=car_model or 'N/A')
        self.car_year_label.config(text=str(contract.car_year) if contract.car_year else 'N/A')
        self.car_color_label.config(text=contract.car_color or 'N/A')
        self.car_vin_label.config(text=contract.car_vin or 'N/A')
        self.car_plate_label.config(text=contract.car_license_plate or 'N/A')

        # Update pricing
        self.car_price_label.config(text=f"{contract.car_price:,.0f} VNĐ")
        self.discount_label.config(text=f"{contract.discount_amount:,.0f} VNĐ")
        self.total_label.config(text=f"{contract.total_amount:,.0f} VNĐ")
        self.vat_label.config(text=f"{contract.vat_amount:,.0f} VNĐ")
        self.final_label.config(text=f"{contract.final_amount:,.0f} VNĐ")
        self.paid_label.config(text=f"{contract.paid_amount:,.0f} VNĐ")
        self.remaining_label.config(text=f"{contract.remaining_amount:,.0f} VNĐ")

        # Update items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        for item in contract.items:
            self.items_tree.insert('', 'end', values=(
                item.item_type,
                item.item_name,
                item.quantity,
                f"{item.unit_price:,.0f}",
                f"{item.total_price:,.0f}"
            ))

        # Update payments
        for payment in self.payments_tree.get_children():
            self.payments_tree.delete(payment)

        for payment in contract.payments:
            self.payments_tree.insert('', 'end', values=(
                payment.payment_code or 'N/A',
                payment.payment_type or 'N/A',
                f"{payment.amount:,.0f}",
                payment.payment_method or 'N/A',
                payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else 'N/A'
            ))

        # Update history
        history = self.contract_service.contract_repo.get_status_history(contract.id)
        self.history_text.config(state='normal')
        self.history_text.delete('1.0', tk.END)

        for record in history:
            old_status = status_labels.get(record['old_status'], record['old_status'])
            new_status = status_labels.get(record['new_status'], record['new_status'])
            changed_at = record['changed_at'][:16] if record['changed_at'] else 'N/A'
            notes = record['notes'] or ''

            self.history_text.insert(tk.END, f"[{changed_at}] {old_status} → {new_status}\n")
            if notes:
                self.history_text.insert(tk.END, f"  Ghi chú: {notes}\n")
            self.history_text.insert(tk.END, "\n")

        self.history_text.config(state='disabled')

    def _on_edit_click(self):
        """Handle edit button click."""
        if self.on_edit:
            self.on_edit(self.contract_id)
            self._load_contract()

    def _on_delete_click(self):
        """Handle delete button click."""
        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa hợp đồng {self.contract.contract_code}?"
        ):
            return

        result = self.contract_service.delete_contract(self.contract_id, self.current_user_id)

        if result.success:
            messagebox.showinfo("Thành công", "Hợp đồng đã được xóa")
            if self.on_delete:
                self.on_delete(self.contract_id)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.error)

    def _on_approve_click(self):
        """Handle approve button click."""
        if self.on_approve:
            self.on_approve(self.contract_id)
            self._load_contract()

    def _on_print_click(self):
        """Handle print button click."""
        messagebox.showinfo("Thông báo", "Tính năng in hợp đồng đang được phát triển")

    def _on_add_payment(self):
        """Handle add payment button click."""
        messagebox.showinfo("Thông báo", "Tính năng thêm thanh toán đang được phát triển")

    def _on_close(self):
        """Handle window close."""
        if self.on_close:
            self.on_close()
        self.destroy()
