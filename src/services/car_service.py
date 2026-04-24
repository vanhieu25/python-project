"""
Car Service Module
Business logic for car management.
"""

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


class CarValidationServiceError(CarServiceError):
    """Validation error from service."""
    def __init__(self, message: str, errors: List[Dict] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(message)


class CarService:
    """Service layer for car operations."""

    def __init__(self, car_repository: CarRepository,
                 history_repository: CarHistoryRepository):
        """Initialize car service.

        Args:
            car_repository: Car repository instance
            history_repository: History repository instance
        """
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
            CarValidationServiceError: If data is invalid
            DuplicateVINError: If VIN already exists
        """
        # Validate all fields
        try:
            self.validator.validate_all(car_data, is_update=False)
        except CarValidationError as e:
            raise CarValidationServiceError(e.message, [{'field': e.field, 'message': e.message}])

        # Check for duplicate VIN
        if self.car_repo.exists(vin=car_data.get('vin')):
            raise DuplicateVINError(f"VIN '{car_data['vin']}' đã tồn tại")

        # Check for duplicate license plate
        if car_data.get('license_plate'):
            if self.car_repo.exists(license_plate=car_data['license_plate']):
                raise DuplicateVINError(f"Biển số '{car_data['license_plate']}' đã tồn tại")

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

        Raises:
            CarNotFoundError: If car not found
            CarValidationServiceError: If data is invalid
        """
        # Check car exists
        car = self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")

        # Validate
        try:
            self.validator.validate_all(car_data, is_update=True)
        except CarValidationError as e:
            raise CarValidationServiceError(e.message, [{'field': e.field, 'message': e.message}])

        # Check for duplicate license plate if changed
        if car_data.get('license_plate'):
            if car_data['license_plate'].upper() != (car.license_plate or '').upper():
                if self.car_repo.exists(license_plate=car_data['license_plate']):
                    raise DuplicateVINError(f"Biển số '{car_data['license_plate']}' đã tồn tại")

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

        # Check if car is sold (cannot delete)
        if car.status == 'sold':
            raise CarInContractError("Không thể xóa xe đã bán")

        try:
            if permanent:
                # Record history before permanent delete
                self.history_repo.record_delete(car_id, deleted_by)
                success = self.car_repo.delete_permanently(car_id)
            else:
                success = self.car_repo.soft_delete(car_id, deleted_by)
                if success:
                    self.history_repo.record_delete(car_id, deleted_by)

            return success
        except Exception as e:
            raise CarServiceError(f"Không thể xóa xe: {str(e)}")

    def restore_car(self, car_id: int, restored_by: int) -> Car:
        """Restore soft-deleted car.

        Args:
            car_id: Car ID
            restored_by: User ID who restores

        Returns:
            Restored Car instance
        """
        car = self.car_repo.get_by_id(car_id, include_deleted=True)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")

        if not car.is_deleted:
            raise CarServiceError("Xe chưa bị xóa")

        try:
            success = self.car_repo.restore(car_id)
            if not success:
                raise CarServiceError("Khôi phục thất bại")

            # Record history
            self.history_repo.record_create(car_id, restored_by)

            return self.car_repo.get_by_id(car_id)
        except Exception as e:
            raise CarServiceError(f"Không thể khôi phục xe: {str(e)}")

    def get_car(self, car_id: int) -> Car:
        """Get car by ID.

        Args:
            car_id: Car ID

        Returns:
            Car instance

        Raises:
            CarNotFoundError: If car not found
        """
        car = self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Không tìm thấy xe với ID {car_id}")
        return car

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        """Get car by VIN.

        Args:
            vin: VIN string

        Returns:
            Car instance or None
        """
        return self.car_repo.get_by_vin(vin)

    def list_cars(self, status: Optional[str] = None,
                  include_deleted: bool = False) -> List[Car]:
        """List all cars.

        Args:
            status: Filter by status
            include_deleted: Whether to include soft-deleted

        Returns:
            List of Car instances
        """
        return self.car_repo.get_all(status, include_deleted)

    def get_car_history(self, car_id: int) -> List[Dict[str, Any]]:
        """Get history for a car.

        Args:
            car_id: Car ID

        Returns:
            List of history records
        """
        return self.history_repo.get_history(car_id)

    def change_status(self, car_id: int, new_status: str,
                      changed_by: int) -> Car:
        """Change car status.

        Args:
            car_id: Car ID
            new_status: New status
            changed_by: User ID who changes

        Returns:
            Updated Car instance
        """
        car = self.get_car(car_id)
        old_status = car.status

        if old_status == new_status:
            return car

        success = self.car_repo.update_status(car_id, new_status)
        if not success:
            raise CarServiceError("Không thể đổi trạng thái")

        # Record history
        self.history_repo.record_update(
            car_id, 'status', old_status, new_status, changed_by
        )

        return self.car_repo.get_by_id(car_id)

    def _get_changes(self, car: Car, new_data: Dict[str, Any]) -> List[Dict]:
        """Get list of changes for history tracking.

        Args:
            car: Current car data
            new_data: New data

        Returns:
            List of changes
        """
        changes = []
        car_dict = car.__dict__

        for field, new_value in new_data.items():
            old_value = car_dict.get(field)

            # Normalize values for comparison
            if old_value != new_value:
                # Skip None vs empty string
                if old_value is None and new_value == '':
                    continue
                if old_value == '' and new_value is None:
                    continue

                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value
                })

        return changes

    def get_car_statistics(self) -> Dict[str, Any]:
        """Get car statistics.

        Returns:
            Dictionary with statistics
        """
        total = self.car_repo.count()
        available = self.car_repo.count(status='available')
        sold = self.car_repo.count(status='sold')
        reserved = self.car_repo.count(status='reserved')
        maintenance = self.car_repo.count(status='maintenance')

        return {
            'total': total,
            'available': available,
            'sold': sold,
            'reserved': reserved,
            'maintenance': maintenance
        }

    def validate_field(self, field_name: str, value: Any) -> Optional[str]:
        """Validate a single field.

        Args:
            field_name: Field name
            value: Field value

        Returns:
            Error message or None if valid
        """
        try:
            if field_name == 'vin':
                self.validator.validate_vin(value)
            elif field_name == 'license_plate':
                self.validator.validate_license_plate(value)
            elif field_name == 'year':
                self.validator.validate_year(value)
            elif field_name == 'purchase_price':
                self.validator.validate_price(value, "Giá nhập")
            elif field_name == 'selling_price':
                self.validator.validate_price(value, "Giá bán")
            elif field_name == 'mileage':
                self.validator.validate_mileage(value)
            return None
        except CarValidationError as e:
            return e.message
