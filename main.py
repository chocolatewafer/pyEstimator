from gui import ProductScraperApp
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductScraperApp()
    window.show()
    sys.exit(app.exec())