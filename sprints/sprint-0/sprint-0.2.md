# Sprint 0.2: Authentication

> **Module**: 0. FOUNDATION — Employee & Auth  
> **Ưu tiên**: CRITICAL  
> **Thời gian**: 2 ngày  
> **Blocked by**: Sprint-0.1 (Employee Management)  
> **Git Commit**: `feat: authentication system`  
> **Branch**: `feature/0-foundation-auth`

---

## Mục Tiêu

Xây dựng hệ thống xác thực (Authentication) bao gồm đăng nhập, đăng xuất, password hashing, và session management.

---

## Checklist Công Việc

### 1. Xác định yêu cầu

- [ ] Define requirements
- [ ] Identify dependencies: Sprint-0.1
- [ ] Plan database schema (session table)
- [ ] Assign cho developer

### 2. Database

- [ ] Tạo bảng `sessions` (quản lý phiên đăng nhập)
  - id, user_id, session_token
  - started_at, last_activity, expires_at
  - ip_address, user_agent, device_info
  - is_active, ended_at, end_reason
- [ ] Tạo bảng `login_attempts` (theo dõi đăng nhập thất bại)
  - id, username, ip_address, attempted_at
  - success, failure_reason, user_agent
- [ ] Thêm password hashing (bcrypt)
- [ ] Add indexes
  - INDEX on sessions.user_id
  - INDEX on sessions.session_token
  - INDEX on login_attempts.username
- [ ] Test schema integrity

### 3. Backend Logic

- [ ] **Password Hashing**
  - Sử dụng `bcrypt` để hash và verify password
  - `hash_password(password)` → password_hash
  - `verify_password(password, hash)` → bool
- [ ] **Authentication Service**
  - `AuthService` với các phương thức:
    - `login(username, password)` → User + Session
    - `logout(session_token)`
    - `validate_session(session_token)` → bool
    - `refresh_session(session_token)`
    - `change_password(user_id, old_pass, new_pass)`
  - Xử lý login attempts tracking
  - Block tài khoản sau 5 lần sai
- [ ] **Session Management**
  - Tạo session token (JWT hoặc random string)
  - Session timeout sau 30 phút không hoạt động
  - Lưu session vào database
  - Theo dõi last_activity
- [ ] **Middleware/Decorator**
  - `@require_login` decorator
  - Kiểm tra session hợp lệ
  - Redirect về login nếu chưa đăng nhập
- [ ] Handle errors appropriately

### 4. UI Design

- [ ] **Wireframes**
  - Login Screen
  - Change Password Dialog
  - Session Timeout Warning
- [ ] **Implementation**
  - `LoginDialog` hoặc `LoginScreen`
    - Username input
    - Password input (masked)
    - Login button
    - Remember me checkbox
    - Forgot password link
  - Loading indicator khi đang xác thực
  - Error messages (invalid credentials, locked account)
- [ ] **Interactions**
  - Enter key để submit
  - Show/Hide password toggle
  - Auto-focus vào username field
- [ ] **Responsiveness**
  - Centered login form
  - Hiển thị tốt trên mọi kích thước màn hình

### 5. Testing

- [ ] **Unit Tests (≥ 80% coverage)**
  - Test `hash_password` và `verify_password`
  - Test `AuthService.login` success/failure
  - Test session validation
  - Test session expiration
- [ ] **Integration Tests**
  - Test flow: Login → Access protected page → Logout
  - Test session timeout
  - Test concurrent sessions
  - Test brute force protection (5 failed attempts)
- [ ] **Security Tests**
  - Test SQL injection prevention
  - Test XSS prevention
  - Test session fixation
- [ ] **Edge Cases**
  - Login với username không tồn tại
  - Login với password sai
  - Login khi tài khoản bị khóa
  - Session hết hạn giữa chừng
  - Double login từ 2 thiết bị

### 6. Definition of Done

- [ ] Unit test coverage ≥ 80%
- [ ] Tất cả integration test pass
- [ ] Code review ≥ 1 người approve
- [ ] Không còn bug Critical/Blocker
- [ ] Deploy lên staging thành công
- [ ] README / comment cập nhật

### 7. Git Commit

> **Lưu ý**: Tất cả commit của Sprint 0 phải được thực hiện trên branch `feature/0-foundation-auth`

```bash
# 1. Đảm bảo đang ở đúng branch
git branch
# Output: * feature/0-foundation-auth

# 2. Add và commit changes
git add .
git commit -m "feat: authentication system

- Add sessions and login_attempts tables
- Implement bcrypt password hashing
- Create AuthService with login/logout logic
- Add LoginDialog UI
- Implement session timeout (30 minutes)
- Add brute force protection (5 attempts)

Relates to sprint-0.2"

# 3. Push lên remote branch
git push origin feature/0-foundation-auth
```

