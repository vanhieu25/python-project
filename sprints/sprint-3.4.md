# Sprint 3.4: Contract Templates & Printing

> **Module**: 3. CONTRACT MANAGEMENT — Templates & Printing  
> **Ưu tiên**: HIGH  
> **Thời gian**: 2 ngày  
> **Blocked by**: Sprint-3.3  
> **Git Commit**: `feat: mẫu hợp đồng và in ấn`

---

## Mục Tiêu

Xây dựng hệ thống mẫu hợp đồng (templates) và chức năng in ấn, xuất PDF. Cho phép quản lý nhiều mẫu hợp đồng, tùy chỉnh nội dung, và in hợp đồng chuyên nghiệp.

---

## Checklist Công Việc

### 1. Template Model Enhancement

- [ ] **ContractTemplate Model** (`src/models/contract_template.py`)
  - `ContractTemplate` dataclass với các fields:
    - id, template_code, template_name, description
    - template_content: Nội dung mẫu với placeholders
    - header_content, footer_content
    - css_styles: Tùy chỉnh kiểu dáng
    - is_default, is_active
    - created_by, created_at, updated_at
  - `TemplateVariable` dataclass: Định nghĩa các biến có sẵn
  - Methods: `render(contract_data)`, `get_variables()`, `validate()`

- [ ] **Template Repository** (`src/repositories/template_repository.py`)
  - `TemplateRepository` class với các methods:
    - `create(template_data)` - Tạo mẫu mới
    - `update(template_id, data)` - Cập nhật mẫu
    - `delete(template_id)` - Xóa mẫu (soft delete)
    - `get_by_id(id)`, `get_by_code(code)` - Lấy mẫu
    - `get_all(active_only=True)` - Danh sách mẫu
    - `set_default(template_id)` - Đặt mẫu mặc định
    - `clone(template_id, new_code)` - Nhân bản mẫu

### 2. Template Service

- [ ] **TemplateService** (`src/services/template_service.py`)
  - `render_contract(contract_id, template_id=None)` → HTML
  - `preview_template(template_id, sample_data)` → HTML preview
  - `validate_template(template_content)` → Check placeholders
  - `get_available_variables()` → List các biến hỗ trợ
  - `apply_template(contract_id, template_id)` - Gán mẫu cho hợp đồng

- [ ] **Template Variables**
  ```python
  # Customer variables
  {{customer_name}}, {{customer_phone}}, {{customer_id_card}}
  {{customer_address}}, {{customer_email}}
  
  # Car variables
  {{car_brand}}, {{car_model}}, {{car_year}}, {{car_color}}
  {{car_vin}}, {{car_license_plate}}, {{car_price}}
  
  # Pricing variables
  {{car_price_formatted}}, {{discount_amount_formatted}}
  {{total_amount_formatted}}, {{vat_amount_formatted}}
  {{final_amount_formatted}}
  
  # Contract variables
  {{contract_code}}, {{contract_date}}, {{contract_date_vn}}
  {{created_by_name}}, {{approved_by_name}}
  
  # Company variables
  {{company_name}}, {{company_address}}, {{company_phone}}
  {{company_tax_code}}
  ```

### 3. PDF Generation Service

- [ ] **PDF Service** (`src/services/pdf_service.py`)
  - `generate_contract_pdf(contract_id, template_id=None)` → PDF bytes
  - `generate_payment_receipt(payment_id)` → PDF bytes
  - `generate_contract_summary(contract_id)` → PDF báo cáo tóm tắt
  - Options: page_size, orientation, margins
  - Watermark cho bản preview

- [ ] **PDF Generation Options**
  - Support WeasyPrint hoặc ReportLab
  - Header/Footer tùy chỉnh
  - Page numbering
  - Digital signature placeholder

### 4. Template Management UI

- [ ] **Template List View** (`template_list_view.py`)
  - Danh sách mẫu với preview thumbnail
  - Actions: Edit, Delete, Clone, Set Default
  - Filter: Active/Inactive, Default

- [ ] **Template Editor** (`template_editor_view.py`)
  - Rich text editor cho template content
  - Variable picker (dropdown chọn biến)
  - Live preview với sample data
  - Validate placeholders
  - Save as draft / Save & Activate

- [ ] **Template Preview Dialog**
  - Modal preview với real data
  - Switch between templates
  - Print/PDF export buttons

### 5. Printing Integration

- [ ] **Update Contract Detail View**
  - Thêm "In hợp đồng" button
  - Template selection dropdown
  - Print preview trước khi in
  - Lưu lịch sử in ấn

