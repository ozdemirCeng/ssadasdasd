"""
Modern Button Component
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ModernButton(QPushButton):
    """Modern button with ripple effect and smooth transitions"""

    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setObjectName("primaryBtn" if primary else "secondaryBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(54)
        self.setFont(QFont("Segoe UI", 11, QFont.DemiBold))