"""
Unit tests for KPI Service and Repository.
Sprint 0.4: Employee KPI
"""

import unittest
import os
import tempfile
import shutil
from datetime import date, datetime
from decimal import Decimal

from src.database.db_helper import DatabaseHelper
from src.repositories.user_repository import UserRepository, RoleRepository
from src.repositories.kpi_repository import KPIRepository, KPITargetRepository
from src.services.kpi_service import KPIService, InvalidPeriodError
from src.models.kpi import KPIRecord, KPITarget, PerformanceSummary


class TestKPIRepository(unittest.TestCase):
    """Test cases for KPIRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.kpi_repo = KPIRepository(self.db)

        # Create tables using schema.sql
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        # Create a test user
        self.user_repo = UserRepository(self.db)
        self.user_id = self.user_repo.create({
            "username": "testuser",
            "password_hash": "hash",
            "full_name": "Test User",
            "role_id": 3
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_and_get_kpi(self):
        """Test creating and retrieving KPI record."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'period_value': '2024-01',
            'cars_sold': 10,
            'revenue_generated': 1000000,
            'new_customers': 5,
            'contracts_signed': 10,
            'target_cars': 8,
            'target_revenue': 800000,
            'cars_achievement_rate': 125.0,
            'revenue_achievement_rate': 125.0,
            'overall_score': 125.0
        }

        kpi_id = self.kpi_repo.create(data)
        self.assertGreater(kpi_id, 0)

        # Get by ID
        kpi = self.kpi_repo.get_by_id(kpi_id)
        self.assertIsNotNone(kpi)
        self.assertEqual(kpi.cars_sold, 10)

    def test_get_by_user_and_period(self):
        """Test getting KPI by user and period."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'period_value': '2024-02',
            'cars_sold': 5,
            'revenue_generated': 500000
        }
        self.kpi_repo.create(data)

        result = self.kpi_repo.get_by_user_and_period(
            self.user_id, 'monthly', '2024-02'
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['cars_sold'], 5)

    def test_update_rank(self):
        """Test updating KPI rank."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'period_value': '2024-03',
            'cars_sold': 8
        }
        kpi_id = self.kpi_repo.create(data)
        self.assertGreater(kpi_id, 0)

        # Verify created
        kpi_before = self.kpi_repo.get_by_id(kpi_id)
        self.assertIsNotNone(kpi_before)

        result = self.kpi_repo.update_rank(kpi_id, 2, 10)
        self.assertTrue(result)

        kpi = self.kpi_repo.get_by_id(kpi_id)
        self.assertEqual(kpi.period_rank, 2)
        self.assertEqual(kpi.total_staff, 10)

    def test_get_top_performers(self):
        """Test getting top performers."""
        # Create multiple KPI records
        for i in range(5):
            self.user_repo.create({
                "username": f"user{i}",
                "password_hash": "hash",
                "full_name": f"User {i}",
                "role_id": 3
            })

            data = {
                'user_id': self.user_id + i,
                'period_type': 'monthly',
                'period_value': '2024-04',
                'cars_sold': i + 1,
                'revenue_generated': (i + 1) * 100000,
                'overall_score': (i + 1) * 10
            }
            self.kpi_repo.create(data)

        performers = self.kpi_repo.get_top_performers('monthly', '2024-04', 3)
        self.assertLessEqual(len(performers), 3)

    def test_get_team_average(self):
        """Test getting team average."""
        # Create KPI records
        for i in range(3):
            self.user_repo.create({
                "username": f"avguser{i}",
                "password_hash": "hash",
                "full_name": f"Avg User {i}",
                "role_id": 3
            })

            data = {
                'user_id': self.user_id + i,
                'period_type': 'monthly',
                'period_value': '2024-05',
                'cars_sold': 10,
                'revenue_generated': 1000000,
                'overall_score': 100.0
            }
            self.kpi_repo.create(data)

        avg = self.kpi_repo.get_team_average('monthly', '2024-05')
        self.assertIn('avg_cars', avg)
        self.assertIn('avg_revenue', avg)
        self.assertIn('avg_score', avg)


