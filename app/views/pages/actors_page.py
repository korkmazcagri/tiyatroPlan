from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QLineEdit, QComboBox, QDoubleSpinBox,
                             QTextEdit, QCheckBox, QTabWidget, QFormLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDateEdit, QFrame, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from app.controllers.personel_controller import PersonelController


class ActorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PersonelController()
        self.selected_personel_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- SOL TARAF (LİSTE VE ARAMA) ---
        left_layout = QVBoxLayout()

        self.lbl_list_title = QLabel("PERSONEL LİSTESİ")
        self.lbl_list_title.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 16px;")
        left_layout.addWidget(self.lbl_list_title)

        # ARAMA KUTUSU (YENİ)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Personel ara...")
        self.search_input.textChanged.connect(self.refresh_list)  # Yazıldıkça filtrele
        left_layout.addWidget(self.search_input)

        self.personel_list = QListWidget()
        self.personel_list.itemClicked.connect(self.load_personel_details)
        left_layout.addWidget(self.personel_list)

        self.btn_new = QPushButton("+ Yeni Personel Ekle")
        self.btn_new.setProperty("class", "action_btn")
        self.btn_new.clicked.connect(self.prepare_new_personel)
        left_layout.addWidget(self.btn_new)

        main_layout.addLayout(left_layout, 2)  # %20 Genişlik

        # --- SAĞ TARAF (DETAYLAR & TABLAR) ---
        right_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_profile_tab(), "Genel")
        self.tabs.addTab(self.create_finance_tab(), "Finans")
        self.tabs.addTab(self.create_repertoire_tab(), "Oyunlar")

        right_layout.addWidget(self.tabs)
        main_layout.addLayout(right_layout, 5)  # %50 Genişlik

        # İlk açılışta listeyi doldur
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

        self.check_turne = QCheckBox("Turne Engeli Var (Sadece İstanbul)")
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
        self.btn_delete.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px 15px; border: none; border-radius: 4px; font-weight: bold;")
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
        self.lbl_balance.setStyleSheet("font-size: 20px; font-weight: bold; color: #2ecc71; margin-bottom: 15px;")
        layout.addWidget(self.lbl_balance)

        self.table_finance = QTableWidget()
        self.table_finance.setColumnCount(4)
        self.table_finance.setHorizontalHeaderLabels(["Tarih", "İşlem", "Tutar", "Açıklama"])
        self.table_finance.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table_finance.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_finance.setSelectionBehavior(QAbstractItemView.SelectRows)
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
        self.spin_amount.setPrefix("₺")
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Açıklama...")

        btn_add_finance = QPushButton("Ekle")
        btn_add_finance.setProperty("class", "action_btn")
        btn_add_finance.clicked.connect(self.add_finance_transaction)

        action_layout.addWidget(self.date_input)
        action_layout.addWidget(self.combo_action)
        action_layout.addWidget(self.spin_amount)
        action_layout.addWidget(self.input_desc)
        action_layout.addWidget(btn_add_finance)

        layout.addLayout(action_layout)
        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # 3. SEKME: OYUNLAR & REPERTUVAR
    # ----------------------------------------------------------------------
    def create_repertoire_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_list = QLabel("Oyuncunun Repertuvarı")
        lbl_list.setObjectName("section_title")
        layout.addWidget(lbl_list)

        self.table_repertoire = QTableWidget()
        self.table_repertoire.setColumnCount(3)
        self.table_repertoire.setHorizontalHeaderLabels(["Oyun Adı", "Durum", "İşlem"])
        self.table_repertoire.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_repertoire.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.table_repertoire.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_repertoire.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_repertoire.setSelectionMode(QAbstractItemView.NoSelection)

        layout.addWidget(self.table_repertoire)

        add_group = QFrame()
        add_group.setObjectName("add_game_box")

        add_group_layout = QVBoxLayout(add_group)

        lbl_add_title = QLabel("Repertuvara Yeni Oyun Ekle")
        lbl_add_title.setStyleSheet("color: #FFD700; font-weight: bold; margin-bottom: 10px;")
        add_group_layout.addWidget(lbl_add_title)

        inputs_layout = QHBoxLayout()

        self.combo_all_games = QComboBox()
        self.combo_all_games.setMinimumWidth(250)
        self.combo_all_games.setPlaceholderText("Bir Oyun Seçin...")

        self.btn_add_game = QPushButton("Oyunu Ekle")
        self.btn_add_game.setProperty("class", "action_btn")
        self.btn_add_game.clicked.connect(self.add_game_to_repertoire)

        inputs_layout.addWidget(QLabel("Oyun Seç:"))
        inputs_layout.addWidget(self.combo_all_games)
        inputs_layout.addStretch()
        inputs_layout.addWidget(self.btn_add_game)

        add_group_layout.addLayout(inputs_layout)
        layout.addWidget(add_group)

        tab.setLayout(layout)
        return tab

    # ----------------------------------------------------------------------
    # FONKSİYONLAR
    # ----------------------------------------------------------------------
    def refresh_list(self):
        """Personel listesini arama kutusuna göre filtreler."""
        self.personel_list.clear()

        # Arama metnini al
        search_text = self.search_input.text()

        # Controller'da ara
        personels = self.controller.search_personel(search_text)

        for p in personels:
            self.personel_list.addItem(f"{p['id']} - {p['ad_soyad']}")

    def load_games_combo(self, excluded_ids=None):
        if excluded_ids is None:
            excluded_ids = []

        self.combo_all_games.clear()
        games = self.controller.get_all_games()

        count = 0
        for g in games:
            if g['id'] not in excluded_ids:
                self.combo_all_games.addItem(g['oyun_adi'], g['id'])
                count += 1

        if count == 0:
            self.combo_all_games.setPlaceholderText("Tüm oyunlar eklendi!")
        else:
            self.combo_all_games.setPlaceholderText("Bir Oyun Seçin...")

    def prepare_new_personel(self):
        self.selected_personel_id = None
        self.input_ad.clear()
        self.input_tel.clear()
        self.combo_rol.setCurrentIndex(0)
        self.spin_ucret.setValue(0)
        self.input_notlar.clear()
        self.check_turne.setChecked(False)
        self.btn_delete.hide()

        self.tabs.setTabEnabled(2, True)  # Yeni eklerken kilidi aç
        self.tabs.setCurrentIndex(0)
        self.lbl_list_title.setText("YENİ PERSONEL EKLENİYOR")
        self.table_repertoire.setRowCount(0)
        self.load_games_combo()

    def load_personel_details(self, item):
        text = item.text()
        p_id = int(text.split(" - ")[0])
        self.selected_personel_id = p_id

        data = self.controller.get_personel_detail(p_id)
        if data:
            self.input_ad.setText(data['ad_soyad'])
            self.input_tel.setText(data['telefon'])
            self.combo_rol.setCurrentText(data['rol_tipi'])

            # Eğer Teknik ise 3. sekmeyi (Repertuvar) kilitle
            if data['rol_tipi'] == 'Teknik':
                self.tabs.setTabEnabled(2, False)
            else:
                self.tabs.setTabEnabled(2, True)

            self.combo_odeme.setCurrentText(data['odeme_tipi'])
            self.spin_ucret.setValue(data['standart_ucret'])
            self.check_turne.setChecked(bool(data['turne_engeli']))
            self.input_notlar.setText(data['notlar'])

            self.btn_delete.show()
            self.lbl_list_title.setText(f"DÜZENLENİYOR: {data['ad_soyad']}")

            self.load_finance_history(p_id)
            self.load_repertoire_history(p_id)

    def save_personel(self):
        ad = self.input_ad.text()
        if not ad:
            QMessageBox.warning(self, "Hata", "Ad Soyad boş olamaz!")
            return

        self.controller.save_personel(
            ad=ad,
            tel=self.input_tel.text(),
            rol=self.combo_rol.currentText(),
            odeme_tipi=self.combo_odeme.currentText(),
            ucret=self.spin_ucret.value(),
            turne_engeli=1 if self.check_turne.isChecked() else 0,
            notlar=self.input_notlar.toPlainText(),
            personel_id=self.selected_personel_id
        )

        QMessageBox.information(self, "Başarılı", "Personel kaydedildi.")
        self.refresh_list()
        if not self.selected_personel_id:
            self.prepare_new_personel()

    def delete_personel(self):
        if self.selected_personel_id:
            reply = QMessageBox.question(self, 'Sil', 'Bu personeli silmek istediğine emin misin?',
                                         QMessageBox.Yes | QMessageBox.No)
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

            amount_item = QTableWidgetItem(f"{data['miktar']:.2f} TL")

            if "Ödeme" in data['islem_turu']:
                amount_item.setForeground(Qt.red)
            else:
                amount_item.setForeground(Qt.green)

            self.table_finance.setItem(row, 2, amount_item)
            self.table_finance.setItem(row, 3, QTableWidgetItem(data['aciklama']))

        bakiye = self.controller.get_balance(p_id)
        self.lbl_balance.setText(f"Bakiye: {bakiye:.2f} TL")
        if bakiye > 0:
            self.lbl_balance.setStyleSheet("font-size: 20px; font-weight: bold; color: #2ecc71; margin-bottom: 15px;")
        else:
            self.lbl_balance.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c; margin-bottom: 15px;")

    def add_finance_transaction(self):
        if not self.selected_personel_id:
            QMessageBox.warning(self, "Hata", "Lütfen önce bir personel seçin.")
            return

        self.controller.add_transaction(
            personel_id=self.selected_personel_id,
            tarih=self.date_input.date().toString("yyyy-MM-dd"),
            islem_turu=self.combo_action.currentText(),
            miktar=self.spin_amount.value(),
            aciklama=self.input_desc.text()
        )
        self.input_desc.clear()
        self.spin_amount.setValue(0)
        self.load_finance_history(self.selected_personel_id)

    def load_repertoire_history(self, p_id):
        self.table_repertoire.setRowCount(0)
        rep_list = self.controller.get_personel_repertoire(p_id)

        assigned_game_ids = []

        for row, data in enumerate(rep_list):
            assigned_game_ids.append(data['oyun_id'])

            self.table_repertoire.insertRow(row)
            self.table_repertoire.setItem(row, 0, QTableWidgetItem(data['oyun_adi']))

            btn_status = QPushButton(data['durum'])
            btn_status.setCursor(Qt.PointingHandCursor)

            if data['durum'] == 'Hazır':
                btn_status.setStyleSheet("""
                    background-color: #27ae60; 
                    color: white; 
                    border: none; 
                    border-radius: 4px;
                    font-weight: bold;
                    padding: 4px;
                """)
            else:
                btn_status.setStyleSheet("""
                    background-color: #f1c40f; 
                    color: black; 
                    border: none; 
                    border-radius: 4px; 
                    font-weight: bold;
                    padding: 4px;
                """)

            btn_status.clicked.connect(
                lambda _, r_id=data['id'], curr=data['durum']: self.toggle_game_status(r_id, curr))
            self.table_repertoire.setCellWidget(row, 1, btn_status)

            btn_del = QPushButton("Kaldır")
            btn_del.setStyleSheet(
                "background-color: #e74c3c; color: white; padding: 4px 8px; border: none; border-radius: 3px; font-weight: bold;")
            btn_del.clicked.connect(lambda _, r_id=data['id']: self.remove_game(r_id))

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(btn_del)
            self.table_repertoire.setCellWidget(row, 2, container)

        self.load_games_combo(excluded_ids=assigned_game_ids)

    def add_game_to_repertoire(self):
        if not self.selected_personel_id:
            QMessageBox.warning(self, "Hata", "Lütfen önce bir personel seçin.")
            return

        oyun_id = self.combo_all_games.currentData()
        if not oyun_id:
            QMessageBox.warning(self, "Hata", "Lütfen listeden bir oyun seçin.")
            return

        durum = "Çalışıyor"

        self.controller.add_game_to_personel(self.selected_personel_id, oyun_id, durum)
        self.load_repertoire_history(self.selected_personel_id)

    def toggle_game_status(self, rep_id, current_status):
        new_status = "Çalışıyor" if current_status == "Hazır" else "Hazır"
        self.controller.update_repertoire_status(rep_id, new_status)
        self.load_repertoire_history(self.selected_personel_id)

    def remove_game(self, repertuvar_id):
        reply = QMessageBox.question(self, 'Kaldır', 'Bu oyunu oyuncudan kaldırmak istiyor musun?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.remove_game_from_personel(repertuvar_id)
            self.load_repertoire_history(self.selected_personel_id)