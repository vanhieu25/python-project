# Tech Stack - Quản Lý Đại Lý Xe Hơi

**Phiên bản**: 1.0  
**Ngày cập nhật**: 20/04/2026  
**Nhóm**: Nhóm 4

---

## Mục Lục

1. [Tổng Quan Công Nghệ](#1-tổng-quan-công-nghệ)
2. [Python](#2-python)
3. [PyQT6](#3-pyqt6)
4. [SQLite](#4-sqlite)
5. [Thư Viện Hỗ Trợ](#5-thư-viện-hỗ-trợ)
6. [Cài Đặt & Cấu Hình](#6-cài-đặt--cấu-hình)
7. [Cấu Trúc Project](#7-cấu-trúc-project)
8. [Coding Conventions](#8-coding-conventions)
9. [Build & Deploy](#9-build--deploy)

---

## 1. Tổng Quan Công Nghệ

### 1.1 Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────┐
│              PRESENTATION LAYER                  │
│                  (PyQT6 GUI)                     │
│  ┌─────────┬─────────┬─────────┬─────────┐     │
│  │  Views  │ Widgets │ Dialogs │ Screens  │     │
│  └─────────┴─────────┴─────────┴─────────┘     │
├─────────────────────────────────────────────────┤
│              BUSINESS LOGIC LAYER                │
│                (Python Core)                     │
│  ┌─────────┬─────────┬─────────┬─────────┐     │
│  │ Models  │Services │Controllers│ Utils   │     │
│  └─────────┴─────────┴─────────┴─────────┘     │
├─────────────────────────────────────────────────┤
│              DATA ACCESS LAYER                   │
│               (SQLite + ORM)                     │
│  ┌─────────┬─────────┬─────────┬─────────┐     │
│  │ Repository │ DAO  │  Query  │  Cache  │     │
│  └─────────┴─────────┴─────────┴─────────┘     │
├─────────────────────────────────────────────────┤
│              DATABASE LAYER                      │
│              (SQLite3 File)                      │
│           car_management.db                      │
└─────────────────────────────────────────────────┘
```

### 1.2 Sơ Đồ Luồng Dữ Liệu

```
User Action → PyQt6 Signal → Controller → Service → Model → Database
                ↑                                               ↓
                └────────────── Response ←──────────────────────┘
```

### 1.3 Lý Do Chọn Công Nghệ

| Công nghệ  | Lý do chọn                                                              |
| ---------- | ----------------------------------------------------------------------- |
| **Python** | Dễ học, cú pháp rõ ràng, thư viện phong phú, phù hợp cho desktop app    |
| **PyQT6**  | GUI mạnh mẽ, cross-platform, binding Python-Qt xuất sắc, widget đa dạng |
| **SQLite** | Embedded, không cần server, nhẹ, đủ mạnh cho ứng dụng desktop           |

---

## 2. Python

### 2.1 Phiên Bản

- **Yêu cầu**: Python 3.8 trở lên
- **Khuyến nghị**: Python 3.10+ (hỗ trợ pattern matching, type hints tốt hơn)
- **Kiểm tra phiên bản**:

```bash
python --version
# hoặc
python3 --version
```

### 2.2 Tính Năng Sử Dụng

```python
# Type hints (Python 3.8+)
from typing import Optional, List, Dict, Any

def get_car_by_id(car_id: int) -> Optional[Dict[str, Any]]:
    pass

# Data classes (Python 3.7+)
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Car:
    id: int
    license_plate: str
    brand: str
    model: str
    year: int
    color: str
    selling_price: float
    status: str = "available"
    created_at: datetime = field(default_factory=datetime.now)

# f-strings (Python 3.6+)
message = f"Xe {car.brand} {car.model} có giá {car.selling_price:,.0f} VNĐ"

# Context managers
with open("log.txt", "a", encoding="utf-8") as f:
    f.write(log_message)

# Async/await (cho các tác vụ I/O nếu cần)
async def fetch_data():
    pass
```

### 2.3 Thư Viện Chuẩn Sử Dụng

| Module               | Mục đích                         |
| -------------------- | -------------------------------- |
| `sqlite3`            | Kết nối database (built-in)      |
| `datetime`           | Xử lý ngày giờ                   |
| `json`               | Export/Import dữ liệu            |
| `csv`                | Xuất/nhập CSV                    |
| `os` / `pathlib`     | Thao tác file system             |
| `logging`            | Ghi log ứng dụng                 |
| `hashlib` / `bcrypt` | Mã hóa mật khẩu                  |
| `re`                 | Regular expressions (validation) |

---

## 3. PyQT6

### 3.1 Phiên Bản

- **Yêu cầu**: PyQT6 6.4+
- **Cài đặt**:

```bash
pip install PyQt6
pip install PyQt6-tools  # Cho Qt Designer
```

### 3.2 Cấu Trúc Giao Diện

```
src/
├── views/
│   ├── __init__.py
│   ├── main_window.py          # Cửa sổ chính
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── car_dialog.py       # Form thêm/sửa xe
│   │   ├── customer_dialog.py  # Form khách hàng
│   │   └── transaction_dialog.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── car_table.py        # Bảng danh sách xe
│   │   ├── dashboard.py        # Dashboard widgets
│   │   └── search_bar.py       # Thanh tìm kiếm
│   └── screens/
│       ├── __init__.py
│       ├── car_screen.py
│       ├── customer_screen.py
│       └── report_screen.py
```

### 3.3 Widgets Chính Sử Dụng

| Widget                        | Mục đích              |
| ----------------------------- | --------------------- |
| `QMainWindow`                 | Cửa sổ chính          |
| `QDialog`                     | Dialog boxes          |
| `QWidget`                     | Container chung       |
| `QVBoxLayout` / `QHBoxLayout` | Layout dọc/ngang      |
| `QGridLayout`                 | Layout dạng lưới      |
| `QTableWidget` / `QTableView` | Hiển thị dữ liệu bảng |
| `QFormLayout`                 | Form nhập liệu        |
| `QLineEdit` / `QTextEdit`     | Input text            |
| `QComboBox`                   | Dropdown selection    |
| `QDateEdit` / `QDateTimeEdit` | Input ngày giờ        |
| `QSpinBox` / `QDoubleSpinBox` | Input số              |
| `QPushButton`                 | Button                |
| `QMenuBar` / `QToolBar`       | Menu và toolbar       |
| `QStatusBar`                  | Status bar            |
| `QTabWidget`                  | Tabbed interface      |
| `QStackedWidget`              | Multiple pages        |
| `QMessageBox`                 | Alert/Confirmation    |
| `QFileDialog`                 | Open/Save file dialog |
| `QProgressDialog`             | Progress indicator    |

### 3.4 Signals & Slots

```python
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton

# Custom signal
class CarManager(QObject):
    car_added = pyqtSignal(dict)
    car_updated = pyqtSignal(int, dict)
    car_deleted = pyqtSignal(int)

# Connection
btn_add.clicked.connect(self.on_add_car)
self.car_added.connect(self.update_table)

# Lambda với tham số
btn_edit.clicked.connect(lambda: self.edit_car(car_id))
```

### 3.5 Styling với Qt Stylesheets

```python
# Áp dụng stylesheet
self.setStyleSheet("""
    QMainWindow {
        background-color: #f5f5f7;
    }

    QPushButton {
        background-color: #0071e3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 14px;
    }

    QPushButton:hover {
        background-color: #0066cc;
    }

    QPushButton:pressed {
        background-color: #005bb5;
    }

    QTableWidget {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        gridline-color: #f0f0f0;
    }

    QTableWidget::item {
        padding: 8px;
    }

    QTableWidget::item:selected {
        background-color: #0071e3;
        color: white;
    }

    QLineEdit, QComboBox, QDateEdit {
        padding: 8px;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        font-size: 14px;
    }

    QLineEdit:focus {
        border: 2px solid #0071e3;
    }

    QLabel {
        font-size: 14px;
        color: #1d1d1f;
    }

    QLabel[style="heading"] {
        font-size: 24px;
        font-weight: bold;
        color: #1a365d;
    }
""")
```

### 3.6 Qt Designer

Sử dụng Qt Designer để thiết kế UI nhanh:

```bash
# Mở Qt Designer
pyqt6-tools designer

# Chuyển đổi .ui sang .py
pyuic6 -x form.ui -o form_ui.py

# Hoặc load trực tiếp .ui file
from PyQt6 import uic
uic.loadUi("form.ui", self)
```

---

## 4. SQLite

### 4.1 Phiên Bản

- **Yêu cầu**: SQLite 3.35+
- **Python module**: `sqlite3` (built-in, không cần cài thêm)

### 4.2 Database Schema

File database: `car_management.db`

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Bảng dealers
CREATE TABLE IF NOT EXISTS dealers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(50),
    website VARCHAR(100),
    contact_person VARCHAR(50),
    partnership_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng cars
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER,
    color VARCHAR(30),
    mileage INTEGER DEFAULT 0,
    transmission VARCHAR(20),
    fuel_type VARCHAR(20),
    cost_price DECIMAL(15,2) NOT NULL,
    selling_price DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'available',
    dealer_id INTEGER,
    import_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dealer_id) REFERENCES dealers(id) ON DELETE SET NULL
);

-- Bảng customers
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    id_card VARCHAR(20),
    birth_date DATE,
    gender VARCHAR(10),
    address VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(50),
    occupation VARCHAR(50),
    registered_date DATE DEFAULT CURRENT_DATE,
    customer_type VARCHAR(20) DEFAULT 'potential',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    selling_price DECIMAL(15,2) NOT NULL,
    discount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    delivery_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

-- Bảng users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'employee',
    email VARCHAR(50),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cars_brand ON cars(brand);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);
CREATE INDEX IF NOT EXISTS idx_cars_price ON cars(selling_price);
CREATE INDEX IF NOT EXISTS idx_cars_license ON cars(license_plate);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_car ON transactions(car_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
```

### 4.3 Database Helper Class

```python
# src/database/db_helper.py
import sqlite3
from contextlib import contextmanager
from pathlib import Path

class DatabaseHelper:
    def __init__(self, db_path: str = "car_management.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager cho database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Truy cập theo column name
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Khởi tạo database và tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Đọc và execute SQL schema
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    cursor.executescript(f.read())

    def execute(self, query: str, params: tuple = None):
        """Thực thi query không trả kết quả"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch tất cả kết quả"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: tuple = None) -> dict:
        """Fetch một kết quả duy nhất"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
```

### 4.4 Repository Pattern

```python
# src/repositories/car_repository.py
from typing import List, Optional, Dict, Any
from database.db_helper import DatabaseHelper

class CarRepository:
    def __init__(self, db: DatabaseHelper):
        self.db = db

    def create(self, car_data: Dict[str, Any]) -> int:
        """Thêm xe mới"""
        query = """
            INSERT INTO cars (license_plate, brand, model, year, color,
                            mileage, transmission, fuel_type, cost_price,
                            selling_price, status, dealer_id, import_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            car_data['license_plate'],
            car_data['brand'],
            car_data['model'],
            car_data.get('year'),
            car_data.get('color'),
            car_data.get('mileage', 0),
            car_data.get('transmission'),
            car_data.get('fuel_type'),
            car_data['cost_price'],
            car_data['selling_price'],
            car_data.get('status', 'available'),
            car_data.get('dealer_id'),
            car_data.get('import_date'),
            car_data.get('notes')
        )
        return self.db.execute(query, params)

    def get_by_id(self, car_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin xe theo ID"""
        query = "SELECT * FROM cars WHERE id = ?"
        return self.db.fetch_one(query, (car_id,))

    def get_all(self) -> List[Dict[str, Any]]:
        """Lấy tất cả xe"""
        query = "SELECT * FROM cars ORDER BY created_at DESC"
        return self.db.fetch_all(query)

    def search(self, keyword: str, brand: str = None,
               status: str = None, min_price: float = None,
               max_price: float = None) -> List[Dict[str, Any]]:
        """Tìm kiếm xe với nhiều tiêu chí"""
        query = """
            SELECT * FROM cars WHERE 1=1
            AND (license_plate LIKE ? OR brand LIKE ? OR model LIKE ?)
        """
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]

        if brand:
            query += " AND brand = ?"
            params.append(brand)

        if status:
            query += " AND status = ?"
            params.append(status)

        if min_price is not None:
            query += " AND selling_price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND selling_price <= ?"
            params.append(max_price)

        query += " ORDER BY created_at DESC"
        return self.db.fetch_all(query, tuple(params))

    def update(self, car_id: int, car_data: Dict[str, Any]) -> bool:
        """Cập nhật thông tin xe"""
        query = """
            UPDATE cars SET
                license_plate = ?, brand = ?, model = ?, year = ?,
                color = ?, mileage = ?, transmission = ?, fuel_type = ?,
                cost_price = ?, selling_price = ?, status = ?,
                dealer_id = ?, import_date = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            car_data['license_plate'],
            car_data['brand'],
            car_data['model'],
            car_data.get('year'),
            car_data.get('color'),
            car_data.get('mileage', 0),
            car_data.get('transmission'),
            car_data.get('fuel_type'),
            car_data['cost_price'],
            car_data['selling_price'],
            car_data.get('status'),
            car_data.get('dealer_id'),
            car_data.get('import_date'),
            car_data.get('notes'),
            car_id
        )
        try:
            self.db.execute(query, params)
            return True
        except Exception:
            return False

    def delete(self, car_id: int) -> bool:
        """Xóa xe (soft delete - cập nhật status)"""
        query = """
            UPDATE cars SET status = 'sold', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        try:
            self.db.execute(query, (car_id,))
            return True
        except Exception:
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê xe"""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN status = 'reserved' THEN 1 ELSE 0 END) as reserved,
                SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold,
                AVG(selling_price) as avg_price
            FROM cars
        """
        return self.db.fetch_one(query)
```

---

## 5. Thư Viện Hỗ Trợ

### 5.1 Thư Viện Bắt Buộc

```txt
# requirements.txt
PyQt6>=6.4.0
PyQt6-tools>=6.4.0
```

### 5.2 Thư Viện Tùy Chọn (Khuyến Nghị)

```txt
# requirements.txt (full)

# Core
PyQt6>=6.4.0
PyQt6-tools>=6.4.0

# Database ORM (optional but recommended)
sqlalchemy>=2.0.0

# Password hashing
bcrypt>=4.0.0

# Reporting
reportlab>=4.0.0          # Xuất PDF
openpyxl>=3.1.0           # Xuất Excel

# Charts
pyqtgraph>=0.13.0         # Biểu đồ trong PyQt
matplotlib>=3.7.0         # Biểu đồ nâng cao

# Utilities
python-dateutil>=2.8.0    # Xử lý ngày tháng
pillow>=10.0.0            # Xử lý ảnh
qrcode[pil]>=7.0.0        # Tạo QR code

# Development
pytest>=7.0.0             # Testing
pytest-qt>=4.2.0          # PyQt testing
black>=23.0.0             # Code formatting
flake8>=6.0.0             # Linting
mypy>=1.0.0               # Type checking
```

### 5.3 Cài Đặt Tất Cả

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

---

## 6. Cài Đặt & Cấu Hình

### 6.1 Yêu Cầu Hệ Thống

| Thành phần       | Yêu cầu tối thiểu                  | Khuyến nghị                         |
| ---------------- | ---------------------------------- | ----------------------------------- |
| **Hệ điều hành** | Windows 10, Ubuntu 20.04, macOS 11 | Windows 11, Ubuntu 22.04, macOS 13+ |
| **CPU**          | Dual-core 2.0 GHz                  | Quad-core 2.5 GHz+                  |
| **RAM**          | 4 GB                               | 8 GB+                               |
| **Dung lượng**   | 500 MB                             | 1 GB+                               |
| **Màn hình**     | 1366x768                           | 1920x1080+                          |
| **Python**       | 3.8                                | 3.10+                               |

### 6.2 Hướng Dẫn Cài Đặt

#### Bước 1: Cài đặt Python

```bash
# Windows: Tải từ https://python.org
# Linux:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS:
brew install python
```

#### Bước 2: Clone project

```bash
git clone <repository-url>
cd Car-Management
```

#### Bước 3: Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### Bước 4: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

#### Bước 5: Chạy ứng dụng

```bash
python src/main.py
```

### 6.3 Cấu Hình Ứng Dụng

```python
# src/config.py
from pathlib import Path
from datetime import timedelta

# Đường dẫn
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "car_management.db"
BACKUP_DIR = DATA_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Tạo thư mục nếu chưa tồn tại
for directory in [DATA_DIR, BACKUP_DIR, LOG_DIR, ASSETS_DIR]:
    directory.mkdir(exist_ok=True)

# Database
DB_BACKUP_ENABLED = True
DB_BACKUP_INTERVAL = timedelta(days=1)  # Sao lưu hàng ngày
MAX_BACKUP_COUNT = 30  # Giữ tối đa 30 backup

# Session
SESSION_TIMEOUT = timedelta(minutes=30)  # Timeout sau 30 phút
MAX_LOGIN_ATTEMPTS = 5  # Số lần đăng nhập sai tối đa

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Application
APP_NAME = "Car Management System"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Nhóm 4"

# UI
DEFAULT_WINDOW_SIZE = (1280, 720)
MIN_WINDOW_SIZE = (1024, 600)
TABLE_ROW_HEIGHT = 40
```

---

## 7. Cấu Trúc Project

### 7.1 Cây Thư Mục

```
Car-Management/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
│   ├── SRS_Car_Management.md
│   ├── tech_stack.md
│   └── user_manual.md
├── design/
│   └── DESIGN.md
├── sprints/
│   ├── sprint1/
│   ├── sprint2/
│   └── sprint3/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_repositories.py
│   └── test_services.py
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── app.py                  # Application class
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── car.py
│   │   ├── customer.py
│   │   ├── dealer.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── car_repository.py
│   │   ├── customer_repository.py
│   │   ├── dealer_repository.py
│   │   └── transaction_repository.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── car_service.py
│   │   ├── customer_service.py
│   │   ├── transaction_service.py
│   │   └── report_service.py
│   │
│   ├── views/                  # UI layer
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── login_dialog.py
│   │   │
│   │   ├── dialogs/            # Dialog forms
│   │   │   ├── __init__.py
│   │   │   ├── car_dialog.py
│   │   │   ├── customer_dialog.py
│   │   │   └── transaction_dialog.py
│   │   │
│   │   ├── widgets/            # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── car_table.py
│   │   │   ├── dashboard_cards.py
│   │   │   └── search_bar.py
│   │   │
│   │   └── screens/            # Full screens
│   │       ├── __init__.py
│   │       ├── dashboard_screen.py
│   │       ├── car_screen.py
│   │       ├── customer_screen.py
│   │       └── report_screen.py
│   │
│   ├── database/               # Database utilities
│   │   ├── __init__.py
│   │   ├── db_helper.py
│   │   ├── schema.sql
│   │   └── migration.py
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py       # Input validation
│   │   ├── formatters.py       # Data formatting
│   │   ├── exporters.py        # Export PDF/Excel
│   │   └── helpers.py          # Helper functions
│   │
│   └── assets/                 # Static assets
│       ├── icons/
│       ├── images/
│       └── styles/
│           └── theme.qss
│
├── data/                       # Runtime data (gitignore)
│   ├── car_management.db
│   └── backups/
│
└── logs/                       # Application logs (gitignore)
    └── app.log
```

### 7.2 File Entry Point

```python
# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app import CarManagementApp
from config import APP_NAME

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Nhóm 4")

    # Apply stylesheet
    with open("assets/styles/theme.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    # Create and show main window
    window = CarManagementApp()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## 8. Coding Conventions

### 8.1 Python Style Guide

Tuân theo **PEP 8** với các quy tắc cụ thể:

```python
# Tên biến và hàm: snake_case
def get_car_by_id(car_id):
    pass

# Tên class: PascalCase
class CarRepository:
    pass

# Hằng số: UPPER_CASE
MAX_LOGIN_ATTEMPTS = 5

# Type hints
from typing import Optional, List, Dict

def search_cars(
    keyword: str,
    brand: Optional[str] = None,
    min_price: float = None
) -> List[Dict]:
    pass

# Docstrings
def calculate_discount(price: float, percentage: float) -> float:
    """
    Tính giá sau chiết khấu.

    Args:
        price: Giá gốc
        percentage: Phần trăm chiết khấu (0-100)

    Returns:
        Giá sau khi áp dụng chiết khấu

    Raises:
        ValueError: Nếu percentage ngoài khoảng 0-100
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")
    return price * (1 - percentage / 100)
```

### 8.2 Quy Tắc Đặt Tên

| Loại     | Quy tắc    | Ví dụ                            |
| -------- | ---------- | -------------------------------- |
| Biến     | snake_case | `car_list`, `total_amount`       |
| Hàm      | snake_case | `get_car()`, `calculate_total()` |
| Class    | PascalCase | `CarRepository`, `MainWindow`    |
| Constant | UPPER_CASE | `DB_PATH`, `MAX_ROWS`            |
| Private  | \_prefix   | `_internal_method()`             |
| File     | snake_case | `car_service.py`                 |

### 8.3 Cấu Trúc File

```python
# 1. Module docstring
"""
Car Service - Business logic for car management
"""

# 2. Imports (standard library first, then third-party, then local)
import logging
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import QMessageBox

from models.car import Car
from repositories.car_repository import CarRepository

# 3. Module constants
logger = logging.getLogger(__name__)
MAX_CARS_PER_PAGE = 20

# 4. Classes and functions
class CarService:
    """Service layer for car operations"""

    def __init__(self, repository: CarRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def get_car(self, car_id: int) -> Optional[Car]:
        """Get car by ID"""
        try:
            data = self.repository.get_by_id(car_id)
            return Car.from_dict(data) if data else None
        except Exception as e:
            self.logger.error(f"Error getting car {car_id}: {e}")
            raise
```

### 8.4 Error Handling

```python
# Custom exceptions
class CarManagementError(Exception):
    """Base exception for car management"""
    pass

class CarNotFoundError(CarManagementError):
    """Raised when car is not found"""
    pass

class DuplicateLicensePlateError(CarManagementError):
    """Raised when license plate already exists"""
    pass

# Usage
def add_car(car_data: dict) -> int:
    try:
        car_id = repository.create(car_data)
        logger.info(f"Car added successfully with ID: {car_id}")
        return car_id
    except sqlite3.IntegrityError as e:
        if "license_plate" in str(e):
            raise DuplicateLicensePlateError(
                f"Biển số {car_data['license_plate']} đã tồn tại"
            )
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise CarManagementError(f"Lỗi khi thêm xe: {str(e)}")
```

### 8.5 Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage levels
logger.debug("Debug information")      # Chi tiết debug
logger.info("Car added successfully")  # Thông tin bình thường
logger.warning("Low disk space")       # Cảnh báo
logger.error("Database connection failed")  # Lỗi
logger.critical("System crash")        # Lỗi nghiêm trọng
```

---

## 9. Build & Deploy

### 9.1 Đóng Gói Ứng Dụng

Sử dụng **PyInstaller** để đóng gói thành file .exe:

```bash
# Cài đặt PyInstaller
pip install pyinstaller

# Tạo file spec (tùy chọn)
pyi-makespec --onefile --windowed src/main.py

# Build
pyinstaller --onefile --windowed \
    --name "CarManagement" \
    --icon assets/icon.ico \
    --add-data "assets:assets" \
    --add-data "database/schema.sql:database" \
    src/main.py
```

### 9.2 File .spec

```python
# carmanagement.spec
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('database/schema.sql', 'database'),
    ],
    hiddenimports=collect_submodules('PyQt6'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CarManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False cho ứng dụng GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

### 9.3 CI/CD (GitHub Actions)

```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-qt

      - name: Run tests
        run: pytest tests/ -v

      - name: Lint with flake8
        run: flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

  build:
    needs: test
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: pyinstaller carmanagement.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: CarManagement-Windows
          path: dist/
```

### 9.4 Release Checklist

```markdown
## Trước khi release

- [ ] Tất cả tests pass
- [ ] Code đã được lint (flake8, black)
- [ ] Version đã được update trong config.py
- [ ] CHANGELOG.md đã được cập nhật
- [ ] Database migration scripts đã sẵn sàng
- [ ] User manual đã được cập nhật
- [ ] Build executable thành công
- [ ] Test trên Windows, Linux, macOS

## Sau khi release

- [ ] Tạo Git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Tạo GitHub Release với changelog
- [ ] Upload binary cho các platform
- [ ] Thông báo cho người dùng
```

---

## Phụ Lục

### A. Tài Liệu Tham Khảo

- [PyQT6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Documentation](https://docs.python.org/3/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PEP 8 - Style Guide](https://pep8.org/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)

### B. Công Cụ Hỗ Trợ Phát Triển

| Công cụ               | Mục đích               |
| --------------------- | ---------------------- |
| VS Code / PyCharm     | IDE                    |
| Qt Designer           | Thiết kế UI            |
| DB Browser for SQLite | Xem/chỉnh sửa database |
| Git                   | Version control        |
| Black                 | Code formatting        |
| Flake8                | Linting                |
| pytest                | Testing                |

### C. Lệnh Hữu Ích

```bash
# Chạy tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint code
flake8 src/

# Type check
mypy src/

# Xem database
sqlite3 data/car_management.db

# Backup database
cp data/car_management.db data/backup_$(date +%Y%m%d).db

# Tạo requirements
pip freeze > requirements.txt
```

---

**Tài liệu được tạo cho bài tập lớn học phần Lập trình Python**  
**Nhóm 4 - Quản Lý Đại Lý Xe Hơi**  
**© 2026**
