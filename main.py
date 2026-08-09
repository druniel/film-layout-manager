import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import qdarktheme
from backend import FilmProcessor
from gui import MainWindow, get_resource_path
import ctypes

def main():
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('film_layout_manager.app.v4')
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_resource_path("img/filmana-layout-dark-tile.ico")))
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    backend = FilmProcessor()
    window = MainWindow(backend)
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()