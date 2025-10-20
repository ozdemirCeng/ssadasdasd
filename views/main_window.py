"""
views/main_window.py
Kocaeli Üniversitesi - Production Dashboard
Dairesel Navigasyon + Gerçek Veri + Beyaz-Yeşil Tema
"""

import sys
import math
from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGraphicsOpacityEffect,
    QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QRect,
    Signal, Property, QSequentialAnimationGroup, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QCursor, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient
)

sys.path.append(str(Path(__file__).parent.parent))
from config import ThemeConfig


# ============================================================
# RADIAL NAVIGATION BUTTON
# ============================================================

class RadialButton(QPushButton):
    """Dairesel menü butonu - Production"""
    
    def __init__(self, text, icon, module_id, parent=None):
        super().__init__(parent)
        self.button_text = text
        self.icon_text = icon
        self.module_id = module_id
        self.is_hovered = False
        self._scale = 1.0
        
        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 166, 81, 80))
        self.setGraphicsEffect(shadow)
        
    def get_scale(self):
        return self._scale
    
    def set_scale(self, scale):
        self._scale = scale
        self.update()
    
    scale = Property(float, get_scale, set_scale)
        
    def enterEvent(self, event):
        """Hover - büyüt"""
        self.is_hovered = True
        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(200)
        anim.setStartValue(self._scale)
        anim.setEndValue(1.15)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Leave - küçült"""
        self.is_hovered = False
        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(200)
        anim.setStartValue(self._scale)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        """Custom paint"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center point
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = int(55 * self._scale)
        
        # Background circle
        if self.is_hovered:
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(0, 166, 81, 200))
            gradient.setColorAt(1, QColor(0, 143, 71, 200))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
        else:
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(0, 166, 81, 100), 2))
        
        painter.drawEllipse(center, radius, radius)
        
        # Icon
        if self.is_hovered:
            painter.setPen(QPen(QColor(255, 255, 255)))
        else:
            painter.setPen(QPen(QColor(0, 166, 81)))
        
        painter.setFont(QFont("Segoe UI", int(28 * self._scale), QFont.Bold))
        icon_rect = QRect(0, int(35 * self._scale), self.width(), int(40 * self._scale))
        painter.drawText(icon_rect, Qt.AlignCenter, self.icon_text)
        
        # Text
        painter.setFont(QFont("Segoe UI", int(10 * self._scale), QFont.DemiBold))
        text_rect = QRect(0, int(75 * self._scale), self.width(), int(30 * self._scale))
        painter.drawText(text_rect, Qt.AlignCenter, self.button_text)


# ============================================================
# CENTER HUB - Gerçek verilerle
# ============================================================

