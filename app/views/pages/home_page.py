from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QFrame, QPushButton, QDialog,
                             QDoubleSpinBox, QMessageBox, QScrollArea, QAbstractSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from app.controllers.home_controller import HomeController


# =============================================================================
# OYUN TAMAMLAMA VE FİNANS DİYALOĞU (POPUP)
# =============================================================================
class FinalizeDialog(QDialog):
    def __init__(self, parent, event_id, event_name):
        super().__init__(parent)
        self.controller = HomeController()
        self.event_id = event_id
        self.staff_inputs = {}

        self.setWindowTitle(f"Oyunu Tamamla: {event_name}")
        self.setFixedWidth(600)  # Biraz genişlettik

        # --- STİL DOSYASI ---
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: white; border: 2px solid #FFD700; }
            QLabel { color: white; font-size: 14px; }

            /* SAYI KUTUSU TASARIMI (Daha belirgin) */
            QDoubleSpinBox { 
                background-color: #111;         
                color: #2ecc71;                 
                border: 1px solid #555;         
                border-radius: 4px; 
                padding: 8px; 
                font-weight: bold;
                font-size: 15px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #FFD700;      
                background-color: #000;
            }

            QPushButton { 
                background-color: #FFD700; color: black; font-weight: bold; 
                padding: 10px; border-radius: 5px; 
            }
            QPushButton:hover { background-color: #e6c200; }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        lbl_info = QLabel("Bu oyun 'Oynandı' olarak işaretlenecek.\n"
                          "Aşağıdaki personellere yansıtılacak hakedişleri kontrol edin.")
        lbl_info.setStyleSheet("color: #aaa; margin-bottom: 15px; font-style: italic;")
        lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_info)

        # --- PERSONEL LİSTESİ ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        container = QWidget()
        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(15)  # Satırlar arası boşluk artırıldı

        staff_list = self.controller.get_event_staff_details(self.event_id)

        if not staff_list:
            layout.addWidget(QLabel("⚠️ Bu oyuna atanmış personel bulunamadı!"))
        else:
            for person in staff_list:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(0, 0, 0, 0)

                # --- SOL TARAFTAKİ BİLGİLER (İki ayrı Label kullanıyoruz) ---
                info_layout = QVBoxLayout()
                info_layout.setSpacing(4)

                # 1. İsim ve Görev (Beyaz)
                lbl_name = QLabel(f"{person['ad_soyad']} ({person['gorev']})")
                lbl_name.setStyleSheet("font-weight: bold; font-size: 15px; color: white;")

                # 2. Ödeme Tipi (Renkli ve Küçük - HTML YOK)
                lbl_type = QLabel(f"Ödeme Tipi: {person['odeme_tipi']}")
                lbl_type.setStyleSheet("color: #f39c12; font-size: 12px; font-weight: normal;")

                info_layout.addWidget(lbl_name)
                info_layout.addWidget(lbl_type)

                # --- SAĞ TARAFTAKİ ÜCRET KUTUSU ---
                spin = QDoubleSpinBox()
                spin.setMaximum(100000)
                spin.setButtonSymbols(QAbstractSpinBox.NoButtons)  # Okları gizle
                spin.setSuffix(" TL")
                spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                spin.setFixedWidth(130)  # Kutuyu genişlet

                default_wage = person['standart_ucret'] if person['standart_ucret'] else 0
                spin.setValue(default_wage)

                self.staff_inputs[person['id']] = spin

                # Hepsini satıra ekle
                row.addLayout(info_layout)  # Sol (Yazılar)
                row.addStretch()  # Araya boşluk
                row.addWidget(spin)  # Sağ (Kutu)

                # Ayırıcı Çizgi (Altına)
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet("background-color: #333; max-height: 1px;")

                form_layout.addWidget(row_widget)
                form_layout.addWidget(line)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # --- BUTONLAR ---
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setStyleSheet("background-color: #444; color: white;")
        btn_cancel.clicked.connect(self.reject)

        btn_confirm = QPushButton("✅ ONAYLA VE BİTİR")
        btn_confirm.setStyleSheet("background-color: #27ae60; color: white;")
        btn_confirm.clicked.connect(self.save_and_finish)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)

        layout.addLayout(btn_layout)

    def save_and_finish(self):
        payments = {}
        for p_id, spin in self.staff_inputs.items():
            payments[p_id] = spin.value()

        success = self.controller.process_play_finance(self.event_id, payments)

        if success:
            QMessageBox.information(self, "Başarılı",
                                    "Oyun tamamlandı, durum güncellendi ve ücretler finansa yansıtıldı.")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", "İşlem sırasında bir hata oluştu.")


