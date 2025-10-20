"""
KOCAELİ ÜNİVERSİTESİ - MODERN DASHBOARD
Radial Navigation - Non-Cliché Design
==========================================
Ana özellikler:
- Dairesel navigasyon sistemi
- Tek pencere içinde tüm modüller
- Admin ve Koordinatör için farklı layout'lar
- Animasyonlu geçişler
- Real-time activity feed
"""

import sys
import math
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QGraphicsOpacityEffect,
    QStackedWidget, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QRect,
    Signal, Property, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QFont, QCursor, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QPalette
)


# ============================================================
# RADIAL MENU BUTTON (Dairesel navigasyon butonu)
# ============================================================

class RadialButton(QPushButton):
    """
    Merkezi dairesel menü için özel buton
    Animasyonlu hover ve click efektleri
    """
    
    def __init__(self, text, icon_text, color, parent=None):
        super().__init__(parent)
        self.button_text = text
        self.icon_text = icon_text  # Tek karakter icon (örn: "D" for Ders)
        self.base_color = QColor(color)
        self.hover_color = QColor(color).lighter(120)
        self.is_hovered = False
        
        self.setFixedSize(140, 140)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Hover animation setup
        self.scale_factor = 1.0
        
    def enterEvent(self, event):
        """Mouse hover - büyüt"""
        self.is_hovered = True
        self._animate_scale(1.1)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Mouse leave - küçült"""
        self.is_hovered = False
        self._animate_scale(1.0)
        super().leaveEvent(event)
        
    def _animate_scale(self, target_scale):
        """Scale animasyonu"""
        # Basit scale effect - QSS ile
        if target_scale > 1.0:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(16, 185, 129, 0.2),
                        stop:1 rgba(16, 185, 129, 0.4)
                    );
                    border: 3px solid #10B981;
                    border-radius: 70px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.05);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 70px;
                }
                QPushButton:hover {
                    background: rgba(16, 185, 129, 0.15);
                    border: 2px solid #10B981;
                }
            """)
    
    def paintEvent(self, event):
        """Custom paint - icon ve text"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Icon (büyük harf)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        
        icon_rect = QRect(0, 30, self.width(), 50)
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, self.icon_text)
        
        # Text (açıklama)
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        text_rect = QRect(0, 80, self.width(), 30)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.button_text)


# ============================================================
# CENTER HUB (Merkezi kontrol paneli)
# ============================================================

class CenterHub(QFrame):
    """
    Ortadaki merkezi panel
    Kullanıcı bilgileri ve quick stats
    """
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setObjectName("centerHub")
        self.setFixedSize(240, 240)
        
        self._init_ui()
        
    def _init_ui(self):
        """UI elemanları"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # User avatar (initial)
        initial = self.user_data.get('ad_soyad', 'U')[0].upper()
        avatar = QLabel(initial)
        avatar.setObjectName("userAvatar")
        avatar.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(80, 80)
        
        # User name
        name = QLabel(self.user_data.get('ad_soyad', 'Kullanıcı'))
        name.setObjectName("userName")
        name.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        
        # User role
        role = QLabel(self.user_data.get('role', 'Rol'))
        role.setObjectName("userRole")
        role.setFont(QFont("Segoe UI", 11))
        role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Quick stat (örnek: aktif sınav sayısı)
        stat = QLabel("5 Aktif Sınav")
        stat.setObjectName("quickStat")
        stat.setFont(QFont("Segoe UI", 10))
        stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(avatar)
        layout.addWidget(name)
        layout.addWidget(role)
        layout.addSpacing(8)
        layout.addWidget(stat)
        layout.addStretch()


# ============================================================
# ACTIVITY FEED (Son işlemler)
# ============================================================

