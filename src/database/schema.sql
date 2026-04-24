-- Database Schema for Car Management System
-- Sprint 0.1 + 0.2 + 0.3: Employee Management + Authentication + Authorization

PRAGMA foreign_keys = ON;

-- =====================================================
-- 0. FOUNDATION - EMPLOYEE & AUTH
-- =====================================================

-- Bảng roles (Vai trò)
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_code VARCHAR(30) UNIQUE NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng users (Nhân viên)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    avatar_path VARCHAR(255),
    role_id INTEGER,
    department VARCHAR(50),
    position VARCHAR(50),
    hire_date DATE,
    base_salary DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'active',
    last_login DATETIME,
    login_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at DATETIME,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Bảng sessions (Quản lý phiên đăng nhập) - Sprint 0.2
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_info VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    ended_at DATETIME,
    end_reason VARCHAR(20), -- logout, timeout, forced, expired
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Bảng login_attempts (Theo dõi đăng nhập thất bại) - Sprint 0.2
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50),
    ip_address VARCHAR(45),
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 0,
    failure_reason VARCHAR(50), -- user_not_found, wrong_password, account_locked
    user_agent TEXT
);

-- Bảng permissions (Danh sách quyền) - Sprint 0.3
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    permission_name VARCHAR(100) NOT NULL,
    permission_code VARCHAR(50) UNIQUE NOT NULL,
    module VARCHAR(50), -- cars, customers, contracts, etc.
    action VARCHAR(20), -- view, create, edit, delete, approve
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng role_permissions (Gán quyền cho vai trò) - Sprint 0.3
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- Indexes for sessions - Sprint 0.2
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- Indexes for login_attempts - Sprint 0.2
CREATE INDEX IF NOT EXISTS idx_login_username ON login_attempts(username);
CREATE INDEX IF NOT EXISTS idx_login_attempted ON login_attempts(attempted_at);
CREATE INDEX IF NOT EXISTS idx_login_ip ON login_attempts(ip_address);

-- Indexes for permissions - Sprint 0.3
CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(permission_code);
CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module);
CREATE INDEX IF NOT EXISTS idx_permissions_action ON permissions(action);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_perm ON role_permissions(permission_id);

-- Trigger to auto-update updated_at
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =====================================================
-- SEED DATA
-- =====================================================

-- Insert default roles
INSERT OR IGNORE INTO roles (id, role_name, role_code, description, level) VALUES
(1, 'Administrator', 'admin', 'Quản trị viên hệ thống, có toàn quyền', 1),
(2, 'Manager', 'manager', 'Quản lý, có quyền quản lý nhân viên và xem báo cáo', 2),
(3, 'Sales Staff', 'sales', 'Nhân viên bán hàng', 3),
(4, 'Accountant', 'accountant', 'Kế toán viên', 4);

