# nom fitxer: component_lookup.py
"""
Component Lookup App
Cerca components electrònics de Mouser, Farnell i LCSC
Escaneig de codi de barres/QR o entrada manual.

UI generada per Qt Designer → ui_component_lookup.py
"""

import re
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, Signal, QObject, QUrl, QByteArray
from PySide6.QtGui import QFont, QPixmap, QDesktopServices, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QHBoxLayout,
    QVBoxLayout, QWidget, QSizePolicy, QGraphicsDropShadowEffect,
    QSpacerItem
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from ui_component_lookup import Ui_MainWindow

try:
    from request_farnell import get_farnell_by_sku
    from request_lcsc import get_lcsc_data
    from request_mouser import get_mouser_data
except ImportError as e:
    print(f"[AVÍS] No s'han pogut importar els mòduls de proveïdor: {e}")

    def _dummy(name):
        return {
            "name": name, "store_name": "Demo Store",
            "description": "Component de prova (mòduls no carregats)",
            "type2": "IC", "manufacturer": "Demo Mfr", "package": "SOT-23",
            "datasheet": "https://example.com/datasheet.pdf",
            "store": "https://example.com",
            "image": "https://via.placeholder.com/130",
            "price_unit": [{"quantity": 1,  "price": "1.23"},
                           {"quantity": 10, "price": "0.99"}],
            "store_availability": "In Stock",
        }

    def get_farnell_by_sku(sku):  return _dummy(f"Farnell SKU {sku}")
    def get_lcsc_data(sku):       return _dummy(f"LCSC {sku}")
    def get_mouser_data(mpn):     return _dummy(f"Mouser {mpn}")


# ── Configuració d'estoc ──────────────────────────────────────────────────────

class StockConfig:
    STOCK      = 9 #0
    STORAGE    = 10 #1
    REFERENCE  = 5 #3

    # GOOGLE_SHEET_ID = "1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA"                # personal Stock
    GOOGLE_SHEET_ID = "1jTJQL-PM7Uq1Gvns65RWnZOWWBl-359ZsKDoc6suoGQ"                # personal Stock22
    # GOOGLE_CREDENTIALS_JSON = "credentials/mystock-482208-a553ed840217.json"        # personal
    GOOGLE_CREDENTIALS_JSON = "credentials/mystock-482208-9ff7a94ae596.json"        # personal2


def resource_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


# ── StockChecker ──────────────────────────────────────────────────────────────

