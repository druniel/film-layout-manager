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
    
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole): # při volání funkce bez specifikování toho, co chci, automaticky předpokládá, že chci displayrole; tuhle metodu volá gui a ptá se na každou buňku co a jak vykreslit; index je objekt nesoucí mimojiné souřadnice a role je číslo konkrétního dotazu
        if not index.isValid(): # pokud se zeptá na souřadnice, který neexistují, vrátí se none a aplikace nespadne
            return None
        if role == Qt.ItemDataRole.DisplayRole: # jaký text v buňce zobrazit
            return self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.TextAlignmentRole: # jak text zarovnat
            return Qt.AlignmentFlag.AlignCenter
        return None # gui se ptá i na spoustu dalších otázek, třeba na pozadí apod., metoda odpoví none a gui použije výchozí systémové nastavení
    
    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole): # section je číslo/index sloupce, orientation je osa a role opět dotaz/vlastnost vyjádřená číslem
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