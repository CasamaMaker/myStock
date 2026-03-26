# addStock.py
# Lògica de la finestra per afegir i modificar components de l'estoc (myStock)
# Llegeix i escriu directament al Google Sheet definit a configuration.py

import sys
import threading
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtWidgets import QLineEdit, QTextEdit
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QIntValidator

from ui_addStock import Ui_MainWindow
from configuration import Config

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

# ---------------------------------------------------------------------------
# Helpers de ruta (igual que component_lookup.py)
# ---------------------------------------------------------------------------

def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


# ---------------------------------------------------------------------------
# Mapa UI → índex de columna (Config)
# {nom_camp_intern: índex_columna_del_Sheet}
# ---------------------------------------------------------------------------

FIELD_MAP = {
    "ID":               Config.ID,
    "ManufacturerPN":   Config.MANUFACTURER_PN,
    "Manufacturer":     Config.MANUFACTURER_NAME,
    "Category":         Config.CATEGORY,
    "Supplier":         Config.SUPPLIER,
    "SupplierPN":       Config.SUPPLIER_PN,
    "SupplierCategory": Config.SUPPLIER_CATEGORY,
    "Package":          Config.PACKAGE,
    "Description":      Config.DESCRIPTION,
    "Stock":            Config.STOCK,
    "Storage":          Config.STORAGE,
    "Datasheet":        Config.DATASHEET,
    "SupplierLink":     Config.SUPPLIER_PRODUCT,
}

# Camps obligatoris: els que Config marca com a "paràmetres obligatoris per funcionar"
MANDATORY_COLUMNS = {
    Config.ID,
    Config.MANUFACTURER_PN,
    Config.STORAGE,
    Config.CATEGORY,
    Config.SUPPLIER_PRODUCT,
}

# Nombre total de columnes del full (índex màxim + 1)
NUM_COLUMNS = max(FIELD_MAP.values()) + 1

STYLE_EMPTY  = "background-color: #FFCCCC;"
STYLE_NORMAL = ""


# ---------------------------------------------------------------------------
# Signals per comunicar el thread de fons amb la UI
# ---------------------------------------------------------------------------

class _Signals(QObject):
    load_ok    = Signal(list)   # llista de files (list[list[str]])
    load_error = Signal(str)
    save_ok    = Signal(str)    # missatge d'èxit
    save_error = Signal(str)


# ---------------------------------------------------------------------------
# Gestió del Google Sheet (equivalent a StockChecker de component_lookup.py)
# ---------------------------------------------------------------------------

