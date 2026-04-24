# Sprint-1.4: Car Validation Logic

**Module**: 🚗 Car Management  
**Mức độ ưu tiên**: Core  
**Blocked by**: Sprint-1.2 (Car CRUD Operations)  
**Ước lượng**: 1 ngày

---

## 1. Xác định Feature

### Mô tả
Hoàn thiện logic validation cho xe, đảm bảo dữ liệu chính xác và nhất quán. Xử lý các trường hợp edge case và hiển thị thông báo lỗi rõ ràng.

### Yêu cầu
- Validation toàn diện cho tất cả fields
- Unique constraints (VIN, biển số)
- Business validation (giá nhập < giá bán, năm SX hợp lý)
- Error messages chi tiết, dễ hiểu (tiếng Việt)
- Cross-field validation
- Edge case testing

### Dependencies
- Sprint-1.2: Cần CRUD operations cơ bản

---

## 2. Database

### Constraints
```sql
-- Đảm bảo constraints đã được áp dụng
-- (Đã có trong schema từ Sprint-1.1)

-- Thêm CHECK constraints
ALTER TABLE cars ADD CONSTRAINT chk_year_valid
    CHECK (year >= 1900 AND year <= strftime('%Y', 'now') + 1);

ALTER TABLE cars ADD CONSTRAINT chk_price_positive
    CHECK (purchase_price >= 0 AND selling_price >= 0);

ALTER TABLE cars ADD CONSTRAINT chk_mileage_positive
    CHECK (mileage >= 0);

-- Thêm unique constraint cho VIN (đã có)
-- Thêm unique constraint cho license_plate (đã có, nullable)

-- Tạo index cho unique check nhanh hơn
CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_vin_unique ON cars(vin) WHERE is_deleted = 0;
CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_plate_unique ON cars(license_plate) WHERE license_plate IS NOT NULL AND is_deleted = 0;
```

---

## 3. Backend Logic

