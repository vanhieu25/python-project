# Sprint-2.4: Customer VIP Classification

**Module**: 👥 Customer Management  
**Mức độ ưu tiên**: Medium  
**Blocked by**: Sprint-2.3 (Customer History)  
**Ước lượng**: 1.5 ngày

---

## 1. Xác định Feature

### Mô tả
Tự động phân loại khách hàng thành các nhóm (VIP, Regular, Potential) dựa trên lịch sử giao dịch, tần suất mua hàng và giá trị giao dịch. Cho phép phân loại thủ công và tự động.

### Yêu cầu
- Tự động phân loại dựa trên quy tắc
- Cho phép phân loại thủ công
- Thông báo khi khách hàng đạt đủ điều kiện VIP
- Báo cáo phân loại khách hàng
- Khuyến mãi đặc biệt cho từng nhóm

### Dependencies
- Sprint-2.3: Cần lịch sử giao dịch để tính toán phân loại

---

## 2. Database

### Schema Updates
```sql
-- Thêm bảng customer_classification_rules
CREATE TABLE IF NOT EXISTS customer_classification_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(50) NOT NULL,
    customer_class VARCHAR(20) NOT NULL,        -- vip, regular, potential
    min_contracts INTEGER DEFAULT 0,            -- Số hợp đồng tối thiểu
    min_total_value DECIMAL(15,2) DEFAULT 0,      -- Tổng giá trị tối thiểu
    min_avg_value DECIMAL(15,2) DEFAULT 0,       -- Giá trị trung bình tối thiểu
    min_frequency_months INTEGER,               -- Tần suất mua (tháng)
    is_active BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 0,                  -- Ưu tiên áp dụng
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Thêm bảng customer_classification_history
CREATE TABLE IF NOT EXISTS customer_classification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    old_class VARCHAR(20),
    new_class VARCHAR(20),
    reason VARCHAR(50),                          -- auto, manual, rule_based
    changed_by INTEGER,                          -- NULL nếu tự động
    triggered_by_rule_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (changed_by) REFERENCES users(id),
    FOREIGN KEY (triggered_by_rule_id) REFERENCES customer_classification_rules(id)
);

-- Thêm bảng vip_benefits
CREATE TABLE IF NOT EXISTS vip_benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_class VARCHAR(20) NOT NULL,          -- vip, regular, potential
    benefit_name VARCHAR(100) NOT NULL,
    benefit_type VARCHAR(20),                    -- discount, service, gift
    benefit_value DECIMAL(10,2),                 -- Giá trị (%, số tiền)
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default rules
INSERT INTO customer_classification_rules 
(rule_name, customer_class, min_contracts, min_total_value, priority) VALUES
('VIP - High Value', 'vip', 3, 2000000000, 1),      -- 3 hợp đồng hoặc 2 tỷ
('VIP - Frequent Buyer', 'vip', 5, 1000000000, 2),  -- 5 hợp đồng hoặc 1 tỷ
('Regular', 'regular', 1, 500000000, 3),            -- 1 hợp đồng hoặc 500 triệu
('Potential', 'potential', 0, 0, 4);                -- Mặc định

-- Default VIP benefits
INSERT INTO vip_benefits 
(customer_class, benefit_name, benefit_type, benefit_value, description) VALUES
('vip', 'Giảm giá xe', 'discount', 5.0, 'Giảm 5% giá xe'),
('vip', 'Ưu tiên dịch vụ', 'service', NULL, 'Ưu tiên trong xếp hàng dịch vụ'),
('vip', 'Quà tặng bảo dưỡng', 'gift', 2000000, 'Phiếu bảo dưỡng miễn phí'),
('regular', 'Giảm giá phụ kiện', 'discount', 3.0, 'Giảm 3% phụ kiện');

-- Indexes
CREATE INDEX IF NOT EXISTS idx_customer_class_rules ON customer_classification_rules(customer_class);
CREATE INDEX IF NOT EXISTS idx_customer_class_history_customer ON customer_classification_history(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_class_history_date ON customer_classification_history(created_at);
```

---

## 3. Backend Logic

