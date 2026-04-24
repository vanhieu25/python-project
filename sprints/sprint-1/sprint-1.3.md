# Sprint-1.3: Car Search & Filter

**Module**: 🚗 Car Management  
**Mức độ ưu tiên**: Core  
**Blocked by**: Sprint-1.2 (Car CRUD Operations)  
**Ước lượng**: 2 ngày

---

## 1. Xác định Feature

### Mô tả
Nâng cao chức năng tìm kiếm và lọc xe với nhiều tiêu chí, hỗ trợ tìm kiếm nâng cao và hiển thị kết quả nhanh chóng.

### Yêu cầu
- Tìm kiếm theo từ khóa (VIN, biển số, hãng, model)
- Lọc theo nhiều tiêu chí: hãng xe, năm SX, khoảng giá, trạng thái, màu sắc
- Sắp xếp kết quả theo nhiều cột
- Pagination cho danh sách lớn
- Tìm kiếm real-time với debounce

### Dependencies
- Sprint-1.2: Cần CRUD operations hoàn chỉnh

---

## 2. Database

### Indexes
```sql
-- Thêm indexes cho tìm kiếm
CREATE INDEX IF NOT EXISTS idx_cars_brand_model ON cars(brand, model);
CREATE INDEX IF NOT EXISTS idx_cars_price ON cars(selling_price);
CREATE INDEX IF NOT EXISTS idx_cars_status_year ON cars(status, year);
CREATE INDEX IF NOT EXISTS idx_cars_color ON cars(color);

-- Full-text search index (SQLite FTS)
CREATE VIRTUAL TABLE IF NOT EXISTS cars_fts USING fts5(
    vin,
    license_plate,
    brand,
    model,
    description,
    content='cars',
    content_rowid='id'
);

-- Trigger để sync FTS index
CREATE TRIGGER IF NOT EXISTS cars_ai AFTER INSERT ON cars BEGIN
    INSERT INTO cars_fts(rowid, vin, license_plate, brand, model, description)
    VALUES (new.id, new.vin, new.license_plate, new.brand, new.model, new.description);
END;

CREATE TRIGGER IF NOT EXISTS cars_ad AFTER DELETE ON cars BEGIN
    INSERT INTO cars_fts(cars_fts, rowid, vin, license_plate, brand, model, description)
    VALUES ('delete', old.id, old.vin, old.license_plate, old.brand, old.model, old.description);
END;

CREATE TRIGGER IF NOT EXISTS cars_au AFTER UPDATE ON cars BEGIN
    INSERT INTO cars_fts(cars_fts, rowid, vin, license_plate, brand, model, description)
    VALUES ('delete', old.id, old.vin, old.license_plate, old.brand, old.model, old.description);
    INSERT INTO cars_fts(rowid, vin, license_plate, brand, model, description)
    VALUES (new.id, new.vin, new.license_plate, new.brand, new.model, new.description);
END;
```

---

## 3. Backend Logic

