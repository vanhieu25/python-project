# Sprint-1.2: Car CRUD Operations

**Module**: 🚗 Car Management  
**Mức độ ưu tiên**: Core  
**Blocked by**: Sprint-1.1 (Car Management Initial)  
**Ước lượng**: 2 ngày

---

## 1. Xác định Feature

### Mô tả
Hoàn thiện các thao tác CRUD (Create, Read, Update, Delete) cho xe, bao gồm giao diện add/edit dialog và quan hệ với contracts.

### Yêu cầu
- Thêm/Sửa/Xóa xe với validation đầy đủ
- Relations: cars ↔ contracts (xác định xe đã bán trong hợp đồng nào)
- UI: Add/Edit dialog với form đầy đủ thông tin
- Integration test cho toàn bộ luồng

### Dependencies
- Sprint-1.1: Cần cars table và repository cơ bản

---

## 2. Database

### Schema Updates
```sql
-- Thêm foreign key reference đến contracts (cho xe đã bán)
-- Vào bảng contracts sẽ có car_id reference

-- Thêm bảng car_history để track thay đổi
CREATE TABLE IF NOT EXISTS car_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,                  -- create, update, delete
    field_name VARCHAR(50),                       -- Tên field thay đổi (nếu update)
    old_value TEXT,                               -- Giá trị cũ
    new_value TEXT,                               -- Giá trị mới
    changed_by INTEGER,                           -- Người thay đổi
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_car_history_car ON car_history(car_id);
CREATE INDEX IF NOT EXISTS idx_car_history_changed_at ON car_history(changed_at);

-- Cập nhật bảng cars - thêm trường deleted (soft delete)
ALTER TABLE cars ADD COLUMN is_deleted BOOLEAN DEFAULT 0;
ALTER TABLE cars ADD COLUMN deleted_at DATETIME;
ALTER TABLE cars ADD COLUMN deleted_by INTEGER;
```

---

## 3. Backend Logic

### Service Layer
```python
# src/services/car_service.py
from typing import List, Optional, Dict, Any
from ..repositories.car_repository import CarRepository
from ..repositories.car_history_repository import CarHistoryRepository
from ..validators.car_validator import CarValidator, CarValidationError
from ..models.car import Car


class CarServiceError(Exception):
    """Base exception for car service."""
    pass


class DuplicateVINError(CarServiceError):
    """Duplicate VIN error."""
    pass


class CarNotFoundError(CarServiceError):
    """Car not found error."""
    pass


class CarInContractError(CarServiceError):
    """Car is in an active contract."""
    pass


class CarService:
    """Service layer for car operations."""

    def __init__(self, car_repository: CarRepository,
                 history_repository: CarHistoryRepository):
        self.car_repo = car_repository
        self.history_repo = history_repository
        self.validator = CarValidator()

    def create_car(self, car_data: Dict[str, Any],
                   created_by: int) -> Car:
        """Create a new car with validation.

        Args:
            car_data: Dictionary containing car data
            created_by: User ID who creates the car

        Returns:
            Created Car instance

        Raises:
            CarValidationError: If data is invalid
            DuplicateVINError: If VIN already exists
        """
        # Validate required fields
        self._validate_car_data(car_data)

        # Check for duplicate VIN
        if self.car_repo.get_by_vin(car_data['vin']):
            raise DuplicateVINError(f"VIN '{car_data['vin']}' đã tồn tại")

        # Check for duplicate license plate
        if car_data.get('license_plate'):
            existing = self.car_repo.get_by_license_plate(
                car_data['license_plate']
            )
            if existing:
                raise DuplicateVINError(
                    f"Biển số '{car_data['license_plate']}' đã tồn tại"
                )

        # Set creator
        car_data['created_by'] = created_by

        try:
            car_id = self.car_repo.create(car_data)
            car = self.car_repo.get_by_id(car_id)

            # Record history
            self.history_repo.record_create(car_id, created_by)

            return car
        except Exception as e:
            raise CarServiceError(f"Không thể tạo xe: {str(e)}")

    def update_car(self, car_id: int, car_data: Dict[str, Any],
                   updated_by: int) -> Car:
        """Update car with validation and history tracking.

        Args:
            car_id: Car ID
            car_data: Dictionary containing updated data
            updated_by: User ID who updates

        Returns:
            Updated Car instance
        """
        # Check car exists
        car = self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")

        # Validate
        self._validate_car_data(car_data, is_update=True)

        # Check for duplicate license plate
        if car_data.get('license_plate'):
            existing = self.car_repo.get_by_license_plate(
                car_data['license_plate']
            )
            if existing and existing.id != car_id:
                raise DuplicateVINError(
                    f"Biển số '{car_data['license_plate']}' đã tồn tại"
                )

        # Track changes for history
        changes = self._get_changes(car, car_data)

        try:
            success = self.car_repo.update(car_id, car_data)
            if not success:
                raise CarServiceError("Cập nhật thất bại")

            # Record history
            for change in changes:
                self.history_repo.record_update(
                    car_id, change['field'],
                    change['old_value'], change['new_value'],
                    updated_by
                )

            return self.car_repo.get_by_id(car_id)
        except Exception as e:
            raise CarServiceError(f"Không thể cập nhật xe: {str(e)}")

    def delete_car(self, car_id: int, deleted_by: int,
                   permanent: bool = False) -> bool:
        """Delete car (soft or permanent).

        Args:
            car_id: Car ID
            deleted_by: User ID who deletes
            permanent: Whether to permanently delete

        Returns:
            True if successful

        Raises:
            CarNotFoundError: If car not found
            CarInContractError: If car is in an active contract
        """
        car = self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")

        # Check if car is in an active contract
        if self._is_car_in_active_contract(car_id):
            raise CarInContractError(
                "Không thể xóa xe đang trong hợp đồng active"
            )

        try:
            if permanent:
                success = self.car_repo.delete_permanently(car_id)
            else:
                success = self.car_repo.soft_delete(car_id, deleted_by)

            if success:
                self.history_repo.record_delete(car_id, deleted_by)

            return success
        except Exception as e:
            raise CarServiceError(f"Không thể xóa xe: {str(e)}")

    def get_car(self, car_id: int) -> Car:
        """Get car by ID."""
        car = self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")
        return car

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        """Get car by VIN."""
        return self.car_repo.get_by_vin(vin)

    def list_cars(self, status: Optional[str] = None,
                  include_deleted: bool = False) -> List[Car]:
        """List all cars."""
        return self.car_repo.get_all(status, include_deleted)

    def _validate_car_data(self, data: Dict[str, Any],
                          is_update: bool = False) -> None:
        """Validate car data."""
        if not is_update or 'vin' in data:
            self.validator.validate_vin(data.get('vin', ''))
        if 'license_plate' in data:
            self.validator.validate_license_plate(data['license_plate'])
        if 'year' in data:
            self.validator.validate_year(data['year'])
        if 'selling_price' in data:
            self.validator.validate_price(data['selling_price'], "Giá bán")
        if 'purchase_price' in data:
            self.validator.validate_price(data['purchase_price'], "Giá nhập")

    def _get_changes(self, car: Car, new_data: Dict[str, Any]) -> List[Dict]:
        """Get list of changes for history tracking."""
        changes = []
        car_dict = car.__dict__
        for field, new_value in new_data.items():
            old_value = car_dict.get(field)
            if old_value != new_value:
                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value
                })
        return changes

    def _is_car_in_active_contract(self, car_id: int) -> bool:
        """Check if car is in an active contract."""
        # Implementation depends on contracts module
        # For now, check if car status is 'sold'
        car = self.car_repo.get_by_id(car_id)
        return car and car.status == 'sold'
```

