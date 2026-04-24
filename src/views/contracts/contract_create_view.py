"""
Contract Create View Module
Multi-step wizard for creating new contracts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.contract import Contract
from services.contract_service import ContractService, Result


class ContractCreateView(tk.Toplevel):
    """Contract creation wizard dialog."""

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: ContractService,
        customer_repo=None,
        car_repo=None,
        created_by: int = None,
        on_save: Optional[Callable] = None
    ):
        """Initialize create contract dialog.

        Args:
            parent: Parent widget
            contract_service: ContractService instance
            customer_repo: Customer repository
            car_repo: Car repository
            created_by: User ID creating the contract
            on_save: Callback after successful save
        """
        super().__init__(parent)
        self.title("Tạo hợp đồng mới")
        self.geometry("700x600")
        self.resizable(False, False)

        self.contract_service = contract_service
        self.customer_repo = customer_repo
        self.car_repo = car_repo
        self.created_by = created_by
        self.on_save = on_save

        self.current_step = 1
        self.contract_data = {}
        self.selected_customer = None
        self.selected_car = None

        self._create_widgets()
        self._show_step(1)

        # Modal dialog
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create UI widgets."""
        # Header
        header = tk.Frame(self, bg='#2196F3', height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self.step_label = tk.Label(
            header,
            text="Bước 1: Chọn khách hàng",
            font=('Arial', 14, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        self.step_label.pack(pady=10)

        # Content frame
        self.content_frame = tk.Frame(self, padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Step 1: Customer Selection
        self._create_step1()

        # Step 2: Car Selection
        self._create_step2()

        # Step 3: Pricing
        self._create_step3()

        # Step 4: Review
        self._create_step4()

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=10)
        button_frame.pack(fill=tk.X)

        self.back_btn = tk.Button(
            button_frame,
            text="< Quay lại",
            command=self._prev_step,
            state='disabled'
        )
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = tk.Button(
            button_frame,
            text="Tiếp theo >",
            command=self._next_step,
            bg='#2196F3',
            fg='white'
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        self.save_draft_btn = tk.Button(
            button_frame,
            text="Lưu nháp",
            command=self._save_draft
        )
        self.save_draft_btn.pack(side=tk.RIGHT, padx=5)

        self.cancel_btn = tk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

    def _create_step1(self):
        """Create step 1: Customer selection."""
        self.step1_frame = tk.LabelFrame(self.content_frame, text="Chọn khách hàng")

        # Search
        search_frame = tk.Frame(self.step1_frame)
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT)
        self.customer_search = tk.Entry(search_frame, width=30)
        self.customer_search.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Tìm", command=self._search_customers).pack(side=tk.LEFT)

        # Customer list
        list_frame = tk.Frame(self.step1_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.customer_tree = ttk.Treeview(
            list_frame,
            columns=('name', 'phone', 'id_card'),
            show='headings',
            height=10
        )
        self.customer_tree.heading('name', text='Họ tên')
        self.customer_tree.heading('phone', text='Số điện thoại')
        self.customer_tree.heading('id_card', text='CMND/CCCD')
        self.customer_tree.column('name', width=200)
        self.customer_tree.column('phone', width=150)
        self.customer_tree.column('id_card', width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)

        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Selected customer display
        self.selected_customer_label = tk.Label(
            self.step1_frame,
            text="Chưa chọn khách hàng",
            fg='red',
            font=('Arial', 10, 'bold')
        )
        self.selected_customer_label.pack(pady=10)

    def _create_step2(self):
        """Create step 2: Car selection."""
        self.step2_frame = tk.LabelFrame(self.content_frame, text="Chọn xe")

        # Search
        search_frame = tk.Frame(self.step2_frame)
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT)
        self.car_search = tk.Entry(search_frame, width=30)
        self.car_search.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Tìm", command=self._search_cars).pack(side=tk.LEFT)

        # Car list
        list_frame = tk.Frame(self.step2_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.car_tree = ttk.Treeview(
            list_frame,
            columns=('brand', 'model', 'year', 'color', 'price'),
            show='headings',
            height=10
        )
        self.car_tree.heading('brand', text='Hãng')
        self.car_tree.heading('model', text='Model')
        self.car_tree.heading('year', text='Năm SX')
        self.car_tree.heading('color', text='Màu')
        self.car_tree.heading('price', text='Giá')
        self.car_tree.column('brand', width=100)
        self.car_tree.column('model', width=120)
        self.car_tree.column('year', width=80)
        self.car_tree.column('color', width=80)
        self.car_tree.column('price', width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.car_tree.yview)
        self.car_tree.configure(yscrollcommand=scrollbar.set)

        self.car_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Selected car display
        self.selected_car_label = tk.Label(
            self.step2_frame,
            text="Chưa chọn xe",
            fg='red',
            font=('Arial', 10, 'bold')
        )
        self.selected_car_label.pack(pady=10)

    def _create_step3(self):
        """Create step 3: Pricing."""
        self.step3_frame = tk.LabelFrame(self.content_frame, text="Thông tin giá cả")

        # Pricing form
        form_frame = tk.Frame(self.step3_frame)
        form_frame.pack(pady=20)

        # Car price
        tk.Label(form_frame, text="Giá xe:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.car_price_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.car_price_var, width=20).grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(form_frame, text="VNĐ").grid(row=0, column=2, sticky='w')

        # Discount
        tk.Label(form_frame, text="Giảm giá:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.discount_var = tk.StringVar(value='0')
        tk.Entry(form_frame, textvariable=self.discount_var, width=20).grid(row=1, column=1, sticky='w', padx=5)
        tk.Label(form_frame, text="VNĐ").grid(row=1, column=2, sticky='w')

        tk.Label(form_frame, text="Lý do giảm giá:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.discount_reason_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.discount_reason_var, width=30).grid(row=2, column=1, columnspan=2, sticky='w', padx=5)

        # VAT
        tk.Label(form_frame, text="Thuế VAT (10%):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.vat_var = tk.StringVar(value='0')
        tk.Label(form_frame, textvariable=self.vat_var, width=20).grid(row=3, column=1, sticky='w', padx=5)
        tk.Label(form_frame, text="VNĐ").grid(row=3, column=2, sticky='w')

        # Total
        tk.Label(form_frame, text="Tổng thanh toán:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.total_var = tk.StringVar(value='0')
        tk.Label(form_frame, textvariable=self.total_var, font=('Arial', 12, 'bold'), fg='blue').grid(row=4, column=1, sticky='w', padx=5)
        tk.Label(form_frame, text="VNĐ").grid(row=4, column=2, sticky='w')

        # Calculate button
        tk.Button(form_frame, text="Tính toán", command=self._calculate_totals).grid(row=5, column=1, pady=20)

    def _create_step4(self):
        """Create step 4: Review and confirm."""
        self.step4_frame = tk.LabelFrame(self.content_frame, text="Xác nhận thông tin")

        self.review_text = tk.Text(self.step4_frame, height=20, width=70, state='disabled')
        self.review_text.pack(padx=10, pady=10)

    def _show_step(self, step: int):
        """Show specified step.

        Args:
            step: Step number (1-4)
        """
        # Hide all steps
        for frame in [self.step1_frame, self.step2_frame, self.step3_frame, self.step4_frame]:
            frame.pack_forget()

        # Show current step
        if step == 1:
            self.step1_frame.pack(fill=tk.BOTH, expand=True)
            self.step_label.config(text="Bước 1: Chọn khách hàng")
            self.back_btn.config(state='disabled')
            self.next_btn.config(text="Tiếp theo >")
        elif step == 2:
            self.step2_frame.pack(fill=tk.BOTH, expand=True)
            self.step_label.config(text="Bước 2: Chọn xe")
            self.back_btn.config(state='normal')
            self.next_btn.config(text="Tiếp theo >")
        elif step == 3:
            self.step3_frame.pack(fill=tk.BOTH, expand=True)
            self.step_label.config(text="Bước 3: Thông tin giá cả")
            self.back_btn.config(state='normal')
            self.next_btn.config(text="Tiếp theo >")
        elif step == 4:
            self.step4_frame.pack(fill=tk.BOTH, expand=True)
            self.step_label.config(text="Bước 4: Xác nhận")
            self.back_btn.config(state='normal')
            self.next_btn.config(text="Lưu hợp đồng")
            self._update_review()

        self.current_step = step

    def _next_step(self):
        """Go to next step."""
        if self.current_step == 1:
            if not self.selected_customer:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng")
                return
        elif self.current_step == 2:
            if not self.selected_car:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn xe")
                return
        elif self.current_step == 3:
            if not self._validate_pricing():
                return
        elif self.current_step == 4:
            self._save_contract()
            return

        self._show_step(self.current_step + 1)

    def _prev_step(self):
        """Go to previous step."""
        if self.current_step > 1:
            self._show_step(self.current_step - 1)

    def _search_customers(self):
        """Search customers."""
        if not self.customer_repo:
            messagebox.showinfo("Thông báo", "Tính năng tìm kiếm khách hàng chưa được kết nối")
            return

        keyword = self.customer_search.get().strip()
        # TODO: Implement customer search

    def _search_cars(self):
        """Search available cars."""
        if not self.car_repo:
            messagebox.showinfo("Thông báo", "Tính năng tìm kiếm xe chưa được kết nối")
            return

        keyword = self.car_search.get().strip()
        # TODO: Implement car search

    def _validate_pricing(self) -> bool:
        """Validate pricing information.

        Returns:
            True if valid
        """
        try:
            car_price = float(self.car_price_var.get() or 0)
            discount = float(self.discount_var.get() or 0)

            if car_price <= 0:
                messagebox.showwarning("Cảnh báo", "Giá xe phải lớn hơn 0")
                return False

            if discount > car_price:
                messagebox.showwarning("Cảnh báo", "Giảm giá không thể lớn hơn giá xe")
                return False

            return True
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập số hợp lệ")
            return False

    def _calculate_totals(self):
        """Calculate price totals."""
        try:
            car_price = float(self.car_price_var.get() or 0)
            discount = float(self.discount_var.get() or 0)

            total = car_price - discount
            vat = total * 0.1  # 10% VAT
            final = total + vat

            self.vat_var.set(f"{vat:,.0f}")
            self.total_var.set(f"{final:,.0f}")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập số hợp lệ")

    def _update_review(self):
        """Update review text."""
        review = f"""
THÔNG TIN HỢP ĐỒNG

KHÁCH HÀNG:
- Tên: {self.selected_customer.get('full_name', 'N/A') if self.selected_customer else 'N/A'}
- SĐT: {self.selected_customer.get('phone', 'N/A') if self.selected_customer else 'N/A'}

XE:
- Hãng/Model: {self.selected_car.get('brand', 'N/A') if self.selected_car else 'N/A'} {self.selected_car.get('model', 'N/A') if self.selected_car else 'N/A'}
- Năm SX: {self.selected_car.get('year', 'N/A') if self.selected_car else 'N/A'}
- Màu: {self.selected_car.get('color', 'N/A') if self.selected_car else 'N/A'}

GIÁ CẢ:
- Giá xe: {float(self.car_price_var.get() or 0):,.0f} VNĐ
- Giảm giá: {float(self.discount_var.get() or 0):,.0f} VNĐ
- Lý do: {self.discount_reason_var.get() or 'Không có'}
- VAT (10%): {float(self.vat_var.get().replace(',', '') or 0):,.0f} VNĐ
- TỔNG THANH TOÁN: {float(self.total_var.get().replace(',', '') or 0):,.0f} VNĐ
"""
        self.review_text.config(state='normal')
        self.review_text.delete('1.0', tk.END)
        self.review_text.insert('1.0', review)
        self.review_text.config(state='disabled')

    def _save_draft(self):
        """Save contract as draft."""
        self._save_contract()

    def _save_contract(self):
        """Save contract to database."""
        if not self.selected_customer or not self.selected_car:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đầy đủ khách hàng và xe")
            return

        data = {
            'customer_id': self.selected_customer.get('id'),
            'car_id': self.selected_car.get('id'),
            'car_price': float(self.car_price_var.get() or 0),
            'discount_amount': float(self.discount_var.get() or 0),
            'discount_reason': self.discount_reason_var.get()
        }

        result = self.contract_service.create_contract(data, self.created_by)

        if result.success:
            messagebox.showinfo("Thành công", "Hợp đồng đã được tạo thành công")
            if self.on_save:
                self.on_save(result.data)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", f"Không thể tạo hợp đồng: {result.error}")
