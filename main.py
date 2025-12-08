import sys
import os
import time
import sqlite3
import shutil
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt

# Dosya yollarını düzgün yönetmek için
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)

try:
    from app.views.main_window import MainWindow
except ImportError as e:
    print(f"HATA: Modül bulunamadı. Detay: {e}")
    sys.exit(1)

DB_NAME = os.path.join(basedir, "tiyatrodb.db")


# ==========================================
# 1. MAAŞ KONTROL SİSTEMİ (TEK TEK SORAN)
# ==========================================
def check_salary_payments():
    if not os.path.exists(DB_NAME): return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = datetime.now().date()
    start_of_week_str = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    start_of_month_str = today.replace(day=1).strftime("%Y-%m-%d")
    bugun_str = today.strftime("%Y-%m-%d")

    cursor.execute("SELECT id, ad_soyad, standart_ucret, odeme_tipi FROM kisiler")
    tum_kisiler = cursor.fetchall()

    # Eksikleri önce tespit edelim (Kullanıcıyı veritabanı açıkken bekletmemek için)
    eksik_haftaliklar = []
    eksik_ayliklar = []

    for kid, ad, ucret_raw, tip_raw in tum_kisiler:
        try:
            ucret = float(str(ucret_raw).replace(',', '.').strip())
        except:
            ucret = 0

        if ucret <= 0 or not tip_raw: continue
        tip_temiz = str(tip_raw).lower()

        # HAFTALIK KONTROL
        if 'hafta' in tip_temiz:
            cursor.execute("""
                SELECT id FROM finans_hareketleri 
                WHERE kisi_id = ? AND islem_turu = 'Borç' 
                AND aciklama LIKE '%Haftalık%' AND tarih >= ? 
            """, (kid, start_of_week_str))
            if not cursor.fetchone():
                eksik_haftaliklar.append((kid, ad, ucret))

        # AYLIK KONTROL
        elif 'ay' in tip_temiz:
            cursor.execute("""
                SELECT id FROM finans_hareketleri 
                WHERE kisi_id = ? AND islem_turu = 'Borç' 
                AND aciklama LIKE '%Aylık%' AND tarih >= ? 
            """, (kid, start_of_month_str))
            if not cursor.fetchone():
                eksik_ayliklar.append((kid, ad, ucret))

    # --- KULLANICIYA TEK TEK SOR ---

    # 1. HAFTALIKLAR İÇİN DÖNGÜ
    for kid, ad, kucret in eksik_haftaliklar:
        msg_text = f"HAFTALIK MAAŞ KONTROLÜ\n\n" \
                   f"Personel: {ad}\n" \
                   f"Tutar: {kucret} TL\n\n" \
                   f"Bu hafta için ödeme kaydı bulunamadı.\n" \
                   f"Bu tutar borç olarak yansıtılsın mı?"

        reply = QMessageBox.question(None, "Maaş Onayı", msg_text, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            cursor.execute("""
                INSERT INTO finans_hareketleri (kisi_id, tarih, islem_turu, miktar, aciklama)
                VALUES (?, ?, 'Borç', ?, 'Haftalık Maaş')
            """, (kid, bugun_str, kucret))
            conn.commit()  # Her onayı anında kaydet

    # 2. AYLIKLAR İÇİN DÖNGÜ
    for kid, ad, kucret in eksik_ayliklar:
        msg_text = f"AYLIK MAAŞ KONTROLÜ\n\n" \
                   f"Personel: {ad}\n" \
                   f"Tutar: {kucret} TL\n\n" \
                   f"Bu ay için ödeme kaydı bulunamadı.\n" \
                   f"Bu tutar borç olarak yansıtılsın mı?"

        reply = QMessageBox.question(None, "Maaş Onayı", msg_text, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            cursor.execute("""
                INSERT INTO finans_hareketleri (kisi_id, tarih, islem_turu, miktar, aciklama)
                VALUES (?, ?, 'Borç', ?, 'Aylık Maaş')
            """, (kid, bugun_str, kucret))
            conn.commit()

    conn.close()


# ==========================================
# 2. DİĞER FONKSİYONLAR
# ==========================================
def perform_auto_backup():
    backup_dir = os.path.join(basedir, "backups")
    if not os.path.exists(DB_NAME): return
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
        except:
            return

    today = datetime.now()
    monday_str = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    backup_path = os.path.join(backup_dir, f"yedek_{monday_str}.db")

    if not os.path.exists(backup_path):
        try:
            shutil.copy2(DB_NAME, backup_path)
        except:
            pass


def init_db_local():
    if not os.path.exists(DB_NAME):
        temp_app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Hata", f"Veritabanı bulunamadı:\n{DB_NAME}")
        sys.exit(1)

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.close()


def load_stylesheet(app):
    try:
        style_path = os.path.join(basedir, "app", "views", "styles.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except:
        pass


# ==========================================
# 3. ANA DÖNGÜ
# ==========================================
def main():
    app = QApplication(sys.argv)

    # 1. Splash
    logo_path = os.path.join(basedir, "assets", "icon.jpg")
    pixmap = QPixmap(logo_path) if os.path.exists(logo_path) else QPixmap(500, 300)
    if not os.path.exists(logo_path): pixmap.fill(QColor("#1e1e1e"))

    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    # 2. Hazırlık
    init_db_local()
    perform_auto_backup()

    time.sleep(1)

    # 3. Maaş Kontrolü (Pencere açılmadan önce sorar)
    check_salary_payments()

    # 4. Arayüzü Başlat
    splash.showMessage("Arayüz Yükleniyor...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    app.processEvents()

    load_stylesheet(app)

    window = MainWindow()

    splash.finish(window)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()