"""
Unit tests for CustomerHistoryService.
"""

import unittest
import tempfile
import shutil
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.repositories.customer_history_repository import CustomerHistoryRepository
from src.services.customer_history_service import CustomerHistoryService


class TestCustomerHistoryService(unittest.TestCase):
    """Tests for customer history service."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)

        self.customer_repo = CustomerRepository(self.db)
        self.history_repo = CustomerHistoryRepository(self.db)
        self.service = CustomerHistoryService(self.history_repo, self.customer_repo)

        self.user_id = 1

        # Clear existing data
        self.db.execute("DELETE FROM customer_history")
        self.db.execute("DELETE FROM customers")

        # Create test customer
        self.customer_id = self.customer_repo.create({
            'full_name': 'Test Customer',
            'phone': '0901234567',
            'customer_type': 'individual'
        })

        # Add some history
        self.history_repo.record_create(self.customer_id, self.user_id)
        self.history_repo.record_update(self.customer_id, 'phone',
                                       '0900000000', '0901234567', self.user_id)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_get_full_history(self):
        """Test getting full customer history."""
        history = self.service.get_full_history(self.customer_id)

        self.assertIsNotNone(history)
        self.assertIn('profile_changes', history)
        self.assertIn('timeline', history)
        self.assertIn('summary', history)
        self.assertIn('customer', history)

        # Check profile changes
        self.assertEqual(len(history['profile_changes']), 2)

    def test_build_timeline(self):
        """Test timeline building."""
        profile_changes = self.history_repo.get_history(self.customer_id)
        timeline = self.service._build_timeline(profile_changes, [])

        self.assertEqual(len(timeline), 2)
        self.assertEqual(timeline[0]['type'], 'profile')
        self.assertIn('description', timeline[0])
        self.assertIn('icon', timeline[0])

    def test_format_profile_change(self):
        """Test profile change formatting."""
        # Test create
        change = {'action': 'create'}
        result = self.service._format_profile_change(change)
        self.assertEqual(result, 'Tạo mới khách hàng')

        # Test update
        change = {
            'action': 'update',
            'field_name': 'phone',
            'old_value': '0900000000',
            'new_value': '0901234567'
        }
        result = self.service._format_profile_change(change)
        self.assertIn('Cập nhật', result)
        self.assertIn('Số điện thoại', result)

        # Test delete
        change = {'action': 'delete', 'old_value': 'Test reason'}
        result = self.service._format_profile_change(change)
        self.assertIn('Xóa khách hàng', result)

        # Test restore
        change = {'action': 'restore'}
        result = self.service._format_profile_change(change)
        self.assertEqual(result, 'Khôi phục khách hàng')

    def test_get_action_icon(self):
        """Test action icon mapping."""
        self.assertEqual(self.service._get_action_icon('create'), '👤')
        self.assertEqual(self.service._get_action_icon('update'), '✏️')
        self.assertEqual(self.service._get_action_icon('delete'), '🗑️')
        self.assertEqual(self.service._get_action_icon('restore'), '↩️')
        self.assertEqual(self.service._get_action_icon('unknown'), '📝')

    def test_transaction_summary(self):
        """Test transaction summary."""
        summary = self.service._get_transaction_summary(self.customer_id, [])

        self.assertEqual(summary['total_contracts'], 0)
        self.assertEqual(summary['total_value'], 0)
        self.assertEqual(summary['average_value'], 0)
        self.assertEqual(summary['status_breakdown'], {})

    def test_transaction_summary_with_contracts(self):
        """Test transaction summary with contracts."""
        contracts = [
            {'total_amount': 1000000000, 'status': 'signed', 'created_at': datetime.now()},
            {'total_amount': 500000000, 'status': 'paid', 'created_at': datetime.now()}
        ]
        summary = self.service._get_transaction_summary(self.customer_id, contracts)

        self.assertEqual(summary['total_contracts'], 2)
        self.assertEqual(summary['total_value'], 1500000000)
        self.assertEqual(summary['average_value'], 750000000)
        self.assertEqual(summary['status_breakdown']['signed'], 1)
        self.assertEqual(summary['status_breakdown']['paid'], 1)

    def test_customer_statistics(self):
        """Test customer statistics calculation."""
        stats = self.service.get_customer_statistics(self.customer_id)

        self.assertIsNotNone(stats)
        self.assertIn('total_contracts', stats)
        self.assertIn('total_value', stats)
        self.assertIn('vip_score', stats)
        self.assertIn('tier', stats)

        # No contracts = Potential tier
        self.assertEqual(stats['tier'], 'Potential')

    def test_customer_statistics_vip(self):
        """Test VIP customer statistics."""
        # Manually set summary for VIP test
        import unittest.mock
        with unittest.mock.patch.object(self.service, 'get_full_history') as mock_get:
            mock_get.return_value = {
                'summary': {
                    'total_value': 2500000000,  # 2.5 tỷ
                    'total_contracts': 5
                }
            }
            stats = self.service.get_customer_statistics(self.customer_id)
            self.assertEqual(stats['tier'], 'VIP')

    def test_export_history_json(self):
        """Test exporting history to JSON."""
        os.makedirs('exports', exist_ok=True)

        filepath = self.service.export_history(self.customer_id, 'json')

        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.endswith('.json'))
        self.assertTrue(os.path.exists(filepath))

        # Verify JSON content
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('profile_changes', data)
            self.assertIn('timeline', data)
            self.assertIn('summary', data)

        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)

    def test_export_history_csv(self):
        """Test exporting history to CSV."""
        os.makedirs('exports', exist_ok=True)

        filepath = self.service.export_history(self.customer_id, 'csv')

        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.endswith('.csv'))
        self.assertTrue(os.path.exists(filepath))

        # Verify CSV content
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            self.assertIn('Thời gian', content)
            self.assertIn('Loại', content)

        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)

    def test_nonexistent_customer(self):
        """Test handling nonexistent customer."""
        history = self.service.get_full_history(99999)
        self.assertIsNone(history)

        stats = self.service.get_customer_statistics(99999)
        self.assertIsNone(stats)

    def test_export_nonexistent_customer(self):
        """Test exporting nonexistent customer history."""
        filepath = self.service.export_history(99999, 'json')
        self.assertIsNone(filepath)


if __name__ == '__main__':
    unittest.main()
