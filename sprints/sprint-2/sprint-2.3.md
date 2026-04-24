# Sprint-2.3: Customer History

**Module**: 👥 Customer Management  
**Mức độ ưu tiên**: Medium  
**Blocked by**: Sprint-2.2 (Customer CRUD Operations)  
**Ước lượng**: 1.5 ngày

---

## 1. Xác định Feature

### Mô tả
Hiển thị lịch sử giao dịch và hoạt động của khách hàng, bao gồm lịch sử chỉnh sửa thông tin, các hợp đồng đã ký, và tổng giá trị giao dịch.

### Yêu cầu
- Xem lịch sử chỉnh sửa thông tin khách hàng
- Xem danh sách hợp đồng của khách hàng
- Tính toán tổng giá trị giao dịch
- Timeline view cho lịch sử hoạt động
- Export lịch sử ra file

### Dependencies
- Sprint-2.2: Cần customer_history table
- Sprint-4.x: Cần contracts module cho danh sách hợp đồng

---

## 2. Database

### Schema Updates
```sql
-- Bảng contracts (sẽ được tạo ở Sprint 4)
-- Tạm thời reference để hiểu data structure
/*
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_code VARCHAR(20) UNIQUE,
    customer_id INTEGER,
    car_id INTEGER,
    sale_date DATE,
    total_amount DECIMAL(15,2),
    status VARCHAR(20), -- pending, signed, paid, delivered, cancelled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (car_id) REFERENCES cars(id)
);
*/

-- Thêm view cho customer summary
CREATE VIEW IF NOT EXISTS customer_summary AS
SELECT 
    c.id as customer_id,
    c.full_name,
    c.customer_code,
    COUNT(DISTINCT co.id) as total_contracts,
    COALESCE(SUM(co.total_amount), 0) as total_transaction_value,
    MAX(co.created_at) as last_transaction_date,
    CASE 
        WHEN COUNT(DISTINCT co.id) >= 3 OR COALESCE(SUM(co.total_amount), 0) >= 2000000000 
        THEN 'vip'
        WHEN COUNT(DISTINCT co.id) >= 1 OR COALESCE(SUM(co.total_amount), 0) >= 500000000 
        THEN 'regular'
        ELSE 'potential'
    END as auto_class
FROM customers c
LEFT JOIN contracts co ON c.id = co.customer_id 
    AND co.status IN ('signed', 'paid', 'delivered')
WHERE c.is_deleted = 0
GROUP BY c.id;

-- Indexes cho customer history queries
CREATE INDEX IF NOT EXISTS idx_customer_history_action ON customer_history(action);
CREATE INDEX IF NOT EXISTS idx_customer_history_date ON customer_history(changed_at);
```

---

## 3. Backend Logic

