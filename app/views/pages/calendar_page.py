from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QDialog, QFormLayout, QComboBox,
                             QTimeEdit, QLineEdit, QListWidget, QListWidgetItem, QFileDialog,
                             QFrame, QMessageBox, QSizePolicy, QScrollArea)

from PyQt5.QtCore import Qt, QDate, QRect, QTime
from PyQt5.QtGui import QColor, QTextDocument, QPageSize, QPageLayout
from app.controllers.calendar_controller import CalendarController
from app.controllers.tour_controller import TourController
from app.controllers.venue_controller import VenueController
from app.controllers.personel_controller import PersonelController
from PyQt5.QtPrintSupport import QPrinter
from itertools import groupby
from PyQt5.QtWidgets import QShortcut # Diğerlerinin yanına ekle
from PyQt5.QtGui import QKeySequence # Diğerlerinin yanına ekle

# =============================================================================
# 1. POPUP PENCERE
# =============================================================================
class EventDialog(QDialog):
    def __init__(self, parent=None, date=None, event_id=None):
        super().__init__(parent)
        self.controller = CalendarController()
        self.tour_controller = TourController()
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
        tr_months = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                     7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
        tr_days = {1: "Pazartesi", 2: "Salı", 3: "Çarşamba", 4: "Perşembe", 5: "Cuma", 6: "Cumartesi", 7: "Pazar"}

        date_str = f"{self.selected_date.day()} {tr_months[self.selected_date.month()]} {self.selected_date.year()}, {tr_days[self.selected_date.dayOfWeek()]}"
        lbl_date = QLabel(f"TARİH: {date_str}")
        lbl_date.setStyleSheet("font-size: 16px; color: #FFD700; margin-bottom: 10px;")
        lbl_date.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_date)

        form_layout = QFormLayout()
        self.combo_play = QComboBox()
        self.combo_play.currentIndexChanged.connect(self.on_play_changed)

        self.combo_tour = QComboBox()
        self.combo_tour.addItem("Turne Ekibi Yok (Tüm Kadro)", None)
        self.combo_tour.currentIndexChanged.connect(self.update_actor_candidates)

        self.combo_city = QComboBox()
        self.combo_city.currentTextChanged.connect(self.on_city_changed)
        self.combo_venue = QComboBox()
        self.combo_venue.currentIndexChanged.connect(self.update_actor_candidates)
        self.time_edit = QTimeEdit();
        self.time_edit.setDisplayFormat("HH:mm")
        self.input_note = QLineEdit()

        form_layout.addRow("Oyun:", self.combo_play)
        form_layout.addRow("Turne Ekibi:", self.combo_tour)
        form_layout.addRow("Şehir:", self.combo_city)
        form_layout.addRow("Sahne:", self.combo_venue)
        form_layout.addRow("Saat:", self.time_edit)
        form_layout.addRow("Not:", self.input_note)
        layout.addLayout(form_layout)

        cast_layout = QHBoxLayout()
        # OYUNCULAR
        vbox_act = QVBoxLayout();
        vbox_act.addWidget(QLabel("Oyuncu Kadrosu"))
        hbox_act_sel = QHBoxLayout()
        self.combo_actors = QComboBox()
        btn_add_act = QPushButton("+");
        btn_add_act.setObjectName("btn_small");
        btn_add_act.clicked.connect(self.add_actor)
        btn_rem_act = QPushButton("-");
        btn_rem_act.setObjectName("btn_small");
        btn_rem_act.clicked.connect(self.rem_actor)
        hbox_act_sel.addWidget(self.combo_actors);
        hbox_act_sel.addWidget(btn_add_act);
        hbox_act_sel.addWidget(btn_rem_act)
        vbox_act.addLayout(hbox_act_sel);
        self.list_actors = QListWidget();
        vbox_act.addWidget(self.list_actors)
        cast_layout.addLayout(vbox_act)

        # REJİ
        vbox_crew = QVBoxLayout();
        vbox_crew.addWidget(QLabel("Reji / Teknik"))
        hbox_crew_sel = QHBoxLayout()
        self.combo_crew = QComboBox()
        btn_add_crew = QPushButton("+");
        btn_add_crew.setObjectName("btn_small");
        btn_add_crew.clicked.connect(self.add_crew)
        btn_rem_crew = QPushButton("-");
        btn_rem_crew.setObjectName("btn_small");
        btn_rem_crew.clicked.connect(self.rem_crew)
        hbox_crew_sel.addWidget(self.combo_crew);
        hbox_crew_sel.addWidget(btn_add_crew);
        hbox_crew_sel.addWidget(btn_rem_crew)
        vbox_crew.addLayout(hbox_crew_sel);
        self.list_crew = QListWidget();
        vbox_crew.addWidget(self.list_crew)
        cast_layout.addLayout(vbox_crew)
        layout.addLayout(cast_layout)

        btn_box = QHBoxLayout()
        if self.event_id:
            self.btn_status = QPushButton("Durum");
            self.btn_status.clicked.connect(self.toggle_event_status)
            self.btn_status.setFixedWidth(160);
            btn_box.addWidget(self.btn_status)
            self.btn_delete = QPushButton("Etkinliği Sil");
            self.btn_delete.setObjectName("btn_delete")
            self.btn_delete.clicked.connect(self.delete_event);
            btn_box.addWidget(self.btn_delete)
        btn_box.addStretch()
        self.btn_cancel = QPushButton("İptal");
        self.btn_cancel.setStyleSheet("background-color: #444; color: white;");
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Kaydet");
        self.btn_save.clicked.connect(self.save_event)
        btn_box.addWidget(self.btn_cancel);
        btn_box.addWidget(self.btn_save)
        layout.addLayout(btn_box)
        self.load_initial_data()

    def on_play_changed(self):
        play_id = self.combo_play.currentData()
        self.combo_tour.blockSignals(True);
        self.combo_tour.clear()
        self.combo_tour.addItem("Turne Ekibi Yok (Tüm Kadro)", None)
        if play_id:
            teams = self.tour_controller.get_teams_by_game(play_id)
            for t in teams: self.combo_tour.addItem(t['ekip_adi'], t['id'])
        self.combo_tour.blockSignals(False);
        self.update_actor_candidates()

    def update_actor_candidates(self):
        self.combo_actors.clear();
        self.combo_crew.clear()
        play_id = self.combo_play.currentData();
        team_id = self.combo_tour.currentData()
        current_city = self.combo_city.currentText();
        date_str = self.selected_date.toString("yyyy-MM-dd")
        all_actors = self.controller.get_cast_candidates(play_id, current_city, date_str) if play_id else []
        all_crew = self.controller.get_crew_candidates(date_str)
        if team_id:
            t_ids = [m['id'] for m in self.tour_controller.get_team_members(team_id)]
            f_actors = [a for a in all_actors if a['id'] in t_ids]
            f_crew = [c for c in all_crew if c['id'] in t_ids]
        else:
            f_actors, f_crew = all_actors, all_crew
        for a in f_actors: self.combo_actors.addItem(f"{a['ad_soyad']} ({a['durum']})", a['id'])
        for c in f_crew: self.combo_crew.addItem(c['ad_soyad'], c['id'])

    def load_initial_data(self):
        self.combo_play.clear()
        for p in self.controller.get_active_plays(): self.combo_play.addItem(p['oyun_adi'], p['id'])
        self.combo_city.clear()
        for c in self.controller.get_distinct_cities(): self.combo_city.addItem(c['sehir'])
        if self.combo_city.findText("İstanbul") != -1:
            self.combo_city.setCurrentText("İstanbul")
        elif self.combo_city.count() > 0:
            self.combo_city.setCurrentIndex(0)
        if self.combo_play.count() > 0: self.combo_play.setCurrentIndex(0)
        self.on_play_changed()

    def on_city_changed(self, city):
        self.combo_venue.clear()
        if not city: return
        for v in self.controller.get_venues_by_city(city): self.combo_venue.addItem(v['sahne_adi'], v['id'])

    def add_actor(self):
        if self.combo_actors.currentIndex() == -1: return
        n, i = self.combo_actors.currentText(), self.combo_actors.currentData()
        for x in range(self.list_actors.count()):
            if self.list_actors.item(x).data(Qt.UserRole) == i: return
        item = QListWidgetItem(n);
        item.setData(Qt.UserRole, i);
        self.list_actors.addItem(item)

    def rem_actor(self):
        r = self.list_actors.currentRow()
        if r != -1: self.list_actors.takeItem(r)

    def add_crew(self):
        if self.combo_crew.currentIndex() == -1: return
        n, i = self.combo_crew.currentText(), self.combo_crew.currentData()
        for x in range(self.list_crew.count()):
            if self.list_crew.item(x).data(Qt.UserRole) == i: return
        item = QListWidgetItem(n);
        item.setData(Qt.UserRole, i);
        self.list_crew.addItem(item)

    def rem_crew(self):
        r = self.list_crew.currentRow()
        if r != -1: self.list_crew.takeItem(r)

    def toggle_event_status(self):
        if self.current_status == 'Oynandı':
            if QMessageBox.question(self, 'Durum', 'Planlandıya çekilsin mi?',
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.controller.update_event_status(self.event_id, 'Planlandı');
                self.accept()
        else:
            if QMessageBox.question(self, 'Durum', 'Oynandı yapılsın mı?',
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.controller.update_event_status(self.event_id, 'Oynandı');
                self.accept()

    def load_data(self):
        d = dict(self.controller.get_event_full_detail(self.event_id))
        self.combo_play.blockSignals(True);
        self.combo_city.blockSignals(True);
        self.combo_venue.blockSignals(True);
        self.combo_tour.blockSignals(True)
        try:
            self.combo_play.setCurrentIndex(self.combo_play.findData(d['oyun_id']))
            city = self.controller.get_city_of_venue(d['sahne_id'])
            if city:
                self.combo_city.setCurrentText(city);
                self.combo_venue.clear()
                for v in self.controller.get_venues_by_city(city): self.combo_venue.addItem(v['sahne_adi'], v['id'])
                self.combo_venue.setCurrentIndex(self.combo_venue.findData(d['sahne_id']))
            self.time_edit.setTime(QTime.fromString(d['baslangic_saati'], "HH:mm"));
            self.input_note.setText(d.get('notlar', ""))
            self.combo_tour.clear();
            self.combo_tour.addItem("Turne Ekibi Yok (Tüm Kadro)", None)
            for t in self.tour_controller.get_teams_by_game(d['oyun_id']): self.combo_tour.addItem(t['ekip_adi'],
                                                                                                   t['id'])
            if d.get('turne_ekibi_id'): self.combo_tour.setCurrentIndex(self.combo_tour.findData(d['turne_ekibi_id']))
        finally:
            self.combo_play.blockSignals(False); self.combo_city.blockSignals(False); self.combo_venue.blockSignals(
                False); self.combo_tour.blockSignals(False)
        self.update_actor_candidates()
        self.list_actors.clear()
        for a in self.controller.get_event_cast_ids(self.event_id, "Oyuncu"):
            item = QListWidgetItem(self.controller.get_person_name(a));
            item.setData(Qt.UserRole, a);
            self.list_actors.addItem(item)
        self.list_crew.clear()
        for c in self.controller.get_event_cast_ids(self.event_id, "Reji"):
            item = QListWidgetItem(self.controller.get_person_name(c));
            item.setData(Qt.UserRole, c);
            self.list_crew.addItem(item)

    def save_event(self):
        p, v, t_id = self.combo_play.currentData(), self.combo_venue.currentData(), self.combo_tour.currentData()
        if not p or not v: QMessageBox.warning(self, "Eksik", "Oyun/Sahne seçin."); return
        a_ids = [self.list_actors.item(i).data(Qt.UserRole) for i in range(self.list_actors.count())]
        c_ids = [self.list_crew.item(i).data(Qt.UserRole) for i in range(self.list_crew.count())]
        dt, tm, nt = self.selected_date.toString("yyyy-MM-dd"), self.time_edit.text(), self.input_note.text()
        if self.event_id:
            self.controller.update_event_with_cast(self.event_id, p, v, dt, tm, nt, a_ids, c_ids, t_id)
        else:
            self.controller.add_event_with_cast(p, v, dt, tm, nt, a_ids, c_ids, t_id)
        self.accept()

    def delete_event(self):
        if QMessageBox.question(self, 'Sil', 'Silinsin mi?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.controller.delete_event(self.event_id);
            self.accept()


# =============================================================================
# 2. ANA TAKVİM SAYFASI
# =============================================================================
class CalendarPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CalendarController()
        self.tour_controller = TourController()
        self.current_date = QDate.currentDate()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10);
        layout.setSpacing(10)

        # --- FİLTRE ALANI ---
        f_frame = QFrame();
        f_frame.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; padding: 10px;")
        f_layout = QHBoxLayout(f_frame)
        self.f_play = QComboBox();
        self.f_play.addItem("Tüm Oyunlar", None)
        self.f_city = QComboBox();
        self.f_city.addItem("Tüm Şehirler", None)
        self.f_venue = QComboBox();
        self.f_venue.addItem("Tüm Sahneler", None)
        self.f_actor = QComboBox();
        self.f_actor.addItem("Tüm Oyuncular", None)
        self.f_tour = QComboBox();
        self.f_tour.addItem("Tüm Ekipler", None)
        for cb in [self.f_play, self.f_city, self.f_venue, self.f_actor, self.f_tour]:
            cb.currentIndexChanged.connect(self.refresh_calendar);
            f_layout.addWidget(cb)
        layout.addWidget(f_frame)

        # HEADER
        h_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<");
        self.btn_prev.clicked.connect(self.prev_month);
        self.btn_prev.setFixedWidth(50)
        self.lbl_month = QLabel();
        self.lbl_month.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;");
        self.lbl_month.setAlignment(Qt.AlignCenter)
        self.btn_next = QPushButton(">");
        self.btn_next.clicked.connect(self.next_month);
        self.btn_next.setFixedWidth(50)
        h_layout.addWidget(self.btn_prev);
        h_layout.addWidget(self.lbl_month);
        h_layout.addWidget(self.btn_next)
        layout.addLayout(h_layout)

        # PDF
        self.btn_pdf = QPushButton("📄 Programı PDF İndir");
        self.btn_pdf.setFixedHeight(35);
        self.btn_pdf.clicked.connect(self.export_to_pdf)
        self.btn_pdf.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; border-radius: 5px;")
        layout.addWidget(self.btn_pdf)
        self.shortcut_pdf = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut_pdf.activated.connect(self.export_to_pdf)
        self.grid = QTableWidget(6, 7)
        self.grid.setHorizontalHeaderLabels(["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"])
        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch);
        self.grid.verticalHeader().setVisible(False)
        self.grid.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.grid.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.grid)
        self.load_filter_data();
        self.refresh_calendar()

    def load_filter_data(self):
        for p in self.controller.get_active_plays(): self.f_play.addItem(p['oyun_adi'], p['id'])
        for c in self.controller.get_distinct_cities(): self.f_city.addItem(c['sehir'], c['sehir'])
        for v in VenueController.get_all_venues(): self.f_venue.addItem(v['sahne_adi'], v['id'])
        for ps in PersonelController.get_all_personel(): self.f_actor.addItem(ps['ad_soyad'], ps['id'])
        for ps in PersonelController.get_all_personel(): self.f_actor.addItem(ps['ad_soyad'], ps['id'])
        for t in self.tour_controller.get_all_teams(): self.f_tour.addItem(t['ekip_adi'], t['id'])

    def refresh_calendar(self):
        try:
            year, month = self.current_date.year(), self.current_date.month()
            tr_m = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 7: "TEMMUZ", 8: "AĞUSTOS",
                    9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
            self.lbl_month.setText(f"{tr_m[month]} {year}")

            f_day = QDate(year, month, 1)
            start_idx, days_cnt = f_day.dayOfWeek() - 1, f_day.daysInMonth()
            self.grid.clearContents()

            raw_events = self.controller.get_events_for_month(year, month)
            evs_by_date = {}

            # Filtreleri alırken güvenli data çekimi
            f_play_id = self.f_play.currentData()
            f_city_val = self.f_city.currentData()
            f_venue_id = self.f_venue.currentData()
            f_tour_id = self.f_tour.currentData()
            f_actor_id = self.f_actor.currentData()

            for ev in raw_events:
                ev_dict = dict(ev)
                keep = True

                # 1. Oyun Filtresi (Eğer "Tümü" değilse kontrol et)
                if f_play_id is not None:
                    try:
                        if ev_dict.get('oyun_id') is None or int(ev_dict['oyun_id']) != int(f_play_id):
                            keep = False
                    except:
                        keep = False

                # 2. Şehir Filtresi
                if keep and f_city_val is not None:
                    if str(ev_dict.get('sehir')) != str(f_city_val):
                        keep = False

                # 3. Sahne Filtresi (Crash Fix)
                if keep and f_venue_id is not None:
                    try:
                        if ev_dict.get('sahne_id') is None or int(ev_dict['sahne_id']) != int(f_venue_id):
                            keep = False
                    except:
                        keep = False

                # 4. Turne Ekibi Filtresi (Kritik Alan)
                if keep and f_tour_id is not None:
                    try:
                        db_t_id = ev_dict.get('turne_ekibi_id')
                        # Eğer DB boşsa veya ID'ler tutmuyorsa ele
                        if db_t_id is None or int(db_t_id) != int(f_tour_id):
                            keep = False
                    except:
                        keep = False

                # 5. Oyuncu Filtresi
                if keep and f_actor_id is not None:
                    c_ids = self.controller.get_event_cast_ids(ev_dict['id'], "Oyuncu")
                    if f_actor_id not in c_ids:
                        keep = False

                # Kaydet
                if keep:
                    d_s = ev_dict['tarih']
                    if d_s not in evs_by_date: evs_by_date[d_s] = []
                    evs_by_date[d_s].append(ev_dict)

            self._draw_calendar_grid(start_idx, days_cnt, year, month, evs_by_date)

        except Exception as e:
            print(f"Takvim Yenileme Hatası: {e}")
    def _draw_calendar_grid(self, start_idx, days_cnt, year, month, evs_by_date):
        day_cnt = 1
        for r in range(6):
            for c in range(7):
                if (r == 0 and c < start_idx) or day_cnt > days_cnt: continue
                curr = QDate(year, month, day_cnt)
                dt_s = curr.toString("yyyy-MM-dd")

                cell = QWidget();
                cell_l = QVBoxLayout(cell);
                cell_l.setContentsMargins(2, 2, 2, 2);
                cell_l.setSpacing(5)
                top = QHBoxLayout();
                btn = QPushButton("+");
                btn.setFixedSize(18, 18)
                btn.clicked.connect(lambda _, d=curr: self.open_edit_dialog(d, None))
                lbl = QLabel(str(day_cnt));
                lbl.setStyleSheet("color:#FFD700;" if curr == QDate.currentDate() else "color:#777")
                top.addWidget(btn);
                top.addStretch();
                top.addWidget(lbl);
                cell_l.addLayout(top)

                scroll = QScrollArea();
                scroll.setWidgetResizable(True);
                scroll.setFrameShape(QFrame.NoFrame)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                cont = QWidget();
                cont_l = QVBoxLayout(cont);
                cont_l.setContentsMargins(0, 0, 0, 0);
                cont_l.setSpacing(4)

                if dt_s in evs_by_date:
                    for ev in evs_by_date[dt_s]: self.create_event_button(cont_l, ev, curr)

                cont_l.addStretch();
                scroll.setWidget(cont);
                cell_l.addWidget(scroll);
                self.grid.setCellWidget(r, c, cell)
                item = QTableWidgetItem();
                item.setData(Qt.UserRole, curr);
                self.grid.setItem(r, c, item);
                day_cnt += 1

    def create_event_button(self, layout, ev, date_obj):
        # Renk paleti (Oyun ID'sine göre değişir)
        clrs = ["#e74c3c", "#3498db", "#9b59b6", "#2ecc71", "#f1c40f", "#e67e22"]
        c = clrs[ev['oyun_id'] % len(clrs)]

        # Buton metni: Saat ve Oyun Adı
        btn = QPushButton(f"{ev['baslangic_saati']} | {ev['oyun_adi']}")
        btn.setMinimumHeight(25)
        btn.setCursor(Qt.PointingHandCursor)

        # --- TOOLTIP GERİ GETİRİLDİ ---
        # Mouse ile üzerine gelince görünecek zengin metin
        tooltip_text = (f"<b>{ev['oyun_adi']}</b><br>"
                        f"⏰ Saat: {ev['baslangic_saati']}<br>"
                        f"📍 Sahne: {ev.get('sahne_adi', '-')}<br>"
                        f"🎭 Oyuncular: {ev.get('oyuncu_listesi', '-')}")
        btn.setToolTip(tooltip_text)
        # ------------------------------

        # Hover Efekti ve Görsel Stil
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {c}; 
                color: white; 
                border-radius: 6px; 
                font-size: 13px; 
                font-weight: bold; 
                text-align: left; 
                padding: 5px 10px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            QPushButton:hover {{ 
                background-color: white; 
                color: {c}; 
                border: 1px solid {c};
            }}
        """)

        # Tıklama olayı
        btn.clicked.connect(lambda: self.open_edit_dialog(date_obj, ev['id']))
        layout.addWidget(btn)
    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1); self.refresh_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1); self.refresh_calendar()

    def on_cell_double_clicked(self, r, c):
        i = self.grid.item(r, c)
        if i: self.open_edit_dialog(i.data(Qt.UserRole), None)

    def open_edit_dialog(self, d, eid):
        if EventDialog(self, d, eid).exec_(): self.refresh_calendar()

    def export_to_pdf(self):
        import os
        from itertools import groupby

        # 1. Verileri Hazırla
        year = self.current_date.year()
        month = self.current_date.month()

        tr_months = {
            1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
        }
        tr_days = {
            1: "PAZARTESİ", 2: "SALI", 3: "ÇARŞAMBA", 4: "PERŞEMBE", 5: "CUMA", 6: "CUMARTESİ", 7: "PAZAR"
        }

        month_name = f"{tr_months[month]} {year}"

        # --- YENİ MANTIK: FİLTRELERİ UYGULA ---
        all_events = self.controller.get_events_for_month(year, month)
        filtered_events = []

        f_play_id = self.f_play.currentData()
        f_city_val = self.f_city.currentData()
        f_venue_id = self.f_venue.currentData()
        f_tour_id = self.f_tour.currentData()
        f_actor_id = self.f_actor.currentData()

        for ev in all_events:
            ev_dict = dict(ev)
            keep = True

            if f_play_id is not None and int(ev_dict.get('oyun_id')) != int(f_play_id): keep = False
            if keep and f_city_val is not None and ev_dict.get('sehir') != f_city_val: keep = False
            if keep and f_venue_id is not None and int(ev_dict.get('sahne_id')) != int(f_venue_id): keep = False
            if keep and f_tour_id is not None:
                db_t = ev_dict.get('turne_ekibi_id')
                if db_t is None or int(db_t) != int(f_tour_id): keep = False
            if keep and f_actor_id is not None:
                if f_actor_id not in self.controller.get_event_cast_ids(ev_dict['id'], "Oyuncu"): keep = False

            if keep:
                filtered_events.append(ev_dict)

        if not filtered_events:
            QMessageBox.warning(self, "Uyarı", "Filtreye uygun veya bu ay için kayıtlı etkinlik bulunamadı.")
            return

        # Sıralama (Eski koddaki gibi)
        filtered_events.sort(key=lambda x: (x['tarih'], x['baslangic_saati']))

        # 2. Dosya Kaydetme
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        default_filename = os.path.join(desktop_path, f"Program_{month_name.replace(' ', '_')}.pdf")

        filename, _ = QFileDialog.getSaveFileName(
            self, "Programı Kaydet", default_filename, "PDF Dosyası (*.pdf)"
        )

        if not filename:
            return

        # 3. HTML Tasarımı (TAMAMEN ESKİ GÖRSEL TASARIM)
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 10px; color: #000; }}
                h1 {{ text-align: center; margin-bottom: 20px; font-size: 18px; text-transform: uppercase; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; page-break-inside: auto; }}
                tr {{ page-break-inside: avoid; }}
                td, th {{ border: 1px solid #000; padding: 0px; color: #000; vertical-align: middle; }}
                .nobreak {{ page-break-inside: avoid; display: block; padding: 6px; width: 100%; }}
                .col-header {{ background-color: #ddd; font-weight: bold; padding: 6px; vertical-align: middle; }}
                .date-header {{ background-color: #000; color: #fff; font-size: 12px; font-weight: bold; text-align: left; padding: 8px; border: 1px solid #000; vertical-align: middle; }}
                .game-title {{ font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <h1>🎭 {month_name} OYUN PROGRAMI</h1>
        """

        for date_str, day_events_iter in groupby(filtered_events, key=lambda x: x['tarih']):
            day_events = list(day_events_iter)
            date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
            formatted_date = date_obj.toString("dd.MM.yyyy")
            day_name = tr_days.get(date_obj.dayOfWeek(), "")

            html_content += f"""
            <table border="1" cellspacing="0" cellpadding="0">
                <thead>
                    <tr>
                        <th colspan="4" class="date-header">{formatted_date} - {day_name}</th>
                    </tr>
                    <tr class="col-header">
                        <th width="10%">SAAT</th>
                        <th width="30%">ŞEHİR / SAHNE</th>
                        <th width="35%">OYUN ADI</th>
                        <th width="25%">KADRO</th>
                    </tr>
                </thead>
                <tbody>
            """

            for ev in day_events:
                oyuncular = ev.get('oyuncu_listesi', '-')
                html_content += f"""
                <tr>
                    <td><div class="nobreak" style="font-weight:bold; text-align:center;">{ev['baslangic_saati']}</div></td>
                    <td><div class="nobreak" style="text-align:left; font-size:10px;"><b>{ev['sehir']}</b> / {ev['sahne_adi']}</div></td>
                    <td><div class="nobreak game-title" style="text-align:center;">{ev['oyun_adi']}</div></td>
                    <td><div class="nobreak" style="text-align:left; font-size:9px;">{oyuncular}</div></td>
                </tr>
                """
            html_content += "</tbody></table>"

        html_content += "</body></html>"

        # 4. Yazdırma İşlemi
        document = QTextDocument()
        document.setHtml(html_content)

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)

        document.print_(printer)

        try:
            os.startfile(filename)
        except Exception:
            QMessageBox.information(self, "Başarılı", f"PDF kaydedildi:\n{filename}")