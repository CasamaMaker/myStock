# bom.py
"""
Gestor de Bill of Materials (BoM) de KiCad.

Carrega un CSV exportat des de KiCad, el creua amb l'estoc personal
(Google Sheets) i permet consumir l'estoc component a component o en bloc.

Format CSV esperat (capçalera):
    "Reference","Value","Datasheet","Footprint","Qty","DNP"

Integració amb l'estoc:
  - Matching per MANUFACTURER_PN (Config.MANUFACTURER_PN) i
    per SUPPLIER_PN (Config.SUPPLIER_PN), amb fallback a cerca parcial.
  - La lectura/escriptura del Google Sheet utilitza la mateixa
    configuració (Config) que la resta del projecte.

Ús des de myStock.py:
    from bom import BomWindow
    win = BomWindow(stock_data=self.data_google_sheet)
    win.show()

Ús autònom:
    python bom.py
"""

import csv
import logging
import sys
import threading
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import gspread
from google.oauth2.service_account import Credentials
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHeaderView, QAbstractItemView,
    QMainWindow, QMenu, QMessageBox, QTableWidgetItem,
)

from configuration import Config
from ui_bom import Ui_BomWindow

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════════════════

STATUS_OK        = "ok"
STATUS_PARCIAL   = "parcial"
STATUS_FALTA     = "falta"
STATUS_NO_TROBAT = "no_trobat"
STATUS_DNP       = "dnp"

# (color de fons, color del text de la columna Estat)
ROW_COLORS = {
    STATUS_OK:        ("#e8f5e9", "#2e7d32"),
    STATUS_PARCIAL:   ("#fff8e1", "#e65100"),
    STATUS_FALTA:     ("#ffebee", "#c62828"),
    STATUS_NO_TROBAT: ("#fff3e0", "#bf360c"),
    STATUS_DNP:       ("#f5f5f5", "#9e9e9e"),
}

STATUS_LABELS = {
    STATUS_OK:        "✓  OK",
    STATUS_PARCIAL:   "⚠  Parcial",
    STATUS_FALTA:     "✗  Falta",
    STATUS_NO_TROBAT: "?  No trobat",
    STATUS_DNP:       "—  DNP",
}

# Índexs de les columnes de la taula
COL_REFS     = 0
COL_VALUE    = 1
COL_FP       = 2
COL_QTY_NEED = 3
COL_QTY_STOC = 4
COL_STORAGE  = 5
COL_STATUS   = 6
_COL_DEFS = [
    # (capçalera,      amplada, mode resize)
    ("Designadors",    220, QHeaderView.Interactive),
    ("Valor",           95, QHeaderView.Interactive),
    ("Footprint",      140, QHeaderView.Interactive),
    ("Qty nec.",        65, QHeaderView.Fixed),
    ("Qty estoc",       65, QHeaderView.Fixed),
    ("Ubicació",       130, QHeaderView.Interactive),
    ("Estat",          110, QHeaderView.Stretch),
]


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════════

def resource_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


def _col_to_a1(col_0based: int) -> str:
    """Converteix un índex de columna 0-based a notació A1 (ex: 9 → 'J')."""
    col = col_0based + 1
    result = ""
    while col > 0:
        col, rem = divmod(col - 1, 26)
        result = chr(65 + rem) + result
    return result


def _simplify_footprint(raw: str) -> str:
    """
    Extreu un nom curt del footprint.
    "Capacitor_SMD:C_0402_1005Metric_Pad..." → "C_0402"
    Agafa el primer footprint si n'hi ha diversos separats per comes.
    """
    if not raw or raw.strip() in ("~", ""):
        return ""
    first = raw.split(",")[0].strip()
    name = first.split(":")[-1] if ":" in first else first
    parts = name.split("_")
    # Retorna els primers 2 segments per mantenir el nom curt i llegible
    return "_".join(parts[:2]) if len(parts) >= 2 else name


