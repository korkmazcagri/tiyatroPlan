import sys
import os
import time  # Bekleme süresi için
import sqlite3
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# Dosya yollarını düzgün yönetmek için
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ana Pencereyi Çağır
from app.views.main_window import MainWindow


# ==========================================
# 1. VERİTABANI KONTROLÜ (İÇERİ GÖMÜLDÜ)
# ==========================================
def init_db_local():
    """Veritabanı tablolarını kontrol eder, yoksa oluşturur."""
    db_file = "tiyatrodb.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Temel Tabloların Varlığını Garantiye Al
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

    # --- SPLASH SCREEN (YÜKLEME EKRANI) ---
    # Proje klasörüne 'logo.png' koyarsan o çıkar, yoksa sadece yazı çıkar.
    logo_path = os.path.join("assets", "icon.jpg")

    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        # İstersen logoyu boyutlandır:
        # pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = QSplashScreen(pixmap)
    else:
        # Logo yoksa boş bir gri kutu göstermesin diye varsayılan oluşturabiliriz
        # Ama genelde QSplashScreen resim ister. Resim yoksa pas geçelim.
        splash = None

    if splash:
        splash.showMessage("Sistem Başlatılıyor...\nVeritabanı Kontrol Ediliyor...", Qt.AlignBottom | Qt.AlignCenter,
                           Qt.white)
        splash.setFont(QFont("Arial", 10, QFont.Bold))
        splash.show()
        app.processEvents()  # Arayüzün donmaması için

    # --- YÜKLEME İŞLEMLERİ ---

    # 1. Veritabanı Kontrolü
    init_db_local()

    # 2. Yapay Bekleme (Loading ekranı görünsün diye - İstersen kaldırabilirsin)
    if splash:
        time.sleep(1.5)
        splash.showMessage("Arayüz Yükleniyor...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()

    # 3. Tasarım Yüklemesi
    load_stylesheet(app)

    # 4. Ana Pencereyi Oluştur
    window = MainWindow()

    # --- AÇILIŞ ---
    window.show()

    if splash:
        splash.finish(window)  # Ana pencere açılınca splash'i kapat

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()