### Search Repository
```python
# src/repositories/car_search_repository.py
from typing import List, Optional, Dict, Any, Tuple
from ..database.db_helper import DatabaseHelper
from ..models.car import Car

class CarSearchFilter:
    """Filter criteria for car search."""

    def __init__(self):
        self.keyword: Optional[str] = None
        self.brands: List[str] = []
        self.models: List[str] = []
        self.year_from: Optional[int] = None
        self.year_to: Optional[int] = None
        self.price_from: Optional[float] = None
        self.price_to: Optional[float] = None
        self.colors: List[str] = []
        self.statuses: List[str] = []
        self.transmissions: List[str] = []
        self.fuel_types: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'keyword': self.keyword,
            'brands': self.brands,
            'models': self.models,
            'year_from': self.year_from,
            'year_to': self.year_to,
            'price_from': self.price_from,
            'price_to': self.price_to,
            'colors': self.colors,
            'statuses': self.statuses,
            'transmissions': self.transmissions,
            'fuel_types': self.fuel_types
        }


class CarSearchRepository:
    """Repository for advanced car search."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def search(self, filter_criteria: CarSearchFilter,
               sort_by: str = 'created_at',
               sort_order: str = 'DESC',
               page: int = 1,
               per_page: int = 20) -> Tuple[List[Car], int]:
        """Search cars with filters.

        Args:
            filter_criteria: Search filter criteria
            sort_by: Column to sort by
            sort_order: ASC or DESC
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            Tuple of (list of cars, total count)
        """
        # Build WHERE clause
        conditions = ["is_deleted = 0"]
        params = []

        # Keyword search (VIN, license plate, brand, model)
        if filter_criteria.keyword:
            keyword = f"%{filter_criteria.keyword}%"
            conditions.append("""(
                vin LIKE ? OR
                license_plate LIKE ? OR
                brand LIKE ? OR
                model LIKE ?
            )""")
            params.extend([keyword, keyword, keyword, keyword])

        # Brand filter
        if filter_criteria.brands:
            placeholders = ','.join('?' * len(filter_criteria.brands))
            conditions.append(f"brand IN ({placeholders})")
            params.extend(filter_criteria.brands)

        # Model filter
        if filter_criteria.models:
            placeholders = ','.join('?' * len(filter_criteria.models))
            conditions.append(f"model IN ({placeholders})")
            params.extend(filter_criteria.models)

        # Year range
        if filter_criteria.year_from:
            conditions.append("year >= ?")
            params.append(filter_criteria.year_from)
        if filter_criteria.year_to:
            conditions.append("year <= ?")
            params.append(filter_criteria.year_to)

        # Price range
        if filter_criteria.price_from:
            conditions.append("selling_price >= ?")
            params.append(filter_criteria.price_from)
        if filter_criteria.price_to:
            conditions.append("selling_price <= ?")
            params.append(filter_criteria.price_to)

        # Color filter
        if filter_criteria.colors:
            placeholders = ','.join('?' * len(filter_criteria.colors))
            conditions.append(f"color IN ({placeholders})")
            params.extend(filter_criteria.colors)

        # Status filter
        if filter_criteria.statuses:
            placeholders = ','.join('?' * len(filter_criteria.statuses))
            conditions.append(f"status IN ({placeholders})")
            params.extend(filter_criteria.statuses)

        # Transmission filter
        if filter_criteria.transmissions:
            placeholders = ','.join('?' * len(filter_criteria.transmissions))
            conditions.append(f"transmission IN ({placeholders})")
            params.extend(filter_criteria.transmissions)

        # Fuel type filter
        if filter_criteria.fuel_types:
            placeholders = ','.join('?' * len(filter_criteria.fuel_types))
            conditions.append(f"fuel_type IN ({placeholders})")
            params.extend(filter_criteria.fuel_types)

        # Build query
        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"SELECT COUNT(*) as count FROM cars WHERE {where_clause}"
        count_result = self.db.fetch_one(count_query, tuple(params))
        total_count = count_result['count'] if count_result else 0

        # Main query
        allowed_sort_columns = [
            'vin', 'license_plate', 'brand', 'model', 'year',
            'selling_price', 'purchase_price', 'created_at', 'status'
        ]
        if sort_by not in allowed_sort_columns:
            sort_by = 'created_at'

        sort_order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'

        query = f"""
            SELECT * FROM cars
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """
        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        rows = self.db.fetch_all(query, tuple(params))
        cars = [Car.from_dict(row) for row in rows if row]

        return cars, total_count

    def fts_search(self, keyword: str) -> List[Car]:
        """Full-text search using FTS5.

        Args:
            keyword: Search keyword

        Returns:
            List of matching cars
        """
        query = """
            SELECT c.* FROM cars c
            JOIN cars_fts fts ON c.id = fts.rowid
            WHERE cars_fts MATCH ?
            AND c.is_deleted = 0
            ORDER BY rank
        """
        rows = self.db.fetch_all(query, (keyword,))
        return [Car.from_dict(row) for row in rows if row]

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options.

        Returns:
            Dictionary of filter options
        """
        return {
            'brands': self._get_distinct_values('brand'),
            'models': self._get_distinct_values('model'),
            'colors': self._get_distinct_values('color'),
            'statuses': self._get_distinct_values('status'),
            'transmissions': self._get_distinct_values('transmission'),
            'fuel_types': self._get_distinct_values('fuel_type'),
            'years': self._get_distinct_values('year', numeric=True),
        }

    def _get_distinct_values(self, column: str,
                            numeric: bool = False) -> List:
        """Get distinct values for a column."""
        order = f"CAST({column} AS INTEGER)" if numeric else column
        query = f"""
            SELECT DISTINCT {column} as value
            FROM cars
            WHERE {column} IS NOT NULL AND is_deleted = 0
            ORDER BY {order}
        """
        rows = self.db.fetch_all(query)
        return [row['value'] for row in rows if row['value']]

    def get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """Get min and max selling prices."""
        query = """
            SELECT
                MIN(selling_price) as min_price,
                MAX(selling_price) as max_price
            FROM cars
            WHERE is_deleted = 0 AND selling_price IS NOT NULL
        """
        result = self.db.fetch_one(query)
        return (
            result['min_price'] if result else None,
            result['max_price'] if result else None
        )
```

