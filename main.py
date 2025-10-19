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
        if user_data['bolum_adi']:
            logger.info(f"[DEPT] Department: {user_data['bolum_adi']} ({user_data['bolum_kodu']})")

        # TODO: Open main window
        # main_window = MainWindow(user_data)
        # main_window.show()

        # Temporary success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Giriş Başarılı")
        msg.setText(f"Hoş geldiniz, {user_data['ad_soyad']}!")
        msg.setInformativeText(
            f"Rol: {user_data['role']}\n"
            f"E-posta: {user_data['email']}\n"
            f"Bölüm: {user_data['bolum_adi'] or 'Admin'}"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

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