### Classification Service
```python
# src/services/customer_classification_service.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..repositories.customer_repository import CustomerRepository
from ..repositories.customer_classification_repository import CustomerClassificationRepository
from ..models.customer import Customer


@dataclass
class ClassificationRule:
    """Customer classification rule."""
    id: int
    rule_name: str
    customer_class: str
    min_contracts: int
    min_total_value: float
    min_avg_value: float
    min_frequency_months: Optional[int]
    priority: int


@dataclass
class CustomerMetrics:
    """Customer transaction metrics."""
    total_contracts: int
    total_value: float
    avg_value: float
    first_contract_date: Optional[datetime]
    last_contract_date: Optional[datetime]
    frequency_months: Optional[float]


class CustomerClassificationService:
    """Service for customer classification."""
    
    def __init__(self, customer_repo: CustomerRepository,
                 classification_repo: CustomerClassificationRepository):
        self.customer_repo = customer_repo
        self.classification_repo = classification_repo
    
    def classify_customer(self, customer_id: int,
                         changed_by: Optional[int] = None,
                         reason: str = 'auto') -> str:
        """Classify a single customer.
        
        Returns:
            New classification ('vip', 'regular', 'potential')
        """
        # Get customer metrics
        metrics = self._calculate_metrics(customer_id)
        
        # Get active rules sorted by priority
        rules = self.classification_repo.get_active_rules()
        
        # Apply rules
        new_class = 'potential'  # Default
        matched_rule = None
        
        for rule in rules:
            if self._matches_rule(metrics, rule):
                new_class = rule.customer_class
                matched_rule = rule
                break  # Apply first matching rule (highest priority)
        
        # Update if changed
        customer = self.customer_repo.get_by_id(customer_id)
        if customer and customer.customer_class != new_class:
            self._update_classification(
                customer_id,
                customer.customer_class,
                new_class,
                reason,
                changed_by,
                matched_rule.id if matched_rule else None
            )
        
        return new_class
    
    def classify_all_customers(self) -> Dict[str, int]:
        """Classify all customers and return statistics.
        
        Returns:
            Dict with counts for each class
        """
        customers = self.customer_repo.get_all()
        stats = {'vip': 0, 'regular': 0, 'potential': 0, 'changed': 0}
        
        for customer in customers:
            old_class = customer.customer_class
            new_class = self.classify_customer(customer.id, reason='auto_batch')
            
            stats[new_class] += 1
            if old_class != new_class:
                stats['changed'] += 1
        
        return stats
    
    def manual_classify(self, customer_id: int, new_class: str,
                       changed_by: int, reason: str) -> bool:
        """Manually classify a customer."""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return False
        
        if new_class not in ['vip', 'regular', 'potential']:
            raise ValueError(f"Invalid class: {new_class}")
        
        if customer.customer_class == new_class:
            return True  # No change needed
        
        self._update_classification(
            customer_id,
            customer.customer_class,
            new_class,
            f'manual: {reason}',
            changed_by,
            None
        )
        
        return True
    
    def _calculate_metrics(self, customer_id: int) -> CustomerMetrics:
        """Calculate customer transaction metrics."""
        summary = self.customer_repo.get_transaction_summary(customer_id)
        contracts = self.customer_repo.get_contracts(customer_id)
        
        total_contracts = summary.get('total_contracts', 0)
        total_value = summary.get('total_value', 0)
        avg_value = total_value / total_contracts if total_contracts > 0 else 0
        
        # Calculate dates
        first_date = None
        last_date = None
        if contracts:
            dates = [c['created_at'] for c in contracts if c.get('created_at')]
            if dates:
                first_date = min(dates)
                last_date = max(dates)
        
        # Calculate frequency
        frequency = None
        if total_contracts > 1 and first_date and last_date:
            days = (last_date - first_date).days
            months = days / 30.0
            frequency = months / (total_contracts - 1) if total_contracts > 1 else None
        
        return CustomerMetrics(
            total_contracts=total_contracts,
            total_value=total_value,
            avg_value=avg_value,
            first_contract_date=first_date,
            last_contract_date=last_date,
            frequency_months=frequency
        )
    
    def _matches_rule(self, metrics: CustomerMetrics, 
                     rule: ClassificationRule) -> bool:
        """Check if customer matches a classification rule."""
        # Check minimum contracts
        if metrics.total_contracts < rule.min_contracts:
            return False
        
        # Check minimum total value
        if metrics.total_value < rule.min_total_value:
            return False
        
        # Check minimum average value
        if rule.min_avg_value > 0 and metrics.avg_value < rule.min_avg_value:
            return False
        
        # Check frequency (if specified)
        if rule.min_frequency_months is not None:
            if metrics.frequency_months is None:
                return False
            if metrics.frequency_months > rule.min_frequency_months:
                return False
        
        return True
    
    def _update_classification(self, customer_id: int, old_class: str,
                              new_class: str, reason: str,
                              changed_by: Optional[int],
                              rule_id: Optional[int]):
        """Update customer classification."""
        # Update customer
        self.customer_repo.update(customer_id, {
            'customer_class': new_class
        })
        
        # Record history
        self.classification_repo.record_classification_change(
            customer_id, old_class, new_class, reason, changed_by, rule_id
        )
        
        # Check if should notify (upgraded to VIP)
        if new_class == 'vip' and old_class != 'vip':
            self._notify_vip_upgrade(customer_id)
    
    def _notify_vip_upgrade(self, customer_id: int):
        """Notify when customer is upgraded to VIP."""
        # Implementation depends on notification system
        # For now, just log
        print(f"Customer {customer_id} upgraded to VIP!")
    
    def get_classification_report(self) -> Dict[str, Any]:
        """Get classification report."""
        customers = self.customer_repo.get_all()
        
        stats = {
            'vip': {'count': 0, 'total_value': 0, 'avg_value': 0},
            'regular': {'count': 0, 'total_value': 0, 'avg_value': 0},
            'potential': {'count': 0, 'total_value': 0, 'avg_value': 0}
        }
        
        for customer in customers:
            c_class = customer.customer_class or 'potential'
            summary = self.customer_repo.get_transaction_summary(customer.id)
            total_value = summary.get('total_value', 0)
            
            stats[c_class]['count'] += 1
            stats[c_class]['total_value'] += total_value
        
        # Calculate averages
        for c_class in stats:
            count = stats[c_class]['count']
            if count > 0:
                stats[c_class]['avg_value'] = stats[c_class]['total_value'] / count
        
        return {
            'summary': stats,
            'total_customers': len(customers),
            'classification_distribution': {
                c: stats[c]['count'] for c in stats
            }
        }
    
    def get_vip_benefits(self, customer_class: str) -> List[Dict]:
        """Get benefits for a customer class."""
        return self.classification_repo.get_benefits(customer_class)
    
    def should_check_classification(self, customer_id: int) -> bool:
        """Check if customer classification should be re-evaluated.
        
        Returns True if:
        - No classification history
        - Last classification was more than 30 days ago
        - Customer had new transaction since last classification
        """
        last_check = self.classification_repo.get_last_classification_date(customer_id)
        
        if not last_check:
            return True
        
        days_since = (datetime.now() - last_check).days
        return days_since >= 30


class ClassificationRuleManager:
    """Manager for classification rules."""
    
    def __init__(self, classification_repo: CustomerClassificationRepository):
        self.repo = classification_repo
    
    def create_rule(self, rule_data: Dict[str, Any]) -> int:
        """Create a new classification rule."""
        return self.repo.create_rule(rule_data)
    
    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Update a classification rule."""
        return self.repo.update_rule(rule_id, rule_data)
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a classification rule."""
        return self.repo.delete_rule(rule_id)
    
    def get_rules(self, customer_class: Optional[str] = None) -> List[ClassificationRule]:
        """Get classification rules."""
        return self.repo.get_rules(customer_class)
    
    def reorder_rules(self, rule_ids: List[int]) -> bool:
        """Reorder rules by priority."""
        return self.repo.reorder_rules(rule_ids)
```

