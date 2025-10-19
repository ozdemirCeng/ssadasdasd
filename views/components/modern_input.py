"""
Modern Input Field Component with Floating Label
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QFrame)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QGraphicsOpacityEffect


class ModernInput(QWidget):
    """Modern floating label input with smooth animations"""

    textChanged = Signal(str)
    returnPressed = Signal()

    def __init__(self, label_text, placeholder="", is_password=False, icon="", parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.placeholder = placeholder or label_text
        self.is_password = is_password
        self.icon = icon
        self.is_focused = False

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.container = QFrame()
        self.container.setObjectName("inputContainer")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(18, 8, 18, 8)
        container_layout.setSpacing(12)
        container_layout.setAlignment(Qt.AlignVCenter)

        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setObjectName("inputIcon")
            icon_label.setFont(QFont("Segoe UI Emoji", 16))
            container_layout.addWidget(icon_label)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(0)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setAlignment(Qt.AlignVCenter)

        self.label = QLabel(self.label_text)
        self.label.setObjectName("floatingLabel")
        self.label.setFont(QFont("Segoe UI", 9, QFont.DemiBold))

        self.input = QLineEdit()
        self.input.setObjectName("modernInput")
        self.input.setFont(QFont("Segoe UI", 12))
        self.input.setPlaceholderText(self.placeholder)
        self.input.setFixedHeight(44)
        self.input.setAlignment(Qt.AlignVCenter)
        # Dikey hizalama için özel stil
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 12px 0px;
                border: none;
                background: transparent;
                vertical-align: middle;
            }
        """)
        if self.is_password:
            self.input.setEchoMode(QLineEdit.Password)

        self.input.textChanged.connect(self.textChanged.emit)
        self.input.returnPressed.connect(self.returnPressed.emit)

        self.input.focusInEvent = self.on_focus_in
        self.input.focusOutEvent = self.on_focus_out

        input_layout.addWidget(self.label)
        input_layout.addWidget(self.input)

        container_layout.addLayout(input_layout, 1)
        layout.addWidget(self.container)

        self.label.hide()
        self.label_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.label_effect)

    def on_focus_in(self, event):
        self.is_focused = True
        self.animate_label(True)
        self.container.setProperty("focused", True)
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)
        QLineEdit.focusInEvent(self.input, event)

    def on_focus_out(self, event):
        self.is_focused = False
        if not self.input.text():
            self.animate_label(False)
        self.container.setProperty("focused", False)
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)
        QLineEdit.focusOutEvent(self.input, event)

    def animate_label(self, show):
        anim = QPropertyAnimation(self.label_effect, b"opacity")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        if show:
            self.label.show()
            self.input.setPlaceholderText("")
            anim.setStartValue(0)
            anim.setEndValue(1)
        else:
            anim.setStartValue(1)
            anim.setEndValue(0)
            anim.finished.connect(self.label.hide)
            self.input.setPlaceholderText(self.placeholder)

        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def text(self):
        return self.input.text()

    def clear(self):
        self.input.clear()

    def set_echo_mode(self, mode):
        self.input.setEchoMode(mode)