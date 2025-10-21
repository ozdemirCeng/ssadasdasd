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
    def update_password(user_id: int, new_password_hash: str):
        """Update user password"""
        query = """
            UPDATE users 
            SET password_hash = %s
            WHERE user_id = %s
        """
        db.execute_update(query, (new_password_hash, user_id))

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

    def __init__(self, db_connection):
        """Initialize with database connection"""
        self.db = db_connection

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            allowed_fields = ['ad_soyad', 'email', 'bolum_id', 'aktif']

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    updates.append(f"{key} = %s")
                    params.append(value)

            if not updates:
                logger.warning("No fields to update")
                return False

            params.append(user_id)

            query = f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE user_id = %s
            """

            cursor = self.db.execute_query(query, tuple(params))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"User updated (ID: {user_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {e}")
            return False

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Get current password hash
            query = "SELECT password_hash FROM users WHERE user_id = %s"
            cursor = self.db.execute_query(query, (user_id,))

            if not cursor:
                return False

            row = cursor.fetchone()
            if not row:
                return False

            current_hash = row[0]

            # Verify current password
            if not self.verify_password(current_password, current_hash):
                return False

            # Hash new password
            new_hash = self.hash_password(new_password)

            # Update password
            update_query = """
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
            """
            cursor = self.db.execute_query(update_query, (new_hash, user_id))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"Password changed for user ID: {user_id}")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error changing password: {e}")
            return False
