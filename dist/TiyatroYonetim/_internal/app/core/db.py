import sqlite3
import config

def get_db_connection():
    """Veritabanına bağlanır ve bağlantı nesnesini döndürür."""
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row  # Sütunlara isimle erişmek için (row['ad'] gibi)
    return conn

def execute_query(query, params=(), commit=False):
    """
    Tek bir sorgu çalıştırmak için yardımcı fonksiyon.
    INSERT, UPDATE, DELETE için commit=True yapın.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        else:
            result = cursor.fetchall()
            conn.close()
            return result
    except Exception as e:
        print(f"Veritabanı Hatası: {e}")
        conn.close()
        return None