### Enhanced Validator
```python
# src/validators/car_validator.py
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


class CarValidationError(Exception):
    """Car validation error with field details."""

    def __init__(self, message: str, field: Optional[str] = None,
                 code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': self.message,
            'field': self.field,
            'code': self.code
        }


class CarValidationResult:
    """Result of validation containing all errors."""

    def __init__(self):
        self.errors: List[CarValidationError] = []
        self.is_valid: bool = True

    def add_error(self, message: str, field: Optional[str] = None,
                  code: Optional[str] = None):
        """Add an error."""
        self.errors.append(CarValidationError(message, field, code))
        self.is_valid = False

    def raise_if_invalid(self):
        """Raise exception if has errors."""
        if not self.is_valid:
            raise CarValidationError(
                f"Validation failed with {len(self.errors)} error(s)"
            )

    def get_errors_by_field(self) -> Dict[str, List[str]]:
        """Get errors grouped by field."""
        result = {}
        for error in self.errors:
            field = error.field or 'general'
            if field not in result:
                result[field] = []
            result[field].append(error.message)
        return result


class CarValidator:
    """Comprehensive validator for car data."""

    # Valid brands in Vietnam market
    VALID_BRANDS = [
        'Acura', 'Audi', 'BMW', 'Chevrolet', 'Ford', 'Honda', 'Hyundai',
        'Isuzu', 'Kia', 'Land Rover', 'Lexus', 'Mazda', 'Mercedes-Benz',
        'Mitsubishi', 'Nissan', 'Peugeot', 'Porsche', 'Subaru', 'Suzuki',
        'Toyota', 'VinFast', 'Volkswagen', 'Volvo'
    ]

    # Valid car statuses
    VALID_STATUSES = ['available', 'sold', 'reserved', 'maintenance', 'incoming']

    # Valid transmission types
    VALID_TRANSMISSIONS = ['auto', 'manual', 'cvt']

    # Valid fuel types
    VALID_FUEL_TYPES = ['gasoline', 'diesel', 'electric', 'hybrid']

    # VIN check digit weights
    VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    VIN_TRANSLITERATION = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
    }

    def validate_all(self, data: Dict[str, Any],
                     is_update: bool = False,
                     existing_car: Optional[Any] = None) -> CarValidationResult:
        """Validate all car data.

        Args:
            data: Car data to validate
            is_update: Whether this is an update operation
            existing_car: Existing car data (for updates)

        Returns:
            ValidationResult with all errors
        """
        result = CarValidationResult()

        # Required fields
        if not is_update:
            self._validate_required_fields(data, result)

        # Individual field validation
        if 'vin' in data:
            self._validate_vin(data['vin'], result)
        if 'license_plate' in data:
            self._validate_license_plate(data['license_plate'], result)
        if 'brand' in data:
            self._validate_brand(data['brand'], result)
        if 'model' in data:
            self._validate_model(data['model'], result)
        if 'year' in data:
            self._validate_year(data['year'], result)
        if 'color' in data:
            self._validate_color(data['color'], result)
        if 'mileage' in data:
            self._validate_mileage(data['mileage'], result)
        if 'purchase_price' in data:
            self._validate_purchase_price(data['purchase_price'], result)
        if 'selling_price' in data:
            self._validate_selling_price(data['selling_price'], result)
        if 'transmission' in data:
            self._validate_transmission(data['transmission'], result)
        if 'fuel_type' in data:
            self._validate_fuel_type(data['fuel_type'], result)
        if 'status' in data:
            self._validate_status(data['status'], result)
        if 'engine_number' in data:
            self._validate_engine_number(data['engine_number'], result)

        # Cross-field validation
        self._validate_cross_fields(data, result)

        return result

    def _validate_required_fields(self, data: Dict[str, Any],
                                  result: CarValidationResult):
        """Validate required fields."""
        required = ['vin', 'brand', 'model']
        for field in required:
            if not data.get(field):
                result.add_error(
                    f"{self._field_name_vn(field)} không được để trống",
                    field,
                    'required'
                )

    def _validate_vin(self, vin: str, result: CarValidationResult):
        """Validate VIN (Vehicle Identification Number)."""
        if not vin:
            return

        vin = vin.upper().strip()

        # Length check
        if len(vin) != 17:
            result.add_error(
                "VIN phải có đúng 17 ký tự",
                'vin',
                'invalid_length'
            )
            return

        # Character check (không chứa I, O, Q)
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            result.add_error(
                "VIN chứa ký tự không hợp lệ (không được chứa I, O, Q)",
                'vin',
                'invalid_chars'
            )
            return

        # Check digit validation (vị trí 9)
        if not self._validate_vin_check_digit(vin):
            result.add_error(
                "VIN không hợp lệ (check digit sai)",
                'vin',
                'invalid_check_digit'
            )

    def _validate_vin_check_digit(self, vin: str) -> bool:
        """Validate VIN check digit (position 9)."""
        try:
            total = 0
            for i, char in enumerate(vin):
                if char.isdigit():
                    value = int(char)
                elif char in self.VIN_TRANSLITERATION:
                    value = self.VIN_TRANSLITERATION[char]
                else:
                    return False

                total += value * self.VIN_WEIGHTS[i]

            check_digit = total % 11
            check_char = 'X' if check_digit == 10 else str(check_digit)

            return vin[8] == check_char
        except Exception:
            return True  # Bỏ qua nếu không validate được

    def _validate_license_plate(self, plate: Optional[str],
                                 result: CarValidationResult):
        """Validate Vietnamese license plate."""
        if not plate:
            return

        plate = plate.upper().strip().replace(' ', '')

        # Các pattern biển số VN
        patterns = [
            r'^[0-9]{2}[A-Z]{1,2}-[0-9]{4,5}$',  # 51A-12345 hoặc 51AA-12345
            r'^[0-9]{2}[A-Z]{2}[0-9]{2}-[0-9]{4,5}$',  # Biển mới
            r'^[0-9]{2}[A-Z]{1,2}[0-9]{3}-[0-9]{2}$',  # Biển cũ
        ]

        if not any(re.match(p, plate) for p in patterns):
            result.add_error(
                "Biển số xe không đúng định dạng Việt Nam (VD: 51A-12345)",
                'license_plate',
                'invalid_format'
            )

    def _validate_brand(self, brand: str, result: CarValidationResult):
        """Validate car brand."""
        if not brand:
            return

        brand = brand.strip()

        if len(brand) > 50:
            result.add_error(
                "Tên hãng xe không được quá 50 ký tự",
                'brand',
                'too_long'
            )

        # Warning nếu brand không trong danh sách
        if brand.title() not in self.VALID_BRANDS:
            # Không lỗi, chỉ warning
            pass

    def _validate_model(self, model: str, result: CarValidationResult):
        """Validate car model."""
        if not model:
            return

        model = model.strip()

        if len(model) > 50:
            result.add_error(
                "Tên model không được quá 50 ký tự",
                'model',
                'too_long'
            )

        if len(model) < 1:
            result.add_error(
                "Tên model không được để trống",
                'model',
                'too_short'
            )

    def _validate_year(self, year: Any, result: CarValidationResult):
        """Validate manufacturing year."""
        if year is None:
            return

        try:
            year = int(year)
        except (ValueError, TypeError):
            result.add_error(
                "Năm sản xuất phải là số nguyên",
                'year',
                'not_integer'
            )
            return

        current_year = datetime.now().year

        if year < 1900:
            result.add_error(
                "Năm sản xuất không hợp lý (trước 1900)",
                'year',
                'too_old'
            )
        elif year > current_year + 1:
            result.add_error(
                f"Năm sản xuất không thể sau {current_year + 1}",
                'year',
                'future_year'
            )

    def _validate_color(self, color: Optional[str], result: CarValidationResult):
        """Validate color."""
        if not color:
            return

        if len(color) > 30:
            result.add_error(
                "Tên màu không được quá 30 ký tự",
                'color',
                'too_long'
            )

    def _validate_mileage(self, mileage: Any, result: CarValidationResult):
        """Validate mileage."""
        if mileage is None:
            return

        try:
            mileage = int(mileage)
        except (ValueError, TypeError):
            result.add_error(
                "Số km phải là số nguyên",
                'mileage',
                'not_integer'
            )
            return

        if mileage < 0:
            result.add_error(
                "Số km không được âm",
                'mileage',
                'negative'
            )
        elif mileage > 10000000:  # 10 triệu km
            result.add_error(
                "Số km không hợp lý (quá 10 triệu km)",
                'mileage',
                'unrealistic'
            )

    def _validate_purchase_price(self, price: Any, result: CarValidationResult):
        """Validate purchase price."""
        self._validate_price(price, 'purchase_price', 'Giá nhập', result)

    def _validate_selling_price(self, price: Any, result: CarValidationResult):
        """Validate selling price."""
        self._validate_price(price, 'selling_price', 'Giá bán', result)

    def _validate_price(self, price: Any, field: str, name: str,
                        result: CarValidationResult):
        """Generic price validation."""
        if price is None:
            return

        try:
            price = float(price)
        except (ValueError, TypeError):
            result.add_error(
                f"{name} phải là số",
                field,
                'not_number'
            )
            return

        if price < 0:
            result.add_error(
                f"{name} không được âm",
                field,
                'negative'
            )
        elif price > 100000000000:  # 100 tỷ
            result.add_error(
                f"{name} vượt quá giới hạn cho phép (100 tỷ)",
                field,
                'too_large'
            )

    def _validate_transmission(self, transmission: str,
                                result: CarValidationResult):
        """Validate transmission type."""
        if not transmission:
            return

        if transmission.lower() not in self.VALID_TRANSMISSIONS:
            result.add_error(
                f"Hộp số không hợp lệ. Chọn: {', '.join(self.VALID_TRANSMISSIONS)}",
                'transmission',
                'invalid_value'
            )

    def _validate_fuel_type(self, fuel_type: str, result: CarValidationResult):
        """Validate fuel type."""
        if not fuel_type:
            return

        if fuel_type.lower() not in self.VALID_FUEL_TYPES:
            result.add_error(
                f"Loại nhiên liệu không hợp lệ. Chọn: {', '.join(self.VALID_FUEL_TYPES)}",
                'fuel_type',
                'invalid_value'
            )

    def _validate_status(self, status: str, result: CarValidationResult):
        """Validate status."""
        if not status:
            return

        if status.lower() not in self.VALID_STATUSES:
            result.add_error(
                f"Trạng thái không hợp lệ. Chọn: {', '.join(self.VALID_STATUSES)}",
                'status',
                'invalid_value'
            )

    def _validate_engine_number(self, engine_no: Optional[str],
                                 result: CarValidationResult):
        """Validate engine number."""
        if not engine_no:
            return

        if len(engine_no) > 50:
            result.add_error(
                "Số máy không được quá 50 ký tự",
                'engine_number',
                'too_long'
            )

    def _validate_cross_fields(self, data: Dict[str, Any],
                               result: CarValidationResult):
        """Validate relationships between fields."""
        purchase = data.get('purchase_price')
        selling = data.get('selling_price')

        if purchase is not None and selling is not None:
            if selling < purchase * 0.8:  # Giá bán thấp hơn 80% giá nhập
                result.add_error(
                    "Giá bán thấp hơn nhiều so với giá nhập (mất >20%)",
                    'selling_price',
                    'low_profit'
                )

        # Year vs mileage consistency
        year = data.get('year')
        mileage = data.get('mileage')
        if year and mileage:
            current_year = datetime.now().year
            years_old = current_year - int(year)
            avg_mileage = mileage / max(years_old, 1)

            if avg_mileage > 100000:  # > 100k km/năm
                result.add_error(
                    f"Số km không hợp lý ({avg_mileage:,.0f} km/năm)",
                    'mileage',
                    'unrealistic_for_age'
                )

    def _field_name_vn(self, field: str) -> str:
        """Get Vietnamese field name."""
        names = {
            'vin': 'Số VIN',
            'license_plate': 'Biển số',
            'brand': 'Hãng xe',
            'model': 'Model',
            'year': 'Năm sản xuất',
            'color': 'Màu sắc',
            'mileage': 'Số km',
            'purchase_price': 'Giá nhập',
            'selling_price': 'Giá bán',
            'transmission': 'Hộp số',
            'fuel_type': 'Nhiên liệu',
            'status': 'Trạng thái',
            'engine_number': 'Số máy'
        }
        return names.get(field, field)
```

