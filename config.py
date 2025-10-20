"""
Kocaeli Üniversitesi Sınav Takvimi Sistemi
Yapılandırma Dosyası
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ============================================================
# Proje Yolları
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = RESOURCES_DIR / "images"
FONTS_DIR = RESOURCES_DIR / "fonts"
TEMP_DIR = BASE_DIR / "temp"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Klasörleri oluştur
for directory in [RESOURCES_DIR, ICONS_DIR, IMAGES_DIR, FONTS_DIR,
                  TEMP_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# Veritabanı Ayarları
# ============================================================
class DatabaseConfig:
    """PostgreSQL veritabanı ayarları"""

    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "5432"))
    DATABASE = os.getenv("DB_NAME", "sinav_takvimi_db")
    USER = os.getenv("DB_USER", "postgres")
    PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # Connection pool ayarları
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    # SQLAlchemy connection string
    @classmethod
    def get_connection_string(cls):
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"

    # Psycopg2 connection params
    @classmethod
    def get_connection_params(cls):
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'database': cls.DATABASE,
            'user': cls.USER,
            'password': cls.PASSWORD
        }


# ============================================================
# Uygulama Ayarları
# ============================================================
class AppConfig:
    """Genel uygulama ayarları"""

    APP_NAME = "Sınav Takvimi Yönetim Sistemi"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "Kocaeli Üniversitesi"
    DOMAIN = "kocaeli.edu.tr"

    # Debug mode
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Session ayarları
    SESSION_TIMEOUT = 3600  # 1 saat
    REMEMBER_ME_DAYS = 30

    # Güvenlik
    SECRET_KEY = os.getenv("SECRET_KEY", "kocaeli-uni-sinav-takvimi-2025")
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_REQUIRE_NUMBER = True

    # Rate limiting
    LOGIN_MAX_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = 300  # 5 dakika


# ============================================================
# Excel Import Ayarları
# ============================================================
class ExcelConfig:
    """Excel import/export ayarları"""

    # Desteklenen formatlar
    SUPPORTED_FORMATS = ['.xlsx', '.xls', '.xlsm']

    # Maksimum dosya boyutu (MB)
    MAX_FILE_SIZE = 50

    # Excel parser ayarları
    CHUNK_SIZE = 1000
    SKIP_EMPTY_ROWS = True

    # Ders listesi kolonları
    DERS_COLUMNS = {
        'ders_kodu': ['Ders Kodu', 'Ders Kod', 'Kod'],
        'ders_adi': ['Ders Adı', 'Ders Ad', 'Ders'],
        'ogretim_elemani': ['Öğretim Üyesi', 'Hoca', 'Öğretim Elemanı'],
        'sinif': ['Sınıf', 'Sinif'],
        'ders_yapisi': ['Ders Yapısı', 'Yapı', 'Zorunlu/Seçmeli']
    }

    # Öğrenci listesi kolonları
    OGRENCI_COLUMNS = {
        'ogrenci_no': ['Öğrenci No', 'No', 'Numara'],
        'ad_soyad': ['Ad Soyad', 'İsim', 'Öğrenci Adı'],
        'sinif': ['Sınıf', 'Sinif'],
        'ders_kodu': ['Ders Kodu', 'Kod']
    }


# ============================================================
# Sınav Programı Ayarları
# ============================================================
class ExamConfig:
    """Sınav programı oluşturma ayarları"""

    # Varsayılan değerler
    DEFAULT_EXAM_DURATION = 75  # dakika
    DEFAULT_BREAK_TIME = 15     # dakika

    # Sınav saatleri (saat, dakika)
    EXAM_TIME_SLOTS = [
        (9, 0),   # 09:00
        (11, 0),  # 11:00
        (13, 30), # 13:30
        (15, 30), # 15:30
    ]

    # Hafta içi günler
    WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']

    # Optimizasyon parametreleri
    MAX_EXAMS_PER_DAY = 4
    MAX_STUDENT_EXAMS_PER_DAY = 3
    MIN_REST_BETWEEN_EXAMS = 120  # dakika

    # Derslik kullanım oranı (kapasitenin yüzde kaçı kullanılmalı)
    CLASSROOM_USAGE_TARGET = 0.75  # %75


# ============================================================
# PDF Export Ayarları
# ============================================================
class PDFConfig:
    """PDF export ayarları"""

    # Sayfa ayarları
    PAGE_SIZE = 'A4'
    ORIENTATION = 'landscape'

    # Margin (mm)
    MARGIN_TOP = 20
    MARGIN_BOTTOM = 20
    MARGIN_LEFT = 15
    MARGIN_RIGHT = 15

    # Font ayarları
    FONT_FAMILY = 'Helvetica'
    FONT_SIZE_TITLE = 16
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_BODY = 10

    # Renkler (RGB)
    COLOR_PRIMARY = (0, 166, 81)
    COLOR_SECONDARY = (100, 116, 139)
    COLOR_TEXT = (15, 23, 42)
    COLOR_BORDER = (226, 232, 240)


# ============================================================
# Loglama Ayarları
# ============================================================
class LogConfig:
    """Loglama ayarları"""

    # Log seviyeleri
    LEVEL = "DEBUG" if AppConfig.DEBUG else "INFO"

    # Log formatı
    FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

    # Log dosyaları
    LOG_FILE = LOGS_DIR / "app.log"
    ERROR_LOG_FILE = LOGS_DIR / "error.log"

    # Rotation ayarları
    ROTATION = "10 MB"
    RETENTION = "30 days"

    # Compression
    COMPRESSION = "zip"


# ============================================================
# Cache Ayarları
# ============================================================
class CacheConfig:
    """Cache ayarları"""

    ENABLED = True
    TTL = 3600  # 1 saat

    # Redis (opsiyonel)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


# ============================================================
# UI Tema Ayarları
# ============================================================
class ThemeConfig:
    """UI tema ayarları"""

    # Renkler - KOÜ Yeşili
    PRIMARY_COLOR = "#00A651"
    PRIMARY_DARK = "#008F47"
    PRIMARY_LIGHT = "#00C75F"
    ACCENT_COLOR = "#10B981"

    SECONDARY_COLOR = "#64748b"
    BACKGROUND_COLOR = "#f8fafc"
    SURFACE_COLOR = "#ffffff"

    ERROR_COLOR = "#dc2626"
    SUCCESS_COLOR = "#16a34a"
    WARNING_COLOR = "#f59e0b"
    INFO_COLOR = "#2563eb"

    # Font boyutları
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_LARGE = 13
    FONT_SIZE_XLARGE = 16

    # Animasyon süreleri (ms)
    ANIMATION_FAST = 200
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500


# ============================================================
# Bölümler (Sabit)
# ============================================================
class DepartmentConfig:
    """Bölüm bilgileri"""

    DEPARTMENTS = [
        {
            'id': 1,
            'name': 'Bilgisayar Mühendisliği',
            'code': 'BMU',
            'color': '#00A651'
        },
        {
            'id': 2,
            'name': 'Yazılım Mühendisliği',
            'code': 'YMU',
            'color': '#2563eb'
        },
        {
            'id': 3,
            'name': 'Elektrik Mühendisliği',
            'code': 'EMU',
            'color': '#f59e0b'
        },
        {
            'id': 4,
            'name': 'Elektronik Mühendisliği',
            'code': 'ELM',
            'color': '#8b5cf6'
        },
        {
            'id': 5,
            'name': 'İnşaat Mühendisliği',
            'code': 'INS',
            'color': '#dc2626'
        }
    ]

    @classmethod
    def get_department_by_id(cls, dept_id):
        return next((d for d in cls.DEPARTMENTS if d['id'] == dept_id), None)

    @classmethod
    def get_department_by_code(cls, code):
        return next((d for d in cls.DEPARTMENTS if d['code'] == code), None)


# ============================================================
# Export all configs
# ============================================================
__all__ = [
    'DatabaseConfig',
    'AppConfig',
    'ExcelConfig',
    'ExamConfig',
    'PDFConfig',
    'LogConfig',
    'CacheConfig',
    'ThemeConfig',
    'DepartmentConfig',
    'BASE_DIR',
    'RESOURCES_DIR',
    'EXPORTS_DIR',
    'TEMP_DIR',
    'LOGS_DIR'
]