### Classification Repository
```python
# src/repositories/customer_classification_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper


class CustomerClassificationRepository:
    """Repository for customer classification data."""
    
    def __init__(self, db: DatabaseHelper):
        self.db = db
    
    def get_active_rules(self) -> List[Any]:
        """Get active classification rules sorted by priority."""
        query = """
            SELECT * FROM customer_classification_rules
            WHERE is_active = 1
            ORDER BY priority ASC
        """
        rows = self.db.fetch_all(query)
        return [self._row_to_rule(row) for row in rows]
    
    def get_rules(self, customer_class: Optional[str] = None) -> List[Any]:
        """Get classification rules."""
        if customer_class:
            query = """
                SELECT * FROM customer_classification_rules
                WHERE customer_class = ?
                ORDER BY priority ASC
            """
            rows = self.db.fetch_all(query, (customer_class,))
        else:
            query = "SELECT * FROM customer_classification_rules ORDER BY priority ASC"
            rows = self.db.fetch_all(query)
        
        return [self._row_to_rule(row) for row in rows]
    
    def create_rule(self, rule_data: Dict[str, Any]) -> int:
        """Create a new rule."""
        query = """
            INSERT INTO customer_classification_rules
            (rule_name, customer_class, min_contracts, min_total_value,
             min_avg_value, min_frequency_months, priority, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            rule_data['rule_name'],
            rule_data['customer_class'],
            rule_data.get('min_contracts', 0),
            rule_data.get('min_total_value', 0),
            rule_data.get('min_avg_value', 0),
            rule_data.get('min_frequency_months'),
            rule_data.get('priority', 0),
            rule_data.get('is_active', True)
        )
        return self.db.execute(query, params)
    
    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Update a rule."""
        allowed = ['rule_name', 'customer_class', 'min_contracts',
                   'min_total_value', 'min_avg_value', 'min_frequency_months',
                   'priority', 'is_active']
        
        fields = []
        params = []
        for field in allowed:
            if field in rule_data:
                fields.append(f"{field} = ?")
                params.append(rule_data[field])
        
        if not fields:
            return False
        
        fields.append("updated_at = ?")
        params.append(datetime.now())
        params.append(rule_id)
        
        query = f"UPDATE customer_classification_rules SET {', '.join(fields)} WHERE id = ?"
        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule."""
        query = "DELETE FROM customer_classification_rules WHERE id = ?"
        try:
            self.db.execute(query, (rule_id,))
            return True
        except Exception:
            return False
    
    def record_classification_change(self, customer_id: int,
                                    old_class: Optional[str],
                                    new_class: str,
                                    reason: str,
                                    changed_by: Optional[int],
                                    rule_id: Optional[int]) -> int:
        """Record classification change."""
        query = """
            INSERT INTO customer_classification_history
            (customer_id, old_class, new_class, reason, changed_by, 
             triggered_by_rule_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(query, (
            customer_id, old_class, new_class, reason, changed_by,
            rule_id, datetime.now()
        ))
    
    def get_last_classification_date(self, customer_id: int) -> Optional[datetime]:
        """Get last classification date for customer."""
        query = """
            SELECT MAX(created_at) as last_date
            FROM customer_classification_history
            WHERE customer_id = ?
        """
        result = self.db.fetch_one(query, (customer_id,))
        return result['last_date'] if result and result['last_date'] else None
    
    def get_benefits(self, customer_class: str) -> List[Dict]:
        """Get benefits for customer class."""
        query = """
            SELECT * FROM vip_benefits
            WHERE customer_class = ? AND is_active = 1
            ORDER BY benefit_name
        """
        return self.db.fetch_all(query, (customer_class,))
    
    def reorder_rules(self, rule_ids: List[int]) -> bool:
        """Reorder rules by updating priority."""
        try:
            for i, rule_id in enumerate(rule_ids):
                query = "UPDATE customer_classification_rules SET priority = ? WHERE id = ?"
                self.db.execute(query, (i + 1, rule_id))
            return True
        except Exception:
            return False
    
    def _row_to_rule(self, row: Dict) -> Any:
        """Convert database row to ClassificationRule."""
        from ..services.customer_classification_service import ClassificationRule
        return ClassificationRule(
            id=row['id'],
            rule_name=row['rule_name'],
            customer_class=row['customer_class'],
            min_contracts=row['min_contracts'],
            min_total_value=row['min_total_value'],
            min_avg_value=row.get('min_avg_value', 0),
            min_frequency_months=row.get('min_frequency_months'),
            priority=row['priority']
        )
```