class TestKPITargetRepository(unittest.TestCase):
    """Test cases for KPITargetRepository."""

    def setUp(self):
        """Set up test database and repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.target_repo = KPITargetRepository(self.db)

        # Create tables
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.user_repo = UserRepository(self.db)
        self.user_id = self.user_repo.create({
            "username": "targetuser",
            "password_hash": "hash",
            "full_name": "Target User",
            "role_id": 3
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_create_and_get_target(self):
        """Test creating and retrieving target."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'target_period': '2024-01',
            'sales_target': 10,
            'revenue_target': Decimal('1000000'),
            'new_customer_target': 5
        }

        target_id = self.target_repo.create(data)
        self.assertGreater(target_id, 0)

        target = self.target_repo.get_by_id(target_id)
        self.assertIsNotNone(target)
        self.assertEqual(target.sales_target, 10)

    def test_get_by_user_and_period(self):
        """Test getting target by user and period."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'target_period': '2024-02',
            'sales_target': 8
        }
        self.target_repo.create(data)

        result = self.target_repo.get_by_user_and_period(
            self.user_id, 'monthly', '2024-02'
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['sales_target'], 8)

    def test_update_target(self):
        """Test updating target."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'target_period': '2024-03',
            'sales_target': 5
        }
        target_id = self.target_repo.create(data)

        update_data = {'sales_target': 15}
        result = self.target_repo.update(target_id, update_data)
        self.assertTrue(result)

        target = self.target_repo.get_by_id(target_id)
        self.assertEqual(target.sales_target, 15)

    def test_set_bulk_targets(self):
        """Test setting bulk targets."""
        # Create multiple users
        user_ids = []
        for i in range(3):
            uid = self.user_repo.create({
                "username": f"bulk{i}",
                "password_hash": "hash",
                "full_name": f"Bulk User {i}",
                "role_id": 3
            })
            user_ids.append(uid)

        data = {
            'period_type': 'monthly',
            'target_period': '2024-06',
            'sales_target': 10,
            'revenue_target': Decimal('1000000'),
            'new_customer_target': 5
        }

        count = self.target_repo.set_bulk_targets(user_ids, data)
        self.assertEqual(count, 3)