### Customer History Service
```python
# src/services/customer_history_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..repositories.customer_history_repository import CustomerHistoryRepository
from ..repositories.customer_repository import CustomerRepository


class CustomerHistoryService:
    """Service for customer history and transaction tracking."""
    
    def __init__(self, history_repo: CustomerHistoryRepository,
                 customer_repo: CustomerRepository,
                 contract_repo=None):  # Will be injected later
        self.history_repo = history_repo
        self.customer_repo = customer_repo
        self.contract_repo = contract_repo
    
    def get_full_history(self, customer_id: int) -> Dict[str, Any]:
        """Get complete customer history.
        
        Returns:
            Dictionary containing:
            - profile_changes: List of profile edit history
            - contracts: List of contracts
            - timeline: Combined timeline of all activities
            - summary: Transaction summary
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return None
        
        # Get profile history
        profile_changes = self.history_repo.get_history(customer_id)
        
        # Get contracts (if contract repo available)
        contracts = []
        if self.contract_repo:
            contracts = self.contract_repo.get_by_customer(customer_id)
        
        # Build timeline
        timeline = self._build_timeline(profile_changes, contracts)
        
        # Get summary
        summary = self._get_transaction_summary(customer_id, contracts)
        
        return {
            'customer': customer,
            'profile_changes': profile_changes,
            'contracts': contracts,
            'timeline': timeline,
            'summary': summary
        }
    
    def _build_timeline(self, profile_changes: List[Dict],
                       contracts: List[Any]) -> List[Dict]:
        """Build unified timeline from all activities."""
        timeline = []
        
        # Add profile changes
        for change in profile_changes:
            timeline.append({
                'type': 'profile',
                'action': change['action'],
                'description': self._format_profile_change(change),
                'timestamp': change['changed_at'],
                'user': change.get('changed_by_name', 'Unknown'),
                'icon': self._get_action_icon(change['action'])
            })
        
        # Add contracts
        for contract in contracts:
            timeline.append({
                'type': 'contract',
                'action': 'contract_created',
                'description': f"Tạo hợp đồng {contract.contract_code}",
                'timestamp': contract.created_at,
                'user': contract.created_by_name if hasattr(contract, 'created_by_name') else 'Unknown',
                'amount': contract.total_amount,
                'icon': '📄'
            })
        
        # Sort by timestamp (newest first)
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return timeline
    
    def _format_profile_change(self, change: Dict) -> str:
        """Format profile change for display."""
        action = change['action']
        field = change.get('field_name', '')
        old = change.get('old_value', '')
        new = change.get('new_value', '')
        
        action_map = {
            'create': 'Tạo mới khách hàng',
            'delete': f"Xóa khách hàng (lý do: {old or 'Không có'})",
            'restore': 'Khôi phục khách hàng'
        }
        
        if action in action_map:
            return action_map[action]
        
        if action == 'update' and field:
            field_names = {
                'full_name': 'Họ tên',
                'phone': 'Số điện thoại',
                'email': 'Email',
                'address': 'Địa chỉ',
                'customer_class': 'Phân loại',
                'notes': 'Ghi chú'
            }
            field_name = field_names.get(field, field)
            return f"Cập nhật {field_name}: {old or '(trống)'} → {new or '(trống)' }"
        
        return f"Thao tác: {action}"
    
    def _get_action_icon(self, action: str) -> str:
        """Get icon for action type."""
        icons = {
            'create': '👤',
            'update': '✏️',
            'delete': '🗑️',
            'restore': '↩️'
        }
        return icons.get(action, '📝')
    
    def _get_transaction_summary(self, customer_id: int,
                                contracts: List[Any]) -> Dict:
        """Calculate transaction summary."""
        total_contracts = len(contracts)
        total_value = sum(c.total_amount for c in contracts if hasattr(c, 'total_amount'))
        
        # Calculate by status
        status_counts = {}
        for contract in contracts:
            status = contract.status if hasattr(contract, 'status') else 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Last transaction
        last_transaction = None
        if contracts:
            sorted_contracts = sorted(contracts, 
                                    key=lambda x: x.created_at if hasattr(x, 'created_at') else datetime.min,
                                    reverse=True)
            last_transaction = sorted_contracts[0].created_at if sorted_contracts else None
        
        return {
            'total_contracts': total_contracts,
            'total_value': total_value,
            'average_value': total_value / total_contracts if total_contracts > 0 else 0,
            'status_breakdown': status_counts,
            'last_transaction_date': last_transaction
        }
    
    def export_history(self, customer_id: int, 
                      format: str = 'csv') -> str:
        """Export customer history to file.
        
        Args:
            customer_id: Customer ID
            format: 'csv' or 'json'
        
        Returns:
            File path of exported file
        """
        import csv
        import json
        import tempfile
        from datetime import datetime
        
        history = self.get_full_history(customer_id)
        if not history:
            return None
        
        customer = history['customer']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"customer_{customer.customer_code}_{timestamp}.{format}"
        filepath = f"exports/{filename}"
        
        if format == 'csv':
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Thời gian', 'Loại', 'Hành động', 'Mô tả', 'Người thực hiện'])
                for item in history['timeline']:
                    writer.writerow([
                        item['timestamp'],
                        item['type'],
                        item['action'],
                        item['description'],
                        item['user']
                    ])
        else:  # json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, default=str)
        
        return filepath
    
    def get_customer_statistics(self, customer_id: int) -> Dict[str, Any]:
        """Get customer transaction statistics."""
        summary = self.get_full_history(customer_id)['summary'] if self.get_full_history(customer_id) else {}
        
        # Calculate VIP score
        total_value = summary.get('total_value', 0)
        total_contracts = summary.get('total_contracts', 0)
        
        vip_score = 0
        if total_value >= 2000000000:  # 2 tỷ
            vip_score += 50
        elif total_value >= 1000000000:  # 1 tỷ
            vip_score += 30
        elif total_value >= 500000000:  # 500 triệu
            vip_score += 15
        
        vip_score += min(total_contracts * 10, 50)  # Max 50 points from contracts
        
        return {
            'total_contracts': total_contracts,
            'total_value': total_value,
            'vip_score': vip_score,
            'tier': 'VIP' if vip_score >= 60 else 'Regular' if vip_score >= 30 else 'Potential'
        }
```

