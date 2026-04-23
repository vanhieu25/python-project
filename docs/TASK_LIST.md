# TASK LIST - MINI SPRINT FEATURES

## PHẦN MỀM QUẢN LÝ ĐẠI LÝ XE HƠI

---

## CẤU TRÚC MINI SPRINT CHO MỖI FEATURE

```
Mini Sprint Flow:
[Xác định feature] → [Database] → [Backend Logic] → [UI Design] → [Testing] → [Git Commit]
```

- **Mỗi feature** bao gồm đầy đủ: Database + Backend + UI + Test
- **Mỗi sprint** hoàn thành 1 feature nhỏ và commit vào git
- **Tập trung** vào từng feature nhỏ để đảm bảo hoàn chỉnh

---

## DEFINITION OF DONE (DoD)

Một sprint được coi là **HOÀN THÀNH** khi đáp ứng toàn bộ tiêu chí sau:

| Tiêu chí              | Yêu cầu                                                   |
| --------------------- | --------------------------------------------------------- |
| ✅ Unit test coverage | ≥ 80% cho backend logic                                   |
| ✅ Integration test   | Tất cả luồng chính pass                                   |
| ✅ Code review        | Ít nhất 1 người review và approve                         |
| ✅ UI acceptance      | Chạy đúng trên Chrome, Firefox; responsive ≥ 768px        |
| ✅ No critical bug    | Không còn bug mức Blocker hoặc Critical                   |
| ✅ Git commit         | Commit message đúng convention, push lên remote branch    |
| ✅ Deploy             | Deploy thành công lên môi trường **staging**              |
| ✅ Documentation      | Cập nhật README hoặc inline comment nếu có logic phức tạp |

---

## THỨ TỰ THỰC HIỆN ĐỀ XUẤT

> ⚠️ **Lưu ý quan trọng**: Các module có đánh dấu `[PREREQUISITE]` phải hoàn thành **trước** khi bắt đầu các module phụ thuộc vào nó.

```
Giai đoạn 0 - Nền tảng (PHẢI LÀM TRƯỚC):
  Sprint-5.1 → Sprint-5.2 → Sprint-5.3
  (Employee → Authentication → Authorization)

Giai đoạn 1 - Core:
  Sprint-1.x → Sprint-2.x → Sprint-3.x → Sprint-4.x

Giai đoạn 2 - Business:
  Sprint-6.x, Sprint-7.x, Sprint-8.x, Sprint-9.x, Sprint-10.x, Sprint-11.x

Giai đoạn 3 - Extended:
  Sprint-12.x, Sprint-13.x, Sprint-14.x

Giai đoạn 4 - Security Hardening:
  Sprint-15.x
```

---

## FEATURES CHÍNH

---

### 🔐 0. FOUNDATION — EMPLOYEE & AUTH _(Ưu tiên: CRITICAL — làm trước tất cả)_

> Các module này là nền tảng phân quyền cho toàn hệ thống. **Phải hoàn thành trước khi bắt đầu bất kỳ module nào khác.**

| Sprint     | Công việc           | Database                        | Backend                 | UI                  | Test                         | Blocked by | Ước lượng | Assignee | Git Commit                  |
| ---------- | ------------------- | ------------------------------- | ----------------------- | ------------------- | ---------------------------- | ---------- | --------- | -------- | --------------------------- |
| Sprint-0.1 | Employee Management | Tạo bảng users/employees        | Models và role system   | List view nhân viên | Unit test CRUD               | —          | 2 ngày    | —        | feat: employee management   |
| Sprint-0.2 | Authentication      | Password hashing, session table | Login/logout logic, JWT | Login screen        | Auth integration test        | Sprint-0.1 | 2 ngày    | —        | feat: authentication system |
| Sprint-0.3 | Authorization       | Role-based permissions table    | Permission middleware   | Role assignment UI  | Permission test              | Sprint-0.2 | 2 ngày    | —        | feat: authorization system  |
| Sprint-0.4 | Employee KPI        | KPI tracking fields             | Performance calculation | KPI dashboard       | Performance calculation test | Sprint-0.1 | 3 ngày    | —        | feat: employee KPI          |

