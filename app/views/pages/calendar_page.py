from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QDialog, QFormLayout, QComboBox,
                             QTimeEdit, QLineEdit, QListWidget, QListWidgetItem,
                             QFrame, QMessageBox, QSizePolicy, QScrollArea) # QMessageBox burada olmalı

from PyQt5.QtCore import Qt, QDate, QRect, QTime # QTime burada olmalı
from PyQt5.QtGui import QColor
from app.controllers.calendar_controller import CalendarController


# =============================================================================
# 1. POPUP PENCERE (Ekleme ve Düzenleme İşlemleri Burada)
# =============================================================================
class EventDialog(QDialog):
    def __init__(self, parent=None, date=None, event_id=None):
        super().__init__(parent)
        self.controller = CalendarController()
        self.selected_date = date
        self.event_id = event_id

        self.setWindowTitle("Etkinlik Planla" if not event_id else "Etkinlik Düzenle")
        self.setFixedWidth(550)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: white; border: 2px solid #FFD700; }
            QLabel { color: white; font-weight: bold; }
            QLineEdit, QComboBox, QTimeEdit { 
                background-color: #2c2c2c; color: white; border: 1px solid #555; padding: 5px; 
            }
            QListWidget { background-color: #2c2c2c; color: white; border: 1px solid #555; }
            QPushButton { background-color: #FFD700; color: black; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #e6c200; }
            QPushButton#btn_delete { background-color: #c0392b; color: white; }
            QPushButton#btn_small { padding: 2px; width: 30px; }
        """)

        self.init_ui()
        if self.event_id:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- TARİH KISMI (TÜRKÇE) ---
        tr_months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
            7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        tr_days = {
            1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe", 5: "Cuma", 6: "Cumartesi", 7: "Pazar"
        }

        gun = self.selected_date.day()
        ay = tr_months[self.selected_date.month()]
        yil = self.selected_date.year()
        gun_adi = tr_days[self.selected_date.dayOfWeek()]

        date_str = f"{gun} {ay} {yil}, {gun_adi}"

        lbl_date = QLabel(f"TARİH: {date_str}")
        lbl_date.setStyleSheet("font-size: 16px; color: #FFD700; margin-bottom: 10px;")
        lbl_date.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_date)

        # Form
        form_layout = QFormLayout()

        self.combo_play = QComboBox()
        self.combo_play.currentIndexChanged.connect(self.on_play_changed)

        self.combo_city = QComboBox()
        self.combo_city.currentTextChanged.connect(self.on_city_changed)

        self.combo_venue = QComboBox()
        self.combo_venue.currentIndexChanged.connect(self.on_venue_changed)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")

        self.input_note = QLineEdit()

        form_layout.addRow("Oyun:", self.combo_play)
        form_layout.addRow("Şehir:", self.combo_city)
        form_layout.addRow("Sahne:", self.combo_venue)
        form_layout.addRow("Saat:", self.time_edit)
        form_layout.addRow("Not:", self.input_note)

        layout.addLayout(form_layout)

        # --- KADRO SEÇİMİ ---
        cast_layout = QHBoxLayout()

        # 1. OYUNCULAR
        vbox_act = QVBoxLayout()
        vbox_act.addWidget(QLabel("Oyuncu Kadrosu"))

        hbox_act_sel = QHBoxLayout()
        self.combo_actors = QComboBox()  # Adaylar
        btn_add_act = QPushButton("+")
        btn_add_act.setObjectName("btn_small")
        btn_add_act.clicked.connect(self.add_actor)
        btn_rem_act = QPushButton("-")
        btn_rem_act.setObjectName("btn_small")
        btn_rem_act.clicked.connect(self.rem_actor)

        hbox_act_sel.addWidget(self.combo_actors)
        hbox_act_sel.addWidget(btn_add_act)
        hbox_act_sel.addWidget(btn_rem_act)
        vbox_act.addLayout(hbox_act_sel)

        self.list_actors = QListWidget()  # Seçilenler
        vbox_act.addWidget(self.list_actors)
        cast_layout.addLayout(vbox_act)

        # 2. REJİ
        vbox_crew = QVBoxLayout()
        vbox_crew.addWidget(QLabel("Reji / Teknik"))

        hbox_crew_sel = QHBoxLayout()
        self.combo_crew = QComboBox()
        btn_add_crew = QPushButton("+")
        btn_add_crew.setObjectName("btn_small")
        btn_add_crew.clicked.connect(self.add_crew)
        btn_rem_crew = QPushButton("-")
        btn_rem_crew.setObjectName("btn_small")
        btn_rem_crew.clicked.connect(self.rem_crew)

        hbox_crew_sel.addWidget(self.combo_crew)
        hbox_crew_sel.addWidget(btn_add_crew)
        hbox_crew_sel.addWidget(btn_rem_crew)
        vbox_crew.addLayout(hbox_crew_sel)

        self.list_crew = QListWidget()
        vbox_crew.addWidget(self.list_crew)
        cast_layout.addLayout(vbox_crew)

        layout.addLayout(cast_layout)

        # Alt Butonlar
        btn_box = QHBoxLayout()

        if self.event_id:
            self.btn_delete = QPushButton("Etkinliği Sil")
            self.btn_delete.setObjectName("btn_delete")
            self.btn_delete.clicked.connect(self.delete_event)
            btn_box.addWidget(self.btn_delete)

        btn_box.addStretch()

        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setStyleSheet("background-color: #444; color: white;")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Kaydet")
        self.btn_save.clicked.connect(self.save_event)
        btn_box.addWidget(self.btn_save)

        layout.addLayout(btn_box)

        # İlk Yükleme
        self.load_initial_data()

    # --- VERİ YÖNETİMİ ---
    def load_initial_data(self):
        # Oyunları Yükle
        self.combo_play.clear()
        plays = self.controller.get_active_plays()
        for p in plays:
            self.combo_play.addItem(p['oyun_adi'], p['id'])

        # Şehirleri Yükle
        self.combo_city.clear()
        cities = self.controller.get_distinct_cities()
        for c in cities:
            self.combo_city.addItem(c['sehir'])

        # Varsayılan İst
        if self.combo_city.findText("İstanbul") != -1:
            self.combo_city.setCurrentText("İstanbul")
        elif self.combo_city.count() > 0:
            self.combo_city.setCurrentIndex(0)

        # Reji Adaylarını Yükle
        self.combo_crew.clear()
        crew = self.controller.get_crew_candidates()
        for c in crew:
            self.combo_crew.addItem(c['ad_soyad'], c['id'])
        self.update_actor_candidates()
    def on_city_changed(self, city):
        self.combo_venue.clear()
        if not city: return
        venues = self.controller.get_venues_by_city(city)
        for v in venues:
            self.combo_venue.addItem(v['sahne_adi'], v['id'])

    def on_venue_changed(self):
        self.update_actor_candidates()

    def on_play_changed(self):
        self.update_actor_candidates()

    def update_actor_candidates(self):
        self.combo_actors.clear()

        play_id = self.combo_play.currentData()
        current_city = self.combo_city.currentText()  # Şehir ismini al

        if not play_id: return

        # Mantığı Controller'a bıraktık, sadece şehri gönderiyoruz
        actors = self.controller.get_cast_candidates(play_id, city_name=current_city)

        for a in actors:
            item_text = f"{a['ad_soyad']} ({a['durum']})"
            self.combo_actors.addItem(item_text, a['id'])
    def add_actor(self):
        if self.combo_actors.currentIndex() == -1: return
        name = self.combo_actors.currentText()
        a_id = self.combo_actors.currentData()
        # Tekrar kontrolü
        for i in range(self.list_actors.count()):
            if self.list_actors.item(i).data(Qt.UserRole) == a_id: return
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, a_id)
        self.list_actors.addItem(item)

    def rem_actor(self):
        row = self.list_actors.currentRow()
        if row != -1: self.list_actors.takeItem(row)

    def add_crew(self):
        if self.combo_crew.currentIndex() == -1: return
        name = self.combo_crew.currentText()
        c_id = self.combo_crew.currentData()
        for i in range(self.list_crew.count()):
            if self.list_crew.item(i).data(Qt.UserRole) == c_id: return
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, c_id)
        self.list_crew.addItem(item)

    def rem_crew(self):
        row = self.list_crew.currentRow()
        if row != -1: self.list_crew.takeItem(row)

    # --- DÜZENLEME MODU (CRASH FIX İÇERİR) ---
    def load_data(self):
        print(">>> load_data BAŞLADI")  # 1. Kontrol
        data = self.controller.get_event_full_detail(self.event_id)
        if not data: return

        print(">>> Sinyaller bloklanıyor...")
        self.combo_play.blockSignals(True)
        self.combo_city.blockSignals(True)
        self.combo_venue.blockSignals(True)

        try:
            # 1. Oyun Seç
            print(f">>> Oyun Seçiliyor: ID {data['oyun_id']}")
            idx_play = self.combo_play.findData(data['oyun_id'])
            if idx_play != -1: self.combo_play.setCurrentIndex(idx_play)

            # 2. Şehri Bul ve Seç
            venue_city = self.controller.get_city_of_venue(data['sahne_id'])
            print(f">>> Şehir Bulundu: {venue_city}")

            if venue_city:
                print(">>> Şehir Combobox Ayarlanıyor...")
                self.combo_city.setCurrentText(venue_city)

                print(">>> Sahneler Manuel Dolduruluyor...")
                self.combo_venue.clear()
                venues = self.controller.get_venues_by_city(venue_city)
                for v in venues:
                    self.combo_venue.addItem(v['sahne_adi'], v['id'])

                print(f">>> Sahne Seçiliyor: ID {data['sahne_id']}")
                idx_venue = self.combo_venue.findData(data['sahne_id'])
                if idx_venue != -1: self.combo_venue.setCurrentIndex(idx_venue)

            self.time_edit.setTime(QTime.fromString(data['baslangic_saati'], "HH:mm"))
            self.input_note.setText(data['notlar'])
            self.update_actor_candidates()
        except Exception as e:
            print(f"!!! HATA OLUŞTU: {e}")  # Hata varsa buraya düşer

        finally:
            print(">>> Sinyaller Geri Açılıyor...")
            self.combo_play.blockSignals(False)
            self.combo_city.blockSignals(False)
            self.combo_venue.blockSignals(False)

        print(">>> load_data BİTTİ")
    def save_event(self):
        play_id = self.combo_play.currentData()
        venue_id = self.combo_venue.currentData()
        if not play_id or not venue_id:
            QMessageBox.warning(self, "Eksik", "Oyun ve Sahne seçiniz.")
            return

        actor_ids = [self.list_actors.item(i).data(Qt.UserRole) for i in range(self.list_actors.count())]
        crew_ids = [self.list_crew.item(i).data(Qt.UserRole) for i in range(self.list_crew.count())]

        date_str = self.selected_date.toString("yyyy-MM-dd")
        time_str = self.time_edit.text()
        note = self.input_note.text()

        if self.event_id:
            self.controller.update_event_with_cast(self.event_id, play_id, venue_id, date_str, time_str, note,
                                                   actor_ids, crew_ids)
        else:
            self.controller.add_event_with_cast(play_id, venue_id, date_str, time_str, note, actor_ids, crew_ids)

        self.accept()

    def delete_event(self):
        try:
            reply = QMessageBox.question(self, 'Sil', 'Bu etkinliği silmek istiyor musunuz?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.controller.delete_event(self.event_id)
                self.accept()  # Pencereyi kapat
        except Exception as e:
            print(f"Silme Hatası: {e}")
            # Eğer QMessageBox import edilmemişse konsola yazsın, kapanmasın.


# =============================================================================
# 2. ANA TAKVİM SAYFASI (GRID GÖRÜNÜMÜ)
# =============================================================================
class CalendarPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CalendarController()
        self.current_date = QDate.currentDate()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- HEADER ---
        header_layout = QHBoxLayout()

        self.btn_prev = QPushButton("< Önceki Ay")
        self.btn_prev.clicked.connect(self.prev_month)
        self.btn_prev.setFixedWidth(100)

        self.lbl_month = QLabel()
        self.lbl_month.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700;")
        self.lbl_month.setAlignment(Qt.AlignCenter)

        self.btn_next = QPushButton("Sonraki Ay >")
        self.btn_next.clicked.connect(self.next_month)
        self.btn_next.setFixedWidth(100)

        header_layout.addWidget(self.btn_prev)
        header_layout.addWidget(self.lbl_month)
        header_layout.addWidget(self.btn_next)

        layout.addLayout(header_layout)

        # --- GRID TAKVİM ---
        self.grid = QTableWidget()
        self.grid.setColumnCount(7)
        self.grid.setRowCount(6)

        headers = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        self.grid.setHorizontalHeaderLabels(headers)

        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setVisible(False)
        self.grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid.setSelectionMode(QAbstractItemView.NoSelection)
        self.grid.setFocusPolicy(Qt.NoFocus)
        self.grid.setStyleSheet("""
            QTableWidget { background-color: #121212; border: none; gridline-color: #333; }
            QHeaderView::section { background-color: #1e1e1e; color: #aaa; border: 1px solid #333; padding: 10px; font-weight: bold; }
        """)

        self.grid.cellDoubleClicked.connect(self.on_cell_double_clicked)

        layout.addWidget(self.grid)
        self.refresh_calendar()

    def refresh_calendar(self):
        year = self.current_date.year()
        month = self.current_date.month()

        # Türkçe Ay İsmi
        tr_months = {
            1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
        }
        month_name = f"{tr_months[month]} {year}"
        self.lbl_month.setText(month_name)

        first_day = QDate(year, month, 1)
        start_index = first_day.dayOfWeek() - 1
        days_in_month = first_day.daysInMonth()

        self.grid.clearContents()

        events = self.controller.get_events_for_month(year, month)
        events_by_date = {}
        for ev in events:
            d = ev['tarih']
            if d not in events_by_date: events_by_date[d] = []
            events_by_date[d].append(ev)

        day_counter = 1
        for row in range(6):
            for col in range(7):
                if row == 0 and col < start_index: continue
                if day_counter > days_in_month: break

                current_day = QDate(year, month, day_counter)
                date_str = current_day.toString("yyyy-MM-dd")

                # --- HÜCRE İÇERİĞİ ---
                cell_widget = QWidget()
                cell_layout = QVBoxLayout(cell_widget)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(2)

                # 1. ÜST SATIR (+ ve Gün No)
                top_row = QHBoxLayout()
                top_row.setContentsMargins(0, 0, 0, 0)

                btn_quick_add = QPushButton("+")
                btn_quick_add.setFixedSize(22, 22)
                btn_quick_add.setCursor(Qt.PointingHandCursor)
                btn_quick_add.setStyleSheet("""
                    QPushButton { 
                        background-color: #FFD700; color: #000000;            
                        border-radius: 11px; font-weight: bold; font-size: 19px;           
                        border: none; padding-bottom: 4px; margin: 0px;
                    }
                    QPushButton:hover { background-color: #ffcc00; }
                """)
                btn_quick_add.clicked.connect(lambda _, d=current_day: self.open_edit_dialog(d, None))

                lbl_num = QLabel(str(day_counter))
                lbl_num.setAlignment(Qt.AlignRight)
                if current_day == QDate.currentDate():
                    lbl_num.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
                else:
                    lbl_num.setStyleSheet("color: #777;")

                top_row.addWidget(btn_quick_add)
                top_row.addStretch()
                top_row.addWidget(lbl_num)

                cell_layout.addLayout(top_row)

                # 2. SCROLL AREA (Sadece Dikey)
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setFrameShape(QFrame.NoFrame)

                # --- [DEĞİŞİKLİK BURADA] ---
                # Yatay kaydırmayı tamamen kapatıyoruz
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                # Dikey kaydırma sadece gerekirse çıksın
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                # ---------------------------

                scroll_area.setStyleSheet("""
                    QScrollArea { background: transparent; border: none; }
                    QScrollBar:vertical { width: 6px; background: #2c2c2c; }
                    QScrollBar::handle:vertical { background: #555; border-radius: 3px; }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
                """)

                scroll_content = QWidget()
                scroll_content.setStyleSheet("background: transparent;")
                scroll_layout = QVBoxLayout(scroll_content)
                scroll_layout.setContentsMargins(0, 0, 0, 0)
                scroll_layout.setSpacing(2)

                if date_str in events_by_date:
                    for ev in events_by_date[date_str]:
                        self.create_event_button(scroll_layout, ev, current_day)

                scroll_layout.addStretch()
                scroll_area.setWidget(scroll_content)
                cell_layout.addWidget(scroll_area)

                self.grid.setCellWidget(row, col, cell_widget)

                item = QTableWidgetItem()
                item.setData(Qt.UserRole, current_day)
                self.grid.setItem(row, col, item)

                day_counter += 1
    def create_event_button(self, layout, event_data, date_obj):
        colors = [
            "#e74c3c", "#3498db", "#9b59b6", "#2ecc71", "#f1c40f", "#e67e22",
            "#1abc9c", "#34495e", "#16a085", "#27ae60", "#2980b9", "#8e44ad",  # Turkuaz, Koyu Gri, Deniz Yeşili...
            "#f39c12", "#d35400", "#c0392b", "#7f8c8d", "#d2b4de", "#f5b7b1",
            "#a9dfbf", "#fad7a0"
        ]
        color = colors[event_data['oyun_id'] % len(colors)]

        btn = QPushButton(f"{event_data['baslangic_saati']} {event_data['oyun_adi']}")

        tooltip_text = (f"<b>{event_data['oyun_adi']}</b><br>"
                        f"⏰ Saat: {event_data['baslangic_saati']}<br>"
                        f"📍 Sahne: {event_data['sahne_adi']}<br>"
                        f"🎭 Oyuncular: {event_data['oyuncu_listesi']}")
        btn.setToolTip(tooltip_text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: white; border-radius: 3px;
                text-align: left; padding: 2px 5px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #ddd; color: black; }}
        """)
        btn.clicked.connect(lambda: self.open_edit_dialog(date_obj, event_data['id']))
        layout.addWidget(btn)

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.refresh_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.refresh_calendar()

    def on_cell_double_clicked(self, row, col):
        item = self.grid.item(row, col)
        if item:
            date_obj = item.data(Qt.UserRole)
            if date_obj:
                dialog = EventDialog(self, date=date_obj)
                if dialog.exec_():
                    self.refresh_calendar()

    def open_edit_dialog(self, date_obj, event_id):
        dialog = EventDialog(self, date=date_obj, event_id=event_id)
        if dialog.exec_():
            self.refresh_calendar()