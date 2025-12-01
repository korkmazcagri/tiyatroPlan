import sqlite3
import os
import config  # config.py dosyasından DB ismini alıyoruz


def create_database():
    db_file = config.DB_NAME

    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Eski {db_file} silindi, temiz kurulum yapılıyor...")
        except PermissionError:
            print("HATA: Veritabanı dosyası şu an açık! Uygulamayı kapatıp tekrar deneyin.")
            return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # --- 1. TABLO: KİŞİLER (Personel) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kisiler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        telefon TEXT,
        rol_tipi TEXT, -- 'Oyuncu', 'Reji', 'Her İkisi', 'Teknik'
        odeme_tipi TEXT DEFAULT 'Oyun Başı', -- 'Oyun Başı', 'Aylık Maaş'
        standart_ucret REAL DEFAULT 0, 
        turne_engeli INTEGER DEFAULT 0, -- 0: Yok, 1: Var
        notlar TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- 2. TABLO: HAFTALIK MÜSAİTLİK ŞABLONU ---
    # 0=Pzt ... 6=Pazar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kisi_haftalik_musaitlik (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kisi_id INTEGER,
        gun_index INTEGER, 
        durum INTEGER DEFAULT 1, -- 1: Müsait, 0: Değil
        aciklama TEXT, 
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
    );
    """)

    # --- 3. TABLO: TARİH BAZLI ENGELLER (İzinler) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kisi_takvim_engelleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kisi_id INTEGER,
        tarih TEXT NOT NULL, 
        tur TEXT DEFAULT 'İzin', 
        aciklama TEXT,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
    );
    """)

    # --- 4. TABLO: FİNANS HAREKETLERİ ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finans_hareketleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kisi_id INTEGER,
        tarih TEXT NOT NULL,
        islem_turu TEXT NOT NULL, -- 'Hakediş', 'Ödeme'
        miktar REAL NOT NULL,
        aciklama TEXT,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
    );
    """)

    # --- 5. TABLO: OYUNLAR ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oyunlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oyun_adi TEXT NOT NULL,
        tur TEXT, 
        yazar TEXT,
        varsayilan_sure INTEGER DEFAULT 60,
        aktif_mi INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- 6. TABLO: SAHNELER ---
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

    # --- 7. TABLO: ETKİNLİKLER (Takvim) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etkinlikler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oyun_id INTEGER,
        sahne_id INTEGER,
        tarih TEXT NOT NULL, 
        baslangic_saati TEXT NOT NULL, 
        bitis_saati TEXT,
        notlar TEXT,
        durum TEXT DEFAULT 'Planlandı', 
        finans_islendi INTEGER DEFAULT 0,
        FOREIGN KEY (oyun_id) REFERENCES oyunlar(id),
        FOREIGN KEY (sahne_id) REFERENCES sahneler(id)
    );
    """)

    # --- 8. TABLO: ETKİNLİK KADROSU ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etkinlik_kadrosu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etkinlik_id INTEGER,
        kisi_id INTEGER,
        gorev TEXT, 
        anlik_ucret REAL DEFAULT 0,
        FOREIGN KEY (etkinlik_id) REFERENCES etkinlikler(id) ON DELETE CASCADE,
        FOREIGN KEY (kisi_id) REFERENCES kisiler(id)
    );
    """)

    # --- 9. TABLO: BİLET TİPLERİ VE SATIŞLAR ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etkinlik_biletleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etkinlik_id INTEGER,
        bilet_tipi TEXT,
        fiyat REAL,
        kontenjan INTEGER,
        satilan INTEGER DEFAULT 0,
        FOREIGN KEY (etkinlik_id) REFERENCES etkinlikler(id) ON DELETE CASCADE
    );
    """)

    # --- ÖRNEK VERİLER ---
    print("Tablolar oluşturuldu. Örnek veriler yükleniyor...")

    # Sahneler: Aydem Sahne
    cursor.execute("INSERT INTO sahneler (sahne_adi, sehir, kapasite) VALUES (?, ?, ?)",
                   ("Aydem Sahne", "İstanbul", 150))

    conn.commit()
    conn.close()
    print(f"BAŞARILI: '{db_file}' dosyası oluşturuldu!")


if __name__ == "__main__":
    create_database()