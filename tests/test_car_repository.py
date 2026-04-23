"""
Unit tests for Car Repository.
Sprint 1.1: Car Management Initial
"""

import unittest
import os
import tempfile
import shutil

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.models.car import Car


class TestCarRepository(unittest.TestCase):
    """Test cases for CarRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.car_repo = CarRepository(self.db)

    def tearDown(self):
        """Clean up test database."""
        shutil.rmtree(self.temp_dir)

    def test_create_car(self):
        """Test creating a new car."""
        car_data = {
            "vin": "1HGCM82633A111111",
            "license_plate": "51Z-11111",  # Unique plate
            "brand": "Toyota",
            "model": "Vios",
            "year": 2023,
            "color": "Trắng",
            "purchase_price": 550000000,
            "selling_price": 600000000,
            "status": "available"
        }

        car_id = self.car_repo.create(car_data)
        self.assertGreater(car_id, 0)

        # Verify
        car = self.car_repo.get_by_id(car_id)
        self.assertIsNotNone(car)
        self.assertEqual(car.vin, "1HGCM82633A111111")
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Vios")

    def test_create_car_minimal_data(self):
        """Test creating car with minimal required data."""
        car_data = {
            "vin": "1HGCM82633A222222",
            "brand": "Honda",
            "model": "City"
        }

        car_id = self.car_repo.create(car_data)
        self.assertGreater(car_id, 0)

        car = self.car_repo.get_by_id(car_id)
        self.assertEqual(car.status, "available")  # Default status
        self.assertEqual(car.mileage, 0)  # Default mileage

    def test_get_by_vin(self):
        """Test getting car by VIN."""
        # Create car
        car_data = {
            "vin": "1HGCM82633A333333",
            "brand": "Mazda",
            "model": "3"
        }
        self.car_repo.create(car_data)

        # Get by VIN (case insensitive)
        car = self.car_repo.get_by_vin("1hgcm82633a333333")
        self.assertIsNotNone(car)
        self.assertEqual(car.brand, "Mazda")

    def test_get_by_license_plate(self):
        """Test getting car by license plate."""
        # Create car
        car_data = {
            "vin": "1HGCM82633A444444",
            "license_plate": "51A-44444",
            "brand": "Kia",
            "model": "Seltos"
        }
        self.car_repo.create(car_data)

        # Get by license plate (case insensitive)
        car = self.car_repo.get_by_license_plate("51a-44444")
        self.assertIsNotNone(car)
        self.assertEqual(car.brand, "Kia")

    def test_get_all_cars(self):
        """Test getting all cars."""
        # Get initial count (includes seed data)
        initial_cars = self.car_repo.get_all()
        initial_count = len(initial_cars)

        # Create multiple cars
        for i in range(3):
            self.car_repo.create({
                "vin": f"1HGCM82633A{i:06d}",
                "brand": "TestBrand",
                "model": f"Model{i}"
            })

        cars = self.car_repo.get_all()
        # Should include seed data + test cars
        self.assertEqual(len(cars), initial_count + 3)

    def test_get_all_by_status(self):
        """Test getting cars by status."""
        # Create cars with different statuses
        self.car_repo.create({
            "vin": "1HGCM82633A555555",
            "brand": "Test1",
            "model": "Model1",
            "status": "available"
        })
        self.car_repo.create({
            "vin": "1HGCM82633A666666",
            "brand": "Test2",
            "model": "Model2",
            "status": "sold"
        })

        available_cars = self.car_repo.get_all(status="available")
        sold_cars = self.car_repo.get_all(status="sold")

        self.assertGreaterEqual(len(available_cars), 1)
        self.assertGreaterEqual(len(sold_cars), 1)

    def test_update_car(self):
        """Test updating car."""
        # Create car
        car_id = self.car_repo.create({
            "vin": "1HGCM82633A777777",
            "brand": "Hyundai",
            "model": "Accent",
            "color": "Trắng"
        })

        # Update
        result = self.car_repo.update(car_id, {
            "color": "Đen",
            "selling_price": 500000000
        })
        self.assertTrue(result)

        # Verify
        car = self.car_repo.get_by_id(car_id)
        self.assertEqual(car.color, "Đen")
        self.assertEqual(car.selling_price, 500000000)

    def test_soft_delete(self):
        """Test soft delete."""
        # Create car
        car_id = self.car_repo.create({
            "vin": "1HGCM82633A888888",
            "brand": "Ford",
            "model": "Ranger"
        })

        # Soft delete
        result = self.car_repo.soft_delete(car_id, deleted_by=1)
        self.assertTrue(result)

        # Should not appear in get_all
        car = self.car_repo.get_by_id(car_id)
        self.assertIsNone(car)

        # Should appear with include_deleted
        car = self.car_repo.get_by_id(car_id, include_deleted=True)
        self.assertIsNotNone(car)
        self.assertTrue(car.is_deleted)

    def test_restore(self):
        """Test restoring soft-deleted car."""
        # Create and delete
        car_id = self.car_repo.create({
            "vin": "1HGCM82633A999999",
            "brand": "Mitsubishi",
            "model": "Xpander"
        })
        self.car_repo.soft_delete(car_id)

        # Restore
        result = self.car_repo.restore(car_id)
        self.assertTrue(result)

        # Should appear again
        car = self.car_repo.get_by_id(car_id)
        self.assertIsNotNone(car)
        self.assertFalse(car.is_deleted)

    def test_delete_permanently(self):
        """Test permanent delete."""
        # Create car
        car_id = self.car_repo.create({
            "vin": "1HGCM82633A000000",
            "brand": "Nissan",
            "model": "Navara"
        })

        # Delete permanently
        result = self.car_repo.delete_permanently(car_id)
        self.assertTrue(result)

        # Should not appear even with include_deleted
        car = self.car_repo.get_by_id(car_id, include_deleted=True)
        self.assertIsNone(car)

    def test_count(self):
        """Test counting cars."""
        # Get initial count (includes seed data)
        initial_count = self.car_repo.count()

        # Create cars
        for i in range(3):
            self.car_repo.create({
                "vin": f"1HGCM82633B{i:06d}",
                "brand": "CountTest",
                "model": f"Model{i}",
                "status": "available"
            })

        self.assertEqual(self.car_repo.count(), initial_count + 3)

    def test_exists(self):
        """Test checking car existence."""
        # Create car
        self.car_repo.create({
            "vin": "1HGCM82633C111111",
            "license_plate": "51C-11111",
            "brand": "ExistTest",
            "model": "Model"
        })

        self.assertTrue(self.car_repo.exists(vin="1HGCM82633C111111"))
        self.assertTrue(self.car_repo.exists(license_plate="51C-11111"))
        self.assertFalse(self.car_repo.exists(vin="NONEXISTENT"))

    def test_get_brands(self):
        """Test getting unique brands."""
        # Create cars
        self.car_repo.create({
            "vin": "1HGCM82633D111111",
            "brand": "BrandA",
            "model": "Model1"
        })
        self.car_repo.create({
            "vin": "1HGCM82633D222222",
            "brand": "BrandB",
            "model": "Model2"
        })

        brands = self.car_repo.get_brands()
        self.assertIn("BrandA", brands)
        self.assertIn("BrandB", brands)

    def test_get_models_by_brand(self):
        """Test getting models for a brand."""
        # Create cars
        self.car_repo.create({
            "vin": "1HGCM82633E111111",
            "brand": "ToyotaTest",
            "model": "Corolla"
        })
        self.car_repo.create({
            "vin": "1HGCM82633E222222",
            "brand": "ToyotaTest",
            "model": "CamryTest"
        })

        models = self.car_repo.get_models_by_brand("ToyotaTest")
        self.assertIn("Corolla", models)
        self.assertIn("CamryTest", models)

    def test_update_status(self):
        """Test updating car status."""
        # Create car
        car_id = self.car_repo.create({
            "vin": "1HGCM82633F111111",
            "brand": "StatusTest",
            "model": "Model",
            "status": "available"
        })

        # Update status
        result = self.car_repo.update_status(car_id, "reserved")
        self.assertTrue(result)

        # Verify
        car = self.car_repo.get_by_id(car_id)
        self.assertEqual(car.status, "reserved")


class TestCarModel(unittest.TestCase):
    """Test cases for Car model."""

    def test_from_dict(self):
        """Test creating Car from dictionary."""
        data = {
            "id": 1,
            "vin": "1HGCM82633A123456",
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "selling_price": 850000000
        }

        car = Car.from_dict(data)
        self.assertIsNotNone(car)
        self.assertEqual(car.id, 1)
        self.assertEqual(car.vin, "1HGCM82633A123456")
        self.assertEqual(car.brand, "Honda")

    def test_from_dict_empty(self):
        """Test from_dict with empty data."""
        car = Car.from_dict(None)
        self.assertIsNone(car)

        car = Car.from_dict({})
        self.assertIsNone(car)

    def test_get_display_name(self):
        """Test getting display name."""
        car = Car(year=2023, brand="Toyota", model="Camry")
        self.assertEqual(car.get_display_name(), "2023 Toyota Camry")

        car = Car(brand="Honda", model="Civic")
        self.assertEqual(car.get_display_name(), "Honda Civic")

        car = Car()
        self.assertEqual(car.get_display_name(), "Xe chưa đặt tên")

    def test_get_price_display(self):
        """Test price display formatting."""
        car = Car(selling_price=850000000)
        self.assertEqual(car.get_price_display(), "850.000.000 VNĐ")

        car = Car()
        self.assertEqual(car.get_price_display(), "Chưa có giá")

    def test_get_short_vin(self):
        """Test VIN shortening."""
        car = Car(vin="1HGCM82633A123456")
        self.assertEqual(car.get_short_vin(), "1HGCM826...3456")

        car = Car(vin="SHORT")
        self.assertEqual(car.get_short_vin(), "SHORT")

    def test_is_available(self):
        """Test availability check."""
        car = Car(status="available", is_deleted=False)
        self.assertTrue(car.is_available())

        car = Car(status="sold", is_deleted=False)
        self.assertFalse(car.is_available())

        car = Car(status="available", is_deleted=True)
        self.assertFalse(car.is_available())

    def test_calculate_profit(self):
        """Test profit calculation."""
        car = Car(purchase_price=750000000, selling_price=850000000)
        self.assertEqual(car.calculate_profit(), 100000000)

        car = Car()
        self.assertIsNone(car.calculate_profit())

    def test_get_profit_margin(self):
        """Test profit margin calculation."""
        car = Car(purchase_price=750000000, selling_price=850000000)
        self.assertAlmostEqual(car.get_profit_margin(), 13.33, places=1)

        car = Car(purchase_price=0, selling_price=850000000)
        self.assertIsNone(car.get_profit_margin())


if __name__ == "__main__":
    unittest.main()