---

### 🚗 1. CAR MANAGEMENT _(Ưu tiên: Core)_

**Mô tả**: Quản lý thông tin xe

| Sprint     | Công việc              | Database                          | Backend               | UI                   | Test               | Blocked by | Ước lượng | Assignee | Git Commit                   |
| ---------- | ---------------------- | --------------------------------- | --------------------- | -------------------- | ------------------ | ---------- | --------- | -------- | ---------------------------- |
| Sprint-1.1 | Car Management Initial | Tạo bảng cars                     | Models và validators  | List view cơ bản     | Unit test CRUD     | Sprint-0.3 | 2 ngày    | —        | feat: car management initial |
| Sprint-1.2 | Car CRUD Operations    | Relations: cars ↔ contracts       | CRUD functions        | Add/Edit dialog      | Integration test   | Sprint-1.1 | 2 ngày    | —        | feat: car CRUD operations    |
| Sprint-1.3 | Car Search & Filter    | Indexes cho tìm kiếm              | Advanced search logic | Search box + filters | UI acceptance test | Sprint-1.2 | 2 ngày    | —        | feat: car search & filter    |
| Sprint-1.4 | Car Validation         | Unique constraints (VIN, biển số) | Business validation   | Error messages       | Edge case testing  | Sprint-1.2 | 1 ngày    | —        | feat: car validation logic   |

---

### 👥 2. CUSTOMER MANAGEMENT _(Ưu tiên: Core)_

**Mô tả**: Quản lý thông tin khách hàng

| Sprint     | Công việc                   | Database                         | Backend                  | UI                             | Test                    | Blocked by | Ước lượng | Assignee | Git Commit                        |
| ---------- | --------------------------- | -------------------------------- | ------------------------ | ------------------------------ | ----------------------- | ---------- | --------- | -------- | --------------------------------- |
| Sprint-2.1 | Customer Management Initial | Tạo bảng customers               | Models và validators     | List view cá nhân/doanh nghiệp | Unit test CRUD          | Sprint-0.3 | 2 ngày    | —        | feat: customer management initial |
| Sprint-2.2 | Customer CRUD Operations    | Relations: customers ↔ contracts | CRUD functions           | Add/Edit dialog                | Integration test        | Sprint-2.1 | 2 ngày    | —        | feat: customer CRUD operations    |
| Sprint-2.3 | Customer History            | History tracking fields          | History retrieval logic  | Transaction history tab        | UI acceptance test      | Sprint-2.2 | 2 ngày    | —        | feat: customer history tracking   |
| Sprint-2.4 | Customer VIP Classification | VIP status fields                | VIP classification logic | VIP badges in UI               | VIP classification test | Sprint-2.3 | 2 ngày    | —        | feat: customer VIP system         |

---

### 📄 3. CONTRACT MANAGEMENT _(Ưu tiên: Core)_

**Mô tả**: Quản lý hợp đồng bán xe

| Sprint     | Công việc                   | Database                                | Backend                 | UI                      | Test                | Blocked by             | Ước lượng | Assignee | Git Commit                        |
| ---------- | --------------------------- | --------------------------------------- | ----------------------- | ----------------------- | ------------------- | ---------------------- | --------- | -------- | --------------------------------- |
| Sprint-3.1 | Contract Management Initial | Tạo bảng contracts                      | Models và validators    | List view trạng thái    | Unit test CRUD      | Sprint-1.1, Sprint-2.1 | 2 ngày    | —        | feat: contract management initial |
| Sprint-3.2 | Contract Creation           | Foreign key relations (cars, customers) | Creation workflow       | Wizard tạo hợp đồng     | Integration test    | Sprint-1.2, Sprint-2.2 | 3 ngày    | —        | feat: contract creation workflow  |
| Sprint-3.3 | Contract Calculation        | Calculation fields                      | Price calculation logic | Real-time calculator    | Math operation test | Sprint-3.2             | 2 ngày    | —        | feat: contract calculation        |
| Sprint-3.4 | Contract PDF Export         | PDF storage                             | PDF generation logic    | Export button + preview | PDF generation test | Sprint-3.2             | 2 ngày    | —        | feat: contract PDF export         |

