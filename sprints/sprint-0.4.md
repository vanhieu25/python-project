# Sprint 0.4: Employee KPI

> **Module**: 0. FOUNDATION — Employee & Auth  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 3 ngày  
> **Blocked by**: Sprint-0.1 (Employee Management)  
> **Git Commit**: `feat: employee KPI`

---

## Mục Tiêu

Xây dựng hệ thống theo dõi và đánh giá hiệu suất nhân viên (KPI - Key Performance Indicators), bao gồm số xe bán được, doanh thu tạo ra, và dashboard hiển thị.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define requirements
- [ ] Identify dependencies: Sprint-0.1
- [ ] Plan database schema (KPI tracking fields)
- [ ] Define KPI metrics
- [ ] Assign cho developer

### 2. Database

- [ ] Thêm fields vào bảng `users` cho KPI
  - total_sales (tổng số xe đã bán)
  - total_revenue (tổng doanh thu)
  - monthly_sales_target (mục tiêu tháng)
  - monthly_revenue_target (mục tiêu doanh thu)
  - performance_score (điểm hiệu suất)
- [ ] Tạo bảng `kpi_records` (lịch sử KPI)
  - id, user_id, period (tháng/năm)
  - cars_sold, revenue_generated
  - target_cars, target_revenue
  - achievement_rate (% hoàn thành)
- [ ] Tạo bảng `kpi_targets` (mục tiêu KPI)
  - id, user_id, period_type (monthly/quarterly/yearly)
  - target_period, sales_target, revenue_target
  - created_by, created_at
- [ ] Add indexes
  - INDEX on kpi_records.user_id
  - INDEX on kpi_records.period
  - INDEX on kpi_targets.user_id
- [ ] Test schema integrity

### 3. Backend Logic

- [ ] **KPI Models**
  - `KPIRecord` dataclass
  - `KPITarget` dataclass
- [ ] **KPI Repository**
  - `KPIRepository`:
    - `get_kpi_by_user(user_id, period)`
    - `get_kpi_history(user_id, start_date, end_date)`
    - `create_kpi_record(data)`
    - `update_kpi_targets(user_id, targets)`
    - `get_top_performers(limit, period)`
- [ ] **KPI Service**
  - `KPIService`:
    - `calculate_monthly_kpi(user_id, month, year)`
    - `calculate_achievement_rate(actual, target)`
    - `get_performance_ranking(period)`
    - `compare_with_peers(user_id, period)`
    - `generate_kpi_report(user_id, start_date, end_date)`
    - `auto_update_kpi_from_contracts()`
- [ ] **Performance Calculation**
  - Công thức tính điểm hiệu suất
  - Weighted score (số xe: 40%, doanh thu: 60%)
  - Achievement rate calculation
- [ ] Handle errors appropriately

### 4. UI Design

- [ ] **Wireframes**
  - KPI Dashboard Overview
  - Individual KPI Detail View
  - KPI Comparison Chart
  - Target Setting Form
- [ ] **Implementation**
  - `KPIDashboardScreen`
    - Cards hiển thị tổng quan
    - Charts (bar chart, line chart, pie chart)
    - Top performers list
    - My KPI section
  - `KPITrendChart`
    - Biểu đồ xu hướng theo thời gian
    - So sánh actual vs target
  - `PerformanceRankingWidget`
    - Bảng xếp hạng nhân viên
    - Highlight vị trí hiện tại
  - `KPIDetailDialog`
    - Chi tiết KPI theo tháng/quý/năm
    - Breakdown theo loại xe, khách hàng
  - `TargetSettingDialog` (Manager/Admin only)
    - Form set mục tiêu cho nhân viên
    - Bulk set targets
- [ ] **Interactions**
    - Click vào chart để xem chi tiết
    - Filter theo thời gian
    - Export KPI report
    - Drill-down từ summary → detail
- [ ] **Responsiveness**
    - Charts responsive
    - Table scrollable trên mobile

### 5. Testing

- [ ] **Unit Tests (≥ 80% coverage)**
    - Test KPI calculation formulas
    - Test achievement rate calculation
    - Test ranking algorithm
- [ ] **Integration Tests**
    - Test auto-update từ contracts
    - Test KPI aggregation
    - Test comparison with peers
- [ ] **Performance Calculation Test**
    - Test edge cases (target = 0)
    - Test negative values
    - Test very large numbers
- [ ] **Edge Cases**
    - Nhân viên mới chưa có dữ liệu
    - Tháng không có hợp đồng nào
    - Target thay đổi giữa tháng
    - So sánh với nhân viên đã nghỉ việc

### 6. Definition of Done

- [ ] Unit test coverage ≥ 80%
- [ ] Tất cả integration test pass
- [ ] Code review ≥ 1 người approve
- [ ] Không còn bug Critical/Blocker
- [ ] Deploy lên staging thành công
- [ ] README / comment cập nhật

