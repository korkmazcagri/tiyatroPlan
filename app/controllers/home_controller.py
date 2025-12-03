from app.core.db import execute_query
from datetime import date


class HomeController:
    @staticmethod
    def get_summary_stats():
        """Kartlar için özet sayıları getirir."""
        stats = {}

        # Toplam Personel
        res = execute_query("SELECT COUNT(*) as c FROM kisiler")
        stats['personel'] = res[0]['c'] if res else 0

        # Aktif Repertuvar
        res = execute_query("SELECT COUNT(*) as c FROM oyunlar WHERE aktif_mi=1")
        stats['oyunlar'] = res[0]['c'] if res else 0

        # Gelecek Etkinlikler
        today = date.today().strftime("%Y-%m-%d")
        res = execute_query("SELECT COUNT(*) as c FROM etkinlikler WHERE tarih >= ?", (today,))
        stats['etkinlikler'] = res[0]['c'] if res else 0

        return stats

    @staticmethod
    def get_upcoming_events(limit=10):
        """En yakın tarihli etkinlikleri ve KADRO BİLGİSİNİ getirir."""
        today = date.today().strftime("%Y-%m-%d")

        # 1. Etkinlikleri Çek
        query = """
            SELECT e.id, e.tarih, e.baslangic_saati, o.oyun_adi, s.sahne_adi, s.sehir
            FROM etkinlikler e
            JOIN oyunlar o ON e.oyun_id = o.id
            JOIN sahneler s ON e.sahne_id = s.id
            WHERE e.tarih >= ?
            ORDER BY e.tarih ASC, e.baslangic_saati ASC
            LIMIT ?
        """
        events = execute_query(query, (today, limit))

        # SQL'den gelen veriyi düzenlenebilir hale getirmek için listeye çevir (row factory yüzünden)
        event_list = [dict(row) for row in events]

        # 2. Her etkinlik için Kadroyu Bul ve String'e çevir
        for ev in event_list:
            ev['oyuncular'] = HomeController._get_names_string(ev['id'], 'Oyuncu')
            ev['reji'] = HomeController._get_names_string(ev['id'], 'Reji')

        return event_list

    @staticmethod
    def _get_names_string(event_id, gorev):
        """Yardımcı Fonksiyon: ID'ye göre isimleri virgülle birleştirir."""
        query = """
            SELECT k.ad_soyad 
            FROM etkinlik_kadrosu ek
            JOIN kisiler k ON ek.kisi_id = k.id
            WHERE ek.etkinlik_id = ? AND ek.gorev = ?
        """
        res = execute_query(query, (event_id, gorev))

        if not res:
            return "-"

        names = [row['ad_soyad'] for row in res]
        return ", ".join(names)