- [ ] **Print History** (`src/models/print_history.py`)
  - Bảng `printed_contracts` đã có trong schema
  - `PrintHistoryService` để query lịch sử
  - UI xem lịch sử in của hợp đồng

- [ ] **Batch Printing** (optional)
  - Chọn nhiều hợp đồng để in
  - Merge thành 1 PDF

### 6. Default Templates

- [ ] **Standard Templates**
  - `CONTRACT_DEFAULT`: Mẫu cơ bản (đã có)
  - `CONTRACT_INSTALLMENT`: Mẫu trả góp
  - `CONTRACT_COMPANY`: Mẫu bán cho công ty

- [ ] **Sample Template Content**
  ```html
  <!DOCTYPE html>
  <html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; }
      .header { text-align: center; border-bottom: 2px solid #333; }
      .contract-title { font-size: 18px; font-weight: bold; margin: 20px 0; }
      .party { margin: 15px 0; }
      .signatures { margin-top: 50px; display: flex; justify-content: space-between; }
    </style>
  </head>
  <body>
    <div class="header">
      <h1>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</h1>
      <h2>HỢP ĐỒNG MUA BÁN Ô TÔ</h2>
    </div>
    
    <div class="contract-info">
      <p>Số: {{contract_code}}</p>
      <p>Ngày: {{contract_date_vn}}</p>
    </div>
    
    <div class="party">
      <h3>BÊN BÁN (BÊN A): {{company_name}}</h3>
      <p>Địa chỉ: {{company_address}}</p>
    </div>
    
    <div class="party">
      <h3>BÊN MUA (BÊN B): {{customer_name}}</h3>
      <p>CMND/CCCD: {{customer_id_card}}</p>
      <p>Địa chỉ: {{customer_address}}</p>
    </div>
    
    <div class="vehicle-info">
      <h3>Điều 1: Xe bán</h3>
      <p>Hãng xe: {{car_brand}} {{car_model}}</p>
      <p>Năm SX: {{car_year}}</p>
      <p>Số khung: {{car_vin}}</p>
    </div>
    
    <div class="pricing">
      <h3>Điều 2: Giá cả</h3>
      <p>Giá xe: {{car_price_formatted}} VNĐ</p>
      <p>Tổng thanh toán: {{final_amount_formatted}} VNĐ</p>
    </div>
    
    <div class="signatures">
      <div>BÊN BÁN<br><br><br>{{created_by_name}}</div>
      <div>BÊN MUA<br><br><br>{{customer_name}}</div>
    </div>
  </body>
  </html>
  ```

### 7. Testing

- [ ] **Unit Tests** (`tests/test_template_service.py`)
  - Test template rendering với variables
  - Test PDF generation
  - Test validation

- [ ] **Integration Tests**
  - Test print workflow end-to-end
  - Test template cloning

### 8. Documentation

- [ ] **Template Guide** (`docs/TEMPLATE_GUIDE.md`)
  - Hướng dẫn tạo mẫu mới
  - Danh sách variables
  - Tips styling

---

## Files Cần Tạo/Cập Nhật

### New Files
```
src/models/contract_template.py
src/repositories/template_repository.py
src/services/template_service.py
src/services/pdf_service.py
src/views/contracts/template_list_view.py
src/views/contracts/template_editor_view.py
tests/test_template_service.py
docs/TEMPLATE_GUIDE.md
```

### Files to Update
```
src/views/contracts/contract_detail_view.py
src/database/schema.sql (nếu cần bổ sung)
```

---

## Dependencies

```
# requirements.txt
weasyprint==53.3  # Hoặc reportlab==3.6.12
jinja2==3.1.2
```

---

## Tiêu Chí Hoàn Thành

- [ ] Template model và repository hoạt động
- [ ] Có thể tạo, edit, clone templates
- [ ] Template rendering với placeholders
- [ ] PDF generation hoạt động
- [ ] Print history được lưu
- [ ] UI cho template management
- [ ] Unit tests pass
- [ ] Documentation cập nhật
- [ ] Git commit: `feat: mẫu hợp đồng và in ấn`

---

## Lưu Ý Kỹ Thuật

1. **HTML Safety**: Escape tất cả user input khi render template
2. **PDF Fonts**: Đảm bảo hỗ trợ Unicode (tiếng Việt)
3. **Image Support**: Hỗ trợ logo công ty trong template
4. **Page Breaks**: Xử lý page break cho hợp đồng dài
5. **Caching**: Cache rendered PDF để tăng tốc
