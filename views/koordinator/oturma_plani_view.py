"""
Oturma Plan1 View
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QMessageBox)
from PySide6.QtCore import Signal
from controllers.oturma_controller import OturmaController
import logging

logger = logging.getLogger(__name__)


class OturmaPaniView(QWidget):
    """Oturma plan1 ekran1"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = OturmaController()
        self.init_ui()

    def init_ui(self):
        """UI olu_tur"""
        layout = QVBoxLayout()

        # Ba_l1k
        title = QLabel("Oturma Plan1")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Aç1klama
        info = QLabel("Oturma plan1 özellikleri burada olacak.")
        layout.addWidget(info)

        # Buton
        self.btn_generate = QPushButton("Oturma Plan1 Olu_tur")
        self.btn_generate.clicked.connect(self.show_generate_dialog)
        layout.addWidget(self.btn_generate)

        layout.addStretch()
        self.setLayout(layout)

    def show_generate_dialog(self):
        """Oturma plan1 olu_turma dialogu göster"""
        QMessageBox.information(
            self,
            "Bilgi",
            "Oturma plan1 olu_turma özellii yak1nda eklenecek."
        )