### 7. Git Commit

- [ ] Commit message đúng convention: `feat: employee KPI`
- [ ] Push lên remote branch
- [ ] Tạo Pull Request nếu làm theo nhánh

---

## Chi Tiết Kỹ Thuật

### Database Schema

```sql
-- Thêm fields vào bảng users
ALTER TABLE users ADD COLUMN total_sales INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN total_revenue DECIMAL(15,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN monthly_sales_target INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN monthly_revenue_target DECIMAL(15,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN performance_score DECIMAL(5,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN last_kpi_update DATETIME;

-- Bảng kpi_records
CREATE TABLE kpi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    period_type VARCHAR(20) DEFAULT 'monthly', -- monthly, quarterly, yearly
    period_value VARCHAR(10) NOT NULL, -- '2024-01', '2024-Q1', '2024'
    
    -- Số liệu thực tế
    cars_sold INTEGER DEFAULT 0,
    revenue_generated DECIMAL(15,2) DEFAULT 0,
    new_customers INTEGER DEFAULT 0,
    contracts_signed INTEGER DEFAULT 0,
    
    -- Mục tiêu
    target_cars INTEGER DEFAULT 0,
    target_revenue DECIMAL(15,2) DEFAULT 0,
    
    -- Tỷ lệ hoàn thành
    cars_achievement_rate DECIMAL(5,2) DEFAULT 0,
    revenue_achievement_rate DECIMAL(5,2) DEFAULT 0,
    overall_score DECIMAL(5,2) DEFAULT 0,
    
    -- Xếp hạng
    period_rank INTEGER,
    total_staff INTEGER,
    
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, period_type, period_value)
);

-- Bảng kpi_targets
CREATE TABLE kpi_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    period_type VARCHAR(20) DEFAULT 'monthly',
    target_period VARCHAR(10) NOT NULL, -- '2024-01', '2024'
    
    sales_target INTEGER DEFAULT 0,
    revenue_target DECIMAL(15,2) DEFAULT 0,
    new_customer_target INTEGER DEFAULT 0,
    
    description TEXT,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE(user_id, period_type, target_period)
);

-- Indexes
CREATE INDEX idx_kpi_user ON kpi_records(user_id);
CREATE INDEX idx_kpi_period ON kpi_records(period_value);
CREATE INDEX idx_kpi_type_period ON kpi_records(period_type, period_value);
CREATE INDEX idx_kpi_targets_user ON kpi_targets(user_id);
CREATE INDEX idx_kpi_rank ON kpi_records(period_rank);
```

### KPI Service (Python)

