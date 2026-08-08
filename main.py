import sys
from PySide6.QtWidgets import QApplication
from backend import FilmProcessor
from gui import MainWindow
import qdarktheme

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    backend = FilmProcessor()
    window = MainWindow(backend)
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()