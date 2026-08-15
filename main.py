import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import qdarktheme
from gui import MainWindow, get_resource_path

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_resource_path("img/filmana-layout-dark-tile.ico")))
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()