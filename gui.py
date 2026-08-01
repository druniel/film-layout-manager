from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout,QVBoxLayout, QPushButton, QTableView, QFileDialog

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
        self.btn_rebuffer = QPushButton("Doplňovací filmy")
        self.btn_rebuffer.setEnabled(False)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setEnabled(False)
        self.btn_exit = QPushButton("Exit")
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
        print(file_name)