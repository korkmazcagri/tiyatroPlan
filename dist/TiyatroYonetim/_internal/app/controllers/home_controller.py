from app.core.db import execute_query, get_db_connection


class HomeController:
    # --- İSTATİSTİKLER ---
    @staticmethod
    def get_total_active_plays():
        res = execute_query("SELECT COUNT(*) as count FROM oyunlar WHERE aktif_mi = 1")
        return res[0]['count'] if res else 0

    @staticmethod
    def get_total_personel():
        res = execute_query("SELECT COUNT(*) as count FROM kisiler")
        return res[0]['count'] if res else 0

    # --- BEKLEYEN OYUNLAR LİSTESİ ---
    @staticmethod
    def get_pending_events():
        """
        Henüz 'Oynandı' olarak işaretlenmemiş oyunları ve oyuncularını getirir.
        """
        try:
            # Temel etkinlik verisi
            query = """
                    SELECT e.id, e.tarih, e.baslangic_saati, o.oyun_adi, s.sahne_adi, s.sehir, e.durum
                    FROM etkinlikler e
                    JOIN oyunlar o ON e.oyun_id = o.id
                    JOIN sahneler s ON e.sahne_id = s.id
                    WHERE (e.durum IS NULL OR e.durum != 'Oynandı')
                    ORDER BY e.tarih ASC, e.baslangic_saati ASC
                """
            rows = execute_query(query)

            # Oyuncu isimlerini ekleyerek listeyi zenginleştir
            results = []
            for row in rows:
                ev = dict(row)

                # O etkinliğin oyuncularını çek
                actors = execute_query("""
                        SELECT k.ad_soyad FROM etkinlik_kadrosu ek
                        JOIN kisiler k ON ek.kisi_id = k.id
                        WHERE ek.etkinlik_id = ? AND ek.gorev = 'Oyuncu'
                    """, (ev['id'],))

                names = [a['ad_soyad'] for a in actors]
                ev['oyuncu_listesi'] = ", ".join(names) if names else "-"

                results.append(ev)

            return results

        except Exception as e:
            print(f"Hata: {e}")
            return []
    # --- OYUN TAMAMLAMA EKRANI VERİLERİ ---
    @staticmethod
    def get_event_staff_details(event_id):
        """Etkinlikteki personeli ve varsayılan ücretlerini çeker."""
        query = """
            SELECT k.id, k.ad_soyad, ek.gorev, k.standart_ucret, k.odeme_tipi
            FROM etkinlik_kadrosu ek
            JOIN kisiler k ON ek.kisi_id = k.id
            WHERE ek.etkinlik_id = ?
            ORDER BY ek.gorev, k.ad_soyad
        """
        return execute_query(query, (event_id,))

    # --- FİNANS YANSITMA VE KAPATMA ---
    @staticmethod
    def process_play_finance(event_id, staff_payments):
        """
        Oyun tamamlandığında seçilen ücretleri finansa yansıtır ve oyunu 'Oynandı' yapar.
        Açıklama formatı: <OYUN ADI> oyununda <TARİH> <SAAT> gününde <OYNADI/REJİLİK YAPTI>
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. Etkinlik Detayını Al (Saat eklendi)
            cursor.execute("""
                    SELECT e.tarih, e.baslangic_saati, o.oyun_adi 
                    FROM etkinlikler e 
                    JOIN oyunlar o ON e.oyun_id = o.id 
                    WHERE e.id = ?
                """, (event_id,))
            event = cursor.fetchone()

            if not event: return False

            tarih = event['tarih']
            saat = event['baslangic_saati']
            oyun_adi = event['oyun_adi']

            # 2. Finans Hareketlerini Ekle
            for p_id, amount in staff_payments.items():
                if amount > 0:
                    # Kişinin o oyundaki görevini bul (Oyuncu mu, Reji mi?)
                    cursor.execute("""
                            SELECT gorev FROM etkinlik_kadrosu 
                            WHERE etkinlik_id = ? AND kisi_id = ?
                        """, (event_id, p_id))
                    role_data = cursor.fetchone()

                    # Eylemi Belirle
                    eylem = "katkı sağladı"  # Varsayılan
                    if role_data:
                        gorev = role_data['gorev']
                        if gorev == "Oyuncu":
                            eylem = "oynadı"
                        else:
                            eylem = "rejilik yaptı"

                    # İstenilen Format: <OYUN ADI> oyununda <TARİH> <SAAT> gününde <EYLEM>
                    aciklama = f"{oyun_adi} oyununda {tarih} {saat} gününde {eylem}"

                    cursor.execute("""
                            INSERT INTO finans_hareketleri (kisi_id, tarih, islem_turu, miktar, aciklama) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (p_id, tarih, "Hakediş (Oyun)", amount, aciklama))

            # 3. Etkinliği 'Oynandı' Olarak İşaretle
            try:
                cursor.execute("ALTER TABLE etkinlikler ADD COLUMN durum TEXT")
            except:
                pass

            cursor.execute("UPDATE etkinlikler SET durum = 'Oynandı' WHERE id = ?", (event_id,))

            conn.commit()
            return True

        except Exception as e:
            print(f"Hata (Process Finance): {e}")
            conn.rollback()
            return False
        finally:
            conn.close()