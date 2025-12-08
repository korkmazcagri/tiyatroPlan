from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QLineEdit, QComboBox, QDoubleSpinBox,
                             QTextEdit, QCheckBox, QTabWidget, QFormLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDateEdit, QFrame, QAbstractItemView, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from app.controllers.personel_controller import PersonelController


class ActorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PersonelController()
        self.selected_personel_id = None
        self.day_combos = {}  # Haftalık rutin kutuları
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- SOL TARAF (LİSTE VE ARAMA) ---
        left_layout = QVBoxLayout()

        self.lbl_list_title = QLabel("PERSONEL LİSTESİ")
        self.lbl_list_title.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 16px;")
        left_layout.addWidget(self.lbl_list_title)

        # ARAMA
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Personel ara...")
        self.search_input.textChanged.connect(self.refresh_list)
        left_layout.addWidget(self.search_input)

        self.personel_list = QListWidget()
        self.personel_list.itemClicked.connect(self.load_personel_details)
        left_layout.addWidget(self.personel_list)

        self.btn_new = QPushButton("+ Yeni Personel Ekle")
        self.btn_new.setProperty("class", "action_btn")
        self.btn_new.clicked.connect(self.prepare_new_personel)
        left_layout.addWidget(self.btn_new)

        main_layout.addLayout(left_layout, 2)

        # --- SAĞ TARAF (TABLAR) ---
        right_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_profile_tab(), "Genel")
        self.tabs.addTab(self.create_finance_tab(), "Finans")
        self.tabs.addTab(self.create_repertoire_tab(), "Repetuvar")
        self.tabs.addTab(self.create_history_tab(), "Oyunları")
        self.tabs.addTab(self.create_availability_tab(), "Müsaitlik")  # YENİ SEKME

        right_layout.addWidget(self.tabs)
        main_layout.addLayout(right_layout, 5)

        # Başlangıç
        self.refresh_list()
        self.load_games_combo()

    # ----------------------------------------------------------------------
    # 1. SEKME: PROFİL
    # ----------------------------------------------------------------------
    def create_profile_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.input_ad = QLineEdit()
        self.input_tel = QLineEdit()

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Oyuncu", "Teknik"])

        self.combo_odeme = QComboBox()
        self.combo_odeme.addItems(["Oyun Başı", "Aylık Maaş", "Haftalık Maaş"])

        self.spin_ucret = QDoubleSpinBox()
        self.spin_ucret.setMaximum(100000)
        self.spin_ucret.setSuffix(" TL")

        self.check_turne = QCheckBox("Turne Engeli Var")
        self.input_notlar = QTextEdit()
        self.input_notlar.setMaximumHeight(80)

        layout.addRow("Ad Soyad:", self.input_ad)
        layout.addRow("Telefon:", self.input_tel)
        layout.addRow("Rol / Görev:", self.combo_rol)
        layout.addRow("Ödeme Tipi:", self.combo_odeme)
        layout.addRow("Standart Ücret:", self.spin_ucret)
        layout.addRow("Kısıtlamalar:", self.check_turne)
        layout.addRow("Notlar:", self.input_notlar)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Bilgileri Kaydet")
        self.btn_save.setProperty("class", "action_btn")
        self.btn_save.clicked.connect(self.save_personel)

        self.btn_delete = QPushButton("Personeli Sil")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
        self.btn_delete.clicked.connect(self.delete_personel)
        self.btn_delete.hide()

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        layout.addRow("", btn_layout)

        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # 2. SEKME: FİNANS
    # ----------------------------------------------------------------------
    def create_finance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_balance = QLabel("Bakiye: 0.00 TL")
        layout.addWidget(self.lbl_balance)

        self.table_finance = QTableWidget()
        self.table_finance.setColumnCount(5)
        self.table_finance.setHorizontalHeaderLabels(["Tarih", "İşlem", "Tutar", "Açıklama", "Sil"])
        # -----------------------------------------

        self.table_finance.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Sil butonu sütunu çok geniş olmasın, daraltalım (4. indeks)
        self.table_finance.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table_finance.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_finance.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table_finance)
        lbl_add = QLabel("Yeni İşlem Ekle")
        lbl_add.setObjectName("section_title")
        layout.addWidget(lbl_add)

        action_layout = QHBoxLayout()
        self.date_input = QDateEdit(QDate.currentDate())
        self.combo_action = QComboBox()
        self.combo_action.addItems(["Ödeme (Para Çıkışı)", "Hakediş (Borçlanma)"])
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setMaximum(100000)
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Açıklama...")

        btn_add = QPushButton("Ekle")
        btn_add.setProperty("class", "action_btn")
        btn_add.clicked.connect(self.add_finance_transaction)

        action_layout.addWidget(self.date_input)
        action_layout.addWidget(self.combo_action)
        action_layout.addWidget(self.spin_amount)
        action_layout.addWidget(self.input_desc)
        action_layout.addWidget(btn_add)

        layout.addLayout(action_layout)
        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # 3. SEKME: OYUNLAR (REPERTUVAR)
    # ----------------------------------------------------------------------
    def create_repertoire_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Oyuncunun Repertuvarı"))

        self.table_repertoire = QTableWidget()
        self.table_repertoire.setColumnCount(3)
        self.table_repertoire.setHorizontalHeaderLabels(["Oyun Adı", "Durum", "İşlem"])
        self.table_repertoire.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_repertoire.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_repertoire)

        add_group = QFrame()
        add_group.setObjectName("add_game_box")
        add_layout = QVBoxLayout(add_group)

        add_layout.addWidget(QLabel("Repertuvara Yeni Oyun Ekle"))
        inputs_layout = QHBoxLayout()

        self.combo_all_games = QComboBox()
        self.btn_add_game = QPushButton("Oyunu Ekle")
        self.btn_add_game.setProperty("class", "action_btn")
        self.btn_add_game.clicked.connect(self.add_game_to_repertoire)

        inputs_layout.addWidget(self.combo_all_games)
        inputs_layout.addWidget(self.btn_add_game)
        add_layout.addLayout(inputs_layout)

        layout.addWidget(add_group)
        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # 4. SEKME: TEMSİL GEÇMİŞİ
    # ----------------------------------------------------------------------
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Personelin Görev Aldığı Etkinlikler"))

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["Tarih", "Saat", "Oyun", "Sahne", "Görev"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_history)

        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # 5. SEKME: MÜSAİTLİK (AVAILABILITY) - YENİ
    # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # 5. SEKME: MÜSAİTLİK (AVAILABILITY)
        # ----------------------------------------------------------------------
    def create_availability_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. HAFTALIK RUTİN
        lbl_rutin = QLabel("📅 HAFTALIK STANDART RUTİN")
        lbl_rutin.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_rutin)

        # Grid Yapısı (Pazartesi, Salı...)
        grid_days = QGridLayout()
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        self.day_combos = {}  # Comboboxları sakla

        for i, day_name in enumerate(days):
            lbl = QLabel(day_name)
            lbl.setStyleSheet("color: #aaa;")

            combo = QComboBox()
            combo.addItems(["Müsait", "Müsait Değil", "Sahnede"])
            # Renkler
            combo.setItemData(0, QColor("#2ecc71"), Qt.ForegroundRole)  # Yeşil
            combo.setItemData(1, QColor("#e74c3c"), Qt.ForegroundRole)  # Kırmızı
            combo.setItemData(2, QColor("#f39c12"), Qt.ForegroundRole)  # Turuncu

            # Seçim değişince rengi güncelle
            combo.currentIndexChanged.connect(lambda idx, c=combo: self.update_combo_style(c))
            self.update_combo_style(combo)

            self.day_combos[i] = combo

            # Grid'e ekle (2 sütunlu düzen)
            row = i // 2
            col = (i % 2) * 2
            grid_days.addWidget(lbl, row, col)
            grid_days.addWidget(combo, row, col + 1)

        layout.addLayout(grid_days)

        btn_save_rutin = QPushButton("Rutinleri Kaydet")
        btn_save_rutin.setProperty("class", "action_btn")
        btn_save_rutin.clicked.connect(self.save_weekly_routine)
        layout.addWidget(btn_save_rutin)

        layout.addSpacing(20)

        # 2. İSTİSNA TARİHLER
        lbl_istisna = QLabel("⚠️ İSTİSNA TARİHLER (Kişi Müsait Değil)")
        lbl_istisna.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_istisna)

        # Ekleme Alanı
        hbox_exc = QHBoxLayout()
        self.date_exc = QDateEdit(QDate.currentDate())
        self.date_exc.setCalendarPopup(True)
        self.date_exc.calendarWidget().setFirstDayOfWeek(Qt.Monday)
        self.date_exc.setDisplayFormat("dd.MM.yyyy")

        # --- [DEĞİŞİKLİK BURADA] ---
        # Sadece takvimden seçilsin, klavyeyle yazılamasın
        self.date_exc.lineEdit().setReadOnly(True)
        # ---------------------------

        self.input_exc_desc = QLineEdit()
        self.input_exc_desc.setPlaceholderText("Sebep (Örn: Sınav, Düğün...)")
        btn_add_exc = QPushButton("Ekle")
        btn_add_exc.clicked.connect(self.add_exception)

        hbox_exc.addWidget(self.date_exc)
        hbox_exc.addWidget(self.input_exc_desc)
        hbox_exc.addWidget(btn_add_exc)
        layout.addLayout(hbox_exc)

        # Liste
        self.table_exc = QTableWidget()
        self.table_exc.setColumnCount(3)
        self.table_exc.setHorizontalHeaderLabels(["Tarih", "Sebep", "Sil"])
        self.table_exc.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_exc.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_exc)

        tab.setLayout(layout)
        return tab


    def update_combo_style(self, combo):
        txt = combo.currentText()
        if txt == "Müsait":
            color = "#2ecc71"
        elif txt == "Müsait Değil":
            color = "#e74c3c"
        else:
            color = "#f39c12"
        combo.setStyleSheet(f"QComboBox {{ color: {color}; border: 1px solid #555; background: #222; }}")

    def refresh_list(self):
        self.personel_list.clear()
        search_text = self.search_input.text()
        personels = self.controller.search_personel(search_text)
        for p in personels:
            self.personel_list.addItem(f"{p['id']} - {p['ad_soyad']}")

    def load_games_combo(self, excluded_ids=None):
        if excluded_ids is None: excluded_ids = []
        self.combo_all_games.clear()
        games = self.controller.get_all_games()
        for g in games:
            if g['id'] not in excluded_ids:
                self.combo_all_games.addItem(g['oyun_adi'], g['id'])

    def prepare_new_personel(self):
        self.selected_personel_id = None
        self.input_ad.clear()
        self.input_tel.clear()
        self.combo_rol.setCurrentIndex(0)
        self.spin_ucret.setValue(0)
        self.input_notlar.clear()
        self.check_turne.setChecked(False)
        self.btn_delete.hide()

        self.tabs.setCurrentIndex(0)
        self.lbl_list_title.setText("YENİ PERSONEL EKLENİYOR")

        # Tabloları temizle
        self.table_finance.setRowCount(0)
        self.table_repertoire.setRowCount(0)
        self.table_history.setRowCount(0)
        self.table_exc.setRowCount(0)

        # Rutinleri sıfırla
        for combo in self.day_combos.values():
            combo.setCurrentIndex(0)

        self.lbl_balance.setText("Bakiye: 0.00 TL")
        self.load_games_combo()

    def load_personel_details(self, item):
        try:
            p_id = int(item.text().split(" - ")[0])
        except:
            return

        self.selected_personel_id = p_id
        data = self.controller.get_personel_detail(p_id)
        if data:
            self.input_ad.setText(data['ad_soyad'])
            self.input_tel.setText(data['telefon'])
            self.combo_rol.setCurrentText(data['rol_tipi'])
            self.combo_odeme.setCurrentText(data['odeme_tipi'])
            self.spin_ucret.setValue(data['standart_ucret'])
            self.check_turne.setChecked(bool(data['turne_engeli']))
            self.input_notlar.setText(data['notlar'])

            self.btn_delete.show()
            self.lbl_list_title.setText(f"DÜZENLENİYOR: {data['ad_soyad']}")

            # Verileri Yükle
            self.load_finance_history(p_id)
            self.load_repertoire_history(p_id)
            self.load_history_data(p_id)
            self.load_availability_data(p_id)  # [YENİ]

    # --- MÜSAİTLİK VERİLERİNİ YÜKLE ---
    def load_availability_data(self, p_id):
        # 1. Rutin
        routine = self.controller.get_weekly_routine(p_id)
        for day_idx, combo in self.day_combos.items():
            combo.blockSignals(True)
            if day_idx in routine:
                combo.setCurrentText(routine[day_idx])
            else:
                combo.setCurrentText("Müsait")
            self.update_combo_style(combo)
            combo.blockSignals(False)

        # 2. İstisnalar
        self.load_exceptions(p_id)

    def load_exceptions(self, p_id):
        self.table_exc.setRowCount(0)
        excs = self.controller.get_exceptions(p_id)
        for row, data in enumerate(excs):
            self.table_exc.insertRow(row)
            self.table_exc.setItem(row, 0, QTableWidgetItem(data['tarih']))
            self.table_exc.setItem(row, 1, QTableWidgetItem(data['aciklama']))

            btn_del = QPushButton("Sil")
            btn_del.setStyleSheet("background-color: #c0392b; color: white;")
            btn_del.clicked.connect(lambda _, e_id=data['id']: self.delete_exception(e_id))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(btn_del)
            self.table_exc.setCellWidget(row, 2, container)

    def save_weekly_routine(self):
        if not self.selected_personel_id: return
        weekly_data = {}
        for day_idx, combo in self.day_combos.items():
            weekly_data[day_idx] = combo.currentText()

        self.controller.save_weekly_routine(self.selected_personel_id, weekly_data)
        QMessageBox.information(self, "Başarılı", "Rutin kaydedildi.")

    def add_exception(self):
        if not self.selected_personel_id: return

        # 1. Değişkenleri Al
        date_str = self.date_exc.date().toString("yyyy-MM-dd")
        desc = self.input_exc_desc.text()

        if not desc:
            QMessageBox.warning(self, "Hata", "Lütfen bir sebep yazın (Örn: Raporlu, İzinli).")
            return

        # --- [YENİ KONTROL] O GÜN OYUNU VAR MI? ---
        has_event, event_name = self.controller.check_if_person_has_event(self.selected_personel_id, date_str)

        if has_event:
            QMessageBox.critical(
                self, "İşlem Engellendi",
                f"Bu personelin {date_str} tarihinde\n"
                f"'{event_name}' oyununda görevi görünüyor!\n\n"
                "Önce takvimden o görevi kaldırmadan istisna ekleyemezsiniz."
            )
            return
        # ------------------------------------------

        # 2. Sorun Yoksa Kaydet
        self.controller.add_exception(
            self.selected_personel_id,
            date_str,
            desc
        )
        self.input_exc_desc.clear()
        self.load_exceptions(self.selected_personel_id)
        QMessageBox.information(self, "Başarılı", "İstisna tarihi eklendi.")

    def delete_exception(self, exc_id):
        reply = QMessageBox.question(self, 'Sil', 'Silmek istiyor musun?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_exception(exc_id)
            self.load_exceptions(self.selected_personel_id)

    # --- DİĞER KAYIT İŞLEMLERİ ---
    def save_personel(self):
        ad = self.input_ad.text()
        if not ad: return
        self.controller.save_personel(
            ad, self.input_tel.text(), self.combo_rol.currentText(),
            self.combo_odeme.currentText(), self.spin_ucret.value(),
            1 if self.check_turne.isChecked() else 0, self.input_notlar.toPlainText(),
            self.selected_personel_id
        )
        QMessageBox.information(self, "Başarılı", "Kaydedildi.")
        self.refresh_list()
        if not self.selected_personel_id: self.prepare_new_personel()

    def delete_personel(self):
        if self.selected_personel_id:
            reply = QMessageBox.question(self, 'Sil', 'Emin misin?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.controller.delete_personel(self.selected_personel_id)
                self.refresh_list()
                self.prepare_new_personel()

    def load_finance_history(self, p_id):
        self.table_finance.setRowCount(0)
        history = self.controller.get_finance_history(p_id)

        for row, data in enumerate(history):
            self.table_finance.insertRow(row)
            self.table_finance.setItem(row, 0, QTableWidgetItem(data['tarih']))
            self.table_finance.setItem(row, 1, QTableWidgetItem(data['islem_turu']))

            amt = QTableWidgetItem(f"{data['miktar']:.2f} TL")
            # Ödeme ise Kırmızı, Borç ise Yeşil (veya tam tersi senin tercihine göre)
            amt.setForeground(QColor("red") if "Ödeme" in data['islem_turu'] else QColor("green"))
            self.table_finance.setItem(row, 2, amt)

            self.table_finance.setItem(row, 3, QTableWidgetItem(data['aciklama']))

            # --- SİL BUTONU EKLEME ---
            btn_del = QPushButton("Sil")
            btn_del.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 3px;")
            # Tıklanınca o işlemin ID'sini gönder
            btn_del.clicked.connect(lambda _, tid=data['id']: self.delete_finance_item(tid))

            # Butonu ortalamak için widget içine koyuyoruz
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.addWidget(btn_del)
            self.table_finance.setCellWidget(row, 4, container)
            # -------------------------

        # Bakiyeyi Güncelle
        bak = self.controller.get_balance(p_id)

        # Bakiye Rengi
        renk = "#2ecc71" if bak >= 0 else "#e74c3c"  # Pozitifse Yeşil, Negatifse Kırmızı

        self.lbl_balance.setText(f"Bakiye: {bak:.2f} TL")
        self.lbl_balance.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {renk};")

    def add_finance_transaction(self):
        if not self.selected_personel_id: return
        self.controller.add_transaction(
            self.selected_personel_id, self.date_input.date().toString("yyyy-MM-dd"),
            self.combo_action.currentText(), self.spin_amount.value(), self.input_desc.text()
        )
        self.input_desc.clear()
        self.spin_amount.setValue(0)
        self.load_finance_history(self.selected_personel_id)

    def delete_finance_item(self, trans_id):
        """Seçilen finans işlemini siler ve listeyi yeniler."""
        reply = QMessageBox.question(
            self,
            "İşlemi Sil",
            "Bu finansal işlemi silmek istiyor musunuz?\nBakiye yeniden hesaplanacaktır.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.controller.delete_transaction(trans_id)

            # Listeyi ve Bakiyeyi Yenile
            if self.selected_personel_id:
                self.load_finance_history(self.selected_personel_id)

            QMessageBox.information(self, "Başarılı", "İşlem silindi ve bakiye güncellendi.")
    def load_repertoire_history(self, p_id):
        self.table_repertoire.setRowCount(0)
        rep = self.controller.get_personel_repertoire(p_id)
        excludes = []
        for row, data in enumerate(rep):
            excludes.append(data['oyun_id'])
            self.table_repertoire.insertRow(row)
            self.table_repertoire.setItem(row, 0, QTableWidgetItem(data['oyun_adi']))

            btn = QPushButton(data['durum'])
            color = "#27ae60" if data['durum'] == 'Hazır' else "#f1c40f"
            btn.setStyleSheet(
                f"background-color: {color}; color: {'white' if color == '#27ae60' else 'black'}; border-radius: 4px; font-weight: bold;")
            btn.clicked.connect(lambda _, r=data['id'], s=data['durum']: self.toggle_game_status(r, s))
            self.table_repertoire.setCellWidget(row, 1, btn)

            del_btn = QPushButton("Kaldır")
            del_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 4px;")
            del_btn.clicked.connect(lambda _, r=data['id']: self.remove_game(r))

            cont = QWidget()
            lo = QHBoxLayout(cont)
            lo.setContentsMargins(0, 0, 0, 0)
            lo.addWidget(del_btn)
            self.table_repertoire.setCellWidget(row, 2, cont)
        self.load_games_combo(excludes)

    def add_game_to_repertoire(self):
        if not self.selected_personel_id: return
        oid = self.combo_all_games.currentData()
        if not oid: return
        self.controller.add_game_to_personel(self.selected_personel_id, oid, "Çalışıyor")
        self.load_repertoire_history(self.selected_personel_id)

    def toggle_game_status(self, r_id, curr):
        self.controller.update_repertoire_status(r_id, "Çalışıyor" if curr == "Hazır" else "Hazır")
        self.load_repertoire_history(self.selected_personel_id)

    def remove_game(self, r_id):
        if QMessageBox.question(self, 'Sil', 'Emin misin?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.controller.remove_game_from_personel(r_id)
            self.load_repertoire_history(self.selected_personel_id)

    def load_history_data(self, p_id):
        self.table_history.setRowCount(0)
        hist = self.controller.get_person_event_history(p_id)
        today = QDate.currentDate().toString("yyyy-MM-dd")
        for row, data in enumerate(hist):
            self.table_history.insertRow(row)
            item_date = QTableWidgetItem(data['tarih'])
            self.table_history.setItem(row, 0, item_date)
            self.table_history.setItem(row, 1, QTableWidgetItem(data['baslangic_saati']))
            self.table_history.setItem(row, 2, QTableWidgetItem(data['oyun_adi']))
            self.table_history.setItem(row, 3, QTableWidgetItem(data['sahne_adi']))
            self.table_history.setItem(row, 4, QTableWidgetItem(data['gorev']))

            if data['tarih'] < today:
                for c in range(5): self.table_history.item(row, c).setForeground(QColor("gray"))
            else:
                item_date.setForeground(QColor("#2ecc71"))