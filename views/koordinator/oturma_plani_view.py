# -*- coding: utf-8 -*-
"""
Oturma Planı View
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QMessageBox)
from PySide6.QtCore import Signal
from controllers.oturma_controller import OturmaController
import logging

logger = logging.getLogger(__name__)


class OturmaPaniView(QWidget):
    """Oturma planı ekranı"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = OturmaController()
        self.init_ui()

    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()

        # Başlık
        title = QLabel("Oturma Planı")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Açıklama
        info = QLabel("Oturma planı özellikleri burada olacak.")
        layout.addWidget(info)

        # Buton
        self.btn_generate = QPushButton("Oturma Planı Oluştur")
        self.btn_generate.clicked.connect(self.show_generate_dialog)
        layout.addWidget(self.btn_generate)

        layout.addStretch()
        self.setLayout(layout)

    def show_generate_dialog(self):
        """Oturma planı oluşturma dialogu göster"""
        QMessageBox.information(
            self,
            "Bilgi",
            "Oturma planı oluşturma özelliği yakında eklenecek."
        )