---

## 4. UI Design

### Customer Classification Panel
```
┌─────────────────────────────────────────────────────────────────┐
│  ⭐ Phân loại khách hàng                              [✕]     │
├─────────────────────────────────────────────────────────────────┤
│  Khách hàng: Nguyễn Văn An (KH000001)                          │
│  Phân loại hiện tại: [Regular ▼]                              │
│                                                                 │
│  📊 Chỉ số giao dịch                                          │
│  ┌─────────────────┬─────────────────┬─────────────────┐     │
│  │ Tổng hợp đồng   │ Tổng giá trị    │ Giá trị TB      │     │
│  │      3          │   1.8 tỷ VNĐ    │  600 triệu      │     │
│  └─────────────────┴─────────────────┴─────────────────┘     │
│                                                                 │
│  🎯 Phân loại tự động                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Theo quy tắc: VIP (3 hợp đồng ≥ 2 tỷ)                   │   │
│  │ [✓] Áp dụng tự động                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  🎁 Quyền lợi VIP                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ✓ Giảm 5% giá xe                                        │   │
│  │ ✓ Ưu tiên trong xếp hàng dịch vụ                        │   │
│  │ ✓ Phiếu bảo dưỡng miễn phí (2 triệu)                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Ghi chú phân loại:                                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Khách hàng thân thiết, mua nhiều lần                 │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Hủy]  [🔄 Tự động phân loại]  [💾 Lưu thay đổi]             │
└─────────────────────────────────────────────────────────────────┘
```

