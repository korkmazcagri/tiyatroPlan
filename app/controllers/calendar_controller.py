from app.core.db import execute_query, get_db_connection


class CalendarController:
    def __init__(self):
        self.initialize_tables()

    def initialize_tables(self):
        """Tabloların varlığından emin ol."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS etkinlik_kadrosu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik_id INTEGER,
                kisi_id INTEGER,
                gorev TEXT, 
                FOREIGN KEY(etkinlik_id) REFERENCES etkinlikler(id) ON DELETE CASCADE,
                FOREIGN KEY(kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()

    # --- 1. VERİ ÇEKME İŞLEMLERİ ---
    @staticmethod
    def get_events_for_month(year, month):
        month_str = f"{year}-{month:02d}"

        # --- DÜZELTME BURADA: ', s.sehir' EKLENDİ ---
        query = """
                SELECT e.id, e.tarih, e.baslangic_saati, o.id as oyun_id, o.oyun_adi, s.sahne_adi, s.sehir
                FROM etkinlikler e
                JOIN oyunlar o ON e.oyun_id = o.id
                JOIN sahneler s ON e.sahne_id = s.id
                WHERE strftime('%Y-%m', e.tarih) = ?
                ORDER BY e.tarih ASC, e.baslangic_saati ASC
            """
        # ---------------------------------------------

        rows = execute_query(query, (month_str,))

        events = []
        for row in rows:
            ev = dict(row)
            actors = execute_query("""
                    SELECT k.ad_soyad FROM etkinlik_kadrosu ek 
                    JOIN kisiler k ON ek.kisi_id = k.id 
                    WHERE ek.etkinlik_id = ? AND ek.gorev = 'Oyuncu'
                """, (ev['id'],))

            names = [a['ad_soyad'] for a in actors]
            ev['oyuncu_listesi'] = ", ".join(names) if names else "Belirlenmedi"
            events.append(ev)
        return events
    @staticmethod
    def get_event_full_detail(event_id):
        res = execute_query("SELECT * FROM etkinlikler WHERE id = ?", (event_id,))
        return res[0] if res else None

    @staticmethod
    def get_event_cast_ids(event_id, gorev_tipi):
        query = "SELECT kisi_id FROM etkinlik_kadrosu WHERE etkinlik_id = ? AND gorev = ?"
        rows = execute_query(query, (event_id, gorev_tipi))
        return [r['kisi_id'] for r in rows]

    # --- 2. KAYIT (INSERT/UPDATE) İŞLEMLERİ ---
    @staticmethod
    def add_event_with_cast(oyun_id, sahne_id, tarih, saat, notlar, oyuncu_ids, reji_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO etkinlikler (oyun_id, sahne_id, tarih, baslangic_saati, notlar) 
                VALUES (?, ?, ?, ?, ?)
            """, (oyun_id, sahne_id, tarih, saat, notlar))

            event_id = cursor.lastrowid

            for p_id in oyuncu_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, p_id, 'Oyuncu'))

            for p_id in reji_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, p_id, 'Reji'))

            conn.commit()
            print(f"✅ Etkinlik Eklendi: ID {event_id}")

        except Exception as e:
            conn.rollback()
            print(f"❌ Ekleme Hatası: {e}")
        finally:
            conn.close()

    @staticmethod
    def update_event_with_cast(event_id, oyun_id, sahne_id, tarih, saat, notlar, oyuncu_ids, reji_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE etkinlikler 
                SET oyun_id=?, sahne_id=?, tarih=?, baslangic_saati=?, notlar=? 
                WHERE id=?
            """, (oyun_id, sahne_id, tarih, saat, notlar, event_id))

            cursor.execute("DELETE FROM etkinlik_kadrosu WHERE etkinlik_id = ?", (event_id,))

            for p_id in oyuncu_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, p_id, 'Oyuncu'))

            for p_id in reji_ids:
                cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                               (event_id, p_id, 'Reji'))

            conn.commit()
            print(f"✅ Etkinlik Güncellendi: ID {event_id}")

        except Exception as e:
            conn.rollback()
            print(f"❌ Güncelleme Hatası: {e}")
        finally:
            conn.close()

    @staticmethod
    def delete_event(event_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM etkinlik_kadrosu WHERE etkinlik_id = ?", (event_id,))
            cursor.execute("DELETE FROM etkinlikler WHERE id = ?", (event_id,))
            conn.commit()
        except Exception as e:
            print(f"Silme Hatası: {e}")
        finally:
            conn.close()

    # --- 3. YARDIMCI VERİLER ---
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
    def get_cast_candidates(oyun_id, city_name="", date_str=""):
        # 1. Temel Adayları Çek (Şehir ve Oyun Uyumu)
        city_check = city_name.strip() if city_name else ""
        istanbul_vars = ["İstanbul", "Istanbul", "İSTANBUL", "ISTANBUL", "istanbul", "İst", "Ist"]
        is_istanbul = any(v in city_check for v in istanbul_vars)

        sql = """
                SELECT k.id, k.ad_soyad, r.durum, k.turne_engeli
                FROM kisiler k
                JOIN oyuncu_repertuvari r ON k.id = r.kisi_id
                WHERE r.oyun_id = ? 
            """
        # Eğer İstanbul dışıysa ve turne engeli varsa SQL'den ele (Eski Mantık)
        if not is_istanbul:
            sql += " AND k.turne_engeli = 0"

        sql += " ORDER BY k.ad_soyad ASC"

        candidates = execute_query(sql, (oyun_id,))

        # 2. Tarih Müsaitlik Kontrolü (YENİ FİLTRE)
        if not date_str:
            return candidates  # Tarih yoksa hepsini döndür

        filtered_list = []
        for row in candidates:
            p = dict(row)
            # Kişinin o tarihteki durumunu sor
            status = CalendarController.get_person_availability_status(p['id'], date_str)

            # Eğer "Müsait Değil" ise listeye ekleme!
            if status == "Müsait Değil":
                continue

            filtered_list.append(p)

        return filtered_list

    @staticmethod
    def get_crew_candidates(date_str=""):
        # 1. Tüm Personeli Çek
        candidates = execute_query("SELECT id, ad_soyad FROM kisiler ORDER BY ad_soyad ASC")

        # 2. Tarih Müsaitlik Kontrolü (YENİ FİLTRE)
        if not date_str:
            return candidates

        filtered_list = []
        for row in candidates:
            p = dict(row)
            status = CalendarController.get_person_availability_status(p['id'], date_str)

            if status == "Müsait Değil":
                continue

            filtered_list.append(p)

        return filtered_list
    @staticmethod
    def get_person_name(person_id):
        res = execute_query("SELECT ad_soyad FROM kisiler WHERE id = ?", (person_id,))
        return res[0]['ad_soyad'] if res else ""

    # =========================================================================
    # OTOMATİK DOLDURMA ALGORİTMASI (AUTO FILL) - GÜNCELLENMİŞ HALİ
    # =========================================================================
    # =========================================================================
    # OTOMATİK DOLDURMA ALGORİTMASI (DEBUG MODU)
    # =========================================================================
    @staticmethod
    def auto_fill_schedule():
        print("\n" + "=" * 50)
        print(">>> [DEBUG] auto_fill_schedule FONKSİYONU BAŞLADI")

        import random
        import traceback

        try:
            # 1. Oyuncusu ATANMAMIŞ (Boş) Etkinlikleri Çek
            print(">>> [DEBUG] Adım 1: Boş etkinlikler veritabanından çekiliyor...")

            query = """
                    SELECT e.id, e.tarih, o.id as oyun_id, o.oyun_adi, s.sehir
                    FROM etkinlikler e
                    JOIN oyunlar o ON e.oyun_id = o.id
                    JOIN sahneler s ON e.sahne_id = s.id
                    WHERE e.id NOT IN (SELECT etkinlik_id FROM etkinlik_kadrosu WHERE gorev='Oyuncu')
                    ORDER BY e.tarih ASC
                """
            empty_events = execute_query(query)

            if not empty_events:
                print(">>> [DEBUG] Sonuç: Doldurulacak boş etkinlik bulunamadı.")
                return 0, []

            print(f">>> [DEBUG] Bulunan boş etkinlik sayısı: {len(empty_events)}")

            # 2. Turne ve Yerel Oyunları Ayır
            istanbul_vars = ["İstanbul", "Istanbul", "İSTANBUL", "ISTANBUL", "istanbul", "İst", "Ist"]

            tour_events = []
            local_events = []

            for ev in empty_events:
                sehir = ev['sehir'].strip()
                is_istanbul = any(v in sehir for v in istanbul_vars)
                if is_istanbul:
                    local_events.append(ev)
                else:
                    tour_events.append(ev)

            process_order = tour_events + local_events
            print(f">>> [DEBUG] İşlem sırası: {len(tour_events)} Turne + {len(local_events)} Yerel")

            filled_count = 0
            failed_list = []

            for index, event in enumerate(process_order):
                print(f"\n>>> [DEBUG] --- Etkinlik {index + 1} İşleniyor ---")
                print(f">>> [DEBUG] Tarih: {event['tarih']}, Oyun: {event['oyun_adi']}, Şehir: {event['sehir']}")

                sehir = event['sehir'].strip()
                is_istanbul = any(v in sehir for v in istanbul_vars)

                # --- ADAY HAVUZUNU OLUŞTUR ---
                print(f">>> [DEBUG] Bu oyun ({event['oyun_id']}) için repertuvarı olanlar aranıyor...")
                candidates_query = """
                        SELECT k.id, k.ad_soyad, k.odeme_tipi, k.turne_engeli 
                        FROM kisiler k
                        JOIN oyuncu_repertuvari r ON k.id = r.kisi_id
                        WHERE r.oyun_id = ?
                    """
                all_candidates_rows = execute_query(candidates_query, (event['oyun_id'],))
                print(f">>> [DEBUG] Repertuvarında bu oyun olan kişi sayısı: {len(all_candidates_rows)}")

                valid_candidates = []

                for row in all_candidates_rows:
                    # --- DÜZELTME BURADA: Satırı sözlüğe çeviriyoruz ---
                    p = dict(row)
                    # ---------------------------------------------------

                    p_name = p['ad_soyad']

                    # KURAL 1: Turne Engeli
                    if not is_istanbul and p['turne_engeli'] == 1:
                        print(f">>> [ELENDİ] {p_name}: Turne engeli var.")
                        continue

                    # KURAL 2: Şehir Çakışması
                    if CalendarController.has_city_conflict(p['id'], event['tarih'], sehir):
                        print(f">>> [ELENDİ] {p_name}: Başka şehirde oyunu var.")
                        continue

                    # KURAL 3: Müsaitlik Durumu
                    status = CalendarController.get_person_availability_status(p['id'], event['tarih'])
                    if status == "Müsait Değil":
                        print(f">>> [ELENDİ] {p_name}: Müsait değil olarak işaretlenmiş.")
                        continue

                    # Artık 'p' bir sözlük olduğu için içine yazabiliriz
                    p['status'] = status
                    valid_candidates.append(p)
                    print(f">>> [ADAY] {p_name} listeye eklendi. Durumu: {status}")

                # --- SEÇİM MANTIĞI ---
                print(f">>> [DEBUG] Toplam geçerli aday sayısı: {len(valid_candidates)}")

                selected_person = None
                salary_types = ["Aylık Maaş", "Haftalık Maaş"]

                group_salary_stage = [c for c in valid_candidates if
                                      c['odeme_tipi'] in salary_types and c['status'] == 'Sahnede']
                group_salary_avail = [c for c in valid_candidates if
                                      c['odeme_tipi'] in salary_types and c['status'] == 'Müsait']
                group_pplay_stage = [c for c in valid_candidates if
                                     c['odeme_tipi'] not in salary_types and c['status'] == 'Sahnede']
                group_pplay_avail = [c for c in valid_candidates if
                                     c['odeme_tipi'] not in salary_types and c['status'] == 'Müsait']

                if group_salary_stage:
                    selected_person = random.choice(group_salary_stage)
                    print(">>> [SEÇİM] Maaşlı ve Sahnede grubundan seçildi.")
                elif group_salary_avail:
                    selected_person = random.choice(group_salary_avail)
                    print(">>> [SEÇİM] Maaşlı ve Müsait grubundan seçildi.")
                elif group_pplay_stage:
                    selected_person = random.choice(group_pplay_stage)
                    print(">>> [SEÇİM] Oyun Başı ve Sahnede grubundan seçildi.")
                elif group_pplay_avail:
                    selected_person = random.choice(group_pplay_avail)
                    print(">>> [SEÇİM] Oyun Başı ve Müsait grubundan seçildi.")

                if selected_person:
                    print(f">>> [ATAMA] {selected_person['ad_soyad']} seçildi. Veritabanına yazılıyor...")
                    CalendarController.assign_actor_to_event(event['id'], selected_person['id'])
                    filled_count += 1
                else:
                    print(f">>> [UYARI] Bu oyun için uygun aday bulunamadı.")
                    failed_list.append(f"{event['tarih']} - {event['oyun_adi']} ({event['sehir']})")

            print("\n>>> [DEBUG] auto_fill_schedule BAŞARIYLA TAMAMLANDI")
            print("=" * 50 + "\n")
            return filled_count, failed_list

        except Exception as e:
            print("\n" + "!" * 50)
            print(f"!!! [CRASH] KRİTİK HATA OLUŞTU: {e}")
            print("!!! HATA DETAYI (Traceback):")
            traceback.print_exc()
            print("!" * 50 + "\n")
            return 0, []
    # --- YARDIMCI FONKSİYONLAR (HEPSİ @staticmethod) ---

    @staticmethod
    def has_city_conflict(person_id, date_str, target_city):
        """Kişinin o tarihte BAŞKA bir şehirde oyunu var mı?"""
        # print(f">>> [DEBUG-Helper] City Conflict kontrolü: ID {person_id}, Tarih {date_str}")
        query = """
                SELECT s.sehir 
                FROM etkinlikler e
                JOIN sahneler s ON e.sahne_id = s.id
                JOIN etkinlik_kadrosu ek ON e.id = ek.etkinlik_id
                WHERE ek.kisi_id = ? AND e.tarih = ?
            """
        res = execute_query(query, (person_id, date_str))

        if res:
            existing_city = res[0]['sehir'].strip()
            if existing_city.lower() != target_city.lower():
                return True
        return False

    @staticmethod
    def get_person_availability_status(person_id, date_str):
        """Kişinin o tarihteki durumu: 'Müsait', 'Sahnede' veya 'Müsait Değil'."""
        # print(f">>> [DEBUG-Helper] Availability kontrolü: ID {person_id}, Tarih {date_str}")
        from datetime import datetime

        # 1. İstisna Kontrolü
        exc_query = "SELECT aciklama FROM musaitlik_istisna WHERE kisi_id = ? AND tarih = ?"
        exc_res = execute_query(exc_query, (person_id, date_str))
        if exc_res:
            return "Müsait Değil"

        # 2. Haftalık Rutin Kontrolü
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_idx = dt.weekday()  # 0: Pzt ... 6: Paz

            rout_query = "SELECT durum FROM musaitlik_haftalik WHERE kisi_id = ? AND gun_index = ?"
            rout_res = execute_query(rout_query, (person_id, day_idx))

            if rout_res:
                return rout_res[0]['durum']
        except Exception as e:
            print(f">>> [DEBUG-Helper HATA] Tarih formatı hatası olabilir: {e}")

        return "Müsait"

    @staticmethod
    def assign_actor_to_event(event_id, person_id):
        from app.core.db import get_db_connection  # Importu garantiye al
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO etkinlik_kadrosu (etkinlik_id, kisi_id, gorev) VALUES (?, ?, ?)",
                           (event_id, person_id, 'Oyuncu'))
            conn.commit()
        except Exception as e:
            print(f">>> [DEBUG-Helper HATA] Insert Hatası: {e}")
        finally:
            conn.close()


    @staticmethod
    def update_event_status(event_id, new_status):
        """Etkinliğin durumunu (Oynandı / Planlandı) günceller."""
        from app.core.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Kolon yoksa ekle (Hata almamak için)
            try:
                cursor.execute("ALTER TABLE etkinlikler ADD COLUMN durum TEXT")
            except:
                pass

            cursor.execute("UPDATE etkinlikler SET durum = ? WHERE id = ?", (new_status, event_id))
            conn.commit()
        except Exception as e:
            print(f"Status Update Error: {e}")
        finally:
            conn.close()