"""
Component Lookup App
Cerca components electrònics de Mouser, Farnell i LCSC
escaneig de codi de barres/QR o entrada manual.
"""

import re
import sys
import threading

from PySide6.QtCore import Qt, Signal, QObject, QUrl
from PySide6.QtGui import QFont, QPixmap, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

# ── Importa les funcions dels proveïdors ─────────────────────────────────────
try:
    from request_farnell import get_farnell_by_sku
    from request_lcsc import get_lcsc_data
    from request_mouser import get_mouser_data
except ImportError as e:
    print(f"[AVÍS] No s'han pogut importar els mòduls de proveïdor: {e}")

    def _dummy_component(name):
        return {
            "name": name,
            "store_name": "Demo Store",
            "description": "Component de prova (mòduls no carregats)",
            "type2": "IC",
            "manufacturer": "Demo Mfr",
            "package": "SOT-23",
            "datasheet": "https://example.com/datasheet.pdf",
            "store": "https://example.com",
            "image": "",
            "price_unit": "1.23",
            "store_availability": "In Stock",
        }

    def get_farnell_by_sku(sku):
        return _dummy_component(f"Farnell SKU {sku}")

    def get_lcsc_data(sku):
        return _dummy_component(f"LCSC {sku}")

    def get_mouser_data(mpn):
        return _dummy_component(f"Mouser {mpn}")


# ── Helpers ──────────────────────────────────────────────────────────────────

def detect_supplier(code: str) -> str:
    code = code.strip().upper()
    if re.fullmatch(r"C\d+", code):
        return "lcsc"
    if re.fullmatch(r"\d{6,8}", code):
        return "farnell"
    return "mouser"


def parse_barcode(data: str) -> dict:
    data = data.strip()

    # ── LCSC ──
    if data.startswith("{") and "pbn:" in data:
        content = data.strip("{}")
        result = {}
        for field in content.split(","):
            if ":" in field:
                k, v = field.split(":", 1)
                result[k.strip()] = v.strip()
        return {
            "supplier": "LCSC",
            "order_number": result.get("on"),
            "part_number": result.get("pm"),
            "sku": result.get("pc"),
            "quantity": result.get("qty"),
        }

    # ── Mouser ──
    if data.startswith(">[)>"):
        parts = data.split("\x1d")
        result = {"supplier": "Mouser"}
        for part in parts:
            if part.startswith("K"):
                result["order_number"] = part[1:]
            elif part.startswith("1P"):
                result["part_number"] = part[2:]
            elif part.startswith("Q"):
                result["quantity"] = part[1:]
            elif part.startswith("4L"):
                result["lot"] = part[2:]
        return result

    return {"supplier": "Unknown", "raw": data}


def fetch_component(code: str):
    """Retorna (component_dict, supplier_str) o llança una excepció."""
    code = code.strip()

    # Codis de barres de proveïdors
    if code.startswith("{") and "pbn:" in code:
        parsed = parse_barcode(code)
        sku = parsed.get("sku")
        if not sku:
            raise ValueError("No s'ha trobat el camp 'pc' (SKU) al codi LCSC.")
        return get_lcsc_data(sku), "LCSC"

    if code.startswith(">[)>"):
        parsed = parse_barcode(code)
        mpn = parsed.get("part_number")
        if not mpn:
            raise ValueError("No s'ha trobat el 'part_number' al codi Mouser.")
        return get_mouser_data(mpn), "Mouser"

    # Entrada manual: detecta proveïdor pel format
    supplier = detect_supplier(code)
    if supplier == "farnell":
        return get_farnell_by_sku(code), "Farnell"
    elif supplier == "lcsc":
        return get_lcsc_data(code), "LCSC"
    else:
        return get_mouser_data(code), "Mouser"


# ── Signals helper (per threading) ───────────────────────────────────────────

class WorkerSignals(QObject):
    finished = Signal(dict, str)
    error    = Signal(str)


# ── Estils ───────────────────────────────────────────────────────────────────

