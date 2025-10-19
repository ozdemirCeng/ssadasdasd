"""
User Model - Database operations for users table
Real authentication with security logging
"""

from typing import Optional, Dict, Any
from datetime import datetime
import bcrypt
import logging

from .database import db

logger = logging.getLogger(__name__)


class UserModel:
    """User database operations"""

    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address"""
        query = """
            SELECT 
                u.user_id,
                u.email,
                u.password_hash,
                u.role,
                u.bolum_id,
                u.ad_soyad,
                u.aktif,
                u.failed_login_attempts,
                u.account_locked_until,
                u.son_giris,
                b.bolum_adi,
                b.bolum_kodu
            FROM users u
            LEFT JOIN bolumler b ON u.bolum_id = b.bolum_id
            WHERE LOWER(u.email) = LOWER(%s)
        """
        return db.execute_query(query, (email,), fetch_one=True)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def update_last_login(user_id: int):
        """Update last login timestamp"""
        query = """
            UPDATE users 
            SET son_giris = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        db.execute_update(query, (user_id,))

    @staticmethod
    def reset_failed_attempts(user_id: int):
        """Reset failed login attempts counter"""
        query = """
            UPDATE users 
            SET failed_login_attempts = 0,
                account_locked_until = NULL
            WHERE user_id = %s
        """
        db.execute_update(query, (user_id,))

    @staticmethod
    def increment_failed_attempts(user_id: int) -> int:
        """Increment failed login attempts and return new count"""
        query = """
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1
            WHERE user_id = %s
            RETURNING failed_login_attempts
        """
        result = db.execute_query(query, (user_id,), fetch_one=True)
        return result['failed_login_attempts'] if result else 0

    @staticmethod
    def lock_account(user_id: int, duration_minutes: int = 15):
        """Lock user account for specified duration"""
        query = """
            UPDATE users 
            SET account_locked_until = CURRENT_TIMESTAMP + INTERVAL '%s minutes'
            WHERE user_id = %s
        """
        db.execute_update(query, (duration_minutes, user_id))

    @staticmethod
    def is_account_locked(user_id: int) -> bool:
        """Check if account is currently locked"""
        query = """
            SELECT account_locked_until > CURRENT_TIMESTAMP as is_locked
            FROM users
            WHERE user_id = %s
        """
        result = db.execute_query(query, (user_id,), fetch_one=True)
        return result['is_locked'] if result else False

    @staticmethod
    def get_remaining_lock_time(user_id: int) -> Optional[int]:
        """Get remaining lock time in minutes"""
        query = """
            SELECT EXTRACT(EPOCH FROM (account_locked_until - CURRENT_TIMESTAMP)) / 60 as minutes
            FROM users
            WHERE user_id = %s AND account_locked_until > CURRENT_TIMESTAMP
        """
        result = db.execute_query(query, (user_id,), fetch_one=True)
        return int(result['minutes']) + 1 if result and result['minutes'] else None

    @staticmethod
    def log_login_attempt(email: str, success: bool, ip_address: str = None,
                         user_agent: str = None, failure_reason: str = None):
        """Log login attempt to database"""
        try:
            db.execute_procedure('log_login_attempt', [
                email,
                success,
                failure_reason,
                ip_address,
                user_agent
            ])
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")

    @staticmethod
    def create_session(user_id: int, session_id: str, ip_address: str = None,
                      user_agent: str = None, expires_minutes: int = 480):
        """Create new active session"""
        query = """
            INSERT INTO active_sessions (
                session_id, user_id, ip_address, user_agent, 
                expires_at
            ) VALUES (
                %s, %s, %s, %s,
                CURRENT_TIMESTAMP + INTERVAL '%s minutes'
            )
        """
        db.execute_update(query, (session_id, user_id, ip_address,
                                 user_agent, expires_minutes))

    @staticmethod
    def validate_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data"""
        query = """
            SELECT 
                s.user_id,
                s.session_id,
                s.expires_at,
                u.email,
                u.role,
                u.ad_soyad,
                u.bolum_id
            FROM active_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_id = %s 
            AND s.expires_at > CURRENT_TIMESTAMP
            AND u.aktif = TRUE
        """
        return db.execute_query(query, (session_id,), fetch_one=True)

    @staticmethod
    def delete_session(session_id: str):
        """Delete session (logout)"""
        query = "DELETE FROM active_sessions WHERE session_id = %s"
        db.execute_update(query, (session_id,))

    @staticmethod
    def update_session_activity(session_id: str):
        """Update last activity timestamp"""
        query = """
            UPDATE active_sessions 
            SET last_activity = CURRENT_TIMESTAMP
            WHERE session_id = %s
        """
        db.execute_update(query, (session_id,))
