from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QHeaderView, QApplication, QInputDialog, QCheckBox, QDialog, QVBoxLayout, QFormLayout, QComboBox, QPushButton, QLineEdit
from PySide6.QtCore import Qt, QSize, QItemSelectionModel, QThread
from PySide6.QtGui import QShortcut, QKeySequence
import qtawesome as qta
import copy
import data_types as dt
from ui_main import Ui_MainWindow
from security import save_credentials, load_credentials
from workers import LoaderWorker, BuilderWorker
from models import FilmTableModel
from api_client import ApiWorker
import unicodedata
        
class CMSDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Odeslat do CMS")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.api_url = QLineEdit()
        self.api_url.setPlaceholderText("Vložte URL API...")
        self.input_token = QLineEdit()
        self.input_token.setPlaceholderText("Vložte Access token...")
        # self.input_token.setEchoMode(QLineEdit.EchoMode.Password) skryje token
        form_layout.addRow("API:", self.api_url)
        form_layout.addRow("Access token:", self.input_token)
        self.btn_submit = QPushButton("Odeslat")
        self.saved_credentials = load_credentials()
        
        if self.saved_credentials:
            self.api_url.setText(self.saved_credentials.get("api_url", ""))
            self.input_token.setText(self.saved_credentials.get("token", ""))
            
        self.api_url.textEdited.connect(self.input_token.clear)
        self.btn_submit.clicked.connect(self.validate_and_submit)
        layout.addLayout(form_layout)
        layout.addWidget(self.btn_submit)
        
    def validate_and_submit(self):
        if not self.api_url.text().strip() or not self.input_token.text().strip():
            QMessageBox.warning(self, "Chyba", "Chybí URL API nebo Access token.")
            return
        self.accept()
        
    def get_data(self):
        return self.api_url.text(), self.input_token.text()
        
