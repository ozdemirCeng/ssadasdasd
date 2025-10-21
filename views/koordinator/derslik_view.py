# -*- coding: utf-8 -*-
"""
Derslik View
Derslik yönetimi ekranı - Tam özellikli
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QLineEdit, QMessageBox, QDialog, QFormLayout, QSpinBox, QTableWidgetItem,
    QHeaderView, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from controllers.derslik_controller import DerslikController
import logging

logger = logging.getLogger(__name__)


class DerslikEkleDialog(QDialog):
    """Derslik ekleme/düzenleme dialogu"""

    def __init__(self, parent=None, derslik_data=None, bolum_id=None):
        super().__init__(parent)
        self.bolum_id = bolum_id
        self.derslik_data = derslik_data
        self.setWindowTitle("Derslik Düzenle" if derslik_data else "Yeni Derslik Ekle")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QFormLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Form alanları
        self.txt_kod = QLineEdit()
        self.txt_kod.setPlaceholderText("Örn: A101")
        self.txt_kod.setStyleSheet(self.get_input_style())

        self.txt_adi = QLineEdit()
        self.txt_adi.setPlaceholderText("Örn: Amfi 1")
        self.txt_adi.setStyleSheet(self.get_input_style())

        self.spin_kapasite = QSpinBox()
        self.spin_kapasite.setRange(1, 500)
        self.spin_kapasite.setValue(60)
        self.spin_kapasite.setStyleSheet(self.get_input_style())

        self.spin_satir = QSpinBox()
        self.spin_satir.setRange(1, 50)
        self.spin_satir.setValue(10)
        self.spin_satir.setStyleSheet(self.get_input_style())

        self.spin_sutun = QSpinBox()
        self.spin_sutun.setRange(1, 50)
        self.spin_sutun.setValue(6)
        self.spin_sutun.setStyleSheet(self.get_input_style())

        self.spin_sira_yapisi = QSpinBox()
        self.spin_sira_yapisi.setRange(1, 5)
        self.spin_sira_yapisi.setValue(2)
        self.spin_sira_yapisi.setSuffix("'li")
        self.spin_sira_yapisi.setStyleSheet(self.get_input_style())

        # Mevcut veri varsa doldur
        if self.derslik_data:
            self.txt_kod.setText(self.derslik_data.get('derslik_kodu', ''))
            self.txt_adi.setText(self.derslik_data.get('derslik_adi', ''))
            self.spin_kapasite.setValue(self.derslik_data.get('kapasite', 60))
            self.spin_satir.setValue(self.derslik_data.get('satir_sayisi', 10))
            self.spin_sutun.setValue(self.derslik_data.get('sutun_sayisi', 6))
            self.spin_sira_yapisi.setValue(self.derslik_data.get('sira_yapisi', 2))

        layout.addRow("Derslik Kodu:", self.txt_kod)
        layout.addRow("Derslik Adı:", self.txt_adi)
        layout.addRow("Kapasite:", self.spin_kapasite)
        layout.addRow("Satır Sayısı:", self.spin_satir)
        layout.addRow("Sütun Sayısı:", self.spin_sutun)
        layout.addRow("Sıra Yapısı:", self.spin_sira_yapisi)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_kaydet = QPushButton("💾 Kaydet")
        self.btn_kaydet.setMinimumSize(120, 40)
        self.btn_kaydet.setCursor(Qt.PointingHandCursor)
        self.btn_kaydet.setStyleSheet(self.get_button_style("#10b981"))
        self.btn_kaydet.clicked.connect(self.accept)

        btn_iptal = QPushButton("✖ İptal")
        btn_iptal.setMinimumSize(120, 40)
        btn_iptal.setCursor(Qt.PointingHandCursor)
        btn_iptal.setStyleSheet(self.get_button_style("#ef4444"))
        btn_iptal.clicked.connect(self.reject)

        btn_layout.addWidget(btn_iptal)
        btn_layout.addWidget(self.btn_kaydet)

        layout.addRow(btn_layout)

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

    def get_button_style(self, color):
        """Buton stil"""
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """

    def get_data(self):
        """Form verilerini al"""
        return {
            'derslik_kodu': self.txt_kod.text().strip(),
            'derslik_adi': self.txt_adi.text().strip(),
            'kapasite': self.spin_kapasite.value(),
            'satir_sayisi': self.spin_satir.value(),
            'sutun_sayisi': self.spin_sutun.value(),
            'sira_yapisi': self.spin_sira_yapisi.value()
        }