# ══════════════════════════════════════════════════════════════════════════════
#  Model de dades
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BomEntry:
    """Una línia del BoM, amb informació del CSV i de l'estoc (si es troba)."""
    references:    List[str]        # ["C1", "C6", "C23"]
    value:         str              # "100k"
    footprint:     str              # "R_0402"
    datasheet:     str              # URL o "~"
    qty_needed:    int              # quantitat necessària
    dnp:           bool             # Do Not Place
    # Camps omplerts pel StockMatcher:
    qty_stock:     int  = 0
    storage:       str  = ""
    stock_row_idx: int  = -1        # 0-based en data_rows; -1 = no trobat
    status:        str  = STATUS_NO_TROBAT

    @property
    def refs_display(self) -> str:
        """Refs resumides per mostrar a la taula (max 60 chars)."""
        s = ", ".join(self.references)
        return s if len(s) <= 60 else s[:57] + "…"

    @property
    def refs_full(self) -> str:
        return ", ".join(self.references)

    @property
    def qty_consumable(self) -> int:
        """Quantitat que es pot consumir sense posar l'estoc en negatiu."""
        return min(self.qty_needed, self.qty_stock)


# ══════════════════════════════════════════════════════════════════════════════
#  Parser del CSV de KiCad
# ══════════════════════════════════════════════════════════════════════════════

class BomParser:
    """
    Parseja un CSV exportat des de KiCad.

    Format esperat:
        "Reference","Value","Datasheet","Footprint","Qty","DNP"
        "C1,C2,C3","100n","~","Capacitor_SMD:C_0402","3",""

    El parser és tolerant amb:
    - Cometes als noms de les columnes
    - Columnes extra o en ordre diferent
    - DNP com a "DNP", "X", "1" o "true" (case-insensitive)
    - Qty com a enter o float
    """

    _DNP_TRUTHY = {"dnp", "x", "1", "true", "yes", "si"}

    @classmethod
    def parse(cls, filepath: str) -> List[BomEntry]:
        entries: List[BomEntry] = []

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            # Detectar separador (coma o tabulador)
            sample = f.read(2048)
            f.seek(0)
            sep = "\t" if sample.count("\t") > sample.count(",") else ","

            reader = csv.DictReader(f, delimiter=sep)
            if not reader.fieldnames:
                raise ValueError("El fitxer CSV és buit o no té capçalera.")

            # Normalitzar noms de columnes (treure cometes i espais)
            normalized = {
                fn.strip().strip('"').lower(): fn
                for fn in reader.fieldnames
            }

            col_ref = cls._find(normalized, ["reference"])
            col_val = cls._find(normalized, ["value"])
            col_fp  = cls._find(normalized, ["footprint"])
            col_ds  = cls._find(normalized, ["datasheet"])
            col_qty = cls._find(normalized, ["qty", "quantity"])
            col_dnp = cls._find(normalized, ["dnp"])

            if col_ref is None:
                raise ValueError("Columna 'Reference' no trobada al CSV.")
            if col_val is None:
                raise ValueError("Columna 'Value' no trobada al CSV.")

            for row in reader:
                # Netejar valors: treure cometes exteriors i espais
                clean = {k: (v.strip().strip('"') if v else "") for k, v in row.items()}

                refs_raw = clean.get(col_ref, "")
                refs = [r.strip() for r in refs_raw.split(",") if r.strip()]
                if not refs:
                    continue

                value = clean.get(col_val, "").strip()
                fp    = _simplify_footprint(clean.get(col_fp, "") if col_fp else "")
                ds    = clean.get(col_ds, "~") if col_ds else "~"

                qty_raw = clean.get(col_qty, "") if col_qty else ""
                try:
                    qty = max(1, int(float(qty_raw)))
                except (ValueError, TypeError):
                    qty = len(refs)

                dnp_raw = clean.get(col_dnp, "").lower() if col_dnp else ""
                dnp = dnp_raw in cls._DNP_TRUTHY

                entries.append(BomEntry(
                    references=refs,
                    value=value,
                    footprint=fp,
                    datasheet=ds,
                    qty_needed=qty,
                    dnp=dnp,
                    status=STATUS_DNP if dnp else STATUS_NO_TROBAT,
                ))

        if not entries:
            raise ValueError("El fitxer CSV no conté cap component vàlid.")

        logger.info("BoM llegit: %d línies des de '%s'", len(entries), filepath)
        return entries

    @staticmethod
    def _find(normalized: dict, candidates: List[str]) -> Optional[str]:
        """Retorna el nom original de la columna que coincideix amb alguna candidata."""
        for c in candidates:
            if c in normalized:
                return normalized[c]
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  Matching BoM ↔ Estoc
# ══════════════════════════════════════════════════════════════════════════════

