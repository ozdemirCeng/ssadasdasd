def paintEvent(self, event):
    """Custom paint - KOÜ yeşil"""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)

    center = QPoint(self.width() // 2, self.height() // 2)
    radius = int(60 * self._scale)

    # Hover: Yeşil gradient
    if self.is_hovered:
        # Outer glow
        glow = QRadialGradient(center, radius + 12)
        glow.setColorAt(0, QColor(0, 166, 81, 100))
        glow.setColorAt(1, QColor(0, 166, 81, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius + 12, radius + 12)

        # Glass circle - yeşil
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(0, 166, 81, 240))
        gradient.setColorAt(1, QColor(0, 143, 71, 200))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.drawEllipse(center, radius, radius)

        # Text - beyaz
        painter.setPen(QPen(QColor(255, 255, 255)))
    else:
        # Normal: Saydam beyaz glass
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(255, 255, 255, 200))
        gradient.setColorAt(1, QColor(255, 255, 255, 140))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 220), 2))
        painter.drawEllipse(center, radius, radius)

        # Text - yeşil
        painter.setPen(QPen(QColor(0, 166, 81)))

    # Inner shine
    if self.is_hovered:
        shine = QRadialGradient(QPoint(center.x() - 15, center.y() - 15), 25)
        shine.setColorAt(0, QColor(255, 255, 255, 120))
        shine.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(shine))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(center.x() - 15, center.y() - 15), 25, 25)

    # Text
    painter.setFont(QFont("Segoe UI", int(12 * self._scale), QFont.Bold))
    text_rect = self.rect().adjusted(8, int(40 * self._scale), -8, -8)
    painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.text_label)


# ============================================================
# CENTER HUB - Minimal
# ============================================================

class MinimalCenterHub(QFrame):
    """Minimal merkez hub - az boşluk"""

    def __init__(self, user_data, stats, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.stats = stats
        self.setMinimumSize(180, 180)
        self.setMaximumSize(240, 240)
        self.setStyleSheet("background: transparent; border: none;")

        self.setup_ui()

    def setup_ui(self):
        """Compact UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # Avatar
        initial = self.user_data.get('ad_soyad', 'K')[0].upper()
        avatar = QLabel(initial)
        avatar.setFont(QFont("Segoe UI", 32, QFont.Bold))
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(65, 65)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00A651,
                    stop:1 #008F47
                );
                color: white;
                border-radius: 32px;
            }
        """)

        # Name - compact
        name_parts = self.user_data.get('ad_soyad', 'K').split()
        name = QLabel(name_parts[0] if name_parts else "Kullanıcı")
        name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: #1d1d1f;")

        # Role
        role = QLabel(self.user_data.get('role', 'Rol'))
        role.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        role.setAlignment(Qt.AlignCenter)
        role.setStyleSheet("""
            QLabel {
                background: rgba(0, 166, 81, 0.15);
                color: #00A651;
                border-radius: 8px;
                padding: 4px 10px;
            }
        """)

        # Stats - inline
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        for label, value in [("Sınav", self.stats['exams']), ("Ders", self.stats['courses'])]:
            stat = QWidget()
            stat_layout = QVBoxLayout(stat)
            stat_layout.setSpacing(1)
            stat_layout.setContentsMargins(0, 0, 0, 0)

            val = QLabel(str(value))
            val.setFont(QFont("Segoe UI", 18, QFont.Bold))
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet("color: #00A651;")

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 8))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #666;")

            stat_layout.addWidget(val)
            stat_layout.addWidget(lbl)

            stats_layout.addWidget(stat)

        layout.addWidget(avatar)
        layout.addWidget(name)
        layout.addWidget(role)
        layout.addSpacing(4)
        layout.addWidget(stats_widget)

    def paintEvent(self, event):
        """Glass circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 5

        # Glass
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(255, 255, 255, 220))
        gradient.setColorAt(1, QColor(255, 255, 255, 160))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 240), 3))
        painter.drawEllipse(center, radius, radius)

        # Shine
        shine = QRadialGradient(QPoint(center.x() - 20, center.y() - 20), 40)
        shine.setColorAt(0, QColor(255, 255, 255, 140))
        shine.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(shine))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(center.x() - 20, center.y() - 20), 40, 40)


# ============================================================
# STAT CARD - No border
# ============================================================

class CleanStatCard(QWidget):
    """Clean stat card - no border"""

    def __init__(self, label, current, total, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        lbl.setStyleSheet("color: #333;")

        val = QLabel(f"{current}/{total}")
        val.setFont(QFont("Segoe UI", 10))
        val.setStyleSheet("color: #00A651;")

        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(val)

        # Progress
        progress = QProgressBar()
        progress.setMaximum(total)
        progress.setValue(current)
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet("""
            QProgressBar {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background: #00A651;
                border-radius: 3px;
            }
        """)

        layout.addLayout(header)
        layout.addWidget(progress)

        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.7);
                border-radius: 12px;
                border: none;
            }
            QWidget:hover {
                background: rgba(255, 255, 255, 0.9);
            }
        """)