class ActivityFeed(QFrame):
    """
    Son işlemler ve bildirimler
    Timeline görünümü
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("activityFeed")
        
        self._init_ui()
        
    def _init_ui(self):
        """UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Son İşlemler")
        header.setObjectName("feedHeader")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        
        layout.addWidget(header)
        
        # Activity items
        activities = [
            ("Bilgisayar Müh. Final Programı oluşturuldu", "2 saat önce", "#10B981"),
            ("301 nolu derslik kapasitesi güncellendi", "5 saat önce", "#3B82F6"),
            ("Yazılım Müh. Vize sınavı tamamlandı", "1 gün önce", "#8B5CF6"),
            ("Yeni öğrenci listesi yüklendi (142 kayıt)", "2 gün önce", "#F59E0B"),
        ]
        
        for title, time, color in activities:
            item = self._create_activity_item(title, time, color)
            layout.addWidget(item)
        
        layout.addStretch()
        
    def _create_activity_item(self, title, time, color):
        """Activity item widget"""
        item = QFrame()
        item.setObjectName("activityItem")
        
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(16, 12, 16, 12)
        item_layout.setSpacing(12)
        
        # Color indicator
        indicator = QFrame()
        indicator.setFixedSize(4, 40)
        indicator.setStyleSheet(f"background: {color}; border-radius: 2px;")
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setObjectName("activityTitle")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        title_label.setWordWrap(True)
        
        time_label = QLabel(time)
        time_label.setObjectName("activityTime")
        time_label.setFont(QFont("Segoe UI", 10))
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(time_label)
        
        item_layout.addWidget(indicator)
        item_layout.addLayout(content_layout, 1)
        
        return item


# ============================================================
# MAIN DASHBOARD VIEW
# ============================================================

