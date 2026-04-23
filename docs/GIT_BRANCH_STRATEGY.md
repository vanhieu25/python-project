# Git Branch Strategy

**Phần Mềm Quản Lý Đại Lý Xe Hơi**

---

## Tổng Quan

Project sử dụng **Git Branching Strategy** với mỗi FEATURE có một branch riêng. Điều này giúp:
- Phát triển song song nhiều tính năng
- Cô lập lỗi, dễ rollback
- Code review hiệu quả
- Quản lý release rõ ràng

---

## Danh Sách Branch

### Branch Chính

| Branch | Mô tả | Bảo vệ |
|--------|-------|--------|
| `main` | Production-ready code | ✅ Yes |
| `develop` | Integration branch (tùy chọn) | ✅ Yes |

### Feature Branches (15 branches)

| # | Branch Name | Feature | Ưu tiên | Số Sprint |
|---|-------------|---------|---------|-----------|
| 0 | `feature/0-foundation-auth` | Foundation - Employee & Auth | 🔴 CRITICAL | 4 |
| 1 | `feature/1-car-management` | Car Management | 🔴 Core | 4 |
| 2 | `feature/2-customer-management` | Customer Management | 🔴 Core | 4 |
| 3 | `feature/3-contract-management` | Contract Management | 🔴 Core | 4 |
| 4 | `feature/4-inventory-management` | Inventory Management | 🟠 High | 3 |
| 5 | `feature/5-reporting-system` | Reporting System | 🟠 High | 4 |
| 6 | `feature/6-warranty-management` | Warranty Management | 🟡 Medium | 3 |
| 7 | `feature/7-promotion-management` | Promotion Management | 🟡 Medium | 3 |
| 8 | `feature/8-accessory-management` | Accessory Management | 🟡 Medium | 3 |
| 9 | `feature/9-supplier-management` | Supplier Management | 🟡 Medium | 3 |
| 10 | `feature/10-installment-management` | Installment Management | 🟡 Medium | 3 |
| 11 | `feature/11-after-sales-services` | After-sales Services | 🟢 Low | 2 |
| 12 | `feature/12-marketing-management` | Marketing Management | 🟢 Low | 2 |
| 13 | `feature/13-complaint-management` | Complaint Management | 🟡 Medium | 3 |
| 14 | `feature/14-security-system` | Security System | 🟠 High | 3 |

---

## Quy Trình Làm Việc

### 1. Bắt đầu Feature Mới

```bash
# Chuyển sang branch main và pull code mới nhất
git checkout main
git pull origin main

# Chuyển sang feature branch
git checkout feature/1-car-management

# Làm việc, commit thay đổi
git add .
git commit -m "feat: add car model and repository"

# Push lên remote
git push origin feature/1-car-management
```

### 2. Cập Nhật Từ Main

```bash
# Khi main có thay đổi mới
git checkout feature/1-car-management
git fetch origin
git rebase origin/main

# Hoặc merge nếu không dùng rebase
git merge origin/main
```

### 3. Hoàn Thành Feature

```bash
# Chuyển về main
git checkout main

# Merge feature branch (dùng --no-ff để giữ history)
git merge --no-ff feature/1-car-management -m "Merge feature/1-car-management: Car Management"

# Push lên main
git push origin main

# Xóa feature branch (tùy chọn)
git branch -d feature/1-car-management
git push origin --delete feature/1-car-management
```

---

## Sử Dụng Script Hỗ Trợ

Project cung cấp script `git-workflow.sh` để quản lý branch dễ dàng.

### Các Lệnh

```bash
# Liệt kê tất cả feature branches
./git-workflow.sh list

# Tạo tất cả feature branches
./git-workflow.sh create-all

# Chuyển sang branch cụ thể
./git-workflow.sh switch feature/1-car-management

# Xem trạng thái các branch
./git-workflow.sh status

# Merge branch vào main
./git-workflow.sh merge feature/1-car-management

# Xóa một branch
./git-workflow.sh delete feature/1-car-management

# Xóa tất cả feature branches (⚠️ Cẩn thận!)
./git-workflow.sh clean

# Hiển thị help
./git-workflow.sh help
```

---

## Thứ Tự Phát Triển (Dependency)

