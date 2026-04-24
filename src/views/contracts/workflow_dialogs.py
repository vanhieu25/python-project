"""
Workflow Dialogs Module
Dialogs for approval, signature, and delivery workflow actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Callable

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.contract_workflow_service import ContractWorkflowService, WorkflowResult


class ApprovalDialog(tk.Toplevel):
    """Dialog for approving or rejecting contracts."""

    def __init__(
        self,
        parent: tk.Widget,
        workflow_service: ContractWorkflowService,
        contract_id: int,
        approver_id: int,
        action: str = 'approve',  # 'approve' or 'reject'
        on_complete: Optional[Callable] = None
    ):
        """Initialize approval dialog.

        Args:
            parent: Parent widget
            workflow_service: Workflow service instance
            contract_id: Contract ID to approve/reject
            approver_id: Approver user ID
            action: 'approve' or 'reject'
            on_complete: Callback when action complete
        """
        super().__init__(parent)
        self.workflow_service = workflow_service
        self.contract_id = contract_id
        self.approver_id = approver_id
        self.action = action
        self.on_complete = on_complete

        self.title("Phê duyệt hợp đồng" if action == 'approve' else "Từ chối hợp đồng")
        self.geometry("400x300")
        self.resizable(False, False)

        self._create_widgets()

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Header
        header_text = (
            "Xác nhận PHÊ DUYỆT hợp đồng"
            if self.action == 'approve'
            else "Xác nhận TỪ CHỐI hợp đồng"
        )
        header_color = '#4CAF50' if self.action == 'approve' else '#F44336'

        header = tk.Frame(self, bg=header_color, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=header_text,
            font=('Arial', 12, 'bold'),
            bg=header_color,
            fg='white'
        ).pack(pady=8)

        # Content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Notes
        tk.Label(
            content,
            text="Ghi chú (không bắt buộc):" if self.action == 'approve' else "Lý do từ chối (bắt buộc):",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))

        self.notes_text = tk.Text(content, height=6, width=40)
        self.notes_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        ).pack(side=tk.LEFT)

        action_text = "Phê duyệt" if self.action == 'approve' else "Từ chối"
        action_color = '#4CAF50' if self.action == 'approve' else '#F44336'

        tk.Button(
            button_frame,
            text=action_text,
            bg=action_color,
            fg='white',
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _confirm(self):
        """Handle confirm button click."""
        notes = self.notes_text.get('1.0', tk.END).strip()

        if self.action == 'reject' and not notes:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập lý do từ chối")
            return

        # Execute action
        if self.action == 'approve':
            result = self.workflow_service.approve(
                self.contract_id, self.approver_id, notes
            )
        else:
            result = self.workflow_service.reject(
                self.contract_id, self.approver_id, notes
            )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            if self.on_complete:
                self.on_complete(result)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.message)


class SignatureDialog(tk.Toplevel):
    """Dialog for recording contract signatures."""

    def __init__(
        self,
        parent: tk.Widget,
        workflow_service: ContractWorkflowService,
        contract_id: int,
        user_id: int,
        on_complete: Optional[Callable] = None
    ):
        """Initialize signature dialog.

        Args:
            parent: Parent widget
            workflow_service: Workflow service instance
            contract_id: Contract ID
            user_id: User recording signatures
            on_complete: Callback when complete
        """
        super().__init__(parent)
        self.workflow_service = workflow_service
        self.contract_id = contract_id
        self.user_id = user_id
        self.on_complete = on_complete

        self.title("Ký hợp đồng")
        self.geometry("400x350")
        self.resizable(False, False)

        self._create_widgets()

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Header
        header = tk.Frame(self, bg='#9C27B0', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Xác nhận ký hợp đồng",
            font=('Arial', 12, 'bold'),
            bg='#9C27B0',
            fg='white'
        ).pack(pady=8)

        # Content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Signature checkboxes
        tk.Label(
            content,
            text="Chữ ký đã thu thập:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 10))

        self.customer_signed = tk.BooleanVar(value=False)
        tk.Checkbutton(
            content,
            text="Khách hàng đã ký",
            variable=self.customer_signed
        ).pack(anchor='w', pady=5)

        self.rep_signed = tk.BooleanVar(value=False)
        tk.Checkbutton(
            content,
            text="Đại diện công ty đã ký",
            variable=self.rep_signed
        ).pack(anchor='w', pady=5)

        # Notes
        tk.Label(
            content,
            text="Ghi chú:",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(15, 5))

        self.notes_text = tk.Text(content, height=4, width=40)
        self.notes_text.pack(fill=tk.X)

        # Info label
        tk.Label(
            content,
            text="Lưu ý: Cần đủ cả 2 chữ ký để chuyển sang trạng thái 'Đã ký'",
            fg='gray',
            font=('Arial', 9)
        ).pack(anchor='w', pady=(10, 0))

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="Xác nhận ký",
            bg='#9C27B0',
            fg='white',
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _confirm(self):
        """Handle confirm button click."""
        notes = self.notes_text.get('1.0', tk.END).strip()

        result = self.workflow_service.mark_signed(
            self.contract_id,
            self.user_id,
            signed_by_customer=self.customer_signed.get(),
            signed_by_representative=self.rep_signed.get(),
            notes=notes
        )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            if self.on_complete:
                self.on_complete(result)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.message)


class PaymentDialog(tk.Toplevel):
    """Dialog for recording payments."""

    def __init__(
        self,
        parent: tk.Widget,
        workflow_service: ContractWorkflowService,
        contract_id: int,
        user_id: int,
        remaining_amount: float = 0,
        on_complete: Optional[Callable] = None
    ):
        """Initialize payment dialog.

        Args:
            parent: Parent widget
            workflow_service: Workflow service instance
            contract_id: Contract ID
            user_id: User recording payment
            remaining_amount: Remaining amount to pay
            on_complete: Callback when complete
        """
        super().__init__(parent)
        self.workflow_service = workflow_service
        self.contract_id = contract_id
        self.user_id = user_id
        self.remaining_amount = remaining_amount
        self.on_complete = on_complete

        self.title("Ghi nhận thanh toán")
        self.geometry("400x400")
        self.resizable(False, False)

        self._create_widgets()

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Header
        header = tk.Frame(self, bg='#2196F3', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Ghi nhận thanh toán",
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='white'
        ).pack(pady=8)

        # Content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Remaining amount info
        tk.Label(
            content,
            text=f"Số tiền còn lại: {self.remaining_amount:,.0f} VNĐ",
            font=('Arial', 11, 'bold'),
            fg='red'
        ).pack(anchor='w', pady=(0, 15))

        # Amount
        tk.Label(content, text="Số tiền thanh toán:").pack(anchor='w')
        self.amount_var = tk.StringVar()
        tk.Entry(content, textvariable=self.amount_var, width=25).pack(anchor='w', pady=5)

        # Payment method
        tk.Label(content, text="Phương thức thanh toán:").pack(anchor='w', pady=(10, 0))
        self.method_var = tk.StringVar(value='cash')
        methods = ttk.Combobox(
            content,
            textvariable=self.method_var,
            values=['cash', 'bank_transfer', 'card', 'check'],
            width=23,
            state='readonly'
        )
        methods.pack(anchor='w', pady=5)

        # Notes
        tk.Label(content, text="Ghi chú:").pack(anchor='w', pady=(10, 0))
        self.notes_text = tk.Text(content, height=4, width=40)
        self.notes_text.pack(fill=tk.X, pady=5)

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="Ghi nhận",
            bg='#2196F3',
            fg='white',
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _confirm(self):
        """Handle confirm button click."""
        try:
            amount = float(self.amount_var.get().replace(',', ''))
        except ValueError:
            messagebox.showwarning("Lỗi", "Vui lòng nhập số tiền hợp lệ")
            return

        if amount <= 0:
            messagebox.showwarning("Lỗi", "Số tiền phải lớn hơn 0")
            return

        notes = self.notes_text.get('1.0', tk.END).strip()

        result = self.workflow_service.record_payment(
            self.contract_id,
            self.user_id,
            amount,
            payment_method=self.method_var.get(),
            notes=notes
        )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            if self.on_complete:
                self.on_complete(result)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.message)


class DeliveryDialog(tk.Toplevel):
    """Dialog for confirming delivery."""

    def __init__(
        self,
        parent: tk.Widget,
        workflow_service: ContractWorkflowService,
        contract_id: int,
        user_id: int,
        on_complete: Optional[Callable] = None
    ):
        """Initialize delivery dialog.

        Args:
            parent: Parent widget
            workflow_service: Workflow service instance
            contract_id: Contract ID
            user_id: User confirming delivery
            on_complete: Callback when complete
        """
        super().__init__(parent)
        self.workflow_service = workflow_service
        self.contract_id = contract_id
        self.user_id = user_id
        self.on_complete = on_complete

        self.title("Xác nhận giao xe")
        self.geometry("400x350")
        self.resizable(False, False)

        self._create_widgets()

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Header
        header = tk.Frame(self, bg='#009688', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Xác nhận giao xe",
            font=('Arial', 12, 'bold'),
            bg='#009688',
            fg='white'
        ).pack(pady=8)

        # Content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Delivery date
        tk.Label(content, text="Ngày giao xe:").pack(anchor='w')
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        tk.Entry(content, textvariable=self.date_var, width=20).pack(anchor='w', pady=5)

        # Confirmation checkbox
        self.confirmed = tk.BooleanVar(value=False)
        tk.Checkbutton(
            content,
            text="Xác nhận đã giao xe cho khách hàng",
            variable=self.confirmed
        ).pack(anchor='w', pady=15)

        # Notes
        tk.Label(content, text="Ghi chú giao xe:").pack(anchor='w')
        self.notes_text = tk.Text(content, height=6, width=40)
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Warning
        tk.Label(
            content,
            text="Lưu ý: Sau khi giao xe, hợp đồng không thể chỉnh sửa",
            fg='red',
            font=('Arial', 9)
        ).pack(anchor='w', pady=(5, 0))

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Hủy",
            command=self.destroy
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="Xác nhận giao xe",
            bg='#009688',
            fg='white',
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _confirm(self):
        """Handle confirm button click."""
        if not self.confirmed.get():
            messagebox.showwarning("Thiếu xác nhận", "Vui lòng tick xác nhận đã giao xe")
            return

        # Parse date
        try:
            date_str = self.date_var.get()
            delivery_date = datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showwarning("Lỗi", "Vui lòng nhập ngày đúng định dạng DD/MM/YYYY")
            return

        notes = self.notes_text.get('1.0', tk.END).strip()

        result = self.workflow_service.mark_delivered(
            self.contract_id,
            self.user_id,
            delivery_date,
            notes
        )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            if self.on_complete:
                self.on_complete(result)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.message)


class CancelDialog(tk.Toplevel):
    """Dialog for cancelling contracts."""

    def __init__(
        self,
        parent: tk.Widget,
        workflow_service: ContractWorkflowService,
        contract_id: int,
        user_id: int,
        on_complete: Optional[Callable] = None
    ):
        """Initialize cancel dialog.

        Args:
            parent: Parent widget
            workflow_service: Workflow service instance
            contract_id: Contract ID
            user_id: User cancelling
            on_complete: Callback when complete
        """
        super().__init__(parent)
        self.workflow_service = workflow_service
        self.contract_id = contract_id
        self.user_id = user_id
        self.on_complete = on_complete

        self.title("Hủy hợp đồng")
        self.geometry("400x300")
        self.resizable(False, False)

        self._create_widgets()

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Header
        header = tk.Frame(self, bg='#F44336', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Xác nhận HỦY hợp đồng",
            font=('Arial', 12, 'bold'),
            bg='#F44336',
            fg='white'
        ).pack(pady=8)

        # Warning
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            content,
            text="Cảnh báo: Hành động này không thể hoàn tác!",
            fg='red',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 15))

        # Reason
        tk.Label(content, text="Lý do hủy (bắt buộc):").pack(anchor='w')
        self.reason_text = tk.Text(content, height=6, width=40)
        self.reason_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons
        button_frame = tk.Frame(self, padx=20, pady=15)
        button_frame.pack(fill=tk.X)

        tk.Button(
            button_frame,
            text="Không hủy",
            command=self.destroy
        ).pack(side=tk.LEFT)

        tk.Button(
            button_frame,
            text="Xác nhận HỦY",
            bg='#F44336',
            fg='white',
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _confirm(self):
        """Handle confirm button click."""
        reason = self.reason_text.get('1.0', tk.END).strip()

        if not reason:
            messagebox.showwarning("Thiếu lý do", "Vui lòng nhập lý do hủy hợp đồng")
            return

        if not messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn HỦY hợp đồng này?\nHành động này không thể hoàn tác."
        ):
            return

        result = self.workflow_service.cancel(
            self.contract_id,
            self.user_id,
            reason
        )

        if result.success:
            messagebox.showinfo("Thành công", result.message)
            if self.on_complete:
                self.on_complete(result)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", result.message)
