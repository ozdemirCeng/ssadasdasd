"""
dashboard_view.py
Ana Dashboard - İstatistikler ve Özet Bilgiler
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from models.database import db


class StatCard(QFrame):
    """Modern istatistik kartı"""

    def __init__(self, icon, title, value, subtitle="", color="#00A651", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Üst kısım - Icon ve değer
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        # Icon container
        icon_container = QFrame()
        icon_container.setObjectName("iconContainer")
        icon_container.setFixedSize(56, 56)
        icon_container.setStyleSheet(f"""
            #iconContainer {{
                background: {color};
                border-radius: 14px;
            }}
        """)

        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: white;")
        icon_layout.addWidget(icon_label)

        # Value container
        value_container = QWidget()
        value_layout = QVBoxLayout(value_container)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(4)

        value_label = QLabel(str(value))
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Medium))

        value_layout.addWidget(value_label)
        value_layout.addWidget(title_label)

        top_layout.addWidget(icon_container)
        top_layout.addWidget(value_container, 1)

        layout.addLayout(top_layout)

        # Alt kısım - Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("statSubtitle")
            subtitle_label.setFont(QFont("Segoe UI", 9))
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)


class ActivityCard(QFrame):
    """Son aktiviteler kartı"""

    def __init__(self, icon, text, time, parent=None):
        super().__init__(parent)
        self.setObjectName("activityCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 18))
        icon_label.setFixedWidth(30)

        # Text container
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        text_label = QLabel(text)
        text_label.setObjectName("activityText")
        text_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        text_label.setWordWrap(True)

        time_label = QLabel(time)
        time_label.setObjectName("activityTime")
        time_label.setFont(QFont("Segoe UI", 9))

        text_layout.addWidget(text_label)
        text_layout.addWidget(time_label)

        layout.addWidget(icon_label)
        layout.addWidget(text_container, 1)


class DashboardView(QWidget):
    """Ana Dashboard Sayfası"""

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.stats = {}

        self.setup_ui()
        self.apply_styles()
        self.load_statistics()

    def setup_ui(self):
        """UI oluştur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(30)

        # İstatistik kartları
        stats_grid = self.create_stats_grid()
        scroll_layout.addWidget(stats_grid)

        # Alt kısım - Son aktiviteler ve hızlı eylemler
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(24)

        # Son aktiviteler
        activities = self.create_activities_section()
        bottom_layout.addWidget(activities, 6)

        # Hızlı eylemler
        quick_actions = self.create_quick_actions()
        bottom_layout.addWidget(quick_actions, 4)

        scroll_layout.addLayout(bottom_layout)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def create_header(self):
        """Sayfa başlığı"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Hoşgeldin mesajı
        greeting = QLabel(f"Hoş geldiniz, {self.user_data['ad_soyad'].split()[0]}! 👋")
        greeting.setObjectName("pageTitle")
        greeting.setFont(QFont("Segoe UI", 28, QFont.Bold))

        # Subtitle
        subtitle = QLabel("İşte sisteminizin genel durumu")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setFont(QFont("Segoe UI", 13))

        layout.addWidget(greeting)
        layout.addWidget(subtitle)

        return container

    def create_stats_grid(self):
        """İstatistik kartları grid"""
        container = QFrame()
        container.setObjectName("statsContainer")

        layout = QGridLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stat cards placeholder
        self.stat_cards = {}

        cards_config = [
            ("toplam_ders", "📚", "Toplam Ders", "#3b82f6"),
            ("toplam_ogrenci", "👨‍🎓", "Toplam Öğrenci", "#8b5cf6"),
            ("toplam_derslik", "🏢", "Toplam Derslik", "#f59e0b"),
            ("aktif_program", "📅", "Aktif Program", "#10b981")
        ]

        for idx, (key, icon, title, color) in enumerate(cards_config):
            card = StatCard(icon, title, "...", "", color)
            self.stat_cards[key] = card
            layout.addWidget(card, idx // 2, idx % 2)

        return container

    def create_activities_section(self):
        """Son aktiviteler bölümü"""
        container = QFrame()
        container.setObjectName("sectionCard")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Başlık
        header_layout = QHBoxLayout()

        title = QLabel("📋 Son Aktiviteler")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_activities)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Activity list container
        self.activities_container = QWidget()
        self.activities_layout = QVBoxLayout(self.activities_container)
        self.activities_layout.setContentsMargins(0, 0, 0, 0)
        self.activities_layout.setSpacing(8)

        layout.addWidget(self.activities_container)
        layout.addStretch()

        return container

    def create_quick_actions(self):
        """Hızlı eylemler bölümü"""
        container = QFrame()
        container.setObjectName("sectionCard")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Başlık
        title = QLabel("⚡ Hızlı Eylemler")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        # Action buttons
        actions = [
            ("🏢", "Derslik Ekle", "derslik"),
            ("📚", "Ders Yükle", "ders"),
            ("👨‍🎓", "Öğrenci Yükle", "ogrenci"),
            ("📅", "Sınav Oluştur", "sinav")
        ]

        for icon, text, page in actions:
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName("quickActionBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(52)
            btn.setFont(QFont("Segoe UI", 11, QFont.Medium))
            layout.addWidget(btn)

        layout.addStretch()

        return container

    def load_statistics(self):
        """İstatistikleri veritabanından yükle"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            # Toplam ders sayısı
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM dersler
                           WHERE aktif = TRUE
                             AND (%(bolum_id)s IS NULL OR bolum_id = %(bolum_id)s)
                           """, {'bolum_id': self.user_data.get('bolum_id')})
            toplam_ders = cursor.fetchone()[0]

            # Toplam öğrenci sayısı
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM ogrenciler
                           WHERE aktif = TRUE
                             AND (%(bolum_id)s IS NULL OR bolum_id = %(bolum_id)s)
                           """, {'bolum_id': self.user_data.get('bolum_id')})
            toplam_ogrenci = cursor.fetchone()[0]

            # Toplam derslik sayısı
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM derslikler
                           WHERE aktif = TRUE
                             AND (%(bolum_id)s IS NULL OR bolum_id = %(bolum_id)s)
                           """, {'bolum_id': self.user_data.get('bolum_id')})
            toplam_derslik = cursor.fetchone()[0]

            # Aktif program sayısı
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM sinav_programi
                           WHERE (%(bolum_id)s IS NULL OR bolum_id = %(bolum_id)s)
                             AND bitis_tarihi >= CURRENT_DATE
                           """, {'bolum_id': self.user_data.get('bolum_id')})
            aktif_program = cursor.fetchone()[0]

            cursor.close()

            # Update cards
            self.update_stat_card("toplam_ders", toplam_ders, f"{toplam_ders} ders kayıtlı")
            self.update_stat_card("toplam_ogrenci", toplam_ogrenci, f"{toplam_ogrenci} öğrenci")
            self.update_stat_card("toplam_derslik", toplam_derslik, f"{toplam_derslik} derslik mevcut")
            self.update_stat_card("aktif_program", aktif_program, f"{aktif_program} aktif program")

        except Exception as e:
            print(f"İstatistik yükleme hatası: {e}")

    def update_stat_card(self, key, value, subtitle):
        """Stat card güncelle"""
        if key in self.stat_cards:
            card = self.stat_cards[key]
            # Value label'ı bul ve güncelle
            for child in card.findChildren(QLabel):
                if child.objectName() == "statValue":
                    child.setText(str(value))
                elif child.objectName() == "statSubtitle":
                    child.setText(subtitle)

    def load_activities(self):
        """Son aktiviteleri yükle"""
        try:
            # Önceki aktiviteleri temizle
            while self.activities_layout.count():
                child = self.activities_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            conn = db.get_connection()
            cursor = conn.cursor()

            # Son import logları
            cursor.execute("""
                           SELECT il.dosya_adi,
                                  il.dosya_tipi,
                                  il.basarili_kayit,
                                  il.created_at,
                                  u.ad_soyad
                           FROM import_logs il
                                    JOIN users u ON il.user_id = u.user_id
                           WHERE (%(bolum_id)s IS NULL OR u.bolum_id = %(bolum_id)s)
                           ORDER BY il.created_at DESC LIMIT 5
                           """, {'bolum_id': self.user_data.get('bolum_id')})

            logs = cursor.fetchall()
            cursor.close()

            if logs:
                for log in logs:
                    dosya_adi, dosya_tipi, basarili, created_at, kullanici = log

                    icon = "📚" if dosya_tipi == "Ders Listesi" else "👨‍🎓"
                    text = f"{kullanici} - {dosya_tipi} yükledi ({basarili} kayıt)"
                    time_str = created_at.strftime("%d.%m.%Y %H:%M")

                    activity = ActivityCard(icon, text, time_str)
                    self.activities_layout.addWidget(activity)
            else:
                # Henüz aktivite yok
                no_activity = QLabel("Henüz aktivite bulunmuyor")
                no_activity.setObjectName("noDataLabel")
                no_activity.setFont(QFont("Segoe UI", 11))
                no_activity.setAlignment(Qt.AlignCenter)
                self.activities_layout.addWidget(no_activity)

        except Exception as e:
            print(f"Aktivite yükleme hatası: {e}")

    def refresh_data(self):
        """Sayfaya her girildiğinde verileri yenile"""
        self.load_statistics()
        self.load_activities()

    def apply_styles(self):
        """Modern stil"""
        self.setStyleSheet("""
            /* Page Title */
            #pageTitle {
                color: #111827;
            }

            #pageSubtitle {
                color: #6b7280;
            }

            /* Stats Container */
            #statsContainer {
                background: transparent;
            }

            /* Stat Card */
            #statCard {
                background: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }

            #statValue {
                color: #111827;
            }

            #statTitle {
                color: #6b7280;
            }

            #statSubtitle {
                color: #9ca3af;
            }

            /* Section Card */
            #sectionCard {
                background: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }

            #sectionTitle {
                color: #111827;
            }

            /* Activity Card */
            #activityCard {
                background: #f9fafb;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
            }

            #activityCard:hover {
                background: #f3f4f6;
                border: 1px solid #d1d5db;
            }

            #activityText {
                color: #374151;
            }

            #activityTime {
                color: #9ca3af;
            }

            /* Quick Action Button */
            QPushButton#quickActionBtn {
                background: #f9fafb;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                text-align: left;
                padding: 14px 18px;
                color: #374151;
            }

            QPushButton#quickActionBtn:hover {
                background: #00A651;
                border: 2px solid #00A651;
                color: white;
            }

            QPushButton#quickActionBtn:pressed {
                background: #008F47;
            }

            /* Refresh Button */
            QPushButton#refreshBtn {
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px 16px;
                color: #6b7280;
                font-size: 11px;
            }

            QPushButton#refreshBtn:hover {
                background: #e5e7eb;
                color: #374151;
            }

            /* Scroll Area */
            QScrollArea#dashboardScroll {
                border: none;
                background: transparent;
            }

            QScrollArea#dashboardScroll > QWidget > QWidget {
                background: transparent;
            }

            /* Scrollbar */
            QScrollBar:vertical {
                background: #f3f4f6;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #d1d5db;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }

            #noDataLabel {
                color: #9ca3af;
                padding: 40px;
            }
        """)