### Search Service
```python
# src/services/car_search_service.py
from typing import List, Optional, Dict, Any, Tuple
from ..repositories.car_search_repository import (
    CarSearchRepository, CarSearchFilter
)
from ..models.car import Car


class CarSearchService:
    """Service for car search operations."""

    def __init__(self, search_repository: CarSearchRepository):
        self.search_repo = search_repository

    def quick_search(self, keyword: str,
                     page: int = 1,
                     per_page: int = 20) -> Tuple[List[Car], int]:
        """Quick search by keyword only.

        Args:
            keyword: Search keyword
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter()
        filter_criteria.keyword = keyword
        return self.search_repo.search(filter_criteria, page=page, per_page=per_page)

    def advanced_search(self,
                        keyword: Optional[str] = None,
                        brands: List[str] = None,
                        models: List[str] = None,
                        year_from: Optional[int] = None,
                        year_to: Optional[int] = None,
                        price_from: Optional[float] = None,
                        price_to: Optional[float] = None,
                        colors: List[str] = None,
                        statuses: List[str] = None,
                        transmissions: List[str] = None,
                        fuel_types: List[str] = None,
                        sort_by: str = 'created_at',
                        sort_order: str = 'DESC',
                        page: int = 1,
                        per_page: int = 20
                        ) -> Tuple[List[Car], int]:
        """Advanced search with multiple filters.

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter()
        filter_criteria.keyword = keyword
        filter_criteria.brands = brands or []
        filter_criteria.models = models or []
        filter_criteria.year_from = year_from
        filter_criteria.year_to = year_to
        filter_criteria.price_from = price_from
        filter_criteria.price_to = price_to
        filter_criteria.colors = colors or []
        filter_criteria.statuses = statuses or []
        filter_criteria.transmissions = transmissions or []
        filter_criteria.fuel_types = fuel_types or []

        return self.search_repo.search(
            filter_criteria,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

    def get_filter_options(self) -> Dict[str, List]:
        """Get available filter options for UI."""
        return self.search_repo.get_filter_options()

    def get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """Get min/max price for price slider."""
        return self.search_repo.get_price_range()

    def find_similar_cars(self, car_id: int,
                          limit: int = 5) -> List[Car]:
        """Find cars similar to a given car (same brand/model)."""
        # Implementation would fetch the car first, then search
        pass
```

---

## 4. UI Design

### Search & Filter Panel
```
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 Tìm kiếm xe                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 🔍 Nhập VIN, biển số, hãng xe...                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  [Bộ lọc ▼]                                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │ Hãng xe ▼    │ │ Năm SX ▼     │ │ Giá ▼        │ │ Trạng thái│  │
│  │ [ ] Toyota   │ │ [ ] 2024     │ │ 0 - 2 tỷ     │ │ [x] Còn   │  │
│  │ [x] Honda    │ │ [ ] 2023     │ │ [━━━━━●━━━]  │ │ [ ] Đã bán│  │
│  │ [ ] Mazda    │ │ [x] 2022     │ │              │ │           │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └───────────┘  │
│  [Xóa bộ lọc]                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  Tìm thấy 15 xe │ Sắp xếp: [Ngày nhập ▼]                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬──────┬───────┬──────────┬────────┐        │
│  │ VIN      │ Biển số  │ Hãng │ Model │ Giá bán  │ Tr.thái│        │
│  ├──────────┼──────────┼──────┼───────┼──────────┼────────┤        │
│  │ 1HGCM... │ 51A-12345│ Honda│ Civic │ 850M     │ 🟢Còn  │        │
│  │ JTDBU... │ 51A-67890│Toyota│ Camry │ 1.35B    │ 🟢Còn  │        │
│  └──────────┴──────────┴──────┴───────┴──────────┴────────┘        │
│  Trang 1/2 [❮] [1] [2] [❯]                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Components
1. **Search Box**: Real-time search with debounce (300ms)
2. **Filter Panel**: Collapsible panel với nhiều filter options
3. **Price Slider**: Range slider cho khoảng giá
4. **Checkbox Groups**: Multi-select cho brands, models, colors
5. **Sort Dropdown**: Chọn cột sắp xếp
6. **Pagination**: Page navigation với page size selector

---

## 5. Testing

### UI Acceptance Tests
```python
# tests/test_car_search.py
import unittest
import tempfile
import shutil
import os

