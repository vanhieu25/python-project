# Sprint-2.1: Customer Management Initial

**Module**: 👥 Customer Management  
**Mức độ ưu tiên**: Core  
**Blocked by**: Sprint-0.3 (Authorization)  
**Ước lượng**: 2 ngày

---

## 1. Xác định Feature

### Mô tả
Khởi tạo module quản lý khách hàng - tạo nền tảng database và cấu trúc cơ bản cho chức năng quản lý thông tin khách hàng cá nhân và doanh nghiệp.

### Yêu cầu
- Tạo bảng `customers` trong database
- Định nghĩa model và validators cho khách hàng
- Phân loại khách hàng: cá nhân và doanh nghiệp
- Tạo giao diện list view cơ bản hiển thị danh sách khách hàng
- Unit test CRUD cơ bản

### Dependencies
- Sprint-0.3 (Authorization): Cần hệ thống phân quyền để kiểm soát truy cập

---

## 2. Database

### Schema
```sql
-- Bảng customers (Thông tin khách hàng)
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_code VARCHAR(20) UNIQUE,           -- Mã khách hàng (tự động sinh)
    customer_type VARCHAR(20) DEFAULT 'individual', -- individual/business
    
    -- Thông tin cá nhân
    full_name VARCHAR(100) NOT NULL,            -- Họ tên (cá nhân) hoặc tên người đại diện (doanh nghiệp)
    id_card VARCHAR(20),                        -- CMND/CCCD
    date_of_birth DATE,                         -- Ngày sinh
    gender VARCHAR(10),                         -- Nam/Nữ/Khác
    
    -- Thông tin doanh nghiệp (nếu customer_type = 'business')
    company_name VARCHAR(100),                  -- Tên công ty
    tax_code VARCHAR(20),                       -- Mã số thuế
    business_registration VARCHAR(50),          -- Số đăng ký kinh doanh
    
    -- Thông tin liên hệ
    phone VARCHAR(20),                          -- Số điện thoại chính
    phone2 VARCHAR(20),                         -- Số điện thoại phụ
    email VARCHAR(100),                         -- Email
    
    -- Địa chỉ
    address TEXT,                               -- Địa chỉ đầy đủ
    province VARCHAR(50),                       -- Tỉnh/Thành phố
    district VARCHAR(50),                       -- Quận/Huyện
    ward VARCHAR(50),                           -- Phường/Xã
    
    -- Thông tin phân loại
    customer_class VARCHAR(20) DEFAULT 'regular', -- regular/potential/vip
    source VARCHAR(50),                         -- Nguồn khách hàng (facebook, website, referral, etc.)
    
    -- Metadata
    notes TEXT,                                 -- Ghi chú
    assigned_to INTEGER,                        -- Nhân viên phụ trách
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,                         -- Người tạo record
    is_deleted BOOLEAN DEFAULT 0,               -- Soft delete flag
    deleted_at DATETIME,
    deleted_by INTEGER,
    
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (deleted_by) REFERENCES users(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(customer_type);
CREATE INDEX IF NOT EXISTS idx_customers_class ON customers(customer_class);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(full_name);
CREATE INDEX IF NOT EXISTS idx_customers_assigned ON customers(assigned_to);
CREATE INDEX IF NOT EXISTS idx_customers_is_deleted ON customers(is_deleted);

-- Trigger cập nhật updated_at
CREATE TRIGGER IF NOT EXISTS update_customers_timestamp
AFTER UPDATE ON customers
BEGIN
    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### Seed Data (Sample)
```sql
INSERT INTO customers (customer_code, customer_type, full_name, id_card, phone, email, address, province, customer_class, source) VALUES
('KH000001', 'individual', N'Nguyễn Văn An', '012345678901', '0901234567', 'an.nguyen@email.com', N'123 Lê Lợi, Quận 1', N'Hồ Chí Minh', 'vip', 'referral'),
('KH000002', 'individual', N'Trần Thị Bình', '023456789012', '0912345678', 'binh.tran@email.com', N'456 Nguyễn Huệ, Quận 1', N'Hồ Chí Minh', 'regular', 'facebook'),
('KH000003', 'business', N'Lê Văn Cường', NULL, '0923456789', 'cuong.le@company.com', N'789 Điện Biên Phủ, Quận 3', N'Hồ Chí Minh', 'potential', 'website');