class StockChecker:
    def __init__(self):
        self._data: List[List[str]] = []
        self._loaded    = False
        self._worksheet = None

    def load(self) -> bool:
        try:
            import gspread
            from google.oauth2.service_account import Credentials as GCreds

            creds_path = resource_path(StockConfig.GOOGLE_CREDENTIALS_JSON)
            if not creds_path.exists():
                print(f"[StockChecker] Credencials no trobades: {creds_path}")
                return False

            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds  = GCreds.from_service_account_file(str(creds_path), scopes=SCOPES)
            client = gspread.authorize(creds)
            sheet  = client.open_by_key(StockConfig.GOOGLE_SHEET_ID)

            self._worksheet = sheet.sheet1
            self._data      = self._worksheet.get_all_values()

            if not self._data:
                print("[StockChecker] Full d'estoc buit.")
                return False

            self._loaded = True
            print(f"[StockChecker] {len(self._data) - 1} files carregades.")
            return True

        except Exception as e:
            print(f"[StockChecker] Error en carregar: {type(e).__name__}: {e}")
            return False

    def find(self, *search_terms: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        if not self._loaded or len(self._data) < 2:
            return None, None, None

        terms = [t.strip().lower() for t in search_terms if t and t.strip()]
        if not terms:
            return None, None, None

        for i, row in enumerate(self._data[1:], start=2):
            ref = row[StockConfig.REFERENCE].strip().lower()
            if any(term == ref for term in terms):
                return (
                    row[StockConfig.STOCK].strip() or "0",
                    row[StockConfig.STORAGE].strip() or "—",
                    i,
                )

        for i, row in enumerate(self._data[1:], start=2):
            ref = row[StockConfig.REFERENCE].strip().lower()
            if any(term in ref or ref in term for term in terms):
                return (
                    row[StockConfig.STOCK].strip() or "0",
                    row[StockConfig.STORAGE].strip() or "—",
                    i,
                )

        return None, None, None

    def update_row(self, sheet_row: int, qty: str, storage: str) -> bool:
        if not self._loaded or self._worksheet is None:
            print("[StockChecker] No es pot escriure: estoc no carregat.")
            return False

        try:
            stock_col   = StockConfig.STOCK   + 1
            storage_col = StockConfig.STORAGE + 1

            self._worksheet.update_cell(sheet_row, stock_col,   qty)
            self._worksheet.update_cell(sheet_row, storage_col, storage)

            row_idx = sheet_row - 1
            if 0 <= row_idx < len(self._data):
                self._data[row_idx][StockConfig.STOCK]   = qty
                self._data[row_idx][StockConfig.STORAGE] = storage

            print(f"[StockChecker] Fila {sheet_row} actualitzada → qty={qty!r}, storage={storage!r}")
            return True

        except Exception as e:
            print(f"[StockChecker] Error en escriure: {type(e).__name__}: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# ── Lògica de detecció i parsing ─────────────────────────────────────────────

def detect_supplier(code: str) -> str:
    c = code.strip().upper()
    if re.fullmatch(r"C\d+", c):    return "lcsc"
    if re.fullmatch(r"\d{6,8}", c): return "farnell"
    return "mouser"


def parse_barcode(data: str) -> dict:
    data = data.strip()

    is_lcsc_new = data.startswith("^") and "Ñ" in data
    is_lcsc_old = data.startswith("{") and "pbn:" in data

    if is_lcsc_new or is_lcsc_old:
        content = data.lstrip("^").rstrip("*") if is_lcsc_new else data.strip("{}")
        sep = "Ñ" if is_lcsc_new else ":"
        result = {}
        for field in content.split(","):
            if sep in field:
                k, v = field.split(sep, 1)
                result[k.strip()] = v.strip()
        return {
            "supplier":     "LCSC",
            "order_number": result.get("on"),
            "part_number":  result.get("pm"),
            "sku":          result.get("pc"),
            "quantity":     result.get("qty"),
        }

    if data.startswith("[)>") or data.startswith(">[)>"):
        return _parse_mouser_barcode(data)

    if re.search(r'\(1P\)|\(10V\)|10V\d', data):
        result = {"supplier": "Farnell"}
        for ai, fname in [("1P", "sku"), ("10V", "order_ref"),
                          ("Q",  "quantity"), ("4L", "country")]:
            m = re.search(r'\(' + re.escape(ai) + r'\)([^(]+)', data)
            if m:
                result[fname] = m.group(1).strip()
        if "sku" not in result:
            for ai, fname in [("10V", "order_ref"), ("1P", "sku"),
                               ("Q",  "quantity"),  ("4L", "country")]:
                m = re.search(re.escape(ai) + r'(\S+)', data)
                if m:
                    result[fname] = m.group(1)
        return result

    return {"supplier": "Unknown", "raw": data}


def _parse_mouser_barcode(data: str) -> dict:
    body = re.sub(r'^[>\[\]()]+>?\d*', '', data)

    FIELDS = [
        ("11K", "order_number"), ("1P",  "part_number"),
        ("1T",  "lot_number"),   ("1V",  "manufacturer"),
        ("4L",  "country"),      ("0D",  "date_code"),
        ("9D",  "date_code"),    ("4K",  "line_number"),
        ("1K",  "order_line"),   ("Q",   "quantity"),
        ("P",   "mfr_part"),     ("K",   "customer_po"),
    ]

    if "\x1d" in body:
        result = {"supplier": "Mouser"}
        for part in body.split("\x1d"):
            part = part.strip()
            for fid, fname in FIELDS:
                if part.startswith(fid):
                    result.setdefault(fname, part[len(fid):])
                    break
        return result

    hits = []
    for fid, fname in FIELDS:
        for m in re.finditer(re.escape(fid), body):
            pos_after = m.end()
            if fid == "Q" and (pos_after >= len(body) or not body[pos_after].isdigit()):
                continue
            hits.append((m.start(), m.end(), fid, fname))

    hits.sort(key=lambda x: (x[0], -len(x[2])))
    filtered, prev_end, seen_names = [], 0, set()
    for start, end, fid, fname in hits:
        if start >= prev_end:
            if fname not in seen_names or fname == "mfr_part":
                filtered.append((start, end, fid, fname))
                prev_end = end
                seen_names.add(fname)

    result = {"supplier": "Mouser"}
    for i, (start, end, fid, fname) in enumerate(filtered):
        nxt = filtered[i + 1][0] if i + 1 < len(filtered) else len(body)
        result.setdefault(fname, body[end:nxt].strip())

    pn = result.get("part_number", "")
    if "," in pn:
        result["part_number"] = pn.split(",")[0].strip()
    if not result.get("part_number") and result.get("mfr_part"):
        result["part_number"] = result["mfr_part"]

    return result


def fetch_component(code: str):
    code = code.strip()

    is_lcsc_bc = (code.startswith("{") and "pbn:" in code) or \
                 (code.startswith("^") and "Ñ" in code)
    if is_lcsc_bc:
        parsed = parse_barcode(code)
        sku = parsed.get("sku")
        if not sku:
            raise ValueError("No s'ha trobat el camp 'pc' (SKU) al codi LCSC.")
        return get_lcsc_data(sku), "LCSC"

    if code.startswith("[)>") or code.startswith(">[)>"):
        parsed = parse_barcode(code)
        mpn = (parsed.get("part_number") or parsed.get("mfr_part") or "").strip()
        if not mpn:
            raise ValueError(f"No s'ha trobat el part number al codi Mouser.\nParse: {parsed}")
        return get_mouser_data(mpn), "Mouser"

    if re.search(r'\(1P\)|\(10V\)|10V\d', code):
        parsed = parse_barcode(code)
        sku = parsed.get("sku", "").strip()
        if not sku:
            raise ValueError("No s'ha trobat el SKU al codi Farnell.")
        return get_farnell_by_sku(sku), "Farnell"

    supplier = detect_supplier(code)
    if supplier == "farnell": return get_farnell_by_sku(code), "Farnell"
    if supplier == "lcsc":    return get_lcsc_data(code),      "LCSC"
    return get_mouser_data(code), "Mouser"


# ── Preus ─────────────────────────────────────────────────────────────────────

def parse_prices(price_unit) -> list:
    if not price_unit:
        return []
    if isinstance(price_unit, list):
        result = []
        for entry in price_unit:
            if not isinstance(entry, dict):
                continue
            qty = entry.get("quantity") or entry.get("Quantity") or entry.get("qty") or "?"
            raw = str(entry.get("price") or entry.get("Price") or entry.get("unit_price") or "?")
            raw = raw.replace("€","").replace("$","").replace("£","").replace(",",".").strip()
            result.append({"quantity": qty, "price": raw})
        return result
    return [{"quantity": 1, "price": str(price_unit)}]


def is_out_of_stock(avail: str) -> bool:
    """Retorna True si la disponibilitat indica que no hi ha estoc a la botiga."""
    print(avail)
    if not avail:
        return False
    a = avail.strip().lower()
    return a in ("0", "out of stock", "no stock", "discontinued",
                 "not available", "unavailable", "eol", "obsolete", "", "None")


# ── Signals ───────────────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    finished      = Signal(dict, str)
    error         = Signal(str)
    stock_found   = Signal(str, str, int)
    stock_missing = Signal()
    save_ok       = Signal()
    save_error    = Signal(str)


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE — myStock coherent: gris base, caixa blanca centrada, controls plans
# ══════════════════════════════════════════════════════════════════════════════
STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #1f1f1f;
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 12px;
}

/* ── Barra de cerca ── */
QLineEdit#lineEdit_search_box {
    background-color: #ffffff;
    color: #1f1f1f;
    border: 1px solid #acacac;
    border-radius: 2px;
    padding: 5px 8px;
    font-size: 13px;
    min-height: 22px;
    selection-background-color: #0078d7;
    selection-color: #ffffff;
}
QLineEdit#lineEdit_search_box:focus {
    border-color: #0078d7;
}

