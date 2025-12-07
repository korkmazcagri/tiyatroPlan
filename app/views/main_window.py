from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QFrame, QLabel, QButtonGroup)
from PyQt5.QtCore import Qt
import config

# Sayfaları içe aktar
from app.views.pages.home_page import HomePage
from app.views.pages.calendar_page import CalendarPage
from app.views.pages.plays_page import PlaysPage
from app.views.pages.actors_page import ActorsPage
from app.views.pages.venues_page import VenuesPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

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

        # Menü Butonları Grubu (Biri seçilince diğerini söndürmek için)
        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)

        # Butonları Ekleme Fonksiyonu
        self.create_menu_item("Ana Sayfa", 0)
        self.create_menu_item("Takvim", 1)
        self.create_menu_item("Oyunlar", 2)
        self.create_menu_item("Oyuncu ve Teknik", 3)
        self.create_menu_item("Sahneler", 4)

        self.sidebar_layout.addStretch()  # Butonları yukarı it

        # Versiyon Bilgisi
        lbl_version = QLabel(f"v{config.VERSION}")
        lbl_version.setStyleSheet("color: #555; padding: 10px;")
        lbl_version.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(lbl_version)

        # --- 2. SAĞ İÇERİK ALANI ---
        self.content_area = QStackedWidget()

        # Sayfaları Yükle
        self.pages = [
            HomePage(),  # 0
            CalendarPage(),  # 1
            PlaysPage(),  # 2
            ActorsPage(),  # 3
            VenuesPage()  # 4
        ]

        for page in self.pages:
            self.content_area.addWidget(page)

        # Layout Birleşimi
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def create_menu_item(self, text, index):
        """Menüye buton ekler ve tıklandığında sayfayı değiştirir."""
        btn = QPushButton(text)
        btn.setObjectName("menu_btn")  # CSS sınıfı
        btn.setProperty("class", "menu_btn")  # Selector için
        btn.setCheckable(True)
        if index == 0: btn.setChecked(True)  # İlk açılışta ana sayfa seçili

        btn.clicked.connect(lambda: self.switch_page(index))

        self.sidebar_layout.addWidget(btn)
        self.menu_group.addButton(btn)

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)