-- Update company_name cho business customers
UPDATE customers SET company_name = N'Công ty TNHH ABC' WHERE customer_code = 'KH000003';
UPDATE customers SET tax_code = '0123456789' WHERE customer_code = 'KH000003';
```

---

## 3. Backend Logic

### Models
```python
# src/models/customer.py
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class Customer:
    """Model representing a customer."""
    
    # Primary fields
    id: Optional[int] = None
    customer_code: Optional[str] = None
    customer_type: str = "individual"  # individual/business
    
    # Personal info
    full_name: str = ""
    id_card: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None  # Nam/Nữ/Khác
    
    # Business info
    company_name: Optional[str] = None
    tax_code: Optional[str] = None
    business_registration: Optional[str] = None
    
    # Contact info
    phone: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    
    # Address
    address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    
    # Classification
    customer_class: str = "regular"  # regular/potential/vip
    source: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    
    @property
    def is_business(self) -> bool:
        """Check if customer is a business."""
        return self.customer_type == 'business'
    
    @property
    def display_name(self) -> str:
        """Get display name for customer."""
        if self.is_business and self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name
    
    @classmethod
    def from_dict(cls, data: dict) -> Optional["Customer"]:
        """Create Customer from dictionary."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            customer_code=data.get('customer_code'),
            customer_type=data.get('customer_type', 'individual'),
            full_name=data.get('full_name', ''),
            id_card=data.get('id_card'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            company_name=data.get('company_name'),
            tax_code=data.get('tax_code'),
            business_registration=data.get('business_registration'),
            phone=data.get('phone'),
            phone2=data.get('phone2'),
            email=data.get('email'),
            address=data.get('address'),
            province=data.get('province'),
            district=data.get('district'),
            ward=data.get('ward'),
            customer_class=data.get('customer_class', 'regular'),
            source=data.get('source'),
            notes=data.get('notes'),
            assigned_to=data.get('assigned_to'),
            created_by=data.get('created_by'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_deleted=bool(data.get('is_deleted', 0)),
            deleted_at=data.get('deleted_at'),
            deleted_by=data.get('deleted_by')
        )
```

### Repository
```python
# src/repositories/customer_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database.db_helper import DatabaseHelper
from ..models.customer import Customer


class CustomerRepository:
    """Repository for Customer data access."""
    
    def __init__(self, db: DatabaseHelper):
        self.db = db
    
    def _generate_customer_code(self) -> str:
        """Generate next customer code (KH000001, KH000002, ...)."""
        result = self.db.fetch_one(
            "SELECT customer_code FROM customers WHERE customer_code LIKE 'KH%' "
            "ORDER BY customer_code DESC LIMIT 1"
        )
        if result and result['customer_code']:
            last_num = int(result['customer_code'][2:])
            return f"KH{last_num + 1:06d}"
        return "KH000001"
    
    def create(self, customer_data: Dict[str, Any]) -> int:
        """Create new customer with auto-generated code."""
        if not customer_data.get('customer_code'):
            customer_data['customer_code'] = self._generate_customer_code()
        
        query = """
            INSERT INTO customers (
                customer_code, customer_type, full_name, id_card, date_of_birth, gender,
                company_name, tax_code, business_registration,
                phone, phone2, email, address, province, district, ward,
                customer_class, source, notes, assigned_to, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            customer_data['customer_code'],
            customer_data.get('customer_type', 'individual'),
            customer_data['full_name'],
            customer_data.get('id_card'),
            customer_data.get('date_of_birth'),
            customer_data.get('gender'),
            customer_data.get('company_name'),
            customer_data.get('tax_code'),
            customer_data.get('business_registration'),
            customer_data.get('phone'),
            customer_data.get('phone2'),
            customer_data.get('email'),
            customer_data.get('address'),
            customer_data.get('province'),
            customer_data.get('district'),
            customer_data.get('ward'),
            customer_data.get('customer_class', 'regular'),
            customer_data.get('source'),
            customer_data.get('notes'),
            customer_data.get('assigned_to'),
            customer_data.get('created_by')
        )
        return self.db.execute(query, params)
    
    def get_by_id(self, customer_id: int, include_deleted: bool = False) -> Optional[Customer]:
        """Get customer by ID."""
        query = "SELECT * FROM customers WHERE id = ?"
        if not include_deleted:
            query += " AND is_deleted = 0"
        row = self.db.fetch_one(query, (customer_id,))
        return Customer.from_dict(row) if row else None
    
    def get_all(self, customer_type: Optional[str] = None, 
                customer_class: Optional[str] = None,
                include_deleted: bool = False) -> List[Customer]:
        """Get all customers with optional filters."""
        conditions = []
        params = []
        
        if not include_deleted:
            conditions.append("is_deleted = 0")
        if customer_type:
            conditions.append("customer_type = ?")
            params.append(customer_type)
        if customer_class:
            conditions.append("customer_class = ?")
            params.append(customer_class)
        
        query = "SELECT * FROM customers"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"
        
        rows = self.db.fetch_all(query, tuple(params) if params else ())
        return [Customer.from_dict(row) for row in rows if row]
    
    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Update customer."""
        allowed_fields = [
            'full_name', 'id_card', 'date_of_birth', 'gender',
            'company_name', 'tax_code', 'business_registration',
            'phone', 'phone2', 'email', 'address', 'province', 'district', 'ward',
            'customer_class', 'source', 'notes', 'assigned_to'
        ]
        
        fields = []
        params = []
        for field in allowed_fields:
            if field in customer_data:
                fields.append(f"{field} = ?")
                params.append(customer_data[field])
        
        if not fields:
            return False
        
        query = f"UPDATE customers SET {', '.join(fields)} WHERE id = ?"
        params.append(customer_id)
        
        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False
    
    def soft_delete(self, customer_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete customer."""
        query = """
            UPDATE customers SET
                is_deleted = 1,
                deleted_at = ?,
                deleted_by = ?
            WHERE id = ?
        """
        try:
            self.db.execute(query, (datetime.now(), deleted_by, customer_id))
            return True
        except Exception:
            return False
    
    def exists(self, phone: Optional[str] = None, 
               id_card: Optional[str] = None,
               exclude_id: Optional[int] = None) -> bool:
        """Check if customer exists by phone or id_card."""
        conditions = []
        params = []
        
        if phone:
            conditions.append("phone = ?")
            params.append(phone)
        if id_card:
            conditions.append("id_card = ?")
            params.append(id_card)
        
        if not conditions:
            return False
        
        query = f"SELECT 1 FROM customers WHERE ({' OR '.join(conditions)}) AND is_deleted = 0"
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        
        result = self.db.fetch_one(query, tuple(params))
        return result is not None
