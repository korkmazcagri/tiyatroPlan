from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QLineEdit, QSpinBox, QTextEdit,
                             QFormLayout, QMessageBox, QComboBox, QFrame)
from app.controllers.venue_controller import VenueController


class VenuesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = VenueController()
        self.selected_venue_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- SOL TARAF (LİSTE VE FİLTRE) ---
        left_layout = QVBoxLayout()

        self.lbl_list_title = QLabel("SAHNE LİSTESİ")
        self.lbl_list_title.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 16px;")
        left_layout.addWidget(self.lbl_list_title)

        # --- FİLTRE ALANI (YENİ) ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #1a1a1a; border-radius: 5px; padding: 5px;")
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setSpacing(5)

        # Şehir Filtresi
        self.filter_city = QComboBox()
        self.filter_city.addItem("Tümü")  # Varsayılan
        self.filter_city.currentTextChanged.connect(self.refresh_list)  # Değişince listeyi yenile

        # İsim Arama
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Sahne adı ara...")
        self.filter_name.textChanged.connect(self.refresh_list)  # Yazdıkça listeyi yenile

        filter_layout.addWidget(QLabel("Şehir Filtrele:"))
        filter_layout.addWidget(self.filter_city)
        filter_layout.addWidget(QLabel("İsim Ara:"))
        filter_layout.addWidget(self.filter_name)

        left_layout.addWidget(filter_frame)
        # ---------------------------

        self.venue_list = QListWidget()
        self.venue_list.itemClicked.connect(self.load_venue_details)
        left_layout.addWidget(self.venue_list)

        self.btn_new = QPushButton("+ Yeni Sahne Ekle")
        self.btn_new.setProperty("class", "action_btn")
        self.btn_new.clicked.connect(self.prepare_new_venue)
        left_layout.addWidget(self.btn_new)

        main_layout.addLayout(left_layout, 2)  # %20 Genişlik

        # --- SAĞ TARAF (DETAY FORMU) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 0, 0, 0)

        # Başlık
        self.lbl_detail_title = QLabel("YENİ SAHNE")
        self.lbl_detail_title.setObjectName("page_title")
        right_layout.addWidget(self.lbl_detail_title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_ad = QLineEdit()
        self.input_ad.setPlaceholderText("Örn: Aydem Sahne")

        # --- ŞEHİR SEÇİMİ (81 İL) ---
        self.combo_sehir = QComboBox()
        iller = [
            "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan",
            "Artvin", "Aydın",
            "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa",
            "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan",
            "Erzurum", "Eskişehir",
            "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir",
            "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli",
            "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya",
            "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye",
            "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak",
            "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
        ]
        self.combo_sehir.addItems(iller)
        self.combo_sehir.setCurrentText("İstanbul")
        # ----------------------------

        self.spin_kapasite = QSpinBox()
        self.spin_kapasite.setRange(0, 10000)
        self.spin_kapasite.setValue(150)
        self.spin_kapasite.setSuffix(" Kişi")

        self.input_yetkili = QLineEdit()
        self.input_yetkili.setPlaceholderText("Oradaki kontak kişi")

        self.input_iletisim = QLineEdit()
        self.input_iletisim.setPlaceholderText("Telefon no vb.")

        self.input_adres = QTextEdit()
        self.input_adres.setPlaceholderText("Açık adres...")
        self.input_adres.setMaximumHeight(80)

        form_layout.addRow("Sahne Adı:", self.input_ad)
        form_layout.addRow("Şehir:", self.combo_sehir)
        form_layout.addRow("Kapasite:", self.spin_kapasite)
        form_layout.addRow("Yetkili Kişi:", self.input_yetkili)
        form_layout.addRow("İletişim:", self.input_iletisim)
        form_layout.addRow("Adres:", self.input_adres)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        # Butonlar
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Sahneyi Kaydet")
        self.btn_save.setProperty("class", "action_btn")
        self.btn_save.clicked.connect(self.save_venue)

        self.btn_delete = QPushButton("Sahneyi Sil")
        self.btn_delete.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_venue)
        self.btn_delete.hide()

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_widget, 4)  # %40 Genişlik
        main_layout.addStretch(1)

        # İlk Yüklemeler
        self.load_filter_cities()
        self.refresh_list()

    # --- FONKSİYONLAR ---

    def load_filter_cities(self):
        """Filtre için sadece veritabanında olan şehirleri yükler."""
        # Mevcut seçimi korumak için
        current = self.filter_city.currentText()

        self.filter_city.clear()
        self.filter_city.addItem("Tümü")

        cities = self.controller.get_distinct_cities()
        for c in cities:
            self.filter_city.addItem(c['sehir'])

        # Eğer önceden seçili olan hala listede varsa onu seç
        index = self.filter_city.findText(current)
        if index != -1:
            self.filter_city.setCurrentIndex(index)

    def refresh_list(self):
        """Filtrelere göre listeyi yeniler."""
        self.venue_list.clear()

        # Filtre değerlerini al
        city_filter = self.filter_city.currentText()
        name_filter = self.filter_name.text()

        # Controller'a sor
        venues = self.controller.search_venues(city_filter, name_filter)

        for v in venues:
            self.venue_list.addItem(f"{v['id']} - {v['sahne_adi']} ({v['sehir']})")

    def prepare_new_venue(self):
        self.selected_venue_id = None
        self.input_ad.clear()
        self.combo_sehir.setCurrentText("İstanbul")
        self.spin_kapasite.setValue(150)
        self.input_yetkili.clear()
        self.input_iletisim.clear()
        self.input_adres.clear()

        self.btn_delete.hide()
        self.lbl_detail_title.setText("YENİ SAHNE EKLENİYOR")

    def load_venue_details(self, item):
        text = item.text()
        try:
            v_id = int(text.split(" - ")[0])
        except ValueError:
            return  # Hata durumunda çık

        self.selected_venue_id = v_id

        data = self.controller.get_venue_detail(v_id)
        if data:
            self.input_ad.setText(data['sahne_adi'])
            self.combo_sehir.setCurrentText(data['sehir'])
            self.spin_kapasite.setValue(data['kapasite'])
            self.input_yetkili.setText(data['yetkili_kisi'])
            self.input_iletisim.setText(data['iletisim'])
            self.input_adres.setText(data['adres'])

            self.btn_delete.show()
            self.lbl_detail_title.setText(f"DÜZENLENİYOR: {data['sahne_adi']}")

    def save_venue(self):
        ad = self.input_ad.text()

        if not ad:
            QMessageBox.warning(self, "Hata", "Sahne adı boş olamaz!")
            return

        self.controller.save_venue(
            ad=ad,
            sehir=self.combo_sehir.currentText(),
            adres=self.input_adres.toPlainText(),
            kapasite=self.spin_kapasite.value(),
            yetkili=self.input_yetkili.text(),
            iletisim=self.input_iletisim.text(),
            venue_id=self.selected_venue_id
        )

        QMessageBox.information(self, "Başarılı", "Sahne kaydedildi.")

        # Kaydettikten sonra filtre listesini de güncelle (Belki yeni şehir eklendi)
        self.load_filter_cities()
        self.refresh_list()

        if not self.selected_venue_id:
            self.prepare_new_venue()

    def delete_venue(self):
        if self.selected_venue_id:
            reply = QMessageBox.question(self, 'Sil', 'Bu sahneyi silmek istediğine emin misin?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.controller.delete_venue(self.selected_venue_id)
                self.load_filter_cities()  # Şehir silinmiş olabilir
                self.refresh_list()
                self.prepare_new_venue()