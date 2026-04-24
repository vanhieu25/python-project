"""
Car Dialog Module
Add/Edit dialog for cars.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any

from ...models.car import Car
from ...services.car_service import CarService


class CarDialog(tk.Toplevel):
    """Dialog for adding/editing cars."""

    def __init__(self, parent, car_service: CarService,
                 car: Optional[Car] = None,
                 on_save: Optional[Callable] = None,
                 current_user_id: int = 1):
        """Initialize car dialog.

        Args:
            parent: Parent window
            car_service: CarService instance
            car: Car to edit (None for new car)
            on_save: Callback after save
            current_user_id: Current user ID
        """
        super().__init__(parent)
        self.car_service = car_service
        self.car = car
        self.on_save = on_save
        self.current_user_id = current_user_id
        self.result = None

        # Set title
        if car:
            self.title("Sửa thông tin xe")
        else:
            self.title("Thêm xe mới")

        self.geometry("600x700")
        self.minsize(500, 600)

        self._create_widgets()
        self._load_data()

        # Make modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create UI widgets."""
        # Main frame with scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)

        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.form_frame, anchor=tk.NW, width=560)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Form fields
        row = 0

        # VIN
        ttk.Label(self.form_frame, text="VIN *").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vin_var = tk.StringVar()
        self.vin_entry = ttk.Entry(self.form_frame, textvariable=self.vin_var, width=40)
        self.vin_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        self.vin_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.vin_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # License Plate
        ttk.Label(self.form_frame, text="Biển số").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.plate_var = tk.StringVar()
        self.plate_entry = ttk.Entry(self.form_frame, textvariable=self.plate_var, width=20)
        self.plate_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.plate_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.plate_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Brand
        ttk.Label(self.form_frame, text="Hãng xe *").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.brand_var = tk.StringVar()
        self.brand_combo = ttk.Combobox(self.form_frame, textvariable=self.brand_var, width=25)
        self.brand_combo['values'] = self._get_brands()
        self.brand_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.brand_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.brand_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Model
        ttk.Label(self.form_frame, text="Model *").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_entry = ttk.Entry(self.form_frame, textvariable=self.model_var, width=25)
        self.model_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.model_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.model_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Year
        ttk.Label(self.form_frame, text="Năm SX").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.year_var = tk.StringVar()
        self.year_entry = ttk.Entry(self.form_frame, textvariable=self.year_var, width=10)
        self.year_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.year_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.year_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Color
        ttk.Label(self.form_frame, text="Màu sắc").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.color_var = tk.StringVar()
        self.color_entry = ttk.Entry(self.form_frame, textvariable=self.color_var, width=20)
        self.color_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Transmission
        ttk.Label(self.form_frame, text="Hộp số").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.trans_var = tk.StringVar()
        self.trans_combo = ttk.Combobox(self.form_frame, textvariable=self.trans_var,
                                         values=['auto', 'manual', 'cvt'], width=15, state='readonly')
        self.trans_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Fuel Type
        ttk.Label(self.form_frame, text="Nhiên liệu").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fuel_var = tk.StringVar()
        self.fuel_combo = ttk.Combobox(self.form_frame, textvariable=self.fuel_var,
                                        values=['gasoline', 'diesel', 'electric', 'hybrid'],
                                        width=15, state='readonly')
        self.fuel_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Mileage
        ttk.Label(self.form_frame, text="Số km").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.mileage_var = tk.StringVar()
        self.mileage_entry = ttk.Entry(self.form_frame, textvariable=self.mileage_var, width=15)
        self.mileage_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.mileage_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.mileage_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Purchase Price
        ttk.Label(self.form_frame, text="Giá nhập").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.purchase_var = tk.StringVar()
        self.purchase_entry = ttk.Entry(self.form_frame, textvariable=self.purchase_var, width=20)
        self.purchase_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(self.form_frame, text="VNĐ").grid(row=row, column=2, sticky=tk.W, pady=5)
        self.purchase_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.purchase_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Selling Price
        ttk.Label(self.form_frame, text="Giá bán *").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.selling_var = tk.StringVar()
        self.selling_entry = ttk.Entry(self.form_frame, textvariable=self.selling_var, width=20)
        self.selling_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(self.form_frame, text="VNĐ").grid(row=row, column=2, sticky=tk.W, pady=5)
        self.selling_error = ttk.Label(self.form_frame, text="", foreground="red")
        self.selling_error.grid(row=row, column=1, sticky=tk.W, pady=(25, 0))
        row += 1

        # Status
        ttk.Label(self.form_frame, text="Trạng thái").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value='available')
        self.status_combo = ttk.Combobox(self.form_frame, textvariable=self.status_var,
                                          values=['available', 'sold', 'reserved', 'maintenance'],
                                          width=15, state='readonly')
        self.status_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Description
        ttk.Label(self.form_frame, text="Mô tả").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.desc_text = tk.Text(self.form_frame, width=40, height=5)
        self.desc_text.grid(row=row, column=1, sticky=tk.EW, pady=5)
        row += 1

        # Configure grid
        self.form_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Lưu", command=self._on_save).pack(side=tk.RIGHT, padx=5)

        # Bind validation
        self.vin_entry.bind('<FocusOut>', lambda e: self._validate_field('vin', self.vin_var.get()))
        self.plate_entry.bind('<FocusOut>', lambda e: self._validate_field('license_plate', self.plate_var.get()))
        self.brand_combo.bind('<FocusOut>', lambda e: self._validate_field('brand', self.brand_var.get()))
        self.model_entry.bind('<FocusOut>', lambda e: self._validate_field('model', self.model_var.get()))
        self.year_entry.bind('<FocusOut>', lambda e: self._validate_field('year', self.year_var.get()))
        self.mileage_entry.bind('<FocusOut>', lambda e: self._validate_field('mileage', self.mileage_var.get()))
        self.purchase_entry.bind('<FocusOut>', lambda e: self._validate_field('purchase_price', self.purchase_var.get()))
        self.selling_entry.bind('<FocusOut>', lambda e: self._validate_field('selling_price', self.selling_var.get()))

    def _get_brands(self) -> tuple:
        """Get list of brands for combobox."""
        return ('Toyota', 'Honda', 'Mazda', 'Hyundai', 'Kia', 'Ford',
                'Mitsubishi', 'Suzuki', 'BMW', 'Mercedes-Benz', 'Audi',
                'VinFast', 'Chevrolet', 'Nissan', 'Lexus', 'Porsche',
                'Land Rover', 'Volkswagen', 'Volvo', 'Subaru')

    def _load_data(self):
        """Load car data if editing."""
        if not self.car:
            return

        # Disable VIN for edit
        self.vin_entry.config(state='disabled')

        # Load values
        self.vin_var.set(self.car.vin or '')
        self.plate_var.set(self.car.license_plate or '')
        self.brand_var.set(self.car.brand or '')
        self.model_var.set(self.car.model or '')
        self.year_var.set(str(self.car.year) if self.car.year else '')
        self.color_var.set(self.car.color or '')
        self.trans_var.set(self.car.transmission or '')
        self.fuel_var.set(self.car.fuel_type or '')
        self.mileage_var.set(str(self.car.mileage) if self.car.mileage else '0')
        self.purchase_var.set(str(self.car.purchase_price) if self.car.purchase_price else '')
        self.selling_var.set(str(self.car.selling_price) if self.car.selling_price else '')
        self.status_var.set(self.car.status or 'available')
        self.desc_text.delete('1.0', tk.END)
        self.desc_text.insert('1.0', self.car.description or '')

    def _validate_field(self, field_name: str, value: str) -> bool:
        """Validate a single field."""
        error_label = getattr(self, f"{field_name}_error", None)
        if error_label is None:
            return True

        # Map field names
        field_map = {
            'license_plate': 'plate',
            'purchase_price': 'purchase',
            'selling_price': 'selling'
        }
        error_label_name = field_map.get(field_name, field_name)
        error_label = getattr(self, f"{error_label_name}_error", None)

        if error_label is None:
            return True

        # Validate
        if value == '':
            error_label.config(text="")
            return True

        error = self.car_service.validate_field(field_name, value)
        if error:
            error_label.config(text=error)
            return False
        else:
            error_label.config(text="")
            return True

    def _validate_all(self) -> bool:
        """Validate all required fields."""
        is_valid = True

        # Required fields
        if not self.vin_var.get().strip():
            self.vin_error.config(text="VIN không được để trống")
            is_valid = False
        else:
            if not self._validate_field('vin', self.vin_var.get()):
                is_valid = False

        if not self.brand_var.get().strip():
            self.brand_error.config(text="Hãng xe không được để trống")
            is_valid = False
        else:
            self.brand_error.config(text="")

        if not self.model_var.get().strip():
            self.model_error.config(text="Model không được để trống")
            is_valid = False
        else:
            self.model_error.config(text="")

        # Validate optional fields if provided
        self._validate_field('year', self.year_var.get())
        self._validate_field('license_plate', self.plate_var.get())
        self._validate_field('mileage', self.mileage_var.get())
        self._validate_field('purchase_price', self.purchase_var.get())
        self._validate_field('selling_price', self.selling_var.get())

        return is_valid

    def _on_save(self):
        """Handle save button."""
        if not self._validate_all():
            messagebox.showerror("Lỗi", "Vui lòng sửa các lỗi trước khi lưu")
            return

        # Build car data
        car_data = {
            'vin': self.vin_var.get().strip(),
            'license_plate': self.plate_var.get().strip() or None,
            'brand': self.brand_var.get().strip(),
            'model': self.model_var.get().strip(),
            'color': self.color_var.get().strip() or None,
            'transmission': self.trans_var.get() or None,
            'fuel_type': self.fuel_var.get() or None,
            'status': self.status_var.get(),
            'description': self.desc_text.get('1.0', tk.END).strip() or None
        }

        # Numeric fields
        if self.year_var.get():
            car_data['year'] = int(self.year_var.get())
        if self.mileage_var.get():
            car_data['mileage'] = int(self.mileage_var.get())
        if self.purchase_var.get():
            car_data['purchase_price'] = float(self.purchase_var.get())
        if self.selling_var.get():
            car_data['selling_price'] = float(self.selling_var.get())

        try:
            if self.car:
                # Update
                updated_car = self.car_service.update_car(
                    self.car.id, car_data, self.current_user_id
                )
                self.result = updated_car
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin xe")
            else:
                # Create
                new_car = self.car_service.create_car(car_data, self.current_user_id)
                self.result = new_car
                messagebox.showinfo("Thành công", "Đã thêm xe mới")

            if self.on_save:
                self.on_save(self.result)

            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