---

### 📦 4. INVENTORY MANAGEMENT _(Ưu tiên: High)_

**Mô tả**: Quản lý tồn kho xe

| Sprint     | Công việc                                   | Database                  | Backend                 | UI                     | Test                  | Blocked by              | Ước lượng | Assignee | Git Commit                  |
| ---------- | ------------------------------------------- | ------------------------- | ----------------------- | ---------------------- | --------------------- | ----------------------- | --------- | -------- | --------------------------- |
| Sprint-4.1 | Inventory Tracking                          | Stock quantity fields     | Stock update logic      | Inventory dashboard    | Unit test updates     | Sprint-1.2              | 2 ngày    | —        | feat: inventory tracking    |
| Sprint-4.2 | Stock Alerts                                | Alert configuration table | Low stock detection     | Notification system    | Alert threshold test  | Sprint-4.1              | 1 ngày    | —        | feat: inventory alerts      |
| Sprint-4.3 | Stock Purchase Orders _(nhập hàng tồn kho)_ | Stock PO tables           | Stock PO creation logic | Stock PO management UI | Order processing test | Sprint-4.1, Sprint-10.1 | 2 ngày    | —        | feat: stock purchase orders |

> ℹ️ Sprint-4.3 là **đặt lệnh nhập hàng để bổ sung tồn kho**. Khác với Sprint-10.2 (quản lý quan hệ đặt hàng với nhà cung cấp).

---

### 📊 5. REPORTING SYSTEM _(Ưu tiên: High)_

**Mô tả**: Hệ thống báo cáo thống kê

| Sprint     | Công việc            | Database                  | Backend                 | UI                    | Test                     | Blocked by | Ước lượng | Assignee | Git Commit                 |
| ---------- | -------------------- | ------------------------- | ----------------------- | --------------------- | ------------------------ | ---------- | --------- | -------- | -------------------------- |
| Sprint-5.1 | Revenue Reports      | Report calculation fields | Revenue aggregation     | Revenue chart UI      | Report accuracy test     | Sprint-3.3 | 2 ngày    | —        | feat: revenue reports      |
| Sprint-5.2 | Top Cars Report      | Car sales analytics       | Top selling calculation | Top cars chart        | Sales calculation test   | Sprint-3.2 | 2 ngày    | —        | feat: top cars report      |
| Sprint-5.3 | Employee Performance | Performance metrics       | Employee stats          | Performance dashboard | Metrics calculation test | Sprint-0.4 | 2 ngày    | —        | feat: employee performance |
| Sprint-5.4 | VIP Customer Report  | VIP criteria fields       | VIP identification      | VIP customer list     | VIP classification test  | Sprint-2.4 | 1 ngày    | —        | feat: VIP customer report  |

---

### 🔧 6. WARRANTY MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý bảo hành

| Sprint     | Công việc                   | Database                   | Backend              | UI                  | Test                        | Blocked by | Ước lượng | Assignee | Git Commit                |
| ---------- | --------------------------- | -------------------------- | -------------------- | ------------------- | --------------------------- | ---------- | --------- | -------- | ------------------------- |
| Sprint-6.1 | Warranty Management Initial | Tạo bảng warranties        | Models và validators | Warranty list view  | Unit test CRUD              | Sprint-3.2 | 2 ngày    | —        | feat: warranty management |
| Sprint-6.2 | Warranty Claims             | Claims tracking table      | Claim processing     | Claim submission UI | Claim workflow test         | Sprint-6.1 | 2 ngày    | —        | feat: warranty claims     |
| Sprint-6.3 | Warranty Expiration Alerts  | Expiration tracking fields | Expiration detection | Alert notifications | Expiration calculation test | Sprint-6.1 | 1 ngày    | —        | feat: warranty alerts     |

---

### 🎁 7. PROMOTION MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý khuyến mãi