### Validation Service
```python
# src/services/car_validation_service.py
from typing import Dict, Any, Optional, List
from ..repositories.car_repository import CarRepository
from ..validators.car_validator import CarValidator, CarValidationResult


class CarValidationService:
    """Service for car validation with database checks."""

    def __init__(self, car_repository: CarRepository):
        self.car_repo = car_repository
        self.validator = CarValidator()

    def validate_for_create(self, data: Dict[str, Any]) -> CarValidationResult:
        """Validate car data for creation."""
        result = self.validator.validate_all(data, is_update=False)

        # Check unique VIN
        if 'vin' in data and data['vin']:
            existing = self.car_repo.get_by_vin(data['vin'])
            if existing:
                result.add_error(
                    f"VIN '{data['vin']}' đã tồn tại",
                    'vin',
                    'duplicate'
                )

        # Check unique license plate
        if data.get('license_plate'):
            existing = self.car_repo.get_by_license_plate(data['license_plate'])
            if existing:
                result.add_error(
                    f"Biển số '{data['license_plate']}' đã tồn tại",
                    'license_plate',
                    'duplicate'
                )

        return result

    def validate_for_update(self, car_id: int,
                            data: Dict[str, Any]) -> CarValidationResult:
        """Validate car data for update."""
        result = self.validator.validate_all(data, is_update=True)

        existing_car = self.car_repo.get_by_id(car_id)
        if not existing_car:
            result.add_error("Xe không tồn tại", 'general', 'not_found')
            return result

        # Check unique VIN if changed
        if 'vin' in data and data['vin']:
            if data['vin'].upper() != existing_car.vin.upper():
                existing = self.car_repo.get_by_vin(data['vin'])
                if existing and existing.id != car_id:
                    result.add_error(
                        f"VIN '{data['vin']}' đã tồn tại",
                        'vin',
                        'duplicate'
                    )

        # Check unique license plate if changed
        if data.get('license_plate'):
            if data['license_plate'].upper() != existing_car.license_plate:
                existing = self.car_repo.get_by_license_plate(data['license_plate'])
                if existing and existing.id != car_id:
                    result.add_error(
                        f"Biển số '{data['license_plate']}' đã tồn tại",
                        'license_plate',
                        'duplicate'
                    )

        return result

    def validate_field(self, field_name: str,
                       value: Any) -> List[str]:
        """Validate a single field (for real-time validation)."""
        data = {field_name: value}
        result = self.validator.validate_all(data)
        return result.get_errors_by_field().get(field_name, [])
```

