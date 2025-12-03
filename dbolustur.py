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

    # ==========================================
    # 2. VERİLERİ YÜKLE
    # ==========================================

    # --- OYUNLAR ---
    print("Oyunlar ekleniyor...")
    cursor.execute("INSERT INTO oyunlar (oyun_adi, yazar, varsayilan_sure) VALUES (?, ?, ?)",
                   ("Saatleri Ayarlama Enstitüsü", "Ahmet Hamdi Tanpınar", 70))
    id_saatler = cursor.lastrowid

    cursor.execute("INSERT INTO oyunlar (oyun_adi, yazar, varsayilan_sure) VALUES (?, ?, ?)",
                   ("Suç ve Ceza", "Dostoyevski", 90))
    id_sucveceza = cursor.lastrowid

    # --- KİŞİLER ---
    print("Kişiler ekleniyor...")
    # 1. Çağrı Korkmaz (Oyuncu - Turne Engeli YOK)
    cursor.execute("INSERT INTO kisiler (ad_soyad, rol_tipi, turne_engeli) VALUES (?, ?, ?)",
                   ("Çağrı Korkmaz", "Oyuncu", 0))
    id_cagri = cursor.lastrowid

    # 2. Müslüm Çelik (Oyuncu - Turne Engeli YOK)
    cursor.execute("INSERT INTO kisiler (ad_soyad, rol_tipi, turne_engeli) VALUES (?, ?, ?)",
                   ("Müslüm Çelik", "Oyuncu", 0))
    id_muslum = cursor.lastrowid

    # 3. Mehmet Işık (Teknik)
    cursor.execute("INSERT INTO kisiler (ad_soyad, rol_tipi) VALUES (?, ?)", ("Mehmet Işık", "Teknik"))
    id_mehmet = cursor.lastrowid

    # --- REPERTUVAR (KİM HANGİ OYUNDA?) ---
    print("Repertuvar tanımlanıyor...")
    # Çağrı -> Hem Saatler hem Suç ve Ceza
    cursor.execute("INSERT INTO oyuncu_repertuvari (kisi_id, oyun_id, durum) VALUES (?, ?, ?)",
                   (id_cagri, id_saatler, "Hazır"))
    cursor.execute("INSERT INTO oyuncu_repertuvari (kisi_id, oyun_id, durum) VALUES (?, ?, ?)",
                   (id_cagri, id_sucveceza, "Hazır"))

    # Müslüm -> Sadece Suç ve Ceza
    cursor.execute("INSERT INTO oyuncu_repertuvari (kisi_id, oyun_id, durum) VALUES (?, ?, ?)",
                   (id_muslum, id_sucveceza, "Hazır"))

    # --- SAHNELER ---
    print("Sahneler ekleniyor...")
    # 1. Aydem Sahne (İstanbul - Merkez)
    cursor.execute("INSERT INTO sahneler (sahne_adi, sehir, kapasite) VALUES (?, ?, ?)",
                   ("Aydem Sahne", "İstanbul", 150))
    id_aydem = cursor.lastrowid

    # 2. Bolu
    cursor.execute("INSERT INTO sahneler (sahne_adi, sehir, kapasite) VALUES (?, ?, ?)",
                   ("Bolu Merkez Kültür Merkezi", "Bolu", 300))
    id_bolu = cursor.lastrowid

    # 3. Ankara (2 Tane)
    cursor.execute("INSERT INTO sahneler (sahne_adi, sehir, kapasite) VALUES (?, ?, ?)",
                   ("Ankara Kültür Merkezi", "Ankara", 500))
    id_ankara_km = cursor.lastrowid

    cursor.execute("INSERT INTO sahneler (sahne_adi, sehir, kapasite) VALUES (?, ?, ?)",
                   ("Ankara Sahnesi", "Ankara", 200))
    id_ankara_sahne = cursor.lastrowid

    # --- ÖRNEK ETKİNLİKLER (TAKVİM) ---
    print("Takvim oluşturuluyor...")
    bugun = date.today()

    # Etkinlik 1: Yarın - Saatleri Ayarlama Enstitüsü @ Aydem Sahne (Sadece Çağrı)
    tarih1 = (bugun + timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, notlar) VALUES (?, ?, ?, ?, ?)",
                   (id_saatler, id_aydem, tarih1, "20:30", "Prömiyer Tadında"))
    event1_id = cursor.lastrowid
    # Kadro: Çağrı (Oyuncu), Mehmet (Reji)
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event1_id, id_cagri, "Oyuncu"))
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event1_id, id_mehmet, "Reji"))

    # Etkinlik 2: 3 Gün Sonra - Suç ve Ceza @ Bolu (Turne) - (Çağrı ve Müslüm)
    tarih2 = (bugun + timedelta(days=3)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, notlar) VALUES (?, ?, ?, ?, ?)",
                   (id_sucveceza, id_bolu, tarih2, "19:00", "Turne Ekibi 14:00'da çıkacak"))
    event2_id = cursor.lastrowid
    # Kadro: Çağrı, Müslüm, Mehmet
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event2_id, id_cagri, "Oyuncu"))
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event2_id, id_muslum, "Oyuncu"))
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event2_id, id_mehmet, "Reji"))

    # Etkinlik 3: 5 Gün Sonra - Suç ve Ceza @ Ankara
    tarih3 = (bugun + timedelta(days=5)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, notlar) VALUES (?, ?, ?, ?, ?)",
                   (id_sucveceza, id_ankara_km, tarih3, "20:00", "Büyük Salon"))
    event3_id = cursor.lastrowid
    # Kadro: Çağrı, Müslüm, Mehmet
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event3_id, id_cagri, "Oyuncu"))
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event3_id, id_muslum, "Oyuncu"))
    cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                   (event3_id, id_mehmet, "Reji"))

    conn.commit()
    conn.close()
    print(f"BAŞARILI: '{db_file}' dosyası VERİLERLE HAZIR!")


if __name__ == "__main__":
    create_database()