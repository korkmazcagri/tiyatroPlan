from app.core.db import execute_query, get_db_connection

class TourController:
    @staticmethod
    def initialize_tables():
        """Tabloları oluşturur."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turne_ekipleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ekip_adi TEXT NOT NULL,
                notlar TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turne_ekip_uyeleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ekip_id INTEGER,
                kisi_id INTEGER,
                UNIQUE(ekip_id, kisi_id),
                FOREIGN KEY(ekip_id) REFERENCES turne_ekipleri(id) ON DELETE CASCADE,
                FOREIGN KEY(kisi_id) REFERENCES kisiler(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_teams():
        """Tüm ekipleri listeler. Hata aldığın yer burasıydı."""
        return execute_query("SELECT * FROM turne_ekipleri ORDER BY ekip_adi ASC")

    @staticmethod
    def save_team(name, notes, team_id=None):
        """Ekibi kaydeder veya günceller."""
        if team_id:
            # Güncelleme işlemi
            execute_query("UPDATE turne_ekipleri SET ekip_adi=?, notlar=? WHERE id=?", (name, notes, team_id),
                          commit=True)
            return team_id
        else:
            # Yeni kayıt işlemi
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO turne_ekipleri (ekip_adi, notlar) VALUES (?, ?)", (name, notes))
            new_id = cursor.lastrowid  # Yeni oluşan ID'yi alıyoruz
            conn.commit()
            conn.close()
            return new_id
    @staticmethod
    def add_member_to_team(team_id, person_id):
        """Ekibe üye ekler."""
        check = execute_query("SELECT id FROM turne_ekip_uyeleri WHERE ekip_id=? AND kisi_id=?", (team_id, person_id))
        if not check:
            execute_query("INSERT INTO turne_ekip_uyeleri (ekip_id, kisi_id) VALUES (?, ?)", (team_id, person_id), commit=True)

    @staticmethod
    def remove_member_from_team(team_id, person_id):
        """Ekipten üye çıkarır."""
        execute_query("DELETE FROM turne_ekip_uyeleri WHERE ekip_id=? AND kisi_id=?", (team_id, person_id), commit=True)

    @staticmethod
    def get_team_members(team_id):
        """Ekip üyelerini getirir."""
        query = """
            SELECT k.id, k.ad_soyad FROM turne_ekip_uyeleri teu
            JOIN kisiler k ON teu.kisi_id = k.id
            WHERE teu.ekip_id = ?
        """
        return execute_query(query, (team_id,))

    @staticmethod
    def get_team_shared_games(team_id):
        """Ekibin ortak oyunlarını getirir."""
        query = """
            SELECT DISTINCT o.id, o.oyun_adi FROM turne_ekip_uyeleri teu
            JOIN oyuncu_repertuvari r ON teu.kisi_id = r.kisi_id
            JOIN oyunlar o ON r.oyun_id = o.id
            WHERE teu.ekip_id = ? AND o.aktif_mi = 1
        """
        return execute_query(query, (team_id,))

    @staticmethod
    def delete_team(team_id):
        """Ekibi siler."""
        execute_query("DELETE FROM turne_ekipleri WHERE id=?", (team_id,), commit=True)

    @staticmethod
    def get_teams_by_game(oyun_id):
        """Bu oyunu oynayabilen (repertuvarında olan) ekipleri getirir."""
        query = """
                SELECT DISTINCT te.id, te.ekip_adi 
                FROM turne_ekipleri te
                JOIN turne_ekip_uyeleri teu ON te.id = teu.ekip_id
                JOIN oyuncu_repertuvari r ON teu.kisi_id = r.kisi_id
                WHERE r.oyun_id = ?
            """
        return execute_query(query, (oyun_id,))