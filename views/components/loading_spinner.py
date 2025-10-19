"""
Modern Loading Spinner Component
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Property
from PySide6.QtGui import QPainter, QColor, QPen


class LoadingSpinner(QWidget):
    """Modern loading spinner with smooth animation"""

    def __init__(self, parent=None, size=40, color="#00A651"):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._color = color
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        self._angle = angle
        self.update()

    angle = Property(int, get_angle, set_angle)

    def start(self):
        self.timer.start(20)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.rect().center())
        painter.rotate(self._angle)

        pen = QPen(QColor(self._color))
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        for i in range(8):
            opacity = 1.0 - (i * 0.12)
            painter.setOpacity(opacity)
            painter.drawLine(0, -15, 0, -8)
            painter.rotate(45)