### History Repository
```python
# src/repositories/car_history_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper

class CarHistoryRepository:
    """Repository for car history tracking."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def record_create(self, car_id: int, user_id: int) -> int:
        """Record car creation."""
        query = """
            INSERT INTO car_history (car_id, action, changed_by, changed_at)
            VALUES (?, 'create', ?, ?)
        """
        return self.db.execute(query, (car_id, user_id, datetime.utcnow()))

    def record_update(self, car_id: int, field_name: str,
                     old_value: Any, new_value: Any,
                     user_id: int) -> int:
        """Record field update."""
        query = """
            INSERT INTO car_history (car_id, action, field_name,
                                   old_value, new_value, changed_by, changed_at)
            VALUES (?, 'update', ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            car_id, field_name, str(old_value) if old_value else None,
            str(new_value) if new_value else None, user_id, datetime.utcnow()
        ))

    def record_delete(self, car_id: int, user_id: int) -> int:
        """Record car deletion."""
        query = """
            INSERT INTO car_history (car_id, action, changed_by, changed_at)
            VALUES (?, 'delete', ?, ?)
        """
        return self.db.execute(query, (car_id, user_id, datetime.utcnow()))

    def get_history(self, car_id: int) -> List[Dict[str, Any]]:
        """Get history for a car."""
        query = """
            SELECT h.*, u.full_name as changed_by_name
            FROM car_history h
            LEFT JOIN users u ON h.changed_by = u.id
            WHERE h.car_id = ?
            ORDER BY h.changed_at DESC
        """
        return self.db.fetch_all(query, (car_id,))
```

---

## 4. UI Design

