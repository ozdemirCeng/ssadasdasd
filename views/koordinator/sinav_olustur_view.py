# -*- coding: utf-8 -*-
"""
Sınav Programı Oluşturma View
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QMessageBox)
from PySide6.QtCore import Signal
from controllers.sinav_controller import SinavController
import logging

logger = logging.getLogger(__name__)


class SinavOlusturView(QWidget):
    """Sınav programı oluşturma ekranı"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = SinavController()
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()

        # Başlık
        title = QLabel("Sınav Programı Oluşturma")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Açıklama
        info = QLabel("Sınav programı oluşturma özellikleri burada olacak.")
        layout.addWidget(info)

        # Buton
        self.btn_create = QPushButton("Yeni Sınav Programı Oluştur")
        self.btn_create.clicked.connect(self.show_create_dialog)
        layout.addWidget(self.btn_create)

        layout.addStretch()
        self.setLayout(layout)

    def show_create_dialog(self):
        """Sınav programı oluşturma dialogu göster"""
        QMessageBox.information(
            self,
            "Bilgi",
            "Sınav programı oluşturma özelliği yakında eklenecek."
        )
