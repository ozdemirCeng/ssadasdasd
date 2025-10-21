"""
Ders Yükleme View
Excel'den ders listesi yükleme ekran1
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QFileDialog, QMessageBox, QTextEdit)
from PySide6.QtCore import Signal
from controllers.excel_controller import ExcelController
import logging

logger = logging.getLogger(__name__)


class DersYukleView(QWidget):
    """Ders listesi yükleme ekran1"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = ExcelController()
        self.init_ui()

    def init_ui(self):
        """UI olu_tur"""
        layout = QVBoxLayout()

        # Ba_l1k
        title = QLabel("Ders Listesi Yükleme")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Aç1klama
        info = QLabel("Excel dosyas1ndan ders listesini yükleyin.")
        layout.addWidget(info)

        # Yükleme butonu
        self.btn_upload = QPushButton("Excel Dosyas1 Seç")
        self.btn_upload.clicked.connect(self.select_file)
        layout.addWidget(self.btn_upload)

        # Sonuç alan1
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        layout.addWidget(self.result_text)

        layout.addStretch()
        self.setLayout(layout)

    def select_file(self):
        """Excel dosyas1 seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel Dosyas1 Seç",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.upload_ders_listesi(file_path)

    def upload_ders_listesi(self, file_path: str):
        """Ders listesini yükle"""
        bolum_id = self.user_data.get('bolum_id')

        if not bolum_id:
            QMessageBox.warning(self, "Uyar1", "Bölüm bilgisi bulunamad1")
            return

        self.result_text.append(f"Dosya yükleniyor: {file_path}\\n")

        success, message, basarili, hatali = self.controller.import_dersler(
            file_path, bolum_id
        )

        if success:
            self.result_text.append(f"Ba_ar1l1: {message}")
            QMessageBox.information(self, "Ba_ar1l1", message)
        else:
            self.result_text.append(f"Hata: {message}")
            QMessageBox.critical(self, "Hata", message)