class CarHistoryDialog(tk.Toplevel):
    """Dialog for showing car history."""

    def __init__(self, parent, car_service: CarService, car_id: int):
        """Initialize history dialog.

        Args:
            parent: Parent window
            car_service: CarService instance
            car_id: Car ID
        """
        super().__init__(parent)
        self.title("Lịch sử thay đổi")
        self.geometry("700x500")

        self._create_widgets()
        self._load_history(car_id)

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self):
        """Create UI widgets."""
        # Title
        ttk.Label(self, text="Lịch sử thay đổi", font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Treeview
        columns = ('time', 'action', 'field', 'old', 'new', 'user')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        self.tree.heading('time', text='Thời gian')
        self.tree.heading('action', text='Hành động')
        self.tree.heading('field', text='Trường')
        self.tree.heading('old', text='Giá trị cũ')
        self.tree.heading('new', text='Giá trị mới')
        self.tree.heading('user', text='Người thực hiện')

        self.tree.column('time', width=120)
        self.tree.column('action', width=80)
        self.tree.column('field', width=80)
        self.tree.column('old', width=120)
        self.tree.column('new', width=120)
        self.tree.column('user', width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Close button
        ttk.Button(self, text="Đóng", command=self.destroy).pack(pady=10)

    def _load_history(self, car_id: int):
        """Load history data."""
        # This would need car_service to expose history
        # For now, show placeholder
        pass
