from app.core.db import execute_query


class VenueController:
    @staticmethod
    def get_all_venues():
        """Tüm sahneleri getirir (Varsayılan)."""
        query = "SELECT * FROM sahneler ORDER BY sahne_adi ASC"
        return execute_query(query)

    @staticmethod
    def get_venue_detail(venue_id):
        """Tek bir sahnenin detayını getirir."""
        query = "SELECT * FROM sahneler WHERE id = ?"
        result = execute_query(query, (venue_id,))
        return result[0] if result else None

    @staticmethod
    def save_venue(ad, sehir, adres, kapasite, yetkili, iletisim, venue_id=None):
        if venue_id:
            query = """
                UPDATE sahneler SET 
                sahne_adi=?, sehir=?, adres=?, kapasite=?, yetkili_kisi=?, iletisim=?
                WHERE id=?
            """
            params = (ad, sehir, adres, kapasite, yetkili, iletisim, venue_id)
        else:
            query = """
                INSERT INTO sahneler (sahne_adi, sehir, adres, kapasite, yetkili_kisi, iletisim)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (ad, sehir, adres, kapasite, yetkili, iletisim)

        execute_query(query, params, commit=True)

    @staticmethod
    def delete_venue(venue_id):
        query = "DELETE FROM sahneler WHERE id = ?"
        execute_query(query, (venue_id,), commit=True)

    # --- FİLTRELEME İÇİN YENİ FONKSİYONLAR ---
    @staticmethod
    def get_distinct_cities():
        """Sadece kayıtlı sahnelerin olduğu şehirleri getirir (Filtre kutusu için)."""
        query = "SELECT DISTINCT sehir FROM sahneler ORDER BY sehir ASC"
        return execute_query(query)

    @staticmethod
    def search_venues(city_filter=None, name_filter=""):
        """Şehir ve İsme göre arama yapar."""
        query = "SELECT * FROM sahneler WHERE 1=1"
        params = []

        # Eğer şehir seçiliyse ve 'Tümü' değilse
        if city_filter and city_filter != "Tümü":
            query += " AND sehir = ?"
            params.append(city_filter)

        # İsim filtresi varsa (LIKE kullanılır)
        if name_filter:
            query += " AND sahne_adi LIKE ?"
            params.append(f"%{name_filter}%")  # İçinde geçenleri bulur

        query += " ORDER BY sahne_adi ASC"

        return execute_query(query, tuple(params))