class TestKPIService(unittest.TestCase):
    """Test cases for KPIService."""

    def setUp(self):
        """Set up test database and service."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        # Create tables
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.user_repo = UserRepository(self.db)
        self.kpi_repo = KPIRepository(self.db)
        self.target_repo = KPITargetRepository(self.db)

        self.kpi_service = KPIService(
            self.kpi_repo,
            self.target_repo,
            self.user_repo
        )

        # Create test users
        self.user1 = self.user_repo.create({
            "username": "user1",
            "password_hash": "hash",
            "full_name": "User One",
            "role_id": 3
        })

        self.user2 = self.user_repo.create({
            "username": "user2",
            "password_hash": "hash",
            "full_name": "User Two",
            "role_id": 3
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_calculate_achievement_rate(self):
        """Test achievement rate calculation."""
        # Normal case
        rate = self.kpi_service.calculate_achievement_rate(10, 8)
        self.assertEqual(rate, 125.0)

        # Target is 0, actual > 0
        rate = self.kpi_service.calculate_achievement_rate(10, 0)
        self.assertEqual(rate, 100.0)

        # Target is 0, actual is 0
        rate = self.kpi_service.calculate_achievement_rate(0, 0)
        self.assertEqual(rate, 0.0)

        # Capped at 999.99%
        rate = self.kpi_service.calculate_achievement_rate(1000, 1)
        self.assertEqual(rate, 999.99)

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        score = self.kpi_service.calculate_overall_score(100.0, 100.0)
        self.assertEqual(score, 100.0)

        # Weighted calculation
        score = self.kpi_service.calculate_overall_score(100.0, 120.0)
        # 100 * 0.4 + 120 * 0.6 = 112
        self.assertEqual(score, 112.0)

    def test_get_performance_rating(self):
        """Test performance rating."""
        self.assertEqual(self.kpi_service.get_performance_rating(150), "Xuất sắc")
        self.assertEqual(self.kpi_service.get_performance_rating(120), "Xuất sắc")
        self.assertEqual(self.kpi_service.get_performance_rating(100), "Tốt")
        self.assertEqual(self.kpi_service.get_performance_rating(80), "Đạt")
        self.assertEqual(self.kpi_service.get_performance_rating(60), "Cần cải thiện")
        self.assertEqual(self.kpi_service.get_performance_rating(50), "Kém")

    def test_calculate_monthly_kpi(self):
        """Test monthly KPI calculation."""
        # Set target first
        self.kpi_service.set_kpi_target(
            self.user1,
            'monthly',
            '2024-01',
            sales_target=10,
            revenue_target=Decimal('1000000')
        )

        # Calculate KPI
        kpi = self.kpi_service.calculate_monthly_kpi(
            self.user1,
            2024,
            1,
            cars_sold=12,
            revenue_generated=Decimal('1200000'),
            new_customers=5,
            contracts_signed=12
        )

        self.assertIsInstance(kpi, KPIRecord)
        self.assertEqual(kpi.cars_sold, 12)
        self.assertEqual(kpi.revenue_generated, Decimal('1200000'))
        self.assertEqual(kpi.cars_achievement_rate, 120.0)
        self.assertEqual(kpi.revenue_achievement_rate, 120.0)
        self.assertEqual(kpi.overall_score, 120.0)

    def test_get_performance_ranking(self):
        """Test performance ranking."""
        # Create KPI records for multiple users
        for i, user_id in enumerate([self.user1, self.user2], 1):
            data = {
                'user_id': user_id,
                'period_type': 'monthly',
                'period_value': '2024-03',
                'cars_sold': i * 10,
                'revenue_generated': i * 1000000,
                'target_cars': 10,
                'target_revenue': 1000000,
                'cars_achievement_rate': i * 100,
                'revenue_achievement_rate': i * 100,
                'overall_score': i * 100
            }
            self.kpi_repo.create(data)

        # Recalculate rankings
        self.kpi_service._recalculate_rankings('monthly', '2024-03')

        ranking = self.kpi_service.get_performance_ranking('monthly', '2024-03')
        self.assertEqual(len(ranking), 2)

        # Should be sorted by score descending
        self.assertEqual(ranking[0].rank, 1)
        self.assertEqual(ranking[1].rank, 2)

    def test_compare_with_peers(self):
        """Test peer comparison."""
        # Create KPI records
        for user_id in [self.user1, self.user2]:
            data = {
                'user_id': user_id,
                'period_type': 'monthly',
                'period_value': '2024-04',
                'cars_sold': 10,
                'revenue_generated': 1000000,
                'overall_score': 100.0,
                'period_rank': 1 if user_id == self.user1 else 2
            }
            self.kpi_repo.create(data)

        comparison = self.kpi_service.compare_with_peers(
            self.user1, 'monthly', '2024-04'
        )

        self.assertIsNotNone(comparison)
        self.assertIn('user', comparison)
        self.assertIn('team_average', comparison)
        self.assertIn('comparison', comparison)

    def test_generate_kpi_report(self):
        """Test KPI report generation."""
        # Create KPI records for multiple months
        for month in range(1, 4):
            data = {
                'user_id': self.user1,
                'period_type': 'monthly',
                'period_value': f'2024-{month:02d}',
                'cars_sold': month * 5,
                'revenue_generated': month * 500000,
                'overall_score': month * 25
            }
            result = self.kpi_repo.create(data)
            # Debug
            print(f"Created KPI for month {month}: id={result}, cars_sold={month*5}")

        # Verify records exist
        all_kpis = self.kpi_repo.get_by_user(self.user1, 'monthly')
        print(f"Total KPI records: {len(all_kpis)}")
        for kpi in all_kpis:
            print(f"  Period: {kpi['period_value']}, Cars: {kpi['cars_sold']}")

        report = self.kpi_service.generate_kpi_report(
            self.user1,
            date(2024, 1, 1),
            date(2024, 3, 31)
        )

        self.assertIsNotNone(report)
        self.assertIn('summary', report)
        self.assertIn('best_performance', report)
        self.assertIn('worst_performance', report)
        self.assertIn('monthly_data', report)

        # Sum should be 5+10+15=30
        total = report['summary']['total_cars_sold']
        self.assertEqual(total, 30, f"Expected 30 but got {total}. Monthly data: {[r['period_value'] + ':' + str(r['cars_sold']) for r in report['monthly_data']]}")

    def test_get_kpi_trend(self):
        """Test KPI trend retrieval."""
        for month in range(1, 4):
            data = {
                'user_id': self.user1,
                'period_type': 'monthly',
                'period_value': f'2024-{month:02d}',
                'cars_sold': month * 5,
                'revenue_generated': month * 500000
            }
            self.kpi_repo.create(data)

        trend = self.kpi_service.get_kpi_trend(self.user1, months=6)
        self.assertEqual(len(trend), 3)

    def test_set_kpi_target(self):
        """Test setting KPI target."""
        target_id = self.kpi_service.set_kpi_target(
            self.user1,
            'monthly',
            '2024-05',
            sales_target=15,
            revenue_target=Decimal('1500000'),
            new_customer_target=8,
            description='Test target'
        )

        self.assertGreater(target_id, 0)

        target = self.target_repo.get_by_id(target_id)
        self.assertEqual(target.sales_target, 15)
        self.assertEqual(target.revenue_target, Decimal('1500000'))

    def test_get_current_period(self):
        """Test getting current period."""
        period = self.kpi_service.get_current_period('monthly')
        self.assertRegex(period, r'^\d{4}-\d{2}$')

        period = self.kpi_service.get_current_period('yearly')
        self.assertRegex(period, r'^\d{4}$')

    def test_get_previous_period(self):
        """Test getting previous period."""
        # Monthly
        prev = self.kpi_service._get_previous_period('monthly', '2024-03')
        self.assertEqual(prev, '2024-02')

        prev = self.kpi_service._get_previous_period('monthly', '2024-01')
        self.assertEqual(prev, '2023-12')

        # Quarterly
        prev = self.kpi_service._get_previous_period('quarterly', '2024-Q2')
        self.assertEqual(prev, '2024-Q1')

        prev = self.kpi_service._get_previous_period('quarterly', '2024-Q1')
        self.assertEqual(prev, '2023-Q4')

        # Yearly
        prev = self.kpi_service._get_previous_period('yearly', '2024')
        self.assertEqual(prev, '2023')


class TestKPIEdgeCases(unittest.TestCase):
    """Test edge cases for KPI calculations."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                with self.db.get_connection() as conn:
                    conn.executescript(f.read())

        self.user_repo = UserRepository(self.db)
        self.kpi_repo = KPIRepository(self.db)
        self.target_repo = KPITargetRepository(self.db)

        self.kpi_service = KPIService(
            self.kpi_repo,
            self.target_repo,
            self.user_repo
        )

        self.user_id = self.user_repo.create({
            "username": "edgeuser",
            "password_hash": "hash",
            "full_name": "Edge User",
            "role_id": 3
        })

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)

    def test_zero_target(self):
        """Test with zero target."""
        # No target set, should handle gracefully
        kpi = self.kpi_service.calculate_monthly_kpi(
            self.user_id,
            2024,
            1,
            cars_sold=5,
            revenue_generated=Decimal('500000')
        )

        # When target is 0 and actual > 0, achievement is 100% (per logic)
        self.assertEqual(kpi.cars_achievement_rate, 100.0)
        self.assertEqual(kpi.revenue_achievement_rate, 100.0)

    def test_no_data(self):
        """Test with no data."""
        report = self.kpi_service.generate_kpi_report(
            self.user_id,
            date(2024, 1, 1),
            date(2024, 1, 31)
        )
        self.assertIsNone(report)

        comparison = self.kpi_service.compare_with_peers(
            self.user_id, 'monthly', '2024-01'
        )
        self.assertIsNone(comparison)

    def test_empty_ranking(self):
        """Test ranking with no data."""
        ranking = self.kpi_service.get_performance_ranking('monthly', '2024-01')
        self.assertEqual(len(ranking), 0)

    def test_large_numbers(self):
        """Test with very large numbers."""
        data = {
            'user_id': self.user_id,
            'period_type': 'monthly',
            'period_value': '2024-01',
            'cars_sold': 999999,
            'revenue_generated': 999999999999.99
        }
        kpi_id = self.kpi_repo.create(data)
        kpi = self.kpi_repo.get_by_id(kpi_id)

        self.assertEqual(kpi.cars_sold, 999999)

    def test_update_existing_kpi(self):
        """Test updating existing KPI record."""
        # Create initial KPI
        kpi = self.kpi_service.calculate_monthly_kpi(
            self.user_id,
            2024,
            1,
            cars_sold=5,
            revenue_generated=Decimal('500000')
        )

        # Update with new data
        kpi2 = self.kpi_service.calculate_monthly_kpi(
            self.user_id,
            2024,
            1,
            cars_sold=10,
            revenue_generated=Decimal('1000000')
        )

        self.assertEqual(kpi.id, kpi2.id)  # Same record
        self.assertEqual(kpi2.cars_sold, 10)


if __name__ == "__main__":
    unittest.main()
