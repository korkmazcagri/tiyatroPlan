from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QLineEdit, QTextEdit, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from app.controllers.tour_controller import TourController
from app.controllers.personel_controller import PersonelController


class TourPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = TourController()
        self.personel_controller = PersonelController()
        self.controller.initialize_tables()
        self.selected_team_id = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # --- SOL: LİSTE ---
        left_side = QVBoxLayout()
        left_side.addWidget(QLabel("TURNE EKİPLERİ"))
        self.team_list = QListWidget()
        self.team_list.itemClicked.connect(self.load_team_details)
        left_side.addWidget(self.team_list)

        btn_new = QPushButton("+ Yeni Ekip Tanımla")
        btn_new.clicked.connect(self.prepare_new_team)
        left_side.addWidget(btn_new)

        btn_del = QPushButton("Ekibi Sil")
        btn_del.setStyleSheet("background-color: #c0392b;")
        btn_del.clicked.connect(self.delete_team)
        left_side.addWidget(btn_del)

        layout.addLayout(left_side, 2)

        # --- SAĞ: DETAYLAR ---
        right_side = QVBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ekip adını girin ve Kaydet'e basın...")
        self.input_notes = QTextEdit()
        self.input_notes.setMaximumHeight(60)

        form = QFormLayout()
        form.addRow("Ekip Adı:", self.input_name)
        form.addRow("Notlar:", self.input_notes)
        right_side.addLayout(form)

        # Oyuncu Seçimi
        member_layout = QHBoxLayout()

        v_all = QVBoxLayout()
        v_all.addWidget(QLabel("Personel (Ekle: Çift Tıkla)"))
        self.list_all_staff = QListWidget()
        self.list_all_staff.itemDoubleClicked.connect(self.add_member)
        v_all.addWidget(self.list_all_staff)

        v_team = QVBoxLayout()
        v_team.addWidget(QLabel("Ekipteki Kadro (Çıkar: Çift Tıkla)"))
        self.list_team_members = QListWidget()
        self.list_team_members.itemDoubleClicked.connect(self.remove_member)
        v_team.addWidget(self.list_team_members)

        member_layout.addLayout(v_all)
        member_layout.addLayout(v_team)
        right_side.addLayout(member_layout)

        right_side.addWidget(QLabel("🎬 BU EKİBİN REPERTUVARI"))
        self.list_team_games = QListWidget()
        right_side.addWidget(self.list_team_games)

        self.btn_save = QPushButton("💾 EKİBİ KAYDET")
        self.btn_save.clicked.connect(self.save_team)
        self.btn_save.setStyleSheet("background-color: #27ae60; height: 40px;")
        right_side.addWidget(self.btn_save)

        layout.addLayout(right_side, 5)
        self.refresh_teams()
        self.load_all_staff()

    def refresh_teams(self):
        """Ekip listesini veritabanından çeker ve yeniler."""
        self.team_list.clear()
        teams = self.controller.get_all_teams()
        if teams:
            for t in teams:
                self.team_list.addItem(f"{t['id']} - {t['ekip_adi']}")

    def load_all_staff(self):
        self.list_all_staff.clear()
        for p in self.personel_controller.get_all_personel():
            self.list_all_staff.addItem(f"{p['id']} - {p['ad_soyad']}")

    def save_team(self):
        name = self.input_name.text().strip()
        notes = self.input_notes.toPlainText()

        if not name:
            QMessageBox.warning(self, "Hata", "Lütfen bir ekip adı girin!")
            return

        try:
            # Controller'dan dönen sonucu al
            res_id = self.controller.save_team(name, notes, self.selected_team_id)

            # Eğer res_id bir sayı ise (0'dan büyükse) başarılıdır
            if res_id is not None:
                self.selected_team_id = res_id
                self.refresh_teams()
                QMessageBox.information(self, "Başarılı", "Ekip başarıyla sisteme işlendi.")
            else:
                QMessageBox.critical(self, "Hata", "Veritabanı ID döndürmedi!")
        except Exception as e:
            QMessageBox.critical(self, "Sistem Hatası", f"Hata oluştu: {str(e)}")
            print(f"DEBUG: Kayıt Hatası -> {e}")
    def load_team_details(self, item):
        try:
            self.selected_team_id = int(item.text().split(" - ")[0])
            # Veritabanından güncel bilgiyi tekrar çek
            all_teams = self.controller.get_all_teams()
            team = next(t for t in all_teams if t['id'] == self.selected_team_id)

            self.input_name.setText(team['ekip_adi'])
            self.input_notes.setText(team['notlar'])
            self.refresh_team_info()
        except Exception as e:
            print(f"Yükleme hatası: {e}")

    def add_member(self, item):
        if not self.selected_team_id:
            QMessageBox.warning(self, "Hata", "Önce ekibi kaydedip sol listeden seçmelisiniz!")
            return
        p_id = int(item.text().split(" - ")[0])
        self.controller.add_member_to_team(self.selected_team_id, p_id)
        self.refresh_team_info()

    def remove_member(self, item):
        if not self.selected_team_id: return
        p_id = int(item.text().split(" - ")[0])
        self.controller.remove_member_from_team(self.selected_team_id, p_id)
        self.refresh_team_info()

    def refresh_team_info(self):
        """Üyeleri ve otomatik oyunları günceller."""
        if not self.selected_team_id: return

        self.list_team_members.clear()
        for m in self.controller.get_team_members(self.selected_team_id):
            self.list_team_members.addItem(f"{m['id']} - {m['ad_soyad']}")

        self.list_team_games.clear()
        for g in self.controller.get_team_shared_games(self.selected_team_id):
            self.list_team_games.addItem(f"• {g['oyun_adi']}")

    def delete_team(self):
        if not self.selected_team_id: return
        if QMessageBox.question(self, "Onay", "Ekibi silmek istediğinize emin misiniz?") == QMessageBox.Yes:
            self.controller.delete_team(self.selected_team_id)
            self.prepare_new_team()
            self.refresh_teams()

    def prepare_new_team(self):
        self.selected_team_id = None
        self.input_name.clear()
        self.input_notes.clear()
        self.list_team_members.clear()
        self.list_team_games.clear()