import sys
from PySide6.QtWidgets import QApplication
from backend import FilmProcessor
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    backend = FilmProcessor()
    window = MainWindow(backend)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()