```
main
│
├─► feature/0-foundation-auth (Sprint 0.1-0.4) [LÀM TRƯỚC TẤT CẢ]
│   │
│   ├─► feature/1-car-management (Sprint 1.1-1.4)
│   │   │
│   │   └─► feature/4-inventory-management (Sprint 4.1-4.3)
│   │
│   ├─► feature/2-customer-management (Sprint 2.1-2.4)
│   │   │
│   │   └─► feature/12-marketing-management (Sprint 12.1-12.2)
│   │
│   ├─► feature/3-contract-management (Sprint 3.1-3.4)
│   │   │
│   │   ├─► feature/5-reporting-system (Sprint 5.1-5.4)
│   │   │
│   │   ├─► feature/6-warranty-management (Sprint 6.1-6.3)
│   │   │
│   │   ├─► feature/7-promotion-management (Sprint 7.1-7.3)
│   │   │
│   │   ├─► feature/8-accessory-management (Sprint 8.1-8.3)
│   │   │
│   │   ├─► feature/10-installment-management (Sprint 10.1-10.3)
│   │   │
│   │   ├─► feature/11-after-sales-services (Sprint 11.1-11.2)
│   │   │
│   │   └─► feature/13-complaint-management (Sprint 13.1-13.3)
│   │
│   ├─► feature/9-supplier-management (Sprint 9.1-9.3)
│   │
│   └─► feature/14-security-system (Sprint 14.1-14.3)
```

### Ghi Chú Quan Trọng

- **Feature 0** (Foundation) **PHẢI** hoàn thành trước tất cả các feature khác
- Các feature **Core** (1, 2, 3) có thể phát triển song song sau khi Feature 0 xong
- Feature 5 (Reporting) phụ thuộc vào các feature có dữ liệu để báo cáo
- Feature 14 (Security) nên làm cuối cùng sau khi đã có đủ tính năng

---

## Commit Message Convention

```
[type]: [mô tả ngắn gọn]

[body - tùy chọn]

[footer - tùy chọn]
```

### Types

| Type | Mô tả | Ví dụ |
|------|-------|-------|
| `feat` | Tính năng mới | `feat: add car CRUD operations` |
| `fix` | Sửa lỗi | `fix: resolve null pointer in car search` |
| `docs` | Tài liệu | `docs: update API documentation` |
| `style` | Format code | `style: fix indentation` |
| `refactor` | Tái cấu trúc | `refactor: simplify car service logic` |
| `test` | Test | `test: add unit tests for car repository` |
| `chore` | Công việc khác | `chore: update dependencies` |

### Ví Dụ

```bash
# Feature commit
git commit -m "feat: implement car search with filters"

# Fix commit
git commit -m "fix: handle empty result in car search

- Return empty list instead of None
- Add validation for search keywords"

# With issue reference
git commit -m "feat: add customer VIP classification

Closes #42"
```

---

## Pull Request Template

Khi tạo Pull Request để merge feature vào main:

```markdown
## 🎯 Feature
[Feature Name] - [Mô tả ngắn]

## ✅ Checklist
- [ ] Code đã được test locally
- [ ] Unit test coverage ≥ 80%
- [ ] Không có lỗi lint
- [ ] Đã cập nhật documentation
- [ ] Commit message đúng convention

## 📝 Changes
- [Liệt kê các thay đổi chính]

## 🧪 Testing
- [Mô tả cách test]

## 📸 Screenshots (nếu có UI)
[Chèn ảnh]

## 🔗 Related
- Sprint: [Sprint number]
- Dependencies: [Các PR liên quan]
```

---

## Xử Lý Conflict

### Khi Rebase Gặp Conflict

```bash
git checkout feature/1-car-management
git rebase origin/main

# Nếu có conflict, sửa file rồi:
git add .
git rebase --continue

# Hoặc hủy rebase:
git rebase --abort
```

### Khi Merge Gặp Conflict

```bash
git checkout main
git merge feature/1-car-management

# Nếu có conflict, sửa file rồi:
git add .
git commit -m "Merge feature/1-car-management with conflict resolution"
```

---

## Best Practices

### ✅ Nên Làm

1. **Pull trước khi làm việc**: Luôn `git pull origin main` trước khi bắt đầu
2. **Commit thường xuyên**: Nhiều commit nhỏ tốt hơn 1 commit lớn
3. **Viết commit message rõ ràng**: Mô tả WHAT và WHY
4. **Test trước khi push**: Đảm bảo code chạy được
5. **Review code**: Tạo PR và yêu cầu review trước khi merge

### ❌ Không Nên

1. **Commit trực tiếp lên main**: Luôn dùng feature branch
2. **Force push**: Tránh `git push -f` trừ khi thực sự cần
3. **Commit binary files**: Không commit file `.exe`, `.db`, `node_modules/`
4. **Commit secrets**: Không commit password, API keys

---

## Liên Kết

- [Git Workflow Script](../git-workflow.sh)
- [Task List](./TASK_LIST.md)
- [Coding Conventions](./TECH_STACK.md#8-coding-conventions)

---

**Tài liệu cho đồ án Lập trình Python**
**Nhóm 4 - Quản Lý Đại Lý Xe Hơi**
**© 2026**
