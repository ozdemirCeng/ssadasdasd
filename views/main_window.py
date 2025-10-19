"""
Main Window - Ana uygulama penceresi
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QStackedWidget,
    QMenuBar, QStatusBar, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from utils.logger import logger


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """UI'yi başlat"""
        self.setWindowTitle(f"Kocaeli Üniversitesi - Sınav Takvimi Sistemi - {self.user_data['ad_soyad']}")
        self.setMinimumSize(1200, 800)
        
        # Menu bar
        self.create_menu_bar()
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Hoş geldin mesajı
        welcome_label = QLabel(f"Hoş Geldiniz, {self.user_data['ad_soyad']}")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00A651;
                padding: 20px;
                background: rgba(0, 166, 81, 0.1);
                border-radius: 10px;
                border: 2px solid #00A651;
            }
        """)
        main_layout.addWidget(welcome_label)
        
        # Kullanıcı bilgileri
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        
        # Kullanıcı detayları
        user_info = QLabel(f"""
        <b>Kullanıcı Bilgileri:</b><br>
        E-posta: {self.user_data['email']}<br>
        Rol: {self.user_data['role']}<br>
        Bölüm ID: {self.user_data['bolum_id']}
        """)
        user_info.setStyleSheet("font-size: 14px; color: #333;")
        info_layout.addWidget(user_info)
        
        info_layout.addStretch()
        
        # Çıkış butonu
        logout_btn = QPushButton("Çıkış Yap")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        info_layout.addWidget(logout_btn)
        
        main_layout.addWidget(info_frame)
        
        # Ana içerik alanı
        content_label = QLabel("Ana içerik buraya gelecek...")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #666;
                padding: 50px;
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(content_label)
        
        main_layout.addStretch()
        
        # Status bar
        self.statusBar().showMessage(f"Kullanıcı: {self.user_data['ad_soyad']} | Rol: {self.user_data['role']}")
        
        logger.info(f"Ana pencere açıldı: {self.user_data['ad_soyad']}")
        
    def create_menu_bar(self):
        """Menu bar oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        
        # Görünüm menüsü
        view_menu = menubar.addMenu('Görünüm')
        
        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        
    def apply_theme(self):
        """Tema uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMenuBar {
                background: #00A651;
                color: white;
                border: none;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.2);
            }
            QStatusBar {
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
                color: #666;
            }
        """)
        
    def logout(self):
        """Çıkış yap"""
        logger.info(f"Kullanıcı çıkış yaptı: {self.user_data['ad_soyad']}")
        self.close()
        
        # Login penceresini tekrar aç
        from views.login_view import LoginView
        from controllers.login_controller import LoginController
        
        login_controller = LoginController()
        login_window = LoginView(login_controller)
        login_window.show()
        
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        logger.info("Ana pencere kapatıldı")
        event.accept()



