# Sprint-1.1: Car Management Initial

**Module**: 🚗 Car Management  
**Mức độ ưu tiên**: Core  
**Blocked by**: Sprint-0.3 (Authorization)  
**Ước lượng**: 2 ngày

---

## 1. Xác định Feature

### Mô tả
Khởi tạo module quản lý xe - tạo nền tảng database và cấu trúc cơ bản cho chức năng quản lý thông tin xe.

### Yêu cầu
- Tạo bảng `cars` trong database
- Định nghĩa model và validators cho xe
- Tạo giao diện list view cơ bản hiển thị danh sách xe
- Unit test CRUD cơ bản

### Dependencies
- Sprint-0.3 (Authorization): Cần hệ thống phân quyền để kiểm soát truy cập

---

## 2. Database

### Schema
```sql
-- Bảng cars (Thông tin xe)
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin VARCHAR(17) UNIQUE NOT NULL,              -- Số khung (Vehicle Identification Number)
    license_plate VARCHAR(20) UNIQUE,             -- Biển số xe
    brand VARCHAR(50) NOT NULL,                   -- Hãng xe (Toyota, Honda, etc.)
    model VARCHAR(50) NOT NULL,                   -- Dòng xe (Camry, Civic, etc.)
    year INTEGER,                                 -- Năm sản xuất
    color VARCHAR(30),                            -- Màu sắc
    engine_number VARCHAR(50),                    -- Số máy
    transmission VARCHAR(20),                     -- Hộp số (auto/manual)
    fuel_type VARCHAR(20),                        -- Loại nhiên liệu (gasoline/diesel/electric)
    mileage INTEGER DEFAULT 0,                    -- Số km đã đi
    purchase_price DECIMAL(15,2),                 -- Giá nhập
    selling_price DECIMAL(15,2),                  -- Giá bán
    status VARCHAR(20) DEFAULT 'available',       -- Trạng thái (available/sold/reserved/maintenance)
    description TEXT,                             -- Mô tả chi tiết
    images TEXT,                                  -- JSON array chứa đường dẫn ảnh
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,                           -- Người tạo record
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cars_vin ON cars(vin);
CREATE INDEX IF NOT EXISTS idx_cars_license_plate ON cars(license_plate);
CREATE INDEX IF NOT EXISTS idx_cars_brand ON cars(brand);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);
CREATE INDEX IF NOT EXISTS idx_cars_year ON cars(year);

-- Trigger cập nhật updated_at
CREATE TRIGGER IF NOT EXISTS update_cars_timestamp
AFTER UPDATE ON cars
BEGIN
    UPDATE cars SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### Seed Data (Sample)
```sql
INSERT INTO cars (vin, license_plate, brand, model, year, color, purchase_price, selling_price, status) VALUES
('1HGCM82633A123456', '51A-12345', 'Honda', 'Civic', 2023, 'Đen', 750000000, 850000000, 'available'),
('JTDBU4EE3B9123456', '51A-67890', 'Toyota', 'Camry', 2023, 'Trắng', 1200000000, 1350000000, 'available'),
('WBA3A5G59C1234567', '51A-11111', 'BMW', '320i', 2022, 'Xám', 1500000000, 1650000000, 'available');
```

---

## 3. Backend Logic

### Models
```python
# src/models/car.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Car:
    id: Optional[int] = None
    vin: str = ""
    license_plate: Optional[str] = None
    brand: str = ""
    model: str = ""
    year: Optional[int] = None
    color: Optional[str] = None
    engine_number: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    mileage: int = 0
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    status: str = "available"
    description: Optional[str] = None
    images: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Car":
        if not data:
            return None
        return cls(**data)
```

### Validators
```python
# src/validators/car_validator.py
import re
from typing import List, Optional

class CarValidationError(Exception):
    """Car validation error."""
    pass