```python
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict
from decimal import Decimal

@dataclass
class KPIRecord:
    id: int
    user_id: int
    period_type: str
    period_value: str
    cars_sold: int
    revenue_generated: Decimal
    new_customers: int
    contracts_signed: int
    target_cars: int
    target_revenue: Decimal
    cars_achievement_rate: float
    revenue_achievement_rate: float
    overall_score: float
    period_rank: Optional[int]

@dataclass
class PerformanceSummary:
    user_id: int
    user_name: str
    period: str
    cars_sold: int
    target_cars: int
    cars_achievement: float
    revenue: Decimal
    target_revenue: Decimal
    revenue_achievement: float
    overall_score: float
    rank: int
    trend: str  # up, down, stable


class KPIService:
    # Weights for overall score calculation
    CARS_WEIGHT = 0.4
    REVENUE_WEIGHT = 0.6
    
    def __init__(self, kpi_repository, user_repository, contract_repository):
        self.kpi_repo = kpi_repository
        self.user_repo = user_repository
        self.contract_repo = contract_repository
    
    def calculate_monthly_kpi(self, user_id: int, year: int, month: int) -> KPIRecord:
        """Calculate KPI for a specific month"""
        period_value = f"{year}-{month:02d}"
        
        # Get contracts signed by this user in the period
        contracts = self.contract_repo.get_by_sales_user_and_period(
            user_id, year, month
        )
        
        # Calculate metrics
        cars_sold = len(contracts)
        revenue_generated = sum(c['total_amount'] for c in contracts)
        contracts_signed = len(contracts)
        
        # Count new customers (first purchase in this period)
        new_customers = self._count_new_customers(user_id, year, month)
        
        # Get targets
        target = self.kpi_repo.get_target(user_id, 'monthly', period_value)
        target_cars = target.get('sales_target', 0) if target else 0
        target_revenue = target.get('revenue_target', Decimal('0')) if target else Decimal('0')
        
        # Calculate achievement rates
        cars_achievement = self._calculate_achievement_rate(cars_sold, target_cars)
        revenue_achievement = self._calculate_achievement_rate(
            float(revenue_generated), float(target_revenue)
        )
        
        # Calculate overall score (weighted)
        overall_score = (
            cars_achievement * self.CARS_WEIGHT +
            revenue_achievement * self.REVENUE_WEIGHT
        )
        
        # Create or update KPI record
        kpi_data = {
            'user_id': user_id,
            'period_type': 'monthly',
            'period_value': period_value,
            'cars_sold': cars_sold,
            'revenue_generated': revenue_generated,
            'new_customers': new_customers,
            'contracts_signed': contracts_signed,
            'target_cars': target_cars,
            'target_revenue': target_revenue,
            'cars_achievement_rate': cars_achievement,
            'revenue_achievement_rate': revenue_achievement,
            'overall_score': overall_score
        }
        
        existing = self.kpi_repo.get_by_user_and_period(
            user_id, 'monthly', period_value
        )
        
        if existing:
            kpi_record = self.kpi_repo.update(existing['id'], kpi_data)
        else:
            kpi_record = self.kpi_repo.create(kpi_data)
        
        # Update user totals
        self._update_user_totals(user_id)
        
        # Recalculate rankings for the period
        self._recalculate_rankings('monthly', period_value)
        
        return KPIRecord(**kpi_record)
    
    def _calculate_achievement_rate(self, actual: float, target: float) -> float:
        """Calculate achievement rate as percentage"""
        if target == 0:
            return 100.0 if actual > 0 else 0.0
        return min((actual / target) * 100, 999.99)  # Cap at 999.99%
    
    def _count_new_customers(self, user_id: int, year: int, month: int) -> int:
        """Count new customers acquired in the period"""
        return self.contract_repo.count_new_customers_by_sales(
            user_id, year, month
        )
    
    def _update_user_totals(self, user_id: int):
        """Update cumulative totals in users table"""
        totals = self.contract_repo.get_cumulative_totals(user_id)
        self.user_repo.update_kpi_totals(
            user_id,
            total_sales=totals['total_cars'],
            total_revenue=totals['total_revenue'],
            last_update=datetime.now()
        )
    
    def _recalculate_rankings(self, period_type: str, period_value: str):
        """Recalculate rankings for all staff in a period"""
        all_kpis = self.kpi_repo.get_all_by_period(period_type, period_value)
        
        # Sort by overall_score descending
        sorted_kpis = sorted(
            all_kpis,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        # Assign ranks
        total_staff = len(sorted_kpis)
        for rank, kpi in enumerate(sorted_kpis, start=1):
            self.kpi_repo.update_rank(kpi['id'], rank, total_staff)
    
    def get_performance_ranking(self, period_type: str, 
                                 period_value: str,
                                 limit: int = 10) -> List[PerformanceSummary]:
        """Get top performers for a period"""
        top_kpis = self.kpi_repo.get_top_performers(
            period_type, period_value, limit
        )
        
        results = []
        for kpi in top_kpis:
            user = self.user_repo.get_by_id(kpi['user_id'])
            
            # Determine trend
            prev_period = self._get_previous_period(period_type, period_value)
            prev_kpi = self.kpi_repo.get_by_user_and_period(
                kpi['user_id'], period_type, prev_period
            )
            
            trend = 'stable'
            if prev_kpi:
                if kpi['overall_score'] > prev_kpi['overall_score'] * 1.05:
                    trend = 'up'
                elif kpi['overall_score'] < prev_kpi['overall_score'] * 0.95:
                    trend = 'down'
            
            results.append(PerformanceSummary(
                user_id=kpi['user_id'],
                user_name=user['full_name'] if user else 'Unknown',
                period=period_value,
                cars_sold=kpi['cars_sold'],
                target_cars=kpi['target_cars'],
                cars_achievement=kpi['cars_achievement_rate'],
                revenue=kpi['revenue_generated'],
                target_revenue=kpi['target_revenue'],
                revenue_achievement=kpi['revenue_achievement_rate'],
                overall_score=kpi['overall_score'],
                rank=kpi['period_rank'],
                trend=trend
            ))
        
        return results
    
    def compare_with_peers(self, user_id: int, period_type: str,
                           period_value: str) -> Dict:
        """Compare user's performance with team average"""
        user_kpi = self.kpi_repo.get_by_user_and_period(
            user_id, period_type, period_value
        )
        
        if not user_kpi:
            return None
        
        team_avg = self.kpi_repo.get_team_average(period_type, period_value)
        
        return {
            'user': {
                'cars_sold': user_kpi['cars_sold'],
                'revenue': user_kpi['revenue_generated'],
                'overall_score': user_kpi['overall_score'],
                'rank': user_kpi['period_rank']
            },
            'team_average': team_avg,
            'comparison': {
                'cars_vs_avg': (
                    (user_kpi['cars_sold'] / team_avg['avg_cars'] - 1) * 100
                    if team_avg['avg_cars'] > 0 else 0
                ),
                'revenue_vs_avg': (
                    (float(user_kpi['revenue_generated']) / 
                     float(team_avg['avg_revenue']) - 1) * 100
                    if team_avg['avg_revenue'] > 0 else 0
                )
            }
        }
    
    def generate_kpi_report(self, user_id: int, 
                           start_date: date,
                           end_date: date) -> Dict:
        """Generate comprehensive KPI report"""
        records = self.kpi_repo.get_by_user_and_date_range(
            user_id, start_date, end_date
        )
        
        if not records:
            return None
        
        total_cars = sum(r['cars_sold'] for r in records)
        total_revenue = sum(r['revenue_generated'] for r in records)
        avg_score = sum(r['overall_score'] for r in records) / len(records)
        
        best_month = max(records, key=lambda r: r['overall_score'])
        worst_month = min(records, key=lambda r: r['overall_score'])
        
        return {
            'period': f"{start_date} to {end_date}",
            'summary': {
                'total_cars_sold': total_cars,
                'total_revenue': total_revenue,
                'average_score': round(avg_score, 2),
                'months_count': len(records)
            },
            'best_performance': {
                'month': best_month['period_value'],
                'score': best_month['overall_score'],
                'cars': best_month['cars_sold'],
                'revenue': best_month['revenue_generated']
            },
            'worst_performance': {
                'month': worst_month['period_value'],
                'score': worst_month['overall_score'],
                'cars': worst_month['cars_sold'],
                'revenue': worst_month['revenue_generated']
            },
            'monthly_data': records
        }
    
    def auto_update_kpi_from_contracts(self):
        """Auto-update KPI when new contracts are signed"""
        # Get all contracts signed today
        today = date.today()
        new_contracts = self.contract_repo.get_by_date(today)
        
        # Group by sales person
        by_salesperson = {}
        for contract in new_contracts:
            sales_id = contract['sales_by']
            if sales_id not in by_salesperson:
                by_salesperson[sales_id] = []
            by_salesperson[sales_id].append(contract)
        
        # Update KPI for each salesperson
        for user_id, contracts in by_salesperson.items():
            self.calculate_monthly_kpi(user_id, today.year, today.month)
    
    def _get_previous_period(self, period_type: str, 
                             period_value: str) -> str:
        """Get the previous period string"""
        if period_type == 'monthly':
            year, month = map(int, period_value.split('-'))
            if month == 1:
                return f"{year-1}-12"
            else:
                return f"{year}-{month-1:02d}"
        # Add quarterly and yearly logic if needed
        return period_value
```