### Add/Edit Car Dialog
```
┌─────────────────────────────────────────────────────────────┐
│  [✕] Thêm xe mới                                            │
├─────────────────────────────────────────────────────────────┤
│  Thông tin cơ bản                                           │
│  ┌──────────────────┐ ┌──────────────────┐                  │
│  │ VIN *            │ │ Biển số          │                  │
│  │ 1HGCM826...      │ │ 51A-12345        │                  │
│  └──────────────────┘ └──────────────────┘                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Hãng xe *        │ │ Model *          │ │ Năm SX       │ │
│  │ [Honda ▼]        │ │ [Civic ▼]        │ │ 2023         │ │
│  └──────────────────┘ └──────────────────┘ └──────────────┘ │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Màu sắc          │ │ Số km            │ │ Hộp số       │ │
│  │ Đen              │ │ 0                │ │ [Tự động ▼]  │ │
│  └──────────────────┘ └──────────────────┘ └──────────────┘ │
│                                                             │
│  Thông tin giá                                              │
│  ┌──────────────────┐ ┌──────────────────┐                  │
│  │ Giá nhập         │ │ Giá bán          │                  │
│  │ 750,000,000      │ │ 850,000,000      │                  │
│  └──────────────────┘ └──────────────────┘                  │
│                                                             │
│  Mô tả                                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Xe mới 100%, nhập khẩu nguyên chiếc...                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Hủy]                              [💾 Lưu]                │
└─────────────────────────────────────────────────────────────┘
```

### Validation Messages
- Hiển thị lỗi inline dưới mỗi field
- Đỏ viền input khi có lỗi
- Tooltip giải thích yêu cầu validation

---

## 5. Testing

### Integration Tests
```python
# tests/test_car_service.py
import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.repositories.car_history_repository import CarHistoryRepository
from src.services.car_service import CarService, DuplicateVINError, CarNotFoundError

class TestCarService(unittest.TestCase):
    """Integration tests for CarService."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.car_repo = CarRepository(self.db)
        self.history_repo = CarHistoryRepository(self.db)
        self.car_service = CarService(self.car_repo, self.history_repo)

        # Create test user (admin)
        self.admin_id = 1

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_car_success(self):
        """Test successful car creation."""
        car_data = {
            "vin": "1HGCM82633A111111",
            "license_plate": "51A-99999",
            "brand": "Toyota",
            "model": "Vios",
            "year": 2023,
            "selling_price": 600000000,
            "purchase_price": 550000000
        }
        car = self.car_service.create_car(car_data, self.admin_id)

        self.assertIsNotNone(car)
        self.assertEqual(car.vin, "1HGCM82633A111111")
        self.assertEqual(car.brand, "Toyota")

    def test_create_car_duplicate_vin(self):
        """Test creating car with duplicate VIN."""
        car_data = {
            "vin": "1HGCM82633A222222",
            "brand": "Honda",
            "model": "City"
        }
        self.car_service.create_car(car_data, self.admin_id)

        # Try to create again with same VIN
        with self.assertRaises(DuplicateVINError):
            self.car_service.create_car(car_data, self.admin_id)

    def test_update_car_with_history(self):
        """Test updating car creates history records."""
        # Create car
        car = self.car_service.create_car({
            "vin": "1HGCM82633A333333",
            "brand": "Mazda",
            "model": "3",
            "selling_price": 800000000
        }, self.admin_id)

        # Update
        updated = self.car_service.update_car(
            car.id,
            {"selling_price": 850000000, "color": "Trắng"},
            self.admin_id
        )

        self.assertEqual(updated.selling_price, 850000000)

        # Check history
        history = self.history_repo.get_history(car.id)
        self.assertEqual(len(history), 3)  # create + 2 updates

    def test_delete_car_prevents_if_in_contract(self):
        """Test cannot delete car in active contract."""
        # Create car and mark as sold
        car = self.car_service.create_car({
            "vin": "1HGCM82633A444444",
            "brand": "Kia",
            "model": "Seltos",
            "status": "sold"
        }, self.admin_id)

        from src.services.car_service import CarInContractError
        with self.assertRaises(CarInContractError):
            self.car_service.delete_car(car.id, self.admin_id)
```

---

## 6. Definition of Done

- [ ] CarService with full CRUD operations
- [ ] History tracking for all changes
- [ ] Validation for all fields
- [ ] Soft delete support
- [ ] Add/Edit dialog UI implemented
- [ ] Integration tests pass
- [ ] No duplicate VIN/license plate allowed
- [ ] Cannot delete car in active contract
- [ ] Code committed: `feat: thao tác CRUD quản lý xe`

---

## 7. Git Commit

```bash
# Files to commit
- src/services/car_service.py (mới)
- src/repositories/car_history_repository.py (mới)
- src/ui/cars/car_dialog.py (mới)
- src/database/schema.sql (cập nhật)
- tests/test_car_service.py (mới)

# Commit message
feat: thao tác CRUD quản lý xe

- Thêm CarService với các thao tác tạo, cập nhật, xóa
- Triển khai lịch sử thay đổi cho tất cả thao tác
- Thêm giao diện dialog Thêm/Sửa xe
- Hỗ trợ xóa mềm (soft delete)
- Ngăn chặn xóa xe đang trong hợp đồng active
- Thêm integration tests
```
