from app.core.db import execute_query, get_db_connection


class PersonelController:
    def __init__(self):
        # Controller başlatıldığında tabloları kontrol et
        self.init_availability_tables()

    def init_availability_tables(self):
        """Müsaitlik tabloları yoksa oluşturur (EKSİK OLAN KISIMDI)."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Haftalık Rutin Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS musaitlik_haftalik (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kisi_id INTEGER,
                gun_index INTEGER,
                durum TEXT,
                UNIQUE(kisi_id, gun_index)
            )
        """)

        # İstisna Tarihler Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS musaitlik_istisna (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kisi_id INTEGER,
                tarih TEXT,
                aciklama TEXT
            )
        """)
        conn.commit()
        conn.close()

    # --- STANDART PERSONEL İŞLEMLERİ ---
    @staticmethod
    def get_all_personel():
        """Tüm personeli getirir."""
        query = "SELECT * FROM kisiler ORDER BY ad_soyad ASC"
        return execute_query(query)

    @staticmethod
    def search_personel(name_filter=""):
        """Personel adına göre arama yapar."""
        query = "SELECT * FROM kisiler WHERE ad_soyad LIKE ? ORDER BY ad_soyad ASC"
        return execute_query(query, (f"%{name_filter}%",))

        # app/controllers/personel_controller.py dosyasında, mevcut record_payment metodunu bununla değiştir:

        # app/controllers/personel_controller.py dosyasında, record_payment fonksiyonunu bul ve şu hale getir:

        # app/controllers/personel_controller.py dosyasında:

        # app/controllers/personel_controller.py dosyasında:

    @staticmethod
    def safely_record_payment(personel_id, amount, tarih, aciklama="Maaş Ödemesi"):
        """
        [YENİ GÜVENLİK KATMANI]
        PersonelController.add_transaction fonksiyonunu çağırır ve crash'leri yakalar.
        """
        islem_turu = 'Ödeme'
        if amount <= 0:
            return False, "Ödeme miktarı pozitif olmalıdır."

        try:
            # Kullanıcının istediği standart add_transaction fonksiyonunu çağırıyoruz
            # Bu fonksiyon, harici execute_query'yi kullanır.
            PersonelController.add_transaction(personel_id, tarih, islem_turu, amount, aciklama)
            return True, "Ödeme başarıyla kaydedildi."

        except Exception as e:
            # Eğer add_transaction/execute_query hata fırlatırsa (DB kilidi, format hatası vb.)
            print(f"VERİ KAYIT HATASI (add_transaction): {e}")
            return False, f"Ödeme işlemi başarısız oldu: {e}"
    @staticmethod
    def get_personel_detail(personel_id):
        """Tek bir personelin detayını getirir."""
        query = "SELECT * FROM kisiler WHERE id = ?"
        result = execute_query(query, (personel_id,))
        return result[0] if result else None

    @staticmethod
    def save_personel(ad, tel, rol, odeme_tipi, ucret, turne_engeli, notlar, personel_id=None):
        if personel_id:
            query = """
                UPDATE kisiler SET 
                ad_soyad=?, telefon=?, rol_tipi=?, odeme_tipi=?, standart_ucret=?, turne_engeli=?, notlar=?
                WHERE id=?
            """
            params = (ad, tel, rol, odeme_tipi, ucret, turne_engeli, notlar, personel_id)
        else:
            query = """
                INSERT INTO kisiler (ad_soyad, telefon, rol_tipi, odeme_tipi, standart_ucret, turne_engeli, notlar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (ad, tel, rol, odeme_tipi, ucret, turne_engeli, notlar)

        execute_query(query, params, commit=True)

    @staticmethod
    def delete_personel(personel_id):
        query = "DELETE FROM kisiler WHERE id = ?"
        execute_query(query, (personel_id,), commit=True)

    # --- FİNANS İŞLEMLERİ ---
    @staticmethod
    def get_finance_history(personel_id):
        query = "SELECT * FROM finans_hareketleri WHERE kisi_id = ? ORDER BY tarih DESC, id DESC"
        return execute_query(query, (personel_id,))

    @staticmethod
    def get_balance(personel_id):
        # DÜZELTME: Hem 'Borç' hem de 'Hakediş' toplanmalı.
        query_borc = """
                    SELECT SUM(miktar) as toplam 
                    FROM finans_hareketleri 
                    WHERE kisi_id = ? 
                    AND (islem_turu = 'Borç' OR islem_turu LIKE 'Hakediş%')
                """

        query_odeme = """
                    SELECT SUM(miktar) as toplam 
                    FROM finans_hareketleri 
                    WHERE kisi_id = ? 
                    AND islem_turu LIKE 'Ödeme%'
                """

        res_borc = execute_query(query_borc, (personel_id,))
        res_odeme = execute_query(query_odeme, (personel_id,))

        # KRİTİK DÜZELTME: None gelirse 0.0 yap
        toplam_borc = res_borc[0]['toplam'] if res_borc and res_borc[0]['toplam'] is not None else 0.0
        toplam_odeme = res_odeme[0]['toplam'] if res_odeme and res_odeme[0]['toplam'] is not None else 0.0

        return toplam_borc - toplam_odeme

    def get_personnel_with_balance(self):
        """Tüm personeli bakiyeleriyle birlikte getirir, borç miktarına göre sıralar ve hataları yutar."""

        try:
            # 1. Tüm personeli çek
            query = "SELECT id, ad_soyad FROM kisiler"
            all_personel = execute_query(query)

            personel_list_with_balance = []

            # 2. Herkesin bakiyesini hesapla
            for p in all_personel:
                try:
                    # Bakiye hesaplanırken oluşabilecek hataları burada yakala
                    balance = self.get_balance(p['id'])
                    personel_list_with_balance.append({
                        'id': p['id'],
                        'ad_soyad': p['ad_soyad'],
                        'bakiye': balance
                    })
                except Exception as e:
                    # Eğer bir kişinin bakiyesi hesaplanamazsa, o kişiyi atla.
                    print(f"UYARI: Personel ID {p['id']} bakiyesi hesaplanamadı ve atlandı: {e}")
                    continue

            # 3. Borç miktarına göre sırala
            personel_list_with_balance.sort(key=lambda x: x['bakiye'] or 0, reverse=True)

            return personel_list_with_balance

        except Exception as general_e:
            # En tepede oluşan KRİTİK hataları yakala ve boş liste dön
            print(f"KRİTİK HATA: Personel listesi yüklenirken beklenmedik hata: {general_e}")
            return []

    @staticmethod
    def add_transaction(personel_id, tarih, islem_turu, miktar, aciklama):
        query = """
            INSERT INTO finans_hareketleri (kisi_id, tarih, islem_turu, miktar, aciklama)
            VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (personel_id, tarih, islem_turu, miktar, aciklama), commit=True)

    # --- REPERTUVAR VE OYUN İŞLEMLERİ ---
    @staticmethod
    def get_all_games():
        query = "SELECT id, oyun_adi FROM oyunlar ORDER BY oyun_adi ASC"
        return execute_query(query)

    @staticmethod
    def get_personel_repertoire(personel_id):
        query = """
            SELECT r.id, r.oyun_id, o.oyun_adi, r.durum 
            FROM oyuncu_repertuvari r
            JOIN oyunlar o ON r.oyun_id = o.id
            WHERE r.kisi_id = ?
            ORDER BY o.oyun_adi ASC
        """
        return execute_query(query, (personel_id,))

    @staticmethod
    def add_game_to_personel(personel_id, oyun_id, durum):
        check_query = "SELECT id FROM oyuncu_repertuvari WHERE kisi_id = ? AND oyun_id = ?"
        existing = execute_query(check_query, (personel_id, oyun_id))

        if existing:
            query = "UPDATE oyuncu_repertuvari SET durum = ? WHERE id = ?"
            execute_query(query, (durum, existing[0]['id']), commit=True)
        else:
            query = "INSERT INTO oyuncu_repertuvari (kisi_id, oyun_id, durum) VALUES (?, ?, ?)"
            execute_query(query, (personel_id, oyun_id, durum), commit=True)

    @staticmethod
    def update_repertoire_status(repertuvar_id, new_status):
        query = "UPDATE oyuncu_repertuvari SET durum = ? WHERE id = ?"
        execute_query(query, (new_status, repertuvar_id), commit=True)

    @staticmethod
    def remove_game_from_personel(repertuvar_id):
        query = "DELETE FROM oyuncu_repertuvari WHERE id = ?"
        execute_query(query, (repertuvar_id,), commit=True)

    # --- TEMSİL GEÇMİŞİ ---
    @staticmethod
    def get_person_event_history(person_id):
        """Kişinin görev aldığı (Oyuncu veya Reji) tüm etkinlikleri getirir."""
        query = """
                SELECT e.tarih, e.baslangic_saati, o.oyun_adi, s.sahne_adi, ek.gorev
                FROM etkinlik_kadrosu ek
                JOIN etkinlikler e ON ek.etkinlik_id = e.id
                JOIN oyunlar o ON e.oyun_id = o.id
                JOIN sahneler s ON e.sahne_id = s.id
                WHERE ek.kisi_id = ?
                ORDER BY e.tarih DESC, e.baslangic_saati ASC
            """
        return execute_query(query, (person_id,))

    # --- MÜSAİTLİK (AVAILABILITY) - BU BÖLÜM EKSİKTİ ---
    @staticmethod
    def get_weekly_routine(person_id):
        rows = execute_query("SELECT gun_index, durum FROM musaitlik_haftalik WHERE kisi_id = ?", (person_id,))
        return {row['gun_index']: row['durum'] for row in rows}

    @staticmethod
    def save_weekly_routine(person_id, weekly_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for day_idx, status in weekly_data.items():
                cursor.execute("""
                    INSERT INTO musaitlik_haftalik (kisi_id, gun_index, durum) VALUES (?, ?, ?)
                    ON CONFLICT(kisi_id, gun_index) DO UPDATE SET durum=excluded.durum
                """, (person_id, day_idx, status))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        finally:
            conn.close()

    @staticmethod
    def get_exceptions(person_id):
        return execute_query("SELECT * FROM musaitlik_istisna WHERE kisi_id = ? ORDER BY tarih ASC", (person_id,))

    @staticmethod
    def add_exception(person_id, date_str, desc):
        execute_query("INSERT INTO musaitlik_istisna (kisi_id, tarih, aciklama) VALUES (?, ?, ?)",
                      (person_id, date_str, desc), commit=True)

    @staticmethod
    def delete_exception(exc_id):
        execute_query("DELETE FROM musaitlik_istisna WHERE id = ?", (exc_id,), commit=True)

    @staticmethod
    def check_if_person_has_event(person_id, date_str):
        """Kişinin belirtilen tarihte bir oyunu veya görevi var mı bakar."""
        query = """
                    SELECT e.tarih, o.oyun_adi 
                    FROM etkinlik_kadrosu ek
                    JOIN etkinlikler e ON ek.etkinlik_id = e.id
                    JOIN oyunlar o ON e.oyun_id = o.id
                    WHERE ek.kisi_id = ? AND e.tarih = ?
                """
        result = execute_query(query, (person_id, date_str))
        # Eğer kayıt varsa True ve oyun adını döndür, yoksa False
        if result:
            return True, result[0]['oyun_adi']
        else:
            return False, None

    @staticmethod
    def delete_transaction(trans_id):
        """Finansal işlemi ID'ye göre siler."""
        query = "DELETE FROM finans_hareketleri WHERE id = ?"
        execute_query(query, (trans_id,), commit=True)