class DashboardView(QWidget):
    """
    Ana dashboard ekranı
    - Radial navigation
    - Activity feed
    - Module switching
    """
    
    module_changed = Signal(str)  # "ders", "derslik", "sinav", "rapor"
    logout_requested = Signal()
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_admin = user_data.get('role') == 'Admin'
        
        self._init_ui()
        self._apply_styles()
        self._animate_entrance()
        
    def _init_ui(self):
        """Ana UI yapısı"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Content area (radial menu + activity feed)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(40)
        
        # Left: Radial navigation
        radial_area = self._create_radial_navigation()
        content_layout.addWidget(radial_area, 3)
        
        # Right: Activity feed
        self.activity_feed = ActivityFeed()
        content_layout.addWidget(self.activity_feed, 2)
        
        main_layout.addLayout(content_layout, 1)
        
    def _create_top_bar(self):
        """Üst bar (profil, bildirim, ayarlar)"""
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(70)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)
        
        # Logo ve başlık
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)
        
        logo = QLabel("KOÜ")
        logo.setObjectName("appLogo")
        logo.setFont(QFont("Segoe UI", 20, QFont.Weight.Black))
        
        title = QLabel("Sınav Takvimi Sistemi")
        title.setObjectName("appTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        
        logo_layout.addWidget(logo)
        logo_layout.addWidget(title)
        
        layout.addLayout(logo_layout)
        layout.addStretch()
        
        # Right actions
        # Notifications
        notif_btn = QPushButton("Bildirimler (3)")
        notif_btn.setObjectName("topBarBtn")
        notif_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Settings
        settings_btn = QPushButton("Ayarlar")
        settings_btn.setObjectName("topBarBtn")
        settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Logout
        logout_btn = QPushButton("Çıkış")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logout_btn.clicked.connect(self.logout_requested.emit)
        
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(logout_btn)
        
        return bar
        
    def _create_radial_navigation(self):
        """Dairesel navigasyon alanı"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Manual layout - dairesel yerleşim için
        self.radial_container = container
        
        # Center hub
        self.center_hub = CenterHub(self.user_data, container)
        
        # Radial buttons
        if self.is_admin:
            modules = [
                ("Dersler", "D", "#10B981", "ders"),
                ("Derslikler", "K", "#3B82F6", "derslik"),
                ("Sınavlar", "S", "#8B5CF6", "sinav"),
                ("Raporlar", "R", "#F59E0B", "rapor"),
                ("Kullanıcılar", "U", "#EF4444", "kullanici"),
                ("Loglar", "L", "#6B7280", "log"),
            ]
        else:
            modules = [
                ("Dersler", "D", "#10B981", "ders"),
                ("Derslikler", "K", "#3B82F6", "derslik"),
                ("Sınavlar", "S", "#8B5CF6", "sinav"),
                ("Raporlar", "R", "#F59E0B", "rapor"),
            ]
        
        self.radial_buttons = []
        for text, icon, color, module in modules:
            btn = RadialButton(text, icon, color, container)
            btn.clicked.connect(lambda checked, m=module: self._on_module_clicked(m))
            self.radial_buttons.append(btn)
        
        # Resize event'te konumları ayarla
        container.resizeEvent = self._on_radial_resize
        
        return container
        
    def _on_radial_resize(self, event):
        """Radial button'ları dairesel olarak yerleştir"""
        center_x = self.radial_container.width() // 2
        center_y = self.radial_container.height() // 2
        
        # Center hub konumu
        hub_x = center_x - self.center_hub.width() // 2
        hub_y = center_y - self.center_hub.height() // 2
        self.center_hub.move(hub_x, hub_y)
        
        # Radial buttons konumu (dairesel)
        radius = 280  # Merkeze uzaklık
        num_buttons = len(self.radial_buttons)
        
        for i, btn in enumerate(self.radial_buttons):
            angle = (360 / num_buttons) * i - 90  # -90: üstten başla
            angle_rad = math.radians(angle)
            
            btn_x = center_x + int(radius * math.cos(angle_rad)) - btn.width() // 2
            btn_y = center_y + int(radius * math.sin(angle_rad)) - btn.height() // 2
            
            btn.move(btn_x, btn_y)
    
    def _on_module_clicked(self, module_name):
        """Modül değişikliği"""
        print(f"Module clicked: {module_name}")
        self.module_changed.emit(module_name)
        
        # TODO: Sağ tarafta modül içeriğini göster
        # Şimdilik sadece activity feed var
        
    def _animate_entrance(self):
        """Giriş animasyonu"""
        # Center hub fade in
        hub_effect = QGraphicsOpacityEffect(self.center_hub)
        self.center_hub.setGraphicsEffect(hub_effect)
        hub_effect.setOpacity(0)
        
        hub_anim = QPropertyAnimation(hub_effect, b"opacity")
        hub_anim.setDuration(600)
        hub_anim.setStartValue(0)
        hub_anim.setEndValue(1)
        hub_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        hub_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        # Radial buttons cascade
        for i, btn in enumerate(self.radial_buttons):
            effect = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(effect)
            effect.setOpacity(0)
            
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Staggered start
            QTimer.singleShot(100 * (i + 1), anim.start)
        
    def _apply_styles(self):
        """Tema stilleri"""
        self.setStyleSheet("""
            /* Main Widget */
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A,
                    stop:1 #1E293B
                );
            }
            
            /* Top Bar */
            #topBar {
                background: rgba(255, 255, 255, 0.05);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #appLogo {
                color: #10B981;
                background: transparent;
            }
            
            #appTitle {
                color: white;
                background: transparent;
            }
            
            #topBarBtn {
                background: rgba(255, 255, 255, 0.05);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: 600;
            }
            
            #topBarBtn:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            #logoutBtn {
                background: rgba(239, 68, 68, 0.1);
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: 600;
            }
            
            #logoutBtn:hover {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #EF4444;
            }
            
            /* Center Hub */
            #centerHub {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(16, 185, 129, 0.1),
                    stop:1 rgba(16, 185, 129, 0.05)
                );
                border: 2px solid rgba(16, 185, 129, 0.3);
                border-radius: 120px;
            }
            
            #userAvatar {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10B981,
                    stop:1 #059669
                );
                color: white;
                border-radius: 40px;
            }
            
            #userName {
                color: white;
                background: transparent;
            }
            
            #userRole {
                color: #10B981;
                background: transparent;
            }
            
            #quickStat {
                color: rgba(255, 255, 255, 0.6);
                background: transparent;
            }
            
            /* Activity Feed */
            #activityFeed {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
            
            #feedHeader {
                color: white;
                background: transparent;
            }
            
            #activityItem {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
            
            #activityItem:hover {
                background: rgba(255, 255, 255, 0.08);
            }
            
            #activityTitle {
                color: white;
                background: transparent;
            }
            
            #activityTime {
                color: rgba(255, 255, 255, 0.5);
                background: transparent;
            }
        """)