from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout,QVBoxLayout, QPushButton, QTableView, QFileDialog, QMessageBox
from PySide6.QtCore import QAbstractTableModel, Qt

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
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None
    
    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
        return None
    
    def update_data(self, new_data):
        self._data = new_data
        self.layoutChanged.emit()
        

class MainWindow(QMainWindow):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.mainwidget = QWidget()
        self.setCentralWidget(self.mainwidget)
        self.horizontal_layout = QHBoxLayout()
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(200)
        self.horizontal_layout.addWidget(self.left_panel)
        self.mainwidget.setLayout(self.horizontal_layout)
        self.left_vertical_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_vertical_layout)
        self.btn_menu = QPushButton("☰")
        self.btn_load = QPushButton("Načíst databázi")
        self.btn_load.clicked.connect(self.load_database)
        self.btn_create = QPushButton("Unikátní filmy")
        self.btn_create.setEnabled(False)
        self.btn_create.clicked.connect(self.create_unique_films)
        self.btn_rebuffer = QPushButton("Doplňovací filmy")
        self.btn_rebuffer.setEnabled(False)
        self.btn_rebuffer.clicked.connect(self.fill_from_rebuffer)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setEnabled(False)
        self.btn_reset.clicked.connect(self.reset_table)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        self.left_vertical_layout.addWidget(self.btn_menu)
        self.left_vertical_layout.addWidget(self.btn_load)
        self.left_vertical_layout.addWidget(self.btn_create)
        self.left_vertical_layout.addWidget(self.btn_rebuffer)
        self.left_vertical_layout.addWidget(self.btn_reset)
        self.left_vertical_layout.addStretch()
        self.left_vertical_layout.addWidget(self.btn_exit)
        self.table_view = QTableView()
        self.horizontal_layout.addWidget(self.table_view)
        
    def load_database(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Vyberte soubor", "", "Excel soubory (*.xlsx)")
        if file_name:
            self.backend.load_data(file_name)
            self.btn_create.setEnabled(True)
            self.btn_rebuffer.setEnabled(True)
            self.btn_reset.setEnabled(True)
            self.table_model = FilmTableModel(self.backend.result_table, self.backend.categories)
            self.table_view.setModel(self.table_model)
            
    def create_unique_films(self):
        try:
            new_data, message = self.backend.get_carousel_data_unique()
            self.table_model.update_data(new_data)
            self.statusBar().showMessage(message, 5000)
        except Exception as e:
            QMessageBox.critical(self, "Chyba", str(e))
        
    def fill_from_rebuffer(self):
        try:
            new_data, message = self.backend.get_carousel_data_additional()
            self.table_model.update_data(new_data)
            self.statusBar().showMessage(message, 5000)
        except Exception as e:
            QMessageBox.critical(self, "Chyba", str(e))
        
    def reset_table(self):
        self.backend.reset()
        self.table_model.update_data(self.backend.result_table)