class CarValidator:
    """Validator for car data."""

    # Các hãng xe phổ biến ở VN
    VALID_BRANDS = [
        'Toyota', 'Honda', 'Mazda', 'Hyundai', 'Kia',
        'Ford', 'Mitsubishi', 'Suzuki', 'BMW', 'Mercedes-Benz',
        'Audi', 'VinFast', 'Chevrolet', 'Nissan', 'Lexus'
    ]

    VALID_STATUSES = ['available', 'sold', 'reserved', 'maintenance']

    @staticmethod
    def validate_vin(vin: str) -> None:
        """Validate VIN (17 ký tự)."""
        if not vin:
            raise CarValidationError("VIN không được để trống")
        if len(vin) != 17:
            raise CarValidationError("VIN phải có đúng 17 ký tự")
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin.upper()):
            raise CarValidationError("VIN chứa ký tự không hợp lệ")

    @staticmethod
    def validate_license_plate(plate: Optional[str]) -> None:
        """Validate biển số xe Việt Nam."""
        if not plate:
            return  # Có thể null
        # Pattern: XX[A-Z]-XXXXX hoặc XX-XXXXX
        pattern = r'^[0-9]{2}[A-Z]{1,2}-[0-9]{4,5}$'
        if not re.match(pattern, plate.upper()):
            raise CarValidationError("Biển số xe không hợp lệ")

    @staticmethod
    def validate_year(year: Optional[int]) -> None:
        """Validate năm sản xuất."""
        if year is None:
            return
        current_year = datetime.now().year
        if year < 1900 or year > current_year + 1:
            raise CarValidationError(f"Năm sản xuất phải từ 1900 đến {current_year + 1}")

    @staticmethod
    def validate_price(price: Optional[float], field_name: str = "Giá") -> None:
        """Validate giá tiền."""
        if price is None:
            return
        if price < 0:
            raise CarValidationError(f"{field_name} không được âm")
        if price > 100000000000:  # 100 tỷ
            raise CarValidationError(f"{field_name} vượt quá giới hạn cho phép")
```

### Repository
```python
# src/repositories/car_repository.py
from typing import List, Optional, Dict, Any
from ..database.db_helper import DatabaseHelper
from ..models.car import Car

class CarRepository:
    """Repository for car data access."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def create(self, car_data: Dict[str, Any]) -> int:
        """Create a new car record."""
        query = """
            INSERT INTO cars (vin, license_plate, brand, model, year, color,
                            engine_number, transmission, fuel_type, mileage,
                            purchase_price, selling_price, status, description,
                            created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            car_data['vin'].upper(),
            car_data.get('license_plate', '').upper() if car_data.get('license_plate') else None,
            car_data['brand'],
            car_data['model'],
            car_data.get('year'),
            car_data.get('color'),
            car_data.get('engine_number'),
            car_data.get('transmission'),
            car_data.get('fuel_type'),
            car_data.get('mileage', 0),
            car_data.get('purchase_price'),
            car_data.get('selling_price'),
            car_data.get('status', 'available'),
            car_data.get('description'),
            car_data.get('created_by')
        )
        return self.db.execute(query, params)

    def get_by_id(self, car_id: int) -> Optional[Car]:
        """Get car by ID."""
        query = "SELECT * FROM cars WHERE id = ?"
        row = self.db.fetch_one(query, (car_id,))
        return Car.from_dict(row)

    def get_by_vin(self, vin: str) -> Optional[Car]:
        """Get car by VIN."""
        query = "SELECT * FROM cars WHERE vin = ?"
        row = self.db.fetch_one(query, (vin.upper(),))
        return Car.from_dict(row)

    def get_all(self, status: Optional[str] = None) -> List[Car]:
        """Get all cars with optional status filter."""
        if status:
            query = "SELECT * FROM cars WHERE status = ? ORDER BY created_at DESC"
            rows = self.db.fetch_all(query, (status,))
        else:
            query = "SELECT * FROM cars ORDER BY created_at DESC"
            rows = self.db.fetch_all(query)
        return [Car.from_dict(row) for row in rows if row]

    def update(self, car_id: int, car_data: Dict[str, Any]) -> bool:
        """Update car record."""
        allowed_fields = [
            'license_plate', 'brand', 'model', 'year', 'color',
            'engine_number', 'transmission', 'fuel_type', 'mileage',
            'purchase_price', 'selling_price', 'status', 'description'
        ]
        fields = []
        params = []
        for field in allowed_fields:
            if field in car_data:
                fields.append(f"{field} = ?")
                params.append(car_data[field])
        if not fields:
            return False
        query = f"UPDATE cars SET {', '.join(fields)} WHERE id = ?"
        params.append(car_id)
        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def delete(self, car_id: int) -> bool:
        """Delete car record."""
        query = "DELETE FROM cars WHERE id = ?"
        try:
            self.db.execute(query, (car_id,))
            return True
        except Exception:
            return False
