from app.core.db import execute_query


class CalendarController:
    # --- 1. AYLIK GÖRÜNÜM İÇİN ---
    @staticmethod
    def get_events_for_month(year, month):
        """Takvimi boyamak için o aydaki tüm etkinlikleri ve OYUNCULARINI çeker."""
        month_str = f"{year}-{month:02d}"

        # 1. Temel Etkinlik Bilgileri
        query = """
                SELECT e.id, e.tarih, e.baslangic_saati, o.id as oyun_id, o.oyun_adi, s.sahne_adi
                FROM etkinlikler e
                JOIN oyunlar o ON e.oyun_id = o.id
                JOIN sahneler s ON e.sahne_id = s.id
                WHERE strftime('%Y-%m', e.tarih) = ?
                ORDER BY e.tarih ASC, e.baslangic_saati ASC
            """
        rows = execute_query(query, (month_str,))

        # 2. Her etkinlik için oyuncu isimlerini bulup ekle
        events = []
        for row in rows:
            ev = dict(row)  # Sqlite Row nesnesini sözlüğe çevir (düzenleyebilmek için)

            # Oyuncuları Çek
            q_actors = """
                    SELECT k.ad_soyad 
                    FROM etkinlik_kadrosu ek
                    JOIN kisiler k ON ek.kisi_id = k.id
                    WHERE ek.etkinlik_id = ? AND ek.gorev = 'Oyuncu'
                """
            actor_res = execute_query(q_actors, (ev['id'],))

            # İsimleri virgülle birleştir (Örn: "Ali, Ayşe")
            names = [a['ad_soyad'] for a in actor_res]
            ev['oyuncu_listesi'] = ", ".join(names) if names else "Kadrosuz"

            events.append(ev)

        return events
    # --- 2. POPUP DETAY İÇİN ---
    @staticmethod
    def get_event_full_detail(event_id):
        query = "SELECT * FROM etkinlikler WHERE id = ?"
        res = execute_query(query, (event_id,))
        return res[0] if res else None

    @staticmethod
    def get_event_cast_ids(event_id, gorev_tipi):
        query = "SELECT kisi_id FROM etkinlik_kadrosu WHERE etkinlik_id = ? AND gorev = ?"
        res = execute_query(query, (event_id, gorev_tipi))
        return [row['kisi_id'] for row in res]

    # --- 3. CRUD İŞLEMLERİ ---
    @staticmethod
    def add_event_with_cast(oyun_id, sahne_id, tarih, saat, notlar, secilen_oyuncular_ids, secilen_reji_ids):
        import sqlite3
        from app.core.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, notlar) VALUES (?, ?, ?, ?, ?)",
                (oyun_id, sahne_id, tarih, saat, notlar))
            event_id = cursor.lastrowid

            for k_id in secilen_oyuncular_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, k_id, 'Oyuncu'))
            for k_id in secilen_reji_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, k_id, 'Reji'))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        finally:
            conn.close()

    @staticmethod
    def update_event_with_cast(event_id, oyun_id, sahne_id, tarih, saat, notlar, secilen_oyuncular_ids,
                               secilen_reji_ids):
        import sqlite3
        from app.core.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE etkinlikler SET oyun_id=?, sahne_id=?, tarih=?, baslangic_saati=?, notlar=? WHERE id=?",
                (oyun_id, sahne_id, tarih, saat, notlar, event_id))
            cursor.execute("DELETE FROM etkinlik_kadrosu WHERE etkinlik_id = ?", (event_id,))

            for k_id in secilen_oyuncular_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, k_id, 'Oyuncu'))
            for k_id in secilen_reji_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, k_id, 'Reji'))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        finally:
            conn.close()

    @staticmethod
    def delete_event(event_id):
        execute_query("DELETE FROM etkinlikler WHERE id = ?", (event_id,), commit=True)

    # --- 4. YARDIMCI VERİLER ---
    @staticmethod
    def get_active_plays():
        return execute_query("SELECT id, oyun_adi FROM oyunlar WHERE aktif_mi = 1 ORDER BY oyun_adi ASC")

    @staticmethod
    def get_distinct_cities():
        return execute_query("SELECT DISTINCT sehir FROM sahneler ORDER BY sehir ASC")

    @staticmethod
    def get_venues_by_city(city_name):
        return execute_query("SELECT id, sahne_adi FROM sahneler WHERE sehir = ? ORDER BY sahne_adi ASC", (city_name,))

    @staticmethod
    def get_city_of_venue(venue_id):
        res = execute_query("SELECT sehir FROM sahneler WHERE id = ?", (venue_id,))
        return res[0]['sehir'] if res else None

    @staticmethod
    def get_cast_candidates(oyun_id, city_name=""):
        """
        Oyun için uygun oyuncuları getirir.
        Şehir ismini kontrol eder:
        - Eğer 'İstanbul' ise -> Herkesi getirir.
        - Değilse -> Sadece turne engeli olmayanları (0) getirir.
        """

        # 1. Gelen şehir ismini temizle
        if city_name:
            city_check = city_name.strip()  # Boşlukları at
        else:
            city_check = ""

        # 2. İstanbul kontrolü (Kaba Kuvvet Yöntemi - Garanti Çözüm)
        # Python'un lower() fonksiyonuna güvenmiyoruz, olası tüm yazımları elle kontrol ediyoruz.
        istanbul_varyasyonlari = [
            "İstanbul", "Istanbul", "İSTANBUL", "ISTANBUL",
            "istanbul", "İstanbuL", "Ist", "İst"
        ]

        is_istanbul = False

        # Gelen şehir ismi, listemizdeki herhangi bir kelimeyi içeriyor mu?
        for varyasyon in istanbul_varyasyonlari:
            if varyasyon in city_check:
                is_istanbul = True
                break

        # 3. Sorguyu Hazırla
        sql = """
                SELECT k.id, k.ad_soyad, r.durum
                FROM kisiler k
                JOIN oyuncu_repertuvari r ON k.id = r.kisi_id
                WHERE r.oyun_id = ? 
            """

        # Eğer İstanbul DEĞİLSE, turne engeli olmayanları (0) filtrele
        if not is_istanbul:
            sql += " AND k.turne_engeli = 0"

        sql += " ORDER BY k.ad_soyad ASC"

        return execute_query(sql, (oyun_id,))
    @staticmethod
    def get_crew_candidates():
        return execute_query("SELECT id, ad_soyad FROM kisiler ORDER BY ad_soyad ASC")

    @staticmethod
    def get_person_name(person_id):
        res = execute_query("SELECT ad_soyad FROM kisiler WHERE id = ?", (person_id,))
        return res[0]['ad_soyad'] if res else ""