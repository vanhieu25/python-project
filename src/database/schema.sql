-- Database Schema for Car Management System
-- Sprint 3.1: Contract Management Initial

PRAGMA foreign_keys = ON;

-- =====================================================
-- BASE TABLES (from previous sprints)
-- =====================================================

-- Bảng users (Người dùng hệ thống)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL,      -- admin, sales, manager, etc.
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng customers (Khách hàng)
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    id_card VARCHAR(20),
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng cars (Xe)
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin VARCHAR(17) UNIQUE NOT NULL,              -- Số khung
    license_plate VARCHAR(20),                     -- Biển số
    brand VARCHAR(50) NOT NULL,                    -- Hãng xe
    model VARCHAR(50) NOT NULL,                    -- Model
    year INTEGER NOT NULL,                         -- Năm SX
    color VARCHAR(30),                             -- Màu sắc
    price DECIMAL(15,2) NOT NULL,                  -- Giá bán
    status VARCHAR(20) DEFAULT 'available',        -- available, reserved, sold
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SPRINT 3.1: CONTRACT MANAGEMENT
-- =====================================================

-- Bảng contracts (Hợp đồng mua bán)
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_code VARCHAR(20) UNIQUE NOT NULL,    -- Mã hợp đồng (HD000001)

    -- Thông tin khách hàng
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(100),                    -- Tên khách hàng lúc ký (snapshot)
    customer_phone VARCHAR(20),
    customer_id_card VARCHAR(20),
    customer_address TEXT,

    -- Thông tin xe
    car_id INTEGER NOT NULL,
    car_vin VARCHAR(17),                          -- Số khung (snapshot)
    car_license_plate VARCHAR(20),
    car_brand VARCHAR(50),
    car_model VARCHAR(50),
    car_year INTEGER,
    car_color VARCHAR(30),

    -- Thông tin giá
    car_price DECIMAL(15,2) NOT NULL,             -- Giá xe
    discount_amount DECIMAL(15,2) DEFAULT 0,      -- Giảm giá
    discount_reason VARCHAR(100),                 -- Lý do giảm giá
    total_amount DECIMAL(15,2) NOT NULL,          -- Tổng tiền sau giảm giá
    vat_amount DECIMAL(15,2) DEFAULT 0,           -- Thuế VAT
    final_amount DECIMAL(15,2) NOT NULL,          -- Tổng thanh toán (bao gồm VAT)

    -- Thông tin thanh toán
    payment_method VARCHAR(20),                   -- cash, bank_transfer, installment
    deposit_amount DECIMAL(15,2) DEFAULT 0,       -- Tiền đặt cọc
    paid_amount DECIMAL(15,2) DEFAULT 0,          -- Đã thanh toán
    remaining_amount DECIMAL(15,2) DEFAULT 0,     -- Còn lại

    -- Thông tin trả góp (nếu có)
    is_installment BOOLEAN DEFAULT 0,
    installment_down_payment DECIMAL(15,2),       -- Trả trước
    installment_months INTEGER,                     -- Số tháng trả góp
    installment_monthly_amount DECIMAL(15,2),     -- Số tiền hàng tháng

    -- Thông tin giao xe
    delivery_date DATE,                           -- Ngày giao xe dự kiến
    actual_delivery_date DATE,                      -- Ngày giao xe thực tế
    delivery_location VARCHAR(200),

    -- Trạng thái hợp đồng
    status VARCHAR(20) DEFAULT 'draft',           -- draft, pending, approved, signed, paid, delivered, cancelled
    approval_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected

    -- Thông tin phê duyệt
    created_by INTEGER NOT NULL,
    approved_by INTEGER,
    approved_at DATETIME,
    approval_notes TEXT,

    -- Thông tin ký
    signed_at DATETIME,
    signed_by_customer BOOLEAN DEFAULT 0,
    signed_by_representative BOOLEAN DEFAULT 0,

    -- Metadata
    notes TEXT,
    contract_template_id INTEGER,                 -- Mẫu hợp đồng sử dụng
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng contract_items (Chi tiết hợp đồng - phụ kiện, dịch vụ)
CREATE TABLE IF NOT EXISTS contract_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    item_type VARCHAR(20) NOT NULL,               -- accessory, service, insurance, registration
    item_name VARCHAR(100) NOT NULL,
    item_description TEXT,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(15,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    is_optional BOOLEAN DEFAULT 0,
    is_selected BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

-- Bảng contract_payments (Lịch sử thanh toán)
CREATE TABLE IF NOT EXISTS contract_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    payment_code VARCHAR(20),                     -- Mã phiếu thu
    payment_type VARCHAR(20),                     -- deposit, installment, final
    amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(20),                   -- cash, bank_transfer, card
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    received_by INTEGER,                          -- Người nhận tiền
    notes TEXT,
    receipt_printed BOOLEAN DEFAULT 0,            -- Đã in biên lai
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (received_by) REFERENCES users(id)
);

