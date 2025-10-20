"""
main.py
Kocaeli Üniversitesi Sınav Takvimi Sistemi
Main Entry Point - Single Window with Page System
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, 
                               QMessageBox, QSplashScreen, QLabel)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QColor

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from config import DATABASE, LOGGING, APP, UI
from models.database import db
from controllers.login_controller import LoginController
from views.login_view import LoginView
from views.main_window import MainWindow
import logging
import logging.config


class MainApplication(QMainWindow):
    """
    Ana uygulama penceresi
    Tek pencere içinde sayfa geçişi (QStackedWidget)
    """
    
    def __init__(self):
        super().__init__()
        self.login_controller = LoginController()
        self.current_user = None
        
        self.setWindowTitle(f"{APP['name']} v{APP['version']}")
        self.setMinimumSize(1400, 800)
        
        # Frameless + modern look (opsiyonel)
        # self.setWindowFlag(Qt.FramelessWindowHint)
        
        self.init_ui()
        
    def init_ui(self):
        """UI oluştur - Stacked widget"""
        # Central widget - Page switching
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Login page (Dialog olarak değil, widget olarak)
        self.login_page = self.create_login_widget()
        self.dashboard_page = None  # Login sonrası oluşturulacak
        
        # Add login page
        self.stacked_widget.addWidget(self.login_page)
        
        # Show login page
        self.stacked_widget.setCurrentWidget(self.login_page)
        
    def create_login_widget(self):
        """Login page widget oluştur"""
        # LoginView'u widget olarak kullan
        login_view = LoginView(self.login_controller)
        
        # Connect signals
        login_view.login_success.connect(self.on_login_success)
        
        return login_view
        
    def on_login_success(self, user_data):
        """Login başarılı - Dashboard'a geç"""
        logger = logging.getLogger(__name__)
        logger.info(f"Login successful: {user_data['email']} ({user_data['role']})")
        
        self.current_user = user_data
        
        # Create dashboard page
        logger = logging.getLogger(__name__)
        logger.info("Creating dashboard...")
        self.dashboard_page = MainWindow(user_data)
        
        # Dashboard'u widget olarak ekle
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Connect signals
        self.dashboard_page.logout_requested.connect(self.on_logout)
        
        # Switch to dashboard
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        
        # Window title güncelle
        self.setWindowTitle(
            f"{APP['name']} - {user_data['ad_soyad']} ({user_data['role']})"
        )
        
    def on_logout(self):
        """Logout - Login sayfasına dön"""
        logger = logging.getLogger(__name__)
        logger.info("User logged out")
        
        reply = QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Sistemden çıkış yapmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear data
            self.current_user = None
            
            # Remove dashboard
            if self.dashboard_page:
                self.stacked_widget.removeWidget(self.dashboard_page)
                self.dashboard_page = None
            
            # Clear login fields
            self.login_page.clear()
            
            # Switch to login
            self.stacked_widget.setCurrentWidget(self.login_page)
            
            # Reset title
            self.setWindowTitle(f"{APP['name']} v{APP['version']}")
            
            logger = logging.getLogger(__name__)
            logger.info("Returned to login page")


def create_splash_screen():
    """Splash screen oluştur"""
    splash = QSplashScreen()
    splash.setFixedSize(500, 300)
    
    # Basit bir label ile splash
    splash_widget = QLabel()
    splash_widget.setAlignment(Qt.AlignCenter)
    splash_widget.setStyleSheet("""
        QLabel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #00A651,
                stop:1 #008F47
            );
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
    """)
    splash_widget.setText(
        f"🎓\n\n{APP['name']}\n\nv{APP['version']}\n\nYükleniyor..."
    )
    
    return splash


def setup_logging():
    """Logging başlat"""
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"  {APP['name']}")
    logger.info(f"  Version: {APP['version']}")
    logger.info(f"  {APP['organization']}")
    logger.info("=" * 60)


def initialize_database():
    """Veritabanı bağlantısını başlat"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing database connection...")
    
    try:
        # Initialize database
        db.initialize(DATABASE)
        
        # Test connection
        if db.test_connection():
            logger.info("Database connection successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def show_database_error():
    """Veritabanı hata dialog'u"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Veritabanı Bağlantı Hatası")
    msg.setText("Veritabanına bağlanılamadı!")
    msg.setInformativeText(
        "Lütfen aşağıdaki kontrolleri yapın:\n\n"
        f"• PostgreSQL servisi çalışıyor mu?\n"
        f"• Host: {DATABASE['host']}:{DATABASE['port']}\n"
        f"• Database: {DATABASE['database']}\n"
        f"• User: {DATABASE['user']}\n\n"
        "Veritabanı kurulumu için:\n"
        "psql -U postgres -f sinav_takvimi_final.sql"
    )
    msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
    msg.setDefaultButton(QMessageBox.Retry)
    
    return msg.exec() == QMessageBox.Retry


def main():
    """Ana giriş noktası"""
    
    # Setup logging
    setup_logging()
    
    try:
        # Create Qt Application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName(APP['name'])
        app.setOrganizationName(APP['organization'])
        app.setOrganizationDomain(APP['domain'])
        app.setStyle("Fusion")  # Modern look
        
        # High DPI support
        app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Splash screen (opsiyonel)
        splash = None  # Şimdilik splash screen'i devre dışı bırak
        
        # Initialize database
        logger = logging.getLogger(__name__)
        logger.info("Checking database connection...")
        
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            if initialize_database():
                break
            else:
                retry_count += 1
                if retry_count < max_retries:
                    if not show_database_error():
                        logger.info("User cancelled database connection")
                        return 1
                else:
                    QMessageBox.critical(
                        None,
                        "Kritik Hata",
                        f"Veritabanı bağlantısı {max_retries} denemeden sonra başarısız oldu.\n"
                        "Uygulama kapatılıyor."
                    )
                    return 1
        
        # Create main window
        logger.info("Creating main application window...")
        main_window = MainApplication()
        
        # Close splash
        if splash:
            QTimer.singleShot(1000, splash.close)
        
        # Show main window
        main_window.show()
        
        # Run application
        logger.info("Application started successfully")
        exit_code = app.exec()
        
        # Cleanup
        logger.info("Application closing...")
        logger.info("Closing database connections...")
        db.close_all()
        
        if exit_code == 0:
            logger.info("✓ Application closed normally")
        else:
            logger.warning(f"⚠ Application exited with code: {exit_code}")
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        return 0
        
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        
        QMessageBox.critical(
            None,
            "Kritik Hata",
            f"Beklenmeyen bir hata oluştu:\n\n{str(e)}\n\n"
            f"Detaylar için logs/error.log dosyasını kontrol edin."
        )
        
        return 1


if __name__ == "__main__":
    sys.exit(main())