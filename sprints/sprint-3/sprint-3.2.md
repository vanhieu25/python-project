# Sprint 3.2: Contract CRUD Operations

> **Module**: 3. CONTRACT MANAGEMENT — Contract CRUD Operations  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 2 ngày  
> **Blocked by**: Sprint-3.1 (Contract Management Initial)  
> **Git Commit**: `feat: CRUD operations cho quản lý hợp đồng`

---

## Mục Tiêu

Xây dựng tầng Business Logic (Service Layer) và Presentation Layer cho quản lý hợp đồng bao gồm: tạo hợp đồng mới, tìm kiếm, cập nhật, xóa hợp đồng, và quản lý danh sách hợp đồng.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define requirements
- [ ] Identify dependencies: Sprint-3.1
- [ ] Review contract workflow (draft → pending → approved → signed → paid → delivered)
- [ ] Assign cho developer

### 2. Business Logic Layer (src/services/contract_service.py)

- [ ] **ContractService Class**
  - `__init__(contract_repo, customer_repo, car_repo)`
  - Inject dependencies vào service

- [ ] **Create Contract**
  - `create_contract(data: dict, created_by: int) -> Result[Contract]`
  - Validate customer tồn tại và có thể tạo hợp đồng
  - Validate car tồn tại và status = 'available'
  - Copy customer info vào contract (snapshot pattern)
  - Copy car info vào contract (snapshot pattern)
  - Tính toán total_amount = car_price - discount_amount
  - Tính toán final_amount = total_amount + vat_amount
  - Tạo contract với status = 'draft'

- [ ] **Get Contract**
  - `get_contract_by_id(contract_id: int) -> Optional[Contract]`
  - `get_contract_by_code(contract_code: str) -> Optional[Contract]`
  - Load đầy đủ items và payments khi get detail

- [ ] **Search Contracts**
  - `search_contracts(filters: dict) -> List[Contract]`
  - Filter by: customer_name, customer_phone, car_brand, car_model
  - Filter by: status, date_from, date_to
  - Filter by: created_by (contracts của tôi)
  - Pagination: page, per_page

- [ ] **Update Contract**
  - `update_contract(contract_id: int, data: dict, updated_by: int) -> Result[bool]`
  - Chỉ cho phép update khi status = 'draft'
  - Validate permission (creator hoặc admin)
  - Không cho update: customer_id, car_id, contract_code

- [ ] **Delete Contract**
  - `delete_contract(contract_id: int, deleted_by: int) -> Result[bool]`
  - Chỉ cho phép delete khi status = 'draft'
  - Validate permission (creator hoặc admin)

- [ ] **Add/Remove Items**
  - `add_item_to_contract(contract_id: int, item_data: dict) -> Result[int]`
  - `remove_item_from_contract(contract_id: int, item_id: int) -> Result[bool]`
  - Tự động cập nhật total_amount khi thêm/xóa items

- [ ] **Calculate Totals**
  - `calculate_totals(contract_id: int) -> Result[dict]`
  - Tính lại tất cả các giá trị tiền tệ
  - Cập nhật vào database

- [ ] **Unit Tests**
  - `tests/test_contract_service.py`
  - Test create_contract (success và validation errors)
  - Test update_contract (chỉ draft được update)
  - Test delete_contract (chỉ draft được delete)
  - Test search with filters

### 3. Presentation Layer (src/views/contracts/)

- [ ] **Contract List View** (`contract_list_view.py`)
  - Hiển thị danh sách hợp đồng dạng bảng
  - Columns: Mã HĐ, Khách hàng, Xe, Tổng tiền, Trạng thái, Ngày tạo
  - Filter dropdown: Tất cả, Draft, Pending, Approved, Signed, Paid, Delivered, Cancelled
  - Search box: Tìm theo tên KH, số điện thoại, mã HĐ
  - Button: "Tạo hợp đồng mới"
  - Double-click để mở detail
  - Pagination controls

- [ ] **Contract Create View** (`contract_create_view.py`)
  - Step 1: Chọn khách hàng (search customer)
  - Step 2: Chọn xe (search available car)
  - Step 3: Nhập thông tin giá cả và thanh toán
  - Step 4: Xem trước và xác nhận
  - Validation realtime
  - Button: Back, Next, Cancel, Save as Draft

- [ ] **Contract Detail View** (`contract_detail_view.py`)
  - Tab "Thông tin chung": Thông tin KH, xe, giá cả
  - Tab "Phụ kiện & Dịch vụ": Danh sách items
  - Tab "Thanh toán": Lịch sử thanh toán
  - Tab "Lịch sử": Audit log các thay đổi
  - Buttons: Edit (nếu draft), Delete (nếu draft), Print, Approve, Sign

- [ ] **Contract Search Dialog** (`contract_search_dialog.py`)
  - Advanced search với nhiều filter
  - Date range picker
  - Customer autocomplete
  - Car brand/model dropdown

- [ ] **Contract Dashboard Widget** (`contract_dashboard.py`)
  - Widget hiển thị trên dashboard chính
  - Số hợp đồng theo trạng thái
  - Top 5 hợp đồng mới nhất
  - Tổng doanh thu tháng này

