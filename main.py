import sys
import os
import time
import sqlite3
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox  # QMessageBox eklendi
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt

# Dosya yollarını düzgün yönetmek için
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ana Pencereyi Çağır
try:
    from app.views.main_window import MainWindow
except ImportError as e:
    print(f"HATA: Modül bulunamadı. Lütfen dosya yapısını kontrol edin. Detay: {e}")
    sys.exit(1)


# ==========================================
# 1. VERİTABANI KONTROLÜ (GÜNCELLENDİ)
# ==========================================
def init_db_local():
    """Veritabanı var mı kontrol eder. Yoksa HATA verir ve kapanır."""
    db_file = "tiyatrodb.db"

    # --- YENİ KONTROL BLOĞU BAŞLANGICI ---
    if not os.path.exists(db_file):
        # Eğer dosya yoksa, kullanıcıya hata göster ve çık
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Veritabanı Bulunamadı!")
        msg.setText(f"Kritik Hata: '{db_file}' dosyası bulunamadı.")
        msg.setInformativeText("Programın çalışması için veritabanı dosyası gereklidir.\n\n"
                               "Lütfen 'tiyatrodb.db' dosyasını .exe veya main.py dosyasının yanına kopyalayın.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        sys.exit(1)  # Programı güvenli şekilde kapat
    # --- YENİ KONTROL BLOĞU BİTİŞİ ---

    # Dosya varsa bağlanıp tabloları garantiye al (Schema update ihtimaline karşı)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Tabloları yine de kontrol edelim (Eksik tablo varsa tamamlasın ama dosya yoksa yaratmasın)
    tables = [
        "CREATE TABLE IF NOT EXISTS kisiler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT NOT NULL, telefon TEXT, rol_tipi TEXT, odeme_tipi TEXT DEFAULT 'Oyun Başı', standart_ucret REAL DEFAULT 0, turne_engeli INTEGER DEFAULT 0, notlar TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "CREATE TABLE IF NOT EXISTS oyunlar (id INTEGER PRIMARY KEY AUTOINCREMENT, oyun_adi TEXT NOT NULL, yazar TEXT, varsayilan_sure INTEGER DEFAULT 40, aktif_mi INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "CREATE TABLE IF NOT EXISTS oyuncu_repertuvari (id INTEGER PRIMARY KEY AUTOINCREMENT, kisi_id INTEGER, oyun_id INTEGER, durum TEXT DEFAULT 'Hazır', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE, FOREIGN KEY (oyun_id) REFERENCES oyunlar(id) ON DELETE CASCADE, UNIQUE(kisi_id, oyun_id));",
        "CREATE TABLE IF NOT EXISTS sahneler (id INTEGER PRIMARY KEY AUTOINCREMENT, sahne_adi TEXT NOT NULL, sehir TEXT NOT NULL, adres TEXT, kapasite INTEGER, yetkili_kisi TEXT, iletisim TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "CREATE TABLE IF NOT EXISTS etkinlikler (id INTEGER PRIMARY KEY AUTOINCREMENT, oyun_id INTEGER, sahne_id INTEGER, tarih TEXT NOT NULL, baslangic_saati TEXT NOT NULL, notlar TEXT, durum TEXT DEFAULT 'Planlandı', FOREIGN KEY (oyun_id) REFERENCES oyunlar(id), FOREIGN KEY (sahne_id) REFERENCES sahneler(id));",
        "CREATE TABLE IF NOT EXISTS etkinlik_kadrosu (id INTEGER PRIMARY KEY AUTOINCREMENT, etkinlik_id INTEGER, kisi_id INTEGER, gorev TEXT, ucret REAL DEFAULT 0, FOREIGN KEY (etkinlik_id) REFERENCES etkinlikler(id) ON DELETE CASCADE, FOREIGN KEY (kisi_id) REFERENCES kisiler(id));",
        "CREATE TABLE IF NOT EXISTS finans_hareketleri (id INTEGER PRIMARY KEY AUTOINCREMENT, kisi_id INTEGER, tarih TEXT NOT NULL, islem_turu TEXT NOT NULL, miktar REAL NOT NULL, aciklama TEXT, FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE);",
        "CREATE TABLE IF NOT EXISTS kisi_haftalik_musaitlik (id INTEGER PRIMARY KEY, kisi_id INTEGER, gun_index INTEGER, durum TEXT DEFAULT 'Müsait', aciklama TEXT);",
        "CREATE TABLE IF NOT EXISTS musaitlik_istisna (id INTEGER PRIMARY KEY, kisi_id INTEGER, tarih TEXT, tur TEXT, aciklama TEXT);"
    ]

    for query in tables:
        cursor.execute(query)

    conn.commit()
    conn.close()


def load_stylesheet(app):
    """CSS dosyasını yükler (UTF-8 Destekli)"""
    try:
        style_path = os.path.join("app", "views", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Stil Dosyası Hatası: {e}")


# ==========================================
# 2. ANA FONKSİYON
# ==========================================
def main():
    app = QApplication(sys.argv)

    # --- SPLASH SCREEN ---
    logo_path = os.path.join("assets", "icon.jpg")

    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
    else:
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor("#1e1e1e"))

    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    # --- YÜKLEME İŞLEMLERİ ---

    # 1. Veritabanı Kontrolü (HATA VARSA BURADA KESİLİR)
    init_db_local()

    # 2. Bekleme
    time.sleep(1.5)
    splash.showMessage("Arayüz Yükleniyor...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    app.processEvents()
    time.sleep(0.5)

    load_stylesheet(app)

    window = MainWindow()
    window.show()
    splash.finish(window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()