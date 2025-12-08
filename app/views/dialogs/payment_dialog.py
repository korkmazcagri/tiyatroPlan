from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QLineEdit, QMessageBox # QMessageBox Eklendi
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont


class PaymentDialog(QDialog):
    def __init__(self, parent=None, personel_name="", current_balance=0):
        super().__init__(parent)
        self.setWindowTitle("Ödeme Onayı")
        self.setModal(True)

        self.personel_name = personel_name
        self.current_balance = current_balance
        self.payment_amount = 0.0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Başlık ve Bilgi
        lbl_info = QLabel(f"Ödeme Yapılıyor: <b>{self.personel_name}</b>")
        lbl_info.setFont(QFont("Arial", 12, QFont.Bold))

        lbl_balance = QLabel(
            f"Güncel Borç (Alacak): <span style='color:#2ecc71;'>{self.current_balance:,.2f} TL</span>")

        layout.addWidget(lbl_info)
        layout.addWidget(lbl_balance)
        layout.addSpacing(10)

        # Miktar Girişi
        lbl_amount = QLabel("Ödenecek Miktar (TL):")
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setMaximum(999999.99)
        self.spin_amount.setMinimum(0.00)
        self.spin_amount.setDecimals(2)
        self.spin_amount.setSuffix(" TL")

        # Varsayılan Miktar Ayarı (Kritik Alan)
        if self.current_balance > 0:
            # Borç pozitif ise, borcun tamamını ödeme miktarı yap
            self.spin_amount.setValue(self.current_balance)
        else:
            # Borç negatif ise (personel bize borçlu ise), varsayılan ödeme 0 TL
            self.spin_amount.setValue(0.00)

        layout.addWidget(lbl_amount)
        layout.addWidget(self.spin_amount)

        # Açıklama
        lbl_desc = QLabel("Açıklama:")
        self.input_desc = QLineEdit("Maaş Ödemesi")
        layout.addWidget(lbl_desc)
        layout.addWidget(self.input_desc)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_confirm = QPushButton("Ödemeyi Kaydet")
        btn_cancel = QPushButton("İptal")

        btn_confirm.clicked.connect(self.accept_payment)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_confirm)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def accept_payment(self):
        amount = self.spin_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir ödeme miktarı girin.")
            return

        self.payment_amount = amount
        self.accept()

    def get_payment_data(self):
        return {
            'amount': self.payment_amount,
            'desc': self.input_desc.text()
        }