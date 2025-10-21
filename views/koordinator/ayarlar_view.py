# -*- coding: utf-8 -*-
"""
Ayarlar View - Tam özellikli
Kullanıcı ve sistem ayarları
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QLineEdit, QGroupBox, QMessageBox, QSpinBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from models.database import db
from models.user_model import UserModel
import logging

logger = logging.getLogger(__name__)


class SettingGroup(QGroupBox):
    """Ayar grubu"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 12px;
                padding: 16px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #374151;
            }
        """)


class AyarlarView(QWidget):
    """Ayarlar ekranı - Tam özellikli"""

    settings_changed = Signal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """UI oluştur"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("⚙ Ayarlar")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #111827;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addWidget(header)

        # Kullanıcı bilgileri
        user_group = SettingGroup("Kullanıcı Bilgileri")
        user_layout = QVBoxLayout()

        # Ad Soyad
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Ad Soyad:"))
        self.txt_name = QLineEdit()
        self.txt_name.setStyleSheet(self.get_input_style())
        name_layout.addWidget(self.txt_name)
        user_layout.addLayout(name_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("E-posta:"))
        self.txt_email = QLineEdit()
        self.txt_email.setReadOnly(True)  # Email değiştirilemez
        self.txt_email.setStyleSheet(self.get_input_style() + "background: #f3f4f6;")
        email_layout.addWidget(self.txt_email)
        user_layout.addLayout(email_layout)

        # Rol
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Rol:"))
        self.txt_role = QLineEdit()
        self.txt_role.setReadOnly(True)
        self.txt_role.setStyleSheet(self.get_input_style() + "background: #f3f4f6;")
        role_layout.addWidget(self.txt_role)
        user_layout.addLayout(role_layout)

        user_group.setLayout(user_layout)
        layout.addWidget(user_group)

        # Şifre değiştir
        password_group = SettingGroup("Şifre Değiştir")
        password_layout = QVBoxLayout()

        # Mevcut şifre
        current_pw_layout = QHBoxLayout()
        current_pw_layout.addWidget(QLabel("Mevcut Şifre:"))
        self.txt_current_pw = QLineEdit()
        self.txt_current_pw.setEchoMode(QLineEdit.Password)
        self.txt_current_pw.setStyleSheet(self.get_input_style())
        current_pw_layout.addWidget(self.txt_current_pw)
        password_layout.addLayout(current_pw_layout)

        # Yeni şifre
        new_pw_layout = QHBoxLayout()
        new_pw_layout.addWidget(QLabel("Yeni Şifre:"))
        self.txt_new_pw = QLineEdit()
        self.txt_new_pw.setEchoMode(QLineEdit.Password)
        self.txt_new_pw.setStyleSheet(self.get_input_style())
        new_pw_layout.addWidget(self.txt_new_pw)
        password_layout.addLayout(new_pw_layout)

        # Yeni şifre tekrar
        confirm_pw_layout = QHBoxLayout()
        confirm_pw_layout.addWidget(QLabel("Yeni Şifre (Tekrar):"))
        self.txt_confirm_pw = QLineEdit()
        self.txt_confirm_pw.setEchoMode(QLineEdit.Password)
        self.txt_confirm_pw.setStyleSheet(self.get_input_style())
        confirm_pw_layout.addWidget(self.txt_confirm_pw)
        password_layout.addLayout(confirm_pw_layout)

        # Şifre değiştir butonu
        btn_change_pw = QPushButton("🔑 Şifreyi Değiştir")
        btn_change_pw.setMinimumHeight(44)
        btn_change_pw.setCursor(Qt.PointingHandCursor)
        btn_change_pw.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        btn_change_pw.clicked.connect(self.change_password)
        password_layout.addWidget(btn_change_pw)

        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # Sistem ayarları
        system_group = SettingGroup("Sistem Ayarları")
        system_layout = QVBoxLayout()

        # Varsayılan sınav süresi
        sinav_suresi_layout = QHBoxLayout()
        sinav_suresi_layout.addWidget(QLabel("Varsayılan Sınav Süresi:"))
        self.spin_sinav_suresi = QSpinBox()
        self.spin_sinav_suresi.setRange(30, 240)
        self.spin_sinav_suresi.setValue(75)
        self.spin_sinav_suresi.setSuffix(" dakika")
        self.spin_sinav_suresi.setStyleSheet(self.get_input_style())
        sinav_suresi_layout.addWidget(self.spin_sinav_suresi)
        sinav_suresi_layout.addStretch()
        system_layout.addLayout(sinav_suresi_layout)

        # Bekleme süresi
        bekleme_layout = QHBoxLayout()
        bekleme_layout.addWidget(QLabel("Sınavlar Arası Bekleme:"))
        self.spin_bekleme = QSpinBox()
        self.spin_bekleme.setRange(0, 60)
        self.spin_bekleme.setValue(15)
        self.spin_bekleme.setSuffix(" dakika")
        self.spin_bekleme.setStyleSheet(self.get_input_style())
        bekleme_layout.addWidget(self.spin_bekleme)
        bekleme_layout.addStretch()
        system_layout.addLayout(bekleme_layout)

        # Otomatik yedekleme
        self.chk_auto_backup = QCheckBox("Otomatik veritabanı yedeği al")
        self.chk_auto_backup.setFont(QFont("Segoe UI", 10))
        system_layout.addWidget(self.chk_auto_backup)

        # E-posta bildirimleri
        self.chk_email_notif = QCheckBox("E-posta bildirimleri gönder")
        self.chk_email_notif.setFont(QFont("Segoe UI", 10))
        system_layout.addWidget(self.chk_email_notif)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Veritabanı işlemleri
        db_group = SettingGroup("Veritabanı")
        db_layout = QVBoxLayout()

        db_info = QLabel("Veritabanı işlemleri dikkatli kullanılmalıdır.")
        db_info.setFont(QFont("Segoe UI", 10))
        db_info.setStyleSheet("color: #f59e0b;")
        db_layout.addWidget(db_info)

        db_buttons = QHBoxLayout()

        btn_backup = QPushButton("💾 Yedek Al")
        btn_backup.setMinimumHeight(40)
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_backup.clicked.connect(self.backup_database)

        btn_restore = QPushButton("📥 Geri Yükle")
        btn_restore.setMinimumHeight(40)
        btn_restore.setCursor(Qt.PointingHandCursor)
        btn_restore.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        btn_restore.clicked.connect(self.restore_database)

        db_buttons.addWidget(btn_backup)
        db_buttons.addWidget(btn_restore)
        db_buttons.addStretch()

        db_layout.addLayout(db_buttons)
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        # Kaydet butonu
        btn_save = QPushButton("💾 Ayarları Kaydet")
        btn_save.setMinimumHeight(50)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #14b8a6);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #0d9488);
            }
        """)
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def get_input_style(self):
        """Input stil"""
        return """
            QLineEdit, QSpinBox {
                padding: 10px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #10b981;
            }
        """

    def load_settings(self):
        """Ayarları yükle"""
        try:
            self.txt_name.setText(self.user_data.get('ad_soyad', ''))
            self.txt_email.setText(self.user_data.get('email', ''))
            self.txt_role.setText(self.user_data.get('role', ''))

            # Sistem ayarları (örnek değerler)
            self.chk_auto_backup.setChecked(True)
            self.chk_email_notif.setChecked(False)

        except Exception as e:
            logger.error(f"Ayar yükleme hatası: {e}")

    def save_settings(self):
        """Ayarları kaydet"""
        try:
            new_name = self.txt_name.text().strip()

            if not new_name:
                QMessageBox.warning(self, "Uyarı", "Ad soyad boş olamaz!")
                return

            # Kullanıcı bilgilerini güncelle
            success = self.user_model.update_user(
                self.user_data['user_id'],
                ad_soyad=new_name
            )

            if success:
                self.user_data['ad_soyad'] = new_name
                self.settings_changed.emit()
                QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!")
            else:
                QMessageBox.critical(self, "Hata", "Ayarlar kaydedilemedi!")

        except Exception as e:
            logger.error(f"Ayar kaydetme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilemedi:\n{str(e)}")

    def change_password(self):
        """Şifre değiştir"""
        try:
            current_pw = self.txt_current_pw.text()
            new_pw = self.txt_new_pw.text()
            confirm_pw = self.txt_confirm_pw.text()

            if not current_pw or not new_pw or not confirm_pw:
                QMessageBox.warning(self, "Uyarı", "Tüm alanları doldurun!")
                return

            if new_pw != confirm_pw:
                QMessageBox.warning(self, "Uyarı", "Yeni şifreler eşleşmiyor!")
                return

            if len(new_pw) < 6:
                QMessageBox.warning(self, "Uyarı", "Şifre en az 6 karakter olmalıdır!")
                return

            # Şifreyi değiştir
            success = self.user_model.change_password(
                self.user_data['user_id'],
                current_pw,
                new_pw
            )

            if success:
                QMessageBox.information(self, "Başarılı", "Şifre başarıyla değiştirildi!")
                self.txt_current_pw.clear()
                self.txt_new_pw.clear()
                self.txt_confirm_pw.clear()
            else:
                QMessageBox.critical(self, "Hata", "Mevcut şifre yanlış!")

        except Exception as e:
            logger.error(f"Şifre değiştirme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Şifre değiştirilemedi:\n{str(e)}")

    def backup_database(self):
        """Veritabanı yedeği al"""
        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime
        import subprocess

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Yedek Dosyası Kaydet",
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            "SQL Files (*.sql)"
        )

        if filename:
            try:
                # PostgreSQL yedek alma komutu (pg_dump)
                # NOT: Bu örnek bir implementasyon, gerçek durumda config'den alınmalı
                QMessageBox.information(
                    self,
                    "Bilgi",
                    "Veritabanı yedeği özelliği geliştirilme aşamasındadır.\n\n"
                    "Manuel yedek almak için:\npg_dump -U postgres sinav_takvimi > backup.sql"
                )
            except Exception as e:
                logger.error(f"Yedek alma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Yedek alınamadı:\n{str(e)}")

    def restore_database(self):
        """Veritabanını geri yükle"""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Yedek Dosyası Seç",
            "",
            "SQL Files (*.sql)"
        )

        if filename:
            reply = QMessageBox.question(
                self,
                "Geri Yükleme",
                "Mevcut veritabanı silinecek ve yedek yüklenecek.\n\nDevam etmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self,
                    "Bilgi",
                    "Veritabanı geri yükleme özelliği geliştirilme aşamasındadır.\n\n"
                    "Manuel geri yükleme için:\npsql -U postgres sinav_takvimi < backup.sql"
                )
