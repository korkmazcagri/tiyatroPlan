import sqlite3
import os

# Veritabanı adı
try:
    import config

    DB_NAME = config.DB_NAME
except ImportError:
    DB_NAME = "tiyatrodb.db"

# ==============================================================================
# SADECE BURAYI DEĞİŞTİRİN
# ==============================================================================

OYUN_ADI_ARA = "Kamelyalı Kadın"
VARSAYILAN_SEHIR = "İstanbul"

# Format: (Gün, Ay, Yıl, Saat, Sahne Adı)
YENI_ETKINLIKLER = [
    # Aralık 2025
    #("21", "12", "2025", "19:15", "Kartal Ada Sanat Tiyatrosu"),

    # Ocak 2026
    ("04", "01", "2026", "20:30", "Aydem Sahne"),
]
# ==============================================================================
# KODUN GERİ KALANINA DOKUNMANIZA GEREK YOK
# ==============================================================================

def veri_ekle():
    if not os.path.exists(DB_NAME):
        print("HATA: Veritabanı dosyası bulunamadı!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f">>> İşlem Başladı: '{OYUN_ADI_ARA}'...")

    # 1. OYUN ID BUL
    cursor.execute("SELECT id, oyun_adi FROM oyunlar WHERE oyun_adi LIKE ?", (f"%{OYUN_ADI_ARA}%",))
    oyun = cursor.fetchone()

    if not oyun:
        print(f"❌ HATA: '{OYUN_ADI_ARA}' içeren bir oyun bulunamadı!")
        print("   -> Lütfen oyun adını kontrol edin veya önce veritabanına ekleyin.")
        return

    oyun_id = oyun[0]
    tam_oyun_adi = oyun[1]
    print(f"✅ Oyun Bulundu: {tam_oyun_adi} (ID: {oyun_id})")

    # 2. ETKİNLİKLERİ EKLE
    print("\n--- Tarihler ve Sahneler İşleniyor ---")
    eklenen_sayisi = 0

    for gun, ay, yil, saat, sahne_adi in YENI_ETKINLIKLER:
        tarih_str = f"{yil}-{ay}-{gun}"

        # A. Sahne ID Bul veya Oluştur
        cursor.execute("SELECT id FROM sahneler WHERE sahne_adi = ?", (sahne_adi,))
        sahne_res = cursor.fetchone()

        if sahne_res:
            sahne_id = sahne_res[0]
        else:
            # Sahne yoksa oluştur
            cursor.execute("INSERT INTO sahneler (sahne_adi, sehir) VALUES (?, ?)", (sahne_adi, VARSAYILAN_SEHIR))
            sahne_id = cursor.lastrowid
            print(f"  ➕ Yeni Sahne Eklendi: {sahne_adi}")

        # B. Etkinliği Ekle (Çakışma Kontrolüyle)
        # Aynı oyun, aynı tarih, aynı saat, aynı sahne var mı?
        cursor.execute("""
            SELECT id FROM etkinlikler 
            WHERE oyun_id=? AND tarih=? AND baslangic_saati=? AND sahne_id=?
        """, (oyun_id, tarih_str, saat, sahne_id))

        if cursor.fetchone():
            print(f"  ⚠️  Zaten Var: {tarih_str} {saat} - {sahne_adi}")
        else:
            cursor.execute("""
                INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, durum) 
                VALUES (?, ?, ?, ?, 'Planlandı')
            """, (oyun_id, sahne_id, tarih_str, saat))
            print(f"  📅 Eklendi: {tarih_str} - {saat} @ {sahne_adi}")
            eklenen_sayisi += 1

    conn.commit()
    conn.close()
    print(f"\n>>> İşlem Tamam. Toplam {eklenen_sayisi} yeni etkinlik eklendi.")


if __name__ == "__main__":
    veri_ekle()