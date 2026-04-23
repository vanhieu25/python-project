"""
Car Validator Module
Validation logic for car data.
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime


class CarValidationError(Exception):
    """Car validation error with field information."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class CarValidator:
    """Validator for car data."""

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

    # VIN transliteration for check digit
    VIN_TRANSLITERATION = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
    }

    # VIN position weights
    VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validate_vin(vin: str) -> None:
        """Validate VIN (Vehicle Identification Number).

        Args:
            vin: VIN string to validate

        Raises:
            CarValidationError: If VIN is invalid
        """
        if not vin:
            raise CarValidationError("VIN không được để trống", 'vin')

        vin = vin.upper().strip()

        # Length check
        if len(vin) != 17:
            raise CarValidationError("VIN phải có đúng 17 ký tự", 'vin')

        # Character check (không chứa I, O, Q)
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            raise CarValidationError(
                "VIN chứa ký tự không hợp lệ (không được chứa I, O, Q)", 'vin'
            )

        # Check digit validation (vị trí 9) - optional
        # Tính toán check digit phức tạp, có thể bỏ qua cho sprint đầu

    @staticmethod
    def validate_license_plate(plate: Optional[str]) -> None:
        """Validate Vietnamese license plate.

        Args:
            plate: License plate string

        Raises:
            CarValidationError: If plate format is invalid
        """
        if not plate:
            return  # Có thể null

        plate = plate.upper().strip().replace(' ', '')

        # Pattern: XXA-XXXXX hoặc XXAA-XXXXX (biển số VN)
        pattern = r'^[0-9]{2}[A-Z]{1,2}-[0-9]{4,5}$'
        if not re.match(pattern, plate):
            raise CarValidationError(
                "Biển số xe không đúng định dạng Việt Nam (VD: 51A-12345)",
                'license_plate'
            )

    @staticmethod
    def validate_year(year: Optional[int]) -> None:
        """Validate manufacturing year.

        Args:
            year: Manufacturing year

        Raises:
            CarValidationError: If year is invalid
        """
        if year is None:
            return

        current_year = datetime.now().year

        if year < 1900:
            raise CarValidationError(
                f"Năm sản xuất không hợp lý (trước 1900)", 'year'
            )

        if year > current_year + 1:
            raise CarValidationError(
                f"Năm sản xuất không thể sau {current_year + 1}", 'year'
            )

    @staticmethod
    def validate_price(price: Optional[float], field_name: str = "Giá") -> None:
        """Validate price value.

        Args:
            price: Price value
            field_name: Name of the price field for error message

        Raises:
            CarValidationError: If price is invalid
        """
        if price is None:
            return

        if price < 0:
            raise CarValidationError(f"{field_name} không được âm", 'price')

        if price > 100000000000:  # 100 tỷ
            raise CarValidationError(
                f"{field_name} vượt quá giới hạn cho phép (100 tỷ)", 'price'
            )

    @staticmethod
    def validate_mileage(mileage: Optional[int]) -> None:
        """Validate mileage.

        Args:
            mileage: Mileage value

        Raises:
            CarValidationError: If mileage is invalid
        """
        if mileage is None:
            return

        if mileage < 0:
            raise CarValidationError("Số km không được âm", 'mileage')

        if mileage > 10000000:  # 10 triệu km
            raise CarValidationError(
                "Số km không hợp lý (quá 10 triệu km)", 'mileage'
            )

    @staticmethod
    def validate_brand(brand: str) -> None:
        """Validate brand name.

        Args:
            brand: Brand name

        Raises:
            CarValidationError: If brand is invalid
        """
        if not brand:
            raise CarValidationError("Hãng xe không được để trống", 'brand')

        if len(brand) > 50:
            raise CarValidationError(
                "Tên hãng xe không được quá 50 ký tự", 'brand'
            )

    @staticmethod
    def validate_model(model: str) -> None:
        """Validate model name.

        Args:
            model: Model name

        Raises:
            CarValidationError: If model is invalid
        """
        if not model:
            raise CarValidationError("Model xe không được để trống", 'model')

        if len(model) > 50:
            raise CarValidationError(
                "Tên model không được quá 50 ký tự", 'model'
            )

    @staticmethod
    def validate_status(status: str) -> None:
        """Validate status value.

        Args:
            status: Status string

        Raises:
            CarValidationError: If status is invalid
        """
        if status not in CarValidator.VALID_STATUSES:
            raise CarValidationError(
                f"Trạng thái không hợp lệ. Các giá trị hợp lệ: {', '.join(CarValidator.VALID_STATUSES)}",
                'status'
            )

    @staticmethod
    def validate_transmission(transmission: Optional[str]) -> None:
        """Validate transmission type.

        Args:
            transmission: Transmission type

        Raises:
            CarValidationError: If transmission is invalid
        """
        if transmission is None:
            return

        if transmission not in CarValidator.VALID_TRANSMISSIONS:
            raise CarValidationError(
                f"Hộp số không hợp lệ. Các giá trị hợp lệ: {', '.join(CarValidator.VALID_TRANSMISSIONS)}",
                'transmission'
            )

    @staticmethod
    def validate_fuel_type(fuel_type: Optional[str]) -> None:
        """Validate fuel type.

        Args:
            fuel_type: Fuel type

        Raises:
            CarValidationError: If fuel type is invalid
        """
        if fuel_type is None:
            return

        if fuel_type not in CarValidator.VALID_FUEL_TYPES:
            raise CarValidationError(
                f"Loại nhiên liệu không hợp lệ. Các giá trị hợp lệ: {', '.join(CarValidator.VALID_FUEL_TYPES)}",
                'fuel_type'
            )

    def validate_all(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """Validate all car data.

        Args:
            data: Dictionary containing car data
            is_update: Whether this is an update operation

        Raises:
            CarValidationError: If any validation fails
        """
        # Required fields (only for create)
        if not is_update:
            if not data.get('vin'):
                raise CarValidationError("VIN không được để trống", 'vin')
            if not data.get('brand'):
                raise CarValidationError("Hãng xe không được để trống", 'brand')
            if not data.get('model'):
                raise CarValidationError("Model xe không được để trống", 'model')

        # Validate individual fields if present
        if 'vin' in data and data['vin']:
            self.validate_vin(data['vin'])

        if 'license_plate' in data and data['license_plate']:
            self.validate_license_plate(data['license_plate'])

        if 'brand' in data:
            self.validate_brand(data['brand'])

        if 'model' in data:
            self.validate_model(data['model'])

        if 'year' in data and data['year'] is not None:
            self.validate_year(data['year'])

        if 'purchase_price' in data and data['purchase_price'] is not None:
            self.validate_price(data['purchase_price'], "Giá nhập")

        if 'selling_price' in data and data['selling_price'] is not None:
            self.validate_price(data['selling_price'], "Giá bán")

        if 'mileage' in data and data['mileage'] is not None:
            self.validate_mileage(data['mileage'])

        if 'status' in data:
            self.validate_status(data['status'])

        if 'transmission' in data and data['transmission']:
            self.validate_transmission(data['transmission'])

        if 'fuel_type' in data and data['fuel_type']:
            self.validate_fuel_type(data['fuel_type'])
