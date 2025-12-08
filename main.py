import sys
import os
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow


def load_stylesheet(app):
    """CSS dosyasını yükler"""
    try:
        style_path = os.path.join("app", "views", "styles.qss")

        # --- DÜZELTME BURADA ---
        # encoding="utf-8" parametresini ekliyoruz:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    except FileNotFoundError:
        print("HATA: styles.qss dosyası bulunamadı!")
    except Exception as e:
        print(f"Stil Dosyası Hatası: {e}")


def main():
    app = QApplication(sys.argv)

    # Stilleri yükle
    load_stylesheet(app)

    # Ana pencereyi oluştur
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()