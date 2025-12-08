from app.core.db import execute_query


class PlayController:
    @staticmethod
    def get_all_plays():
        """Tüm oyunları isme göre sıralı getirir."""
        query = "SELECT * FROM oyunlar ORDER BY oyun_adi ASC"
        return execute_query(query)

    @staticmethod
    def get_play_detail(play_id):
        """Tek bir oyunun detayını getirir."""
        query = "SELECT * FROM oyunlar WHERE id = ?"
        result = execute_query(query, (play_id,))
        return result[0] if result else None

    @staticmethod
    def save_play(ad, yazar, sure, aktif_mi, play_id=None):
        if play_id:
            query = """
                UPDATE oyunlar SET 
                oyun_adi=?, yazar=?, varsayilan_sure=?, aktif_mi=?
                WHERE id=?
            """
            params = (ad, yazar, sure, aktif_mi, play_id)
        else:
            query = """
                INSERT INTO oyunlar (oyun_adi, yazar, varsayilan_sure, aktif_mi)
                VALUES (?, ?, ?, ?)
            """
            params = (ad, yazar, sure, aktif_mi)

        execute_query(query, params, commit=True)

    @staticmethod
    def delete_play(play_id):
        query = "DELETE FROM oyunlar WHERE id = ?"
        execute_query(query, (play_id,), commit=True)

    @staticmethod
    def get_play_cast(play_id):
        query = """
            SELECT k.ad_soyad, r.durum 
            FROM oyuncu_repertuvari r
            JOIN kisiler k ON r.kisi_id = k.id
            WHERE r.oyun_id = ?
            ORDER BY r.durum ASC, k.ad_soyad ASC
        """
        return execute_query(query, (play_id,))

    # --- YENİ FİLTRELEME FONKSİYONU ---
    @staticmethod
    def search_plays(name_filter="", status_filter="Tümü"):
        """Oyun adı ve aktiflik durumuna göre filtreler."""
        query = "SELECT * FROM oyunlar WHERE 1=1"
        params = []

        # İsim Filtresi
        if name_filter:
            query += " AND oyun_adi LIKE ?"
            params.append(f"%{name_filter}%")

        # Durum Filtresi
        if status_filter == "Aktif Oyunlar":
            query += " AND aktif_mi = 1"
        elif status_filter == "Pasif (Arşiv)":
            query += " AND aktif_mi = 0"

        # 'Tümü' seçilirse ekstra bir AND eklenmez, hepsi gelir.

        query += " ORDER BY oyun_adi ASC"

        return execute_query(query, tuple(params))