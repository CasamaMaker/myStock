
"""
nowstock_app.py
===============
App d'escriptori PySide6 per importar albarans LCSC al Google Sheet d'estoc.

Flux:
  FASE A (Preview) — connecta, llegeix sheet+albarà, consulta API, mostra taula
  Revisió          — usuari revisa taula lliurement (copia, cerca lookup, filtra)
  Confirmació      — botó "Aplicar canvis" → backup → escriure
  FASE B (Commit)  — backup del sheet original → escriure canvis

Requisits:
    pip install PySide6 gspread google-auth

Ús:
    python nowstock_app.py
"""

import os
import sys
import csv
import datetime
import threading
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
    QGroupBox, QFrame, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QStyledItemDelegate, QComboBox,
    QCompleter, QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Qt, QThread, QObject, Signal, QSortFilterProxyModel, QStringListModel
from PySide6.QtGui import QTextCursor, QColor, QBrush, QGuiApplication

# ── Ruta del projecte ──────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

try:
    from configuration import Config
    from request_lcsc import get_lcsc_data
    import gspread
    from google.oauth2.service_account import Credentials
    DEPS_OK = True
    _MISSING = ""
except ImportError as _e:
    DEPS_OK = False
    _MISSING = str(_e)

    class Config:
        GOOGLE_SHEET_ID         = "(no disponible)"
        GOOGLE_CREDENTIALS_JSON = "(no disponible)"
        BACKUP_FOLDER           = str(Path.home() / "Downloads")
        SUPPLIER_PRODUCT        = 12
        ID = 0; MANUFACTURER_PN = 1; MANUFACTURER_NAME = 2
        CATEGORY = 3; SUPPLIER = 4; SUPPLIER_PN = 5
        SUPPLIER_CATEGORY = 6; PACKAGE = 7; DESCRIPTION = 8
        STOCK = 9; STORAGE = 10; DATASHEET = 11

# ── Component Lookup (import opcional) ────────────────────────────────────────
try:
    from component_lookup import MainWindow as LookupWindow
    _LOOKUP_AVAILABLE = True
except Exception:
    _LOOKUP_AVAILABLE = False
    LookupWindow = None


# =============================================================================
#  PALETA
# =============================================================================

ROW_BG = {
    "NOU":      "#e8f5e9",
    "EXISTENT": "#e3f2fd",
    "WARN":     "#fff8e1",
    "ERROR":    "#ffebee",
}
ACTION_FG = {
    "NOU":      "#2e7d32",
    "EXISTENT": "#1565c0",
    "WARN":     "#e65100",
    "ERROR":    "#c62828",
}
ACTION_LABEL = {
    "NOU":      "NOU",
    "EXISTENT": "EXISTENT",
    "WARN":     "AVIS",
    "ERROR":    "ERROR",
}
PHASE_FG = {
    "info":  "#555555",
    "ok":    "#107c10",
    "warn":  "#9a5a00",
    "error": "#c42b1c",
    "head":  "#0078d4",
}

# =============================================================================
#  COLUMNES DE LA TAULA
# =============================================================================

_COLS = [
    "ID", "LCSC Part", "Accio", "MPN", "Fabricant", "Categoria", "Storage",
    "Estoc ant.", "Afegit", "Total",
    "Descripcio", "Datasheet", "Botiga",
]
_COL_IDX = {name: i for i, name in enumerate(_COLS)}
_COL_WIDTHS = {
    "ID":          50,
    "LCSC Part":  104,
    "Accio":       82,
    "MPN":        155,
    "Fabricant":  128,
    "Categoria":  110,
    "Storage":    100,
    "Estoc ant.":  70,
    "Afegit":      58,
    "Total":       56,
    "Descripcio":  72,
    "Datasheet":   72,
    "Botiga":      62,
}

# =============================================================================
#  ESTIL
# =============================================================================

APP_STYLE = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #1a1a1a;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 0px;
    padding: 10px;
}
QGroupBox::title { color: transparent; }
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 5px 8px;
    color: #1a1a1a;
}
QLineEdit:focus { border-color: #0078d4; }
QLineEdit:disabled, QLineEdit[readOnly="true"] {
    background-color: #f5f5f5; color: #888888; border-color: #d0d0d0;
}
QPushButton {
    background-color: #e1e1e1;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 5px 16px;
    color: #1a1a1a;
    font-size: 13px;
}
QPushButton:hover   { background-color: #cce4f7; border-color: #0078d4; }
QPushButton:pressed { background-color: #bbd3e9; }
QPushButton:disabled { background-color: #f0f0f0; color: #a0a0a0; border-color: #d0d0d0; }

QPushButton#btn_run {
    background-color: #0078d4; border: 1px solid #006cbe;
    color: #ffffff; font-weight: 600; padding: 6px 24px;
}
QPushButton#btn_run:hover   { background-color: #106ebe; }
QPushButton#btn_run:pressed { background-color: #005a9e; }
QPushButton#btn_run:disabled { background-color: #cccccc; border-color: #bbbbbb; color: #888888; }

QPushButton#btn_run[commit="true"] {
    background-color: #107c10; border: 1px solid #0b5e0b; color: #ffffff; font-weight: 600;
}
QPushButton#btn_run[commit="true"]:hover   { background-color: #0e6b0e; }
QPushButton#btn_run[commit="true"]:pressed { background-color: #0a560a; }
QPushButton#btn_run[commit="true"]:disabled { background-color: #cccccc; border-color: #bbbbbb; color: #888888; }

QPushButton#btn_cancel {
    background-color: #e1e1e1; border: 1px solid #ababab; color: #c42b1c;
}
QPushButton#btn_cancel:hover { background-color: #fde7e9; border-color: #c42b1c; }
QPushButton#btn_cancel:disabled { color: #a0a0a0; background-color: #f0f0f0; border-color: #d0d0d0; }

QPushButton#btn_lookup {
    background-color: #ebebeb; border: 1px solid #ababab; color: #1a1a1a;
    padding: 3px 12px; font-size: 12px;
}
QPushButton#btn_lookup:hover   { background-color: #cce4f7; border-color: #0078d4; }
QPushButton#btn_lookup:disabled { color: #a0a0a0; background-color: #f0f0f0; }