QPushButton#pushButton_search_button {
    background-color: #e1e1e1;
    color: #1f1f1f;
    border: 1px solid #acacac;
    border-radius: 2px;
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
    min-width: 80px;
    padding: 0 16px;
}
QPushButton#pushButton_search_button:hover {
    background-color: #d4e8f8;
    border-color: #0078d7;
}
QPushButton#pushButton_search_button:pressed {
    background-color: #b8d8f0;
    border-color: #005fa3;
}
QPushButton#pushButton_search_button:disabled {
    background-color: #f4f4f4;
    color: #a0a0a0;
    border-color: #d0d0d0;
}

/* ══ CAIXA PRINCIPAL — fons blanc, vora visible contra el gris base ══ */
QWidget#widget_result {
    background-color: #ffffff;
    border: 1px solid #c8c8c8;
    border-radius: 2px;
}
/* El widget interior i tots els fills hereten el fons blanc */
QWidget#widget_result QWidget,
QWidget#widget_result QLabel {
    background-color: #ffffff;
}

/* ── Nom del component ── */
QLabel#label_nomcompoennt {
    font-size: 14px;
    font-weight: 700;
    color: #1f1f1f;
    background-color: transparent;
}

/* ── Tag proveïdor ── */
QLabel#label_tagSupplier {
    background-color: #ebebeb;
    color: #404040;
    border: 1px solid #c0c0c0;
    border-radius: 2px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* ── Tag disponibilitat ── */
QLabel#label_tagAvailability {
    background-color: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #a5d6a7;
    border-radius: 2px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
/* Vermell quan out-of-stock */
QLabel#label_tagAvailability[out_of_stock="true"] {
    background-color: #ffebee;
    color: #c62828;
    border-color: #ef9a9a;
}

/* ── Descripció ── */
QLabel#label_description {
    font-size: 11px;
    color: #606060;
    background-color: transparent;
}

