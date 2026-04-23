-- Database Schema for Car Management System
-- Sprint 0.1 + 0.2: Employee Management + Authentication

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