class CenterHub(QFrame):
    """Merkezi kullanıcı paneli - Gerçek veri"""
    
    stats_clicked = Signal()
    
    def __init__(self, user_data, stats_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.stats_data = stats_data
        self.setObjectName("centerHub")
        self.setFixedSize(200, 200)
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Avatar initial
        initial = self.user_data.get('ad_soyad', 'K')[0].upper()
        avatar = QLabel(initial)
        avatar.setObjectName("avatar")
        avatar.setFont(QFont("Segoe UI", 36, QFont.Bold))
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(60, 60)
        
        # Name
        name_parts = self.user_data.get('ad_soyad', 'Kullanıcı').split()
        short_name = name_parts[0] if len(name_parts) > 0 else "Kullanıcı"
        
        name = QLabel(short_name)
        name.setObjectName("hubName")
        name.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name.setAlignment(Qt.AlignCenter)
        
        # Role
        role = QLabel(self.user_data.get('role', 'Rol'))
        role.setObjectName("hubRole")
        role.setFont(QFont("Segoe UI", 9))
        role.setAlignment(Qt.AlignCenter)
        
        # Stats button
        stats_text = f"{self.stats_data.get('active_exams', 0)} Aktif Sınav"
        stats_btn = QPushButton(stats_text)
        stats_btn.setObjectName("statsBtn")
        stats_btn.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        stats_btn.setCursor(Qt.PointingHandCursor)
        stats_btn.clicked.connect(self.stats_clicked.emit)
        
        layout.addWidget(avatar)
        layout.addWidget(name)
        layout.addWidget(role)
        layout.addSpacing(5)
        layout.addWidget(stats_btn)
        
    def paintEvent(self, event):
        """Custom background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Circle background
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = 100
        
        # Gradient
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(255, 255, 255))
        gradient.setColorAt(1, QColor(240, 255, 248))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 166, 81, 100), 3))
        painter.drawEllipse(center, radius, radius)


# ============================================================
# ACTIVITY ITEM - Gerçek veri
# ============================================================

class ActivityItem(QFrame):
    """Tek activity item"""
    
    def __init__(self, activity_data, parent=None):
        super().__init__(parent)
        self.activity_data = activity_data
        self.setObjectName("activityItem")
        self.setCursor(Qt.PointingHandCursor)
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        
        # Time indicator
        time_label = QLabel(self.format_time())
        time_label.setObjectName("activityTime")
        time_label.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        time_label.setFixedWidth(60)
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Separator line
        separator = QFrame()
        separator.setFixedSize(3, 40)
        separator.setStyleSheet(f"background: {self.get_color()}; border-radius: 1px;")
        
        # Content
        content = QVBoxLayout()
        content.setSpacing(3)
        
        title = QLabel(self.activity_data['title'])
        title.setObjectName("activityTitle")
        title.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        title.setWordWrap(True)
        
        detail = QLabel(self.activity_data.get('detail', ''))
        detail.setObjectName("activityDetail")
        detail.setFont(QFont("Segoe UI", 9))
        detail.setWordWrap(True)
        
        content.addWidget(title)
        if self.activity_data.get('detail'):
            content.addWidget(detail)
        
        layout.addWidget(time_label)
        layout.addWidget(separator)
        layout.addLayout(content, 1)
        
    def format_time(self):
        """Zamanı formatla"""
        created = self.activity_data.get('created_at')
        if not created:
            return ""
        
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        
        now = datetime.now()
        diff = now - created
        
        if diff.seconds < 60:
            return "Şimdi"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}dk"
        elif diff.seconds < 86400:
            return f"{diff.seconds // 3600}sa"
        else:
            return f"{diff.days}g"
    
    def get_color(self):
        """Activity tipine göre renk"""
        action_type = self.activity_data.get('action', '')
        colors = {
            'INSERT': '#10B981',
            'UPDATE': '#3B82F6',
            'DELETE': '#EF4444',
            'LOGIN': '#8B5CF6',
            'EXPORT': '#F59E0B'
        }
        return colors.get(action_type, '#6B7280')


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):
    """Production Dashboard - Gerçek veri"""
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_admin = user_data.get('role') == 'Admin'
        
        self.setWindowTitle(f"KOÜ Sınav Takvimi - {user_data.get('ad_soyad')}")
        self.setMinimumSize(1400, 800)
        
        # Gerçek verileri yükle
        self.load_real_data()
        
        self.setup_ui()
        self.apply_styles()
        
        # Startup animation
        QTimer.singleShot(100, self.animate_entrance)
        
        self.showMaximized()
        
    def load_real_data(self):
        """VERİTABANINDAN gerçek verileri yükle"""
        from models.database import db
        
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Stats yükle
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM sinavlar WHERE tarih >= CURRENT_DATE) as active_exams,
                    (SELECT COUNT(*) FROM derslikler WHERE aktif = TRUE) as total_classrooms,
                    (SELECT COUNT(*) FROM dersler WHERE aktif = TRUE) as total_courses,
                    (SELECT COUNT(*) FROM ogrenciler WHERE aktif = TRUE) as total_students
            """)
            stats = cursor.fetchone()
            
            self.stats_data = {
                'active_exams': stats[0] if stats else 0,
                'total_classrooms': stats[1] if stats else 0,
                'total_courses': stats[2] if stats else 0,
                'total_students': stats[3] if stats else 0
            }
            
            # Son işlemler (audit logs)
            cursor.execute("""
                SELECT 
                    al.action,
                    al.table_name,
                    al.created_at,
                    u.ad_soyad
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.user_id
                WHERE al.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
                ORDER BY al.created_at DESC
                LIMIT 10
            """)
            
            activities = cursor.fetchall()
            self.activities_data = []
            
            for action, table, created_at, user_name in activities:
                self.activities_data.append({
                    'action': action,
                    'table': table,
                    'title': self.format_activity_title(action, table),
                    'detail': f"{user_name or 'Sistem'}" if user_name else None,
                    'created_at': created_at
                })
            
            cursor.close()
            db.return_connection(conn)
            
        except Exception as e:
            print(f"Veri yükleme hatası: {e}")
            self.stats_data = {'active_exams': 0, 'total_classrooms': 0, 'total_courses': 0, 'total_students': 0}
            self.activities_data = []
    
    def format_activity_title(self, action, table):
        """Activity başlığı oluştur"""
        table_names = {
            'dersler': 'Ders',
            'derslikler': 'Derslik',
            'ogrenciler': 'Öğrenci',
            'sinavlar': 'Sınav',
            'sinav_programi': 'Sınav Programı',
            'oturma_planlari': 'Oturma Planı'
        }
        
        action_names = {
            'INSERT': 'eklendi',
            'UPDATE': 'güncellendi',
            'DELETE': 'silindi',
            'LOGIN': 'giriş yapıldı',
            'EXPORT': 'dışa aktarıldı'
        }
        
        table_tr = table_names.get(table, table)
        action_tr = action_names.get(action, action.lower())
        
        return f"{table_tr} {action_tr}"
        
    def setup_ui(self):
        """Ana UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Content: Radial + Activities
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Left: Radial navigation
        self.radial_widget = QWidget()
        self.radial_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_radial_navigation()
        
        content_layout.addWidget(self.radial_widget, 3)
        
        # Right: Activities
        activities_panel = self.create_activities_panel()
        content_layout.addWidget(activities_panel, 2)
        
        main_layout.addWidget(content, 1)
        
    def create_top_bar(self):
        """Top bar - gerçek bilgilerle"""
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(65)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)
        
        # Logo + Title
        logo = QLabel("🎓 KOÜ")
        logo.setObjectName("logo")
        logo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        title = QLabel("Sınav Takvimi Yönetim Sistemi")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        
        # Stats (hızlı bilgiler)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        stats_items = [
            ("Sınavlar", self.stats_data['active_exams']),
            ("Derslikler", self.stats_data['total_classrooms']),
            ("Dersler", self.stats_data['total_courses'])
        ]
        
        for label, value in stats_items:
            item = QWidget()
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(2)
            
            val_label = QLabel(str(value))
            val_label.setObjectName("statValue")
            val_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
            val_label.setAlignment(Qt.AlignCenter)
            
            txt_label = QLabel(label)
            txt_label.setObjectName("statLabel")
            txt_label.setFont(QFont("Segoe UI", 9))
            txt_label.setAlignment(Qt.AlignCenter)
            
            item_layout.addWidget(val_label)
            item_layout.addWidget(txt_label)
            
            stats_layout.addWidget(item)
        
        layout.addLayout(stats_layout)
        
        # Logout
        logout_btn = QPushButton("Çıkış Yap")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        
        layout.addWidget(logout_btn)
        
        return bar
        
    def setup_radial_navigation(self):
        """Dairesel navigasyon kurulumu"""
        # Center hub
        self.center_hub = CenterHub(self.user_data, self.stats_data, self.radial_widget)
        self.center_hub.stats_clicked.connect(self.show_stats_detail)
        
        # Modules
        if self.is_admin:
            modules = [
                ("Dersler", "📚", "ders"),
                ("Derslikler", "🏢", "derslik"),
                ("Öğrenciler", "👥", "ogrenci"),
                ("Sınavlar", "📝", "sinav"),
                ("Oturma", "💺", "oturma"),
                ("Raporlar", "📊", "rapor")
            ]
        else:
            modules = [
                ("Dersler", "📚", "ders"),
                ("Derslikler", "🏢", "derslik"),
                ("Öğrenciler", "👥", "ogrenci"),
                ("Sınavlar", "📝", "sinav")
            ]
        
        self.radial_buttons = []
        for text, icon, module_id in modules:
            btn = RadialButton(text, icon, module_id, self.radial_widget)
            btn.clicked.connect(lambda checked, m=module_id: self.open_module(m))
            self.radial_buttons.append(btn)
        
        # Resize event
        self.radial_widget.resizeEvent = self.position_radial_elements
        
    def position_radial_elements(self, event):
        """Dairesel konumlandırma"""
        cx = self.radial_widget.width() // 2
        cy = self.radial_widget.height() // 2
        
        # Center hub
        self.center_hub.move(
            cx - self.center_hub.width() // 2,
            cy - self.center_hub.height() // 2
        )
        
        # Radial buttons
        radius = 250
        num = len(self.radial_buttons)
        
        for i, btn in enumerate(self.radial_buttons):
            angle = (360 / num) * i - 90
            rad = math.radians(angle)
            
            x = cx + int(radius * math.cos(rad)) - btn.width() // 2
            y = cy + int(radius * math.sin(rad)) - btn.height() // 2
            
            btn.move(x, y)
    
    def create_activities_panel(self):
        """Son işlemler paneli"""
        panel = QFrame()
        panel.setObjectName("activitiesPanel")
        panel.setMinimumWidth(350)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Son İşlemler")
        header.setObjectName("panelHeader")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setObjectName("activitiesScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setAlignment(Qt.AlignTop)
        
        # Activities
        for activity in self.activities_data[:8]:  # Son 8
            item = ActivityItem(activity)
            scroll_layout.addWidget(item)
        
        if not self.activities_data:
            no_data = QLabel("Henüz işlem yok")
            no_data.setFont(QFont("Segoe UI", 11))
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #94a3b8;")
            scroll_layout.addWidget(no_data)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return panel
        
    def open_module(self, module_id):
        """Modül aç"""
        print(f"Modül açılıyor: {module_id}")
        # TODO: İlgili modülü aç
        
    def show_stats_detail(self):
        """İstatistik detayı göster"""
        print("Stats detail")
        
    def handle_logout(self):
        """Çıkış"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Çıkış",
            "Çıkış yapmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            
    def animate_entrance(self):
        """Giriş animasyonu"""
        # Center hub
        hub_opacity = QGraphicsOpacityEffect(self.center_hub)
        self.center_hub.setGraphicsEffect(hub_opacity)
        hub_opacity.setOpacity(0)
        
        hub_anim = QPropertyAnimation(hub_opacity, b"opacity")
        hub_anim.setDuration(500)
        hub_anim.setStartValue(0)
        hub_anim.setEndValue(1)
        hub_anim.setEasingCurve(QEasingCurve.OutCubic)
        hub_anim.start(QPropertyAnimation.DeleteWhenStopped)
        
        # Radial buttons cascade
        for i, btn in enumerate(self.radial_buttons):
            opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(opacity)
            opacity.setOpacity(0)
            
            anim = QPropertyAnimation(opacity, b"opacity")
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            
            QTimer.singleShot(100 * (i + 1), anim.start)
        
    def apply_styles(self):
        """Beyaz-Yeşil tema"""
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc,
                    stop:1 #f0f9ff
                );
            }}
            
            #topBar {{
                background: white;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            #logo {{
                color: {ThemeConfig.PRIMARY_COLOR};
            }}
            
            #title {{
                color: #0f172a;
            }}
            
            #statValue {{
                color: {ThemeConfig.PRIMARY_COLOR};
            }}
            
            #statLabel {{
                color: #64748b;
            }}
            
            #logoutBtn {{
                background: white;
                color: #ef4444;
                border: 2px solid #fecaca;
                border-radius: 8px;
                padding: 10px 24px;
            }}
            
            #logoutBtn:hover {{
                background: #fef2f2;
                border: 2px solid #ef4444;
            }}
            
            #centerHub {{
                background: transparent;
            }}
            
            #avatar {{
                background: {ThemeConfig.PRIMARY_COLOR};
                color: white;
                border-radius: 30px;
            }}
            
            #hubName {{
                color: #0f172a;
            }}
            
            #hubRole {{
                color: {ThemeConfig.PRIMARY_COLOR};
            }}
            
            #statsBtn {{
                background: {ThemeConfig.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            
            #statsBtn:hover {{
                background: {ThemeConfig.PRIMARY_DARK};
            }}
            
            #activitiesPanel {{
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
            }}
            
            #panelHeader {{
                color: #0f172a;
            }}
            
            #activitiesScroll {{
                background: transparent;
                border: none;
            }}
            
            #activityItem {{
                background: #f8fafc;
                border-radius: 10px;
            }}
            
            #activityItem:hover {{
                background: #f1f5f9;
            }}
            
            #activityTime {{
                color: {ThemeConfig.PRIMARY_COLOR};
            }}
            
            #activityTitle {{
                color: #0f172a;
            }}
            
            #activityDetail {{
                color: #64748b;
            }}
        """)