from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QLineEdit, QSpinBox,
                             QCheckBox, QFormLayout, QMessageBox, QFrame, QListWidgetItem, QComboBox)
from PyQt5.QtCore import Qt
from app.controllers.play_controller import PlayController


class PlaysPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PlayController()
        self.selected_play_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- SOL TARAF (LİSTE VE FİLTRE) ---
        left_layout = QVBoxLayout()

        self.lbl_list_title = QLabel("OYUN LİSTESİ")
        self.lbl_list_title.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 16px;")
        left_layout.addWidget(self.lbl_list_title)

        # --- FİLTRE ALANI (YENİ) ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #1a1a1a; border-radius: 5px; padding: 5px;")
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setSpacing(5)

        # Durum Filtresi
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tümü", "Aktif Oyunlar", "Pasif (Arşiv)"])
        self.filter_status.currentTextChanged.connect(self.refresh_list)  # Değişince yenile

        # İsim Arama
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Oyun adı ara...")
        self.filter_name.textChanged.connect(self.refresh_list)  # Yazdıkça yenile

        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(self.filter_status)
        filter_layout.addWidget(QLabel("Oyun Adı:"))
        filter_layout.addWidget(self.filter_name)

        left_layout.addWidget(filter_frame)
        # ---------------------------

        self.play_list = QListWidget()
        self.play_list.itemClicked.connect(self.load_play_details)
        left_layout.addWidget(self.play_list)

        self.btn_new = QPushButton("+ Yeni Oyun Ekle")
        self.btn_new.setProperty("class", "action_btn")
        self.btn_new.clicked.connect(self.prepare_new_play)
        left_layout.addWidget(self.btn_new)

        main_layout.addLayout(left_layout, 2)  # %20 Genişlik

        # --- SAĞ TARAF (DETAY FORMU ve KADRO LİSTESİ) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 0, 0, 0)

        # 1. BÖLÜM: OYUN BİLGİLERİ FORM
        self.lbl_detail_title = QLabel("YENİ OYUN")
        self.lbl_detail_title.setObjectName("page_title")
        right_layout.addWidget(self.lbl_detail_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_ad = QLineEdit()
        self.input_ad.setPlaceholderText("Örn: Godot'yu Beklerken")

        self.input_yazar = QLineEdit()
        self.input_yazar.setPlaceholderText("Yazarın Adı")

        self.spin_sure = QSpinBox()
        self.spin_sure.setRange(1, 300)
        self.spin_sure.setValue(40)  # Varsayılan 40 dk
        self.spin_sure.setSuffix(" Dakika")

        self.check_aktif = QCheckBox("Aktif")
        self.check_aktif.setChecked(True)

        form_layout.addRow("Oyun Adı:", self.input_ad)
        form_layout.addRow("Yazar:", self.input_yazar)
        form_layout.addRow("Ortalama Süre:", self.spin_sure)
        form_layout.addRow("Durum:", self.check_aktif)

        right_layout.addLayout(form_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Oyunu Kaydet")
        self.btn_save.setProperty("class", "action_btn")
        self.btn_save.clicked.connect(self.save_play)

        self.btn_delete = QPushButton("Oyunu Sil")
        self.btn_delete.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_play)
        self.btn_delete.hide()

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        right_layout.addLayout(btn_layout)

        # Araya çizgi veya boşluk
        right_layout.addSpacing(20)

        # 2. BÖLÜM: OYUNCU KADROSU
        lbl_cast = QLabel("Bu Oyunu Oynayanlar")
        lbl_cast.setObjectName("section_title")
        right_layout.addWidget(lbl_cast)

        self.cast_list = QListWidget()
        self.cast_list.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; color: #ddd;")
        right_layout.addWidget(self.cast_list)

        main_layout.addWidget(right_widget, 4)  # %40 Genişlik
        main_layout.addStretch(1)

        # Listeyi doldur
        self.refresh_list()

    # --- FONKSİYONLAR ---

    def refresh_list(self):
        """Listeyi filtrelere göre yeniler."""
        self.play_list.clear()

        # Filtreleri al
        name_val = self.filter_name.text()
        status_val = self.filter_status.currentText()

        # Controller'dan veriyi çek
        plays = self.controller.search_plays(name_filter=name_val, status_filter=status_val)

        for p in plays:
            item_text = f"{p['oyun_adi']}"
            if p['aktif_mi'] == 0:
                item_text += " (Pasif)"

            item = QListWidgetItem(item_text)
            # Veri olarak ID'yi sakla, metin parse etmek riskli olabilir
            item.setData(Qt.UserRole, p['id'])

            # Pasifse rengi gri yap
            if p['aktif_mi'] == 0:
                item.setForeground(Qt.gray)

            self.play_list.addItem(item)

    def prepare_new_play(self):
        """Formu temizler."""
        self.selected_play_id = None
        self.input_ad.clear()
        self.input_yazar.clear()
        self.spin_sure.setValue(40)
        self.check_aktif.setChecked(True)

        self.btn_delete.hide()
        self.cast_list.clear()
        self.lbl_detail_title.setText("YENİ OYUN EKLENİYOR")

    def load_play_details(self, item):
        """Seçilen oyunu forma yükler."""
        # ID'yi UserRole'den al (Daha güvenli)
        p_id = item.data(Qt.UserRole)

        # Eğer eski usul eklenmişse ve data yoksa text'ten parse et (Geriye uyumluluk)
        if not p_id:
            try:
                # Ancak refresh_list artık data koyuyor, bu ihtimal düşük.
                # Yine de string'de "ID - Ad" formatı kullanmıyorsak direkt ID alamayız.
                # Bu örnekte listede sadece AD yazıyor, o yüzden ID'yi item.data'dan almak ZORUNLU.
                pass
            except:
                return

        self.selected_play_id = p_id

        data = self.controller.get_play_detail(p_id)
        if data:
            self.input_ad.setText(data['oyun_adi'])
            self.input_yazar.setText(data['yazar'])
            self.spin_sure.setValue(data['varsayilan_sure'])
            self.check_aktif.setChecked(bool(data['aktif_mi']))

            self.btn_delete.show()
            self.lbl_detail_title.setText(f"DÜZENLENİYOR: {data['oyun_adi']}")

            # KADROYU YÜKLE
            self.load_cast_list(p_id)

    def load_cast_list(self, play_id):
        """Bu oyunu oynayanları listeye doldurur."""
        self.cast_list.clear()
        cast = self.controller.get_play_cast(play_id)

        if not cast:
            self.cast_list.addItem("Henüz kimse eklenmemiş.")
            return

        for actor in cast:
            durum_text = f"({actor['durum']})"
            full_text = f"{actor['ad_soyad']} {durum_text}"

            item = QListWidgetItem(full_text)

            if actor['durum'] == 'Hazır':
                item.setForeground(Qt.green)
            else:
                item.setForeground(Qt.yellow)

            self.cast_list.addItem(item)

    def save_play(self):
        ad = self.input_ad.text()
        if not ad:
            QMessageBox.warning(self, "Hata", "Oyun adı boş olamaz!")
            return

        self.controller.save_play(
            ad=ad,
            yazar=self.input_yazar.text(),
            sure=self.spin_sure.value(),
            aktif_mi=1 if self.check_aktif.isChecked() else 0,
            play_id=self.selected_play_id
        )

        QMessageBox.information(self, "Başarılı", "Oyun kaydedildi.")
        self.refresh_list()

        if not self.selected_play_id:
            self.prepare_new_play()

    def delete_play(self):
        if self.selected_play_id:
            reply = QMessageBox.question(self, 'Sil',
                                         'Bu oyunu silmek istediğine emin misin?\nBuna bağlı takvim kayıtları etkilenebilir.',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.controller.delete_play(self.selected_play_id)
                self.refresh_list()
                self.prepare_new_play()