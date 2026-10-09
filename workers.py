from PySide6.QtCore import QThread, Signal
import data_types as dt

class LoaderWorker(QThread):
    finished_signal = Signal(list, list, list) # vrací: valid_films, category_rules, ignored_films
    error_signal = Signal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            import loader
            valid_films, category_rules, ignored_films = loader.load_database(self.file_path)
            self.finished_signal.emit(valid_films, category_rules, ignored_films)
        except Exception as e:
            self.error_signal.emit(str(e))
            
class BuilderWorker(QThread):
    finished_signal = Signal(object) # vrací hotový dt.LayoutResult
    error_signal = Signal(str)
    
    def __init__(self, phase: int, films: list[dt.Film], category_rules: list[dt.CategoryRule], layout_backup: dt.LayoutResult | None = None):
        super().__init__()
        self.phase = phase
        self.films = films
        self.category_rules = category_rules
        self.layout_backup = layout_backup # Záloha tabulky potřebná pro Fázi 2
        self.is_smart_switch = False
        
    def run(self):
        try:
            import builder
            if self.phase == 1:
                result = builder.generate_layout(self.films, self.category_rules)
            else:
                if self.layout_backup is None:
                    raise ValueError("Kritická chyba: Chybí záloha rozvržení pro doplňování rebufferu.")
                result = builder.refill_empty_slots(self.layout_backup, self.films, self.category_rules)
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))