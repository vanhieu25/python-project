# Phần Mềm Quản Lý Đại Lý Xe Hơi

<p align="center">
  <img src="assets/images/logo.png" alt="Car Management System Logo" width="200"/>
</p>

<p align="center">
  <strong>Giải pháp quản lý toàn diện cho đại lý xe hơi</strong>
</p>

<p align="center">
  <a href="#tính-năng">Tính năng</a> •
  <a href="#công-nghệ">Công nghệ</a> •
  <a href="#cài-đặt">Cài đặt</a> •
  <a href="#sử-dụng">Sử dụng</a> •
  <a href="#tài-liệu">Tài liệu</a>
</p>

---

## 📋 Giới thiệu

**Phần Mềm Quản Lý Đại Lý Xe Hơi** là ứng dụng desktop toàn diện giúp các đại lý xe hơi quản lý mọi khía cạnh của hoạt động kinh doanh - từ quản lý kho xe, khách hàng, hợp đồng bán hàng đến dịch vụ hậu mãi và báo cáo thống kê.

Ứng dụng được thiết kế với giao diện hiện đại theo phong cách Apple (minimalist, sang trọng), dễ sử dụng và tối ưu cho hiệu suất cao.

---

## ✨ Tính năng

Hệ thống bao gồm **15 module** với **71 chức năng**:

### 🚗 Quản lý thông tin xe

- Thêm, sửa, xóa thông tin xe
- Tìm kiếm nâng cao theo nhiều tiêu chí
- Lọc theo trạng thái: còn hàng / đã bán / sắp về

### 👥 Quản lý khách hàng

- Quản lý thông tin cá nhân/doanh nghiệp
- Lịch sử giao dịch đầy đủ
- Phân loại tự động (VIP, Regular, Potential)

### 📄 Quản lý hợp đồng

- Tạo hợp đồng bán xe với tính toán tự động
- Theo dõi trạng thái: mới tạo → đã thanh toán → đã giao xe
- Xuất hợp đồng PDF chuyên nghiệp

### 📦 Quản lý kho & nhập hàng

- Cập nhật tồn kho tự động
- Cảnh báo khi tồn kho thấp
- Quản lý đơn đặt hàng từ nhà cung cấp

### 🔧 Quản lý bảo hành

- Ghi nhận và theo dõi bảo hành
- Cảnh báo bảo hành sắp hết hạn
- Tiếp nhận và xử lý yêu cầu bảo hành

### 🎁 Quản lý khuyến mãi

- Tạo chương trình khuyến mãi đa dạng
- Áp dụng tự động khi tạo hợp đồng
- Theo dõi hiệu quả khuyến mãi

### 📊 Báo cáo thống kê

- Doanh thu theo thời gian (ngày/tháng/năm)
- Top 10 xe bán chạy
- Hiệu suất nhân viên
- Danh sách khách hàng VIP

### Và các module khác:

- 🏭 Quản lý nhà cung cấp
- 💳 Quản lý trả góp
- 🎒 Quản lý phụ kiện
- 🛠️ Dịch vụ hậu mãi
- 📣 Quản lý marketing
- ⚠️ Quản lý khiếu nại
- 🔐 Phân quyền & bảo mật

---

## 🛠️ Công nghệ

| Thành phần        | Công nghệ                         |
| ----------------- | --------------------------------- |
| **Ngôn ngữ**      | Python 3.10+                      |
| **GUI Framework** | PyQt6 6.4+                        |
| **Database**      | SQLite3                           |
| **ORM**           | SQLAlchemy 2.0+                   |
| **Security**      | bcrypt                            |
| **Reporting**     | ReportLab (PDF), openpyxl (Excel) |
| **Charts**        | pyqtgraph, matplotlib             |

### Yêu cầu hệ thống

| Thành phần  | Tối thiểu                            | Khuyến nghị               |
| ----------- | ------------------------------------ | ------------------------- |
| **OS**      | Windows 10 / Ubuntu 20.04 / macOS 11 | Windows 11 / Ubuntu 22.04 |
| **CPU**     | Dual-core 2.0 GHz                    | Quad-core 2.5 GHz+        |
| **RAM**     | 4 GB                                 | 8 GB+                     |
| **Storage** | 500 MB                               | 1 GB+                     |
| **Display** | 1366x768                             | 1920x1080+                |

---

## 📦 Cài đặt

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd python-project
```

### Bước 2: Tạo virtual environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng

```bash
python src/main.py
```

---

## 🚀 Sử dụng

### Đăng nhập

- **Tài khoản mặc định:**
  - Username: `admin`
  - Password: `admin123`

### Luồng làm việc chính

1. **Nhập kho xe** → Quản lý xe → Thêm mới
2. **Tiếp nhận khách** → Quản lý khách hàng → Thêm mới
3. **Tạo hợp đồng** → Quản lý hợp đồng → Tạo mới
4. **Theo dõi thanh toán** → Quản lý hợp đồng → Cập nhật trạng thái
5. **Xuất báo cáo** → Báo cáo thống kê → Chọn loại báo cáo

---

## 📁 Cấu trúc Project

```
python-project/
├── assets/               # Icons, images, stylesheets
├── data/                 # Database & backups
│   └── car_management.db
├── designs/
│   └── DESIGN.md         # UI Design System (Apple style)
├── docs/
│   ├── YEU_CAU_CHUC_NANG.md    # Yêu cầu chức năng
│   ├── LIST_CHUC_NANG.md       # 71 chức năng chi tiết
│   ├── TASK_LIST.md            # 48 Sprint kế hoạch
│   └── TECH_STACK.md           # Tài liệu công nghệ
├── sprints/              # Sprint tracking
├── src/                  # Source code
│   ├── main.py          # Entry point
│   ├── app.py           # Application class
│   ├── config.py        # Configuration
│   ├── models/          # Data models
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── views/           # UI components
│   ├── database/        # Database utilities
│   └── utils/           # Helper functions
├── tests/                # Unit & integration tests
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 📚 Tài liệu

- [Yêu cầu chức năng](docs/YEU_CAU_CHUC_NANG.md)
- [Danh sách chức năng](docs/LIST_CHUC_NANG.md)
- [Task List & Sprint](docs/TASK_LIST.md)
- [Tech Stack](docs/TECH_STACK.md)
- [Design System](designs/DESIGN.md)

---

## 🧪 Testing

Xem chi tiết tại [Testing Guide](docs/TESTING.md)

### Chạy nhanh

```bash
# Chạy tất cả unit tests
python -m unittest discover tests/ -v

# Chạy test cụ thể
python -m unittest tests.test_kpi_service -v

# Chạy test giao diện
python run_ui_tests.py
```

### Unit Tests Coverage

| Sprint | Tests | Status |
|--------|-------|--------|
| Sprint 0.1: Employee Management | 13 | ✅ Pass |
| Sprint 0.2: Authentication | 21 | ✅ Pass |
| Sprint 0.3: Authorization | 31 | ✅ Pass |
| Sprint 0.4: Employee KPI | 25 | ✅ Pass |
| **Tổng** | **90** | ✅ **Pass** |

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/

# Type checking
mypy src/
```

---

## 👥 Tác giả

**Nhóm 4** - Đồ án Lập trình Python

- Thành viên:
  - Nguyễn Văn Hiếu
  - Lê minh Đạt
  - Nguyễn Hữu Hải

---

## 📄 License

© 2026 Nhóm 4. All rights reserved.

Dự án được thực hiện cho mục đích học tập.

---

<p align="center">
  <sub>Built with ❤️ using Python & PyQt6</sub>
</p>
