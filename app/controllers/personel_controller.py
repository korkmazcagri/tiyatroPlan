from app.core.db import execute_query


class PersonelController:
    @staticmethod
    def get_all_personel():
        """Tüm personeli getirir."""
        query = "SELECT * FROM kisiler ORDER BY ad_soyad ASC"
        return execute_query(query)

    @staticmethod
    def search_personel(name_filter=""):
        """Personel adına göre arama yapar (YENİ)."""
        query = "SELECT * FROM kisiler WHERE ad_soyad LIKE ? ORDER BY ad_soyad ASC"
        return execute_query(query, (f"%{name_filter}%",))

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
        query_hakedis = "SELECT SUM(miktar) as toplam FROM finans_hareketleri WHERE kisi_id = ? AND islem_turu LIKE 'Hakediş%'"
        query_odeme = "SELECT SUM(miktar) as toplam FROM finans_hareketleri WHERE kisi_id = ? AND islem_turu LIKE 'Ödeme%'"

        res_hakedis = execute_query(query_hakedis, (personel_id,))
        res_odeme = execute_query(query_odeme, (personel_id,))

        toplam_hakedis = res_hakedis[0]['toplam'] if res_hakedis[0]['toplam'] else 0
        toplam_odeme = res_odeme[0]['toplam'] if res_odeme[0]['toplam'] else 0

        return toplam_hakedis - toplam_odeme

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