### Classification Rules Management
```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Quản lý quy tắc phân loại                          [✕]     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Ưu tiên │ Quy tắt                        │ Phân loại    │   │
│  ├─────────┼────────────────────────────────┼──────────────┤   │
│  │ 1       │ VIP - High Value               │ ⭐ VIP       │   │
│  │         │ ≥3 hợp đồng HOẶC ≥2 tỷ        │              │   │
│  ├─────────┼────────────────────────────────┼──────────────┤   │
│  │ 2       │ VIP - Frequent Buyer           │ ⭐ VIP       │   │
│  │         │ ≥5 hợp đồng HOẶC ≥1 tỷ        │              │   │
│  ├─────────┼────────────────────────────────┼──────────────┤   │
│  │ 3       │ Regular                        │ ● Regular    │   │
│  │         │ ≥1 hợp đồng HOẶC ≥500tr       │              │   │
│  ├─────────┼────────────────────────────────┼──────────────┤   │
│  │ 4       │ Potential                      │ ○ Potential  │   │
│  │         │ Mặc định                       │              │   │
│  └─────────┴────────────────────────────────┴──────────────┘   │
│                                                                 │
│  [➕ Thêm quy tắc]  [✏️ Sửa]  [🗑️ Xóa]  [🔄 Chạy phân loại]   │
└─────────────────────────────────────────────────────────────────┘
```

### Classification Report
```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Báo cáo phân loại khách hàng                                │
├─────────────────────────────────────────────────────────────────┤
│  Tổng số: 150 khách hàng                                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Phân loại        │ Số lượng │ Tỷ lệ  │ Tổng giá trị   │     │
│  ├──────────────────┼──────────┼────────┼────────────────┤     │
│  │ ⭐ VIP           │    15    │  10%   │   25 tỷ VNĐ    │     │
│  │ ● Regular        │    45    │  30%   │   18 tỷ VNĐ    │     │
│  │ ○ Potential      │    90    │  60%   │    0 VNĐ       │     │
│  └──────────────────┴──────────┴────────┴────────────────┘     │
│                                                                 │
│  📈 Giá trị trung bình theo phân loại:                         │
│  VIP: 1.67 tỷ  │  Regular: 400 triệu  │  Potential: N/A        │
│                                                                 │
│  [📥 Export Excel]  [🖨️ In báo cáo]                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Testing

### Service Tests
```python
# tests/test_customer_classification_service.py
import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.repositories.customer_classification_repository import CustomerClassificationRepository
from src.services.customer_classification_service import (
    CustomerClassificationService, ClassificationRuleManager,
    CustomerMetrics, ClassificationRule
)


