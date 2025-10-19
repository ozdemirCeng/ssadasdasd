"""
Kocaeli Üniversitesi Sınav Takvimi Sistemi
Global Configuration Settings
"""

import os
from pathlib import Path

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sinav_takvimi_db',
    'user': 'postgres',
    'password': '123213oo',  # CHANGE THIS!
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600
}

# ============================================================
# SMTP EMAIL CONFIGURATION (Gmail Example)
# ============================================================
SMTP_CONFIG = {
    'enabled': True,  # Email gönderimi aktif mi?
    'host': 'smtp.gmail.com',
    'port': 587,
    'use_tls': True,
    'username': 'ozdmromer24@gmail.com',
    'password': '123213oo',      # Gmail App Password!
    'from_email': 'omer.ozdemir@kocaeli.edu.tr',
    'from_name': 'Kocaeli Üniversitesi Sınav Sistemi'
}

# ============================================================
# SECURITY SETTINGS
# ============================================================
SECURITY = {
    'password_min_length': 8,
    'max_login_attempts': 5,
    'account_lock_duration': 15,  # minutes
    'session_timeout': 480,  # minutes (8 hours)
    'password_reset_expiry': 15,  # minutes
    'jwt_secret_key': 'your-super-secret-jwt-key-change-this',  # CHANGE THIS!
    'jwt_algorithm': 'HS256',
    'bcrypt_rounds': 12
}

# ============================================================
# APPLICATION SETTINGS
# ============================================================
APP = {
    'name': 'Sınav Takvimi Yönetim Sistemi',
    'version': '1.0.0',
    'organization': 'Kocaeli Üniversitesi',
    'domain': 'kocaeli.edu.tr',
    'debug_mode': True,  # Production'da False yap!
    'log_level': 'INFO'
}

# ============================================================
# UI SETTINGS
# ============================================================
UI = {
    'theme': 'modern',
    'window_title': 'KOÜ Sınav Takvimi Sistemi',
    'min_width': 1200,
    'min_height': 700,
    'animation_duration': 300,  # ms
    'particle_count': 30,
    'enable_animations': True
}

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / 'resources'
LOGS_DIR = BASE_DIR / 'logs'
TEMP_DIR = BASE_DIR / 'temp'
EXPORTS_DIR = BASE_DIR / 'exports'

# Create directories if not exist
for directory in [LOGS_DIR, TEMP_DIR, EXPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# AppConfig class for compatibility
class AppConfig:
    APP_NAME = APP['name']
    APP_VERSION = APP['version']
    APP_ORGANIZATION = APP['organization']
    APP_DOMAIN = APP['domain']
    DEBUG_MODE = APP['debug_mode']
    LOG_LEVEL = APP['log_level']

# ============================================================
# EXCEL IMPORT SETTINGS
# ============================================================
EXCEL = {
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'allowed_extensions': ['.xlsx', '.xls'],
    'sheet_names': {
        'ders': 'Dersler',
        'ogrenci': 'Öğrenciler'
    }
}

# ============================================================
# PDF EXPORT SETTINGS
# ============================================================
PDF = {
    'page_size': 'A4',
    'orientation': 'landscape',
    'font_family': 'Arial',
    'margin': 20
}

# ============================================================
# LOGGING CONFIGURATION
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'INFO'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG' if APP['debug_mode'] else 'INFO'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if APP['debug_mode'] else 'INFO'
        }
    }
}

# LogConfig class for loguru logger
class LogConfig:
    FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LEVEL = "DEBUG" if APP['debug_mode'] else "INFO"
    LOG_FILE = str(LOGS_DIR / "app.log")
    ERROR_LOG_FILE = str(LOGS_DIR / "error.log")
    ROTATION = "10 MB"
    RETENTION = "7 days"
    COMPRESSION = "zip"

# ============================================================
# VALIDATION MESSAGES (Turkish)
# ============================================================
MESSAGES = {
    'login': {
        'empty_email': '📧 Lütfen e-posta adresinizi girin',
        'empty_password': '🔒 Lütfen şifrenizi girin',
        'invalid_email': '⚠️ Geçerli bir e-posta adresi girin',
        'invalid_credentials': '❌ E-posta veya şifre hatalı',
        'account_locked': '🔒 Hesabınız kilitlendi. {} dakika sonra tekrar deneyin',
        'success': '✅ Hoş geldiniz, {}!',
        'session_expired': '⏱️ Oturumunuzun süresi doldu',
        'connection_error': '🔌 Veritabanı bağlantı hatası: {}'
    },
    'password_reset': {
        'email_sent': '📧 Şifre sıfırlama bağlantısı e-postanıza gönderildi',
        'invalid_token': '❌ Geçersiz veya süresi dolmuş token',
        'success': '✅ Şifreniz başarıyla güncellendi'
    },
    'validation': {
        'required_field': 'Bu alan zorunludur',
        'min_length': 'En az {} karakter olmalıdır',
        'max_length': 'En fazla {} karakter olmalıdır',
        'invalid_format': 'Geçersiz format'
    }
}

# ============================================================
# COLOR PALETTE (Modern Green Theme)
# ============================================================
COLORS = {
    'primary': '#00A651',        # KOÜ Yeşil
    'primary_hover': '#00C75F',
    'primary_pressed': '#007A3D',
    'primary_light': '#E8F5E9',

    'secondary': '#2196F3',
    'secondary_hover': '#42A5F5',

    'success': '#4CAF50',
    'success_bg': '#E8F5E9',

    'error': '#F44336',
    'error_bg': '#FFEBEE',

    'warning': '#FF9800',
    'warning_bg': '#FFF3E0',

    'info': '#2196F3',
    'info_bg': '#E3F2FD',

    'background': '#F5F7FA',
    'surface': '#FFFFFF',
    'card': '#FFFFFF',

    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'text_disabled': '#94A3B8',

    'border': '#E2E8F0',
    'border_focus': '#00A651',

    'shadow': 'rgba(0, 0, 0, 0.1)'
}