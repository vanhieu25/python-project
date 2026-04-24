"""
Authentication Repository - Data access for sessions and login attempts.
Sprint 0.2: Authentication
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets

from ..database.db_helper import DatabaseHelper


class AuthRepository:
    """Repository for authentication data access."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def create_session(self, user_id: int, expires_at: datetime,
                       ip_address: str = None, user_agent: str = None,
                       device_info: str = None) -> str:
        """Create new session.

        Args:
            user_id: User ID
            expires_at: Session expiration time
            ip_address: Client IP address
            user_agent: Client user agent
            device_info: Device information

        Returns:
            str: Session token
        """
        session_token = self._generate_session_token()

        query = """
            INSERT INTO sessions (user_id, session_token, expires_at,
                                 ip_address, user_agent, device_info)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id, session_token, expires_at,
            ip_address, user_agent, device_info
        )

        self.db.execute(query, params)
        return session_token

    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by token.

        Args:
            session_token: Session token

        Returns:
            Session data or None
        """
        query = """
            SELECT s.*, u.username, u.full_name, u.role_id, r.role_code
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE s.session_token = ? AND s.is_active = 1
        """
        return self.db.fetch_one(query, (session_token,))

    def get_active_sessions_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of session data
        """
        query = """
            SELECT * FROM sessions
            WHERE user_id = ? AND is_active = 1
            ORDER BY started_at DESC
        """
        return self.db.fetch_all(query, (user_id,))

    def update_session_activity(self, session_token: str) -> bool:
        """Update last activity time.

        Args:
            session_token: Session token

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE sessions SET last_activity = ?
            WHERE session_token = ?
        """
        try:
            self.db.execute(query, (datetime.now(), session_token))
            return True
        except Exception:
            return False

    def deactivate_session(self, session_token: str,
                          reason: str = 'logout') -> bool:
        """Deactivate session.

        Args:
            session_token: Session token
            reason: End reason (logout, timeout, forced, expired)

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE sessions SET
                is_active = 0,
                ended_at = ?,
                end_reason = ?
            WHERE session_token = ?
        """
        try:
            self.db.execute(query, (datetime.now(), reason, session_token))
            return True
        except Exception:
            return False

    def deactivate_all_user_sessions(self, user_id: int,
                                     reason: str = 'forced') -> bool:
        """Deactivate all sessions for a user.

        Args:
            user_id: User ID
            reason: End reason

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE sessions SET
                is_active = 0,
                ended_at = ?,
                end_reason = ?
            WHERE user_id = ? AND is_active = 1
        """
        try:
            self.db.execute(query, (datetime.now(), reason, user_id))
            return True
        except Exception:
            return False

    def clean_expired_sessions(self) -> int:
        """Clean expired sessions.

        Returns:
            int: Number of sessions cleaned
        """
        query = """
            UPDATE sessions SET
                is_active = 0,
                ended_at = ?,
                end_reason = 'expired'
            WHERE is_active = 1 AND expires_at < ?
        """
        try:
            now = datetime.now()
            self.db.execute(query, (now, now))
            # Get count of affected rows (SQLite doesn't return this directly)
            # We can query for it
            count_query = """
                SELECT COUNT(*) as count FROM sessions
                WHERE is_active = 0 AND end_reason = 'expired'
                AND ended_at > ?
            """
            result = self.db.fetch_one(count_query, (now,))
            return result['count'] if result else 0
        except Exception:
            return 0

    # Login attempts tracking
    def record_login_attempt(self, username: str, success: bool,
                            failure_reason: str = None,
                            ip_address: str = None,
                            user_agent: str = None) -> int:
        """Record login attempt.

        Args:
            username: Username attempted
            success: Whether login was successful
            failure_reason: Reason for failure
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            int: Record ID
        """
        query = """
            INSERT INTO login_attempts (username, success, failure_reason,
                                       ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (username, success, failure_reason, ip_address, user_agent)
        return self.db.execute(query, params)

    def get_recent_failed_attempts(self, username: str,
                                   since: datetime) -> List[Dict[str, Any]]:
        """Get recent failed login attempts.

        Args:
            username: Username to check
            since: Datetime to check from

        Returns:
            List of failed attempt records
        """
        query = """
            SELECT * FROM login_attempts
            WHERE username = ? AND success = 0 AND attempted_at > ?
            ORDER BY attempted_at DESC
        """
        return self.db.fetch_all(query, (username, since))

    def get_failed_attempts_count(self, username: str,
                                  minutes: int = 30) -> int:
        """Get count of failed attempts in last N minutes.

        Args:
            username: Username to check
            minutes: Time window in minutes

        Returns:
            int: Number of failed attempts
        """
        since = datetime.now() - timedelta(minutes=minutes)
        query = """
            SELECT COUNT(*) as count FROM login_attempts
            WHERE username = ? AND success = 0 AND attempted_at > ?
        """
        result = self.db.fetch_one(query, (username, since))
        return result['count'] if result else 0

    def is_account_locked(self, username: str,
                          max_attempts: int = 5,
                          lockout_minutes: int = 30) -> bool:
        """Check if account is locked due to failed attempts.

        Args:
            username: Username to check
            max_attempts: Maximum allowed failed attempts
            lockout_minutes: Lockout duration in minutes

        Returns:
            bool: True if account is locked
        """
        count = self.get_failed_attempts_count(username, lockout_minutes)
        return count >= max_attempts

    def _generate_session_token(self) -> str:
        """Generate secure random session token.

        Returns:
            str: Session token
        """
        return secrets.token_urlsafe(32)

    def get_login_statistics(self, start_date: datetime,
                            end_date: datetime) -> Dict[str, Any]:
        """Get login statistics for date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with statistics
        """
        # Total attempts
        total_query = """
            SELECT COUNT(*) as count FROM login_attempts
            WHERE attempted_at BETWEEN ? AND ?
        """
        total_result = self.db.fetch_one(total_query, (start_date, end_date))
        total = total_result['count'] if total_result else 0

        # Successful attempts
        success_query = """
            SELECT COUNT(*) as count FROM login_attempts
            WHERE attempted_at BETWEEN ? AND ? AND success = 1
        """
        success_result = self.db.fetch_one(success_query, (start_date, end_date))
        successful = success_result['count'] if success_result else 0

        # Failed attempts
        failed = total - successful

        # Unique users
        users_query = """
            SELECT COUNT(DISTINCT username) as count FROM login_attempts
            WHERE attempted_at BETWEEN ? AND ?
        """
        users_result = self.db.fetch_one(users_query, (start_date, end_date))
        unique_users = users_result['count'] if users_result else 0

        return {
            'total_attempts': total,
            'successful': successful,
            'failed': failed,
            'unique_users': unique_users,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
