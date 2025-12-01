import os

# --- Uygulama Ayarları ---
APP_NAME = "Pray Tiyatro Yönetim Sistemi"
VERSION = "1.0.0"

# Pencere Boyutları
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768

# Veritabanı Yolu
DB_NAME = "tiyatrodb.db"

# --- Renk Paleti (Sarı - Siyah / Gold & Dark) ---
# Tasarımda bu değişkenleri kullanacağız.

# Arka Planlar
COLOR_BACKGROUND = "#121212"       # Ana zemin (Koyu Siyah)
COLOR_SIDEBAR = "#1e1e1e"          # Yan menü
COLOR_CARD = "#252525"             # Kutular/Kartlar
COLOR_INPUT_BG = "#2c2c2c"         # Yazı yazma alanları

# Yazılar
COLOR_TEXT_PRIMARY = "#ffffff"     # Ana başlıklar
COLOR_TEXT_SECONDARY = "#b0b0b0"   # Açıklamalar

# Vurgu (Gold / Sarı)
COLOR_ACCENT = "#FFD700"           # Altın Sarısı (Butonlar, Seçili Alanlar)
COLOR_ACCENT_HOVER = "#e6c200"     # Üzerine gelince koyu sarı
COLOR_ACCENT_TEXT = "#000000"      # Sarı üzerindeki yazı rengi

# Durum Renkleri
COLOR_SUCCESS = "#2ecc71"          # Yeşil
COLOR_DANGER = "#e74c3c"           # Kırmızı
COLOR_WARNING = "#f39c12"          # Turuncu

# Font Ayarları
FONT_FAMILY = "Segoe UI"           # Windows için modern font
FONT_SIZE_TITLE = "16pt"
FONT_SIZE_NORMAL = "10pt"