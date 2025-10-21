# -*- coding: utf-8 -*-
"""
Öğrenci Yükleme View
Excel'den öğrenci listesi yükleme ekranı
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QFileDialog, QMessageBox, QTextEdit)
from PySide6.QtCore import Signal
from controllers.excel_controller import ExcelController
import logging

logger = logging.getLogger(__name__)


class OgrenciYukleView(QWidget):
    """Öğrenci listesi yükleme ekranı"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = ExcelController()
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()

        # Başlık
        title = QLabel("Öğrenci Listesi Yükleme")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Açıklama
        info = QLabel("Excel dosyasından öğrenci listesini yükleyin.")
        layout.addWidget(info)

        # Yükleme butonu
        self.btn_upload = QPushButton("Excel Dosyası Seç")
        self.btn_upload.clicked.connect(self.select_file)
        layout.addWidget(self.btn_upload)

        # Sonuç alanı
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        layout.addWidget(self.result_text)

        layout.addStretch()
        self.setLayout(layout)

    def select_file(self):
        """Excel dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel Dosyası Seç",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.upload_ogrenci_listesi(file_path)

    def upload_ogrenci_listesi(self, file_path: str):
        """Öğrenci listesini yükle"""
        bolum_id = self.user_data.get('bolum_id')

        if not bolum_id:
            QMessageBox.warning(self, "Uyarı", "Bölüm bilgisi bulunamadı")
            return

        self.result_text.append(f"Dosya yükleniyor: {file_path}\n")

        success, message, basarili, hatali = self.controller.import_ogrenciler(
            file_path, bolum_id
        )

        if success:
            self.result_text.append(f"Başarılı: {message}")
            QMessageBox.information(self, "Başarılı", message)
        else:
            self.result_text.append(f"Hata: {message}")
            QMessageBox.critical(self, "Hata", message)
