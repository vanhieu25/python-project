"""
Car Management UI Module
List view for car management with full CRUD.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List

from ...models.car import Car
from ...repositories.car_repository import CarRepository
from ...repositories.car_history_repository import CarHistoryRepository
from ...services.car_service import CarService
from ...database.db_helper import DatabaseHelper


class CarListView(ttk.Frame):
    """List view for cars with full CRUD operations."""

    def __init__(self, parent, db_helper: DatabaseHelper,
                 current_user_id: int = 1, **kwargs):
        """Initialize car list view.

        Args:
            parent: Parent widget
            db_helper: DatabaseHelper instance
            current_user_id: Current user ID for audit
        """
        super().__init__(parent, **kwargs)
        self.db = db_helper
        self.current_user_id = current_user_id

        # Initialize service layer
        self.car_repo = CarRepository(self.db)
        self.history_repo = CarHistoryRepository(self.db)
        self.car_service = CarService(self.car_repo, self.history_repo)

        self._create_widgets()
        self._load_cars()

    def _create_widgets(self):
        """Create UI widgets."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            title_frame,
            text="🚗 Quản Lý Xe",
            font=('Helvetica', 16, 'bold')
        ).pack(side=tk.LEFT)

        # Action buttons
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(
            btn_frame,
            text="➕ Thêm xe",
            command=self._on_add_car
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🔄 Làm mới",
            command=self._load_cars
        ).pack(side=tk.LEFT, padx=5)

        # Filter frame
        filter_frame = ttk.LabelFrame(self, text="Bộ lọc", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Status filter
        ttk.Label(filter_frame, text="Trạng thái:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["all", "available", "sold", "reserved", "maintenance"],
            width=15,
            state="readonly"
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._load_cars())

        # Statistics
        self.stats_label = ttk.Label(filter_frame, text="")
        self.stats_label.pack(side=tk.RIGHT)

        # Treeview for cars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        # Treeview
        columns = ('id', 'vin', 'license_plate', 'brand', 'model', 'year', 'color', 'price', 'status')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('vin', text='VIN')
        self.tree.heading('license_plate', text='Biển số')
        self.tree.heading('brand', text='Hãng')
        self.tree.heading('model', text='Model')
        self.tree.heading('year', text='Năm SX')
        self.tree.heading('color', text='Màu')
        self.tree.heading('price', text='Giá bán')
        self.tree.heading('status', text='Trạng thái')

        # Column widths
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('vin', width=120)
        self.tree.column('license_plate', width=80, anchor='center')
        self.tree.column('brand', width=100)
        self.tree.column('model', width=100)
        self.tree.column('year', width=60, anchor='center')
        self.tree.column('color', width=60, anchor='center')
        self.tree.column('price', width=100, anchor='e')
        self.tree.column('status', width=80, anchor='center')

        # Pack tree and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Xem chi tiết", command=self._on_view_car)
        self.context_menu.add_command(label="Sửa", command=self._on_edit_car)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Xóa", command=self._on_delete_car)

        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self._on_view_car())

        # Status bar
        self.status_bar = ttk.Label(self, text="Sẵn sàng")
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    def _load_cars(self):
        """Load cars into treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter
        status = self.status_var.get()
        if status == "all":
            status = None

        # Load cars via service
        try:
            cars = self.car_service.list_cars(status=status)

            # Insert into tree
            for car in cars:
                status_text = self._get_status_text(car.status)
                price_text = car.get_price_display() if car.selling_price else "-"

                self.tree.insert('', tk.END, values=(
                    car.id,
                    car.get_short_vin(),
                    car.license_plate or "-",
                    car.brand,
                    car.model,
                    car.year or "-",
                    car.color or "-",
                    price_text,
                    status_text
                ))

            # Update statistics
            stats = self.car_service.get_car_statistics()
            self.stats_label.config(
                text=f"Tổng: {stats['total']} | Còn: {stats['available']} | Đã bán: {stats['sold']} | Đặt: {stats['reserved']}"
            )
            self.status_bar.config(text=f"Đã tải {len(cars)} xe")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách xe: {str(e)}")

    def _get_status_text(self, status: str) -> str:
        """Get Vietnamese status text."""
        status_map = {
            'available': 'Còn hàng',
            'sold': 'Đã bán',
            'reserved': 'Đã đặt',
            'maintenance': 'Bảo dưỡng',
            'incoming': 'Sắp về'
        }
        return status_map.get(status, status)

    def _show_context_menu(self, event):
        """Show context menu on right click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _get_selected_car_id(self) -> Optional[int]:
        """Get ID of selected car."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]

    def _on_add_car(self):
        """Handle add car button."""
        from .car_dialog import CarDialog
        dialog = CarDialog(self, self.car_service, current_user_id=self.current_user_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_cars()

    def _on_view_car(self):
        """Handle view car."""
        car_id = self._get_selected_car_id()
        if not car_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một xe")
            return

        try:
            car = self.car_service.get_car(car_id)
            profit = car.calculate_profit()
            profit_str = f"{profit:,.0f} VNĐ ({car.get_profit_margin():.1f}%)" if profit else "Chưa có"

            info = f"""VIN: {car.vin}
