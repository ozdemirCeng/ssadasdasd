"""
Login Controller - Business logic for authentication
Clean MVC separation with comprehensive error handling
"""

import uuid
import logging
from typing import Dict, Any

from models.user_model import UserModel
from utils.validators import EmailValidator, PasswordValidator
from config import SECURITY, MESSAGES

logger = logging.getLogger(__name__)


class LoginController:
    """Login business logic controller"""

    def __init__(self):
        self.user_model = UserModel()
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator()

    def login(self, email: str, password: str, ip_address: str = None,
             user_agent: str = None) -> Dict[str, Any]:
        """
        Authenticate user and create session

        Args:
            email: User email address
            password: Plain text password
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)

        Returns:
            {
                'success': bool,
                'message': str,
                'user': dict (if success),
                'session_id': str (if success)
            }
        """

        # Input validation
        validation_result = self._validate_inputs(email, password)
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['message']
            }

        # Normalize email
        email = email.strip().lower()

        # Find user
        user = self.user_model.find_by_email(email)

        if not user:
            # User not found
            self.user_model.log_login_attempt(
                email, False, ip_address, user_agent, 'user_not_found'
            )
            logger.warning(f"Login attempt for non-existent user: {email}")
            return {
                'success': False,
                'message': 'E-posta veya şifre hatalı'
            }

        # Check if account is active
        if not user['aktif']:
            self.user_model.log_login_attempt(
                email, False, ip_address, user_agent, 'account_inactive'
            )
            logger.warning(f"Login attempt for inactive account: {email}")
            return {
                'success': False,
                'message': 'Hesabınız devre dışı bırakılmış. Lütfen sistem yöneticisi ile iletişime geçin'
            }

        # Check if account is locked
        if self.user_model.is_account_locked(user['user_id']):
            remaining_minutes = self.user_model.get_remaining_lock_time(user['user_id'])
            self.user_model.log_login_attempt(
                email, False, ip_address, user_agent, 'account_locked'
            )
            logger.warning(f"Login attempt for locked account: {email}")
            return {
                'success': False,
                'message': f'Hesabınız kilitlendi. {remaining_minutes} dakika sonra tekrar deneyin'
            }

        # Verify password
        if not self.user_model.verify_password(password, user['password_hash']):
            # Wrong password
            failed_count = self.user_model.increment_failed_attempts(user['user_id'])

            # Lock account after max attempts
            if failed_count >= SECURITY['max_login_attempts']:
                self.user_model.lock_account(
                    user['user_id'],
                    SECURITY['account_lock_duration']
                )
                self.user_model.log_login_attempt(
                    email, False, ip_address, user_agent, 'account_locked_max_attempts'
                )
                logger.warning(f"Account locked due to max failed attempts: {email}")
                return {
                    'success': False,
                    'message': f'Çok fazla başarısız deneme. Hesabınız {SECURITY["account_lock_duration"]} dakika kilitlendi'
                }

            self.user_model.log_login_attempt(
                email, False, ip_address, user_agent, 'invalid_password'
            )

            remaining_attempts = SECURITY['max_login_attempts'] - failed_count
            return {
                'success': False,
                'message': f'Şifre hatalı. Kalan deneme hakkı: {remaining_attempts}'
            }

        # ✅ LOGIN SUCCESS

        # Reset failed attempts
        self.user_model.reset_failed_attempts(user['user_id'])

        # Update last login
        self.user_model.update_last_login(user['user_id'])

        # Create session
        session_id = str(uuid.uuid4())
        self.user_model.create_session(
            user['user_id'],
            session_id,
            ip_address,
            user_agent,
            SECURITY['session_timeout']
        )

        # Log successful login
        self.user_model.log_login_attempt(
            email, True, ip_address, user_agent
        )

        logger.info(f"Successful login: {email} (Role: {user['role']}, User ID: {user['user_id']})")

        # Prepare user data (remove sensitive info)
        user_data = {
            'user_id': user['user_id'],
            'email': user['email'],
            'role': user['role'],
            'ad_soyad': user['ad_soyad'],
            'bolum_id': user['bolum_id'],
            'bolum_adi': user.get('bolum_adi'),
            'bolum_kodu': user.get('bolum_kodu')
        }

        return {
            'success': True,
            'message': f'Hoş geldiniz, {user["ad_soyad"]}',
            'user': user_data,
            'session_id': session_id
        }

    def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Logout user by deleting session

        Args:
            session_id: Active session ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            self.user_model.delete_session(session_id)
            logger.info(f"User logged out: session={session_id[:8]}...")
            return {
                'success': True,
                'message': 'Çıkış yapıldı'
            }
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                'success': False,
                'message': 'Çıkış yapılırken hata oluştu'
            }

    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Validate active session

        Args:
            session_id: Session ID to validate

        Returns:
            {
                'valid': bool,
                'user': dict (if valid),
                'message': str (if invalid)
            }
        """
        try:
            session = self.user_model.validate_session(session_id)

            if session:
                # Update activity timestamp
                self.user_model.update_session_activity(session_id)
                return {
                    'valid': True,
                    'user': {
                        'user_id': session['user_id'],
                        'email': session['email'],
                        'role': session['role'],
                        'ad_soyad': session['ad_soyad'],
                        'bolum_id': session['bolum_id']
                    }
                }

            return {
                'valid': False,
                'message': 'Oturumunuzun süresi doldu. Lütfen tekrar giriş yapın'
            }

        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return {
                'valid': False,
                'message': 'Oturum doğrulama hatası'
            }

    def change_password(self, user_id: int, old_password: str,
                       new_password: str) -> Dict[str, Any]:
        """
        Change user password

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            # Get user
            user = self.user_model.find_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'Kullanıcı bulunamadı'
                }

            # Verify old password
            if not self.user_model.verify_password(old_password, user['password_hash']):
                return {
                    'success': False,
                    'message': 'Mevcut şifreniz hatalı'
                }

            # Validate new password
            validation = self.password_validator.validate_strength(new_password)
            if not validation['valid']:
                return {
                    'success': False,
                    'message': ', '.join(validation['messages'])
                }

            # Hash and update
            new_hash = self.user_model.hash_password(new_password)
            self.user_model.update_password(user_id, new_hash)

            logger.info(f"Password changed for user: {user['email']}")

            return {
                'success': True,
                'message': 'Şifreniz başarıyla değiştirildi'
            }

        except Exception as e:
            logger.error(f"Password change error: {e}")
            return {
                'success': False,
                'message': 'Şifre değiştirme sırasında hata oluştu'
            }

    def _validate_inputs(self, email: str, password: str) -> Dict[str, Any]:
        """
        Validate login inputs
        
        Args:
            email: Email address
            password: Password
        
        Returns:
            {'valid': bool, 'message': str}
        """

        # Email validation
        if not email or not email.strip():
            return {
                'valid': False,
                'message': 'Lütfen e-posta adresinizi girin'
            }

        if not self.email_validator.validate(email):
            return {
                'valid': False,
                'message': 'Geçerli bir e-posta adresi girin'
            }

        # Password validation
        if not password:
            return {
                'valid': False,
                'message': 'Lütfen şifrenizi girin'
            }

        if len(password) < 3:  # Minimum length check
            return {
                'valid': False,
                'message': 'Şifre çok kısa'
            }

        return {'valid': True}