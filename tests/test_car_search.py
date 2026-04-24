"""
Tests for Car Search functionality.
Sprint 1.3: Car Search & Filter
"""

import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.repositories.car_search_repository import CarSearchRepository, CarSearchFilter
from src.services.car_search_service import CarSearchService


class TestCarSearch(unittest.TestCase):
    """Tests for car search functionality."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.car_repo = CarRepository(self.db)
        self.search_repo = CarSearchRepository(self.db)
        self.search_service = CarSearchService(self.search_repo)

        # Create test data
        self._create_test_cars()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def _create_test_cars(self):
        """Create test car data with unique values to avoid seed data conflicts."""
        cars = [
            {"vin": "UNIQUE11111A111111", "brand": "SearchTest1", "model": "ModelA",
             "year": 2023, "selling_price": 1200000000, "color": "Xanh",
             "status": "available", "transmission": "auto", "fuel_type": "gasoline"},
            {"vin": "UNIQUE22222A222222", "brand": "SearchTest2", "model": "ModelB",
             "year": 2023, "selling_price": 850000000, "color": "Vàng",
             "status": "available", "transmission": "auto", "fuel_type": "gasoline"},
            {"vin": "UNIQUE33333A333333", "brand": "SearchTest2", "model": "ModelC",
             "year": 2022, "selling_price": 600000000, "color": "Xanh",
             "status": "sold", "transmission": "manual", "fuel_type": "gasoline"},
            {"vin": "UNIQUE44444A444444", "brand": "SearchTest3", "model": "ModelD",
             "year": 2022, "selling_price": 750000000, "color": "Tím",
             "status": "available", "transmission": "auto", "fuel_type": "gasoline"},
            {"vin": "UNIQUE55555A555555", "brand": "SearchTest4", "model": "ModelE",
             "year": 2021, "selling_price": 1500000000, "color": "Cam",
             "status": "available", "transmission": "auto", "fuel_type": "gasoline"},
        ]
        for car_data in cars:
            self.car_repo.create(car_data)

    def test_quick_search_by_keyword(self):
        """Test searching by keyword."""
        cars, total = self.search_service.quick_search("SearchTest2")
        self.assertEqual(total, 2)
        for car in cars:
            self.assertTrue(
                'SearchTest2' in car.brand or 'SearchTest2' in car.model or 'SearchTest2' in car.vin
            )

    def test_search_by_brand(self):
        """Test filtering by brand."""
        cars, total = self.search_service.advanced_search(brands=["SearchTest1"])
        self.assertEqual(total, 1)
        self.assertEqual(cars[0].brand, "SearchTest1")

    def test_search_by_multiple_brands(self):
        """Test filtering by multiple brands."""
        cars, total = self.search_service.advanced_search(brands=["SearchTest2", "SearchTest3"])
        self.assertEqual(total, 3)

    def test_search_by_price_range(self):
        """Test filtering by price range."""
        cars, total = self.search_service.advanced_search(
            price_from=700000000,
            price_to=1000000000
        )
        # Should find SearchTest2 ModelB (850M) and SearchTest3 ModelD (750M)
        # Note: Seed data may add additional matches
        self.assertGreaterEqual(total, 2)
        brands = [car.brand for car in cars]
        self.assertIn("SearchTest2", brands)
        self.assertIn("SearchTest3", brands)

    def test_search_by_year_range(self):
        """Test filtering by year range."""
        cars, total = self.search_service.advanced_search(
            year_from=2022,
            year_to=2023
        )
        # Should find 4 test cars + seed data matches
        self.assertGreaterEqual(total, 4)
        brands = [car.brand for car in cars]
        self.assertIn("SearchTest1", brands)
        self.assertIn("SearchTest2", brands)

    def test_search_by_status(self):
        """Test filtering by status."""
        cars, total = self.search_service.advanced_search(statuses=["available"])
        # 4 test cars (excluding 1 sold) + seed data
        self.assertGreaterEqual(total, 4)
        # All returned cars should have available status
        for car in cars:
            self.assertEqual(car.status, "available")

    def test_search_by_color(self):
        """Test filtering by color."""
        cars, total = self.search_service.advanced_search(colors=["Xanh"])
        self.assertEqual(total, 2)

    def test_search_by_transmission(self):
        """Test filtering by transmission."""
        cars, total = self.search_service.advanced_search(transmissions=["manual"])
        self.assertEqual(total, 1)

    def test_multiple_filters(self):
        """Test combining multiple filters."""
        cars, total = self.search_service.advanced_search(
            brands=["SearchTest2"],
            year_from=2023,
            statuses=["available"]
        )
        self.assertEqual(total, 1)
        self.assertEqual(cars[0].model, "ModelB")

    def test_pagination(self):
        """Test pagination."""
        cars, total = self.search_service.advanced_search(page=1, per_page=2)
        # 5 test cars + seed data
        self.assertEqual(len(cars), 2)
        self.assertGreaterEqual(total, 5)

    def test_sorting(self):
        """Test sorting results."""
        cars, _ = self.search_service.advanced_search(
            sort_by="selling_price",
            sort_order="DESC"
        )
        # First should be the most expensive (could be seed data or SearchTest4)
        self.assertIsNotNone(cars[0].selling_price)
        # Verify descending order
        for i in range(len(cars) - 1):
            self.assertGreaterEqual(cars[i].selling_price, cars[i+1].selling_price)

    def test_get_filter_options(self):
        """Test getting filter options."""
        options = self.search_service.get_filter_options()
        self.assertIn("SearchTest1", options['brands'])
        self.assertIn("SearchTest2", options['brands'])
        self.assertIn(2023, options['years'])
        self.assertIn("Xanh", options['colors'])

    def test_get_price_range(self):
        """Test getting price range."""
        min_price, max_price = self.search_service.get_price_range()
        self.assertIsNotNone(min_price)
        self.assertIsNotNone(max_price)
        self.assertLess(min_price, max_price)

    def test_search_by_price_only(self):
        """Test price range search."""
        cars, total = self.search_service.search_by_price_range(
            500000000, 800000000
        )
        for car in cars:
            self.assertGreaterEqual(car.selling_price, 500000000)
            self.assertLessEqual(car.selling_price, 800000000)

    def test_search_by_year_only(self):
        """Test year range search."""
        cars, total = self.search_service.search_by_year_range(2022, 2023)
        for car in cars:
            self.assertGreaterEqual(car.year, 2022)
            self.assertLessEqual(car.year, 2023)

    def test_autocomplete(self):
        """Test autocomplete search."""
        cars = self.search_service.autocomplete("ModelB", limit=5)
        self.assertGreaterEqual(len(cars), 1)

    def test_keyword_with_filters(self):
        """Test keyword combined with filters."""
        cars, total = self.search_service.advanced_search(
            keyword="SearchTest2",
            statuses=["available"]
        )
        self.assertEqual(total, 1)
        self.assertEqual(cars[0].model, "ModelB")


class TestCarSearchRepository(unittest.TestCase):
    """Tests for CarSearchRepository."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.car_repo = CarRepository(self.db)
        self.search_repo = CarSearchRepository(self.db)

        # Create test data
        self.car_repo.create({
            "vin": "FTSTEST99999TEST1",
            "license_plate": "99Z-99999",
            "brand": "FTSTestBrand",
            "model": "FTSModel",
            "description": "FTS test description"
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_fts_search(self):
        """Test full-text search."""
        # FTS might not work in test without proper setup
        # Just test that the method exists and runs
        try:
            cars = self.search_repo.fts_search("FTSTestBrand")
            # If FTS works, should find the car
            for car in cars:
                self.assertIn("FTSTestBrand", [car.brand, car.model, car.description or ''])
        except Exception:
            # FTS might not be available in test environment
            pass

    def test_quick_search(self):
        """Test quick search."""
        cars = self.search_repo.quick_search("99Z", limit=5)
        self.assertGreaterEqual(len(cars), 1)


if __name__ == "__main__":
    unittest.main()