| Sprint     | Công việc                    | Database               | Backend                         | UI                         | Test                      | Blocked by             | Ước lượng | Assignee | Git Commit                    |
| ---------- | ---------------------------- | ---------------------- | ------------------------------- | -------------------------- | ------------------------- | ---------------------- | --------- | -------- | ----------------------------- |
| Sprint-7.1 | Promotion Management Initial | Tạo bảng promotions    | Models và validators            | Promotion list UI          | Unit test CRUD            | Sprint-0.3             | 2 ngày    | —        | feat: promotion management    |
| Sprint-7.2 | Promotion Application        | Auto-application logic | Discount calculation            | Auto-apply trong contracts | Discount calculation test | Sprint-7.1, Sprint-3.3 | 2 ngày    | —        | feat: promotion application   |
| Sprint-7.3 | Promotion Effectiveness      | Tracking fields        | Effectiveness & ROI calculation | Effectiveness reports      | ROI calculation test      | Sprint-7.2             | 2 ngày    | —        | feat: promotion effectiveness |

---

### 🎒 8. ACCESSORY MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý phụ kiện

| Sprint     | Công việc                | Database                           | Backend               | UI                     | Test                      | Blocked by             | Ước lượng | Assignee | Git Commit                     |
| ---------- | ------------------------ | ---------------------------------- | --------------------- | ---------------------- | ------------------------- | ---------------------- | --------- | -------- | ------------------------------ |
| Sprint-8.1 | Accessory Catalog        | Tạo bảng accessories               | Models và inventory   | Catalog list UI        | Unit test CRUD            | Sprint-0.3             | 2 ngày    | —        | feat: accessory catalog        |
| Sprint-8.2 | Combo Pricing            | Combo definitions table            | Pricing logic         | Combo selection UI     | Price calculation test    | Sprint-8.1             | 2 ngày    | —        | feat: combo pricing            |
| Sprint-8.3 | Accessories in Contracts | Relations: accessories ↔ contracts | Add to contract logic | Add accessories dialog | Contract integration test | Sprint-8.1, Sprint-3.2 | 2 ngày    | —        | feat: accessories in contracts |

---

### 🏭 9. SUPPLIER MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý nhà cung cấp

| Sprint     | Công việc                                                      | Database           | Backend                   | UI                      | Test                    | Blocked by             | Ước lượng | Assignee | Git Commit                     |
| ---------- | -------------------------------------------------------------- | ------------------ | ------------------------- | ----------------------- | ----------------------- | ---------------------- | --------- | -------- | ------------------------------ |
| Sprint-9.1 | Supplier Management Initial                                    | Tạo bảng suppliers | Models và rating          | Supplier list UI        | Unit test CRUD          | Sprint-0.3             | 2 ngày    | —        | feat: supplier management      |
| Sprint-9.2 | Supplier Purchase Orders _(quản lý đơn hàng với nhà cung cấp)_ | Supplier PO system | Supplier order processing | Supplier PO creation UI | Order workflow test     | Sprint-9.1, Sprint-4.3 | 3 ngày    | —        | feat: supplier purchase orders |
| Sprint-9.3 | Supplier Rating                                                | Rating fields      | Rating calculation        | Rating display UI       | Rating calculation test | Sprint-9.2             | 1 ngày    | —        | feat: supplier rating          |

> ℹ️ Sprint-9.2 là **quản lý quan hệ và lịch sử đặt hàng với từng nhà cung cấp**. Khác với Sprint-4.3 (tạo lệnh nhập hàng bổ sung tồn kho).

---

### 💳 10. INSTALLMENT MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý trả góp

| Sprint      | Công việc               | Database               | Backend                | UI                  | Test                   | Blocked by  | Ước lượng | Assignee | Git Commit                    |
| ----------- | ----------------------- | ---------------------- | ---------------------- | ------------------- | ---------------------- | ----------- | --------- | -------- | ----------------------------- |
| Sprint-10.1 | Installment Calculation | Payment schedule table | Calculation logic      | Payment calculator  | Math operation test    | Sprint-3.3  | 2 ngày    | —        | feat: installment calculation |
| Sprint-10.2 | Payment Tracking        | Payment tracking table | Tracking system        | Payment history UI  | Tracking accuracy test | Sprint-10.1 | 2 ngày    | —        | feat: payment tracking        |
| Sprint-10.3 | Payment Alerts          | Alert triggers         | Late payment detection | Alert notifications | Alert threshold test   | Sprint-10.2 | 1 ngày    | —        | feat: payment alerts          |

