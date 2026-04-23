"""
Car Repository Module
Provides data access operations for Car model.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper
from ..models.car import Car


class CarRepository:
    """Repository for Car data access."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def create(self, car_data: Dict[str, Any]) -> int:
        """Create a new car record.

        Args:
            car_data: Dictionary containing car data

        Returns:
            int: ID of created car
        """
        query = """
            INSERT INTO cars (
                vin, license_plate, brand, model, year, color,
                engine_number, transmission, fuel_type, mileage,
                purchase_price, selling_price, status, description,
                images, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Handle images (convert list to JSON)
        images = car_data.get('images')
        if isinstance(images, list):
            import json
            images = json.dumps(images)

        params = (
            car_data['vin'].upper() if car_data.get('vin') else None,
            car_data.get('license_plate', '').upper() if car_data.get('license_plate') else None,
            car_data.get('brand'),
            car_data.get('model'),
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
            images,
            car_data.get('created_by')
        )

        return self.db.execute(query, params)

    def get_by_id(self, car_id: int, include_deleted: bool = False) -> Optional[Car]:
        """Get car by ID.

        Args:
            car_id: Car ID
            include_deleted: Whether to include soft-deleted cars

        Returns:
            Car instance or None
        """
        if include_deleted:
            query = "SELECT * FROM cars WHERE id = ?"
        else:
            query = "SELECT * FROM cars WHERE id = ? AND is_deleted = 0"

        row = self.db.fetch_one(query, (car_id,))
        return Car.from_dict(row) if row else None

    def get_by_vin(self, vin: str) -> Optional[Car]:
        """Get car by VIN.

        Args:
            vin: VIN string

        Returns:
            Car instance or None
        """
        query = "SELECT * FROM cars WHERE vin = ? AND is_deleted = 0"
        row = self.db.fetch_one(query, (vin.upper(),))
        return Car.from_dict(row) if row else None

    def get_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Get car by license plate.

        Args:
            license_plate: License plate string

        Returns:
            Car instance or None
        """
        query = """
            SELECT * FROM cars
            WHERE license_plate = ? AND is_deleted = 0
        """
        row = self.db.fetch_one(query, (license_plate.upper(),))
        return Car.from_dict(row) if row else None

    def get_all(self, status: Optional[str] = None,
                include_deleted: bool = False) -> List[Car]:
        """Get all cars with optional filters.

        Args:
            status: Filter by status
            include_deleted: Whether to include soft-deleted cars

        Returns:
            List of Car instances
        """
        if include_deleted:
            if status:
                query = """
                    SELECT * FROM cars WHERE status = ?
                    ORDER BY created_at DESC
                """
                rows = self.db.fetch_all(query, (status,))
            else:
                query = "SELECT * FROM cars ORDER BY created_at DESC"
                rows = self.db.fetch_all(query)
        else:
            if status:
                query = """
                    SELECT * FROM cars
                    WHERE status = ? AND is_deleted = 0
                    ORDER BY created_at DESC
                """
                rows = self.db.fetch_all(query, (status,))
            else:
                query = """
                    SELECT * FROM cars WHERE is_deleted = 0
                    ORDER BY created_at DESC
                """
                rows = self.db.fetch_all(query)

        return [Car.from_dict(row) for row in rows if row]

    def update(self, car_id: int, car_data: Dict[str, Any]) -> bool:
        """Update car record.

        Args:
            car_id: Car ID
            car_data: Dictionary containing updated data

        Returns:
            bool: True if successful
        """
        # Build dynamic query based on provided fields
        allowed_fields = [
            'license_plate', 'brand', 'model', 'year', 'color',
            'engine_number', 'transmission', 'fuel_type', 'mileage',
            'purchase_price', 'selling_price', 'status', 'description', 'images'
        ]

        fields = []
        params = []

        for field in allowed_fields:
            if field in car_data:
                fields.append(f"{field} = ?")
                value = car_data[field]

                # Handle images (convert list to JSON)
                if field == 'images' and isinstance(value, list):
                    import json
                    value = json.dumps(value)

                # Handle license_plate (uppercase)
                if field == 'license_plate' and value:
                    value = value.upper()

                params.append(value)

        if not fields:
            return False

        query = f"UPDATE cars SET {', '.join(fields)} WHERE id = ?"
        params.append(car_id)

        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def soft_delete(self, car_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete car.

        Args:
            car_id: Car ID
            deleted_by: User ID who deleted

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE cars SET
                is_deleted = 1,
                deleted_at = ?,
                deleted_by = ?,
                status = 'sold'
            WHERE id = ?
        """
        try:
            self.db.execute(query, (datetime.now(), deleted_by, car_id))
            return True
        except Exception:
            return False

    def restore(self, car_id: int) -> bool:
        """Restore soft-deleted car.

        Args:
            car_id: Car ID

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE cars SET
                is_deleted = 0,
                deleted_at = NULL,
                deleted_by = NULL,
                status = 'available'
            WHERE id = ? AND is_deleted = 1
        """
        try:
            self.db.execute(query, (car_id,))
            return True
        except Exception:
            return False

    def delete_permanently(self, car_id: int) -> bool:
        """Permanently delete car.

        Args:
            car_id: Car ID

        Returns:
            bool: True if successful
        """
        query = "DELETE FROM cars WHERE id = ?"
        try:
            self.db.execute(query, (car_id,))
            return True
        except Exception:
            return False

    def count(self, status: Optional[str] = None) -> int:
        """Count cars.

        Args:
            status: Filter by status

        Returns:
            int: Number of cars
        """
        if status:
            query = """
                SELECT COUNT(*) as count FROM cars
                WHERE status = ? AND is_deleted = 0
            """
            result = self.db.fetch_one(query, (status,))
        else:
            query = """
                SELECT COUNT(*) as count FROM cars WHERE is_deleted = 0
            """
            result = self.db.fetch_one(query)

        return result['count'] if result else 0

    def get_brands(self) -> List[str]:
        """Get list of unique brands.

        Returns:
            List of brand names
        """
        query = """
            SELECT DISTINCT brand FROM cars
            WHERE is_deleted = 0 AND brand IS NOT NULL
            ORDER BY brand
        """
        rows = self.db.fetch_all(query)
        return [row['brand'] for row in rows if row['brand']]

    def get_models_by_brand(self, brand: str) -> List[str]:
        """Get list of models for a brand.

        Args:
            brand: Brand name

        Returns:
            List of model names
        """
        query = """
            SELECT DISTINCT model FROM cars
            WHERE brand = ? AND is_deleted = 0 AND model IS NOT NULL
            ORDER BY model
        """
        rows = self.db.fetch_all(query, (brand,))
        return [row['model'] for row in rows if row['model']]

    def exists(self, vin: Optional[str] = None,
               license_plate: Optional[str] = None,
               exclude_id: Optional[int] = None) -> bool:
        """Check if car exists by VIN or license plate.

        Args:
            vin: VIN to check
            license_plate: License plate to check
            exclude_id: Car ID to exclude from check

        Returns:
            bool: True if exists
        """
        conditions = []
        params = []

        if vin:
            conditions.append("vin = ?")
            params.append(vin.upper())

        if license_plate:
            conditions.append("license_plate = ?")
            params.append(license_plate.upper())

        if not conditions:
            return False

        query = f"""
            SELECT 1 FROM cars
            WHERE ({' OR '.join(conditions)})
            AND is_deleted = 0
        """

        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)

        result = self.db.fetch_one(query, tuple(params))
        return result is not None

    def update_status(self, car_id: int, status: str) -> bool:
        """Update car status.

        Args:
            car_id: Car ID
            status: New status

        Returns:
            bool: True if successful
        """
        query = "UPDATE cars SET status = ? WHERE id = ?"
        try:
            self.db.execute(query, (status, car_id))
            return True
        except Exception:
            return False
