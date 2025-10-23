"""
views/main_window.py
Kocaeli Üniversitesi - Professional Dashboard with Sidebar Menu
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGraphicsOpacityEffect, QSizePolicy, QProgressBar,
    QApplication, QStackedWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, Signal, QParallelAnimationGroup
from PySide6.QtGui import QFont, QIcon, QPainter, QPainterPath, QColor, QLinearGradient

sys.path.append(str(Path(__file__).parent.parent))

# Import views
from views.koordinator.derslik_view import DerslikView
from views.koordinator.ders_yukle_view import DersYukleView
from views.koordinator.ogrenci_yukle_view import OgrenciYukleView
from views.koordinator.sinav_olustur_view import SinavOlusturView
from views.koordinator.oturma_plani_view import OturmaPaniView
from views.koordinator.raporlar_view import RaporlarView
from views.koordinator.ayarlar_view import AyarlarView


class Theme:
    """Tema yönetimi"""

    def __init__(self, dark_mode=False):
        self.dark_mode = dark_mode

    @property
    def bg(self):
        return "#0f172a" if self.dark_mode else "#f9fafb"

    @property
    def card(self):
        return "#1e293b" if self.dark_mode else "#ffffff"

    @property
    def border(self):
        return "#334155" if self.dark_mode else "#e5e7eb"

    @property
    def text(self):
        return "#f1f5f9" if self.dark_mode else "#111827"

    @property
    def text_muted(self):
        return "#94a3b8" if self.dark_mode else "#6b7280"

    @property
    def hover(self):
        return "#334155" if self.dark_mode else "#f3f4f6"

    @property
    def sidebar(self):
        return "#1e293b" if self.dark_mode else "#ffffff"

    @property
    def menu_active(self):
        if self.dark_mode:
            return "background: rgba(16, 185, 129, 0.2); color: #34d399;"
        return "background: #ecfdf5; color: #047857;"


class ModernButton(QPushButton):
    """Modern buton komponenti"""

    def __init__(self, text="", icon_char="", parent=None):
        super().__init__(text, parent)
        self.icon_char = icon_char
        self.setCursor(Qt.PointingHandCursor)
        
    def enterEvent(self, event):
        self.animate_scale(1.05)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animate_scale(1.0)
        super().leaveEvent(event)
        
    def animate_scale(self, scale):
        # Simple hover effect via stylesheet
        pass


class StatCard(QFrame):
    """İstatistik kartı"""

    def __init__(self, label, value, total, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.value = value
        self.total = total
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color: {theme.text_muted}; font-weight: 500;")

        val = QLabel(str(value))
        val.setFont(QFont("Segoe UI", 20, QFont.Bold))
        val.setStyleSheet("color: #10b981;")

        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(val)

        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(total)
        progress.setValue(value)
        progress.setTextVisible(False)
        progress.setFixedHeight(8)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background: {"#334155" if theme.dark_mode else "#f3f4f6"};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #14b8a6);
                border-radius: 4px;
            }}
        """)

        # Total label
        total_lbl = QLabel(f"Toplam: {total}")
        total_lbl.setFont(QFont("Segoe UI", 8))
        total_lbl.setStyleSheet(f"color: {theme.text_muted};")

        layout.addLayout(header)
        layout.addWidget(progress)
        layout.addWidget(total_lbl)

        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {self.theme.card};
                border: 1px solid {self.theme.border};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid #10b981;
            }}
        """)


class QuickActionCard(QFrame):
    """Hızlı işlem kartı"""

    clicked = Signal()

    def __init__(self, label, desc, icon, color, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.color = color
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)

        # Title
        title = QLabel(label)
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet(f"color: {theme.text};")

        # Description
        description = QLabel(desc)
        description.setFont(QFont("Segoe UI", 9))
        description.setStyleSheet(f"color: {theme.text_muted};")

        layout.addWidget(icon_container)
        layout.addWidget(title)
        layout.addWidget(description)

        self.update_style()

    def update_style(self):
        color_map = {
            'emerald': ('#ecfdf5', '#10b981', '#d1fae5') if not self.theme.dark_mode else ('rgba(16, 185, 129, 0.1)',
                                                                                           '#10b981',
                                                                                           'rgba(16, 185, 129, 0.2)'),
            'blue': ('#eff6ff', '#2563eb', '#dbeafe') if not self.theme.dark_mode else ('rgba(37, 99, 235, 0.1)',
                                                                                        '#2563eb',
                                                                                        'rgba(37, 99, 235, 0.2)'),
            'indigo': ('#eef2ff', '#4f46e5', '#e0e7ff') if not self.theme.dark_mode else ('rgba(79, 70, 229, 0.1)',
                                                                                          '#4f46e5',
                                                                                          'rgba(79, 70, 229, 0.2)'),
            'orange': ('#fff7ed', '#f97316', '#ffedd5') if not self.theme.dark_mode else ('rgba(249, 115, 22, 0.1)',
                                                                                          '#f97316',
                                                                                          'rgba(249, 115, 22, 0.2)')
        }

        bg, text, border = color_map.get(self.color, color_map['emerald'])

        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QFrame:hover {{
                transform: scale(1.05);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
        """)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class MenuButton(QPushButton):
    """Sidebar menü butonu"""

    def __init__(self, text, icon, theme, parent=None):
        super().__init__(parent)
        self.menu_text = text
        self.icon = icon
        self.theme = theme
        self.is_active = False
        self.is_collapsed = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)

        self.update_style()

    def set_active(self, active):
        self.is_active = active
        self.update_style()

    def set_collapsed(self, collapsed):
        self.is_collapsed = collapsed
        self.update_style()

    def update_style(self):
        if self.is_active:
            bg = self.theme.menu_active
        else:
            bg = f"background: transparent; color: {self.theme.text_muted};"

        self.setStyleSheet(f"""
            QPushButton {{
                {bg}
                border: none;
                border-radius: 12px;
                text-align: left;
                padding-left: {"16px" if not self.is_collapsed else "0px"};
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {self.theme.hover};
            }}
        """)

        if self.is_collapsed:
            self.setText(self.icon)
            self.setToolTip(self.menu_text)
        else:
            self.setText(f"{self.icon}  {self.menu_text}")