### Extended Repository Methods
```python
# Add to src/repositories/customer_repository.py

    def get_transaction_summary(self, customer_id: int) -> Dict[str, Any]:
        """Get transaction summary for customer."""
        query = """
            SELECT 
                COUNT(*) as total_contracts,
                COALESCE(SUM(total_amount), 0) as total_value,
                MAX(created_at) as last_transaction
            FROM contracts
            WHERE customer_id = ? AND status IN ('signed', 'paid', 'delivered')
        """
        result = self.db.fetch_one(query, (customer_id,))
        return {
            'total_contracts': result['total_contracts'] if result else 0,
            'total_value': result['total_value'] if result else 0,
            'last_transaction': result['last_transaction'] if result else None
        }
    
    def get_contracts(self, customer_id: int) -> List[Dict]:
        """Get all contracts for customer."""
        query = """
            SELECT c.*, 
                   car.brand, car.model, car.license_plate,
                   u.full_name as created_by_name
            FROM contracts c
            LEFT JOIN cars car ON c.car_id = car.id
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.customer_id = ?
            ORDER BY c.created_at DESC
        """
        return self.db.fetch_all(query, (customer_id,))
```

---

## 4. UI Design

### Customer History Dialog
```
┌─────────────────────────────────────────────────────────────────┐
│  📋 Lịch sử khách hàng: Nguyễn Văn An (KH000001)      [✕]     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌───────────────────────────────────────┐ │
│  │ 📊 TỔNG QUAN    │ │ 🕐 TIMELINE HOẠT ĐỘNG               │ │
│  │ ──────────────  │ │                                      │ │
│  │ Tổng hợp đồng:  │ │ 2024-01-15 10:30                     │ │
│  │     5           │ │ 👤 Tạo mới khách hàng               │ │
│  │                 │ │    bởi Admin                        │ │
│  │ Tổng giá trị:   │ │                                      │ │
│  │   4.5 tỷ VNĐ    │ │ 2024-02-20 14:15                     │ │
│  │                 │ │ 📄 Tạo hợp đồng HD000123            │ │
│  │ Giao dịch cuối: │ │    850 triệu - Honda Civic          │ │
│  │ 2024-02-20      │ │    bởi Nguyễn Văn B                 │ │
│  │                 │ │                                      │ │
│  │ Phân loại: ⭐VIP│ │ 2024-03-01 09:00                     │ │
│  │                 │ │ ✏️ Cập nhật SĐT: 0901... → 0909...  │ │
│  │ [📥 Export]     │ │    bởi Admin                        │ │
│  │                 │ │                                      │ │
│  │                 │ │ 2024-03-15 16:45                     │ │
│  │                 │ │ 📄 Tạo hợp đồng HD000145            │ │
│  │                 │ │    1.2 tỷ - Toyota Camry            │ │
│  │                 │ │                                      │ │
│  └─────────────────┘ └───────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  [📄 Xem hợp đồng]  [💾 Export CSV]  [🔄 Refresh]              │
└─────────────────────────────────────────────────────────────────┘
```

### Contract List Panel
```
┌────────────────────────────────────────────────────────────┐
│  📄 Danh sách hợp đồng                                     │
├────────────────────────┬───────────┬────────────┬─────────┤
│ Mã HĐ     │ Xe                │ Ngày       │ Giá trị │
├───────────┼───────────────────┼────────────┼─────────┤
│ HD000145  │ Toyota Camry 2023 │ 2024-03-15 │ 1.2 tỷ  │
│ HD000123  │ Honda Civic 2023  │ 2024-02-20 │ 850tr   │
│ HD000099  │ Mazda 3 2022      │ 2024-01-10 │ 750tr   │
└───────────┴───────────────────┴────────────┴─────────┘
```

