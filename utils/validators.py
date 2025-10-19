"""
Input Validation Utilities
"""

import re
from typing import Dict, Any


class EmailValidator:
    """Email address validation"""

    # Comprehensive email regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate(cls, email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False

        email = email.strip().lower()

        # Basic format check
        if not cls.EMAIL_PATTERN.match(email):
            return False

        # Additional checks
        if len(email) > 255:
            return False

        if '..' in email:
            return False

        return True

    @classmethod
    def validate_domain(cls, email: str, allowed_domains: list = None) -> bool:
        """Validate email domain"""
        if not cls.validate(email):
            return False

        if allowed_domains:
            domain = email.split('@')[1].lower()
            return domain in [d.lower() for d in allowed_domains]

        return True


class PasswordValidator:
    """Password strength validation"""

    @staticmethod
    def validate_strength(password: str, min_length: int = 8) -> Dict[str, Any]:
        """
        Validate password strength

        Returns:
            {
                'valid': bool,
                'strength': int (0-4),
                'messages': list
            }
        """

        if not password:
            return {
                'valid': False,
                'strength': 0,
                'messages': ['Şifre boş olamaz']
            }

        messages = []
        strength = 0

        # Length check
        if len(password) < min_length:
            messages.append(f'En az {min_length} karakter olmalı')
        else:
            strength += 1

        # Has uppercase
        if re.search(r'[A-Z]', password):
            strength += 1
        else:
            messages.append('En az bir büyük harf içermeli')

        # Has lowercase
        if re.search(r'[a-z]', password):
            strength += 1
        else:
            messages.append('En az bir küçük harf içermeli')

        # Has digit
        if re.search(r'\d', password):
            strength += 1
        else:
            messages.append('En az bir rakam içermeli')

        # Has special character
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength += 1

        is_valid = len(messages) == 0

        return {
            'valid': is_valid,
            'strength': strength,
            'messages': messages
        }

    @staticmethod
    def get_strength_text(strength: int) -> str:
        """Get password strength description"""
        strengths = {
            0: 'Çok Zayıf',
            1: 'Zayıf',
            2: 'Orta',
            3: 'İyi',
            4: 'Güçlü',
            5: 'Çok Güçlü'
        }
        return strengths.get(strength, 'Bilinmiyor')


class InputValidator:
    """General input validation utilities"""

    @staticmethod
    def is_empty(value: str) -> bool:
        """Check if value is empty or whitespace"""
        return not value or not value.strip()

    @staticmethod
    def validate_length(value: str, min_len: int = 0, max_len: int = None) -> bool:
        """Validate string length"""
        if not value:
            return min_len == 0

        length = len(value.strip())

        if length < min_len:
            return False

        if max_len and length > max_len:
            return False

        return True

    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize user input (remove dangerous characters)"""
        if not value:
            return ""

        # Remove potential SQL injection characters
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = value

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Turkish phone number format"""
        if not phone:
            return False

        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Turkish phone: 10 or 11 digits
        return len(digits) in [10, 11]

    @staticmethod
    def validate_ogrenci_no(ogrenci_no: str) -> bool:
        """Validate student number format"""
        if not ogrenci_no:
            return False

        # Example: 260201001 (9 digits)
        pattern = re.compile(r'^\d{9}$')
        return bool(pattern.match(ogrenci_no.strip()))