-- Bảng contract_status_history (Lịch sử thay đổi trạng thái)
CREATE TABLE IF NOT EXISTS contract_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by INTEGER,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- Bảng contract_templates (Mẫu hợp đồng)
CREATE TABLE IF NOT EXISTS contract_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name VARCHAR(100) NOT NULL,
    template_code VARCHAR(20) UNIQUE,
    template_content TEXT NOT NULL,               -- Nội dung mẫu với placeholders
    description TEXT,
    is_default BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contracts_code ON contracts(contract_code);
CREATE INDEX IF NOT EXISTS idx_contracts_customer ON contracts(customer_id);
CREATE INDEX IF NOT EXISTS idx_contracts_car ON contracts(car_id);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_created ON contracts(created_at);
CREATE INDEX IF NOT EXISTS idx_contract_items_contract ON contract_items(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_payments_contract ON contract_payments(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_history_contract ON contract_status_history(contract_id);

-- Triggers
CREATE TRIGGER IF NOT EXISTS update_contracts_timestamp
AFTER UPDATE ON contracts
BEGIN
    UPDATE contracts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Default contract template
INSERT OR IGNORE INTO contract_templates (id, template_name, template_code, template_content, description, is_default) VALUES
(1, 'Mẫu hợp đồng mua bán xe cơ bản', 'CONTRACT_DEFAULT',
'HỢP ĐỒNG MUA BÁN XE Ô TÔ

Số: {{contract_code}}
Ngày: {{created_date}}

BÊN BÁN (BÊN A): CÔNG TY TNHH SHOWROOM Ô TÔ
Địa chỉ: 123 Đường ABC, Quận 1, TP.HCM
Đại diện: {{seller_name}}
Chức vụ: Nhân viên bán hàng

BÊN MUA (BÊN B): {{customer_name}}
CMND/CCCD: {{customer_id_card}}
Địa chỉ: {{customer_address}}
Điện thoại: {{customer_phone}}

Điều 1: Xe bán
- Hãng xe: {{car_brand}}
- Model: {{car_model}}
- Năm SX: {{car_year}}
- Màu sắc: {{car_color}}
- Số khung (VIN): {{car_vin}}
- Biển số: {{car_license_plate}}

Điều 2: Giá cả và thanh toán
- Giá xe: {{car_price}} VNĐ
- Giảm giá: {{discount_amount}} VNĐ
- Tổng tiền: {{total_amount}} VNĐ
- Thuế VAT: {{vat_amount}} VNĐ
- Tổng thanh toán: {{final_amount}} VNĐ

Phương thức thanh toán: {{payment_method}}

Điều 3: Giao xe
Thời gian giao xe dự kiến: {{delivery_date}}
Địa điểm giao xe: {{delivery_location}}

Các bên cam kết thực hiện đúng các điều khoản trong hợp đồng.

ĐẠI DIỆN BÊN A                    NGƯỜI MUA (BÊN B)
(Ký và ghi rõ họ tên)            (Ký và ghi rõ họ tên)',
'Mẫu hợp đồng mua bán xe cơ bản mặc định', 1);