### KPI Dashboard UI Structure

```
KPIDashboardScreen
├── Header
│   ├── Title: "KPI Dashboard"
│   ├── Period Selector (Month/Quarter/Year)
│   └── Export Report Button
├── Overview Cards (4 cards)
│   ├── My Performance Score
│   ├── Cars Sold / Target
│   ├── Revenue / Target
│   ├── Current Rank
├── Charts Section
│   ├── Trend Chart (Line chart: Actual vs Target)
│   ├── Achievement Rate Chart (Bar chart)
│   └── Team Comparison (Horizontal bar)
├── Top Performers Table
│   ├── Rank, Name, Cars, Revenue, Score
│   └── Highlight current user
└── My KPI History
    ├── Monthly breakdown table
    └── Detail button for each month
```

### KPI Calculation Formula

```python
# Achievement Rate Formula
achievement_rate = (actual / target) * 100

# Overall Score Formula (Weighted)
overall_score = (
    cars_achievement_rate * 0.4 +
    revenue_achievement_rate * 0.6
)

# Performance Rating
if overall_score >= 120:
    rating = "Excellent"  # Xuất sắc
elif overall_score >= 100:
    rating = "Good"       # Tốt
elif overall_score >= 80:
    rating = "Average"    # Đạt
elif overall_score >= 60:
    rating = "Below Average"  # Cần cải thiện
else:
    rating = "Poor"       # Kém
```

---

## Ghi Chú

- **Auto-update**: KPI tự động cập nhật khi có hợp đồng mới
- **Ranking**: Xếp hạng được tính toán lại sau mỗi lần update
- **Targets**: Chỉ Admin/Manager mới có quyền set target
- **Reports**: Có thể export ra PDF/Excel
- **Trends**: So sánh với kỳ trước để xác định xu hướng

---

## Liên Kết

- [Sprint 0.3: Authorization](./sprint-0.3.md)
- [Sprint 1.1: Car Management Initial](./sprint-1.1.md)
- [Yêu cầu chức năng](../docs/YEU_CAU_CHUC_NANG.md)
- [Task List](../docs/TASK_LIST.md)
- [Database Design](../docs/DATABASE_DESIGN.md)