class SheetManager:
    """Encapsula la connexió i les operacions sobre el Google Sheet d'estoc."""

    def __init__(self):
        self._worksheet = None
        self._data: list[list[str]] = []
        self._loaded = False

    # ── Connexió ──────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Obre la connexió al sheet. Retorna True si ha anat bé."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials as GCreds

            creds_path = resource_path(Config.GOOGLE_CREDENTIALS_JSON)
            if not creds_path.exists():
                print(f"[SheetManager] Credencials no trobades: {creds_path}")
                return False

            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds  = GCreds.from_service_account_file(str(creds_path), scopes=SCOPES)
            client = gspread.authorize(creds)
            sheet  = client.open_by_key(Config.GOOGLE_SHEET_ID)

            self._worksheet = sheet.sheet1
            self._data      = self._worksheet.get_all_values()
            self._loaded    = True
            print(f"[SheetManager] {len(self._data_rows())} files carregades.")
            return True

        except Exception as exc:
            print(f"[SheetManager] Error en connectar: {type(exc).__name__}: {exc}")
            return False

    # ── Dades ─────────────────────────────────────────────────────────────────

    def _has_header(self) -> bool:
        """La primera fila és capçalera si la cel·la de l'ID no és numèrica."""
        if not self._data:
            return False
        cell = self._data[0][Config.ID].strip()
        return not cell.lstrip("-").isdigit()

    def _data_rows(self) -> list[list[str]]:
        """Retorna les files de dades (sense la capçalera si n'hi ha)."""
        return self._data[1:] if self._has_header() else self._data

    def _sheet_row_of(self, data_index: int) -> int:
        """
        Converteix un índex de la llista de dades a número de fila del sheet
        (1-based, comptant la capçalera si existeix).
        """
        offset = 2 if self._has_header() else 1
        return data_index + offset

    # ── Consultes ─────────────────────────────────────────────────────────────

    def all_rows(self) -> list[list[str]]:
        """Retorna una còpia de les files de dades."""
        return [row[:] for row in self._data_rows()]

    def find_index(self, component_id: str) -> int:
        """
        Retorna l'índex dins de data_rows() per a l'ID donat, o -1 si no existeix.
        """
        for i, row in enumerate(self._data_rows()):
            if len(row) > Config.ID and row[Config.ID].strip() == str(component_id).strip():
                return i
        return -1

    def next_id(self) -> int:
        """Calcula el proper ID disponible (màxim + 1)."""
        rows = self._data_rows()
        if not rows:
            return 1
        ids = []
        for row in rows:
            if len(row) > Config.ID:
                try:
                    ids.append(int(row[Config.ID]))
                except ValueError:
                    pass
        return (max(ids) + 1) if ids else 1

    def adjacent_id(self, current_id: str, direction: int) -> Optional[str]:
        """
        Retorna l'ID adjacent al corrent.
        direction = -1 → anterior  |  direction = +1 → següent
        """
        try:
            current = int(current_id)
        except ValueError:
            return None

        ids = sorted(
            int(row[Config.ID])
            for row in self._data_rows()
            if len(row) > Config.ID and row[Config.ID].strip().lstrip("-").isdigit()
        )

        if direction == -1:
            candidates = [i for i in ids if i < current]
            return str(max(candidates)) if candidates else None
        else:
            candidates = [i for i in ids if i > current]
            return str(min(candidates)) if candidates else None

    # ── Escriptura ────────────────────────────────────────────────────────────

    def update_row(self, data_index: int, row_data: list[str]) -> bool:
        """Actualitza una fila existent al sheet i a la caché local."""
        if not self._loaded or self._worksheet is None:
            return False
        try:
            sheet_row  = self._sheet_row_of(data_index)
            col_end    = chr(ord("A") + len(row_data) - 1)
            cell_range = f"A{sheet_row}:{col_end}{sheet_row}"
            self._worksheet.update(cell_range, [row_data])
            raw_index  = data_index + (1 if self._has_header() else 0)
            self._data[raw_index] = row_data
            return True
        except Exception as exc:
            print(f"[SheetManager] Error update_row: {exc}")
            return False

    def append_row(self, row_data: list[str]) -> bool:
        """Afegeix una nova fila al final del sheet i a la caché local."""
        if not self._loaded or self._worksheet is None:
            return False
        try:
            self._worksheet.append_row(row_data, value_input_option="USER_ENTERED")
            self._data.append(row_data)
            return True
        except Exception as exc:
            print(f"[SheetManager] Error append_row: {exc}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# ---------------------------------------------------------------------------
# Finestra principal
# ---------------------------------------------------------------------------

class AddStockWindow(QMainWindow):
    """Finestra per afegir i modificar components de l'estoc (Google Sheets)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("myStock – Afegir / Modificar component")

        self._sheet   = SheetManager()
        self._loading = True
        self._signals = _Signals()

        # {nom_camp_intern: QlineEdit}
        self._fields: dict[str, object] = {
            "ID":               self.ui.lineEdit_Id,
            "ManufacturerPN":   self.ui.lineEdit_ManufacturerPN,
            "Manufacturer":     self.ui.lineEdit_Manufacturer,
            "Category":         self.ui.comboBox_Category,
            "Supplier":         self.ui.comboBox_Supplier,
            "SupplierPN":       self.ui.lineEdit_SupplierPN,
            "SupplierCategory": self.ui.lineEdit_SupplierCategory,
            "Package":          self.ui.lineEdit_Package,
            "Description":      self.ui.textEdit_Description,
            "Stock":            self.ui.lineEdit_Stock,
            "Storage":          self.ui.lineEdit_Storage,
            "Datasheet":        self.ui.lineEdit_Datasheet,
            "SupplierLink":     self.ui.lineEdit_SupplierLink,
        }

        # Permet només enters >= 0 (pots canviar límits)
        validator = QIntValidator(0, 999999)
        self.ui.lineEdit_Stock.setValidator(validator)

        # Connexió de signals (cross-thread → UI)
        self._signals.load_ok.connect(self._on_load_ok)
        self._signals.load_error.connect(self._on_load_error)
        self._signals.save_ok.connect(self._on_save_ok)
        self._signals.save_error.connect(self._on_save_error)

        # Connexió de botons
        self.ui.pushButton_Nou.clicked.connect(self._on_new)
        self.ui.pushButton_safe.clicked.connect(self._on_save)
        self.ui.pushButton_previous.clicked.connect(self._on_previous)
        self.ui.pushButton_next.clicked.connect(self._on_next)

        # Autocompliment quan l'usuari surt del camp ID
        self.ui.lineEdit_Id.focusOutEvent = self._id_focus_out
        self.ui.lineEdit_Id.returnPressed.connect(self._id_return_pressed)

        # Estil de camps buits
        # for widget in self._fields.values():
        #     widget.textChanged.connect(self._update_empty_style)
        for widget in self._fields.values():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._update_empty_style)

            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(self._update_empty_style)

            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._update_empty_style)
                widget.editTextChanged.connect(self._update_empty_style)

        # Obrir links
        self._enable_link_open(self.ui.lineEdit_Datasheet)
        self._enable_link_open(self.ui.lineEdit_SupplierLink)

        # Bloqueja la UI fins que el sheet estigui carregat
        self._set_ui_enabled(False)
        self._set_status("Connectant al Google Sheet…")

        threading.Thread(target=self._load_background, daemon=True).start()

    # -----------------------------------------------------------------------
    # Càrrega en background
    # -----------------------------------------------------------------------

    def _load_background(self):
        ok = self._sheet.connect()
        self._loading = False
        if ok:
            self._signals.load_ok.emit(self._sheet.all_rows())
        else:
            self._signals.load_error.emit(
                "No s'ha pogut connectar al Google Sheet.\n"
                "Comprova les credencials i la connexió a Internet."
            )

    def _on_load_ok(self, rows):
        self._set_ui_enabled(True)
        self._set_status("Sheet carregat correctament.")
        # self._on_new()
        self._populate_comboboxes(rows)
        self._on_last()

    def _on_load_error(self, msg: str):
        self._set_ui_enabled(False)
        self._set_status(f"Error: {msg}")
        self._show_error(msg)

    # def _update_empty_style(self):
    #     for name, widget in self._fields.items():
    #         if widget.text().strip() == "":
    #             widget.setStyleSheet("background-color: #ffe6e6;")  # vermell suau
    #         else:
    #             widget.setStyleSheet("")

    def _update_empty_style(self):
        for name, widget in self._fields.items():
            # Obtenir el text segons el tipus
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                text = widget.currentText().strip()
            else:
                continue

            if text == "":
                widget.setStyleSheet("background-color: #ffe6e6;")  # vermell suau
            else:
                widget.setStyleSheet("")

    def _populate_comboboxes(self, rows):
        suppliers = set()
        categories = set()

        for row in rows:
            if len(row) > Config.SUPPLIER:
                suppliers.add(row[Config.SUPPLIER].strip())
            if len(row) > Config.CATEGORY:
                categories.add(row[Config.CATEGORY].strip())

        combo_supplier = self._fields["Supplier"]
        combo_category = self._fields["Category"]

        if isinstance(combo_supplier, QComboBox):
            combo_supplier.clear()
            combo_supplier.addItems(sorted(suppliers))
            combo_supplier.setEditable(True)

        if isinstance(combo_category, QComboBox):
            combo_category.clear()
            combo_category.addItems(sorted(categories))
            combo_category.setEditable(True)

    # -----------------------------------------------------------------------
    # Camps de la UI
    # -----------------------------------------------------------------------

    # def _get_field_text(self, name: str) -> str:
    #     return self._fields[name].text().strip()
    
    def _get_field_text(self, name: str) -> str:
        widget = self._fields[name]
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        elif isinstance(widget, QComboBox):
            return widget.currentText().strip()
        return ""

    # def _set_field_text(self, name: str, value: str) -> None:
    #     self._fields[name].blockSignals(True)
    #     self._fields[name].setText(str(value))
    #     self._fields[name].setCursorPosition(0)
    #     self._fields[name].blockSignals(False)

    # def _set_field_text(self, name: str, value: str) -> None:
    #     field = self._fields[name]
    #     # field.blockSignals(True)
    #     field.setText(str(value))

    #     if isinstance(field, QLineEdit):
    #         field.setCursorPosition(0)
    #     elif isinstance(field, QTextEdit):
    #         cursor = field.textCursor()
    #         cursor.setPosition(0)
    #         field.setTextCursor(cursor)

    #     # field.blockSignals(False)

    def _set_field_text(self, name: str, value: str) -> None:
        field = self._fields[name]

        if isinstance(field, QLineEdit):
            field.setText(str(value))
            field.setCursorPosition(0)

        elif isinstance(field, QTextEdit):
            field.setPlainText(str(value))

        elif isinstance(field, QComboBox):
            index = field.findText(str(value))
            if index >= 0:
                field.setCurrentIndex(index)
            else:
                field.setCurrentText(str(value))  # opcional si és editable

    # def _clear_fields(self) -> None:
    #     for widget in self._fields.values():
    #         widget.setText("")

    def _clear_fields(self) -> None:
        for widget in self._fields.values():

            if isinstance(widget, QLineEdit):
                widget.setText("")

            elif isinstance(widget, QTextEdit):
                widget.clear()

            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(-1)  # deselecciona
                # si és editable:
                widget.setCurrentText("")

    # def _row_to_fields(self, row: list[str]) -> None:
    #     """Omple els camps de la UI a partir d'una fila del sheet."""
    #     for field_name, col_idx in FIELD_MAP.items():
    #         value = row[col_idx] if col_idx < len(row) else ""
    #         self._fields[field_name].blockSignals(True)
    #         self._fields[field_name].setText(str(value))
    #         self._fields[field_name].setCursorPosition(0)
    #         self._fields[field_name].blockSignals(False)

    # def _row_to_fields(self, row: list[str]) -> None:
    #     for field_name, col_idx in FIELD_MAP.items():
    #         value = row[col_idx] if col_idx < len(row) else ""
    #         field = self._fields[field_name]
    #         # field.blockSignals(True)
    #         field.setText(str(value))

    #         if isinstance(field, QLineEdit):
    #             field.setCursorPosition(0)
    #         elif isinstance(field, QTextEdit):
    #             cursor = field.textCursor()
    #             cursor.setPosition(0)
    #             field.setTextCursor(cursor)

    #         # field.blockSignals(False)

    def _row_to_fields(self, row: list[str]) -> None:
        for field_name, col_idx in FIELD_MAP.items():
            value = row[col_idx] if col_idx < len(row) else ""
            field = self._fields[field_name]

            if isinstance(field, QLineEdit):
                field.setText(str(value))
                field.setCursorPosition(0)

            elif isinstance(field, QTextEdit):
                field.setPlainText(str(value))
                cursor = field.textCursor()
                cursor.setPosition(0)
                field.setTextCursor(cursor)

            elif isinstance(field, QComboBox):
                text = str(value)

                index = field.findText(text)
                if index >= 0:
                    field.setCurrentIndex(index)
                else:
                    # Si no existeix, el posem (important si és editable)
                    field.addItem(text)
                    field.setCurrentText(text)

    # def _fields_to_row(self) -> list[str]:
    #     """Recull els camps de la UI i retorna una fila posicional."""
    #     row = [""] * NUM_COLUMNS
    #     for field_name, col_idx in FIELD_MAP.items():
    #         row[col_idx] = self._fields[field_name].text().strip()
    #     return row

    def _fields_to_row(self) -> list[str]:
        """Recull els camps de la UI i retorna una fila posicional."""
        row = [""] * NUM_COLUMNS
        for field_name, col_idx in FIELD_MAP.items():
            widget = self._fields[field_name]
            if isinstance(widget, QLineEdit):
                row[col_idx] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                row[col_idx] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                row[col_idx] = widget.currentText().strip()
            else:
                row[col_idx] = ""
        return row

    # -----------------------------------------------------------------------
    # Validació visual
    # -----------------------------------------------------------------------

    # def _validate_fields(self) -> bool:
    #     """
    #     Marca en vermell els camps de MANDATORY_COLUMNS que estiguin buits.
    #     MANDATORY_COLUMNS es deriva dels paràmetres obligatoris de Config:
    #     ID, STOCK, STORAGE, WEB i REFERENCE.
    #     Retorna True si tots estan omplerts.
    #     """
    #     all_ok = True
    #     for name, widget in self._fields.items():
    #         col_idx      = FIELD_MAP[name]
    #         is_mandatory = col_idx in MANDATORY_COLUMNS
    #         if is_mandatory and not widget.text().strip():
    #             widget.setStyleSheet(STYLE_EMPTY)
    #             all_ok = False
    #         else:
    #             widget.setStyleSheet(STYLE_NORMAL)
    #     return all_ok

    def _validate_fields(self) -> bool:
        all_ok = True

        for name, widget in self._fields.items():
            col_idx = FIELD_MAP[name]
            is_mandatory = col_idx in MANDATORY_COLUMNS

            # Obtenir valor
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()

            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()

            elif isinstance(widget, QComboBox):
                value = widget.currentText().strip()

            else:
                value = ""

            # Validació + estil
            if is_mandatory and not value:
                if isinstance(widget, QComboBox):
                    widget.setStyleSheet("QComboBox { background-color: #FFCCCC; }")
                else:
                    widget.setStyleSheet(STYLE_EMPTY)
                all_ok = False
            else:
                widget.setStyleSheet(STYLE_NORMAL)

        return all_ok

    def _reset_styles(self) -> None:
        for widget in self._fields.values():
            widget.setStyleSheet(STYLE_NORMAL)

    # -----------------------------------------------------------------------
    # Gestors de botons i events
    # -----------------------------------------------------------------------

    def _on_new(self) -> None:
        """Prepara la finestra per introduir un nou component."""
        if not self._sheet.is_loaded:
            return
        self._reset_styles()
        self._clear_fields()
        self._set_field_text("ID", str(self._sheet.next_id()))

    def _on_last(self) -> None:
        """Carrega el component amb l'ID més alt (últim)."""
        if not self._sheet.is_loaded:
            return

        rows = self._sheet.all_rows()
        if not rows:
            self._show_info("No hi ha components a l'estoc.")
            return

        # Trobar el row amb ID més gran
        max_id = None
        max_row = None

        for row in rows:
            if len(row) > Config.ID:
                try:
                    current_id = int(row[Config.ID])
                    if max_id is None or current_id > max_id:
                        max_id = current_id
                        max_row = row
                except ValueError:
                    continue

        if max_row:
            self._reset_styles()
            self._row_to_fields(max_row)
        else:
            self._show_warning("No s'ha pogut determinar l'últim component.")

    def _on_save(self) -> None:
        """Guarda el component actual al Google Sheet (nou o actualitzat)."""
        if not self._sheet.is_loaded:
            self._show_warning("El sheet encara no s'ha carregat. Espera un moment.")
            return

        if not self._validate_fields():
            self._show_warning(
                "Hi ha camps obligatoris buits (marcats en vermell).\n"
                "Omple'ls abans de guardar."
            )
            return

        component_id = self._get_field_text("ID")
        if not component_id:
            self._show_warning("L'ID no pot estar buit.")
            return

        row_data = self._fields_to_row()
        data_idx = self._sheet.find_index(component_id)
        is_update = data_idx >= 0

        self._set_ui_enabled(False)
        self._set_status("Desant al Google Sheet…")

        def run():
            if is_update:
                ok = self._sheet.update_row(data_idx, row_data)
            else:
                ok = self._sheet.append_row(row_data)

            action = "actualitzat" if is_update else "afegit"
            if ok:
                self._signals.save_ok.emit(f"Component {component_id} {action} correctament.")
            else:
                self._signals.save_error.emit(
                    "No s'han pogut desar les dades al Google Sheet.\n"
                    "Comprova la connexió i els permisos."
                )

        threading.Thread(target=run, daemon=True).start()

    def _on_save_ok(self, msg: str) -> None:
        self._reset_styles()
        self._set_ui_enabled(True)
        self._set_status(msg)

    def _on_save_error(self, msg: str) -> None:
        self._set_ui_enabled(True)
        self._set_status(f"Error: {msg}")
        self._show_error(msg)

    def _on_previous(self) -> None:
        """Carrega el component amb ID immediatament inferior."""
        if not self._sheet.is_loaded:
            return
        prev_id = self._sheet.adjacent_id(self._get_field_text("ID"), direction=-1)
        if prev_id is None:
            self._show_info("Ja ets al primer component.")
            return
        idx = self._sheet.find_index(prev_id)
        if idx >= 0:
            self._reset_styles()
            self._row_to_fields(self._sheet.all_rows()[idx])

    def _on_next(self) -> None:
        """Carrega el component amb ID immediatament superior."""
        if not self._sheet.is_loaded:
            return
        next_id = self._sheet.adjacent_id(self._get_field_text("ID"), direction=+1)
        if next_id is None:
            self._show_info("Ja ets al darrer component.")
            return
        idx = self._sheet.find_index(next_id)
        if idx >= 0:
            self._reset_styles()
            self._row_to_fields(self._sheet.all_rows()[idx])

    def _id_focus_out(self, event) -> None:
        """
        Quan l'usuari abandona el camp ID, autocompleix els camps
        si l'ID ja existeix al sheet.
        """
        type(self.ui.lineEdit_Id).focusOutEvent(self.ui.lineEdit_Id, event)

        if not self._sheet.is_loaded:
            return

        component_id = self._get_field_text("ID")
        if not component_id:
            return

        try:
            entered_id = int(component_id)
            next_id = self._sheet.next_id()

            if entered_id >= next_id:
                self._on_new()
                return
        except ValueError:
            return

        idx = self._sheet.find_index(component_id)
        if idx >= 0:
            self._reset_styles()
            self._row_to_fields(self._sheet.all_rows()[idx])

    def _id_return_pressed(self) -> None:
        if not self._sheet.is_loaded:
            return

        component_id = self._get_field_text("ID")
        if not component_id:
            return

        try:
            entered_id = int(component_id)
            next_id = self._sheet.next_id()

            if entered_id >= next_id:
                self._on_new()
                return
        except ValueError:
            return

        idx = self._sheet.find_index(component_id)
        if idx >= 0:
            
            self._reset_styles()
            self._row_to_fields(self._sheet.all_rows()[idx])

    def _enable_link_open(self, widget):
        def mouseDoubleClickEvent(event):
            url = widget.text().strip()
            if url:
                QDesktopServices.openUrl(QUrl(url))
        

        # def mousePressEvent(event):
        #     url = widget.text().strip()
        #     if url:
        #         QDesktopServices.openUrl(QUrl(url))

        widget.mouseDoubleClickEvent = mouseDoubleClickEvent
        # widget.mousePressEvent = mousePressEvent


    # -----------------------------------------------------------------------
    # Helpers de UI
    # -----------------------------------------------------------------------

    def _set_ui_enabled(self, enabled: bool) -> None:
        for widget in self._fields.values():
            widget.setEnabled(enabled)
        self.ui.pushButton_Nou.setEnabled(enabled)
        self.ui.pushButton_safe.setEnabled(enabled)
        self.ui.pushButton_previous.setEnabled(enabled)
        self.ui.pushButton_next.setEnabled(enabled)

    def _set_status(self, msg: str) -> None:
        self.statusBar().showMessage(msg, 3000)

    def _show_info(self, message: str) -> None:
        QMessageBox.information(self, "myStock", message)

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "myStock – Avís", message)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "myStock – Error", message)


# ---------------------------------------------------------------------------
# Punt d'entrada directe (per proves)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = AddStockWindow()
    window.show()
    sys.exit(app.exec())