class MainWindow(QMainWindow):
    """Ana pencere - Professional Dashboard"""

    module_opened = Signal(str)
    logout_requested = Signal()

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.theme = Theme(dark_mode=False)
        self.sidebar_collapsed = False
        self.active_menu = 'dashboard'
        self.pages = {}  # Sayfa önbelleği

        self.setWindowTitle(f"KOÜ Sınav Takvimi - {user_data.get('ad_soyad')}")
        self.setMinimumSize(1400, 800)

        self.setup_ui()
        self.apply_styles()

        self.showMaximized()

    def setup_ui(self):
        """UI kurulumu"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        main_layout.addWidget(self.create_top_bar())

        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = self.create_sidebar()
        content_layout.addWidget(self.sidebar)

        # Main content - QStackedWidget for page transitions
        self.content_stack = QStackedWidget()

        # Dashboard sayfa
        self.dashboard_page = self.create_dashboard_page()
        self.content_stack.addWidget(self.dashboard_page)
        self.pages['dashboard'] = self.dashboard_page

        content_layout.addWidget(self.content_stack, 1)

        main_layout.addWidget(content)

    def create_top_bar(self):
        """Üst bar"""
        bar = QFrame()
        bar.setFixedHeight(73)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        # Logo + Title
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setSpacing(16)

        # Logo
        logo = QLabel("🎓")
        logo.setFont(QFont("Segoe UI", 24))
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #10b981, stop:1 #14b8a6);
            border-radius: 11px;
        """)

        # Title
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(2)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Sınav Takvimi Yönetim Sistemi")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))

        subtitle = QLabel("Kocaeli Üniversitesi")
        subtitle.setFont(QFont("Segoe UI", 10))

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        logo_layout.addWidget(logo)
        logo_layout.addWidget(title_widget)
        
        layout.addWidget(logo_container)
        layout.addStretch()
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)

        # User info
        user_widget = QFrame()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setSpacing(12)

        avatar = QLabel("A")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #10b981, stop:1 #14b8a6);
            color: white;
            border-radius: 9px;
        """)

        user_info = QWidget()
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setSpacing(0)
        user_info_layout.setContentsMargins(0, 0, 0, 0)

        name = QLabel(self.user_data.get('ad_soyad', 'Kullanıcı'))
        name.setFont(QFont("Segoe UI", 10, QFont.Bold))

        role = QLabel(self.user_data.get('role', 'Admin'))
        role.setFont(QFont("Segoe UI", 8))

        user_info_layout.addWidget(name)
        user_info_layout.addWidget(role)

        user_layout.addWidget(avatar)
        user_layout.addWidget(user_info)

        # Logout button
        logout_btn = QPushButton("↪")
        logout_btn.setFixedSize(40, 40)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-radius: 10px;
                color: #ef4444;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
            }
        """)

        layout.addWidget(self.theme_btn)
        layout.addWidget(user_widget)
        layout.addWidget(logout_btn)
        
        return bar
        
    def create_sidebar(self):
        """Sidebar oluştur"""
        sidebar = QFrame()
        sidebar.setFixedWidth(288)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        # Menu items
        menu_items = [
            ('🏠', 'Ana Sayfa', 'dashboard'),
            ('🏛', 'Derslikler', 'derslikler'),
            ('📚', 'Ders Listesi', 'dersler'),
            ('👥', 'Öğrenci Listesi', 'ogrenciler'),
            ('📅', 'Sınav Programı', 'sinavlar'),
            ('📝', 'Oturma Planı', 'oturma'),
            ('📊', 'Raporlar', 'raporlar'),
            ('⚙', 'Ayarlar', 'ayarlar')
        ]

        self.menu_buttons = []
        for icon, text, menu_id in menu_items:
            btn = MenuButton(text, icon, self.theme)
            # Lambda ile menu_id'yi doğru şekilde yakala
            btn.clicked.connect(lambda checked=False, mid=menu_id: self.switch_menu(mid))
            layout.addWidget(btn)
            self.menu_buttons.append((btn, menu_id))

        # Collapse button
        layout.addStretch()

        collapse_btn = QPushButton("◀")
        collapse_btn.setFixedHeight(32)
        collapse_btn.setCursor(Qt.PointingHandCursor)
        collapse_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(collapse_btn)

        self.collapse_btn = collapse_btn
        self.menu_buttons[0][0].set_active(True)

        return sidebar

    def create_dashboard_page(self):
        """Dashboard sayfası"""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Stats grid
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(16)

        # Get real statistics from database
        try:
            from models.database import db
            from models.sinav_model import SinavModel
            from models.ders_model import DersModel
            from models.derslik_model import DerslikModel
            from models.ogrenci_model import OgrenciModel

            bolum_id = self.user_data.get('bolum_id', 1)

            sinav_model = SinavModel(db)
            ders_model = DersModel(db)
            derslik_model = DerslikModel(db)
            ogrenci_model = OgrenciModel(db)

            # Get counts
            programlar = sinav_model.get_programs_by_bolum(bolum_id)
            aktif_sinav_count = sum(len(sinav_model.get_sinavlar_by_program(p['program_id'])) for p in programlar if p.get('aktif', True))

            dersler = ders_model.get_dersler_by_bolum(bolum_id)
            ders_count = len(dersler)

            derslikler = derslik_model.get_derslikler_by_bolum(bolum_id)
            derslik_count = len(derslikler)

            ogrenciler = ogrenci_model.get_ogrenciler_by_bolum(bolum_id)
            ogrenci_count = len(ogrenciler)

            stats = [
                ("Aktif Sınavlar", aktif_sinav_count, max(aktif_sinav_count + 10, 30)),
                ("Toplam Dersler", ders_count, max(ders_count + 10, 60)),
                ("Derslikler", derslik_count, max(derslik_count + 5, 15)),
                ("Öğrenciler", ogrenci_count, max(ogrenci_count + 100, 1000))
            ]
        except Exception as e:
            import logging
            logging.error(f"Dashboard stats error: {e}")
            # Fallback to default values
            stats = [
                ("Aktif Sınavlar", 0, 30),
                ("Toplam Dersler", 0, 60),
                ("Derslikler", 0, 15),
                ("Öğrenciler", 0, 1000)
            ]

        for label, value, total in stats:
            card = StatCard(label, value, total, self.theme)
            stats_layout.addWidget(card)

        layout.addWidget(stats_container)

        # Welcome card
        welcome_card = self.create_welcome_card()
        layout.addWidget(welcome_card)

        # System status
        status_card = self.create_status_card()
        layout.addWidget(status_card)

        return content

    def create_welcome_card(self):
        """Hoş geldiniz kartı"""
        card = QFrame()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()

        header_text = QWidget()
        header_layout = QVBoxLayout(header_text)
        header_layout.setSpacing(4)

        title = QLabel(f"Hoş Geldiniz, {self.user_data.get('ad_soyad')} 👋")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        subtitle = QLabel("Bugün ne yapmak istersiniz?")
        subtitle.setFont(QFont("Segoe UI", 11))

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        header.addWidget(header_text)
        header.addStretch()

        layout.addLayout(header)

        # Quick actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setSpacing(16)

        actions = [
            ("Derslik Ekle", "Yeni derslik tanımla", "🏛", "emerald", "derslikler"),
            ("Excel Yükle", "Ders/Öğrenci listesi", "📄", "blue", "dersler"),
            ("Program Oluştur", "Sınav takvimi yap", "📅", "indigo", "sinavlar"),
            ("Rapor Al", "PDF/Excel çıktı", "📊", "orange", "raporlar")
        ]

        for label, desc, icon, color, page_id in actions:
            action_card = QuickActionCard(label, desc, icon, color, self.theme)
            # Lambda ile page_id'yi doğru şekilde yakala
            action_card.clicked.connect(lambda checked=False, pid=page_id: self.switch_menu(pid))
            actions_layout.addWidget(action_card)

        layout.addWidget(actions_container)

        return card

    def create_status_card(self):
        """Sistem durumu kartı"""
        card = QFrame()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Sistem Durumu")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))

        layout.addWidget(title)

        # Status items
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setSpacing(24)

        statuses = [
            ("0", "Bekleyen Sınav", "emerald"),
            ("0", "Aktif Program", "blue"),
            ("15", "Gün Kaldı", "orange")
        ]

        for value, label, color in statuses:
            item = QWidget()
            item_layout = QVBoxLayout(item)
            item_layout.setAlignment(Qt.AlignCenter)

            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 32, QFont.Bold))
            val.setAlignment(Qt.AlignCenter)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setAlignment(Qt.AlignCenter)

            item_layout.addWidget(val)
            item_layout.addWidget(lbl)

            status_layout.addWidget(item)

        layout.addWidget(status_container)

        return card

    def toggle_theme(self):
        """Tema değiştir"""
        self.theme.dark_mode = not self.theme.dark_mode
        self.theme_btn.setText("☀" if self.theme.dark_mode else "🌙")
        self.apply_styles()

        # Update all components
        for btn, _ in self.menu_buttons:
            btn.theme = self.theme
            btn.update_style()

    def toggle_sidebar(self):
        """Sidebar aç/kapat"""
        self.sidebar_collapsed = not self.sidebar_collapsed

        if self.sidebar_collapsed:
            self.sidebar.setFixedWidth(80)
            self.collapse_btn.setText("▶")
        else:
            self.sidebar.setFixedWidth(288)
            self.collapse_btn.setText("◀")

        for btn, _ in self.menu_buttons:
            btn.set_collapsed(self.sidebar_collapsed)

    def switch_menu(self, menu_id):
        """Menü değiştir ve sayfaya geç"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Switching to menu: {menu_id}")

        self.active_menu = menu_id

        # Menü butonlarını güncelle
        for btn, mid in self.menu_buttons:
            btn.set_active(mid == menu_id)

        # Sayfa geçişi
        self.show_page(menu_id)

        # Signal emit
        self.module_opened.emit(menu_id)

    def show_page(self, page_id):
        """Sayfayı göster (animasyonlu geçiş)"""
        import logging
        logger = logging.getLogger(__name__)

        # Sayfa önbellekte yoksa oluştur
        if page_id not in self.pages:
            try:
                logger.info(f"Creating page: {page_id}")
                page_widget = self.create_page(page_id)
                if page_widget:
                    self.content_stack.addWidget(page_widget)
                    self.pages[page_id] = page_widget
                    logger.info(f"Page created successfully: {page_id}")
                else:
                    logger.warning(f"Page widget is None for: {page_id}")
                    return
            except Exception as e:
                logger.error(f"Error creating page {page_id}: {e}", exc_info=True)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    "Sayfa Yükleme Hatası",
                    f"'{page_id}' sayfası yüklenirken hata oluştu:\n\n{str(e)}\n\nDetaylar için log dosyasını kontrol edin."
                )
                return

        # Sayfaya geç
        if page_id in self.pages:
            target_page = self.pages[page_id]
            current_index = self.content_stack.currentIndex()
            target_index = self.content_stack.indexOf(target_page)

            # Animasyonlu geçiş için opacity efekti
            if current_index != target_index:
                logger.debug(f"Switching to page: {page_id} (index: {target_index})")
                self.animate_page_transition(target_page)
                self.content_stack.setCurrentWidget(target_page)
        else:
            logger.error(f"Page {page_id} not found in pages dict after creation attempt")

    def create_page(self, page_id):
        """Sayfa widget'ı oluştur"""
        import logging
        logger = logging.getLogger(__name__)

        page_map = {
            'dashboard': lambda: self.dashboard_page,
            'derslikler': lambda: DerslikView(self.user_data),
            'dersler': lambda: DersYukleView(self.user_data),
            'ogrenciler': lambda: OgrenciYukleView(self.user_data),
            'sinavlar': lambda: SinavOlusturView(self.user_data),
            'oturma': lambda: OturmaPaniView(self.user_data),
            'raporlar': lambda: RaporlarView(self.user_data),
            'ayarlar': lambda: AyarlarView(self.user_data)
        }

        if page_id in page_map:
            try:
                logger.debug(f"Instantiating page widget for: {page_id}")
                widget = page_map[page_id]()
                logger.debug(f"Page widget instantiated: {page_id} -> {type(widget).__name__}")
                return widget
            except Exception as e:
                logger.error(f"Error instantiating page widget for {page_id}: {e}", exc_info=True)
                raise
        else:
            logger.warning(f"Unknown page_id: {page_id}")
            return None

    def create_placeholder_page(self, title, icon):
        """Placeholder sayfa oluştur"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 72))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {self.theme.text_muted};")

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.theme.text};")

        subtitle = QLabel("Bu özellik yakında eklenecek")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.theme.text_muted};")

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle)

        return page

    def animate_page_transition(self, target_widget):
        """Sayfa geçiş animasyonu"""
        try:
            # Fade in efekti
            effect = QGraphicsOpacityEffect(target_widget)
            target_widget.setGraphicsEffect(effect)

            self._current_animation = QPropertyAnimation(effect, b"opacity")
            self._current_animation.setDuration(200)
            self._current_animation.setStartValue(0.3)
            self._current_animation.setEndValue(1.0)
            self._current_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self._current_animation.start()
        except Exception as e:
            # Animasyon hatasında sessizce devam et
            import logging
            logging.debug(f"Animation error (non-critical): {e}")

    def handle_logout(self):
        """Çıkış yap"""
        # Signal emit et - main.py handle edecek
        self.logout_requested.emit()

    def apply_styles(self):
        """Stilleri uygula - Cam görünümü ile"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {self.theme.bg};
            }}
            QFrame {{
                background: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 16px;
                backdrop-filter: blur(10px);
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.4);
            }}
            QLabel {{
                color: {self.theme.text};
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background: {self.theme.card};
                border: 1px solid {self.theme.border};
                border-radius: 10px;
                color: {self.theme.text};
            }}
            QPushButton:hover {{
                background: {self.theme.hover};
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    user_data = {
        'user_id': 1,
        'email': 'admin@kocaeli.edu.tr',
        'role': 'Admin',
        'ad_soyad': 'Ahmet Yılmaz',
        'bolum_id': None
    }

    window = MainWindow(user_data)
    window.show()

    sys.exit(app.exec())