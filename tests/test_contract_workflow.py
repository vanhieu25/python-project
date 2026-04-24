"""
Unit tests for ContractWorkflowService.
Tests state transitions, permissions, and validations.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import sqlite3
import tempfile
from datetime import datetime

from database.db_helper import DatabaseHelper
from repositories.contract_repository import ContractRepository
from services.contract_workflow_service import (
    ContractWorkflowService, WorkflowResult, ContractStatus
)


class MockUser:
    """Mock user for testing."""
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


class MockUserRepository:
    """Mock user repository for testing."""
    def __init__(self):
        self.users = {
            1: MockUser(1, 'sales_user', 'sales'),
            2: MockUser(2, 'manager_user', 'manager'),
            3: MockUser(3, 'admin_user', 'admin'),
            4: MockUser(4, 'accountant_user', 'accountant')
        }

    def get_by_id(self, user_id):
        return self.users.get(user_id)


class TestContractWorkflowService(unittest.TestCase):
    """Test cases for ContractWorkflowService."""

    def setUp(self):
        """Set up test database and service."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        self.db = DatabaseHelper(self.db_path)
        self._init_schema()

        self.contract_repo = ContractRepository(self.db)
        self.user_repo = MockUserRepository()

        self.workflow_service = ContractWorkflowService(
            self.contract_repo,
            user_repo=self.user_repo
        )

        self._insert_test_data()

    def tearDown(self):
        """Clean up test database."""
        import time
        time.sleep(0.1)
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except PermissionError:
            pass

    def _init_schema(self):
        """Initialize database schema."""
        schema_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()

    def _insert_test_data(self):
        """Insert test data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (id, username, full_name, password_hash, role)
            VALUES (1, 'sales', 'Sales User', 'hash', 'sales'),
                   (2, 'manager', 'Manager User', 'hash', 'manager'),
                   (3, 'admin', 'Admin User', 'hash', 'admin')
        """)

        # Create test contracts
        contracts = [
            ('HD001', 'draft', 1),      # Draft contract
            ('HD002', 'pending', 1),    # Pending approval
            ('HD003', 'approved', 2),   # Approved, waiting for signature
            ('HD004', 'signed', 2),     # Signed, waiting for payment
            ('HD005', 'paid', 2),       # Paid, waiting for delivery
            ('HD006', 'delivered', 2),  # Completed
            ('HD007', 'cancelled', 1),  # Cancelled
        ]

        for code, status, created_by in contracts:
            cursor.execute("""
                INSERT INTO contracts (
                    contract_code, customer_id, customer_name, car_id,
                    car_brand, car_model, car_price, total_amount,
                    final_amount, created_by, status, paid_amount
                )
                VALUES (?, 1, 'Test Customer', 1, 'Toyota', 'Camry', 1000000000,
                        1000000000, 1100000000, ?, ?, 0)
            """, (code, created_by, status))

        # Create contract with full payment
        cursor.execute("""
            INSERT INTO contracts (
                contract_code, customer_id, customer_name, car_id,
                car_brand, car_model, car_price, total_amount,
                final_amount, created_by, status, paid_amount
            )
            VALUES ('HD008', 1, 'Test Customer', 1, 'Toyota', 'Camry', 1000000000,
                    1000000000, 1100000000, 2, 'signed', 1100000000)
        """)

        # Create signed contract with full payment
        cursor.execute("""
            INSERT INTO contracts (
                contract_code, customer_id, customer_name, car_id,
                car_brand, car_model, car_price, total_amount,
                final_amount, created_by, status, paid_amount
            )
            VALUES ('HD010', 1, 'Test Customer', 1, 'Toyota', 'Camry', 1000000000,
                    1000000000, 1100000000, 2, 'paid', 1100000000)
        """)

        conn.commit()
        conn.close()

    def test_can_transition_valid(self):
        """Test valid state transitions."""
        self.assertTrue(
            self.workflow_service.can_transition('draft', 'pending', 'sales')
        )
        self.assertTrue(
            self.workflow_service.can_transition('pending', 'approved', 'manager')
        )
        self.assertTrue(
            self.workflow_service.can_transition('approved', 'signed', 'sales')
        )

    def test_can_transition_invalid(self):
        """Test invalid state transitions."""
        self.assertFalse(
            self.workflow_service.can_transition('draft', 'approved', 'sales')
        )
        self.assertFalse(
            self.workflow_service.can_transition('delivered', 'cancelled', 'admin')
        )

    def test_can_transition_no_permission(self):
        """Test transition without permission."""
        # Sales cannot approve
        self.assertFalse(
            self.workflow_service.can_transition('pending', 'approved', 'sales')
        )
        # Non-manager cannot reject
        self.assertFalse(
            self.workflow_service.can_transition('pending', 'draft', 'sales')
        )

    def test_submit_for_approval_success(self):
        """Test submitting draft contract for approval."""
        contract = self.contract_repo.get_by_code('HD001')

        result = self.workflow_service.submit_for_approval(
            contract.id, user_id=1, notes="Please approve"
        )

        self.assertTrue(result.success)
        self.assertIn("đã được gửi", result.message)

        # Verify status changed
        updated = self.contract_repo.get_by_code('HD001')
        self.assertEqual(updated.status, 'pending')

    def test_submit_for_approval_not_draft(self):
        """Test submitting non-draft contract."""
        contract = self.contract_repo.get_by_code('HD002')  # Already pending

        result = self.workflow_service.submit_for_approval(
            contract.id, user_id=1, notes="Please approve"
        )

        self.assertFalse(result.success)
        self.assertIn("pending", result.message)

    def test_approve_success(self):
        """Test approving pending contract."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        result = self.workflow_service.approve(
            contract.id, approver_id=2, notes="Approved"
        )

        self.assertTrue(result.success)

        # Verify status changed
        updated = self.contract_repo.get_by_code('HD002')
        self.assertEqual(updated.status, 'approved')

    def test_approve_no_permission(self):
        """Test approve without permission."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        # Sales user cannot approve
        result = self.workflow_service.approve(
            contract.id, approver_id=1, notes="Approved"
        )

        self.assertFalse(result.success)
        # Should indicate transition not allowed due to role
        self.assertTrue(
            "sales" in result.message.lower() or "quyền" in result.message.lower()
        )

    def test_reject_success(self):
        """Test rejecting pending contract."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        result = self.workflow_service.reject(
            contract.id, approver_id=2, reason="Price too high"
        )

        self.assertTrue(result.success)

        # Verify status changed back to draft
        updated = self.contract_repo.get_by_code('HD002')
        self.assertEqual(updated.status, 'draft')

    def test_reject_without_reason(self):
        """Test reject without reason."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        result = self.workflow_service.reject(
            contract.id, approver_id=2, reason=""
        )

        self.assertFalse(result.success)
        self.assertIn("lý do", result.message.lower())

    def test_mark_signed_complete(self):
        """Test marking contract as signed with both signatures."""
        contract = self.contract_repo.get_by_code('HD003')  # Approved

        result = self.workflow_service.mark_signed(
            contract.id, user_id=2,
            signed_by_customer=True,
            signed_by_representative=True
        )

        self.assertTrue(result.success)

        # Verify status changed
        updated = self.contract_repo.get_by_code('HD003')
        self.assertEqual(updated.status, 'signed')

    def test_mark_signed_partial(self):
        """Test marking with only one signature."""
        contract = self.contract_repo.get_by_code('HD003')  # Approved

        result = self.workflow_service.mark_signed(
            contract.id, user_id=2,
            signed_by_customer=True,
            signed_by_representative=False
        )

        # Should update signature but not transition
        self.assertTrue(result.success)
        self.assertIn("đủ cả 2", result.message)

    def test_record_payment_partial(self):
        """Test recording partial payment."""
        contract = self.contract_repo.get_by_code('HD004')  # Signed

        result = self.workflow_service.record_payment(
            contract.id, user_id=2, amount=500000000, payment_method='cash'
        )

        self.assertTrue(result.success)

        # Verify amounts updated
        updated = self.contract_repo.get_by_code('HD004')
        self.assertEqual(updated.paid_amount, 500000000)
        self.assertEqual(updated.remaining_amount, 600000000)

    def test_record_payment_full(self):
        """Test recording full payment."""
        # Create signed contract
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contracts (
                contract_code, customer_id, customer_name, car_id,
                car_brand, car_model, car_price, total_amount,
                final_amount, created_by, status, paid_amount,
                signed_by_customer, signed_by_representative
            )
            VALUES ('HD009', 1, 'Test Customer', 1, 'Toyota', 'Camry', 1000000000,
                    1000000000, 1100000000, 2, 'signed', 0,
                    1, 1)
        """)
        conn.commit()
        conn.close()

        contract = self.contract_repo.get_by_code('HD009')

        result = self.workflow_service.record_payment(
            contract.id, user_id=2, amount=1100000000, payment_method='bank_transfer'
        )

        self.assertTrue(result.success)

        # Verify status changed to paid
        updated = self.contract_repo.get_by_code('HD009')
        self.assertEqual(updated.status, 'paid')

    def test_mark_delivered_success(self):
        """Test marking contract as delivered."""
        contract = self.contract_repo.get_by_code('HD005')  # Paid

        result = self.workflow_service.mark_delivered(
            contract.id, user_id=2, notes="Delivered to customer"
        )

        self.assertTrue(result.success)

        # Verify status changed
        updated = self.contract_repo.get_by_code('HD005')
        self.assertEqual(updated.status, 'delivered')

    def test_mark_delivered_not_paid(self):
        """Test delivering unpaid contract."""
        contract = self.contract_repo.get_by_code('HD004')  # Signed, not paid

        result = self.workflow_service.mark_delivered(
            contract.id, user_id=2, notes="Delivered"
        )

        self.assertFalse(result.success)
        # Message should indicate that transition from 'signed' to 'delivered' is not allowed
        # or that contract must be in 'paid' status
        self.assertTrue(
            "paid" in result.message.lower() or "signed" in result.message.lower()
        )

    def test_cancel_contract(self):
        """Test cancelling contract."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        result = self.workflow_service.cancel(
            contract.id, user_id=3, reason="Customer changed mind"
        )

        self.assertTrue(result.success)

        # Verify status changed
        updated = self.contract_repo.get_by_code('HD002')
        self.assertEqual(updated.status, 'cancelled')

    def test_cancel_delivered_contract(self):
        """Test cancelling delivered contract (should fail)."""
        contract = self.contract_repo.get_by_code('HD006')  # Delivered

        result = self.workflow_service.cancel(
            contract.id, user_id=3, reason="Test"
        )

        self.assertFalse(result.success)
        # Should mention cannot cancel delivered
        self.assertTrue(
            "delivered" in result.message.lower() or "giao xe" in result.message.lower()
        )

    def test_get_workflow_history(self):
        """Test getting workflow history."""
        contract = self.contract_repo.get_by_code('HD001')  # Draft

        # Submit for approval
        self.workflow_service.submit_for_approval(contract.id, user_id=1)

        # Get history
        history = self.workflow_service.get_workflow_history(contract.id)

        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)

    def test_get_pending_approvals(self):
        """Test getting pending approvals."""
        contracts = self.workflow_service.get_pending_approvals()

        # Should return HD002 which is pending
        codes = [c.contract_code for c in contracts]
        self.assertIn('HD002', codes)

    def test_get_allowed_actions_draft(self):
        """Test allowed actions for draft contract."""
        contract = self.contract_repo.get_by_code('HD001')  # Draft

        actions = self.workflow_service.get_allowed_actions(contract, 1, 'sales')

        self.assertIn('edit', actions)
        self.assertIn('submit', actions)
        self.assertIn('cancel', actions)
        self.assertIn('delete', actions)

    def test_get_allowed_actions_pending(self):
        """Test allowed actions for pending contract."""
        contract = self.contract_repo.get_by_code('HD002')  # Pending

        # Sales user (creator)
        actions_sales = self.workflow_service.get_allowed_actions(contract, 1, 'sales')
        self.assertIn('view', actions_sales)
        self.assertNotIn('approve', actions_sales)

        # Manager user
        actions_manager = self.workflow_service.get_allowed_actions(contract, 2, 'manager')
        self.assertIn('approve', actions_manager)
        self.assertIn('reject', actions_manager)

    def test_get_allowed_actions_delivered(self):
        """Test allowed actions for delivered contract."""
        contract = self.contract_repo.get_by_code('HD006')  # Delivered

        actions = self.workflow_service.get_allowed_actions(contract, 1, 'sales')

        self.assertIn('view', actions)
        # No other actions allowed
        self.assertNotIn('edit', actions)
        self.assertNotIn('cancel', actions)


if __name__ == '__main__':
    unittest.main()