### 4. Integration

- [ ] **Main App Integration**
  - Thêm "Quản lý hợp đồng" vào menu chính
  - Icon: document/file icon
  - Shortcut: Ctrl+Shift+C

- [ ] **Customer Context Menu**
  - Thêm "Tạo hợp đồng" vào context menu của khách hàng
  - Auto-fill customer info

- [ ] **Car Context Menu**
  - Thêm "Tạo hợp đồng" vào context menu của xe
  - Auto-fill car info (chỉ khi status = available)

### 5. Testing & Documentation

- [ ] **Unit Tests**
  - Test coverage > 80% cho ContractService
  - Test all validation rules
  - Test permission checks

- [ ] **UI Tests**
  - Test create contract flow
  - Test search và filter
  - Test pagination

- [ ] **Update Documentation**
  - `docs/CONTRACT_MANAGEMENT.md`: Hướng dẫn sử dụng
  - Update `docs/FEATURE_LIST.md` đánh dấu features đã xong

---

## Thiết Kế Chi Tiết

### ContractService Interface

```python
class ContractService:
    def __init__(self, contract_repo, customer_repo, car_repo, user_repo):
        self.contract_repo = contract_repo
        self.customer_repo = customer_repo
        self.car_repo = car_repo
        self.user_repo = user_repo

    def create_contract(self, data: dict, created_by: int) -> Result[Contract]:
        """Tạo hợp đồng mới."""
        pass

    def get_contract_detail(self, contract_id: int) -> Optional[Contract]:
        """Lấy chi tiết hợp đồng kèm items và payments."""
        pass

    def search_contracts(
        self,
        filters: dict = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResult[Contract]:
        """Tìm kiếm hợp đồng với filter và pagination."""
        pass

    def update_contract(
        self,
        contract_id: int,
        data: dict,
        updated_by: int
    ) -> Result[bool]:
        """Cập nhật hợp đồng (chỉ draft)."""
        pass

    def delete_contract(self, contract_id: int, deleted_by: int) -> Result[bool]:
        """Xóa hợp đồng (chỉ draft)."""
        pass

    def add_item(self, contract_id: int, item_data: dict) -> Result[int]:
        """Thêm item vào hợp đồng."""
        pass

    def remove_item(self, contract_id: int, item_id: int) -> Result[bool]:
        """Xóa item khỏi hợp đồng."""
        pass

    def calculate_totals(self, contract_id: int) -> Result[dict]:
        """Tính lại các giá trị tiền tệ."""
        pass
```

### Search Filters

```python
{
    "customer_name": str,          # Tìm theo tên KH (LIKE)
    "customer_phone": str,         # Tìm theo SĐT
    "car_brand": str,              # Filter theo hãng xe
    "car_model": str,              # Filter theo model
    "status": str,                 # Filter theo status
    "date_from": date,             # Từ ngày
    "date_to": date,               # Đến ngày
    "created_by": int,             # Contracts của user này
    "min_amount": float,           # Giá trị tối thiểu
    "max_amount": float            # Giá trị tối đa
}
```

### Status Flow

```
draft → pending → approved → signed → paid → delivered
  ↓       ↓          ↓          ↓        ↓
cancelled (có thể hủy từ bất kỳ status nào trước delivered)
```

---

## Files Cần Tạo/Cập Nhật

### New Files
```
src/services/contract_service.py
tests/test_contract_service.py
src/views/contracts/contract_list_view.py
src/views/contracts/contract_create_view.py
src/views/contracts/contract_detail_view.py
src/views/contracts/contract_search_dialog.py
src/views/contracts/contract_dashboard.py
src/views/contracts/__init__.py
docs/CONTRACT_MANAGEMENT.md
```

### Files to Update
```
src/services/__init__.py
src/views/main_menu.py (hoặc tương đương)
docs/FEATURE_LIST.md
```

---

## Tiêu Chí Hoàn Thành

- [ ] ContractService đầy đủ các methods với validation
- [ ] Tất cả CRUD operations hoạt động đúng
- [ ] UI cho list, create, detail đã hoàn thiện
- [ ] Search và filter hoạt động
- [ ] Pagination hoạt động
- [ ] Unit tests pass (>80% coverage)
- [ ] Documentation đã cập nhật
- [ ] Git commit: `feat: CRUD operations cho quản lý hợp đồng`

---

## Lưu Ý Kỹ Thuật

1. **Snapshot Pattern**: KHÔNG dùng foreign key trực tiếp đến customers/cars cho display. Copy thông tin vào contract.

2. **Status Validation**: Luôn kiểm tra status trước khi cho phép operation.

3. **Permission**: Chỉ creator, manager, hoặc admin mới có quyền sửa/xóa.

4. **Auto-calculate**: Giá trị tiền tệ phải được tính toán tự động, không để user nhập trực tiếp total, final_amount.

5. **Soft Delete**: Không xóa cứng hợp đồng, chỉ chuyển sang status 'cancelled'.

6. **Transaction**: Các operations liên quan đến nhiều bảng phải dùng transaction.