### Timeline Item Component
```
┌────────────────────────────────────────────────────────────┐
│  2024-03-15 14:30                              👤 Admin    │
│  ─────────────────────────────────────────────────────────  │
│  📄 Tạo hợp đồng HD000145                                │
│  Xe: Toyota Camry 2023                                    │
│  Giá trị: 1,200,000,000 VNĐ                              │
│  Trạng thái: Đã thanh toán                               │
└────────────────────────────────────────────────────────────┘
```

---

## 5. Testing

### Service Tests
```python
# tests/test_customer_history_service.py
import unittest
import tempfile
import shutil
import os
from datetime import datetime

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.repositories.customer_history_repository import CustomerHistoryRepository
from src.services.customer_history_service import CustomerHistoryService


class TestCustomerHistoryService(unittest.TestCase):
    """Tests for customer history service."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        
        self.customer_repo = CustomerRepository(self.db)
        self.history_repo = CustomerHistoryRepository(self.db)
        self.service = CustomerHistoryService(self.history_repo, self.customer_repo)
        
        self.user_id = 1
        
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
        shutil.rmtree(self.temp_dir)
    
    def test_get_full_history(self):
        """Test getting full customer history."""
        history = self.service.get_full_history(self.customer_id)
        
        self.assertIsNotNone(history)
        self.assertIn('profile_changes', history)
        self.assertIn('timeline', history)
        self.assertIn('summary', history)
        
        # Check profile changes
        self.assertEqual(len(history['profile_changes']), 2)
    
    def test_build_timeline(self):
        """Test timeline building."""
        profile_changes = self.history_repo.get_history(self.customer_id)
        timeline = self.service._build_timeline(profile_changes, [])
        
        self.assertEqual(len(timeline), 2)
        self.assertEqual(timeline[0]['type'], 'profile')
        self.assertIn('description', timeline[0])
    
    def test_transaction_summary(self):
        """Test transaction summary."""
        summary = self.service._get_transaction_summary(self.customer_id, [])
        
        self.assertEqual(summary['total_contracts'], 0)
        self.assertEqual(summary['total_value'], 0)
    
    def test_customer_statistics(self):
        """Test customer statistics calculation."""
        stats = self.service.get_customer_statistics(self.customer_id)
        
        self.assertIn('total_contracts', stats)
        self.assertIn('total_value', stats)
        self.assertIn('vip_score', stats)
        self.assertIn('tier', stats)
    
    def test_export_history_csv(self):
        """Test exporting history to CSV."""
        import os
        os.makedirs('exports', exist_ok=True)
        
        filepath = self.service.export_history(self.customer_id, 'csv')
        
        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.endswith('.csv'))
        self.assertTrue(os.path.exists(filepath))
        
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_nonexistent_customer(self):
        """Test handling nonexistent customer."""
        history = self.service.get_full_history(99999)
        self.assertIsNone(history)
```

---

## 6. Definition of Done

- [ ] CustomerHistoryService với timeline building
- [ ] Contract list integration
- [ ] Transaction summary calculation
- [ ] VIP score calculation
- [ ] Timeline UI với icons
- [ ] Export to CSV/JSON
- [ ] Customer statistics display
- [ ] Unit tests pass (≥ 80% coverage)
- [ ] Code committed: `feat: lịch sử giao dịch khách hàng`

---

## 7. Git Commit

```bash
# Files to commit
- src/services/customer_history_service.py (mới)
- src/repositories/customer_repository.py (cập nhật)
- src/database/schema.sql (cập nhật - view customer_summary)
- src/ui/customers/customer_history_dialog.py (mới)
- src/ui/customers/timeline_component.py (mới)
- tests/test_customer_history_service.py (mới)

# Commit message
feat: lịch sử giao dịch khách hàng

- Thêm CustomerHistoryService với timeline building
- Triển khi tính toán tổng quan giao dịch
- Thêm VIP score calculation dựa trên giá trị giao dịch
- Tạo Timeline UI component với visual indicators
- Thêm export history ra CSV và JSON
- Thêm customer_summary view trong database
- Cập nhật CustomerRepository với transaction methods

Closes sprint-2.3
```
