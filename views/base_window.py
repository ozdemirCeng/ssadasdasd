"""
Base Window - Tüm pencerelerin kalıtım alacağı temel sınıf
"""

from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
import sys
from pathlib import Path

# Config import
sys.path.append(str(Path(__file__).parent.parent))
from config import AppConfig, RESOURCES_DIR


class BaseWindow(QMainWindow):
    """Temel pencere sınıfı"""

    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()

    def setup_window(self):
        """Pencere ayarları"""
        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")

        # Icon varsa set et
        icon_path = RESOURCES_DIR / "icons" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.closed.emit()
        super().closeEvent(event)