/* ── Labels de camp (text fix) ── */
QLabel#label_storetext,
QLabel#label_tipostext,
QLabel#label_fabricanttext,
QLabel#label_packagetext,
QLabel#label_pricetext,
QLabel#label_stocktext,
QLabel#label_storagetext {
    font-size: 11px;
    font-weight: 700;
    color: #505050;
    min-width: 72px;
    max-width: 90px;
    background-color: transparent;
}

/* ── Labels de valor ── */
QLabel#label_storevariable,
QLabel#label_tiposvariable,
QLabel#label_fabricantvariable,
QLabel#label_packagevariable {
    font-size: 11px;
    color: #1f1f1f;
    background-color: transparent;
}

/* ── LineEdits d'estoc (compactes) ── */
QLineEdit#lineEdit,
QLineEdit#lineEdit_storagevariable {
    background-color: #fafafa;
    color: #1f1f1f;
    border: 1px solid #c0c0c0;
    border-radius: 2px;
    padding: 2px 6px;
    font-size: 11px;
    max-width: 110px;
    min-width: 55px;
    selection-background-color: #0078d7;
    selection-color: #ffffff;
}
QLineEdit#lineEdit:focus,
QLineEdit#lineEdit_storagevariable:focus {
    border-color: #0078d7;
    background-color: #ffffff;
}
QLineEdit#lineEdit:disabled,
QLineEdit#lineEdit_storagevariable:disabled {
    background-color: #f4f4f4;
    color: #b0b0b0;
    border-color: #dcdcdc;
}
/* Verd — component trobat a l'estoc personal */
QLineEdit#lineEdit[stock_status="found"],
QLineEdit#lineEdit_storagevariable[stock_status="found"] {
    border-color: #4caf50;
    color: #2e7d32;
    font-weight: bold;
    background-color: #f1faf2;
}
/* Vermell — no trobat */
QLineEdit#lineEdit[stock_status="missing"],
QLineEdit#lineEdit_storagevariable[stock_status="missing"] {
    border-color: #ef9a9a;
    color: #c62828;
    background-color: #fff8f8;
    font-style: italic;
}
/* Ambre — desant */
QLineEdit#lineEdit[stock_status="saving"],
QLineEdit#lineEdit_storagevariable[stock_status="saving"] {
    border-color: #f9a825;
    background-color: #fffde7;
    color: #6d4c00;
}

/* ── Botons d'enllaç ── */
QLabel#label_botigalink,
QLabel#label_datasheetlink {
    font-size: 11px;
    color: #1f1f1f;
    padding: 4px 12px;
    border-radius: 2px;
    background-color: #ebebeb;
    border: 1px solid #c0c0c0;
}
QLabel#label_botigalink:hover,
QLabel#label_datasheetlink:hover {
    background-color: #d4e8f8;
    border-color: #0078d7;
}

/* ── Placeholder imatge ── */
QLabel#label_img_placeholder {
    background-color: #f4f4f4;
    border-radius: 2px;
    border: 1px solid #d8d8d8;
    color: #c8c8c8;
    font-size: 24px;
}