---

### 🛠️ 11. AFTER-SALES SERVICES _(Ưu tiên: Low)_

**Mô tả**: Dịch vụ hậu mãi

| Sprint      | Công việc              | Database                | Backend            | UI                   | Test                  | Blocked by             | Ước lượng | Assignee | Git Commit                   |
| ----------- | ---------------------- | ----------------------- | ------------------ | -------------------- | --------------------- | ---------------------- | --------- | -------- | ---------------------------- |
| Sprint-11.1 | Maintenance Scheduling | Schedule tracking table | Scheduling logic   | Schedule calendar UI | Scheduling test       | Sprint-3.2, Sprint-6.1 | 3 ngày    | —        | feat: maintenance scheduling |
| Sprint-11.2 | Service Requests       | Request tracking table  | Request processing | Service request UI   | Request workflow test | Sprint-11.1            | 2 ngày    | —        | feat: service requests       |

---

### 📣 12. MARKETING MANAGEMENT _(Ưu tiên: Low)_

**Mô tả**: Quản lý marketing

| Sprint      | Công việc           | Database                | Backend             | UI                 | Test                   | Blocked by  | Ước lượng | Assignee | Git Commit                |
| ----------- | ------------------- | ----------------------- | ------------------- | ------------------ | ---------------------- | ----------- | --------- | -------- | ------------------------- |
| Sprint-12.1 | Marketing Campaigns | Campaign tracking table | Campaign management | Campaign dashboard | Campaign workflow test | Sprint-2.4  | 3 ngày    | —        | feat: marketing campaigns |
| Sprint-12.2 | Lead Management     | Lead tracking table     | Lead processing     | Lead management UI | Lead workflow test     | Sprint-12.1 | 2 ngày    | —        | feat: lead management     |

---

### ⚠️ 13. COMPLAINT MANAGEMENT _(Ưu tiên: Medium)_

**Mô tả**: Quản lý khiếu nại

| Sprint      | Công việc                    | Database                   | Backend             | UI                     | Test                     | Blocked by             | Ước lượng | Assignee | Git Commit                 |
| ----------- | ---------------------------- | -------------------------- | ------------------- | ---------------------- | ------------------------ | ---------------------- | --------- | -------- | -------------------------- |
| Sprint-13.1 | Complaint Management Initial | Tạo bảng complaints        | Models và workflow  | Complaint list UI      | Unit test CRUD           | Sprint-2.2, Sprint-3.2 | 2 ngày    | —        | feat: complaint management |
| Sprint-13.2 | Complaint Processing         | Assignment logic           | Processing workflow | Processing UI          | Workflow test            | Sprint-13.1            | 2 ngày    | —        | feat: complaint processing |
| Sprint-13.3 | Resolution Tracking          | Resolution tracking fields | Status updates      | Resolution tracking UI | Resolution workflow test | Sprint-13.2            | 1 ngày    | —        | feat: resolution tracking  |

---

### 🔒 14. SECURITY SYSTEM _(Ưu tiên: High — hoàn thiện sau khi deploy staging)_

**Mô tả**: Tăng cường bảo mật toàn hệ thống

> ℹ️ Authentication/Authorization cơ bản đã được xử lý tại **Sprint-0.2 và Sprint-0.3**. Module này là lớp bảo mật nâng cao.

| Sprint      | Công việc          | Database               | Backend                   | UI                         | Test            | Blocked by  | Ước lượng | Assignee | Git Commit               |
| ----------- | ------------------ | ---------------------- | ------------------------- | -------------------------- | --------------- | ----------- | --------- | -------- | ------------------------ |
| Sprint-14.1 | Session Management | Session tracking table | Session handling, timeout | Session timeout warning UI | Security test   | Sprint-0.2  | 2 ngày    | —        | feat: session management |
| Sprint-14.2 | Activity Logging   | Audit logs table       | Logging middleware        | Log viewer UI              | Logging test    | Sprint-0.3  | 2 ngày    | —        | feat: activity logging   |
| Sprint-14.3 | Data Encryption    | Encrypted fields (PII) | Encryption logic          | Secure data handling UI    | Encryption test | Sprint-14.1 | 3 ngày    | —        | feat: data encryption    |

