# -*- coding: utf-8 -*-
"""
Sınav Programı Oluşturma View - Tam özellikli
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QCheckBox,
    QListWidget, QListWidgetItem, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from controllers.sinav_controller import SinavController
from models.database import db
from models.ders_model import DersModel
from models.sinav_model import SinavModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProgramOlusturDialog(QDialog):
    """Yeni sınav programı oluşturma dialogu"""

    def __init__(self, parent=None, bolum_id=None):
        super().__init__(parent)
        self.bolum_id = bolum_id
        self.setWindowTitle("Yeni Sınav Programı Oluştur")
        self.setMinimumSize(600, 500)
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Program adı
        self.txt_program_adi = QLineEdit()
        self.txt_program_adi.setPlaceholderText("Örn: 2024 Bahar Dönemi Ara Sınav")
        self.txt_program_adi.setStyleSheet(self.get_input_style())
        form_layout.addRow("Program Adı:", self.txt_program_adi)

        # Sınav tipi
        self.cmb_sinav_tipi = QComboBox()
        self.cmb_sinav_tipi.addItems(["Ara Sınav", "Final", "Bütünleme", "Mazeret"])
        self.cmb_sinav_tipi.setStyleSheet(self.get_input_style())
        form_layout.addRow("Sınav Tipi:", self.cmb_sinav_tipi)

        # Tarih aralığı
        self.date_baslangic = QDateEdit()
        self.date_baslangic.setCalendarPopup(True)
        self.date_baslangic.setDate(QDate.currentDate())
        self.date_baslangic.setStyleSheet(self.get_input_style())
        form_layout.addRow("Başlangıç Tarihi:", self.date_baslangic)

        self.date_bitis = QDateEdit()
        self.date_bitis.setCalendarPopup(True)
        self.date_bitis.setDate(QDate.currentDate().addDays(14))
        self.date_bitis.setStyleSheet(self.get_input_style())
        form_layout.addRow("Bitiş Tarihi:", self.date_bitis)

        # Sınav süresi
        self.spin_sinav_suresi = QSpinBox()
        self.spin_sinav_suresi.setRange(30, 240)
        self.spin_sinav_suresi.setValue(75)
        self.spin_sinav_suresi.setSuffix(" dakika")
        self.spin_sinav_suresi.setStyleSheet(self.get_input_style())
        form_layout.addRow("Varsayılan Sınav Süresi:", self.spin_sinav_suresi)

        # Bekleme süresi
        self.spin_bekleme_suresi = QSpinBox()
        self.spin_bekleme_suresi.setRange(0, 60)
        self.spin_bekleme_suresi.setValue(15)
        self.spin_bekleme_suresi.setSuffix(" dakika")
        self.spin_bekleme_suresi.setStyleSheet(self.get_input_style())
        form_layout.addRow("Bekleme Süresi:", self.spin_bekleme_suresi)

        layout.addLayout(form_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_iptal = QPushButton("✖ İptal")
        btn_iptal.setMinimumSize(120, 40)
        btn_iptal.setCursor(Qt.PointingHandCursor)
        btn_iptal.setStyleSheet(self.get_button_style("#ef4444"))
        btn_iptal.clicked.connect(self.reject)

        btn_olustur = QPushButton("✓ Oluştur")
        btn_olustur.setMinimumSize(120, 40)
        btn_olustur.setCursor(Qt.PointingHandCursor)
        btn_olustur.setStyleSheet(self.get_button_style("#10b981"))
        btn_olustur.clicked.connect(self.accept)

        btn_layout.addWidget(btn_iptal)
        btn_layout.addWidget(btn_olustur)

        layout.addLayout(btn_layout)

    def get_input_style(self):
        """Input stil"""
        return """
            QLineEdit, QSpinBox, QDateEdit, QComboBox {
                padding: 10px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus, QComboBox:focus {
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
            'program_adi': self.txt_program_adi.text().strip(),
            'sinav_tipi': self.cmb_sinav_tipi.currentText(),
            'baslangic_tarihi': self.date_baslangic.date().toPython(),
            'bitis_tarihi': self.date_bitis.date().toPython(),
            'varsayilan_sinav_suresi': self.spin_sinav_suresi.value(),
            'bekleme_suresi': self.spin_bekleme_suresi.value()
        }


class DersSecDialog(QDialog):
    """Ders seçim dialogu"""

    def __init__(self, parent=None, bolum_id=None):
        super().__init__(parent)
        self.bolum_id = bolum_id
        self.ders_model = DersModel(db)
        self.setWindowTitle("Sınava Dahil Edilecek Dersleri Seçin")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_dersler()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Bilgi
        info = QLabel("Sınav programına dahil edilecek dersleri seçin:")
        info.setFont(QFont("Segoe UI", 11))
        layout.addWidget(info)

        # Hepsi seç butonu
        btn_hepsi = QPushButton("Tümünü Seç / Temizle")
        btn_hepsi.clicked.connect(self.toggle_all)
        btn_hepsi.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(btn_hepsi)

        # Ders listesi
        self.list_dersler = QListWidget()
        self.list_dersler.setStyleSheet("""
            QListWidget {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QListWidget::item:hover {
                background: #f3f4f6;
            }
        """)
        layout.addWidget(self.list_dersler)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_iptal = QPushButton("✖ İptal")
        btn_iptal.setMinimumSize(120, 40)
        btn_iptal.setCursor(Qt.PointingHandCursor)
        btn_iptal.setStyleSheet(self.get_button_style("#ef4444"))
        btn_iptal.clicked.connect(self.reject)

        btn_devam = QPushButton("✓ Devam Et")
        btn_devam.setMinimumSize(120, 40)
        btn_devam.setCursor(Qt.PointingHandCursor)
        btn_devam.setStyleSheet(self.get_button_style("#10b981"))
        btn_devam.clicked.connect(self.accept)

        btn_layout.addWidget(btn_iptal)
        btn_layout.addWidget(btn_devam)

        layout.addLayout(btn_layout)

    def load_dersler(self):
        """Dersleri yükle"""
        try:
            dersler = self.ders_model.get_dersler_by_bolum(self.bolum_id or 1)
            for ders in dersler:
                item = QListWidgetItem(f"{ders['ders_kodu']} - {ders['ders_adi']}")
                item.setCheckState(Qt.Checked)
                item.setData(Qt.UserRole, ders['ders_id'])
                self.list_dersler.addItem(item)
        except Exception as e:
            logger.error(f"Ders yükleme hatası: {e}")

    def toggle_all(self):
        """Tümünü seç/temizle"""
        if self.list_dersler.count() == 0:
            return

        # İlk öğeye bakarak durumu belirle
        first_item = self.list_dersler.item(0)
        new_state = Qt.Unchecked if first_item.checkState() == Qt.Checked else Qt.Checked

        for i in range(self.list_dersler.count()):
            self.list_dersler.item(i).setCheckState(new_state)

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

    def get_selected_ders_ids(self):
        """Seçili ders ID'lerini al"""
        selected_ids = []
        for i in range(self.list_dersler.count()):
            item = self.list_dersler.item(i)
            if item.checkState() == Qt.Checked:
                selected_ids.append(item.data(Qt.UserRole))
        return selected_ids


class SinavOlusturView(QWidget):
    """Sınav programı oluşturma ekranı - Tam özellikli"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = SinavController()
        self.sinav_model = SinavModel(db)
        self.programlar = []
        self.init_ui()
        self.load_programlar()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📅 Sınav Programı Yönetimi")
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

        toolbar_layout.addStretch()

        btn_yenile = QPushButton("🔄 Yenile")
        btn_yenile.setFixedHeight(44)
        btn_yenile.setMinimumWidth(100)
        btn_yenile.setCursor(Qt.PointingHandCursor)
        btn_yenile.setStyleSheet("""
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
        btn_yenile.clicked.connect(self.load_programlar)

        btn_yeni = QPushButton("➕ Yeni Program Oluştur")
        btn_yeni.setFixedHeight(44)
        btn_yeni.setMinimumWidth(180)
        btn_yeni.setCursor(Qt.PointingHandCursor)
        btn_yeni.setStyleSheet("""
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
        btn_yeni.clicked.connect(self.create_program)

        toolbar_layout.addWidget(btn_yenile)
        toolbar_layout.addWidget(btn_yeni)

        layout.addWidget(toolbar)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Program Adı", "Sınav Tipi", "Başlangıç", "Bitiş", "Sınav Sayısı", "Durum", "İşlemler"
        ])

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

    def load_programlar(self):
        """Programları yükle"""
        try:
            bolum_id = self.user_data.get('bolum_id', 1)
            self.programlar = self.controller.get_programs_by_bolum(bolum_id)
            self.populate_table()
            logger.info(f"{len(self.programlar)} program yüklendi")
        except Exception as e:
            logger.error(f"Program yükleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Programlar yüklenemedi:\n{str(e)}")

    def populate_table(self):
        """Tabloyu doldur"""
        self.table.setRowCount(len(self.programlar))

        for i, program in enumerate(self.programlar):
            # Program adı
            self.table.setItem(i, 0, QTableWidgetItem(program['program_adi']))

            # Sınav tipi
            self.table.setItem(i, 1, QTableWidgetItem(program['sinav_tipi']))

            # Başlangıç
            bas_tarih = program['baslangic_tarihi']
            if isinstance(bas_tarih, str):
                bas_str = bas_tarih
            else:
                bas_str = bas_tarih.strftime("%d.%m.%Y")
            self.table.setItem(i, 2, QTableWidgetItem(bas_str))

            # Bitiş
            bit_tarih = program['bitis_tarihi']
            if isinstance(bit_tarih, str):
                bit_str = bit_tarih
            else:
                bit_str = bit_tarih.strftime("%d.%m.%Y")
            self.table.setItem(i, 3, QTableWidgetItem(bit_str))

            # Sınav sayısı (DB'den alalım)
            sinav_sayisi = len(self.controller.get_sinavlar_by_program(program['program_id']))
            self.table.setItem(i, 4, QTableWidgetItem(str(sinav_sayisi)))

            # Durum
            durum = "✅ Aktif" if program.get('aktif', True) else "❌ Pasif"
            self.table.setItem(i, 5, QTableWidgetItem(durum))

            # İşlemler
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(8)

            btn_olustur = QPushButton("📝")
            btn_olustur.setFixedSize(32, 32)
            btn_olustur.setCursor(Qt.PointingHandCursor)
            btn_olustur.setToolTip("Sınavları Oluştur")
            btn_olustur.setStyleSheet("""
                QPushButton {
                    background: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #059669;
                }
            """)
            btn_olustur.clicked.connect(lambda checked, p=program: self.generate_sinavlar(p))

            btn_goruntule = QPushButton("👁️")
            btn_goruntule.setFixedSize(32, 32)
            btn_goruntule.setCursor(Qt.PointingHandCursor)
            btn_goruntule.setToolTip("Sınavları Görüntüle")
            btn_goruntule.setStyleSheet("""
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
            btn_goruntule.clicked.connect(lambda checked, p=program: self.view_sinavlar(p))

            btn_sil = QPushButton("🗑️")
            btn_sil.setFixedSize(32, 32)
            btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.setToolTip("Programı Sil")
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
            btn_sil.clicked.connect(lambda checked, p=program: self.delete_program(p))

            btn_layout.addWidget(btn_olustur)
            btn_layout.addWidget(btn_goruntule)
            btn_layout.addWidget(btn_sil)
            btn_layout.addStretch()

            self.table.setCellWidget(i, 6, btn_widget)

    def create_program(self):
        """Yeni program oluştur"""
        bolum_id = self.user_data.get('bolum_id', 1)
        dialog = ProgramOlusturDialog(self, bolum_id=bolum_id)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['program_adi']:
                QMessageBox.warning(self, "Uyarı", "Program adı zorunludur!")
                return

            success, message, program_id = self.controller.create_program(
                bolum_id=bolum_id,
                program_adi=data['program_adi'],
                sinav_tipi=data['sinav_tipi'],
                baslangic_tarihi=data['baslangic_tarihi'],
                bitis_tarihi=data['bitis_tarihi'],
                varsayilan_sinav_suresi=data['varsayilan_sinav_suresi'],
                bekleme_suresi=data['bekleme_suresi']
            )

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_programlar()
            else:
                QMessageBox.critical(self, "Hata", message)

    def generate_sinavlar(self, program):
        """Sınavları otomatik oluştur"""
        bolum_id = self.user_data.get('bolum_id', 1)

        # Ders seçim dialogu
        ders_dialog = DersSecDialog(self, bolum_id=bolum_id)

        if ders_dialog.exec() == QDialog.Accepted:
            ders_ids = ders_dialog.get_selected_ders_ids()

            if not ders_ids:
                QMessageBox.warning(self, "Uyarı", "En az bir ders seçmelisiniz!")
                return

            # Sınavları oluştur
            success, message = self.controller.generate_sinav_programi(
                program_id=program['program_id'],
                ders_ids=ders_ids
            )

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_programlar()
            else:
                QMessageBox.critical(self, "Hata", message)

    def view_sinavlar(self, program):
        """Sınavları görüntüle"""
        sinavlar = self.controller.get_sinavlar_by_program(program['program_id'])

        if not sinavlar:
            QMessageBox.information(self, "Bilgi", "Bu programa ait sınav bulunmuyor.")
            return

        # Basit bir tablo dialogu
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{program['program_adi']} - Sınavlar")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Ders", "Tarih", "Saat", "Derslik", "Öğrenci"])
        table.setRowCount(len(sinavlar))

        for i, sinav in enumerate(sinavlar):
            table.setItem(i, 0, QTableWidgetItem(sinav.get('ders_adi', 'N/A')))

            tarih = sinav.get('tarih')
            if isinstance(tarih, str):
                tarih_str = tarih
            else:
                tarih_str = tarih.strftime("%d.%m.%Y") if tarih else "N/A"
            table.setItem(i, 1, QTableWidgetItem(tarih_str))

            bas_saat = sinav.get('baslangic_saati')
            bit_saat = sinav.get('bitis_saati')
            saat_str = f"{bas_saat} - {bit_saat}" if bas_saat and bit_saat else "N/A"
            table.setItem(i, 2, QTableWidgetItem(saat_str))

            table.setItem(i, 3, QTableWidgetItem(sinav.get('derslik_adi', 'Atanmadı')))
            table.setItem(i, 4, QTableWidgetItem(str(sinav.get('ogrenci_sayisi', 0))))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)

        btn_kapat = QPushButton("Kapat")
        btn_kapat.clicked.connect(dialog.accept)
        layout.addWidget(btn_kapat)

        dialog.exec()

    def delete_program(self, program):
        """Programı sil"""
        reply = QMessageBox.question(
            self,
            "Program Sil",
            f"{program['program_adi']} programını silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.controller.delete_program(program['program_id'])

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_programlar()
            else:
                QMessageBox.critical(self, "Hata", message)