```

---

## 4. UI Design

### Customer List View
```
┌─────────────────────────────────────────────────────────────────────┐
│  👥 Quản lý khách hàng                                              │
├─────────────────────────────────────────────────────────────────────┤
│  [🔍 Tìm kiếm...] [📋 Cá nhân ▼] [⭐ Tất cả ▼] [➕ Thêm KH]        │
├─────────────────────────────────────────────────────────────────────┤
│  Mã KH    │ Họ tên/Công ty          │ Điện thoại  │ Phân loại     │
│  KH000001 │ Nguyễn Văn An           │ 0901234567  │ ⭐ VIP        │
│  KH000002 │ Trần Thị Bình           │ 0912345678  │ ● Regular     │
│  KH000003 │ ABC Company (Lê Văn C)  │ 0923456789  │ ○ Potential   │
└─────────────────────────────────────────────────────────────────────┘
```

### Customer Dialog (Add/Edit)
```
┌─────────────────────────────────────────────────────────────┐
│  Thêm khách hàng mới                               [✕]     │
├─────────────────────────────────────────────────────────────┤
│  Loại khách hàng: ○ Cá nhân  ● Doanh nghiệp               │
│                                                             │
│  THÔNG TIN CÁ NHÂN                                          │
│  Họ tên *          [____________________]                   │
│  CMND/CCCD         [____________________]                   │
│  Ngày sinh         [____/____/________]                     │
│  Giới tính         ○ Nam  ○ Nữ  ○ Khác                      │
│                                                             │
│  THÔNG TIN DOANH NGHIỆP (hiện khi chọn Doanh nghiệp)        │
│  Tên công ty *     [____________________]                   │
│  Mã số thuế        [____________________]                   │
│                                                             │
│  THÔNG TIN LIÊN HỆ                                          │
│  Điện thoại *      [____________________]                   │
│  Email             [____________________]                   │
│  Địa chỉ           [____________________]                   │
│                                                             │
│  PHÂN LOẠI                                                  │
│  Nguồn KH          [Facebook ▼]                             │
│  Nhân viên phụ trách [Chọn NV ▼]                            │
│  Ghi chú           [                    ]                   │
│                                                             │
│           [Hủy]              [💾 Lưu]                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Testing