from src.database.db_helper import DatabaseHelper
from src.repositories.car_repository import CarRepository
from src.repositories.car_search_repository import CarSearchRepository
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
        """Create test car data."""
        cars = [
            {"vin": "1HGCM82633A111111", "brand": "Toyota", "model": "Camry",
             "year": 2023, "selling_price": 1200000000, "color": "Trắng",
             "status": "available"},
            {"vin": "1HGCM82633A222222", "brand": "Honda", "model": "Civic",
             "year": 2023, "selling_price": 850000000, "color": "Đen",
             "status": "available"},
            {"vin": "1HGCM82633A333333", "brand": "Honda", "model": "City",
             "year": 2022, "selling_price": 600000000, "color": "Trắng",
             "status": "sold"},
            {"vin": "1HGCM82633A444444", "brand": "Mazda", "model": "3",
             "year": 2022, "selling_price": 750000000, "color": "Đỏ",
             "status": "available"},
        ]
        for car_data in cars:
            self.car_repo.create(car_data)

    def test_keyword_search(self):
        """Test searching by keyword."""
        cars, total = self.search_service.quick_search("Honda")
        self.assertEqual(total, 2)  # 2 Honda cars

    def test_brand_filter(self):
        """Test filtering by brand."""
        cars, total = self.search_service.advanced_search(brands=["Toyota"])
        self.assertEqual(total, 1)
        self.assertEqual(cars[0].brand, "Toyota")

    def test_price_range_filter(self):
        """Test filtering by price range."""
        cars, total = self.search_service.advanced_search(
            price_from=700000000,
            price_to=1000000000
        )
        self.assertEqual(total, 2)  # Civic và Mazda 3

    def test_multiple_filters(self):
        """Test combining multiple filters."""
        cars, total = self.search_service.advanced_search(
            brands=["Honda"],
            year_from=2023,
            statuses=["available"]
        )
        self.assertEqual(total, 1)  # Chỉ Honda Civic 2023 available

    def test_pagination(self):
        """Test pagination."""
        cars, total = self.search_service.advanced_search(
            page=1, per_page=2
        )
        self.assertEqual(len(cars), 2)
        self.assertEqual(total, 4)  # Total 4 cars

    def test_sorting(self):
        """Test sorting results."""
        cars, _ = self.search_service.advanced_search(
            sort_by="selling_price",
            sort_order="DESC"
        )
        # First should be most expensive
        self.assertEqual(cars[0].brand, "Toyota")  # 1.2B

    def test_get_filter_options(self):
        """Test getting filter options."""
        options = self.search_service.get_filter_options()
        self.assertIn("Toyota", options['brands'])
        self.assertIn("Honda", options['brands'])
        self.assertIn(2023, options['years'])
```

---

## 6. Definition of Done

- [ ] Full-text search with FTS5 enabled
- [ ] Advanced filter UI with all criteria
- [ ] Real-time search with debounce
- [ ] Pagination working correctly
- [ ] Sorting by multiple columns
- [ ] Filter options dynamically loaded
- [ ] UI acceptance tests pass (Chrome, Firefox)
- [ ] Performance: Search < 500ms for 10k records
- [ ] Code committed: `feat: tìm kiếm và lọc xe`

---

## 7. Git Commit

```bash
# Files to commit
- src/repositories/car_search_repository.py (mới)
- src/services/car_search_service.py (mới)
- src/ui/cars/search_panel.py (mới)
- src/ui/cars/filter_dialog.py (mới)
- src/database/schema.sql (cập nhật - FTS indexes)
- tests/test_car_search.py (mới)

# Commit message
feat: tìm kiếm và lọc xe

- Thêm full-text search với FTS5
- Triển khai bộ lọc nâng cao
- Thêm tìm kiếm real-time với debounce
- Thêm phân trang và sắp xếp
- Tạo các UI components cho tìm kiếm
- Thêm UI acceptance tests
```
