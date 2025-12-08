import sqlite3
import os
import config
from datetime import date, timedelta


def create_database():
    db_file = config.DB_NAME

    # Temiz başlangıç için eskiyi sil
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Eski {db_file} silindi, temiz kurulum yapılıyor...")
        except PermissionError:
            print("HATA: Veritabanı dosyası şu an açık! Lütfen uygulamayı kapatıp tekrar deneyin.")
            return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ==========================================
    # 1. TABLO YAPILARINI OLUŞTUR
    # ==========================================

    # Kişiler
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kisiler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        telefon TEXT,
        rol_tipi TEXT, -- 'Oyuncu' veya 'Teknik'
        odeme_tipi TEXT DEFAULT 'Oyun Başı', 
        standart_ucret REAL DEFAULT 0, 
        turne_engeli INTEGER DEFAULT 0, 
        notlar TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Oyunlar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oyunlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oyun_adi TEXT NOT NULL,
        yazar TEXT,
        varsayilan_sure INTEGER DEFAULT 40,
        aktif_mi INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Repertuvar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oyuncu_repertuvari (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kisi_id INTEGER,
        oyun_id INTEGER,
        durum TEXT DEFAULT 'Hazır', 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE,
        FOREIGN KEY (oyun_id) REFERENCES oyunlar(id) ON DELETE CASCADE,
        UNIQUE(kisi_id, oyun_id) 
    );
    """)

    # Sahneler
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sahneler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sahne_adi TEXT NOT NULL,
        sehir TEXT NOT NULL,
        adres TEXT,
        kapasite INTEGER,
        yetkili_kisi TEXT,
        iletisim TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Etkinlikler
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etkinlikler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oyun_id INTEGER,
        sahne_id INTEGER,
        tarih TEXT NOT NULL, 
        baslangic_saati TEXT NOT NULL, 
        notlar TEXT,
        durum TEXT DEFAULT 'Planlandı', 
        FOREIGN KEY (oyun_id) REFERENCES oyunlar(id),
        FOREIGN KEY (sahne_id) REFERENCES sahneler(id)
    );
    """)

    # Etkinlik Kadrosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etkinlik_kadrosu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etkinlik_id INTEGER,
        kisi_id INTEGER,
        gorev TEXT, 
        ucret REAL DEFAULT 0,
        FOREIGN KEY (etkinlik_id) REFERENCES etkinlikler(id) ON DELETE CASCADE,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id)
    );
    """)

    # Finans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finans_hareketleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kisi_id INTEGER,
        tarih TEXT NOT NULL,
        islem_turu TEXT NOT NULL, 
        miktar REAL NOT NULL,
        aciklama TEXT,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
    );
    """)

    # Diğer Yan Tablolar
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS kisi_haftalik_musaitlik (id INTEGER PRIMARY KEY, kisi_id INTEGER, gun_index INTEGER, durum INTEGER DEFAULT 1, aciklama TEXT);")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS kisi_takvim_engelleri (id INTEGER PRIMARY KEY, kisi_id INTEGER, tarih TEXT, tur TEXT, aciklama TEXT);")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS etkinlik_biletleri (id INTEGER PRIMARY KEY, etkinlik_id INTEGER, bilet_tipi TEXT, fiyat REAL, kontenjan INTEGER, satilan INTEGER);")

    print("Tablolar oluşturuldu.")



    conn.commit()
    conn.close()
    print(f"BAŞARILI: '{db_file}' dosyası VERİLERLE HAZIR!")


if __name__ == "__main__":
    create_database()