Biển số: {car.license_plate or 'Chưa có'}
Hãng/Model: {car.brand} {car.model}
Năm SX: {car.year or 'Chưa có'}
Màu: {car.color or 'Chưa có'}
Hộp số: {car.transmission or 'Chưa có'}
Nhiên liệu: {car.fuel_type or 'Chưa có'}
Số km: {car.mileage:,} km
Giá nhập: {car.get_price_display('purchase')}
Giá bán: {car.get_price_display('selling')}
Lợi nhuận: {profit_str}
Trạng thái: {self._get_status_text(car.status)}
Mô tả: {car.description or 'Không có'}"""

            messagebox.showinfo("Thông tin xe", info)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _on_edit_car(self):
        """Handle edit car."""
        car_id = self._get_selected_car_id()
        if not car_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một xe để sửa")
            return

        try:
            car = self.car_service.get_car(car_id)
            from .car_dialog import CarDialog
            dialog = CarDialog(self, self.car_service, car=car,
                             current_user_id=self.current_user_id)
            self.wait_window(dialog)
            if dialog.result:
                self._load_cars()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _on_delete_car(self):
        """Handle delete car."""
        car_id = self._get_selected_car_id()
        if not car_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một xe để xóa")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa xe này?"):
            try:
                self.car_service.delete_car(car_id, self.current_user_id)
                messagebox.showinfo("Thành công", "Đã xóa xe")
                self._load_cars()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))


class CarManagementWindow(tk.Toplevel):
    """Standalone window for car management."""

    def __init__(self, parent, db_helper: DatabaseHelper, current_user_id: int = 1):
        """Initialize car management window.

        Args:
            parent: Parent window
            db_helper: DatabaseHelper instance
            current_user_id: Current user ID
        """
        super().__init__(parent)
        self.title("Quản Lý Xe")
        self.geometry("1200x700")
        self.minsize(900, 500)

        # Create main view
        self.car_list = CarListView(self, db_helper, current_user_id)
        self.car_list.pack(fill=tk.BOTH, expand=True)

        # Center window
        self.transient(parent)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


def open_car_management(parent: tk.Tk, db_path: str = "data/car_management.db",
                       current_user_id: int = 1):
    """Open car management window.

    Args:
        parent: Parent Tk instance
        db_path: Path to database file
        current_user_id: Current user ID
    """
    from ...database.db_helper import DatabaseHelper
    db = DatabaseHelper(db_path)
    CarManagementWindow(parent, db, current_user_id)


if __name__ == "__main__":
    # Demo
    root = tk.Tk()
    root.title("Car Management Demo")
    root.geometry("200x100")

    db = DatabaseHelper()
    btn = ttk.Button(
        root,
        text="Mở Quản Lý Xe",
        command=lambda: CarManagementWindow(root, db)
    )
    btn.pack(padx=20, pady=20)

    root.mainloop()
