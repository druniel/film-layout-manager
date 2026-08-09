from PySide6.QtWidgets import QMainWindow, QMessageBox,QFileDialog, QHeaderView, QApplication, QInputDialog
from PySide6.QtCore import QAbstractTableModel, Qt, QSize, QItemSelectionModel
from PySide6.QtGui import QShortcut, QKeySequence
import qtawesome as qta
from ui_main import Ui_MainWindow
from pathlib import Path
import sys

def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(getattr(sys, '_MEIPASS'))
    else:
        base_path = Path(__file__).resolve().parent
    return (base_path / relative_path).as_posix()

class FilmTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
        
    def rowCount(self, parent = None):
        return len(self._data)
    
    def columnCount(self,parent = None):
        return len(self._headers)
    
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None
    
    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            cat_name = str(self._headers[section])
            return cat_name.replace(" ", "\n")
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None
    
    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()
        

class MainWindow(QMainWindow):
    STYLE_COLLAPSED = """
        QPushButton {background-color: transparent; border: none; color: white; text-align: center; padding: 8px;} 
        QPushButton:hover {background-color: rgba(255, 255, 255, 0.1); border-radius: 5px;}
        QPushButton:disabled {color: gray;}
    """
    STYLE_EXPANDED = """
        QPushButton {background-color: transparent; border: none; color: white; text-align: left; font-weight: bold; font-size: 14px; padding: 8px;} 
        QPushButton:hover {background-color: rgba(255, 255, 255, 0.1); border-radius: 5px;}
        QPushButton:disabled {color: gray;}
    """
    
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.table_model = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Filmana generátor rozvržení filmů")
        self.is_menu_expanded = False
        self.ui.btn_load.hide()
        self.ui.btn_create.hide()
        self.ui.btn_rebuffer.hide()
        self.ui.btn_reset.hide()
        self.ui.btn_menu.setText("")
        self.ui.btn_exit.setText("")
        self.ui.tableView.setStyleSheet("QHeaderView::section {font-weight: bold; font-size: 14px;}")
        self.ui.tableView.setWordWrap(True)
        self.ui.btn_create.setEnabled(False)
        self.ui.btn_rebuffer.setEnabled(False)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_menu.clicked.connect(self.toggle_menu)
        self.ui.btn_load.clicked.connect(self.load_database)
        self.ui.btn_create.clicked.connect(self.create_unique_films)
        self.ui.btn_rebuffer.clicked.connect(self.fill_from_rebuffer)
        self.ui.btn_reset.clicked.connect(self.reset_table)
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_menu.setIcon(qta.icon('fa5s.bars', color='white'))
        self.ui.btn_load.setIcon(qta.icon('fa5s.folder-open', color='white'))
        self.ui.btn_create.setIcon(qta.icon('fa5s.star', color='white', color_disabled='gray'))
        self.ui.btn_rebuffer.setIcon(qta.icon('fa5s.puzzle-piece', color='white', color_disabled='gray'))
        self.ui.btn_reset.setIcon(qta.icon('fa5s.sync-alt', color='white', color_disabled='gray'))
        self.ui.btn_exit.setIcon(qta.icon('fa5s.times', color='white'))
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.search_film)
        for btn in [self.ui.btn_menu, self.ui.btn_load, self.ui.btn_create, self.ui.btn_rebuffer, self.ui.btn_reset, self.ui.btn_exit]:
            btn.setIconSize(QSize(30, 30))
        self.ui.frame.setStyleSheet(self.STYLE_COLLAPSED)
        
    def toggle_menu(self):
        buttons = [self.ui.btn_menu, self.ui.btn_load, self.ui.btn_create, self.ui.btn_rebuffer, self.ui.btn_reset, self.ui.btn_exit]
        
        if not self.is_menu_expanded:
            new_width = 200
            self.is_menu_expanded = True
            self.ui.frame.setStyleSheet(self.STYLE_EXPANDED)
            for btn in buttons:
                btn.setIconSize(QSize(20, 20))
            self.ui.btn_menu.setIcon(qta.icon('fa5s.chevron-left', color='white'))
            self.ui.btn_menu.setText("  Skrýt menu")
            self.ui.btn_exit.setText("  Zavřít aplikaci")
            self.ui.btn_create.show()
            self.ui.btn_load.show()
            self.ui.btn_rebuffer.show()
            self.ui.btn_reset.show()
        else:
            new_width = 50
            self.is_menu_expanded = False
            self.ui.frame.setStyleSheet(self.STYLE_COLLAPSED)
            for btn in buttons:
                btn.setIconSize(QSize(30, 30))
            self.ui.btn_menu.setIcon(qta.icon('fa5s.bars', color='white'))
            self.ui.btn_menu.setText("")
            self.ui.btn_exit.setText("")
            self.ui.btn_create.hide()
            self.ui.btn_load.hide()
            self.ui.btn_rebuffer.hide()
            self.ui.btn_reset.hide()
        
        self.ui.frame.setMinimumWidth(new_width)
        self.ui.frame.setMaximumWidth(new_width)
        
    def load_database(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Vyberte soubor", "", "Excel soubory (*.xlsx)")
        
        if not file_name:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                ignored_films = self.backend.load_data(file_name)
                self.ui.btn_create.setEnabled(True)
                self.table_model = FilmTableModel(self.backend.result_table, self.backend.categories)
                self.ui.tableView.setModel(self.table_model)
                self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                self.ui.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            finally:
                QApplication.restoreOverrideCursor()
            if ignored_films:
                QMessageBox.information(self, "Ignorované filmy", "Některé filmy byly ignorovány, protože neměly platný ID:\n" + "\n".join(ignored_films))
        except Exception as e:
            QMessageBox.critical(self, "Chyba", str(e))
            
    def create_unique_films(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                self.backend.reset()
                new_data, message = self.backend.get_carousel_data_unique()
                if self.table_model:
                    self.table_model.update_data(new_data)
                    self.statusBar().showMessage(message, 5000)
                    self.ui.btn_rebuffer.setEnabled(True)
                    self.ui.btn_reset.setEnabled(True)
            finally:
                QApplication.restoreOverrideCursor()
        except Exception as e:
            QMessageBox.critical(self, "Chyba", str(e))
        
    def fill_from_rebuffer(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                new_data, message = self.backend.get_carousel_data_additional()
                if self.table_model:
                    self.table_model.update_data(new_data)
                    self.statusBar().showMessage(message, 5000)
            finally:
                QApplication.restoreOverrideCursor()
        except Exception as e:
            QMessageBox.critical(self, "Chyba", str(e))
        
    def reset_table(self):
        self.backend.reset()
        if self.table_model:
            self.table_model.update_data(self.backend.result_table)
            self.statusBar().showMessage("Tabulka resetována.", 5000)
            self.ui.btn_rebuffer.setEnabled(False)
            self.ui.btn_reset.setEnabled(False)
            
    def search_film(self):
        if not self.table_model or not self.backend.used_films:
            QMessageBox.information(self, "Hledání", "Není možné hledat, protože tabulka není načtena, nebo vyplněna.")
            return
            
        text, ok = QInputDialog.getText(self, "Vyhledávání", "Zadejte název filmu:")
        
        if ok and text:
            search_query = text.lower().strip()
            found = False
            self.ui.tableView.clearSelection()
            
            for r in range(self.table_model.rowCount()):
                for c in range(self.table_model.columnCount()):
                    index = self.table_model.index(r, c)
                    cell_data = self.table_model.data(index)
                    
                    if cell_data and search_query in str(cell_data).lower():
                        self.ui.tableView.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                        
                        if not found:
                            self.ui.tableView.scrollTo(index)
                            found = True
            
            if found:
                self.statusBar().showMessage(f"Hledání pro '{text}' dokončeno.", 5000)
            else:
                QMessageBox.information(self, "Hledání", f"Film '{text}' nebyl nalezen.")