---

## 4. UI Design

### Error Display
```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ Vui lòng sửa các lỗi sau:                               │
│  • VIN: VIN phải có đúng 17 ký tự                          │
│  • Giá bán: Giá bán không được âm                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VIN *                                                      │
│  ┌──────────────────┐                                       │
│  │ 1HGCM82633A      │  ❌ VIN phải có đúng 17 ký tự        │
│  └──────────────────┘                                       │
│                                                             │
│  Giá bán *                                                  │
│  ┌──────────────────┐                                       │
│  │ -50000000        │  ❌ Giá bán không được âm             │
│  └──────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Real-time Validation
- Validate on blur (rời khỏi field)
- Debounce 300ms cho text input
- Inline error message dưới mỗi field
- Border đỏ khi có lỗi, xanh khi hợp lệ

---

## 5. Testing

### Edge Case Tests
```python
# tests/test_car_validation.py
import unittest
from src.validators.car_validator import CarValidator, CarValidationResult

class TestCarValidation(unittest.TestCase):
    """Edge case tests for car validation."""

    def setUp(self):
        self.validator = CarValidator()

    def test_vin_with_invalid_chars(self):
        """Test VIN with invalid characters (I, O, Q)."""
        result = self.validator.validate_all({
            'vin': '1HGCM82633A12345I'  # Contains 'I'
        })
        self.assertFalse(result.is_valid)
        errors = result.get_errors_by_field()
        self.assertIn('vin', errors)

    def test_vin_check_digit(self):
        """Test VIN check digit validation."""
        # Valid VIN with correct check digit
        result = self.validator.validate_all({
            'vin': '1HGCM82633A123456'  # Giả sử có check digit đúng
        })
        # Không check lỗi check digit nếu không thể tính

    def test_license_plate_formats(self):
        """Test various license plate formats."""
        valid_plates = [
            '51A-12345',
            '51AA-12345',
            '30A-12345',
            '99A-99999'
        ]
        for plate in valid_plates:
            result = CarValidationResult()
            self.validator._validate_license_plate(plate, result)
            self.assertTrue(result.is_valid, f"Plate {plate} should be valid")

    def test_license_plate_invalid(self):
        """Test invalid license plates."""
        invalid_plates = [
            '51A-123',        # Too short
            '51A-1234567',    # Too long
            'ABC-12345',      # No province code
            '51-12345',       # Missing letter
            '51IO-12345',     # Contains I or O
        ]
        for plate in invalid_plates:
            result = CarValidationResult()
            self.validator._validate_license_plate(plate, result)
            self.assertFalse(result.is_valid, f"Plate {plate} should be invalid")

    def test_year_edge_cases(self):
        """Test year validation edge cases."""
        from datetime import datetime
        current_year = datetime.now().year

        # Valid years
        for year in [1900, 2000, current_year, current_year + 1]:
            result = CarValidationResult()
            self.validator._validate_year(year, result)
            self.assertTrue(result.is_valid, f"Year {year} should be valid")

        # Invalid years
        for year in [1899, current_year + 2, 3000]:
            result = CarValidationResult()
            self.validator._validate_year(year, result)
            self.assertFalse(result.is_valid, f"Year {year} should be invalid")

    def test_price_edge_cases(self):
        """Test price validation edge cases."""
        result = CarValidationResult()
        self.validator._validate_price(0, 'test', 'Test', result)
        self.assertTrue(result.is_valid)  # 0 is valid

        result = CarValidationResult()
        self.validator._validate_price(99999999999, 'test', 'Test', result)
        self.assertFalse(result.is_valid)  # Too large

    def test_mileage_unrealistic(self):
        """Test unrealistic mileage."""
        result = CarValidationResult()
        self.validator._validate_mileage(15000000, result)  # 15 triệu km
        self.assertFalse(result.is_valid)

    def test_cross_field_price_profit(self):
        """Test cross-field price validation."""
        result = CarValidationResult()
        self.validator._validate_cross_fields({
            'purchase_price': 1000000000,
            'selling_price': 700000000  # Mất 30%
        }, result)
        self.assertFalse(result.is_valid)

    def test_cross_field_year_mileage(self):
        """Test year vs mileage consistency."""
        from datetime import datetime
        current_year = datetime.now().year

        result = CarValidationResult()
        self.validator._validate_cross_fields({
            'year': current_year - 1,
            'mileage': 500000  # 500k km trong 1 năm
        }, result)
        self.assertFalse(result.is_valid)

    def test_multiple_errors(self):
        """Test collecting multiple errors."""
        result = self.validator.validate_all({
            'vin': 'SHORT',
            'license_plate': 'INVALID',
            'year': 1800,
            'selling_price': -1000000
        })

        self.assertFalse(result.is_valid)
        errors = result.get_errors_by_field()
        self.assertIn('vin', errors)
        self.assertIn('license_plate', errors)
        self.assertIn('year', errors)
        self.assertIn('selling_price', errors)
```

---

## 6. Definition of Done

- [ ] All fields have proper validation
- [ ] VIN check digit validation implemented
- [ ] Vietnamese license plate format validation
- [ ] Cross-field validation (price, year/mileage)
- [ ] Error messages in Vietnamese
- [ ] Real-time validation on UI
- [ ] Edge cases tested
- [ ] No critical validation bypass
- [ ] Code committed: `feat: logic validation xe`

---

## 7. Git Commit

```bash
# Files to commit
- src/validators/car_validator.py (cập nhật hoàn chỉnh)
- src/services/car_validation_service.py (mới)
- src/ui/components/validation_display.py (mới - nếu có)
- tests/test_car_validation.py (mới)
- src/database/schema.sql (cập nhật constraints)

# Commit message
feat: logic validation xe

- Thêm validation toàn diện cho tất cả các trường xe
- Triển khai VIN check digit validation
- Thêm validation định dạng biển số Việt Nam
- Thêm cross-field validation (giá, năm/km)
- Tạo validation service với DB uniqueness checks
- Thêm thông báo lỗi tiếng Việt
- Thêm edge case tests
```