class DerslikView(QWidget):
    """Derslik yönetimi ekranı - Tam özellikli"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = DerslikController()
        self.derslikler = []
        self.init_ui()
        self.load_derslikler()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("🏛 Derslik Yönetimi")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #111827;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addWidget(header)

        # Toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(12)

        # Arama
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Derslik ara...")
        self.txt_search.setFixedHeight(44)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                padding: 0 16px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #10b981;
            }
        """)
        self.txt_search.textChanged.connect(self.filter_derslikler)

        # Butonlar
        self.btn_ekle = QPushButton("➕ Yeni Derslik")
        self.btn_ekle.setFixedHeight(44)
        self.btn_ekle.setMinimumWidth(140)
        self.btn_ekle.setCursor(Qt.PointingHandCursor)
        self.btn_ekle.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #14b8a6);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #0d9488);
            }
        """)
        self.btn_ekle.clicked.connect(self.add_derslik)

        self.btn_yenile = QPushButton("🔄 Yenile")
        self.btn_yenile.setFixedHeight(44)
        self.btn_yenile.setMinimumWidth(100)
        self.btn_yenile.setCursor(Qt.PointingHandCursor)
        self.btn_yenile.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        self.btn_yenile.clicked.connect(self.load_derslikler)

        toolbar_layout.addWidget(self.txt_search)
        toolbar_layout.addWidget(self.btn_yenile)
        toolbar_layout.addWidget(self.btn_ekle)

        layout.addWidget(toolbar)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Kod", "Derslik Adı", "Kapasite", "Satır", "Sütun", "Sıra Yapısı", "Durum", "İşlemler"
        ])

        # Tablo stil
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: #f3f4f6;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #f9fafb;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #374151;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.table)

    def load_derslikler(self):
        """Derslikleri yükle"""
        try:
            bolum_id = self.user_data.get('bolum_id', 1)  # Test için 1
            self.derslikler = self.controller.get_derslikler_by_bolum(bolum_id)
            self.populate_table(self.derslikler)
            logger.info(f"{len(self.derslikler)} derslik yüklendi")
        except Exception as e:
            logger.error(f"Derslik yükleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Derslikler yüklenemedi:\n{str(e)}")

    def populate_table(self, derslikler):
        """Tabloyu doldur"""
        self.table.setRowCount(len(derslikler))

        for i, derslik in enumerate(derslikler):
            # Kod
            self.table.setItem(i, 0, QTableWidgetItem(derslik['derslik_kodu']))

            # Ad
            self.table.setItem(i, 1, QTableWidgetItem(derslik['derslik_adi']))

            # Kapasite
            self.table.setItem(i, 2, QTableWidgetItem(str(derslik['kapasite'])))

            # Satır
            self.table.setItem(i, 3, QTableWidgetItem(str(derslik['satir_sayisi'])))

            # Sütun
            self.table.setItem(i, 4, QTableWidgetItem(str(derslik['sutun_sayisi'])))

            # Sıra yapısı
            self.table.setItem(i, 5, QTableWidgetItem(f"{derslik['sira_yapisi']}'li"))

            # Durum
            durum = "✅ Aktif" if derslik.get('aktif', True) else "❌ Pasif"
            self.table.setItem(i, 6, QTableWidgetItem(durum))

            # İşlemler
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(8)

            btn_duzenle = QPushButton("✏️")
            btn_duzenle.setFixedSize(32, 32)
            btn_duzenle.setCursor(Qt.PointingHandCursor)
            btn_duzenle.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            """)
            btn_duzenle.clicked.connect(lambda checked, d=derslik: self.edit_derslik(d))

            btn_sil = QPushButton("🗑️")
            btn_sil.setFixedSize(32, 32)
            btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #dc2626;
                }
            """)
            btn_sil.clicked.connect(lambda checked, d=derslik: self.delete_derslik(d))

            btn_layout.addWidget(btn_duzenle)
            btn_layout.addWidget(btn_sil)
            btn_layout.addStretch()

            self.table.setCellWidget(i, 7, btn_widget)

    def filter_derslikler(self):
        """Derslikleri filtrele"""
        search_text = self.txt_search.text().lower()
        if not search_text:
            self.populate_table(self.derslikler)
            return

        filtered = [
            d for d in self.derslikler
            if search_text in d['derslik_kodu'].lower() or
               search_text in d['derslik_adi'].lower()
        ]
        self.populate_table(filtered)

    def add_derslik(self):
        """Yeni derslik ekle"""
        bolum_id = self.user_data.get('bolum_id', 1)  # Test için 1
        dialog = DerslikEkleDialog(self, bolum_id=bolum_id)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['derslik_kodu'] or not data['derslik_adi']:
                QMessageBox.warning(self, "Uyarı", "Derslik kodu ve adı zorunludur!")
                return

            success, message, derslik_id = self.controller.create_derslik(
                bolum_id=bolum_id,
                derslik_kodu=data['derslik_kodu'],
                derslik_adi=data['derslik_adi'],
                kapasite=data['kapasite'],
                satir_sayisi=data['satir_sayisi'],
                sutun_sayisi=data['sutun_sayisi'],
                sira_yapisi=data['sira_yapisi']
            )

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_derslikler()
            else:
                QMessageBox.critical(self, "Hata", message)

    def edit_derslik(self, derslik):
        """Derslik düzenle"""
        dialog = DerslikEkleDialog(self, derslik_data=derslik)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            success, message = self.controller.update_derslik(
                derslik['derslik_id'],
                **data
            )

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_derslikler()
            else:
                QMessageBox.critical(self, "Hata", message)

    def delete_derslik(self, derslik):
        """Derslik sil"""
        reply = QMessageBox.question(
            self,
            "Derslik Sil",
            f"{derslik['derslik_kodu']} - {derslik['derslik_adi']} dersliğini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.controller.delete_derslik(derslik['derslik_id'])

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_derslikler()
            else:
                QMessageBox.critical(self, "Hata", message)
