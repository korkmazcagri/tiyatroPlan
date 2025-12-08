import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QFrame, QLabel, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import config

# Sayfaları içe aktar
from app.views.pages.home_page import HomePage
from app.views.pages.calendar_page import CalendarPage
from app.views.pages.plays_page import PlaysPage
from app.views.pages.actors_page import ActorsPage
from app.views.pages.venues_page import VenuesPage
# --- YENİ SAYFA IMPORT EDİLDİ ---
from app.views.pages.payment_page import PaymentPage
# --------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # --- İKON AYARI (Exe için gerekli) ---
        icon_path = os.path.join("assets", "icon.jpg")
        self.setWindowIcon(QIcon(icon_path))
        # -------------------------------------

        # Ana Konteyner
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 1. SOL MENÜ (SIDEBAR) ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(10)

        # Logo / Başlık
        self.lbl_logo = QLabel("PRAY TİYATRO\nYÖNETİM SİSTEMİ")
        self.lbl_logo.setObjectName("logo_text")
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.lbl_logo)

        # Menü Butonları Grubu
        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)

        # --- MENÜ BUTONLARI OLUŞTURMA ---
        # Sayfa Index'leri 0'dan başlıyor ve sıralı olmalı!
        self.create_menu_item("Ana Sayfa", 0)       # Index 0
        self.create_menu_item("Takvim", 1)          # Index 1
        self.create_menu_item("Oyunlar", 2)         # Index 2
        self.create_menu_item("Oyuncu ve Teknik", 3) # Index 3
        self.create_menu_item("Sahneler", 4)        # Index 4
        self.create_menu_item("Ödemeler", 5)        # Index 5 (YENİ EKLENDİ)

        self.sidebar_layout.addStretch()

        # Versiyon Bilgisi
        lbl_version = QLabel(f"v{config.VERSION}")
        lbl_version.setStyleSheet("color: #555; padding: 10px;")
        lbl_version.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(lbl_version)

        # --- 2. SAĞ İÇERİK ALANI ---
        self.content_area = QStackedWidget()

        # --- SAYFALAR LİSTESİ GÜNCELLENDİ ---
        self.pages = [
            HomePage(),        # 0
            CalendarPage(),    # 1
            PlaysPage(),       # 2
            ActorsPage(),      # 3
            VenuesPage(),      # 4
            PaymentPage()      # 5 (YENİ EKLENDİ)
        ]

        for page in self.pages:
            self.content_area.addWidget(page)

        # Layout Birleşimi
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def create_menu_item(self, text, index):
        """Menüye buton ekler ve tıklandığında sayfayı değiştirir."""
        btn = QPushButton(text)
        btn.setObjectName("menu_btn")
        btn.setProperty("class", "menu_btn")
        btn.setCheckable(True)
        if index == 0: btn.setChecked(True)

        # Lambda ile index gönderiyoruz
        btn.clicked.connect(lambda: self.switch_page(index))

        self.sidebar_layout.addWidget(btn)
        self.menu_group.addButton(btn)

    def switch_page(self, index):
        """Sayfayı değiştirir ve verileri yeniler."""
        self.content_area.setCurrentIndex(index)

        # --- [YENİ] VERİ YENİLEME MANTIĞI ---
        current_widget = self.content_area.widget(index)

        # Eğer sayfanın 'load_data' fonksiyonu varsa çalıştır (Home, Actors, Payment)
        if hasattr(current_widget, "load_data"):
            current_widget.load_data()

        # Eğer sayfanın 'refresh_calendar' fonksiyonu varsa çalıştır (Takvim)
        if hasattr(current_widget, "refresh_calendar"):
            current_widget.refresh_calendar()

        # Eğer oyuncular sayfasında liste yenileme varsa
        if hasattr(current_widget, "refresh_list"):
            current_widget.refresh_list()