class MainWindow(QMainWindow):
    STYLE_COLLAPSED = """
        QPushButton {background-color: transparent; border: none; color: white; text-align: center; padding: 8px;} 
        QPushButton:hover {background-color: rgba(255, 255, 255, 0.1); border-radius: 0px;}
        QPushButton:disabled {color: gray;}
    """
    STYLE_EXPANDED = """
        QPushButton {background-color: transparent; border: none; color: white; text-align: left; font-weight: bold; font-size: 14px; padding: 8px;} 
        QPushButton:hover {background-color: rgba(255, 255, 255, 0.1); border-radius: 0px;}
        QPushButton:disabled {color: gray;}
    """
    STYLE_LANG_BTN_ACTIVE = """
        QPushButton {background-color: rgba(255, 255, 255, 0.2); color: white; font-weight: bold; border-radius: 0px; padding: 10px 0px; text-align: center;}
        QPushButton:disabled {background-color: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.3);}
    """
    STYLE_LANG_BTN_INACTIVE = """
        QPushButton {background-color: transparent; color: white; font-weight: normal; border: none; padding: 10px 0px; text-align: center;}
        QPushButton:hover {background-color: rgba(255, 255, 255, 0.1);}
        QPushButton:disabled {color: rgba(255, 255, 255, 0.3);}
    """
    
    STYLE_LANG_COLLAPSED = """
            QPushButton {text-align: center; padding: 10px 0px; background-color: transparent; color: white; border: none; font-weight: bold;}
            QPushButton:hover {background-color: rgba(255, 255, 255, 0.1); border-radius: 0px;}
        """
    
    def __init__(self):
        super().__init__()
        self.films: list[dt.Film] = []
        self.category_rules: list[dt.CategoryRule] = []
        self.column_checkboxes = []
        self.current_layout: dt.LayoutResult | None = None
        self.phase1_layout: dt.LayoutResult | None = None
        self.region_layouts: dict[str, dt.LayoutResult | None] = {"cz": None, "sk": None}
        self.worker: QThread | None = None
        self.is_busy = False
        self.table_model = None
        self.current_api_url = None
        self.current_token = None
        self.current_region = "cz"
        self.ui = Ui_MainWindow()
        self.recovery_state = None
        self.ui.setupUi(self) # načte design z ui_main.py
        self.setWindowTitle("Filmana generátor rozvržení filmů")
        self.ui.tableView.verticalHeader().setVisible(False)
        self.ui.btn_menu.setIcon(qta.icon('fa5s.bars', color='white'))
        self.ui.btn_load.setIcon(qta.icon('fa5s.folder-open', color='white'))
        self.ui.btn_create.setIcon(qta.icon('fa5s.star', color='white', color_disabled='gray'))
        self.ui.btn_rebuffer.setIcon(qta.icon('fa5s.puzzle-piece', color='white', color_disabled='gray'))
        self.ui.btn_reset.setIcon(qta.icon('fa5s.sync-alt', color='white', color_disabled='gray'))
        self.ui.btn_send.setIcon(qta.icon('fa5s.cloud-upload-alt', color='white', color_disabled='gray'))
        self.ui.btn_exit.setIcon(qta.icon('fa5s.times', color='white'))
        self.ui.tableView.setStyleSheet("QHeaderView::section {font-weight: bold; font-size: 14px;}")
        self.ui.tableView.setWordWrap(True)
        self.ui.btn_cz.clicked.connect(lambda: self.switch_region("cz"))
        self.ui.btn_sk.clicked.connect(lambda: self.switch_region("sk"))
        self.ui.btn_lang_collapsed.clicked.connect(lambda: self.switch_region("sk" if self.current_region == "cz" else "cz"))
        self.ui.btn_lang_collapsed.setStyleSheet(self.STYLE_LANG_COLLAPSED)
        self.ui.btn_menu.clicked.connect(self.toggle_menu)
        self.ui.btn_load.clicked.connect(self.load_database)
        self.ui.btn_create.clicked.connect(self.create_unique_films)
        self.ui.btn_rebuffer.clicked.connect(self.fill_from_rebuffer)
        self.ui.btn_reset.clicked.connect(self.reset_table)
        self.ui.btn_send.clicked.connect(self.send_to_cms)
        self.ui.btn_exit.clicked.connect(self.close)
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.search_film)
        self.is_menu_expanded = False
        self._apply_menu_state()
        self.set_ui_busy(False) # povypíná tlačítka, protože zatím nemáme data
        
    def switch_region(self, new_region):
        if self.is_busy or self.current_region == new_region:
            return
        
        old_region = self.current_region
        self.current_region = new_region
        self._update_lang_buttons_style()
        self.ui.btn_lang_collapsed.setText(new_region.upper())
        self.statusBar().showMessage(f"Přepnuto na homepage: {new_region.upper()}", 5000)
        
        if self.current_layout:
            self.region_layouts[old_region] = copy.deepcopy(self.current_layout)
            
        if self.region_layouts.get(new_region):
            self.current_layout = copy.deepcopy(self.region_layouts[new_region])
            self.phase1_layout = copy.deepcopy(self.current_layout)
            if self.table_model and self.current_layout:
                self.table_model.update_data(self.current_layout.result_table)
            self.statusBar().showMessage(f"Obnoveno předchozí rozvržení pro {new_region.upper()}.", 5000)
            return
        
        if self.films and self.category_rules and self.region_layouts.get(old_region):
            valid_films = [f for f in self.films if new_region in f.region]
            self.current_layout = self._smart_swap_layout(self.region_layouts[old_region], valid_films, new_region)
            self.phase1_layout = copy.deepcopy(self.current_layout)
            self.region_layouts[new_region] = copy.deepcopy(self.current_layout)
            
            if self.table_model and self.current_layout:
                self.table_model.update_data(self.current_layout.result_table)
            self.statusBar().showMessage(f"Tabulka byla úspěšně upravena pro {new_region.upper()}.", 5000)
            
        elif self.films and self.category_rules:
                self.create_unique_films()
        
    def toggle_menu(self):
        self.is_menu_expanded = not self.is_menu_expanded
        self._apply_menu_state()
        
    def load_database(self):
        if self.is_busy: return
        file_name, _ = QFileDialog.getOpenFileName(self, "Vyberte soubor", "", "Excel soubory (*.xlsx)")
        if not file_name: return
        self.statusBar().showMessage("Načítám a validuji databázi, prosím čekejte...")
        self.set_ui_busy(True)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.worker = LoaderWorker(file_name)
        self.worker.finished_signal.connect(self._on_load_finished)
        self.worker.error_signal.connect(self._on_worker_error)
        self.worker.finished.connect(self._cleanup_worker)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()
                
    def create_unique_films(self):
        if self.is_busy: return
        if not self.films or not self.category_rules:
            QMessageBox.information(self, "Upozornění", "Nejdříve načtěte data z Excelu.")
            return
        
        for cb in self.column_checkboxes:
            cb.setChecked(False)
        
        valid_films = [f for f in self.films if self.current_region in f.region]
        self.statusBar().showMessage("Algoritmus hledá optimální unikátní rozvržení...")
        self.set_ui_busy(True)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.worker = BuilderWorker(phase = 1, films = valid_films, category_rules = self.category_rules)
        self.worker.finished_signal.connect(self._on_phase1_finished)
        self.worker.error_signal.connect(self._on_worker_error)
        self.worker.finished.connect(self._cleanup_worker)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()
        
    def fill_from_rebuffer(self, custom_backup = None):
        if self.is_busy: return
        
        backup_to_use = self.current_layout if self.current_layout else self.phase1_layout
        
        if not backup_to_use:
            QMessageBox.information(self, "Upozornění", "Doplňování lze spustit až po vytvoření unikátního rozvrhu.")
            return
        
        valid_films = [f for f in self.films if self.current_region in f.region]
        self.statusBar().showMessage("Doplňuji prázdná místa z rebufferu...")
        self.set_ui_busy(True)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        safe_backup = copy.deepcopy(backup_to_use)
        self.worker = BuilderWorker(phase = 2, films = valid_films, category_rules = self.category_rules, layout_backup = safe_backup)
        self.worker.finished_signal.connect(self._on_phase2_finished)
        self.worker.error_signal.connect(self._on_worker_error)
        self.worker.finished.connect(self._cleanup_worker)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()
        
    def reset_table(self):
        if self.is_busy: return
        self.current_layout = None
        self.phase1_layout = None
        self.region_layouts = {"cz": None, "sk": None}
        
        for cb in self.column_checkboxes:
            cb.setChecked(False)
        
        if self.table_model and self.category_rules:
            empty_table = [["" for _ in range(len(self.category_rules))] for _ in range(10)]
            self.table_model.update_data(empty_table)
            self.set_ui_busy(False)
            self.statusBar().showMessage("Tabulka resetována.", 5000)
        
    
    def send_to_cms(self):
        if self.is_busy: return
        if not self.phase1_layout or not self.current_layout:
            QMessageBox.warning(self, "Chyba", "Nejprve musíte vygenerovat rozvržení.")
            return
        
        selected_indices = [i for i, checkbox in enumerate(self.column_checkboxes) if checkbox.isChecked()]
        if not selected_indices:
            QMessageBox.warning(self, "Chyba", "Nejprve vyberte alespoň jednu kategorii pro odeslání.")
            return
        
        dialog = CMSDialog(self)
        if dialog.exec():
            api_url, token = dialog.get_data()
            self.current_api_url = api_url
            self.current_token = token
            
            payload = {}
            for col_index in selected_indices:
                category_name = self.category_rules[col_index].name
                film_ids = []
                for row in self.current_layout.id_table:
                    film_id = row[col_index]
                    if film_id is not None:
                        film_ids.append(film_id)
                payload[category_name] = film_ids
            
            self.statusBar().showMessage(f"Připojuji se k API a odesílám {len(selected_indices)} sekcí...", 5000)
            self.set_ui_busy(True)
            self.worker = ApiWorker(api_url, token, self.current_region, payload, self.recovery_state)
            self.worker.success.connect(self._on_api_success)
            self.worker.error.connect(self._on_worker_error)
            self.worker.token_expired.connect(self._on_token_expired)
            self.worker.finished.connect(self._cleanup_worker)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()
            
    def search_film(self):
        if not self.table_model or not self.current_layout or not self.current_layout.used_films:
            QMessageBox.information(self, "Hledání", "Není možné hledat, protože tabulka není načtena, nebo vyplněna.")
            return
            
        text, ok = QInputDialog.getText(self, "Vyhledávání", "Zadejte název filmu:")
        
        if ok and text:
            def strip_accents(s):
                return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
            
            search_query = strip_accents(text.lower().strip())
            found = False
            self.ui.tableView.clearSelection()
            
            for r in range(self.table_model.rowCount()):
                for c in range(self.table_model.columnCount()):
                    index = self.table_model.index(r, c)
                    cell_data = self.table_model.data(index)
                    
                    if cell_data:
                        clean_cell = strip_accents(str(cell_data).lower())
                        if search_query in clean_cell:
                            self.ui.tableView.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                        
                        if not found:
                            self.ui.tableView.scrollTo(index)
                            found = True
            
            if found:
                self.statusBar().showMessage(f"Hledání pro '{text}' dokončeno.", 5000)
            else:
                QMessageBox.information(self, "Hledání", f"Film '{text}' nebyl nalezen.")
                
    def set_ui_busy(self, busy: bool): # chrání aplikaci proti zběsilému klikání uživatele
        self.is_busy = busy
                
        if busy:
            self.ui.btn_load.setEnabled(False)
            self.ui.btn_create.setEnabled(False)
            self.ui.btn_rebuffer.setEnabled(False)
            self.ui.btn_reset.setEnabled(False)
            self.ui.btn_send.setEnabled(False)
            self.ui.btn_exit.setEnabled(False)
            self.ui.btn_cz.setEnabled(False)
            self.ui.btn_sk.setEnabled(False)
            self.ui.btn_lang_collapsed.setEnabled(False)
        else:
            self.ui.btn_load.setEnabled(True)
            self.ui.btn_exit.setEnabled(True)
            self.ui.btn_create.setEnabled(bool(self.films and self.category_rules))
            self.ui.btn_rebuffer.setEnabled(bool(self.phase1_layout))
            self.ui.btn_reset.setEnabled(bool(self.phase1_layout))
            self.ui.btn_send.setEnabled(bool(self.phase1_layout))
            self.ui.btn_cz.setEnabled(True)
            self.ui.btn_sk.setEnabled(True)
            self.ui.btn_lang_collapsed.setEnabled(True)
                
    def closeEvent(self, event): # Pokud aplikace zrovna pracuje na pozadí, nezavře se
        if getattr(self, "is_busy", False):
            QMessageBox.warning(self, "Probíhá výpočet", "Aplikaci nelze zavřít, dokud probíhá načítání nebo výpočet.\nProsím, vyčkejte na dokončení.")
            event.ignore()
        else:
            super().closeEvent(event)
            
    def _on_phase2_finished(self, layout_result):
        self.statusBar().clearMessage()
        self.current_layout = layout_result
        if self.current_layout is None: return
        self.region_layouts[self.current_region] = copy.deepcopy(self.current_layout)
        if self.table_model:
            self.table_model.update_data(self.current_layout.result_table)
        self.statusBar().showMessage(self.current_layout.message, 5000)
                
    def _on_worker_error(self, error_msg, state):
        self.recovery_state = state
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Chyba", error_msg)
        self.set_ui_busy(False)
        self.statusBar().showMessage("Operace selhala.", 5000)
        
    def _on_phase1_finished(self, layout_result): 
        self.statusBar().clearMessage()
        self.current_layout = layout_result
        self.phase1_layout = copy.deepcopy(self.current_layout) # Tvrdá záloha čistého výsledku pomocí (zabrání problémům se sdílenou pamětí)
        self.region_layouts[self.current_region] = copy.deepcopy(self.current_layout)
        other_region = "sk" if self.current_region == "cz" else "cz"
        self.region_layouts[other_region] = None
        if self.current_layout is None: return
        if self.table_model:
            self.table_model.update_data(self.current_layout.result_table)
        final_message = self.current_layout.message
        if self.current_layout.unassigned_films:
            unassigned_count = len(self.current_layout.unassigned_films)
            titles = ", ".join([film.title for film, _ in self.current_layout.unassigned_films])
            final_message += f" | Nezařazeno ({unassigned_count}): {titles}"
        self.statusBar().showMessage(final_message, 8000)
        
    def _cleanup_worker(self): # Vrací UI zpět do normálu po doběhnutí jakéhokoliv vlákna
        QApplication.restoreOverrideCursor()
        self.set_ui_busy(False)
        self.worker = None
            
    def _on_load_finished(self, valid_films, category_rules, ignored_films): # Spustí se, až LoaderWorker přečte Excel
        self.statusBar().clearMessage()
        self.films = valid_films
        self.category_rules = category_rules
        self.current_layout = None
        self.phase1_layout = None
        self.region_layouts = {"cz": None, "sk": None}
        headers = [rule.name for rule in self.category_rules]
        empty_table = [["" for _ in range(len(headers))] for _ in range(10)]
        
        for cb in self.column_checkboxes:
            cb.deleteLater()
        self.column_checkboxes.clear()

        for rule in self.category_rules:
            checkbox = QCheckBox()
            self.ui.checkbox_layout.addWidget(checkbox, 1, Qt.AlignmentFlag.AlignCenter)
            self.column_checkboxes.append(checkbox)
            
        self.table_model = FilmTableModel(empty_table, headers)
        self.ui.tableView.setModel(self.table_model)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.statusBar().showMessage("Databáze úspěšně načtena.", 5000)
        
        if ignored_films:
            QMessageBox.information(self, "Ignorované filmy", "Některé řádky byly ignorovány kvůli chybám:\n\n" + "\n".join(ignored_films))
            
    def _on_api_success(self, message):
        self.recovery_state = None
        self.statusBar().clearMessage()
        if self.current_api_url and self.current_token:
            save_credentials(self.current_api_url, self.current_token)
        QMessageBox.information(self, "Hotovo", message)
        
    def _on_token_expired(self):
        self.recovery_state = None
        self.statusBar().clearMessage()
        self.set_ui_busy(False)
        QMessageBox.warning(self, "Token vypršel", "Access token vypršel, zadejte nový.")
        self.send_to_cms()
            
    def _apply_menu_state(self):
        buttons = [self.ui.btn_menu, self.ui.btn_load, self.ui.btn_create, self.ui.btn_rebuffer, self.ui.btn_reset, self.ui.btn_send, self.ui.btn_exit]
                
        if self.is_menu_expanded:
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
            self.ui.btn_send.show()
            self.ui.widget_lang_expanded.show()
            self.ui.btn_lang_collapsed.hide()
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
            self.ui.btn_send.hide()
            self.ui.widget_lang_expanded.hide()
            self.ui.btn_lang_collapsed.show()
                
        self.ui.frame.setMinimumWidth(new_width)
        self.ui.frame.setMaximumWidth(new_width)
        self._update_lang_buttons_style()
        
    def _update_lang_buttons_style(self):
        if self.current_region == "cz":
            self.ui.btn_cz.setStyleSheet(self.STYLE_LANG_BTN_ACTIVE)
            self.ui.btn_sk.setStyleSheet(self.STYLE_LANG_BTN_INACTIVE)
        else:
            self.ui.btn_cz.setStyleSheet(self.STYLE_LANG_BTN_INACTIVE)
            self.ui.btn_sk.setStyleSheet(self.STYLE_LANG_BTN_ACTIVE)
    
    def _smart_swap_layout(self, layout, valid_films, new_region):
        new_layout = copy.deepcopy(layout)
        valid_ids = {f.id for f in valid_films}
        
        for r_idx in range(len(new_layout.id_table)):
            for c_idx in range(len(new_layout.id_table[r_idx])):
                f_id = new_layout.id_table[r_idx][c_idx]
                
                if f_id is not None and f_id not in valid_ids:
                    old_title = new_layout.result_table[r_idx][c_idx]
                    
                    old_title_lower = " ".join(old_title.lower().split())
                    base_title = old_title_lower
                    
                    for suffix in [" cz", "-cz", " (cz)", " sk", "-sk", " (sk)"]:
                        if base_title.endswith(suffix):
                            base_title = base_title[:-len(suffix)].strip()
   
                            if base_title.endswith("-"):
                                base_title = base_title[:-1].strip()
                            break
                            
                    target_1 = f"{base_title} {new_region}"
                    target_2 = f"{base_title} ({new_region})"
                    target_3 = f"{base_title}-{new_region}"
                    target_4 = f"{base_title} - {new_region}"
                    
                    replacement = None
                    for f in valid_films:
                        f_title_lower = " ".join(f.title.lower().split())
                        if f_title_lower in [target_1, target_2, target_3, target_4]:
                            replacement = f
                            break
                            
                    if replacement:
                        new_layout.id_table[r_idx][c_idx] = replacement.id
                        new_layout.result_table[r_idx][c_idx] = replacement.title
                        new_layout.used_films.add(replacement.id)
                    else:
                        new_layout.id_table[r_idx][c_idx] = None
                        new_layout.result_table[r_idx][c_idx] = ""
                        cat_name = self.category_rules[c_idx].name
                        new_layout.category_counts[cat_name] -= 1
                        
        new_layout.used_films = {f_id for row in new_layout.id_table for f_id in row if f_id is not None}
        return new_layout