class StockMatcher:
    """
    Creua les entrades del BoM amb les dades de l'estoc.

    Estratègia de matching (en ordre de prioritat):
      1. Coincidència exacta (case-insensitive) contra MANUFACTURER_PN
      2. Coincidència exacta contra SUPPLIER_PN
      3. Coincidència parcial (un conté l'altre) contra MANUFACTURER_PN

    Si cap regla troba res, l'entrada queda com STATUS_NO_TROBAT.
    """

    def __init__(self, stock_data: List[List[str]]):
        self._data_rows = stock_data[1:] if len(stock_data) > 1 else []
        self._idx_mpn:  dict[str, int] = {}   # mfr_pn.lower() → row index
        self._idx_spn:  dict[str, int] = {}   # supplier_pn.lower() → row index
        self._build_index()

    def _build_index(self):
        for i, row in enumerate(self._data_rows):
            # MANUFACTURER_PN
            if Config.MANUFACTURER_PN < len(row):
                key = str(row[Config.MANUFACTURER_PN]).strip().lower()
                if key:
                    self._idx_mpn.setdefault(key, i)
            # SUPPLIER_PN (LCSC / Mouser / Farnell part number)
            if Config.SUPPLIER_PN < len(row):
                key2 = str(row[Config.SUPPLIER_PN]).strip().lower()
                if key2:
                    self._idx_spn.setdefault(key2, i)

    def match(self, entry: BomEntry) -> BomEntry:
        """Omple els camps de stock d'una BomEntry. Retorna la mateixa instància."""
        if entry.dnp:
            return entry

        val = entry.value.strip().lower()

        # 1. Exact per MANUFACTURER_PN
        idx = self._idx_mpn.get(val)

        # 2. Exact per SUPPLIER_PN
        if idx is None:
            idx = self._idx_spn.get(val)

        # 3. Parcial per MANUFACTURER_PN
        if idx is None:
            for key, row_idx in self._idx_mpn.items():
                if val and key and (val in key or key in val):
                    idx = row_idx
                    break

        if idx is not None:
            return self._fill(entry, idx)

        # No trobat
        entry.stock_row_idx = -1
        entry.qty_stock     = 0
        entry.storage       = ""
        entry.status        = STATUS_NO_TROBAT
        return entry

    def _fill(self, entry: BomEntry, idx: int) -> BomEntry:
        row = self._data_rows[idx]

        try:
            qty_stock = int(float(str(row[Config.STOCK]).strip() or "0"))
        except (ValueError, IndexError):
            qty_stock = 0

        storage = ""
        if Config.STORAGE < len(row):
            storage = str(row[Config.STORAGE]).strip()

        entry.stock_row_idx = idx
        entry.qty_stock     = qty_stock
        entry.storage       = storage

        if qty_stock >= entry.qty_needed:
            entry.status = STATUS_OK
        elif qty_stock > 0:
            entry.status = STATUS_PARCIAL
        else:
            entry.status = STATUS_FALTA

        return entry


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: consum d'estoc al Google Sheet
# ══════════════════════════════════════════════════════════════════════════════

