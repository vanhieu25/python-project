-- Database Schema for Car Management System
-- Sprint 0.1: Employee Management

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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

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
-- Note: In production, use proper bcrypt hashing
INSERT OR IGNORE INTO users (id, username, password_hash, full_name, email, role_id, department, position, status) VALUES
(1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Ii2', 'Administrator', 'admin@cardealership.com', 1, 'Management', 'System Admin', 'active');
