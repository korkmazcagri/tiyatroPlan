from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from PyQt5.QtCore import Qt
from app.controllers.home_controller import HomeController


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = HomeController()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # --- 1. BAŞLIK ---
        title = QLabel("PRAY TİYATRO YÖNETİM PANELİ")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFD700;")
        main_layout.addWidget(title)

        subtitle = QLabel("Genel durum özeti ve yaklaşan temsiller aşağıdadır.")
        subtitle.setStyleSheet("font-size: 16px; color: #aaa; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

        # --- 2. İSTATİSTİK KARTLARI ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_personel = self.create_info_card("Toplam Personel", "0")
        self.card_oyun = self.create_info_card("Aktif Oyunlar", "0")
        self.card_etkinlik = self.create_info_card("Yaklaşan Temsiller", "0")

        cards_layout.addWidget(self.card_personel)
        cards_layout.addWidget(self.card_oyun)
        cards_layout.addWidget(self.card_etkinlik)

        main_layout.addLayout(cards_layout)

        # --- 3. YAKLAŞAN ETKİNLİKLER TABLOSU ---
        lbl_table = QLabel("YAKLAŞAN TEMSİLLER & KADRO")
        lbl_table.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700; margin-top: 30px;")
        main_layout.addWidget(lbl_table)

        self.table = QTableWidget()
        # Sütun Sayısı: 7 oldu (Tarih, Saat, Oyun, Sahne, Şehir, Oyuncular, Reji)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Tarih", "Saat", "Oyun", "Sahne", "Şehir", "Oyuncular", "Reji"])

        # Sütun Genişlik Ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # İçeriğe göre daralt (Tarih, Saat)
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Oyun Adı (Genişle)
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Oyuncular (Genişle)
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Reji (Genişle)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setWordWrap(True)  # İsimler çoksa alt satıra geçsin

        # Satır yüksekliğini içeriğe göre ayarla
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.setMinimumHeight(300)

        main_layout.addWidget(self.table)
        main_layout.addStretch()

        self.refresh_data()

    def create_info_card(self, title, value):
        card = QFrame()
        card.setObjectName("add_game_box")
        card.setStyleSheet("""
            QFrame#add_game_box {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-top: 3px solid #FFD700;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(card)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        lbl_value.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; color: #aaa;")
        lbl_title.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl_value)
        layout.addWidget(lbl_title)

        return card

    def refresh_data(self):
        """Veritabanından güncel bilgileri çeker."""
        stats = self.controller.get_summary_stats()

        self.card_personel.layout().itemAt(0).widget().setText(str(stats['personel']))
        self.card_oyun.layout().itemAt(0).widget().setText(str(stats['oyunlar']))
        self.card_etkinlik.layout().itemAt(0).widget().setText(str(stats['etkinlikler']))

        # Tabloyu Güncelle
        events = self.controller.get_upcoming_events()
        self.table.setRowCount(0)

        for row, data in enumerate(events):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(data['tarih']))
            self.table.setItem(row, 1, QTableWidgetItem(data['baslangic_saati']))

            item_game = QTableWidgetItem(data['oyun_adi'])
            item_game.setForeground(Qt.yellow)
            self.table.setItem(row, 2, item_game)

            self.table.setItem(row, 3, QTableWidgetItem(data['sahne_adi']))
            self.table.setItem(row, 4, QTableWidgetItem(data['sehir']))

            # Yeni Sütunlar: Kadro
            self.table.setItem(row, 5, QTableWidgetItem(data['oyuncular']))
            self.table.setItem(row, 6, QTableWidgetItem(data['reji']))

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)