# ============================================================
# ACTIVITY CARD - Clean
# ============================================================

class CleanActivityCard(QFrame):
    """Clean activity card"""

    def __init__(self, title, time, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Dot
        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 12))
        dot.setStyleSheet("color: #00A651;")

        # Content
        content = QVBoxLayout()
        content.setSpacing(2)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        title_label.setStyleSheet("color: #333;")
        title_label.setWordWrap(True)

        time_label = QLabel(time)
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: #999;")

        content.addWidget(title_label)
        content.addWidget(time_label)

        layout.addWidget(dot)
        layout.addLayout(content, 1)

        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 10px;
                border: none;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.85);
            }
        """)


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QWidget):
    """KOÜ Professional Dashboard"""

    logout_requested = Signal()

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_admin = user_data.get('role') == 'Admin'

        self.stats_data = {
            'exams': 15,
            'courses': 42,
            'classrooms': 8,
            'students': 850
        }

        self.setWindowTitle("Kocaeli Üniversitesi - Sınav Takvimi Sistemi")
        self.showMaximized()

        self.setup_ui()
        self.apply_styles()

        QTimer.singleShot(100, self.animate_entrance)

    def setup_ui(self):
        """UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Left panel - compact
        left = self.create_left_panel()
        content_layout.addWidget(left, 1)

        # Center radial - more space
        self.radial_container = QWidget()
        self.radial_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_radial()
        content_layout.addWidget(self.radial_container, 3)

        # Right panel - compact
        right = self.create_right_panel()
        content_layout.addWidget(right, 1)

        main_layout.addWidget(content, 1)

    def create_top_bar(self):
        """Minimal top bar"""
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.85);
                border: none;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(25, 0, 25, 0)

        # Logo
        logo = QLabel("🎓")
        logo.setFont(QFont("Segoe UI", 24))

        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)

        title = QLabel("Sınav Takvimi Sistemi")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #333;")

        subtitle = QLabel("Kocaeli Üniversitesi")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #999;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        layout.addWidget(logo)
        layout.addLayout(title_layout)
        layout.addStretch()

        # User
        user = QLabel(self.user_data['ad_soyad'])
        user.setFont(QFont("Segoe UI", 10))
        user.setStyleSheet("color: #666;")

        # Logout
        logout = QPushButton("Çıkış")
        logout.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        logout.setCursor(Qt.PointingHandCursor)
        logout.setFixedSize(70, 32)
        logout.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
            }
            QPushButton:pressed {
                background: rgba(239, 68, 68, 0.3);
            }
        """)
        logout.clicked.connect(self.logout_requested.emit)

        layout.addWidget(user)
        layout.addWidget(logout)

        return bar

    def create_left_panel(self):
        """Compact left panel"""
        panel = QFrame()
        panel.setMaximumWidth(240)
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 16px;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QLabel("İstatistikler")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #333;")

        layout.addWidget(header)

        stats = [
            ("Sınavlar", 15, 20),
            ("Dersler", 42, 50),
            ("Derslikler", 8, 10),
            ("Öğrenciler", 850, 1000)
        ]

        for label, current, total in stats:
            card = CleanStatCard(label, current, total)
            layout.addWidget(card)

        layout.addStretch()

        return panel

    def setup_radial(self):
        """Radial - compact"""
        # Center hub
        self.center_hub = MinimalCenterHub(
            self.user_data,
            self.stats_data,
            self.radial_container
        )
        self.center_hub.show()

        # Modules
        if self.is_admin:
            modules = [
                ("Dersler", "ders"),
                ("Derslikler", "derslik"),
                ("Öğrenciler", "ogrenci"),
                ("Sınavlar", "sinav"),
                ("Oturma Planı", "oturma"),
                ("Raporlar", "rapor")
            ]
        else:
            modules = [
                ("Dersler", "ders"),
                ("Derslikler", "derslik"),
                ("Sınavlar", "sinav"),
                ("Raporlar", "rapor")
            ]

        self.radial_buttons = []
        for text, module_id in modules:
            btn = KOUGlassButton(text, module_id, self.radial_container)
            btn.clicked_with_id.connect(self.open_module)
            btn.show()
            self.radial_buttons.append(btn)

        QTimer.singleShot(50, lambda: self.position_radial(None))

        original = self.radial_container.resizeEvent

        def safe_resize(e):
            if original and e:
                original(e)
            self.position_radial(e)

        self.radial_container.resizeEvent = safe_resize

    def position_radial(self, event):
        """Compact positioning"""
        if not hasattr(self, 'center_hub'):
            return

        cx = self.radial_container.width() // 2
        cy = self.radial_container.height() // 2

        # Compact radius
        container_size = min(self.radial_container.width(), self.radial_container.height())
        radius = max(180, min(260, container_size // 3))

        # Center hub
        hub_size = max(180, min(220, container_size // 4))
        self.center_hub.setFixedSize(hub_size, hub_size)
        self.center_hub.move(cx - hub_size // 2, cy - hub_size // 2)
        self.center_hub.raise_()
        self.center_hub.show()

        # Buttons
        num = len(self.radial_buttons)
        button_size = max(110, min(130, container_size // 9))

        for i, btn in enumerate(self.radial_buttons):
            angle = (360 / num) * i - 90
            rad = math.radians(angle)

            x = cx + int(radius * math.cos(rad)) - button_size // 2
            y = cy + int(radius * math.sin(rad)) - button_size // 2

            btn.setFixedSize(button_size, button_size)
            btn.move(x, y)
            btn.raise_()
            btn.show()

    def create_right_panel(self):
        """Compact right panel"""
        panel = QFrame()
        panel.setMaximumWidth(280)
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 16px;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header = QLabel("Son İşlemler")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #333;")

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.03);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 166, 81, 0.4);
                border-radius: 3px;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setAlignment(Qt.AlignTop)

        activities = [
            ("BMÜ Final Programı", "2sa"),
            ("301 Derslik", "5sa"),
            ("YMÜ Vize", "1g"),
            ("Öğrenci Listesi", "2g"),
            ("EDA Dersliği", "3g")
        ]

        for title, time in activities:
            card = CleanActivityCard(title, time)
            scroll_layout.addWidget(card)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return panel

    def open_module(self, module_id):
        """Modül aç"""
        print(f"✓ Modül: {module_id}")

        names = {
            'ders': 'Dersler',
            'derslik': 'Derslikler',
            'ogrenci': 'Öğrenciler',
            'sinav': 'Sınavlar',
            'oturma': 'Oturma Planı',
            'rapor': 'Raporlar'
        }

        QMessageBox.information(
            self,
            names.get(module_id, 'Modül'),
            f"{names.get(module_id, module_id)} modülü\n(Geliştiriliyor)",
            QMessageBox.Ok
        )

    def animate_entrance(self):
        """Entrance"""
        if hasattr(self, 'center_hub'):
            self.center_hub.show()

            hub_effect = QGraphicsOpacityEffect(self.center_hub)
            self.center_hub.setGraphicsEffect(hub_effect)

            hub_anim = QPropertyAnimation(hub_effect, b"opacity")
            hub_anim.setDuration(600)
            hub_anim.setStartValue(0)
            hub_anim.setEndValue(1)
            hub_anim.start()

            def remove_hub():
                self.center_hub.setGraphicsEffect(None)

            hub_anim.finished.connect(remove_hub)

        for btn in self.radial_buttons:
            btn.show()

        self.btn_anims = []
        for i, btn in enumerate(self.radial_buttons):
            effect = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(0)
            anim.setEndValue(1)

            def make_remove(b):
                def remove():
                    b.setGraphicsEffect(None)

                return remove

            anim.finished.connect(make_remove(btn))
            self.btn_anims.append(anim)

            QTimer.singleShot(100 * (i + 1), anim.start)

    def apply_styles(self):
        """KOÜ gradient"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f5e9,
                    stop:0.5 #c8e6c9,
                    stop:1 #a5d6a7
                );
                font-family: 'Segoe UI', Arial;
            }
        """)


# ============================================================
# TEST & DEMO
# ============================================================

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    # Application
    app = QApplication(sys.argv)
    app.setApplicationName("KOÜ Sınav Takvimi")
    app.setOrganizationName("Kocaeli Üniversitesi")

    # Demo user data - Admin
    admin_user = {
        'user_id': 1,
        'email': 'admin@kocaeli.edu.tr',
        'role': 'Admin',
        'ad_soyad': 'Ahmet Yılmaz'
    }

    # Demo user data - Koordinatör
    koordinator_user = {
        'user_id': 2,
        'email': 'koordinator@kocaeli.edu.tr',
        'role': 'Bölüm Koordinatörü',
        'ad_soyad': 'Mehmet Demir'
    }

    # Create main window with admin user
    window = MainWindow(admin_user)

    # Window settings
    window.setWindowTitle("Kocaeli Üniversitesi - Sınav Takvimi Sistemi")


    # Connect logout signal
    def on_logout():
        reply = QMessageBox.question(
            window,
            "Çıkış Onayı",
            "Sistemden çıkmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            print("Kullanıcı çıkış yaptı")
            app.quit()


    window.logout_requested.connect(on_logout)

    # Show window
    window.show()

    # Info message
    print("=" * 60)
    print("  KOÜ SINAV TAKVİMİ SİSTEMİ - DASHBOARD")
    print("=" * 60)
    print(f"  Kullanıcı: {admin_user['ad_soyad']}")
    print(f"  Rol: {admin_user['role']}")
    print(f"  Email: {admin_user['email']}")
    print("=" * 60)
    print("\n  Dashboard başarıyla yüklendi!")
    print("  - Dairesel butonlara tıklayarak modülleri açabilirsiniz")
    print("  - Hover yaparak animasyonları görebilirsiniz")
    print("  - Çıkış butonu ile güvenli çıkış yapabilirsiniz\n")

    # Run application
    sys.exit(app.exec())
"""
views/main_window.py
Kocaeli Üniversitesi - PROFESSIONAL DASHBOARD
KOÜ Renkleri: Yeşil (#00A651) + Beyaz
Glassmorphism, Minimal, Clean, Responsive
Production Ready - Full Implementation
"""

import sys
import math
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
    QSizePolicy, QMessageBox, QProgressBar, QSpacerItem
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QSize,
    Signal, Property, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QCursor, QColor, QPainter, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath, QTransform
)

sys.path.append(str(Path(__file__).parent.parent))


# ============================================================
# KOÜ GLASS BUTTON
# ============================================================

class KOUGlassButton(QPushButton):
    """KOÜ tarzı glassmorphism buton"""

    clicked_with_id = Signal(str)

    def __init__(self, text, module_id, parent=None):
        super().__init__(parent)
        self.text_label = text
        self.module_id = module_id
        self.is_hovered = False
        self._scale = 1.0

        self.setFixedSize(130, 130)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.update()

    scale = Property(float, get_scale, set_scale)

    def enterEvent(self, event):
        """Hover - sadece büyüme"""
        self.is_hovered = True

        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(250)
        anim.setStartValue(self._scale)
        anim.setEndValue(1.12)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Leave"""
        self.is_hovered = False

        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(200)
        anim.setStartValue(self._scale)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Press"""
        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(80)
        anim.setStartValue(self._scale)
        anim.setEndValue(0.95)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Release"""
        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(120)
        anim.setStartValue(self._scale)
        anim.setEndValue(1.12 if self.is_hovered else 1.0)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

        self.clicked_with_id.emit(self.module_id)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Custom paint - KOÜ yeşil"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)
        radius = int(60 * self._scale)

        # Hover: Yeşil gradient
        if self.is_hovered:
            # Outer glow
            glow = QRadialGradient(center, radius + 12)
            glow.setColorAt(0, QColor(0, 166, 81, 100))
            glow.setColorAt(1, QColor(0, 166, 81, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, radius + 12, radius + 12)

            # Glass circle - yeşil
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(0, 166, 81, 240))
            gradient.setColorAt(1, QColor(0, 143, 71, 200))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
            painter.drawEllipse(center, radius, radius)

            # Text - beyaz
            painter.setPen(QPen(QColor(255, 255, 255)))
        else:
            # Normal: Saydam beyaz glass
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(255, 255, 255, 200))
            gradient.setColorAt(1, QColor(255, 255, 255, 140))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 220), 2))
            painter.drawEllipse(center, radius, radius)

            # Text - yeşil
            painter.setPen(QPen(QColor(0, 166, 81)))

        # Inner shine
        if self.is_hovered:
            shine = QRadialGradient(QPoint(center.x() - 15, center.y() - 15), 25)
            shine.setColorAt(0, QColor(255, 255, 255, 120))
            shine.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(shine))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(center.x() - 15, center.y() - 15), 25, 25)

        # Text
        painter.setFont(QFont("Segoe UI", int(12 * self._scale), QFont.Bold))
        text_rect = self.rect().adjusted(8, int(40 * self._scale), -8, -8)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.text_label)