class ConsumeWorker(QObject):
    """
    Escriu els descomptes d'estoc al Google Sheet en un thread separat.
    Utilitza batch_update per minimitzar les crides a l'API.
    """
    progress = Signal(int, int)    # (fet, total)
    finished = Signal(bool, str)   # (èxit, missatge)

    _SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, entries: List[BomEntry]):
        super().__init__()
        # Còpia defensiva: el worker pot córrer en un thread diferent
        self.entries = list(entries)

    def run(self):
        to_update = [
            e for e in self.entries
            if not e.dnp and e.stock_row_idx >= 0 and e.qty_needed > 0
        ]
        if not to_update:
            self.finished.emit(False, "No hi ha components a consumir.")
            return

        try:
            creds_path = resource_path(Config.GOOGLE_CREDENTIALS_JSON)
            if not creds_path.exists():
                raise FileNotFoundError(f"Credencials no trobades: {creds_path}")

            creds = Credentials.from_service_account_file(
                str(creds_path), scopes=self._SCOPES
            )
            client = gspread.authorize(creds)
            ws = client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1

            stock_col_a1 = _col_to_a1(Config.STOCK)
            batch = []

            for i, entry in enumerate(to_update):
                # Fila al sheet: +2 perquè l'índex és 0-based sobre data_rows
                # i data_rows comença a la fila 2 del sheet (fila 1 = capçalera)
                sheet_row = entry.stock_row_idx + 2
                new_qty   = max(0, entry.qty_stock - entry.qty_needed)
                batch.append({
                    "range":  f"{stock_col_a1}{sheet_row}",
                    "values": [[new_qty]],
                })
                self.progress.emit(i + 1, len(to_update))

            ws.batch_update(batch, value_input_option="USER_ENTERED")

            self.finished.emit(
                True,
                f"Consumit. {len(batch)} components actualitzats al Google Sheet."
            )

        except Exception as exc:
            logger.error("Error consumint estoc: %s\n%s", exc, traceback.format_exc())
            self.finished.emit(False, f"Error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
#  Estil CSS (coherent amb la resta del projecte)
# ══════════════════════════════════════════════════════════════════════════════

STYLE = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #1a1a1a;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 12px;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 0px;
    margin-top: 0px;
    padding: 4px 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: #666666;
    font-size: 11px;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 4px 8px;
    color: #1a1a1a;
}
QLineEdit:focus { border-color: #0078d4; }

QPushButton {
    background-color: #e1e1e1;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 4px 14px;
    color: #1a1a1a;
    font-size: 12px;
}
QPushButton:hover   { background-color: #cce4f7; border-color: #0078d4; }
QPushButton:pressed { background-color: #bbd3e9; }
QPushButton:disabled { background-color: #f0f0f0; color: #a0a0a0; border-color: #d0d0d0; }

QPushButton#btn_load {
    background-color: #0078d4; border: 1px solid #006cbe;
    color: #ffffff; font-weight: 600;
}
QPushButton#btn_load:hover   { background-color: #106ebe; }
QPushButton#btn_load:pressed { background-color: #005a9e; }
QPushButton#btn_load:disabled { background-color: #cccccc; border-color: #bbbbbb; color: #888888; }

QPushButton#btn_consume_all {
    background-color: #107c10; border: 1px solid #0b5e0b;
    color: #ffffff; font-weight: 600; padding: 4px 18px;
}
QPushButton#btn_consume_all:hover   { background-color: #0e6b0e; }
QPushButton#btn_consume_all:pressed { background-color: #0a560a; }
QPushButton#btn_consume_all:disabled { background-color: #cccccc; border-color: #bbbbbb; color: #888888; }

QComboBox {
    background-color: #ffffff;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 3px 8px;
}
QComboBox:focus { border-color: #0078d4; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #ababab;
    selection-background-color: #cce4f7;
    outline: none;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    gridline-color: #eeeeee;
    font-size: 12px;
    selection-background-color: #cce4f7;
    selection-color: #1a1a1a;
    outline: none;
}
QTableWidget::item { padding: 2px 6px; border: none; }
QHeaderView::section {
    background-color: #f0f0f0;
    border: none;
    border-right: 1px solid #d8d8d8;
    border-bottom: 1px solid #c0c0c0;
    padding: 4px 6px;
    font-weight: 600;
    font-size: 11px;
    color: #444444;
}
QProgressBar {
    background-color: #e1e1e1;
    border: none;
    border-radius: 0px;
}
QProgressBar::chunk { background-color: #0078d4; }

/* Etiquetes de resum */
QLabel#lbl_ok        { color: #2e7d32; font-weight: 600; padding: 0 8px; }
QLabel#lbl_parcial   { color: #e65100; font-weight: 600; padding: 0 8px; }
QLabel#lbl_falta     { color: #c62828; font-weight: 600; padding: 0 8px; }
QLabel#lbl_no_trobat { color: #bf360c; font-weight: 600; padding: 0 8px; }
QLabel#lbl_dnp       { color: #9e9e9e; font-weight: 600; padding: 0 8px; }
QLabel#lbl_total     { color: #1a1a1a; font-weight: 600; padding: 0 8px; }
QLabel#lbl_filter    { color: #555555; }

QStatusBar {
    background-color: #f0f0f0;
    font-size: 11px;
    border-top: 1px solid #d0d0d0;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  Finestra principal
# ══════════════════════════════════════════════════════════════════════════════

class BomWindow(QMainWindow):
    """
    Finestra del gestor de BoM.

    Paràmetre opcional stock_data:
      - Si es passa (des de myStock.py), s'utilitza directament.
      - Si no, es carrega el Google Sheet en background.
    """

    # Signals per comunicar resultats des de threads secundaris al main thread
    _sig_stock_ready = Signal(list)
    _sig_stock_error = Signal(str)

    def __init__(self, stock_data: Optional[List[List[str]]] = None):
        super().__init__()
        self.ui = Ui_BomWindow()
        self.ui.setupUi(self)
        self.setStyleSheet(STYLE)

        # ── Estat intern ──────────────────────────────────────────────────────
        self._raw_entries:    List[BomEntry]       = []   # BoM sense matching
        self._entries:        List[BomEntry]       = []   # BoM amb matching
        self._stock_data:     List[List[str]]      = []
        self._stock_loaded:   bool                 = False
        self._bom_loaded:     bool                 = False
        self._consume_thread: Optional[QThread]    = None
        self._consume_worker: Optional[ConsumeWorker] = None

        # ── Configuració UI ───────────────────────────────────────────────────
        self._setup_filter_combo()
        self._setup_table()
        self._connect_signals()

        # ── Connexions de signals interns (cross-thread) ───────────────────
        self._sig_stock_ready.connect(self._on_stock_ready)
        self._sig_stock_error.connect(
            lambda msg: self._show_status(f"Error estoc: {msg}", "#c42b1c")
        )

        # ── Càrrega inicial de l'estoc ─────────────────────────────────────
        if stock_data is not None:
            self._stock_data   = stock_data
            self._stock_loaded = True
            n = max(0, len(stock_data) - 1)
            self._show_status(f"Estoc rebut ({n} components). Carrega un BoM.", "#107c10")
        else:
            self._show_status("Connectant amb Google Sheets…", "#0078d4")
            threading.Thread(target=self._load_stock_background, daemon=True).start()

    # ── Configuració inicial ──────────────────────────────────────────────────

    def _setup_filter_combo(self):
        cb = self.ui.combo_filter
        cb.addItem("Tots els components",       None)
        cb.addItem("✓  OK",                    STATUS_OK)
        cb.addItem("⚠  Parcial",               STATUS_PARCIAL)
        cb.addItem("✗  Falta",                 STATUS_FALTA)
        cb.addItem("?  No trobat",             STATUS_NO_TROBAT)
        cb.addItem("✗ / ?  Falta + No trobat", [STATUS_FALTA, STATUS_NO_TROBAT])
        cb.addItem("—  DNP",                   STATUS_DNP)

    def _setup_table(self):
        tw = self.ui.tableWidget
        tw.setColumnCount(len(_COL_DEFS))
        tw.setHorizontalHeaderLabels([c[0] for c in _COL_DEFS])

        hh = tw.horizontalHeader()
        hh.setHighlightSections(False)
        for i, (_, width, mode) in enumerate(_COL_DEFS):
            hh.setSectionResizeMode(i, mode)
            if mode != QHeaderView.Stretch:
                tw.setColumnWidth(i, width)

        tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        tw.setSelectionMode(QAbstractItemView.SingleSelection)
        tw.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tw.setAlternatingRowColors(False)
        tw.verticalHeader().setVisible(False)
        tw.verticalHeader().setDefaultSectionSize(24)
        tw.setSortingEnabled(True)

    def _connect_signals(self):
        self.ui.btn_browse.clicked.connect(self._browse_bom)
        self.ui.btn_load.clicked.connect(self._load_bom)
        self.ui.lineEdit_bom_path.returnPressed.connect(self._load_bom)
        self.ui.combo_filter.currentIndexChanged.connect(self._apply_filter)
        self.ui.btn_consume_all.clicked.connect(self._consume_all)
        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self._on_context_menu)

    # ── Càrrega de l'estoc ────────────────────────────────────────────────────

    def _load_stock_background(self):
        """Carrega les dades del Google Sheet en un thread de background."""
        try:
            creds_path = resource_path(Config.GOOGLE_CREDENTIALS_JSON)
            if not creds_path.exists():
                raise FileNotFoundError(f"Credencials no trobades: {creds_path}")

            creds = Credentials.from_service_account_file(
                str(creds_path),
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
            )
            client = gspread.authorize(creds)
            data   = client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1.get_all_values()

            if not data:
                self._sig_stock_error.emit("El Google Sheet és buit.")
                return

            self._sig_stock_ready.emit(data)

        except Exception as exc:
            logger.error("Error carregant estoc per al BoM: %s", exc)
            self._sig_stock_error.emit(str(exc))

    def _on_stock_ready(self, data: List[List[str]]):
        """Slot (main thread) cridat quan l'estoc es carrega en background."""
        self._stock_data   = data
        self._stock_loaded = True
        n = max(0, len(data) - 1)
        logger.info("Estoc carregat per al BoM: %d components.", n)

        if self._bom_loaded:
            self._match_and_populate()
        else:
            self._show_status(
                f"Estoc carregat ({n} components). Ara carrega un BoM.",
                "#107c10"
            )

    def load_stock_data(self, data: List[List[str]]):
        """
        Interfície pública per rebre dades d'estoc des de myStock.
        Pot ser cridat en qualsevol moment; re-fa el matching si el BoM ja és carregat.
        """
        self._stock_data   = data
        self._stock_loaded = True
        if self._bom_loaded:
            self._match_and_populate()

    # ── Càrrega del BoM ───────────────────────────────────────────────────────

    def _browse_bom(self):
        current = self.ui.lineEdit_bom_path.text().strip()
        folder  = str(Path(current).parent) if current else str(Path.home() / "Documents")
        try:
            folder = getattr(Config, "LCSC_BOM_FOLDER", folder) or folder
        except Exception:
            pass

        path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona BoM KiCad",
            folder,
            "CSV (*.csv);;Tots els fitxers (*)"
        )
        if path:
            self.ui.lineEdit_bom_path.setText(path)

    def _load_bom(self):
        path = self.ui.lineEdit_bom_path.text().strip()
        if not path:
            self._show_status("Selecciona primer un fitxer BoM.", "#e65100")
            return
        if not Path(path).is_file():
            self._show_status(f"Fitxer no trobat: {path}", "#c42b1c")
            return

        try:
            self._raw_entries = BomParser.parse(path)
        except Exception as exc:
            self._show_status(f"Error llegint BoM: {exc}", "#c42b1c")
            logger.error("Error llegint BoM '%s': %s", path, exc)
            return

        self._bom_loaded = True
        n = len(self._raw_entries)
        logger.info("BoM carregat: %d línies.", n)

        if self._stock_loaded:
            self._match_and_populate()
        else:
            # Mostra el BoM sense dades d'estoc mentre es connecta
            self._entries = list(self._raw_entries)
            self._populate_table(self._entries)
            self._update_stats()
            self._show_status(
                f"BoM llegit ({n} línies). Esperant connexió amb Google Sheets…",
                "#e65100"
            )

    # ── Matching i actualització de la taula ──────────────────────────────────

    def _match_and_populate(self):
        """Fa el matching entre el BoM i l'estoc i actualitza tota la taula."""
        matcher = StockMatcher(self._stock_data)
        self._entries = [matcher.match(e) for e in self._raw_entries]
        self._populate_table(self._entries)
        self._update_stats()
        self._update_consume_button()

        n_ok    = sum(1 for e in self._entries if e.status == STATUS_OK)
        n_falta = sum(1 for e in self._entries if e.status in (STATUS_FALTA, STATUS_NO_TROBAT))
        self._show_status(
            f"BoM creuat amb l'estoc — OK: {n_ok}  |  Falta/No trobat: {n_falta}",
            "#107c10" if n_falta == 0 else "#e65100"
        )

    def _populate_table(self, entries: List[BomEntry]):
        tw = self.ui.tableWidget
        tw.setSortingEnabled(False)
        tw.setRowCount(0)

        for entry in entries:
            row_i = tw.rowCount()
            tw.insertRow(row_i)
            self._set_row(row_i, entry)

        tw.setSortingEnabled(True)
        self._apply_filter()

    def _set_row(self, row_i: int, entry: BomEntry):
        """Omple una fila de la taula amb les dades d'una BomEntry."""
        bg_hex, fg_status_hex = ROW_COLORS.get(entry.status, ("#ffffff", "#1a1a1a"))
        bg = QBrush(QColor(bg_hex))

        CENTER = Qt.AlignVCenter | Qt.AlignHCenter
        RIGHT  = Qt.AlignVCenter | Qt.AlignRight

        def _item(text, align=Qt.AlignVCenter | Qt.AlignLeft, tooltip=""):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(align)
            it.setBackground(bg)
            if tooltip:
                it.setToolTip(tooltip)
            return it

        qty_stoc_display = str(entry.qty_stock) if entry.stock_row_idx >= 0 else "—"

        cells = [
            _item(entry.refs_display, tooltip=entry.refs_full),  # COL_REFS
            _item(entry.value),                                    # COL_VALUE
            _item(entry.footprint),                                # COL_FP
            _item(entry.qty_needed, align=RIGHT),                  # COL_QTY_NEED
            _item(qty_stoc_display, align=RIGHT),                  # COL_QTY_STOC
            _item(entry.storage),                                  # COL_STORAGE
            _item(STATUS_LABELS.get(entry.status, entry.status),   # COL_STATUS
                  align=CENTER),
        ]

        # Estil de la columna Estat: text amb color i negreta
        status_item = cells[COL_STATUS]
        status_item.setForeground(QBrush(QColor(fg_status_hex)))
        font = status_item.font()
        font.setBold(True)
        status_item.setFont(font)

        # Guardar la referència a l'objecte BomEntry a la primera cel·la
        cells[COL_REFS].setData(Qt.UserRole, entry)

        for col_i, cell in enumerate(cells):
            self.ui.tableWidget.setItem(row_i, col_i, cell)

    # ── Actualització del resum ───────────────────────────────────────────────

    def _update_stats(self):
        if not self._entries:
            return
        counts = {s: 0 for s in [STATUS_OK, STATUS_PARCIAL,
                                   STATUS_FALTA, STATUS_NO_TROBAT, STATUS_DNP]}
        for e in self._entries:
            counts[e.status] = counts.get(e.status, 0) + 1

        total_active = sum(counts[s] for s in
                           [STATUS_OK, STATUS_PARCIAL, STATUS_FALTA, STATUS_NO_TROBAT])

        self.ui.lbl_total.setText(f"Total: {total_active}")
        self.ui.lbl_ok.setText(f"✓  OK: {counts[STATUS_OK]}")
        self.ui.lbl_parcial.setText(f"⚠  Parcial: {counts[STATUS_PARCIAL]}")
        self.ui.lbl_falta.setText(f"✗  Falta: {counts[STATUS_FALTA]}")
        self.ui.lbl_no_trobat.setText(f"?  No trobat: {counts[STATUS_NO_TROBAT]}")
        self.ui.lbl_dnp.setText(f"DNP: {counts[STATUS_DNP]}")

    # ── Filtre de la taula ────────────────────────────────────────────────────

    def _apply_filter(self):
        filter_val = self.ui.combo_filter.currentData()
        for row_i in range(self.ui.tableWidget.rowCount()):
            item = self.ui.tableWidget.item(row_i, COL_REFS)
            if item is None:
                self.ui.tableWidget.setRowHidden(row_i, False)
                continue
            entry: BomEntry = item.data(Qt.UserRole)
            if entry is None or filter_val is None:
                hide = False
            elif isinstance(filter_val, list):
                hide = entry.status not in filter_val
            else:
                hide = entry.status != filter_val
            self.ui.tableWidget.setRowHidden(row_i, hide)

    # ── Consum d'estoc ────────────────────────────────────────────────────────

    def _update_consume_button(self):
        can = (
            self._stock_loaded
            and self._bom_loaded
            and any(
                not e.dnp and e.stock_row_idx >= 0 and e.qty_stock > 0
                for e in self._entries
            )
        )
        self.ui.btn_consume_all.setEnabled(can)

    def _on_context_menu(self, pos):
        item = self.ui.tableWidget.itemAt(pos)
        if item is None:
            return
        first = self.ui.tableWidget.item(item.row(), COL_REFS)
        if first is None:
            return
        entry: BomEntry = first.data(Qt.UserRole)
        if entry is None or entry.dnp or entry.stock_row_idx < 0 or entry.qty_stock <= 0:
            return

        menu = QMenu(self)
        act  = menu.addAction(
            f"Consumir  {entry.qty_needed}×  \"{entry.value}\"  "
            f"(estoc actual: {entry.qty_stock})"
        )
        result = menu.exec(self.ui.tableWidget.viewport().mapToGlobal(pos))
        if result == act:
            self._consume_entries([entry])

    def _consume_all(self):
        to_consume = [
            e for e in self._entries
            if not e.dnp and e.stock_row_idx >= 0 and e.qty_stock > 0
        ]
        if not to_consume:
            self._show_status("No hi ha components a consumir.", "#e65100")
            return

        # Advertir si hi ha parcials (estoc insuficient)
        n_parcial = sum(1 for e in to_consume if e.qty_stock < e.qty_needed)
        warning   = (
            f"\n\n⚠  {n_parcial} component(s) amb estoc insuficient "
            f"(es descomptarà el disponible)."
            if n_parcial else ""
        )

        reply = QMessageBox.question(
            self,
            "Confirmar consum",
            f"Vols consumir l'estoc de {len(to_consume)} components?\n"
            f"Aquesta acció actualitzarà el Google Sheet."
            f"{warning}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._consume_entries(to_consume)

    def _consume_entries(self, entries: List[BomEntry]):
        if self._consume_thread and self._consume_thread.isRunning():
            self._show_status("Hi ha una operació en curs, espereu…", "#e65100")
            return

        self._consume_worker = ConsumeWorker(entries)
        self._consume_thread = QThread()
        self._consume_worker.moveToThread(self._consume_thread)

        self._consume_thread.started.connect(self._consume_worker.run)
        self._consume_worker.progress.connect(self._on_consume_progress)
        self._consume_worker.finished.connect(self._on_consume_finished)
        self._consume_worker.finished.connect(self._consume_thread.quit)
        self._consume_thread.finished.connect(self._cleanup_consume_thread)

        self.ui.btn_consume_all.setEnabled(False)
        self.ui.progress_bar.setValue(0)
        self._consume_thread.start()
        self._show_status("Escrivint al Google Sheet…", "#0078d4")

    def _on_consume_progress(self, done: int, total: int):
        self.ui.progress_bar.setValue(int(100 * done / max(total, 1)))

    def _on_consume_finished(self, success: bool, msg: str):
        color = "#107c10" if success else "#c42b1c"
        self._show_status(msg, color)
        if not success:
            self.ui.progress_bar.setValue(0)
            return

        # Actualitzar la còpia local de l'estoc i refrescar la taula
        if self._consume_worker:
            for entry in self._consume_worker.entries:
                if entry.stock_row_idx < 0:
                    continue
                # data_rows és stock_data[1:], per tant l'índex real al sheet és +1
                sheet_idx = entry.stock_row_idx + 1
                if sheet_idx < len(self._stock_data):
                    new_qty = max(0, entry.qty_stock - entry.qty_needed)
                    self._stock_data[sheet_idx][Config.STOCK] = str(new_qty)

        # Re-match amb l'estoc actualitzat i repintar
        self._match_and_populate()

    def _cleanup_consume_thread(self):
        self._consume_thread = None
        self._consume_worker = None
        self._update_consume_button()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _show_status(self, msg: str, color: str = "#555555"):
        self.statusBar().setStyleSheet(
            f"color: {color}; font-size: 11px; background: #f0f0f0;"
        )
        self.statusBar().showMessage(msg)


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    app = QApplication(sys.argv)
    win = BomWindow()   # Carregarà l'estoc des del Google Sheet automàticament
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()