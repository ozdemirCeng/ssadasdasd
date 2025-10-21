# -*- coding: utf-8 -*-
"""
Derslik View
Derslik yönetimi ekranı
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QLineEdit, QMessageBox)
from PySide6.QtCore import Signal
from controllers.derslik_controller import DerslikController
import logging

logger = logging.getLogger(__name__)


class DerslikView(QWidget):
    """Derslik yönetimi ekranı"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = DerslikController()
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()

        # Başlık
        title = QLabel("Derslik Yönetimi")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Yeni Derslik Ekle")
        self.btn_add.clicked.connect(self.show_add_derslik_dialog)
        btn_layout.addWidget(self.btn_add)
        layout.addLayout(btn_layout)

        # Tablo (gelecekte eklenecek)
        info_label = QLabel("Derslik listesi burada görüntülenecek.")
        layout.addWidget(info_label)

        layout.addStretch()
        self.setLayout(layout)

    def show_add_derslik_dialog(self):
        """Derslik ekleme dialogu göster"""
        QMessageBox.information(self, "Bilgi", "Derslik ekleme özelliği yakında eklenecek.")

    def load_derslikler(self):
        """Derslikleri yükle"""
        bolum_id = self.user_data.get('bolum_id')
        if bolum_id:
            derslikler = self.controller.get_derslikler_by_bolum(bolum_id)
            logger.info(f"{len(derslikler)} derslik yüklendi")