# =============================================================================
# ANA SAYFA (HOME PAGE)
# =============================================================================
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = HomeController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. BAŞLIK
        header_layout = QHBoxLayout()
        lbl_title = QLabel("TİYATRO YÖNETİM PANELİ")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700;")
        lbl_date = QLabel(QDate.currentDate().toString("dd MMMM yyyy, dddd"))
        lbl_date.setStyleSheet("font-size: 14px; color: #aaa;")

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(lbl_date)
        layout.addLayout(header_layout)

        # 2. İSTATİSTİK KARTLARI
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        card1 = self.create_stat_card("Aktif Oyun Sayısı", str(self.controller.get_total_active_plays()), "#3498db")
        card2 = self.create_stat_card("Toplam Personel", str(self.controller.get_total_personel()), "#e67e22")
        self.lbl_pending_count = QLabel("0")
        card3 = self.create_stat_card_widget("Bekleyen Temsiller", self.lbl_pending_count, "#9b59b6")

        stats_layout.addWidget(card1)
        stats_layout.addWidget(card2)
        stats_layout.addWidget(card3)
        layout.addLayout(stats_layout)

        # 3. BEKLEYEN OYUNLAR TABLOSU
        lbl_table_title = QLabel("🎭 OYNANMAMIŞ / BEKLEYEN TEMSİLLER")
        lbl_table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff; margin-top: 10px;")
        layout.addWidget(lbl_table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)  # +1 Buton Sütunu
        self.table.setHorizontalHeaderLabels(["Tarih", "Saat", "Oyun", "Şehir", "Sahne", "İşlem"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 120)  # Buton sütununu sabitledik

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e; color: #ddd; border: 1px solid #333; border-radius: 8px; padding: 5px;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #2c2c2c; }
            QHeaderView::section { background-color: #2c2c2c; color: #FFD700; font-weight: bold; padding: 8px; border: none; }
        """)

        layout.addWidget(self.table)
        self.load_data()

    def create_stat_card(self, title, value, color):
        lbl_val = QLabel(value)
        return self.create_stat_card_widget(title, lbl_val, color)

    def create_stat_card_widget(self, title, val_widget, color):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 10px; }}")
        card.setFixedHeight(80)
        l = QVBoxLayout(card)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: rgba(255,255,255,0.8); font-weight: bold;")

        val_widget.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        val_widget.setAlignment(Qt.AlignRight)

        l.addWidget(lbl_t)
        l.addWidget(val_widget)
        return card

    def load_data(self):
        events = self.controller.get_pending_events()
        if events is None: events = []

        self.table.setRowCount(0)
        self.lbl_pending_count.setText(str(len(events)))

        for row, data in enumerate(events):
            self.table.insertRow(row)

            # --- [DÜZELTME] SATIR YÜKSEKLİĞİNİ AYARLA ---
            # Butonun kesilmemesi için satırı genişletiyoruz (Örn: 50px)
            self.table.setRowHeight(row, 50)
            # --------------------------------------------

            qdate = QDate.fromString(data['tarih'], "yyyy-MM-dd")
            date_str = qdate.toString("dd.MM.yyyy")

            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(data['baslangic_saati']))

            item_game = QTableWidgetItem(data['oyun_adi'])
            item_game.setFont(QFont("Arial", 10, QFont.Bold))
            item_game.setForeground(QColor("#FFD700"))
            self.table.setItem(row, 2, item_game)

            self.table.setItem(row, 3, QTableWidgetItem(data['sehir']))
            self.table.setItem(row, 4, QTableWidgetItem(data['sahne_adi']))

            # --- BUTON TASARIMI ---
            btn_complete = QPushButton("✔️ Oynandı")
            btn_complete.setCursor(Qt.PointingHandCursor)
            btn_complete.setFixedHeight(30)  # Buton yüksekliği
            btn_complete.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60; 
                    color: white; 
                    font-weight: bold;
                    border-radius: 4px; 
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #2ecc71; }
            """)
            btn_complete.clicked.connect(
                lambda _, eid=data['id'], ename=data['oyun_adi']: self.open_finalize_dialog(eid, ename))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)  # Buton etrafına boşluk
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(btn_complete)
            self.table.setCellWidget(row, 5, container)

    def open_finalize_dialog(self, event_id, event_name):
        dialog = FinalizeDialog(self, event_id, event_name)
        if dialog.exec_():
            self.load_data()