/* ── Menú i status bar ── */
QMenuBar {
    background-color: #f0f0f0;
    color: #1f1f1f;
    border-bottom: 1px solid #d0d0d0;
    font-size: 12px;
}
QMenuBar::item:selected { background-color: #d4e8f8; }
QMenu {
    background-color: #ffffff;
    border: 1px solid #acacac;
}
QMenu::item:selected { background-color: #d4e8f8; }

QStatusBar {
    background-color: #f0f0f0;
    font-size: 11px;
    border-top: 1px solid #d0d0d0;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #f0f0f0;
    width: 10px;
    border-left: 1px solid #e0e0e0;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    border-radius: 2px;
    min-height: 20px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover { background: #a0a0a0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


# ── Finestra principal ────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setStyleSheet(STYLE)
        self.setWindowTitle("Component Lookup — Mouser · Farnell · LCSC")
        # self.setMinimumSize(717, 557)

        # ── StockChecker ──────────────────────────────────────────────────────
        self._stock_checker    = StockChecker()
        self._stock_loading    = True
        self._last_search_code = ""
        self._current_stock_row: Optional[int] = None

        threading.Thread(target=self._load_stock_background, daemon=True).start()

        # ── Signals ───────────────────────────────────────────────────────────
        self._signals = WorkerSignals()
        self._signals.finished.connect(self._on_result)
        self._signals.error.connect(self._on_error)
        self._signals.stock_found.connect(self._on_stock_found)
        self._signals.stock_missing.connect(self._on_stock_missing)
        self._signals.save_ok.connect(self._on_save_ok)
        self._signals.save_error.connect(self._on_save_error)

        # ── Textos inicials ───────────────────────────────────────────────────
        self.ui.lineEdit_search_box.setPlaceholderText(
            "p.ex.  C17902  ·  2988437  ·  LM317  ·  [)>06…  ·  ^pbnÑ…"
        )
        self.ui.pushButton_search_button.setText("Cercar")

        # ── Labels d'estoc (text fix) ─────────────────────────────────────────
        self.ui.label_stocktext.setText("Estoc:")
        self.ui.label_storagetext.setText("Ubicació:")
        self._reset_stock_fields()

        # ── Amaga resultat fins que hi hagi dades ─────────────────────────────
        self.ui.widget_result.setVisible(False)

        # ── Ombra subtil a la caixa ───────────────────────────────────────────
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 22))
        self.ui.widget_result.setGraphicsEffect(shadow)

        # ── Widget imatge ─────────────────────────────────────────────────────
        img_layout = QVBoxLayout(self.ui.widget_imatge)
        img_layout.setContentsMargins(0, 0, 8, 0)
        self._img_label = QLabel()
        self._img_label.setObjectName("label_img_placeholder")
        self._img_label.setFixedSize(110, 110)
        self._img_label.setAlignment(Qt.AlignCenter)
        self._img_label.setFont(QFont("Segoe UI", 22))
        self._img_label.setText("·")
        img_layout.addWidget(self._img_label, 0, Qt.AlignCenter)

        # ── Contenidor de preus ───────────────────────────────────────────────
        self._price_layout = QHBoxLayout(self.ui.widget_priceContainer)
        self._price_layout.setContentsMargins(0, 0, 0, 0)
        self._price_layout.setSpacing(4)
        self._price_layout.setAlignment(Qt.AlignLeft)

        # ── Correccions de layout ─────────────────────────────────────────────
        self._fix_result_layouts()

        # ── Connexions UI ─────────────────────────────────────────────────────
        self.ui.pushButton_search_button.clicked.connect(self._on_search)
        self.ui.lineEdit_search_box.returnPressed.connect(self._on_search)

        self.ui.lineEdit.editingFinished.connect(self._on_stock_field_edited)
        self.ui.lineEdit_storagevariable.editingFinished.connect(self._on_stock_field_edited)

        # ── URLs d'enllaços ───────────────────────────────────────────────────
        self._store_url     = ""
        self._datasheet_url = ""

        self.ui.label_botigalink.mousePressEvent    = self._open_store
        self.ui.label_datasheetlink.mousePressEvent = self._open_datasheet
        self.ui.label_botigalink.setCursor(Qt.PointingHandCursor)
        self.ui.label_datasheetlink.setCursor(Qt.PointingHandCursor)

        self.ui.lineEdit_search_box.setFocus()

        # ── Navegació prev/next ───────────────────────────────────────────────────
        self._nav_list: List[str] = []
        self._nav_index: int = 0

        self.ui.pushButton.setText("◀  Anterior")
        self.ui.pushButton_2.setText("Següent  ▶")

        # Etiqueta de posició entre els dos botons (afegida per codi)
        self._nav_counter_label = QLabel("")
        self._nav_counter_label.setAlignment(Qt.AlignCenter)
        self._nav_counter_label.setStyleSheet(
            "font-size: 11px; color: #606060; background: transparent;"
        )
        # Insereix l'etiqueta entre pushButton i pushButton_2
        nav_layout = self.ui.horizontalLayout_10
        nav_layout.insertWidget(1, self._nav_counter_label)

        self.ui.pushButton.clicked.connect(self._nav_prev)
        self.ui.pushButton_2.clicked.connect(self._nav_next)
        self._update_nav_buttons()

    # ── Correccions de layout ─────────────────────────────────────────────────

    def _fix_result_layouts(self):
        """Ajusta polítiques de mida perquè el contingut quedi compacte i centrat."""
        compact = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        # Nom expandeix; tags compactes (el spacer del .ui ja separa nom dels tags)
        self.ui.label_nomcompoennt.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.ui.label_tagSupplier.setSizePolicy(compact)
        self.ui.label_tagAvailability.setSizePolicy(compact)

        # Botons d'enllaç: compactes + stretch al final
        self.ui.label_botigalink.setSizePolicy(compact)
        self.ui.label_datasheetlink.setSizePolicy(compact)
        self.ui.horizontalLayout_7.addStretch()

        # Camps d'estoc: amplada limitada perquè no s'estirin
        self.ui.lineEdit.setMaximumWidth(110)
        self.ui.lineEdit.setMinimumWidth(55)
        self.ui.lineEdit_storagevariable.setMaximumWidth(110)
        self.ui.lineEdit_storagevariable.setMinimumWidth(55)

    # ── Càrrega d'estoc en background ─────────────────────────────────────────

    def _load_stock_background(self):
        ok = self._stock_checker.load()
        self._stock_loading = False
        print("[StockChecker]", "Estoc carregat." if ok else "No s'ha pogut carregar l'estoc.")

    # ── Helpers dels camps d'estoc ────────────────────────────────────────────

    def _set_stock_status(self, status: str):
        for widget in (self.ui.lineEdit, self.ui.lineEdit_storagevariable):
            widget.setProperty("stock_status", status)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _reset_stock_fields(self):
        self.ui.lineEdit.clear()
        self.ui.lineEdit_storagevariable.clear()
        self.ui.lineEdit.setEnabled(False)
        self.ui.lineEdit_storagevariable.setEnabled(False)
        self._set_stock_status("")
        self._current_stock_row = None

    def _on_stock_found(self, qty: str, storage: str, sheet_row: int):
        self._current_stock_row = sheet_row
        self.ui.lineEdit.setText(qty)
        self.ui.lineEdit_storagevariable.setText(storage)
        self.ui.lineEdit.setEnabled(True)
        self.ui.lineEdit_storagevariable.setEnabled(True)
        self._set_stock_status("found")

    def _on_stock_missing(self):
        self._current_stock_row = None
        self.ui.lineEdit.clear()
        self.ui.lineEdit_storagevariable.clear()
        self.ui.lineEdit.setPlaceholderText("—")
        self.ui.lineEdit_storagevariable.setPlaceholderText("—")
        self.ui.lineEdit.setEnabled(False)
        self.ui.lineEdit_storagevariable.setEnabled(False)
        self._set_stock_status("missing")

    # ── Desar al Google Sheet ─────────────────────────────────────────────────

    def _on_stock_field_edited(self):
        if self._current_stock_row is None:
            return

        qty     = self.ui.lineEdit.text().strip()
        storage = self.ui.lineEdit_storagevariable.text().strip()

        self._set_stock_status("saving")
        self._set_status("Desant canvis…", "#6d4c00")

        row = self._current_stock_row

        def run():
            ok = self._stock_checker.update_row(row, qty, storage)
            if ok:
                self._signals.save_ok.emit()
            else:
                self._signals.save_error.emit("No s'han pogut desar els canvis al Google Sheet.")

        threading.Thread(target=run, daemon=True).start()

    def _on_save_ok(self):
        self._set_stock_status("found")
        self._set_status("Canvis desats correctament.", "#2e7d32")

    def _on_save_error(self, msg: str):
        self._set_stock_status("found")
        self._set_status(f"Error: {msg}", "#c62828")

    # ── Cerca de component ────────────────────────────────────────────────────

    def _search_stock(self, search_code: str, component: dict):
        waited = 0
        while self._stock_loading and waited < 15:
            time.sleep(0.2)
            waited += 0.2

        if not self._stock_checker.is_loaded:
            return

        component_name = str(component.get("name", "")).strip()
        qty, storage, row = self._stock_checker.find(search_code, component_name)

        if qty is not None:
            self._signals.stock_found.emit(qty, storage, row)
        else:
            self._signals.stock_missing.emit()

    # def _on_search(self):
    #     code = self.ui.lineEdit_search_box.text().strip()
    #     if not code:
    #         return

    #     self._last_search_code = code
    #     self._reset_stock_fields()

    #     self.ui.widget_result.setVisible(False)
    #     self.ui.pushButton_search_button.setEnabled(False)
    #     self._set_status(f"Cercant «{code}»…", "#505050")

    #     def run():
    #         try:
    #             comp, supplier = fetch_component(code)
    #             self._signals.finished.emit(comp, supplier)
    #         except Exception as exc:
    #             self._signals.error.emit(str(exc))

    #     threading.Thread(target=run, daemon=True).start()

    def _on_search(self):
        code = self.ui.lineEdit_search_box.text().strip()
        if not code:
            return

        # ── Extreu l'identificador efectiu per a la cerca d'estoc ──────────────
        parsed = parse_barcode(code)
        supplier = parsed.get("supplier", "Unknown")

        if supplier == "LCSC":
            effective_code = parsed.get("sku") or parsed.get("part_number") or code
        elif supplier == "Mouser":
            effective_code = parsed.get("part_number") or parsed.get("mfr_part") or code
        elif supplier == "Farnell":
            effective_code = parsed.get("sku") or code
        else:
            effective_code = code  # entrada manual: ja és l'identificador

        self._last_search_code = effective_code  # ← ara és "C434068", no el QR sencer
        # ───────────────────────────────────────────────────────────────────────

        self._reset_stock_fields()
        self.ui.widget_result.setVisible(False)
        self.ui.pushButton_search_button.setEnabled(False)
        self._set_status(f"Cercant «{code}»…", "#505050")

        def run():
            try:
                comp, supplier = fetch_component(code)  # fetch_component segueix rebent el codi original
                self._signals.finished.emit(comp, supplier)
            except Exception as exc:
                self._signals.error.emit(str(exc))

        threading.Thread(target=run, daemon=True).start()

    def _on_result(self, component: dict, supplier: str):
        self.ui.pushButton_search_button.setEnabled(True)
        name = component.get("name", "")
        self._set_status(f"{name}  ·  {supplier}", "#2e7d32")

        self._populate_result(component, supplier)
        self.ui.widget_result.setVisible(True)

        threading.Thread(
            target=self._search_stock,
            args=(self._last_search_code, component),
            daemon=True
        ).start()

    def _on_error(self, msg: str):
        self.ui.pushButton_search_button.setEnabled(True)
        self._set_status(f"Error: {msg}", "#c62828")

    def _set_status(self, text: str, color: str):
        """Mostra l'estat a la statusbar de la finestra."""
        self.statusBar().setStyleSheet(
            f"color: {color}; font-size: 11px; background: #f0f0f0;"
        )
        self.statusBar().showMessage(text)

    # ── Emplena la targeta de resultat ────────────────────────────────────────

    # def _populate_result(self, component: dict, supplier: str):
    #     self.ui.label_nomcompoennt.setText(component.get("name", "—"))
    #     self.ui.label_tagSupplier.setText(supplier)

    #     # ── Tag disponibilitat: verd/vermell segons estoc botiga ──────────────
    #     avail = str(component.get("store_availability") or "")
    #     oos   = is_out_of_stock(avail)

    #     if avail:
    #         display_avail = "Sense estoc" if oos else avail
    #         self.ui.label_tagAvailability.setText(display_avail)
    #         self.ui.label_tagAvailability.setProperty(
    #             "out_of_stock", "true" if oos else "false"
    #         )
    #         self.ui.label_tagAvailability.style().unpolish(self.ui.label_tagAvailability)
    #         self.ui.label_tagAvailability.style().polish(self.ui.label_tagAvailability)
    #         self.ui.label_tagAvailability.setVisible(True)
    #     else:
    #         self.ui.label_tagAvailability.setVisible(False)

    def _populate_result(self, component: dict, supplier: str):
        self.ui.label_nomcompoennt.setText(component.get("name", "—"))
        self.ui.label_tagSupplier.setText(supplier)

        # ── Tag disponibilitat: verd/vermell segons estoc botiga ──────────────
        # Convertim primer a string per evitar que 0 (enter) es tracti com buit
        # raw_avail = component.get("store_availability")
        # avail     = str(raw_avail).strip() if raw_avail is not None else ""
        # oos       = is_out_of_stock(avail)
        raw_avail = component.get("store_availability")

        # None explícit (p.ex. Mouser) → tractem com a absent
        # if raw_avail is None:
        #     avail = ""
        # else:
        avail = str(raw_avail).strip()
        # Filtra el cas que l'API retorni literalment el string "None" o "null"
        # if avail.lower() in ("none", "null", "n/a", "-"):
        #     avail = ""

        oos = is_out_of_stock(avail)

        if avail:
            display_avail = "Sense estoc" if oos else avail
            self.ui.label_tagAvailability.setText(display_avail)
            self.ui.label_tagAvailability.setProperty(
                "out_of_stock", "true" if oos else "false"
            )
            self.ui.label_tagAvailability.style().unpolish(self.ui.label_tagAvailability)
            self.ui.label_tagAvailability.style().polish(self.ui.label_tagAvailability)
            self.ui.label_tagAvailability.setVisible(True)
        else:
            self.ui.label_tagAvailability.setVisible(False)

        desc = str(component.get("description") or "")
        self.ui.label_description.setText(desc)
        self.ui.label_description.setWordWrap(True)

        self.ui.label_storevariable.setText(str(component.get("store_name") or "—"))
        self.ui.label_tiposvariable.setText(str(component.get("type2") or "—"))
        self.ui.label_fabricantvariable.setText(str(component.get("manufacturer") or "—"))
        self.ui.label_packagevariable.setText(str(component.get("package") or "—"))

        # ── Preus ──────────────────────────────────────────────────────────────
        self._clear_price_pills()
        prices = parse_prices(component.get("price_unit"))
        if prices:
            for entry in prices[:3]:
                qty_p  = entry.get("quantity", "?")
                price  = entry.get("price", "?")
                try:
                    price_str = f"{float(price):.4f}".rstrip("0").rstrip(".") + " €"
                except (ValueError, TypeError):
                    price_str = f"{price} €"

                pill = QWidget()
                pill.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
                pill.setStyleSheet(
                    "background-color: #f4f4f4;"
                    "border-radius: 2px;"
                    "border: 1px solid #d8d8d8;"
                )
                pill_lay = QVBoxLayout(pill)
                pill_lay.setContentsMargins(8, 3, 8, 3)
                pill_lay.setSpacing(1)

                qty_lbl = QLabel(f"≥ {qty_p} ut")
                qty_lbl.setFont(QFont("Segoe UI", 8))
                qty_lbl.setStyleSheet(
                    "color: #888888; background: transparent; border: none;"
                )
                qty_lbl.setAlignment(Qt.AlignCenter)

                price_lbl = QLabel(price_str)
                price_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
                price_lbl.setStyleSheet(
                    "color: #1f1f1f; background: transparent; border: none;"
                )
                price_lbl.setAlignment(Qt.AlignCenter)

                pill_lay.addWidget(qty_lbl)
                pill_lay.addWidget(price_lbl)
                self._price_layout.addWidget(pill)
            self._price_layout.addStretch()
        else:
            lbl = QLabel("—")
            lbl.setStyleSheet("color: #606060; background: transparent;")
            self._price_layout.addWidget(lbl)

        # ── Botiga ─────────────────────────────────────────────────────────────
        raw_store = component.get("store")
        if isinstance(raw_store, list):
            raw_store = raw_store[0] if raw_store else None
        self._store_url = str(raw_store).strip() if raw_store else ""
        valid_store = bool(self._store_url and
                           self._store_url.lower() not in ("none", "null", "n/a", ""))
        self.ui.label_botigalink.setVisible(valid_store)
        if valid_store:
            self.ui.label_botigalink.setText("🛒  Botiga")

        # ── Datasheet ──────────────────────────────────────────────────────────
        raw_ds = component.get("datasheet")
        if isinstance(raw_ds, list):
            raw_ds = raw_ds[0] if raw_ds else None
        self._datasheet_url = str(raw_ds).strip() if raw_ds else ""
        valid_ds = bool(self._datasheet_url and
                        self._datasheet_url.lower() not in ("none", "null", "n/a", ""))
        self.ui.label_datasheetlink.setVisible(valid_ds)
        if valid_ds:
            self.ui.label_datasheetlink.setText("📄  Datasheet")

        # ── Imatge ─────────────────────────────────────────────────────────────
        self._img_label.setText("·")
        self._img_label.setPixmap(QPixmap())

        img_url = component.get("image", "")
        if isinstance(img_url, list):
            img_url = img_url[0] if img_url else ""
        img_url = str(img_url).strip()

        if img_url:
            self._nam = QNetworkAccessManager()
            self._nam.finished.connect(self._on_image_loaded)
            req = QNetworkRequest(QUrl(img_url))
            req.setRawHeader(
                QByteArray(b"User-Agent"),
                QByteArray(b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           b"AppleWebKit/537.36 Chrome/120 Safari/537.36")
            )
            req.setRawHeader(
                QByteArray(b"Accept"),
                QByteArray(b"image/webp,image/apng,image/*,*/*;q=0.8")
            )
            req.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute, True)
            self._nam.get(req)
        else:
            self._img_label.setText("🖼️")

    def _clear_price_pills(self):
        while self._price_layout.count():
            item = self._price_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_image_loaded(self, reply):
        data = reply.readAll()
        pix  = QPixmap()
        if pix.loadFromData(data):
            self._img_label.setText("")
            self._img_label.setStyleSheet(
                "background-color: #ffffff;"
                "border-radius: 2px;"
                "border: 1px solid #d8d8d8;"
            )
            self._img_label.setPixmap(
                pix.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self._img_label.setText("🖼️")
        reply.deleteLater()

    def _open_store(self, _event=None):
        if self._store_url:
            QDesktopServices.openUrl(QUrl(self._store_url))

    def _open_datasheet(self, _event=None):
        if self._datasheet_url:
            QDesktopServices.openUrl(QUrl(self._datasheet_url))

    def search(self, code: str):
        """Llança una cerca programàticament."""
        self.ui.lineEdit_search_box.setText(code)
        self._on_search()

    # ── Navegació per la llista filtrada ─────────────────────────────────────

    def set_navigation_list(self, references: List[str], current_index: int):
        """Rep la llista filtrada de mystock i l'índex del component actual."""
        self._nav_list = references
        self._nav_index = current_index
        self._update_nav_buttons()

    def _nav_prev(self):
        if self._nav_index > 0:
            self._nav_index -= 1
            self.search(self._nav_list[self._nav_index])
            self._update_nav_buttons()

    def _nav_next(self):
        if self._nav_index < len(self._nav_list) - 1:
            self._nav_index += 1
            self.search(self._nav_list[self._nav_index])
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        has_list = len(self._nav_list) > 0
        self.ui.pushButton.setEnabled(has_list and self._nav_index > 0)
        self.ui.pushButton_2.setEnabled(has_list and self._nav_index < len(self._nav_list) - 1)
        if has_list:
            self._nav_counter_label.setText(
                f"{self._nav_index + 1} / {len(self._nav_list)}"
            )
        else:
            self._nav_counter_label.setText("")

    def closeEvent(self, event):
        super().closeEvent(event)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 11))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()