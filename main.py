"""
Kocaeli Üniversitesi Sınav Takvimi Sistemi
Main Entry Point
"""

import sys
import logging
import logging.config
from PySide6.QtWidgets import QApplication, QMessageBox
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

    # Create login controller
    login_controller = LoginController()

    # Create and show login window
    logger.info("[UI] Opening login window...")
    login_window = LoginView(login_controller)

    # Handle successful login
    def on_login_success(user_data):
        logger.info(f"[OK] Login successful: {user_data['email']} ({user_data['role']})")
        logger.info(f"[USER] User: {user_data['ad_soyad']}")
        if user_data.get('bolum_adi'):
            logger.info(f"[DEPT] Department: {user_data['bolum_adi']} ({user_data.get('bolum_kodu', 'N/A')})")

        # Close login window
        login_window.close()
        
        # Create and show main dashboard
        logger.info("[UI] Opening main dashboard...")
        main_window = DashboardView(user_data)
        
        # Handle logout from main window
        def on_logout():
            logger.info("[LOGOUT] User logged out")
            main_window.close()
            login_window.show()
            login_window.clear()  # Clear login fields
        
        main_window.logout_requested.connect(on_logout)
        
        # Handle module changes
        def on_module_changed(module_name):
            logger.info(f"[MODULE] Switched to: {module_name}")
            # TODO: Load module content
        
        main_window.module_changed.connect(on_module_changed)
        
        # Show main window
        main_window.show()

    login_window.login_success.connect(on_login_success)

    # Show login window
    login_window.show()
    result = app.exec()
    
    if result == 0:
        logger.info("[OK] Login dialog accepted")
    else:
        logger.info("[CANCEL] Login cancelled")

    # Cleanup
    logger.info("[CLEANUP] Closing database connections...")
    db.close_all()

    logger.info("[END] Application closed")
    return result


if __name__ == "__main__":
    sys.exit(main())