STYLE = """
/*QMainWindow, QWidget#central {
    background-color: #1e1e2e;
}*/

QLineEdit#searchBox {
    background-color: #2a2a3e;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 15px;
}
QLineEdit#searchBox:focus {
    border-color: #89b4fa;
}

QPushButton#searchBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 15px;
    font-weight: bold;
    min-height: 44px;
}
QPushButton#searchBtn:hover {
    background-color: #74c7ec;
}
QPushButton#searchBtn:pressed {
    background-color: #89dceb;
}
QPushButton#searchBtn:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QFrame#card {
    background-color: #2a2a3e;
    border-radius: 14px;
    border: 1px solid #45475a;
}

QLabel#tagSupplier {
    background-color: #1e3a2e;
    color: #a6e3a1;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#tagAvail {
    background-color: #3a3020;
    color: #f9e2af;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 11px;
}

QPushButton#linkBtn {
    background-color: #313244;
    color: #89b4fa;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 13px;
}
QPushButton#linkBtn:hover {
    background-color: #45475a;
}
"""


# ── Widgets ───────────────────────────────────────────────────────────────────

class FieldRow(QWidget):
    """Una fila amb etiqueta + valor."""
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 1, 0, 1)
        lay.setSpacing(10)

        lbl = QLabel(label + ":")
        lbl.setFixedWidth(130)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #7f849c; background: transparent;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

        val = QLabel(value or "—")
        val.setFont(QFont("Segoe UI", 10))
        val.setStyleSheet("color: #cdd6f4; background: transparent;")
        val.setWordWrap(True)
        val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lay.addWidget(lbl)
        lay.addWidget(val)


def parse_prices(price_unit) -> list:
    """Normalitza price_unit sigui llista de dicts, string o None.
    Suporta format LCSC  {'quantity': 100, 'price': '0.0039'}
    i format Mouser      {'Quantity': 10,  'Price': '0,168 €', 'Currency': 'EUR'}
    """
    if not price_unit:
        return []
    if isinstance(price_unit, list):
        result = []
        for entry in price_unit:
            if not isinstance(entry, dict):
                continue
            # Claus en minúscula (LCSC) o majúscula (Mouser)
            qty = (entry.get("quantity") or entry.get("Quantity") or
                   entry.get("qty") or "?")
            raw_price = (entry.get("price") or entry.get("Price") or
                         entry.get("unit_price") or "?")
            # Neteja: elimina símbol de moneda i espais, substitueix coma per punt
            raw_price = str(raw_price).replace("€", "").replace("$", "") \
                                      .replace("£", "").replace(",", ".").strip()
            result.append({"quantity": qty, "price": raw_price})
        return result
    return [{"quantity": 1, "price": str(price_unit)}]


class PriceTableWidget(QWidget):
    """Pastilles de preu per escales de quantitat."""

    def __init__(self, price_unit, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 2, 0, 2)
        main.setSpacing(10)

        lbl = QLabel("Preus:")
        lbl.setFixedWidth(130)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #7f849c; background: transparent;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
        main.addWidget(lbl)

        prices = parse_prices(price_unit)

        if not prices:
            val = QLabel("—")
            val.setFont(QFont("Segoe UI", 10))
            val.setStyleSheet("color: #cdd6f4; background: transparent;")
            main.addWidget(val)
            main.addStretch()
            return

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        flow = QHBoxLayout(container)
        flow.setContentsMargins(0, 0, 0, 0)
        flow.setSpacing(6)
        flow.setAlignment(Qt.AlignLeft)

        for entry in prices:
            qty   = entry.get("quantity", "?")
            price = entry.get("price", "?")
            try:
                price_f   = float(price)
                price_str = f"{price_f:.4f}".rstrip("0").rstrip(".") + " €"
            except (ValueError, TypeError):
                price_str = f"{price} €"

            pill = QWidget()
            pill.setStyleSheet(
                "background-color: #313244; border-radius: 8px; border: 1px solid #45475a;"
            )
            pill_lay = QVBoxLayout(pill)
            pill_lay.setContentsMargins(10, 5, 10, 5)
            pill_lay.setSpacing(1)

            qty_lbl = QLabel(f"≥ {qty} ut")
            qty_lbl.setFont(QFont("Segoe UI", 9))
            qty_lbl.setStyleSheet("color: #7f849c; background: transparent; border: none;")
            qty_lbl.setAlignment(Qt.AlignCenter)

            price_lbl = QLabel(price_str)
            price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            price_lbl.setStyleSheet("color: #a6e3a1; background: transparent; border: none;")
            price_lbl.setAlignment(Qt.AlignCenter)

            pill_lay.addWidget(qty_lbl)
            pill_lay.addWidget(price_lbl)
            flow.addWidget(pill)

        flow.addStretch()
        main.addWidget(container, 1)


