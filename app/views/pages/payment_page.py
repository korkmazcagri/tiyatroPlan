from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox, \
    QHBoxLayout, QLabel, QDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDate, QTimer # QTimer eklendi
# Controller ve Dialog importları
from app.controllers.personel_controller import PersonelController
from app.views.dialogs.payment_dialog import PaymentDialog


class PaymentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PersonelController()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        lbl_title = QLabel("💳 PERSONEL ÖDEME EKRANI")
        lbl_title.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 18px;")
        main_layout.addWidget(lbl_title)

        self.table_payment = QTableWidget()
        self.table_payment.setColumnCount(3)
        self.table_payment.setHorizontalHeaderLabels(["İsim", "Bakiye (Borç)", "İşlem"])

        # İsim ve Bakiyeyi genişlet, İşlemi daralt
        self.table_payment.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_payment.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_payment.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.table_payment.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table_payment)

        # --- YENİLEME MANTIĞI: Tek fonksiyona bağlandı ---
        self.load_data()

    # --- ESKİ load_payment_data -> ŞİMDİ load_data ---
        # app/views/pages/payment_page.py dosyasında, load_data fonksiyonunu değiştirin.

    def load_data(self):
        """MainWindow tarafından çağrıldığında tabloyu yeniler ve borçluya göre sıralar."""

        # UI Yenileme işleminin tamamını bir hata yakalama bloğuna alıyoruz
        try:
            self.table_payment.setRowCount(0)

            # Controller'dan veriyi çek
            personel_data = self.controller.get_personnel_with_balance()

            for row_idx, data in enumerate(personel_data):
                # 1. Veriyi Temizle ve Hazırla
                balance_raw = data['bakiye']
                clean_balance = float(balance_raw) if balance_raw is not None else 0.0

                # 2. Tablo Satırı Oluştur
                self.table_payment.insertRow(row_idx)
                self.table_payment.setItem(row_idx, 0, QTableWidgetItem(data['ad_soyad']))

                # 3. Bakiye (Tutar ve Renk)
                item_bakiye = QTableWidgetItem(f"{clean_balance:,.2f} TL")

                color = QColor("#2ecc71") if clean_balance >= 0 else QColor("#e74c3c")
                item_bakiye.setForeground(color)
                self.table_payment.setItem(row_idx, 1, item_bakiye)

                # 4. Öde Butonu
                btn_pay = QPushButton("Öde")
                btn_pay.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")

                # 5. Butonu Fonksiyona Bağla (Lambda ile temiz veri geçiriliyor)
                btn_pay.clicked.connect(
                    lambda _, p_id=data['id'], name=data['ad_soyad'], bal=clean_balance: self.open_payment_dialog(
                        p_id, name, bal)
                )

                # 6. Hücreye Yerleştir
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(5, 0, 5, 0)
                layout.addWidget(btn_pay)
                self.table_payment.setCellWidget(row_idx, 2, container)

        except Exception as e:
            # Herhangi bir kritik hata oluşursa, çökme yerine uyarı ver
            QMessageBox.critical(self, "Kritik Yükleme Hatası",
                                 f"Ödeme tablosu yüklenirken beklenmedik bir hata oluştu. Lütfen verilerinizi kontrol edin.\n\nHata: {e}")
            self.table_payment.setRowCount(0)  # Tabloyu temizle
    def open_payment_dialog(self, personel_id, personel_name, current_balance):
        """Ödeme onay penceresini açar."""
        dialog = PaymentDialog(
            self,
            personel_name=personel_name,
            current_balance=current_balance
        )
        try:
            if dialog.exec_() == QDialog.Accepted:
                payment_data = dialog.get_payment_data()
                amount = payment_data['amount']
                desc = payment_data['desc']

                if amount <= 0:
                    QMessageBox.warning(self, "Hata", "Ödenecek miktar 0 TL'den büyük olmalıdır.")
                    return

                # Ödeme İşlemini Kaydet

                success = self.controller.add_transaction(
                    personel_id, QDate.currentDate().toString("yyyy-MM-dd"),
                    "Ödeme (Para Çıkışı)", amount, desc
                )

                self.load_data()

        except Exception as e:
            print(e)

    def finish_payment_ui(self, personel_name, amount):
        """Ödeme başarılı olduktan sonra UI işlemlerini yapan fonksiyon."""
        QMessageBox.information(self, "Başarılı", f"{personel_name}'a {amount:,.2f} TL ödeme kaydedildi.")
        self.load_data()  # Yenileme güvenli bir şekilde tetiklenir