```

---

## 4. UI Design

### List View Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  🚗 QUẢN LÝ XE                                      [+ Thêm xe] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                           │
│  │  Tất cả │ │ Còn hàng│ │ Đã bán  │                           │
│  │  (15)   │ │  (12)   │ │  (3)    │                           │
│  └─────────┘ └─────────┘ └─────────┘                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┬─────────────┬──────┬──────────┬────────────┐ │
│  │ VIN          │ Biển số     │ Hãng │ Model    │ Giá bán    │ │
│  ├──────────────┼─────────────┼──────┼──────────┼────────────┤ │
│  │ 1HGCM826...  │ 51A-12345   │ Honda│ Civic    │ 850M       │ │
│  │ JTDBU4EE...  │ 51A-67890   │Toyota│ Camry    │ 1.35B      │ │
│  │ WBA3A5G5...  │ 51A-11111   │ BMW  │ 320i     │ 1.65B      │ │
│  └──────────────┴─────────────┴──────┴──────────┴────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Wireframes
- **Table columns**: VIN, Biển số, Hãng, Model, Năm, Màu, Giá bán, Trạng thái, Actions
- **Actions**: Xem, Sửa, Xóa (icon buttons)
- **Status badges**: Available (green), Sold (gray), Reserved (yellow), Maintenance (orange)

---

## 5. Testing

### Unit Tests
```python
# tests/test_car_repository.py
import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.models.car import Car

class TestCarRepository(unittest.TestCase):
    """Test cases for CarRepository."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.car_repo = CarRepository(self.db)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_car(self):
        """Test creating a car."""
        car_data = {
            "vin": "1HGCM82633A123456",
            "license_plate": "51A-12345",
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "color": "Đen",
            "purchase_price": 750000000,
            "selling_price": 850000000,
            "status": "available"
        }
        car_id = self.car_repo.create(car_data)
        self.assertGreater(car_id, 0)

    def test_get_by_vin(self):
        """Test getting car by VIN."""
        # Create car
        car_data = {
            "vin": "1HGCM82633A999999",
            "brand": "Toyota",
            "model": "Camry"
        }
        self.car_repo.create(car_data)
        # Get by VIN
        car = self.car_repo.get_by_vin("1HGCM82633A999999")
        self.assertIsNotNone(car)
        self.assertEqual(car.brand, "Toyota")

    def test_get_all_cars(self):
        """Test getting all cars."""
        # Create multiple cars
        for i in range(3):
            self.car_repo.create({
                "vin": f"1HGCM82633A{i:06d}",
                "brand": "TestBrand",
                "model": f"Model{i}"
            })
        cars = self.car_repo.get_all()
        # Should include seed data + test cars
        self.assertGreaterEqual(len(cars), 3)
```

### Test Coverage Goals
- Repository CRUD: ≥ 80%
- Model validation: ≥ 90%
- Database constraints: All unique/index constraints tested

---

## 6. Definition of Done

- [ ] Database schema created with all tables, indexes, constraints
- [ ] Models defined with proper data types
- [ ] Validators implemented for all required fields
- [ ] Repository layer with CRUD operations
- [ ] Unit test coverage ≥ 80%
- [ ] List view UI implemented (can be placeholder/Tkinter)
- [ ] No critical bugs
- [ ] Code committed with message: `feat: khởi tạo module quản lý xe`

---

## 7. Git Commit

```bash
# Files to commit
- src/database/schema.sql (cập nhật)
- src/models/car.py (mới)
- src/validators/car_validator.py (mới)
- src/repositories/car_repository.py (mới)
- tests/test_car_repository.py (mới)
- src/ui/cars/ (nếu có UI)

# Commit message
feat: khởi tạo module quản lý xe

- Thêm bảng cars với indexes và constraints
- Triển khai model Car và validator
- Thêm CarRepository với các thao tác CRUD
- Tạo giao diện list view cơ bản
- Thêm unit tests (độ phủ ≥ 80%)
```