QTableWidget {
    background-color: #ffffff; border: 1px solid #d0d0d0;
    gridline-color: #eeeeee; font-size: 12px;
    selection-background-color: #cce4f7; selection-color: #1a1a1a; outline: none;
}
QTableWidget::item { padding: 3px 8px; border: none; }
QHeaderView::section {
    background-color: #f0f0f0; border: none;
    border-right: 1px solid #d8d8d8; border-bottom: 1px solid #c0c0c0;
    padding: 5px 8px; font-weight: 600; font-size: 11px; color: #444444;
}
QTextEdit#phase_log {
    background-color: #fafafa; border: 1px solid #e0e0e0; color: #555555;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 11px; padding: 4px 6px;
}
QProgressBar {
    background-color: #e1e1e1; border: 1px solid #ababab;
    border-radius: 0px; height: 8px; color: transparent;
}
QProgressBar::chunk { background-color: #0078d4; }
QLabel#lbl_title   { font-size: 15px; font-weight: 600; color: #1a1a1a; }
QLabel#lbl_section { font-size: 12px; font-weight: 600; color: #444444; }
QLabel#lbl_status  { font-size: 12px; color: #555555; }
"""


# =============================================================================
#  WORKER
# =============================================================================

class ImportWorker(QObject):
    phase_log         = Signal(str, str)
    component_result  = Signal(dict)
    progress          = Signal(int)
    preview_done      = Signal(dict)
    categories_loaded = Signal(list)   # categories existents al sheet
    storage_loaded    = Signal(list)   # valors de Storage existents al sheet
    finished          = Signal(bool, str)

    def __init__(self, bom_file: str):
        super().__init__()
        self.bom_file               = bom_file
        self._abort                 = False
        self._confirm_event         = threading.Event()
        self._confirmed             = False
        self._data_rows             = []
        self._stock_by_lcsc         = {}
        self._category_overrides: dict = {}
        self._storage_overrides:  dict = {}

    def abort(self):
        self._abort = True
        self._confirm_event.set()

    def confirm(self, yes: bool):
        self._confirmed = yes
        self._confirm_event.set()

    def apply_category_overrides(self, overrides: dict):
        self._category_overrides = overrides

    def apply_storage_overrides(self, overrides: dict):
        self._storage_overrides = overrides

    def _log(self, m, t="info"): self.phase_log.emit(m, t)
    def _ok(self, m):            self.phase_log.emit(m, "ok")
    def _warn(self, m):          self.phase_log.emit(m, "warn")
    def _err(self, m):           self.phase_log.emit(m, "error")
    def _head(self, m):          self.phase_log.emit(m, "head")

    GSCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def _creds_path(self):
        p = Path(Config.GOOGLE_CREDENTIALS_JSON)
        return p if p.is_absolute() else PROJECT_DIR / p

    def _get_client(self):
        cp = self._creds_path()
        if not cp.exists():
            raise FileNotFoundError(f"Credencials no trobades: {cp}")
        creds = Credentials.from_service_account_file(str(cp), scopes=self.GSCOPES)
        return gspread.authorize(creds)

    def _fetch_rows(self, client):
        rows = client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1.get_all_values()
        self._ok(f"Sheet llegit: {len(rows)} files")
        return rows

    def _backup_csv(self, original_rows: list) -> str:
        folder = getattr(Config, "BACKUP_FOLDER", str(Path.home() / "Downloads"))
        os.makedirs(folder, exist_ok=True)
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(folder, f"backup_stock_{ts}.csv")
        with open(fname, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(original_rows)
        size = os.path.getsize(fname) / 1024
        self._ok(f"Backup desat: {fname}  ({len(original_rows)} files, {size:.1f} KB)")
        return fname

    def _write_rows(self, client, rows: list):
        ws = client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1
        ws.clear()
        ws.update(rows, value_input_option="USER_ENTERED")
        self._ok(f"Sheet actualitzat: {len(rows)} files escrites")

    def _read_bom(self, filepath: str) -> list:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            sample = f.read(4096)
        sep = "\t" if sample.count("\t") > sample.count(",") else ","
        rows = []
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=sep):
                clean = {k.strip(): v.strip() for k, v in r.items() if k}
                if clean.get("LCSC Part Number"):
                    rows.append(clean)
        self._ok(f"Albara llegit: {len(rows)} components  (sep={'TAB' if sep == chr(9) else 'COMA'})")
        return rows

    @staticmethod
    def _next_id(data_rows: list) -> int:
        ids = []
        for row in data_rows:
            try:
                ids.append(int(str(row[Config.ID]).strip()))
            except (ValueError, IndexError):
                pass
        return max(ids, default=0) + 1

    def _build_new_row(self, new_id, lcsc_part, bom_row, api) -> list:
        tc  = Config.SUPPLIER_PRODUCT + 1
        row = [""] * tc
        try:
            qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
        except ValueError:
            qty = 0
        row[Config.ID]                = new_id
        row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
        row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
        # row[Config.CATEGORY]          = api.get("type2", "")
        row[Config.SUPPLIER]          = "LCSC"
        row[Config.SUPPLIER_PN]       = lcsc_part
        row[Config.SUPPLIER_CATEGORY] = api.get("type2", "")
        row[Config.PACKAGE]           = api.get("package")      or bom_row.get("Package", "")
        row[Config.DESCRIPTION]       = api.get("description")  or bom_row.get("Description", "")
        row[Config.STOCK]             = qty
        row[Config.STORAGE]           = ""
        row[Config.DATASHEET]         = api.get("datasheet", "")
        row[Config.SUPPLIER_PRODUCT]  = api.get("store", f"https://www.lcsc.com/product-detail/{lcsc_part}.html")
        return row

    def _fill_empty(self, row: list, api: dict) -> tuple:
        tc = Config.SUPPLIER_PRODUCT + 1
        fill_map = {
            Config.MANUFACTURER_PN:   api.get("name", ""),
            Config.MANUFACTURER_NAME: api.get("manufacturer", ""),
            # Config.CATEGORY:          api.get("type2", ""),
            Config.SUPPLIER_CATEGORY: api.get("type2", ""),
            Config.PACKAGE:           api.get("package", ""),
            Config.DESCRIPTION:       api.get("description", ""),
            Config.DATASHEET:         api.get("datasheet", ""),
            Config.SUPPLIER_PRODUCT:  api.get("store", ""),
        }
        while len(row) < tc:
            row.append("")
        filled = 0
        for col_i, val in fill_map.items():
            if val and not str(row[col_i]).strip():
                row[col_i] = val
                filled += 1
        return row, filled

    def run(self):
        if not DEPS_OK:
            self._err(f"Falten dependencies: {_MISSING}")
            self.finished.emit(False, "Dependencies no installades.")
            return
        try:
            tc = Config.SUPPLIER_PRODUCT + 1

            # ══ FASE A — PREVISUALITZACIO ══════════════════════════════════════
            self._head("FASE A - Previsualitzacio")
            self.progress.emit(5)

            client = self._get_client()
            self._ok("Client Google autenticat")
            self.progress.emit(10)

            all_rows      = self._fetch_rows(client)
            original_rows = [list(r) for r in all_rows]
            header_row    = all_rows[0] if all_rows else []
            data_rows     = [list(r) for r in all_rows[1:]]
            self._data_rows = data_rows
            self._log(f"Components al stock actual: {len(data_rows)}")
            self.progress.emit(15)

            # Categories existents al sheet
            existing_cats = sorted({
                str(r[Config.CATEGORY]).strip()
                for r in data_rows
                if len(r) > Config.CATEGORY and str(r[Config.CATEGORY]).strip()
            })
            self.categories_loaded.emit(existing_cats)

            # Valors Storage existents al sheet
            existing_storage = sorted({
                str(r[Config.STORAGE]).strip()
                for r in data_rows
                if len(r) > Config.STORAGE and str(r[Config.STORAGE]).strip()
            })
            self.storage_loaded.emit(existing_storage)

            bom_components = self._read_bom(self.bom_file)
            self._log(f"Components a importar: {len(bom_components)}")
            self.progress.emit(22)

            stock_by_lcsc = {}
            for i, row in enumerate(data_rows):
                if len(row) > Config.SUPPLIER_PN:
                    part = str(row[Config.SUPPLIER_PN]).strip()
                    if part:
                        stock_by_lcsc[part] = i
            self._stock_by_lcsc = stock_by_lcsc

            stats   = {"nous": 0, "existents": 0, "avisos": 0, "errors": 0}
            next_id = self._next_id(data_rows)
            total   = len(bom_components)

            for idx_bom, bom_row in enumerate(bom_components):
                if self._abort:
                    self.finished.emit(False, "Cancel·lat per l'usuari.")
                    return

                lcsc_part = bom_row.get("LCSC Part Number", "").strip()
                if not lcsc_part:
                    continue

                try:
                    qty_new = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
                except ValueError:
                    qty_new = 0

                self.progress.emit(22 + int((idx_bom / max(total, 1)) * 64))

                # ── EXISTENT ──────────────────────────────────────────────────
                if lcsc_part in stock_by_lcsc:
                    i = stock_by_lcsc[lcsc_part]
                    while len(data_rows[i]) < tc:
                        data_rows[i].append("")

                    existing_id = str(data_rows[i][Config.ID]).strip()
                    try:
                        qty_old = int(float(str(data_rows[i][Config.STOCK]).strip() or "0"))
                    except ValueError:
                        qty_old = 0
                    qty_total = qty_old + qty_new
                    data_rows[i][Config.STOCK] = qty_total

                    mpn       = str(data_rows[i][Config.MANUFACTURER_PN])
                    mfr       = str(data_rows[i][Config.MANUFACTURER_NAME])
                    categoria = str(data_rows[i][Config.CATEGORY]) if Config.CATEGORY < len(data_rows[i]) else ""
                    storage   = str(data_rows[i][Config.STORAGE])  if Config.STORAGE  < len(data_rows[i]) else ""

                    ds_before   = bool(str(data_rows[i][Config.DATASHEET]).strip())       if Config.DATASHEET       < len(data_rows[i]) else False
                    bot_before  = bool(str(data_rows[i][Config.SUPPLIER_PRODUCT]).strip()) if Config.SUPPLIER_PRODUCT < len(data_rows[i]) else False
                    desc_before = bool(str(data_rows[i][Config.DESCRIPTION]).strip())      if Config.DESCRIPTION      < len(data_rows[i]) else False

                    cols_check = [
                        Config.MANUFACTURER_PN, Config.MANUFACTURER_NAME,
                        Config.CATEGORY, Config.PACKAGE, Config.DESCRIPTION,
                        Config.DATASHEET, Config.SUPPLIER_PRODUCT,
                    ]
                    needs_fill = any(
                        not str(data_rows[i][c]).strip()
                        for c in cols_check if c < len(data_rows[i])
                    )

                    action    = "EXISTENT"
                    ds_added  = False
                    bot_added = False
                    desc_added = False
                    n_filled  = 0

                    if needs_fill:
                        api = get_lcsc_data(lcsc_part)
                        if api:
                            data_rows[i], n_filled = self._fill_empty(data_rows[i], api)
                            mpn       = api.get("name", mpn)         or mpn
                            mfr       = api.get("manufacturer", mfr) or mfr
                            # Mantenir categoria existent si ja n'hi ha; completar si buida
                            # if not categoria:
                            #     categoria = api.get("type2", "") or ""
                            ds_added   = (not ds_before)   and bool(str(data_rows[i][Config.DATASHEET]).strip())
                            bot_added  = (not bot_before)  and bool(str(data_rows[i][Config.SUPPLIER_PRODUCT]).strip())
                            desc_added = (not desc_before) and bool(str(data_rows[i][Config.DESCRIPTION]).strip())
                        else:
                            action = "WARN"
                            stats["avisos"] += 1

                    ds_after   = bool(str(data_rows[i][Config.DATASHEET]).strip())        if Config.DATASHEET       < len(data_rows[i]) else False
                    bot_after  = bool(str(data_rows[i][Config.SUPPLIER_PRODUCT]).strip()) if Config.SUPPLIER_PRODUCT < len(data_rows[i]) else False
                    desc_after = bool(str(data_rows[i][Config.DESCRIPTION]).strip())      if Config.DESCRIPTION      < len(data_rows[i]) else False

                    if action == "EXISTENT":
                        stats["existents"] += 1

                    self.component_result.emit({
                        "component_id": existing_id,
                        "lcsc":         lcsc_part,
                        "action":       action,
                        "mpn":          mpn,
                        "manufacturer": mfr,
                        "categoria":    categoria,   # valor existent del sheet
                        "storage":      storage,     # valor existent del sheet
                        "stock_old":    qty_old,
                        "stock_added":  qty_new,
                        "stock_total":  qty_total,
                        "desc_before":  desc_before,
                        "desc_after":   desc_after,
                        "desc_added":   desc_added,
                        "ds_before":    ds_before,
                        "ds_after":     ds_after,
                        "ds_added":     ds_added,
                        "bot_before":   bot_before,
                        "bot_after":    bot_after,
                        "bot_added":    bot_added,
                    })

                # ── NOU ───────────────────────────────────────────────────────
                else:
                    api    = get_lcsc_data(lcsc_part)
                    action = "NOU"

                    if api:
                        new_row    = self._build_new_row(next_id, lcsc_part, bom_row, api)
                        mpn        = api.get("name", bom_row.get("Manufacture Part Number", ""))
                        mfr        = api.get("manufacturer", bom_row.get("Manufacturer", ""))
                        # categoria  = api.get("type2", "")
                        ds_after   = bool(api.get("datasheet"))
                        bot_after  = bool(api.get("store")) or True
                        desc_after = bool(api.get("description") or bom_row.get("Description", ""))
                    else:
                        new_row    = self._build_new_row(next_id, lcsc_part, bom_row, {})
                        mpn        = bom_row.get("Manufacture Part Number", "")
                        mfr        = bom_row.get("Manufacturer", "")
                        categoria  = ""
                        ds_after   = False
                        bot_after  = True
                        desc_after = bool(bom_row.get("Description", ""))
                        action     = "WARN"
                        stats["avisos"] += 1

                    self.component_result.emit({
                        "component_id": str(next_id),
                        "lcsc":         lcsc_part,
                        "action":       action,
                        "mpn":          mpn,
                        "manufacturer": mfr,
                        "categoria":    "",          # nou → l'usuari tria
                        "storage":      "",          # nou → l'usuari tria
                        "stock_old":    0,
                        "stock_added":  qty_new,
                        "stock_total":  qty_new,
                        "desc_before":  False,
                        "desc_after":   desc_after,
                        "desc_added":   desc_after,
                        "ds_before":    False,
                        "ds_after":     ds_after,
                        "ds_added":     ds_after,
                        "bot_before":   False,
                        "bot_after":    bot_after,
                        "bot_added":    bot_after,
                    })

                    data_rows.append(new_row)
                    stock_by_lcsc[lcsc_part] = len(data_rows) - 1
                    next_id += 1
                    if action == "NOU":
                        stats["nous"] += 1

            self.progress.emit(88)
            self._head("Previsualitzacio completada - revisa la taula i prem Aplicar canvis")
            self.preview_done.emit(stats)
            self._confirm_event.wait()

            if self._abort or not self._confirmed:
                self.finished.emit(False, "Operacio cancel-lada. No s'ha modificat res.")
                return

            # ══ FASE B — BACKUP + ESCRIPTURA ══════════════════════════════════
            self._head("FASE B - Backup i escriptura al Google Sheet")
            self.progress.emit(91)

            # Aplicar categories triades per l'usuari (si han canviat)
            for lcsc_part, cat in self._category_overrides.items():
                if not cat:
                    continue
                idx = self._stock_by_lcsc.get(lcsc_part)
                if idx is not None and idx < len(data_rows):
                    while len(data_rows[idx]) < tc:
                        data_rows[idx].append("")
                    data_rows[idx][Config.CATEGORY] = cat

            # Aplicar valors Storage triats per l'usuari
            for lcsc_part, stor in self._storage_overrides.items():
                if not stor:
                    continue
                idx = self._stock_by_lcsc.get(lcsc_part)
                if idx is not None and idx < len(data_rows):
                    while len(data_rows[idx]) < tc:
                        data_rows[idx].append("")
                    data_rows[idx][Config.STORAGE] = stor

            backup_ref = self._backup_csv(original_rows)
            self.progress.emit(95)
            self._write_rows(client, [header_row] + data_rows)
            self.progress.emit(100)

            self.finished.emit(True,
                f"Completat.  "
                f"Nous: {stats['nous']}  |  "
                f"Actualitzats: {stats['existents']}  |  "
                f"Avisos: {stats['avisos']}  |  "
                f"Backup: {backup_ref}"
            )

        except Exception as exc:
            import traceback
            self._err(traceback.format_exc())
            self.finished.emit(False, f"ERROR: {exc}")


# =============================================================================
#  MINI-LOG DE FASES
# =============================================================================

class PhaseLogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("phase_log")
        self.setReadOnly(True)
        self.setFixedHeight(68)

    def append_phase(self, msg: str, tipo: str = "info"):
        color  = PHASE_FG.get(tipo, "#555555")
        prefix = {"ok": "OK", "warn": "AVIS", "error": "ERR", "head": ">>>"}.get(tipo, "")
        ts     = datetime.datetime.now().strftime("%H:%M:%S")
        self.append(
            f'<span style="color:#aaaaaa;">[{ts}]</span>&nbsp;'
            f'<span style="color:{color};">{prefix} {msg}</span>'
        )
        self.moveCursor(QTextCursor.End)


# =============================================================================
#  DELEGATES DE LA TAULA
# =============================================================================

class ReadOnlyLineEditDelegate(QStyledItemDelegate):
    """
    Doble clic sobre una cel·la obre un QLineEdit en mode lectura:
    l'usuari pot seleccionar text i copiar-lo (Ctrl+C).
    """
    def createEditor(self, parent, option, index):
        le = QLineEdit(parent)
        le.setReadOnly(True)
        le.setStyleSheet(
            "QLineEdit {"
            "  background:#fffff4; border:1px solid #0078d4;"
            "  padding:1px 6px; font-size:12px;"
            "}"
        )
        return le

    def setEditorData(self, editor, index):
        editor.setText(index.data(Qt.DisplayRole) or "")
        editor.selectAll()

    def setModelData(self, editor, model, index):
        pass   # lectura: mai sobreescrivim la cel·la


class SearchableComboDelegate(QStyledItemDelegate):
    """
    Delegate amb desplegable compacte, scrollable i cercable.
    Reutilitzable per a Categoria i Storage.

    Un clic sobre la cel·la obre un QComboBox editable:
      - Amplada fixa i limitada (no ocupa tota la pantalla)
      - Màxim 12 elements visibles + scrollbar
      - Cerca per contingut (MatchContains) mentre s'escriu
    """
    _POPUP_WIDTH  = 240   # px — amplada màxima del desplegable
    _MAX_VISIBLE  = 12    # files visibles sense scroll

    def __init__(self, values: list, parent=None):
        super().__init__(parent)
        self._values = list(values)

    def set_values(self, values: list):
        self._values = list(values)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.setMaxVisibleItems(self._MAX_VISIBLE)

        combo.addItem("")
        combo.addItems(self._values)

        # Cerca per contingut (no sols per prefix)
        completer = combo.completer()
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.popup().setMaximumWidth(self._POPUP_WIDTH)

        # Limitar amplada del popup del desplegable normal
        combo.view().setMaximumWidth(self._POPUP_WIDTH)
        combo.view().setMinimumWidth(160)

        combo.setStyleSheet(
            "QComboBox {"
            "  background:#ffffff; border:1px solid #0078d4;"
            "  padding:1px 6px; font-size:12px;"
            "}"
            "QComboBox QAbstractItemView {"
            "  border:1px solid #0078d4; background:#ffffff;"
            "  selection-background-color:#cce4f7; font-size:12px;"
            "  outline:none;"
            "}"
        )
        return combo

    def setEditorData(self, editor, index):
        val = index.data(Qt.DisplayRole) or ""
        idx = editor.findText(val)
        if idx >= 0:
            editor.setCurrentIndex(idx)
        else:
            editor.setEditText(val)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        # Amplada = la de la columna; no s'estira per tota la finestra
        rect = option.rect
        rect.setWidth(min(rect.width(), self._POPUP_WIDTH))
        editor.setGeometry(rect)


# =============================================================================
#  WIDGET TAULA DE COMPONENTS
# =============================================================================

class ComponentTableWidget(QTableWidget):
    """
    Descripcio / Datasheet / Botiga:
      "Si"  (verd)  -> ja existia al registre
      "Nou" (blau)  -> afegit/actualitzat en aquesta importacio
      "No"  (gris)  -> no disponible

    Categoria / Storage:
      Desplegable compacte i cercable (SearchableComboDelegate).
      Per als components EXISTENTS es mostra el valor actual del sheet;
      l'usuari el pot canviar lliurement.

    Ctrl+C copia les files seleccionades com a text TSV.
    """

    def __init__(self, parent=None):
        super().__init__(0, len(_COLS), parent)
        self.setHorizontalHeaderLabels(_COLS)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)
        self.setSortingEnabled(False)

        # Delegates
        self._ro_delegate      = ReadOnlyLineEditDelegate(self)
        self._cat_delegate     = SearchableComboDelegate([], self)
        self._storage_delegate = SearchableComboDelegate([], self)

        for col_i in range(len(_COLS)):
            name = _COLS[col_i]
            if name == "Categoria":
                self.setItemDelegateForColumn(col_i, self._cat_delegate)
            elif name == "Storage":
                self.setItemDelegateForColumn(col_i, self._storage_delegate)
            else:
                self.setItemDelegateForColumn(col_i, self._ro_delegate)

        hh = self.horizontalHeader()
        hh.setHighlightSections(False)
        hh.setStretchLastSection(True)
        for col_name, width in _COL_WIDTHS.items():
            col_i = _COL_IDX[col_name]
            if col_name == "Botiga":          # última columna → stretch
                hh.setSectionResizeMode(col_i, QHeaderView.Stretch)
            else:
                hh.setSectionResizeMode(col_i, QHeaderView.Fixed)
                self.setColumnWidth(col_i, width)

        self.verticalHeader().setDefaultSectionSize(24)

        # Clic únic obre el combo (Categoria / Storage)
        self.cellClicked.connect(self._on_cell_clicked)

    # ── Desplegables ──────────────────────────────────────────────────────────

    def _on_cell_clicked(self, row: int, col: int):
        if col in (_COL_IDX["Categoria"], _COL_IDX["Storage"]):
            self.edit(self.model().index(row, col))

    def set_categories(self, categories: list):
        self._cat_delegate.set_values(categories)

    def set_storage_values(self, values: list):
        self._storage_delegate.set_values(values)

    # ── Afegir fila ───────────────────────────────────────────────────────────

    def add_component(self, data: dict):
        action     = data.get("action", "NOU")
        bg         = QColor(ROW_BG.get(action, "#ffffff"))
        fg_act     = ACTION_FG.get(action, "#1a1a1a")
        label      = ACTION_LABEL.get(action, action)

        stock_old  = data.get("stock_old",  0)
        stock_add  = data.get("stock_added", 0)
        stock_tot  = data.get("stock_total", 0)

        desc_before = data.get("desc_before", False)
        desc_after  = data.get("desc_after",  False)
        desc_added  = data.get("desc_added",  False)
        ds_before   = data.get("ds_before",   False)
        ds_after    = data.get("ds_after",    False)
        ds_added    = data.get("ds_added",    False)
        bot_before  = data.get("bot_before",  False)
        bot_after   = data.get("bot_after",   False)
        bot_added   = data.get("bot_added",   False)

        categoria   = data.get("categoria", "")
        storage     = data.get("storage",   "")

        def _link_display(before, after, added):
            """Retorna (text, fg, bold) per a columnes Si/Nou/No."""
            if added:
                return "Nou", "#1565c0", True
            elif after:
                return "Si",  "#2e7d32", False
            else:
                return "No",  "#b0b0b0", False

        desc_text, desc_fg, desc_bold = _link_display(desc_before, desc_after, desc_added)
        ds_text,   ds_fg,   ds_bold   = _link_display(ds_before,   ds_after,   ds_added)
        bot_text,  bot_fg,  bot_bold  = _link_display(bot_before,  bot_after,  bot_added)

        row_i = self.rowCount()
        self.insertRow(row_i)

        def _item(text, align=Qt.AlignVCenter | Qt.AlignLeft,
                  bold=False, fg=None, user_role=None):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(align)
            it.setBackground(QBrush(bg))
            if fg:
                it.setForeground(QBrush(QColor(fg)))
            if bold:
                f = it.font(); f.setBold(True); it.setFont(f)
            if user_role is not None:
                it.setData(Qt.UserRole, user_role)
            return it

        C = _COL_IDX
        CENTER = Qt.AlignVCenter | Qt.AlignHCenter
        RIGHT  = Qt.AlignVCenter | Qt.AlignRight

        self.setItem(row_i, C["ID"],        _item(data.get("component_id", ""), bold=True))
        self.setItem(row_i, C["LCSC Part"], _item(data.get("lcsc", ""), bold=True))
        self.setItem(row_i, C["Accio"],
                     _item(label, align=CENTER, bold=True, fg=fg_act, user_role=action))
        self.setItem(row_i, C["MPN"],       _item(data.get("mpn", "")))
        self.setItem(row_i, C["Fabricant"], _item(data.get("manufacturer", "")))

        # Categoria: mostra el valor existent (editable via delegate)
        self.setItem(row_i, C["Categoria"], _item(categoria))

        # Storage: mostra el valor existent (editable via delegate)
        self.setItem(row_i, C["Storage"],   _item(storage))

        # Estoc
        if action == "NOU":
            self.setItem(row_i, C["Estoc ant."], _item("", align=RIGHT, fg="#c0c0c0"))
        else:
            self.setItem(row_i, C["Estoc ant."], _item(stock_old, align=RIGHT, fg="#777777"))

        fg_add = "#2e7d32" if stock_add > 0 else "#b0b0b0"
        self.setItem(row_i, C["Afegit"], _item(f"+{stock_add}", align=RIGHT, fg=fg_add))
        self.setItem(row_i, C["Total"],  _item(stock_tot, align=RIGHT, bold=True))

        # Descripcio / Datasheet / Botiga (Si / Nou / No)
        self.setItem(row_i, C["Descripcio"],
                     _item(desc_text, align=CENTER, bold=desc_bold, fg=desc_fg))
        self.setItem(row_i, C["Datasheet"],
                     _item(ds_text,   align=CENTER, bold=ds_bold,   fg=ds_fg))
        self.setItem(row_i, C["Botiga"],
                     _item(bot_text,  align=CENTER, bold=bot_bold,  fg=bot_fg))

        self.scrollToBottom()

    def clear_data(self):
        self.setRowCount(0)

    def apply_filter(self, action_key):
        ci = _COL_IDX["Accio"]
        for row in range(self.rowCount()):
            it   = self.item(row, ci)
            hide = False if action_key is None else (
                (it.data(Qt.UserRole) if it else "") != action_key
            )
            self.setRowHidden(row, hide)

    def selected_lcsc_part(self):
        rows = sorted({i.row() for i in self.selectedItems()
                       if not self.isRowHidden(i.row())})
        if not rows:
            return None
        ci = _COL_IDX["LCSC Part"]
        it = self.item(rows[0], ci)
        return it.text().strip() if it else None

    def get_all_category_selections(self) -> dict:
        """Retorna {lcsc_part: categoria} per a totes les files visibles."""
        result = {}
        ci_lcsc = _COL_IDX["LCSC Part"]
        ci_cat  = _COL_IDX["Categoria"]
        for row in range(self.rowCount()):
            if self.isRowHidden(row):
                continue
            it_lcsc = self.item(row, ci_lcsc)
            it_cat  = self.item(row, ci_cat)
            if it_lcsc and it_cat:
                lcsc = it_lcsc.text().strip()
                cat  = it_cat.text().strip()
                if lcsc and cat:
                    result[lcsc] = cat
        return result

    def get_all_storage_selections(self) -> dict:
        """Retorna {lcsc_part: storage} per a totes les files visibles."""
        result = {}
        ci_lcsc = _COL_IDX["LCSC Part"]
        ci_stor = _COL_IDX["Storage"]
        for row in range(self.rowCount()):
            if self.isRowHidden(row):
                continue
            it_lcsc = self.item(row, ci_lcsc)
            it_stor = self.item(row, ci_stor)
            if it_lcsc and it_stor:
                lcsc = it_lcsc.text().strip()
                stor = it_stor.text().strip()
                if lcsc and stor:
                    result[lcsc] = stor
        return result


# =============================================================================
#  FINESTRA PRINCIPAL
# =============================================================================

class MainWindow(QMainWindow):

    _IDLE    = "idle"
    _RUNNING = "running"
    _REVIEW  = "review"
    _COMMIT  = "commit"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("myStock")
        self.setMinimumSize(920, 560)
        self.resize(1200, 680)
        self._worker        = None
        self._thread        = None
        self._state         = self._IDLE
        self._active_filter = None
        self._type_counts   = {k: 0 for k in ACTION_LABEL}
        self._filter_pills  = {}
        self._lookup_wins   = []
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        # ── Capçalera ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        lbl_title = QLabel("Importacio albara LCSC")
        lbl_title.setObjectName("lbl_title")
        hdr.addWidget(lbl_title)
        hdr.addStretch()
        root.addLayout(hdr)
        root.addWidget(self._hsep())

        # ── Selector fitxer ────────────────────────────────────────────────────
        grp = QGroupBox()
        gl  = QVBoxLayout(grp)
        gl.setSpacing(6); gl.setContentsMargins(10, 8, 10, 8)
        lbl_s = QLabel("Fitxer d'albara"); lbl_s.setObjectName("lbl_section")
        gl.addWidget(lbl_s)
        rf = QHBoxLayout(); rf.setSpacing(6)
        self.le_bom = QLineEdit()
        self.le_bom.setPlaceholderText("Selecciona el fitxer .csv o .tsv de la comanda LCSC...")
        self.le_bom.textChanged.connect(self._on_bom_changed)
        btn_browse = QPushButton("Cerca...")
        btn_browse.setFixedWidth(72)
        btn_browse.clicked.connect(self._browse_bom)
        rf.addWidget(self.le_bom); rf.addWidget(btn_browse)
        gl.addLayout(rf)
        self.lbl_file_info = QLabel("Cap fitxer seleccionat.")
        self.lbl_file_info.setStyleSheet("color:#888888; font-size:11px;")
        gl.addWidget(self.lbl_file_info)
        root.addWidget(grp)
        root.addWidget(self._hsep())

        # ── Barra: filtre + accions ────────────────────────────────────────────
        top_bar = QHBoxLayout(); top_bar.setSpacing(6)
        lbl_f = QLabel("Filtre:")
        lbl_f.setStyleSheet("color:#666; font-size:11px;")
        top_bar.addWidget(lbl_f)
        for key in ["NOU", "EXISTENT", "WARN", "ERROR"]:
            btn = QPushButton(ACTION_LABEL[key])
            btn.setFixedHeight(24)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda chk=False, k=key: self._toggle_filter(k))
            self._filter_pills[key] = btn
            top_bar.addWidget(btn)

        top_bar.addSpacing(12)
        top_bar.addStretch()

        self.btn_lookup = QPushButton("Veure component")
        self.btn_lookup.setObjectName("btn_lookup")
        self.btn_lookup.setFixedHeight(24)
        self.btn_lookup.setEnabled(False)
        self.btn_lookup.setToolTip("Obre Component Lookup amb el LCSC Part seleccionat")
        self.btn_lookup.clicked.connect(self._open_lookup)
        top_bar.addWidget(self.btn_lookup)

        btn_clear = QPushButton("Netejar")
        btn_clear.setFixedHeight(24)
        btn_clear.setStyleSheet("font-size:11px; padding:2px 10px;")
        btn_clear.clicked.connect(self._clear_results)
        top_bar.addWidget(btn_clear)

        root.addLayout(top_bar)
        self._update_pill_styles()

        # ── Taula ─────────────────────────────────────────────────────────────
        self.comp_table = ComponentTableWidget()
        self.comp_table.itemSelectionChanged.connect(self._on_selection_changed)
        root.addWidget(self.comp_table, 1)

        # ── Mini-log ──────────────────────────────────────────────────────────
        self.phase_log = PhaseLogWidget()
        root.addWidget(self.phase_log)

        # ── Progrés ───────────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)
        root.addWidget(self._hsep())

        # ── Botons inferiors ──────────────────────────────────────────────────
        bot = QHBoxLayout(); bot.setSpacing(6)
        self.lbl_status = QLabel("Preparat.")
        self.lbl_status.setObjectName("lbl_status")
        bot.addWidget(self.lbl_status, 1)

        self.btn_cancel = QPushButton("Cancel-la")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.clicked.connect(self._on_cancel)
        bot.addWidget(self.btn_cancel)

        self.btn_run = QPushButton("Previsualitzar")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setEnabled(False)
        self.btn_run.setFixedWidth(152)
        self.btn_run.clicked.connect(self._on_btn_run)
        bot.addWidget(self.btn_run)

        root.addLayout(bot)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _hsep():
        f = QFrame(); f.setFrameShape(QFrame.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet("background-color:#d0d0d0; border:none;")
        return f

    def _default_bom_folder(self) -> str:
        for attr in ("LCSC_BOM_FOLDER", "BACKUP_FOLDER"):
            folder = getattr(Config, attr, None)
            if folder and Path(folder).is_dir():
                return str(folder)
        return str(Path.home() / "Downloads")

    # ── Pills ─────────────────────────────────────────────────────────────────

    def _pill_style(self, key: str, active: bool) -> str:
        bg  = ROW_BG[key]; fg = ACTION_FG[key]
        bw  = "2px" if active else "1px"
        bst = fg if active else f"{fg}88"
        fw  = "700" if active else "600"
        return (
            f"background-color:{bg}; color:{fg}; font-weight:{fw};"
            f"font-size:11px; padding:2px 10px;"
            f"border:{bw} solid {bst}; border-radius:0px;"
        )

    def _update_pill_styles(self):
        for key, btn in self._filter_pills.items():
            count  = self._type_counts.get(key, 0)
            label  = ACTION_LABEL[key]
            active = self._active_filter == key
            btn.setText(f"{label} ({count})" if count else label)
            btn.setStyleSheet(self._pill_style(key, active))

    def _toggle_filter(self, key: str):
        self._active_filter = None if self._active_filter == key else key
        self.comp_table.apply_filter(self._active_filter)
        self._update_pill_styles()

    # ── Estat del botó principal ──────────────────────────────────────────────

    def _set_btn_run_mode(self, mode: str):
        if mode == "preview":
            self.btn_run.setProperty("commit", "false")
            self.btn_run.setText("Previsualitzar")
            self.btn_run.setEnabled(DEPS_OK and Path(self.le_bom.text().strip()).is_file())
        elif mode == "commit":
            self.btn_run.setProperty("commit", "true")
            self.btn_run.setText("Aplicar canvis")
            self.btn_run.setEnabled(True)
        elif mode == "disabled":
            self.btn_run.setEnabled(False)
        self.btn_run.style().unpolish(self.btn_run)
        self.btn_run.style().polish(self.btn_run)

    def _on_btn_run(self):
        if self._state == self._REVIEW:
            self._commit()
        else:
            self._start_preview()

    def _on_cancel(self):
        if self._worker:
            self._worker.abort()
        self.lbl_status.setStyleSheet("color:#9a5a00; font-size:12px;")
        self.lbl_status.setText("Cancel-lant...")
        self.btn_cancel.setEnabled(False)
        self._set_btn_run_mode("disabled")

    # ── Seleccio → activa Veure component ────────────────────────────────────

    def _on_selection_changed(self):
        lcsc = self.comp_table.selected_lcsc_part()
        self.btn_lookup.setEnabled(bool(lcsc))

    # =========================================================================
    #  COMPONENT LOOKUP
    # =========================================================================

    def _open_lookup(self):
        lcsc = self.comp_table.selected_lcsc_part()
        if not lcsc:
            return

        if _LOOKUP_AVAILABLE:
            win = LookupWindow()
            win.setWindowTitle(f"Component Lookup - {lcsc}")
            win.show()
            win.raise_()
            win.search(lcsc)
            self._lookup_wins.append(win)
            try:
                win.destroyed.connect(
                    lambda _, w=win: self._lookup_wins.remove(w)
                    if w in self._lookup_wins else None
                )
            except Exception:
                pass
        else:
            script = PROJECT_DIR / "component_lookup.py"
            if script.exists():
                import subprocess
                subprocess.Popen(
                    [sys.executable, str(script)],
                    env={**os.environ, "_NOWSTOCK_LOOKUP_CODE": lcsc},
                )
            else:
                self.lbl_status.setStyleSheet("color:#c42b1c; font-size:12px;")
                self.lbl_status.setText("component_lookup.py no trobat al directori del projecte.")

    # =========================================================================
    #  BROWSE
    # =========================================================================

    def _browse_bom(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona albara LCSC",
            self._default_bom_folder(),
            "Fitxers CSV/TSV (*.csv *.tsv);;Tots els fitxers (*)"
        )
        if path:
            self.le_bom.setText(path)

    def _on_bom_changed(self, text):
        p = Path(text.strip())
        if p.is_file():
            self.lbl_file_info.setText(
                f"{p.name}   -   {p.stat().st_size / 1024:.1f} KB   -   {p.parent}")
            self.lbl_file_info.setStyleSheet("color:#107c10; font-size:11px;")
            if self._state == self._IDLE:
                self._set_btn_run_mode("preview")
        else:
            msg = "Fitxer no trobat." if text.strip() else "Cap fitxer seleccionat."
            col = "#c42b1c" if text.strip() else "#888888"
            self.lbl_file_info.setText(msg)
            self.lbl_file_info.setStyleSheet(f"color:{col}; font-size:11px;")
            if self._state == self._IDLE:
                self._set_btn_run_mode("disabled")

    # =========================================================================
    #  FLUX
    # =========================================================================

    def _start_preview(self):
        bom_file = self.le_bom.text().strip()
        if not Path(bom_file).is_file():
            self.lbl_status.setText("Selecciona un fitxer valid primer.")
            return

        self._state = self._RUNNING
        self._set_btn_run_mode("disabled")
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setStyleSheet("color:#0078d4; font-size:12px;")
        self.lbl_status.setText("Analitzant...")
        self._clear_results(keep_file=True)

        self._worker = ImportWorker(bom_file)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.phase_log.connect(self._on_phase_log)
        self._worker.component_result.connect(self._on_component_result)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.categories_loaded.connect(self.comp_table.set_categories)
        self._worker.storage_loaded.connect(self.comp_table.set_storage_values)
        self._worker.preview_done.connect(self._on_preview_done)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _on_preview_done(self, stats: dict):
        self._state = self._REVIEW
        n = stats.get("nous",      0)
        e = stats.get("existents", 0)
        a = stats.get("avisos",    0)
        self.lbl_status.setStyleSheet("color:#e65100; font-weight:600; font-size:12px;")
        self.lbl_status.setText(
            f"Previsualitzacio llesta  -  "
            f"Nous: {n}  |  Actualitzats: {e}  |  Avisos: {a}  "
            f"|  Revisa i prem 'Aplicar canvis'"
        )
        self._set_btn_run_mode("commit")
        self.btn_cancel.setEnabled(True)

    def _commit(self):
        self._state = self._COMMIT
        self._set_btn_run_mode("disabled")
        self.btn_cancel.setEnabled(False)
        self.lbl_status.setStyleSheet("color:#0078d4; font-size:12px;")
        self.lbl_status.setText("Fent backup i escrivint al Google Sheet...")
        if self._worker:
            cat_overrides  = self.comp_table.get_all_category_selections()
            stor_overrides = self.comp_table.get_all_storage_selections()
            self._worker.apply_category_overrides(cat_overrides)
            self._worker.apply_storage_overrides(stor_overrides)
            self._worker.confirm(True)

    def _clear_results(self, keep_file: bool = False):
        self.comp_table.clear_data()
        self.phase_log.clear()
        self.progress_bar.setValue(0)
        self._type_counts   = {k: 0 for k in ACTION_LABEL}
        self._active_filter = None
        self._update_pill_styles()
        if not keep_file:
            self.lbl_status.setStyleSheet("color:#555555; font-size:12px;")
            self.lbl_status.setText("Preparat.")

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_phase_log(self, msg: str, tipo: str):
        self.phase_log.append_phase(msg, tipo)

    def _on_component_result(self, data: dict):
        action = data.get("action", "NOU")
        self._type_counts[action] = self._type_counts.get(action, 0) + 1
        self.comp_table.add_component(data)
        if self._active_filter:
            row = self.comp_table.rowCount() - 1
            self.comp_table.setRowHidden(row, action != self._active_filter)
        self._update_pill_styles()

    def _on_finished(self, success: bool, msg: str):
        self._state = self._IDLE
        self.btn_cancel.setEnabled(False)
        self._set_btn_run_mode("preview")
        color = "#107c10" if success else "#c42b1c"
        self.lbl_status.setStyleSheet(f"color:{color}; font-size:12px;")
        self.lbl_status.setText(msg)
        if success:
            self.progress_bar.setValue(100)

    def _cleanup_thread(self):
        self._thread = None
        self._worker = None


# =============================================================================
#  ENTRY POINT
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()