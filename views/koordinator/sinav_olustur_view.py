"""
S1nav Program1 Olu_turma View
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QMessageBox)
from PySide6.QtCore import Signal
from controllers.sinav_controller import SinavController
import logging

logger = logging.getLogger(__name__)


class SinavOlusturView(QWidget):
    """S1nav program1 olu_turma ekran1"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.controller = SinavController()
        self.init_ui()

    def init_ui(self):
        """UI olu_tur"""
        layout = QVBoxLayout()

        # Ba_l1k
        title = QLabel("S1nav Program1 Olu_turma")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Aç1klama
        info = QLabel("S1nav program1 olu_turma özellikleri burada olacak.")
        layout.addWidget(info)

        # Buton
        self.btn_create = QPushButton("Yeni S1nav Program1 Olu_tur")
        self.btn_create.clicked.connect(self.show_create_dialog)
        layout.addWidget(self.btn_create)

        layout.addStretch()
        self.setLayout(layout)

    def show_create_dialog(self):
        """S1nav program1 olu_turma dialogu göster"""
        QMessageBox.information(
            self,
            "Bilgi",
            "S1nav program1 olu_turma özellii yak1nda eklenecek."
        )