---

## MINI SPRINT TEMPLATE

### Sprint-[XX.X]: [Tên Feature]

**1. Xác định feature:**

- [ ] Define requirements
- [ ] Identify dependencies (Blocked by sprint nào?)
- [ ] Plan database schema
- [ ] Assign cho developer

**2. Database:**

- [ ] Create/migrate tables
- [ ] Define relationships
- [ ] Add indexes/constraints
- [ ] Test schema integrity

**3. Backend Logic:**

- [ ] Create models
- [ ] Implement business logic
- [ ] Add validation rules
- [ ] Handle errors appropriately

**4. UI Design:**

- [ ] Create wireframes
- [ ] Implement interface
- [ ] Add interactions
- [ ] Ensure responsiveness (≥ 768px)

**5. Testing:**

- [ ] Unit tests ≥ 80% coverage
- [ ] UI acceptance tests (Chrome, Firefox)
- [ ] Integration tests
- [ ] Edge case scenarios

**6. Definition of Done check:**

- [ ] Unit test coverage ≥ 80%
- [ ] Tất cả integration test pass
- [ ] Code review ≥ 1 người approve
- [ ] Không còn bug Critical/Blocker
- [ ] Deploy lên staging thành công
- [ ] README / comment cập nhật

**7. Git Commit:**

- [ ] Commit message đúng convention `feat: [mô tả ngắn gọn]`
- [ ] Push lên remote branch
- [ ] Tạo Pull Request nếu làm theo nhánh

---

## TỔNG SỐ SPRINT & ƯỚC LƯỢNG

| Module                              | Số Sprint | Ưu tiên     | Ước lượng (ngày) | Blocked by                         |
| ----------------------------------- | --------- | ----------- | ---------------- | ---------------------------------- |
| **0. Foundation — Employee & Auth** | 4         | 🔴 CRITICAL | 9                | —                                  |
| 1. Car Management                   | 4         | 🔴 Core     | 7                | Sprint-0.3                         |
| 2. Customer Management              | 4         | 🔴 Core     | 8                | Sprint-0.3                         |
| 3. Contract Management              | 4         | 🔴 Core     | 9                | Sprint-1.x, Sprint-2.x             |
| 4. Inventory Management             | 3         | 🟠 High     | 5                | Sprint-1.2                         |
| 5. Reporting System                 | 4         | 🟠 High     | 7                | Sprint-2.4, Sprint-3.3, Sprint-0.4 |
| 6. Warranty Management              | 3         | 🟡 Medium   | 5                | Sprint-3.2                         |
| 7. Promotion Management             | 3         | 🟡 Medium   | 6                | Sprint-3.3                         |
| 8. Accessory Management             | 3         | 🟡 Medium   | 6                | Sprint-3.2                         |
| 9. Supplier Management              | 3         | 🟡 Medium   | 6                | Sprint-4.3                         |
| 10. Installment Management          | 3         | 🟡 Medium   | 5                | Sprint-3.3                         |
| 11. After-sales Services            | 2         | 🟢 Low      | 5                | Sprint-6.1                         |
| 12. Marketing Management            | 2         | 🟢 Low      | 5                | Sprint-2.4                         |
| 13. Complaint Management            | 3         | 🟡 Medium   | 5                | Sprint-3.2                         |
| 14. Security System                 | 3         | 🟠 High     | 7                | Sprint-0.2                         |
| **Tổng cộng**                       | **48**    | —           | **~100 ngày**    | —                                  |

### Ghi chú ước lượng

- Ước lượng trên tính cho **1 developer**, làm việc **full-time**.
- Nếu có **2 developers** làm song song các module độc lập → rút xuống còn **~55–60 ngày**.
- Các sprint có ký hiệu ⚠️ trong công việc là sprint có độ phức tạp cao, cần review kỹ hơn.
