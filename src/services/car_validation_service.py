"""
Car Validation Service Module
Service for car validation with database checks.
"""

from typing import Dict, Any, Optional, List
from ..repositories.car_repository import CarRepository
from ..validators.car_validator import CarValidator, CarValidationResult


class CarValidationService:
    """Service for car validation with database checks."""

    def __init__(self, car_repository: CarRepository):
        """Initialize validation service.

        Args:
            car_repository: Car repository instance
        """
        self.car_repo = car_repository
        self.validator = CarValidator()

    def validate_for_create(self, data: Dict[str, Any]) -> CarValidationResult:
        """Validate car data for creation.

        Args:
            data: Car data to validate

        Returns:
            ValidationResult with all errors
        """
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
        """Validate car data for update.

        Args:
            car_id: Car ID being updated
            data: Car data to validate

        Returns:
            ValidationResult with all errors
        """
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
            current_plate = (existing_car.license_plate or '').upper()
            new_plate = data['license_plate'].upper()
            if new_plate != current_plate:
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
        """Validate a single field (for real-time validation).

        Args:
            field_name: Field name to validate
            value: Field value

        Returns:
            List of error messages (empty if valid)
        """
        data = {field_name: value}
        result = self.validator.validate_all(data)
        return result.get_errors_by_field().get(field_name, [])

    def get_validation_errors(self, data: Dict[str, Any],
                              is_update: bool = False,
                              car_id: Optional[int] = None) -> Dict[str, List[str]]:
        """Get all validation errors as dictionary.

        Args:
            data: Car data to validate
            is_update: Whether this is an update
            car_id: Car ID (for update validation)

        Returns:
            Dictionary of field -> list of errors
        """
        if is_update and car_id:
            result = self.validate_for_update(car_id, data)
        else:
            result = self.validate_for_create(data)

        return result.get_errors_by_field()

    def is_valid(self, data: Dict[str, Any],
                 is_update: bool = False,
                 car_id: Optional[int] = None) -> bool:
        """Quick check if data is valid.

        Args:
            data: Car data to validate
            is_update: Whether this is an update
            car_id: Car ID (for update validation)

        Returns:
            True if valid, False otherwise
        """
        if is_update and car_id:
            result = self.validate_for_update(car_id, data)
        else:
            result = self.validate_for_create(data)

        return result.is_valid