### Unit Tests
```python
# tests/test_customer_repository.py
import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.customer_repository import CustomerRepository
from src.models.customer import Customer


class TestCustomerRepository(unittest.TestCase):
    """Tests for customer repository."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseHelper(self.db_path)
        self.repo = CustomerRepository(self.db)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_individual_customer(self):
        """Test creating individual customer."""
        customer_id = self.repo.create({
            'customer_type': 'individual',
            'full_name': 'Nguyễn Văn Test',
            'phone': '0901234567',
            'customer_class': 'regular'
        })
        self.assertIsNotNone(customer_id)
        
        customer = self.repo.get_by_id(customer_id)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.full_name, 'Nguyễn Văn Test')
        self.assertEqual(customer.customer_type, 'individual')
        self.assertTrue(customer.customer_code.startswith('KH'))
    
    def test_create_business_customer(self):
        """Test creating business customer."""
        customer_id = self.repo.create({
            'customer_type': 'business',
            'full_name': 'Người đại diện',
            'company_name': 'Công ty Test',
            'tax_code': '0123456789',
            'phone': '0901234568'
        })
        self.assertIsNotNone(customer_id)
        
        customer = self.repo.get_by_id(customer_id)
        self.assertEqual(customer.customer_type, 'business')
        self.assertEqual(customer.company_name, 'Công ty Test')
    
    def test_customer_code_generation(self):
        """Test auto-generated customer codes."""
        id1 = self.repo.create({'full_name': 'KH 1', 'phone': '0911111111'})
        id2 = self.repo.create({'full_name': 'KH 2', 'phone': '0922222222'})
        
        customer1 = self.repo.get_by_id(id1)
        customer2 = self.repo.get_by_id(id2)
        
        self.assertEqual(customer1.customer_code, 'KH000001')
        self.assertEqual(customer2.customer_code, 'KH000002')
    
    def test_exists_by_phone(self):
        """Test checking duplicate phone."""
        self.repo.create({'full_name': 'Test', 'phone': '0901234567'})
        self.assertTrue(self.repo.exists(phone='0901234567'))
        self.assertFalse(self.repo.exists(phone='0999999999'))
```

---

## 6. Definition of Done

- [ ] Bảng `customers` được tạo với đầy đủ fields
- [ ] Model `Customer` với đầy đủ thuộc tính
- [ ] Repository với CRUD operations
- [ ] Auto-generate customer code (KH000001, KH000002...)
- [ ] Phân biệt khách hàng cá nhân và doanh nghiệp
- [ ] UI list view hiển thị danh sách khách hàng
- [ ] UI dialog thêm/sửa khách hàng
- [ ] Unit tests pass (≥ 80% coverage)
- [ ] Code committed: `feat: customer management initial`

---

## 7. Git Commit

```bash
# Commit message
feat: customer management initial

- Thêm bảng customers với đầy đủ fields
- Tạo Customer model với phân loại cá nhân/doanh nghiệp
- Tạo CustomerRepository với CRUD và auto-generate code
- Thêm UI components cho list view và dialog
- Thêm unit tests cho repository

Closes sprint-2.1
```
