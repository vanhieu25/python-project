# Sprint 3.3: Contract Approval Workflow

> **Module**: 3. CONTRACT MANAGEMENT — Approval Workflow  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 2 ngày  
> **Blocked by**: Sprint-3.2  
> **Git Commit**: `feat: approval workflow cho hợp đồng`

---

## Mục Tiêu

Xây dựng workflow phê duyệt hợp đồng với các trạng thái: draft → pending → approved → signed → paid → delivered. Bao gồm validation chuyển trạng thái, phân quyền, và audit trail.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define workflow requirements
- [ ] Identify state transitions
- [ ] Define approval permissions by role
- [ ] Identify notifications needed

### 2. Workflow Service (src/services/contract_workflow_service.py)

- [ ] **ContractWorkflowService Class**
  - `__init__(contract_repo, notification_service=None)`

- [ ] **State Transition Methods**
  - `submit_for_approval(contract_id, user_id, notes)` → draft → pending
    - Validate contract has customer, car, pricing
    - Create approval request
    - Notify managers
  
  - `approve(contract_id, approver_id, notes)` → pending → approved
    - Validate user has approval permission
    - Check contract completeness
    - Update approval_status
    - Notify sales staff
  
  - `reject(contract_id, approver_id, reason)` → pending → draft
    - Require rejection reason
    - Notify creator with reason
    - Add rejection to history
  
  - `mark_signed(contract_id, user_id, signed_by_customer, signed_by_rep)` → approved → signed
    - Record signature info
    - Update signed_at timestamp
    - Require both signatures
  
  - `mark_paid(contract_id, user_id, payment_amount)` → signed → paid
    - Validate payment covers full amount
    - Update paid_amount, remaining_amount
    - Allow partial payments
  
  - `mark_delivered(contract_id, user_id, delivery_notes)` → paid → delivered
    - Record actual_delivery_date
    - Update car status to 'sold'
    - Archive contract

- [ ] **Validation Methods**
  - `can_transition(from_status, to_status, user_role)` → bool
  - `validate_contract_complete(contract_id)` → Result
  - `check_required_approvals(contract_id)` → bool

- [ ] **Permission Checks**
  - `can_approve(user_id, contract_id)` → bool
  - `can_submit(user_id, contract_id)` → bool
  - `can_sign(user_id, contract_id)` → bool

### 3. Workflow Rules

```
Status Transitions:
- draft → pending: Creator/Admin (submit)
- pending → approved: Manager/Admin (approve)
- pending → draft: Manager/Admin (reject)
- approved → signed: Sales/Admin (signatures)
- signed → paid: Any (payment received)
- paid → delivered: Sales/Admin (delivery)
- Any (except delivered) → cancelled: Admin (cancel)

Required Fields by Status:
- pending: customer_name, car_brand, car_price, total_amount
- approved: All required fields
- signed: Both signatures
- paid: final_amount == paid_amount
- delivered: actual_delivery_date
```

### 4. Backend Updates

- [ ] **Update ContractService**
  - Thêm `submit_for_approval()` method
  - Thêm `check_eligibility_for_transition()` helper

- [ ] **Add Notification Service** (optional)
  - `notify_approval_requested(contract_id, managers)`
  - `notify_contract_approved(contract_id, creator)`
  - `notify_contract_rejected(contract_id, creator, reason)`

### 5. UI Updates

- [ ] **Update Contract Detail View**
  - Thêm action buttons theo status:
    - Draft: "Gửi phê duyệt", "Chỉnh sửa"
    - Pending: "Phê duyệt", "Từ chối" (manager only)
    - Approved: "Ký hợp đồng"
    - Signed: "Xác nhận thanh toán"
    - Paid: "Xác nhận giao xe"
  
  - Thêm status timeline/progress bar
  - Thêm approval history panel

- [ ] **Create Approval Dialog**
  - `ApprovalDialog`: Form nhập notes khi approve/reject
  - `SignatureDialog`: Form nhập thông tin ký
  - `DeliveryDialog`: Form xác nhận giao xe

- [ ] **Contract Queue View**
  - `contracts_awaiting_approval_view.py`: Danh sách hợp đồng chờ duyệt
  - Filter: status = 'pending'
  - Quick approve/reject actions

### 6. Dashboard Updates

- [ ] **Add Approval Widgets**
  - Số hợp đồng chờ duyệt của tôi
  - Số hợp đồng chờ duyệt (toàn hệ thống - manager)
  - Recent approvals

### 7. Testing

- [ ] **Unit Tests** (`tests/test_contract_workflow.py`)
  - Test valid state transitions
  - Test invalid transitions (should fail)
  - Test permission checks
  - Test required fields validation
  - Test history recording

- [ ] **Integration Tests**
  - Test full workflow: draft → delivered
  - Test rejection and resubmit
  - Test cancellation at each stage

### 8. Documentation

- [ ] **Update CONTRACT_MANAGEMENT.md**
  - Workflow diagram
  - State transition table
  - Permission matrix

---

## State Machine Diagram

```
                    ┌───────────┐
                    │   DRAFT   │
                    └─────┬─────┘
                          │ submit
                          ▼
                   ┌──────────────┐
              ┌────│   PENDING    │────┐
         reject   │ (awaiting    │   approve
              └────│  approval)   │────┘
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   APPROVED   │
                   └──────┬───────┘
                          │ sign
                          ▼
                   ┌──────────────┐
                   │    SIGNED    │
                   └──────┬───────┘
                          │ pay
                          ▼
                   ┌──────────────┐
                   │     PAID     │
                   └──────┬───────┘
                          │ deliver
                          ▼
                   ┌──────────────┐
                   │  DELIVERED   │
                   └──────────────┘

CANCELLED (from any status except delivered)
```

---

## Files Cần Tạo/Cập Nhật

### New Files
```
src/services/contract_workflow_service.py
tests/test_contract_workflow.py
src/views/contracts/approval_dialog.py
src/views/contracts/signature_dialog.py
src/views/contracts/delivery_dialog.py
src/views/contracts/contracts_awaiting_view.py
```

### Files to Update
```
src/services/contract_service.py
src/views/contracts/contract_detail_view.py
src/views/contracts/contract_dashboard.py
```

---

## Tiêu Chí Hoàn Thành

- [ ] All status transitions work correctly
- [ ] Permission checks enforced at each transition
- [ ] Invalid transitions are blocked with clear error messages
- [ ] History recorded for all transitions
- [ ] UI shows correct actions for each status
- [ ] Unit tests pass (>80% coverage)
- [ ] Documentation updated
- [ ] Git commit: `feat: approval workflow cho hợp đồng`

---

## Lưu Ý Kỹ Thuật

1. **Atomic Operations**: State transitions must be atomic with history recording
2. **Idempotency**: Same transition called twice should not create duplicate history
3. **Race Conditions**: Lock contract during status update to prevent concurrent modifications
4. **Audit Trail**: Every status change must be logged with who, when, and why
5. **Notifications**: Async notifications to avoid blocking UI
6. **Rollback**: Consider rollback mechanism for failed transitions