-- Insert default admin user (password: admin123, hashed with bcrypt)
INSERT OR IGNORE INTO users (id, username, password_hash, full_name, email, role_id, department, position, status) VALUES
(1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Ii2', 'Administrator', 'admin@cardealership.com', 1, 'Management', 'System Admin', 'active');

-- Insert permissions - Sprint 0.3
-- Cars Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(1, 'Xem danh sách xe', 'car.view', 'cars', 'view'),
(2, 'Thêm xe mới', 'car.create', 'cars', 'create'),
(3, 'Chỉnh sửa xe', 'car.edit', 'cars', 'edit'),
(4, 'Xóa xe', 'car.delete', 'cars', 'delete'),
(5, 'Xuất báo cáo xe', 'car.export', 'cars', 'export');

-- Customers Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(6, 'Xem danh sách khách hàng', 'customer.view', 'customers', 'view'),
(7, 'Thêm khách hàng', 'customer.create', 'customers', 'create'),
(8, 'Chỉnh sửa khách hàng', 'customer.edit', 'customers', 'edit'),
(9, 'Xóa khách hàng', 'customer.delete', 'customers', 'delete');

-- Contracts Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(10, 'Xem hợp đồng', 'contract.view', 'contracts', 'view'),
(11, 'Tạo hợp đồng', 'contract.create', 'contracts', 'create'),
(12, 'Chỉnh sửa hợp đồng', 'contract.edit', 'contracts', 'edit'),
(13, 'Xóa hợp đồng', 'contract.delete', 'contracts', 'delete'),
(14, 'Duyệt hợp đồng', 'contract.approve', 'contracts', 'approve'),
(15, 'In hợp đồng', 'contract.print', 'contracts', 'print');

-- Inventory Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(16, 'Xem tồn kho', 'inventory.view', 'inventory', 'view'),
(17, 'Nhập kho', 'inventory.import', 'inventory', 'create'),
(18, 'Xuất kho', 'inventory.export', 'inventory', 'delete');

-- Reports Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(19, 'Xem báo cáo', 'report.view', 'reports', 'view'),
(20, 'Tạo báo cáo', 'report.create', 'reports', 'create'),
(21, 'Xuất báo cáo', 'report.export', 'reports', 'export');

-- Users Module
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(22, 'Xem nhân viên', 'user.view', 'users', 'view'),
(23, 'Thêm nhân viên', 'user.create', 'users', 'create'),
(24, 'Chỉnh sửa nhân viên', 'user.edit', 'users', 'edit'),
(25, 'Xóa nhân viên', 'user.delete', 'users', 'delete'),
(26, 'Phân quyền', 'user.assign_role', 'users', 'assign');

-- Settings Module (Admin only)
INSERT OR IGNORE INTO permissions (id, permission_name, permission_code, module, action) VALUES
(27, 'Quản lý cài đặt', 'settings.manage', 'settings', 'manage'),
(28, 'Sao lưu dữ liệu', 'backup.manage', 'backup', 'manage');

-- Assign permissions to roles - Sprint 0.3
-- Admin: Tất cả quyền
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- Manager: Quản lý (không có xóa)
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions
WHERE action IN ('view', 'create', 'edit', 'approve', 'export', 'print');

-- Sales: Bán hàng (không có xóa, không có settings, backup)
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT 3, id FROM permissions
WHERE module IN ('cars', 'customers', 'contracts')
  AND action IN ('view', 'create', 'edit', 'print');

-- Accountant: Kế toán (chỉ xem và báo cáo)
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT 4, id FROM permissions
WHERE module IN ('contracts', 'reports', 'inventory')
  AND action IN ('view', 'export');

-- =====================================================
-- 0.4 SPRINT: EMPLOYEE KPI
-- =====================================================

-- Thêm fields vào bảng users cho KPI (chỉ nếu chưa tồn tại)
-- SQLite không hỗ trợ IF NOT EXISTS cho ALTER TABLE, nên dùng cách khác

-- Bảng kpi_records (Lịch sử KPI)
CREATE TABLE IF NOT EXISTS kpi_records (
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

-- Bảng kpi_targets (Mục tiêu KPI)
CREATE TABLE IF NOT EXISTS kpi_targets (
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

-- Indexes for KPI tables
CREATE INDEX IF NOT EXISTS idx_kpi_user ON kpi_records(user_id);
CREATE INDEX IF NOT EXISTS idx_kpi_period ON kpi_records(period_value);
CREATE INDEX IF NOT EXISTS idx_kpi_type_period ON kpi_records(period_type, period_value);
CREATE INDEX IF NOT EXISTS idx_kpi_targets_user ON kpi_targets(user_id);
CREATE INDEX IF NOT EXISTS idx_kpi_rank ON kpi_records(period_rank);

-- Trigger to auto-update kpi_records timestamp
CREATE TRIGGER IF NOT EXISTS update_kpi_timestamp
AFTER UPDATE ON kpi_records
BEGIN
    UPDATE kpi_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to auto-update kpi_targets timestamp
CREATE TRIGGER IF NOT EXISTS update_kpi_target_timestamp
AFTER UPDATE ON kpi_targets
BEGIN
    UPDATE kpi_targets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =====================================================
-- SPRINT 1: CAR MANAGEMENT
-- =====================================================

-- Bảng cars (Thông tin xe)
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin VARCHAR(17) UNIQUE NOT NULL,              -- Số khung (Vehicle Identification Number)
    license_plate VARCHAR(20) UNIQUE,             -- Biển số xe
    brand VARCHAR(50) NOT NULL,                   -- Hãng xe (Toyota, Honda, etc.)
    model VARCHAR(50) NOT NULL,                   -- Dòng xe (Camry, Civic, etc.)
    year INTEGER,                                 -- Năm sản xuất
    color VARCHAR(30),                            -- Màu sắc
    engine_number VARCHAR(50),                    -- Số máy
    transmission VARCHAR(20),                     -- Hộp số (auto/manual/cvt)
    fuel_type VARCHAR(20),                        -- Loại nhiên liệu (gasoline/diesel/electric/hybrid)
    mileage INTEGER DEFAULT 0 CHECK (mileage >= 0),                    -- Số km đã đi
    purchase_price DECIMAL(15,2) CHECK (purchase_price >= 0),        -- Giá nhập
    selling_price DECIMAL(15,2) CHECK (selling_price >= 0),          -- Giá bán
    status VARCHAR(20) DEFAULT 'available',       -- Trạng thái (available/sold/reserved/maintenance)
    description TEXT,                             -- Mô tả chi tiết
    images TEXT,                                  -- JSON array chứa đường dẫn ảnh
    is_deleted BOOLEAN DEFAULT 0,                 -- Soft delete flag
    deleted_at DATETIME,                          -- Thời điểm xóa
    deleted_by INTEGER,                           -- Người xóa
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,                           -- Người tạo record
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (deleted_by) REFERENCES users(id)
);

-- Indexes cho cars
CREATE INDEX IF NOT EXISTS idx_cars_vin ON cars(vin);
CREATE INDEX IF NOT EXISTS idx_cars_license_plate ON cars(license_plate) WHERE license_plate IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cars_brand ON cars(brand);
CREATE INDEX IF NOT EXISTS idx_cars_model ON cars(model);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);
CREATE INDEX IF NOT EXISTS idx_cars_year ON cars(year);
CREATE INDEX IF NOT EXISTS idx_cars_price ON cars(selling_price);

-- Trigger cập nhật updated_at cho cars
CREATE TRIGGER IF NOT EXISTS update_cars_timestamp
AFTER UPDATE ON cars
BEGIN
    UPDATE cars SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Seed data cho cars
INSERT OR IGNORE INTO cars (id, vin, license_plate, brand, model, year, color, purchase_price, selling_price, status) VALUES
(1, '1HGCM82633A123456', '51A-12345', 'Honda', 'Civic', 2023, 'Đen', 750000000, 850000000, 'available'),
(2, 'JTDBU4EE3B9123456', '51A-67890', 'Toyota', 'Camry', 2023, 'Trắng', 1200000000, 1350000000, 'available'),
(3, 'WBA3A5G59C1234567', '51A-11111', 'BMW', '320i', 2022, 'Xám', 1500000000, 1650000000, 'available');

-- Bảng car_history (Lịch sử thay đổi xe) - Sprint 1.2
CREATE TABLE IF NOT EXISTS car_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,                  -- create, update, delete
    field_name VARCHAR(50),                       -- Tên field thay đổi (nếu update)
    old_value TEXT,                               -- Giá trị cũ
    new_value TEXT,                               -- Giá trị mới
    changed_by INTEGER,                           -- Người thay đổi
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- Indexes cho car_history
CREATE INDEX IF NOT EXISTS idx_car_history_car ON car_history(car_id);
CREATE INDEX IF NOT EXISTS idx_car_history_changed_at ON car_history(changed_at);

-- =====================================================
-- SPRINT 1.3: CAR SEARCH & FILTER
-- =====================================================

-- Full-text search virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS cars_fts USING fts5(
    vin,
    license_plate,
    brand,
    model,
    description,
    content='cars',
    content_rowid='id'
);

-- Triggers để sync FTS index
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

-- =====================================================
-- SPRINT 1.4: CAR VALIDATION CONSTRAINTS
-- =====================================================

-- Unique indexes (excluding soft-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_vin_unique ON cars(vin) WHERE is_deleted = 0;
CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_plate_unique ON cars(license_plate) WHERE license_plate IS NOT NULL AND is_deleted = 0;

-- Additional indexes for validation
CREATE INDEX IF NOT EXISTS idx_cars_color ON cars(color);
CREATE INDEX IF NOT EXISTS idx_cars_transmission ON cars(transmission);
CREATE INDEX IF NOT EXISTS idx_cars_fuel_type ON cars(fuel_type);
CREATE INDEX IF NOT EXISTS idx_cars_is_deleted ON cars(is_deleted);

-- Note: CHECK constraints were added in table definition above

-- Additional indexes cho search
CREATE INDEX IF NOT EXISTS idx_cars_brand_model ON cars(brand, model);
CREATE INDEX IF NOT EXISTS idx_cars_price_range ON cars(selling_price);
CREATE INDEX IF NOT EXISTS idx_cars_status_year ON cars(status, year);



