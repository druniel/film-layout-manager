from PySide6.QtCore import QAbstractTableModel,Qt

class FilmTableModel(QAbstractTableModel): # PŘEKLADATEL propojující surová data s vizuální tabulkou
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
        
    def rowCount(self, parent = None):
        return len(self._data)
    
    def columnCount(self,parent = None):
        return len(self._headers)
    
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole): # při volání funkce bez specifikování toho, co chci, automaticky předpokládá, že chci displayrole
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