class ComponentCard(QFrame):
    """Targeta amb tota la info d'un component."""

    def __init__(self, component: dict, supplier: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        from PySide6.QtGui import QColor
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(20)

        # ── Imatge ──
        self.img_label = QLabel("⏳")
        self.img_label.setFixedSize(130, 130)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFont(QFont("Segoe UI", 24))
        self.img_label.setStyleSheet(
            "background-color: #313244; border-radius: 10px; color: #45475a;"
        )
        outer.addWidget(self.img_label, 0, Qt.AlignTop)

        # ── Columna info ──
        info = QVBoxLayout()
        info.setSpacing(6)

        # Nom + etiquetes
        header = QHBoxLayout()
        header.setSpacing(8)

        name_lbl = QLabel(component.get("name", "—"))
        name_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        name_lbl.setStyleSheet("color: #cdd6f4; background: transparent;")
        name_lbl.setWordWrap(True)
        header.addWidget(name_lbl, 1)

        tag_sup = QLabel(supplier)
        tag_sup.setObjectName("tagSupplier")
        header.addWidget(tag_sup, 0, Qt.AlignTop)

        avail = str(component.get("store_availability", "") or "")
        if avail:
            tag_av = QLabel(avail)
            tag_av.setObjectName("tagAvail")
            header.addWidget(tag_av, 0, Qt.AlignTop)

        info.addLayout(header)

        # Descripció
        desc = QLabel(component.get("description", "") or "")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #a6adc8; background: transparent; margin-bottom: 4px;")
        desc.setWordWrap(True)
        info.addWidget(desc)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #45475a; background: #45475a; max-height: 1px;")
        info.addWidget(sep)

        # Camps de detall
        fields = [
            ("Store name",  component.get("store_name")),
            ("Tipus",       component.get("type2")),
            ("Fabricant",   component.get("manufacturer")),
            ("Package",     component.get("package")),
        ]
        for label, value in fields:
            row = FieldRow(label, str(value) if value is not None else "—")
            info.addWidget(row)

        # Taula de preus per escales
        price_widget = PriceTableWidget(component.get("price_unit"))
        info.addWidget(price_widget)

        # Botons d'enllaç
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        store_url = component.get("store", "")
        if store_url:
            btn_store = QPushButton("🛒  Veure a la botiga")
            btn_store.setObjectName("linkBtn")
            btn_store.setCursor(Qt.PointingHandCursor)
            url = store_url
            btn_store.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
            btn_row.addWidget(btn_store)

        ds_url = component.get("datasheet", "")
        if ds_url:
            btn_ds = QPushButton("📄  Datasheet")
            btn_ds.setObjectName("linkBtn")
            btn_ds.setCursor(Qt.PointingHandCursor)
            url = ds_url
            btn_ds.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
            btn_row.addWidget(btn_ds)

        info.addLayout(btn_row)
        outer.addLayout(info)

        # ── Carrega la imatge de forma asíncrona ──
        img_url = component.get("image", "")
        # Alguns proveïdors retornen una llista d'URLs
        if isinstance(img_url, list):
            img_url = img_url[0] if img_url else ""
        img_url = str(img_url).strip() if img_url else ""
        if img_url:
            self._nam = QNetworkAccessManager()
            self._nam.finished.connect(self._on_image_loaded)
            self._nam.get(QNetworkRequest(QUrl(img_url)))
        else:
            self.img_label.setText("🖼️")

    def _on_image_loaded(self, reply):
        data = reply.readAll()
        pix = QPixmap()
        if pix.loadFromData(data):
            self.img_label.setText("")
            self.img_label.setPixmap(
                pix.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.img_label.setText("🖼️")
        reply.deleteLater()


# ── Finestra principal ────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Component Lookup — Mouser · Farnell · LCSC")
        self.setMinimumSize(820, 600)
        self.resize(1000, 740)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(32, 26, 32, 26)
        root.setSpacing(16)

        # ── Títol ──
        title = QLabel("🔍  Component Lookup")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        root.addWidget(title)

        subtitle = QLabel(
            "Escaneja o introdueix un codi de barres / MPN / SKU  ·  "
            "Mouser, Farnell o LCSC"
        )
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #585b70;")
        root.addWidget(subtitle)

        # ── Barra de cerca ──
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setFixedHeight(46)
        self.search_box.setPlaceholderText(
            "p.ex. C17902  ·  2988437  ·  LM317  ·  >[)>…  ·  {pbn:…}"
        )
        self.search_box.returnPressed.connect(self._on_search)

        self.search_btn = QPushButton("Cercar")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.setFixedSize(120, 46)
        self.search_btn.clicked.connect(self._on_search)

        search_row.addWidget(self.search_box)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        # ── Ajuda ràpida ──
        help_lbl = QLabel(
            "💡  <b style='color:#585b70'>Mouser</b>: MPN o codi >[)>&nbsp;&nbsp;"
            "<b style='color:#585b70'>LCSC</b>: C + números o codi {pbn:}&nbsp;&nbsp;"
            "<b style='color:#585b70'>Farnell</b>: 6–8 dígits"
        )
        help_lbl.setFont(QFont("Segoe UI", 10))
        help_lbl.setStyleSheet("color: #45475a;")
        help_lbl.setTextFormat(Qt.RichText)
        root.addWidget(help_lbl)

        # ── Estat ──
        self.status_label = QLabel("Introdueix un codi i prem Cercar o prem Intro.")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #585b70;")
        root.addWidget(self.status_label)

        # ── Àrea de resultats (scrollable) ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        root.addWidget(self.scroll)

        self.result_widget = QWidget()
        self.result_widget.setStyleSheet("background: transparent;")
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setAlignment(Qt.AlignTop)
        self.result_layout.setSpacing(16)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.result_widget)

        # Focus inicial al camp de cerca
        self.search_box.setFocus()

    # ── Slots ────────────────────────────────────────────────────────────────

    def _on_search(self):
        code = self.search_box.text().strip()
        if not code:
            return

        self._clear_results()
        self.search_btn.setEnabled(False)
        self.status_label.setStyleSheet("color: #f9e2af; font-size: 11px;")
        self.status_label.setText(f"⏳  Cercant «{code}»…")

        signals = WorkerSignals()
        signals.finished.connect(self._on_result)
        signals.error.connect(self._on_error)

        def run():
            try:
                comp, supplier = fetch_component(code)
                signals.finished.emit(comp, supplier)
            except Exception as exc:
                signals.error.emit(str(exc))

        threading.Thread(target=run, daemon=True).start()

    def _on_result(self, component: dict, supplier: str):
        self.search_btn.setEnabled(True)
        self.status_label.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        name = component.get("name", "")
        self.status_label.setText(f"✔  Component trobat: {name}  ·  Proveïdor: {supplier}")
        card = ComponentCard(component, supplier)
        self.result_layout.addWidget(card)

    def _on_error(self, msg: str):
        self.search_btn.setEnabled(True)
        self.status_label.setStyleSheet("color: #f38ba8; font-size: 11px;")
        self.status_label.setText(f"✘  Error: {msg}")

    def _clear_results(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


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