"""
Kocaeli Üniversitesi Sınav Takvimi Sistemi
Main Entry Point - Single Window with Page System
"""

import sys
import logging
import logging.config
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PySide6.QtCore import Qt

# Import configuration
from config import DATABASE, LOGGING, APP, UI

# Import models
from models.database import db

# Import controllers
from controllers.login_controller import LoginController

# Import views
from views.login_view import LoginView
from views.main_window import DashboardView


class MainApplication(QMainWindow):
    """
    Ana uygulama penceresi
    Tek pencere içinde sayfa geçişi
    """
    
    def __init__(self):
        super().__init__()
        self.login_controller = LoginController()
        self.current_user = None
        
        self.setWindowTitle("Kocaeli Üniversitesi - Sınav Takvimi Sistemi")
        self.setMinimumSize(1400, 800)
        
        self._init_ui()
        
    def _init_ui(self):
        """UI oluştur"""
        # Central widget - Stacked widget for page switching
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create pages
        self.login_page = LoginView(self.login_controller)
        self.dashboard_page = None  # Will be created after login
        
        # Add login page
        self.stacked_widget.addWidget(self.login_page)
        
        # Connect signals
        self.login_page.login_success.connect(self._on_login_success)
        
        # Show login page
        self.stacked_widget.setCurrentWidget(self.login_page)
        
    def _on_login_success(self, user_data):
        """Login başarılı - Dashboard sayfasına geç"""
        logger = logging.getLogger(__name__)
        logger.info(f"[OK] Login successful: {user_data['email']} ({user_data['role']})")
        
        self.current_user = user_data
        
        # Create dashboard page
        self.dashboard_page = DashboardView(user_data)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Connect dashboard signals
        self.dashboard_page.logout_requested.connect(self._on_logout)
        self.dashboard_page.module_changed.connect(self._on_module_changed)
        
        # Switch to dashboard
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        
    def _on_logout(self):
        """Logout - Login sayfasına dön"""
        logger = logging.getLogger(__name__)
        logger.info("[LOGOUT] User logged out")
        
        # Clear login fields
        self.login_page.clear()
        
        # Remove dashboard page
        if self.dashboard_page:
            self.stacked_widget.removeWidget(self.dashboard_page)
            self.dashboard_page = None
        
        # Switch to login page
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.current_user = None
        
    def _on_module_changed(self, module_name):
        """Module değişikliği"""
        logger = logging.getLogger(__name__)
        logger.info(f"[MODULE] Switched to: {module_name}")
        # TODO: Module content loading


def setup_logging():
    """Configure application logging"""
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"[START] {APP['name']} v{APP['version']}")
    logger.info("=" * 60)
    return logger


def initialize_database():
    """Initialize database connection"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("[DB] Initializing database connection...")
        db.initialize(DATABASE)

        # Test connection
        if db.test_connection():
            logger.info("[OK] Database connection successful")
            return True
        else:
            logger.error("[ERROR] Database connection test failed")
            return False

    except Exception as e:
        logger.error(f"[ERROR] Database initialization failed: {e}")
        return False


def show_database_error():
    """Show database connection error dialog"""
    from PySide6.QtWidgets import QMessageBox
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Veritabanı Bağlantı Hatası")
    msg.setText("Veritabanına bağlanılamadı!")
    msg.setInformativeText(
        "Lütfen aşağıdaki kontrolleri yapın:\n\n"
        "• PostgreSQL servisi çalışıyor mu?\n"
        "• config.py dosyasındaki veritabanı ayarları doğru mu?\n"
        "• Veritabanı oluşturulmuş mu? (sinav_takvimi_db)\n"
        "• Kullanıcı adı ve şifre doğru mu?"
    )
    msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
    msg.setDefaultButton(QMessageBox.Retry)

    return msg.exec() == QMessageBox.Retry


def main():
    """Main application entry point"""

    # Setup logging
    logger = setup_logging()

    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName(APP['name'])
    app.setOrganizationName(APP['organization'])
    app.setOrganizationDomain(APP['domain'])

    # Enable high DPI scaling (modern approach)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Initialize database
    while True:
        if initialize_database():
            break
        else:
            if not show_database_error():
                logger.info("[CANCEL] User cancelled database connection")
                sys.exit(1)

    # Create main application window
    logger.info("[UI] Creating main application window...")
    main_window = MainApplication()
    main_window.show()

    # Run application
    result = app.exec()
    
    if result == 0:
        logger.info("[OK] Application closed normally")
    else:
        logger.info("[CANCEL] Application cancelled")

    # Cleanup
    logger.info("[CLEANUP] Closing database connections...")
    db.close_all()

    logger.info("[END] Application closed")
    return result


if __name__ == "__main__":
    sys.exit(main())