class TestCustomerClassificationService(unittest.TestCase):
    """Tests for customer classification service."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        
        self.customer_repo = CustomerRepository(self.db)
        self.classification_repo = CustomerClassificationRepository(self.db)
        self.service = CustomerClassificationService(self.customer_repo, self.classification_repo)
        
        # Create test customer
        self.customer_id = self.customer_repo.create({
            'full_name': 'Test Customer',
            'phone': '0901234567',
            'customer_type': 'individual',
            'customer_class': 'potential'
        })
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_classify_potential_customer(self):
        """Test classifying potential customer."""
        new_class = self.service.classify_customer(self.customer_id)
        
        # Should be potential (no transactions)
        self.assertEqual(new_class, 'potential')
    
    def test_matches_vip_rule(self):
        """Test VIP rule matching."""
        metrics = CustomerMetrics(
            total_contracts=3,
            total_value=2500000000,
            avg_value=833333333,
            first_contract_date=None,
            last_contract_date=None,
            frequency_months=None
        )
        
        rule = ClassificationRule(
            id=1, rule_name='VIP Test',
            customer_class='vip',
            min_contracts=3, min_total_value=2000000000,
            min_avg_value=0, min_frequency_months=None,
            priority=1
        )
        
        matches = self.service._matches_rule(metrics, rule)
        self.assertTrue(matches)
    
    def test_matches_regular_rule(self):
        """Test regular rule matching."""
        metrics = CustomerMetrics(
            total_contracts=1,
            total_value=600000000,
            avg_value=600000000,
            first_contract_date=None,
            last_contract_date=None,
            frequency_months=None
        )
        
        rule = ClassificationRule(
            id=1, rule_name='Regular Test',
            customer_class='regular',
            min_contracts=1, min_total_value=500000000,
            min_avg_value=0, min_frequency_months=None,
            priority=1
        )
        
        matches = self.service._matches_rule(metrics, rule)
        self.assertTrue(matches)
    
    def test_manual_classification(self):
        """Test manual classification."""
        success = self.service.manual_classify(
            self.customer_id, 'vip', 
            changed_by=1, reason='Khách hàng thân thiết'
        )
        
        self.assertTrue(success)
        
        customer = self.customer_repo.get_by_id(self.customer_id)
        self.assertEqual(customer.customer_class, 'vip')
    
    def test_get_classification_report(self):
        """Test classification report."""
        report = self.service.get_classification_report()
        
        self.assertIn('summary', report)
        self.assertIn('total_customers', report)
        self.assertIn('classification_distribution', report)
        
        self.assertEqual(report['total_customers'], 1)


class TestClassificationRuleManager(unittest.TestCase):
    """Tests for classification rule manager."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.classification_repo = CustomerClassificationRepository(self.db)
        self.manager = ClassificationRuleManager(self.classification_repo)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_create_rule(self):
        """Test creating a rule."""
        rule_id = self.manager.create_rule({
            'rule_name': 'Test Rule',
            'customer_class': 'vip',
            'min_contracts': 5,
            'min_total_value': 1000000000,
            'priority': 1
        })
        
        self.assertGreater(rule_id, 0)
        
        rules = self.manager.get_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].rule_name, 'Test Rule')
    
    def test_update_rule(self):
        """Test updating a rule."""
        rule_id = self.manager.create_rule({
            'rule_name': 'Original',
            'customer_class': 'regular',
            'min_contracts': 1,
            'priority': 1
        })
        
        success = self.manager.update_rule(rule_id, {
            'rule_name': 'Updated',
            'min_contracts': 2
        })
        
        self.assertTrue(success)
        
        rules = self.manager.get_rules()
        self.assertEqual(rules[0].rule_name, 'Updated')
        self.assertEqual(rules[0].min_contracts, 2)
```

---

## 6. Definition of Done

- [ ] CustomerClassificationService với rule-based classification
- [ ] ClassificationRuleManager cho quản lý quy tắc
- [ ] Automatic classification dựa trên metrics
- [ ] Manual classification với ghi chú
- [ ] VIP notification khi upgrade
- [ ] Classification report với statistics
- [ ] UI quản lý quy tắc phân loại
- [ ] UI xem và thay đổi phân loại khách hàng
- [ ] Unit tests pass (≥ 80% coverage)
- [ ] Code committed: `feat: phân loại khách hàng VIP`

---

## 7. Git Commit

```bash
# Files to commit
- src/services/customer_classification_service.py (mới)
- src/repositories/customer_classification_repository.py (mới)
- src/database/schema.sql (cập nhật)
- src/ui/customers/classification_dialog.py (mới)
- src/ui/customers/classification_rules_dialog.py (mới)
- src/ui/customers/classification_report.py (mới)
- tests/test_customer_classification_service.py (mới)

# Commit message
feat: phân loại khách hàng VIP

- Thêm CustomerClassificationService với rule-based classification
- Thêm ClassificationRuleManager cho CRUD quy tắc
- Triển khai tự động phân loại dựa trên metrics giao dịch
- Thêm manual classification với audit trail
- Tạo notification khi khách hàng upgrade lên VIP
- Thêm classification report với distribution statistics
- Tạo UI quản lý quy tắc và phân loại khách hàng
- Thêm bảng customer_classification_rules và vip_benefits

Closes sprint-2.4
```