**Checklist:**
- [ ] Đang ở branch `feature/0-foundation-auth`
- [ ] Commit message đúng convention: `feat: authentication system`
- [ ] Commit có description chi tiết
- [ ] Push lên remote branch `origin feature/0-foundation-auth`
- [ ] **KHÔNG push lên `main`** - Sprint 0 chưa cần merge ngay

---

## Chi Tiết Kỹ Thuật

### Database Schema

```sql
-- Bảng sessions
CREATE TABLE sessions (
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
    end_reason VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bảng login_attempts
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50),
    ip_address VARCHAR(45),
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 0,
    failure_reason VARCHAR(50),
    user_agent TEXT
);

-- Indexes
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(session_token);
CREATE INDEX idx_sessions_active ON sessions(is_active);
CREATE INDEX idx_login_username ON login_attempts(username);
CREATE INDEX idx_login_attempted ON login_attempts(attempted_at);
```

### Auth Service (Python)

```python
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple

class AuthService:
    def __init__(self, user_repository, session_repository):
        self.user_repo = user_repository
        self.session_repo = session_repository
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(minutes=30)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    
    def login(self, username: str, password: str, 
              ip_address: str = None, user_agent: str = None) -> Tuple[bool, Optional[dict]]:
        """
        Authenticate user and create session
        Returns: (success, session_data)
        """
        # Check login attempts
        if self._is_account_locked(username):
            return False, {"error": "Account temporarily locked"}
        
        # Find user
        user = self.user_repo.get_by_username(username)
        if not user or user.get('is_deleted'):
            self._record_login_attempt(username, False, "user_not_found", ip_address, user_agent)
            return False, {"error": "Invalid credentials"}
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            self._record_login_attempt(username, False, "wrong_password", ip_address, user_agent)
            return False, {"error": "Invalid credentials"}
        
        # Check account status
        if user['status'] != 'active':
            return False, {"error": "Account is not active"}
        
        # Create session
        session_token = self._generate_session_token()
        expires_at = datetime.now() + self.session_timeout
        
        session_id = self.session_repo.create({
            'user_id': user['id'],
            'session_token': session_token,
            'expires_at': expires_at,
            'ip_address': ip_address,
            'user_agent': user_agent
        })
        
        # Update user login info
        self.user_repo.update_login_info(user['id'])
        
        # Record successful login
        self._record_login_attempt(username, True, None, ip_address, user_agent)
        
        return True, {
            'session_token': session_token,
            'user': user,
            'expires_at': expires_at
        }
    
    def logout(self, session_token: str) -> bool:
        """End session"""
        return self.session_repo.deactivate(session_token)
    
    def validate_session(self, session_token: str) -> Optional[dict]:
        """Validate and return session data"""
        session = self.session_repo.get_by_token(session_token)
        if not session or not session.get('is_active'):
            return None
        
        # Check expiration
        if datetime.now() > session['expires_at']:
            self.session_repo.deactivate(session_token, reason='expired')
            return None
        
        # Update last activity
        self.session_repo.update_activity(session_token)
        
        return session
    
    def _generate_session_token(self) -> str:
        """Generate secure random session token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        recent_attempts = self.session_repo.get_recent_failed_attempts(
            username, self.lockout_duration
        )
        return len(recent_attempts) >= self.max_login_attempts
    
    def _record_login_attempt(self, username: str, success: bool, 
                              reason: str, ip: str, user_agent: str):
        """Record login attempt for audit"""
        self.session_repo.record_attempt({
            'username': username,
            'success': success,
            'failure_reason': reason,
            'ip_address': ip,
            'user_agent': user_agent
        })
```

---

## Ghi Chú

- **Password Requirements**:
  - Tối thiểu 8 ký tự
  - Ít nhất 1 chữ hoa, 1 chữ thường, 1 số
  - Không chứa username
- **Session Timeout**: 30 phút không hoạt động
- **Max Login Attempts**: 5 lần sai liên tiếp → khóa 30 phút
- **Session Token**: Sử dụng `secrets.token_urlsafe(32)` cho độ an toàn cao

---

## Liên Kết

- [Sprint 0.1: Employee Management](./sprint-0.1.md)
- [Yêu cầu chức năng](../docs/YEU_CAU_CHUC_NANG.md)
- [Task List](../docs/TASK_LIST.md)
- [Database Design](../docs/DATABASE_DESIGN.md)
