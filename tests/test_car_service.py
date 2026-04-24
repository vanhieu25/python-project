"""
Integration tests for Car Service.
Sprint 1.2: Car CRUD Operations
"""

import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.repositories.car_history_repository import CarHistoryRepository
from src.services.car_service import (
    CarService, CarNotFoundError, DuplicateVINError,
    CarInContractError, CarValidationServiceError
)


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

        # Admin user ID
        self.admin_id = 1

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_car_success(self):
        """Test successful car creation."""
        car_data = {
            "vin": "1HGCM82633A111111",
            "license_plate": "51Z-11111",
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
        self.assertEqual(car.status, "available")

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

    def test_create_car_duplicate_license_plate(self):
        """Test creating car with duplicate license plate."""
        car_data1 = {
            "vin": "1HGCM82633A333333",
            "license_plate": "51Z-33333",
            "brand": "Mazda",
            "model": "3"
        }
        self.car_service.create_car(car_data1, self.admin_id)

        car_data2 = {
            "vin": "1HGCM82633A444444",
            "license_plate": "51Z-33333",
            "brand": "Kia",
            "model": "Seltos"
        }

        with self.assertRaises(DuplicateVINError):
            self.car_service.create_car(car_data2, self.admin_id)

    def test_create_car_invalid_vin(self):
        """Test creating car with invalid VIN."""
        car_data = {
            "vin": "SHORT",
            "brand": "Toyota",
            "model": "Vios"
        }

        with self.assertRaises(CarValidationServiceError):
            self.car_service.create_car(car_data, self.admin_id)

    def test_get_car_success(self):
        """Test getting car by ID."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A555555",
            "brand": "Hyundai",
            "model": "Accent"
        }, self.admin_id)

        retrieved = self.car_service.get_car(car.id)
        self.assertEqual(retrieved.vin, "1HGCM82633A555555")

    def test_get_car_not_found(self):
        """Test getting non-existent car."""
        with self.assertRaises(CarNotFoundError):
            self.car_service.get_car(99999)

    def test_update_car_success(self):
        """Test updating car."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A666666",
            "brand": "Mazda",
            "model": "3",
            "selling_price": 800000000
        }, self.admin_id)

        updated = self.car_service.update_car(
            car.id,
            {"selling_price": 850000000, "color": "Trắng"},
            self.admin_id
        )

        self.assertEqual(updated.selling_price, 850000000)
        self.assertEqual(updated.color, "Trắng")

    def test_update_car_not_found(self):
        """Test updating non-existent car."""
        with self.assertRaises(CarNotFoundError):
            self.car_service.update_car(99999, {"color": "Đen"}, self.admin_id)

    def test_delete_car_soft(self):
        """Test soft deleting car."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A777777",
            "brand": "Ford",
            "model": "Ranger"
        }, self.admin_id)

        success = self.car_service.delete_car(car.id, self.admin_id)
        self.assertTrue(success)

        # Should not be found
        with self.assertRaises(CarNotFoundError):
            self.car_service.get_car(car.id)

        # Should exist with include_deleted
        deleted_car = self.car_repo.get_by_id(car.id, include_deleted=True)
        self.assertTrue(deleted_car.is_deleted)

    def test_delete_car_permanent(self):
        """Test permanent delete."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A888888",
            "brand": "Mitsubishi",
            "model": "Xpander"
        }, self.admin_id)

        success = self.car_service.delete_car(car.id, self.admin_id, permanent=True)
        self.assertTrue(success)

        # Should not exist at all
        deleted_car = self.car_repo.get_by_id(car.id, include_deleted=True)
        self.assertIsNone(deleted_car)

    def test_delete_sold_car_fails(self):
        """Test cannot delete sold car."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A999999",
            "brand": "Nissan",
            "model": "Navara",
            "status": "sold"
        }, self.admin_id)

        with self.assertRaises(CarInContractError):
            self.car_service.delete_car(car.id, self.admin_id)

    def test_change_status(self):
        """Test changing car status."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633A000000",
            "brand": "Kia",
            "model": "Morning",
            "status": "available"
        }, self.admin_id)

        updated = self.car_service.change_status(car.id, "reserved", self.admin_id)
        self.assertEqual(updated.status, "reserved")

    def test_get_car_statistics(self):
        """Test getting car statistics."""
        # Create cars with different statuses
        self.car_service.create_car({
            "vin": "1HGCM82633B111111",
            "brand": "Test1",
            "model": "Model1",
            "status": "available"
        }, self.admin_id)

        self.car_service.create_car({
            "vin": "1HGCM82633B222222",
            "brand": "Test2",
            "model": "Model2",
            "status": "sold"
        }, self.admin_id)

        stats = self.car_service.get_car_statistics()
        self.assertIn('total', stats)
        self.assertIn('available', stats)
        self.assertIn('sold', stats)
        self.assertGreaterEqual(stats['total'], 2)

    def test_list_cars(self):
        """Test listing cars."""
        # Create cars
        for i in range(3):
            self.car_service.create_car({
                "vin": f"1HGCM82633C{i:06d}",
                "brand": "ListTest",
                "model": f"Model{i}"
            }, self.admin_id)

        cars = self.car_service.list_cars()
        self.assertGreaterEqual(len(cars), 3)

    def test_list_cars_by_status(self):
        """Test listing cars by status."""
        self.car_service.create_car({
            "vin": "1HGCM82633D111111",
            "brand": "StatusTest",
            "model": "Available",
            "status": "available"
        }, self.admin_id)

        available_cars = self.car_service.list_cars(status="available")
        for car in available_cars:
            self.assertEqual(car.status, "available")

    def test_get_car_history(self):
        """Test getting car history."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633E111111",
            "brand": "History",
            "model": "Test"
        }, self.admin_id)

        # Make some changes
        self.car_service.update_car(car.id, {"color": "Đen"}, self.admin_id)
        self.car_service.update_car(car.id, {"color": "Trắng"}, self.admin_id)

        history = self.car_service.get_car_history(car.id)
        self.assertGreaterEqual(len(history), 1)  # At least create record

    def test_restore_car(self):
        """Test restoring soft-deleted car."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633F111111",
            "brand": "Restore",
            "model": "Test"
        }, self.admin_id)

        # Delete
        self.car_service.delete_car(car.id, self.admin_id)

        # Restore
        restored = self.car_service.restore_car(car.id, self.admin_id)
        self.assertFalse(restored.is_deleted)

        # Should be found again
        found = self.car_service.get_car(car.id)
        self.assertEqual(found.id, car.id)

    def test_restore_not_deleted_car(self):
        """Test restoring car that wasn't deleted."""
        car = self.car_service.create_car({
            "vin": "1HGCM82633G111111",
            "brand": "NotDeleted",
            "model": "Test"
        }, self.admin_id)

        from src.services.car_service import CarServiceError
        with self.assertRaises(CarServiceError):
            self.car_service.restore_car(car.id, self.admin_id)

    def test_validate_field(self):
        """Test field validation."""
        error = self.car_service.validate_field('year', 1800)
        self.assertIsNotNone(error)

        error = self.car_service.validate_field('year', 2023)
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
