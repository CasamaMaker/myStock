# """
# Component Lookup App
# Cerca components electrònics de Mouser, Farnell i LCSC
# Escaneig de codi de barres/QR o entrada manual.
# """

# import re
# import sys
# import threading

# from PySide6.QtCore import Qt, Signal, QObject, QUrl, QByteArray
# from PySide6.QtGui import QFont, QPixmap, QDesktopServices, QColor
# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy,
#     QGraphicsDropShadowEffect
# )
# from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

# # ── Importa les funcions dels proveïdors ─────────────────────────────────────
# try:
#     from request_farnell import get_farnell_by_sku
#     from request_lcsc import get_lcsc_data
#     from request_mouser import get_mouser_data
# except ImportError as e:
#     print(f"[AVÍS] No s'han pogut importar els mòduls de proveïdor: {e}")

#     def _dummy(name):
#         return {
#             "name": name, "store_name": "Demo Store",
#             "description": "Component de prova (mòduls no carregats)",
#             "type2": "IC", "manufacturer": "Demo Mfr", "package": "SOT-23",
#             "datasheet": "https://example.com/datasheet.pdf",
#             "store": "https://example.com",
#             "image": "https://via.placeholder.com/130",
#             "price_unit": [{"quantity": 1, "price": "1.23"},
#                            {"quantity": 10, "price": "0.99"}],
#             "store_availability": "In Stock",
#         }

#     def get_farnell_by_sku(sku):  return _dummy(f"Farnell SKU {sku}")
#     def get_lcsc_data(sku):       return _dummy(f"LCSC {sku}")
#     def get_mouser_data(mpn):     return _dummy(f"Mouser {mpn}")


# # ── Lògica de detecció i parsing ─────────────────────────────────────────────

# def detect_supplier(code: str) -> str:
#     """Detecta proveïdor per format de codi manual."""
#     c = code.strip().upper()
#     if re.fullmatch(r"C\d+", c):       return "lcsc"
#     if re.fullmatch(r"\d{6,8}", c):    return "farnell"
#     return "mouser"


# def parse_barcode(data: str) -> dict:
#     """Descodifica codis de barres de Mouser, Farnell i LCSC."""
#     data = data.strip()

#     # ── LCSC ──────────────────────────────────────────────────────────────────
#     # Format nou:  ^pbnÑPICK...,onÑSO...,pcÑC351421,...*
#     # Format antic: {pbn:PICK...,on:SO...,pc:C351421,...}
#     is_lcsc_new = data.startswith("^") and "Ñ" in data
#     is_lcsc_old = data.startswith("{") and "pbn:" in data

#     if is_lcsc_new or is_lcsc_old:
#         content = data.lstrip("^").rstrip("*") if is_lcsc_new else data.strip("{}")
#         sep = "Ñ" if is_lcsc_new else ":"
#         result = {}
#         for field in content.split(","):
#             if sep in field:
#                 k, v = field.split(sep, 1)
#                 result[k.strip()] = v.strip()
#         return {
#             "supplier": "LCSC",
#             "order_number": result.get("on"),
#             "part_number":  result.get("pm"),
#             "sku":          result.get("pc"),
#             "quantity":     result.get("qty"),
#         }

#     # ── Mouser ────────────────────────────────────────────────────────────────
#     # Format: [)>06K<PO>1P<MPN>Q<qty>11K<mouserPN>...
#     if data.startswith("[)>") or data.startswith(">[)>"):
#         body = re.sub(r'^[>\[\]()]+>?\d*', '', data)

#         FIELDS = [
#             ("11K", "mouser_part"),
#             ("1P",  "part_number"),
#             ("1K",  "order_line"),
#             ("4L",  "country"),
#             ("0D",  "date_code"),
#             ("K",   "customer_po"),
#             ("Q",   "quantity"),
#         ]

#         if "\x1d" in body:
#             result = {"supplier": "Mouser"}
#             for part in body.split("\x1d"):
#                 for fid, fname in FIELDS:
#                     if part.startswith(fid):
#                         result[fname] = part[len(fid):]
#                         break
#         else:
#             hits = []
#             for fid, fname in FIELDS:
#                 for m in re.finditer(re.escape(fid), body):
#                     hits.append((m.start(), m.end(), fid, fname))
#             hits.sort(key=lambda x: (x[0], -len(x[2])))
#             filtered, prev_end = [], 0
#             for start, end, fid, fname in hits:
#                 if start >= prev_end:
#                     filtered.append((start, end, fid, fname))
#                     prev_end = end
#             result = {"supplier": "Mouser"}
#             for i, (start, end, fid, fname) in enumerate(filtered):
#                 nxt = filtered[i + 1][0] if i + 1 < len(filtered) else len(body)
#                 result[fname] = body[end:nxt].strip()

#         return result

#     # ── Farnell ───────────────────────────────────────────────────────────────
#     # Format GS1-128 típic: (10V)<ref>  (1P)<sku>  (Q)<qty>  (4L)<country>
#     # Alguns lectors envien sense parèntesis: 10V<ref>1P<sku>Q<qty>
#     if re.search(r'\(1P\)|\(10V\)|10V\d', data):
#         # Extreu camps amb format (AI)value o sense parèntesis
#         result = {"supplier": "Farnell"}
#         # Amb parèntesis
#         for ai, fname in [("1P", "sku"), ("10V", "order_ref"),
#                           ("Q",  "quantity"), ("4L", "country")]:
#             m = re.search(r'\(' + re.escape(ai) + r'\)([^(]+)', data)
#             if m:
#                 result[fname] = m.group(1).strip()
#         # Fallback sense parèntesis — parser seqüencial
#         if "sku" not in result:
#             for ai, fname in [("10V", "order_ref"), ("1P", "sku"),
#                                ("Q",  "quantity"),  ("4L", "country")]:
#                 m = re.search(re.escape(ai) + r'(\S+)', data)
#                 if m:
#                     result[fname] = m.group(1)
#         return result

#     return {"supplier": "Unknown", "raw": data}


# def fetch_component(code: str):
#     """Retorna (component_dict, supplier_str) o llança una excepció."""
#     code = code.strip()

#     # LCSC barcode
#     is_lcsc_bc = (code.startswith("{") and "pbn:" in code) or \
#                  (code.startswith("^") and "Ñ" in code)
#     if is_lcsc_bc:
#         parsed = parse_barcode(code)
#         sku = parsed.get("sku")
#         if not sku:
#             raise ValueError("No s'ha trobat el camp 'pc' (SKU) al codi LCSC.")
#         return get_lcsc_data(sku), "LCSC"

#     # Mouser barcode
#     if code.startswith("[)>") or code.startswith(">[)>"):
#         parsed = parse_barcode(code)
#         mpn = parsed.get("part_number", "").strip()
#         if not mpn:
#             raise ValueError("No s'ha trobat el 'part_number' al codi Mouser.")
#         return get_mouser_data(mpn), "Mouser"

#     # Farnell barcode
#     if re.search(r'\(1P\)|\(10V\)|10V\d', code):
#         parsed = parse_barcode(code)
#         sku = parsed.get("sku", "").strip()
#         if not sku:
#             raise ValueError("No s'ha trobat el SKU al codi Farnell.")
#         return get_farnell_by_sku(sku), "Farnell"

#     # Entrada manual
#     supplier = detect_supplier(code)
#     if supplier == "farnell":  return get_farnell_by_sku(code), "Farnell"
#     if supplier == "lcsc":     return get_lcsc_data(code), "LCSC"
#     return get_mouser_data(code), "Mouser"


# # ── Preus ─────────────────────────────────────────────────────────────────────

# def parse_prices(price_unit) -> list:
#     """Normalitza price_unit de qualsevol format de proveïdor."""
#     if not price_unit:
#         return []
#     if isinstance(price_unit, list):
#         result = []
#         for entry in price_unit:
#             if not isinstance(entry, dict):
#                 continue
#             qty = (entry.get("quantity") or entry.get("Quantity") or
#                    entry.get("qty") or "?")
#             raw = str(entry.get("price") or entry.get("Price") or
#                       entry.get("unit_price") or "?")
#             # Neteja el format: elimina símbols de moneda, substitueix coma per punt
#             raw = raw.replace("€", "").replace("$", "").replace("£", "") \
#                      .replace(",", ".").strip()
#             result.append({"quantity": qty, "price": raw})
#         return result
#     return [{"quantity": 1, "price": str(price_unit)}]


# # ── Signals ───────────────────────────────────────────────────────────────────

# class WorkerSignals(QObject):
#     finished = Signal(dict, str)
#     error    = Signal(str)


# # ── Estils (tema clar) ────────────────────────────────────────────────────────

# STYLE = """
# /* Fons general */
# QMainWindow, QWidget#central {
#     background-color: #f0f2f5;
# }

# /* Camp de cerca */
# QLineEdit#searchBox {
#     background-color: #ffffff;
#     color: #1a1a2e;
#     border: 2px solid #d0d5e0;
#     border-radius: 10px;
#     padding: 10px 16px;
#     font-size: 15px;
# }
# QLineEdit#searchBox:focus {
#     border-color: #4a7bdc;
# }

# /* Botó cercar */
# QPushButton#searchBtn {
#     background-color: #4a7bdc;
#     color: #ffffff;
#     border: none;
#     border-radius: 10px;
#     font-size: 15px;
#     font-weight: bold;
#     min-height: 44px;
# }
# QPushButton#searchBtn:hover    { background-color: #3a6bcb; }
# QPushButton#searchBtn:pressed  { background-color: #2a5bba; }
# QPushButton#searchBtn:disabled { background-color: #c0c8dc; color: #8899bb; }

# /* Scroll area */
# QScrollArea { background: transparent; border: none; }
# QScrollArea > QWidget > QWidget { background: transparent; }
# QScrollBar:vertical {
#     background: #e8eaf0; width: 8px; border-radius: 4px;
# }
# QScrollBar::handle:vertical {
#     background: #b0b8cc; border-radius: 4px; min-height: 20px;
# }
# QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

# /* Targeta de component */
# QFrame#card {
#     background-color: #ffffff;
#     border-radius: 14px;
#     border: 1px solid #dde1ea;
# }

# /* Etiquetes de proveïdor i disponibilitat */
# QLabel#tagSupplier {
#     background-color: #e8f0fe;
#     color: #2a5bba;
#     border-radius: 6px;
#     padding: 2px 10px;
#     font-size: 11px;
#     font-weight: bold;
# }
# QLabel#tagAvail {
#     background-color: #e6f4ea;
#     color: #1e7e34;
#     border-radius: 6px;
#     padding: 2px 10px;
#     font-size: 11px;
#     font-weight: bold;
# }

# /* Botons d'enllaç */
# QPushButton#linkBtn {
#     background-color: #f0f4ff;
#     color: #4a7bdc;
#     border: 1px solid #c8d4f0;
#     border-radius: 8px;
#     padding: 6px 16px;
#     font-size: 13px;
# }
# QPushButton#linkBtn:hover { background-color: #dde8ff; }

# /* Imatge placeholder */
# QLabel#imgPlaceholder {
#     background-color: #f0f2f5;
#     border-radius: 10px;
#     border: 1px solid #e0e4ec;
#     color: #b0b8cc;
#     font-size: 28px;
# }
# """


# # ── Widgets ───────────────────────────────────────────────────────────────────

# class FieldRow(QWidget):
#     def __init__(self, label: str, value: str, parent=None):
#         super().__init__(parent)
#         self.setStyleSheet("background: transparent;")
#         lay = QHBoxLayout(self)
#         lay.setContentsMargins(0, 1, 0, 1)
#         lay.setSpacing(10)

#         lbl = QLabel(label + ":")
#         lbl.setFixedWidth(130)
#         lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
#         lbl.setStyleSheet("color: #7a8499; background: transparent;")
#         lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

#         val = QLabel(value or "—")
#         val.setFont(QFont("Segoe UI", 10))
#         val.setStyleSheet("color: #1a1a2e; background: transparent;")
#         val.setWordWrap(True)
#         val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

#         lay.addWidget(lbl)
#         lay.addWidget(val)


# class PriceTableWidget(QWidget):
#     def __init__(self, price_unit, parent=None):
#         super().__init__(parent)
#         self.setStyleSheet("background: transparent;")
#         main = QHBoxLayout(self)
#         main.setContentsMargins(0, 4, 0, 4)
#         main.setSpacing(10)

#         lbl = QLabel("Preus:")
#         lbl.setFixedWidth(130)
#         lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
#         lbl.setStyleSheet("color: #7a8499; background: transparent;")
#         lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
#         main.addWidget(lbl)

#         prices = parse_prices(price_unit)

#         if not prices:
#             val = QLabel("—")
#             val.setFont(QFont("Segoe UI", 10))
#             val.setStyleSheet("color: #1a1a2e; background: transparent;")
#             main.addWidget(val)
#             main.addStretch()
#             return

#         container = QWidget()
#         container.setStyleSheet("background: transparent;")
#         flow = QHBoxLayout(container)
#         flow.setContentsMargins(0, 0, 0, 0)
#         flow.setSpacing(6)
#         flow.setAlignment(Qt.AlignLeft)

#         for entry in prices:
#             qty   = entry.get("quantity", "?")
#             price = entry.get("price", "?")
#             try:
#                 price_str = f"{float(price):.4f}".rstrip("0").rstrip(".") + " €"
#             except (ValueError, TypeError):
#                 price_str = f"{price} €"

#             pill = QWidget()
#             pill.setStyleSheet(
#                 "background-color: #f5f7ff; border-radius: 8px;"
#                 "border: 1px solid #d0d8f0;"
#             )
#             pill_lay = QVBoxLayout(pill)
#             pill_lay.setContentsMargins(10, 5, 10, 5)
#             pill_lay.setSpacing(1)

#             qty_lbl = QLabel(f"≥ {qty} ut")
#             qty_lbl.setFont(QFont("Segoe UI", 9))
#             qty_lbl.setStyleSheet("color: #7a8499; background: transparent; border: none;")
#             qty_lbl.setAlignment(Qt.AlignCenter)

#             price_lbl = QLabel(price_str)
#             price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
#             price_lbl.setStyleSheet("color: #2e7d32; background: transparent; border: none;")
#             price_lbl.setAlignment(Qt.AlignCenter)

#             pill_lay.addWidget(qty_lbl)
#             pill_lay.addWidget(price_lbl)
#             flow.addWidget(pill)

#         flow.addStretch()
#         main.addWidget(container, 1)


# class ComponentCard(QFrame):
#     def __init__(self, component: dict, supplier: str, parent=None):
#         super().__init__(parent)
#         self.setObjectName("card")

#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(20)
#         shadow.setOffset(0, 3)
#         shadow.setColor(QColor(0, 0, 0, 35))
#         self.setGraphicsEffect(shadow)

#         outer = QHBoxLayout(self)
#         outer.setContentsMargins(20, 20, 20, 20)
#         outer.setSpacing(20)

#         # ── Imatge ────────────────────────────────────────────────────────────
#         self.img_label = QLabel("⏳")
#         self.img_label.setObjectName("imgPlaceholder")
#         self.img_label.setFixedSize(130, 130)
#         self.img_label.setAlignment(Qt.AlignCenter)
#         self.img_label.setFont(QFont("Segoe UI", 28))
#         outer.addWidget(self.img_label, 0, Qt.AlignTop)

#         # ── Columna info ──────────────────────────────────────────────────────
#         info = QVBoxLayout()
#         info.setSpacing(5)

#         # Nom + tags
#         header = QHBoxLayout()
#         header.setSpacing(8)

#         name_lbl = QLabel(component.get("name", "—"))
#         name_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
#         name_lbl.setStyleSheet("color: #1a1a2e; background: transparent;")
#         name_lbl.setWordWrap(True)
#         header.addWidget(name_lbl, 1)

#         tag_sup = QLabel(supplier)
#         tag_sup.setObjectName("tagSupplier")
#         header.addWidget(tag_sup, 0, Qt.AlignTop)

#         avail = str(component.get("store_availability", "") or "")
#         if avail:
#             tag_av = QLabel(avail)
#             tag_av.setObjectName("tagAvail")
#             header.addWidget(tag_av, 0, Qt.AlignTop)

#         info.addLayout(header)

#         # Descripció
#         desc = QLabel(component.get("description", "") or "")
#         desc.setFont(QFont("Segoe UI", 10))
#         desc.setStyleSheet("color: #5a6478; background: transparent; margin-bottom: 4px;")
#         desc.setWordWrap(True)
#         info.addWidget(desc)

#         # Separador
#         sep = QFrame()
#         sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("background-color: #eaecf0; max-height: 1px; border: none;")
#         info.addWidget(sep)

#         # Camps
#         for label, value in [
#             ("Store name",  component.get("store_name")),
#             ("Tipus",       component.get("type2")),
#             ("Fabricant",   component.get("manufacturer")),
#             ("Package",     component.get("package")),
#         ]:
#             info.addWidget(FieldRow(label, str(value) if value is not None else "—"))

#         info.addWidget(PriceTableWidget(component.get("price_unit")))

#         # Botons
#         btn_row = QHBoxLayout()
#         btn_row.setSpacing(10)
#         btn_row.addStretch()

#         for label, key in [("🛒  Botiga", "store"), ("📄  Datasheet", "datasheet")]:
#             raw = component.get(key)
#             if isinstance(raw, list):
#                 raw = raw[0] if raw else None
#             # Evita strings buits, None, "None" o "null"
#             url = str(raw).strip() if raw is not None else ""
#             if url and url.lower() not in ("none", "null", "n/a", ""):
#                 btn = QPushButton(label)
#                 btn.setObjectName("linkBtn")
#                 btn.setCursor(Qt.PointingHandCursor)
#                 btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
#                 btn_row.addWidget(btn)

#         info.addLayout(btn_row)
#         outer.addLayout(info)

#         # ── Imatge asíncrona ──────────────────────────────────────────────────
#         img_url = component.get("image", "")
#         if isinstance(img_url, list):
#             img_url = img_url[0] if img_url else ""
#         img_url = str(img_url).strip()
#         if img_url:
#             self._nam = QNetworkAccessManager()
#             self._nam.finished.connect(self._on_image_loaded)
#             req = QNetworkRequest(QUrl(img_url))
#             # Headers necessaris per a Mouser i Farnell
#             req.setRawHeader(
#                 QByteArray(b"User-Agent"),
#                 QByteArray(b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                            b"AppleWebKit/537.36 Chrome/120 Safari/537.36")
#             )
#             req.setRawHeader(QByteArray(b"Accept"),
#                              QByteArray(b"image/webp,image/apng,image/*,*/*;q=0.8"))
#             req.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute, True)
#             self._nam.get(req)
#         else:
#             self.img_label.setText("🖼️")

#     def _on_image_loaded(self, reply):
#         data = reply.readAll()
#         pix = QPixmap()
#         if pix.loadFromData(data):
#             self.img_label.setText("")
#             self.img_label.setStyleSheet(
#                 "background-color: #f0f2f5; border-radius: 10px;"
#                 "border: 1px solid #e0e4ec;"
#             )
#             self.img_label.setPixmap(
#                 pix.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
#             )
#         else:
#             self.img_label.setText("🖼️")
#         reply.deleteLater()


# # ── Finestra principal ────────────────────────────────────────────────────────

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Component Lookup — Mouser · Farnell · LCSC")
#         self.setMinimumSize(820, 600)
#         self.resize(1000, 740)

#         central = QWidget()
#         central.setObjectName("central")
#         self.setCentralWidget(central)

#         root = QVBoxLayout(central)
#         root.setContentsMargins(32, 26, 32, 26)
#         root.setSpacing(14)

#         # ── Capçalera ─────────────────────────────────────────────────────────
#         title = QLabel("🔍  Component Lookup")
#         title.setFont(QFont("Segoe UI", 22, QFont.Bold))
#         title.setStyleSheet("color: #1a1a2e;")
#         root.addWidget(title)

#         subtitle = QLabel(
#             "Escaneja o introdueix un codi de barres / MPN / SKU  ·  "
#             "Mouser, Farnell o LCSC"
#         )
#         subtitle.setFont(QFont("Segoe UI", 11))
#         subtitle.setStyleSheet("color: #8899bb;")
#         root.addWidget(subtitle)

#         # ── Cerca ─────────────────────────────────────────────────────────────
#         search_row = QHBoxLayout()
#         search_row.setSpacing(10)

#         self.search_box = QLineEdit()
#         self.search_box.setObjectName("searchBox")
#         self.search_box.setFixedHeight(46)
#         self.search_box.setPlaceholderText(
#             "p.ex.  C17902  ·  2988437  ·  LM317  ·  [)>06…  ·  ^pbnÑ…"
#         )
#         self.search_box.returnPressed.connect(self._on_search)
#         # Esborra resultats en quant l'usuari canvia el contingut

#         self.search_btn = QPushButton("Cercar")
#         self.search_btn.setObjectName("searchBtn")
#         self.search_btn.setFixedSize(120, 46)
#         self.search_btn.clicked.connect(self._on_search)

#         search_row.addWidget(self.search_box)
#         search_row.addWidget(self.search_btn)
#         root.addLayout(search_row)

#         # ── Ajuda ─────────────────────────────────────────────────────────────
#         help_lbl = QLabel(
#             "💡 &nbsp;"
#             "<b style='color:#4a7bdc'>Mouser</b>: MPN o codi <code>[)&gt;</code> &nbsp;·&nbsp; "
#             "<b style='color:#4a7bdc'>LCSC</b>: <code>C</code>+número o codi <code>^pbnÑ</code> &nbsp;·&nbsp; "
#             "<b style='color:#4a7bdc'>Farnell</b>: 6–8 dígits o codi <code>(1P)</code>"
#         )
#         help_lbl.setFont(QFont("Segoe UI", 10))
#         help_lbl.setStyleSheet("color: #aab0c0;")
#         help_lbl.setTextFormat(Qt.RichText)
#         root.addWidget(help_lbl)

#         # ── Estat ─────────────────────────────────────────────────────────────
#         self.status_label = QLabel("Introdueix un codi i prem Cercar o Intro.")
#         self.status_label.setFont(QFont("Segoe UI", 11))
#         self.status_label.setStyleSheet("color: #aab0c0;")
#         root.addWidget(self.status_label)

#         # ── Resultats ─────────────────────────────────────────────────────────
#         self.scroll = QScrollArea()
#         self.scroll.setWidgetResizable(True)
#         self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.scroll.setStyleSheet("background: transparent; border: none;")
#         root.addWidget(self.scroll)

#         self.result_widget = QWidget()
#         self.result_widget.setStyleSheet("background: transparent;")
#         self.result_layout = QVBoxLayout(self.result_widget)
#         self.result_layout.setAlignment(Qt.AlignTop)
#         self.result_layout.setSpacing(16)
#         self.result_layout.setContentsMargins(0, 0, 12, 0)
#         self.scroll.setWidget(self.result_widget)

#         self.search_box.setFocus()

#     # ── Slots ─────────────────────────────────────────────────────────────────

#     def _on_search(self):
#         code = self.search_box.text().strip()
#         if not code:
#             return

#         self._clear_results()
#         self.search_btn.setEnabled(False)
#         self.status_label.setStyleSheet("color: #e8a020; font-size: 11px;")
#         self.status_label.setText(f"⏳  Cercant «{code}»…")

#         signals = WorkerSignals()
#         signals.finished.connect(self._on_result)
#         signals.error.connect(self._on_error)

#         def run():
#             try:
#                 comp, supplier = fetch_component(code)
#                 signals.finished.emit(comp, supplier)
#             except Exception as exc:
#                 signals.error.emit(str(exc))

#         threading.Thread(target=run, daemon=True).start()

#     def _on_result(self, component: dict, supplier: str):
#         self.search_btn.setEnabled(True)
#         self.status_label.setStyleSheet("color: #2e7d32; font-size: 11px;")
#         name = component.get("name", "")
#         self.status_label.setText(f"✔  {name}  ·  Proveïdor: {supplier}")
#         # DEBUG temporal — mostra tots els camps per consola
#         print(f"\n{'='*60}")
#         for k, v in component.items():
#             print(f"  {k}: {v!r}")
#         print('='*60)
#         self.result_layout.addWidget(ComponentCard(component, supplier))

#     def _on_error(self, msg: str):
#         self.search_btn.setEnabled(True)
#         self.status_label.setStyleSheet("color: #c62828; font-size: 11px;")
#         self.status_label.setText(f"✘  Error: {msg}")

#     def _clear_results(self):
#         while self.result_layout.count():
#             item = self.result_layout.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()


# # ── Entry point ───────────────────────────────────────────────────────────────

# def main():
#     app = QApplication(sys.argv)
#     app.setStyleSheet(STYLE)
#     app.setFont(QFont("Segoe UI", 11))
#     win = MainWindow()
#     win.show()
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main()



























"""
Component Lookup App
Cerca components electrònics de Mouser, Farnell i LCSC
Escaneig de codi de barres/QR o entrada manual.
"""

import re
import sys
import threading

from PySide6.QtCore import Qt, Signal, QObject, QUrl, QByteArray
from PySide6.QtGui import QFont, QPixmap, QDesktopServices, QColor
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

    def _dummy(name):
        return {
            "name": name, "store_name": "Demo Store",
            "description": "Component de prova (mòduls no carregats)",
            "type2": "IC", "manufacturer": "Demo Mfr", "package": "SOT-23",
            "datasheet": "https://example.com/datasheet.pdf",
            "store": "https://example.com",
            "image": "https://via.placeholder.com/130",
            "price_unit": [{"quantity": 1, "price": "1.23"},
                           {"quantity": 10, "price": "0.99"}],
            "store_availability": "In Stock",
        }

    def get_farnell_by_sku(sku):  return _dummy(f"Farnell SKU {sku}")
    def get_lcsc_data(sku):       return _dummy(f"LCSC {sku}")
    def get_mouser_data(mpn):     return _dummy(f"Mouser {mpn}")


# ── Lògica de detecció i parsing ─────────────────────────────────────────────

def detect_supplier(code: str) -> str:
    """Detecta proveïdor per format de codi manual."""
    c = code.strip().upper()
    if re.fullmatch(r"C\d+", c):       return "lcsc"
    if re.fullmatch(r"\d{6,8}", c):    return "farnell"
    return "mouser"


def parse_barcode(data: str) -> dict:
    """Descodifica codis de barres de Mouser, Farnell i LCSC."""
    data = data.strip()

    # ── LCSC ──────────────────────────────────────────────────────────────────
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
            "supplier": "LCSC",
            "order_number": result.get("on"),
            "part_number":  result.get("pm"),
            "sku":          result.get("pc"),
            "quantity":     result.get("qty"),
        }

    # ── Mouser ────────────────────────────────────────────────────────────────
    if data.startswith("[)>") or data.startswith(">[)>"):
        return _parse_mouser_barcode(data)

    # ── Farnell ───────────────────────────────────────────────────────────────
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


# ── Parser Mouser GS1 (separat per claredat) ──────────────────────────────────
#
# BUGS del parser original que es corregeixen aquí:
#
#  1. FIELDS incomplet: faltaven "1T" (traceabilitat), "1V" (fabricant), "P"
#     (MPN del fabricant), "4K" i "9D" (date code alternatiu).
#     Sense ells, el valor de "1P" absorbia la resta de camps.
#
#  2. "Q" com a primer caràcter del MPN: si el Mouser PN comença per "Q"
#     (ex: QS6K1FRATR), el parser detectava "Q" com a camp de quantitat
#     just darrere de "1P", deixant part_number = ''.
#
#  3. "K" apareix múltiples vegades dins del valor del PO del client
#     (ex: CABOMAILEKMARBL1), generant múltiples entrades "customer_po"
#     falses que fragmenten el parse posterior.
#
#  Estratègia de correcció:
#  - S'amplien FIELDS amb tots els AIs de Mouser documentats.
#  - Es fa un primer pas amb GS (\x1d) si n'hi ha.
#  - Sense GS, s'aplica el parser seqüencial millorat que:
#      a) Prefereix IDs més llargs quan hi ha solapament de posició.
#      b) Nomes accepta la primera ocurrència de cada camp (evita K duplicat).
#      c) Si part_number surt buit o sospitós, fa fallback a mouser_part.
#
def _parse_mouser_barcode(data: str) -> dict:
    # Elimina prefixe [)>, >[)>, parèntesis, i el codi de format (06, 07…)
    body = re.sub(r'^[>\[\]()]+>?\d*', '', data)

    FIELDS = [
        ("11K", "order_number"),    # Número de comanda Mouser
        ("1P",  "part_number"),     # Número de peça Mouser (SKU Mouser)
        ("1T",  "lot_number"),      # Traçabilitat / lot
        ("1V",  "manufacturer"),    # Fabricant
        ("4L",  "country"),         # País d'origen
        ("0D",  "date_code"),       # Codi de data (format 1)
        ("9D",  "date_code"),       # Codi de data (format 2)
        ("4K",  "line_number"),     # Número de línia de comanda
        ("1K",  "order_line"),      # Referència de línia
        ("Q",   "quantity"),        # Quantitat
        ("P",   "mfr_part"),        # MPN del fabricant (sense prefix "1")
        ("K",   "customer_po"),     # PO del client (AI d'un sol caràcter → últim)
    ]

    # ── Amb separador GS (\x1d) → parse trivial ───────────────────────────────
    if "\x1d" in body:
        result = {"supplier": "Mouser"}
        for part in body.split("\x1d"):
            part = part.strip()
            for fid, fname in FIELDS:
                if part.startswith(fid):
                    result.setdefault(fname, part[len(fid):])
                    break
        return result

    # ── Sense GS: parser seqüencial per posició ────────────────────────────────
    hits = []
    for fid, fname in FIELDS:
        for m in re.finditer(re.escape(fid), body):
            pos_after = m.end()
            # Heurística crítica: "Q" (quantitat) NOMÉS és vàlid si el
            # caràcter que el segueix és un dígit. Evita confondre "QS6K1FRATR"
            # (un MPN que comença per Q) amb el camp de quantitat.
            if fid == "Q" and (pos_after >= len(body) or not body[pos_after].isdigit()):
                continue
            hits.append((m.start(), m.end(), fid, fname))

    # Ordena: posició ascending; en empat, AI més llarg primer.
    hits.sort(key=lambda x: (x[0], -len(x[2])))

    # Filtra solapaments.
    # - Cada fname apareix una sola vegada, excepte "mfr_part" (P) que pot
    #   repetir-se per crear fronteres de camp quan el MPN conté comes o
    #   altres variants al final.
    filtered = []
    prev_end = 0
    seen_names = set()
    for start, end, fid, fname in hits:
        if start >= prev_end:
            if fname not in seen_names or fname == "mfr_part":
                filtered.append((start, end, fid, fname))
                prev_end = end
                seen_names.add(fname)

    # Construeix el diccionari.
    result = {"supplier": "Mouser"}
    for i, (start, end, fid, fname) in enumerate(filtered):
        nxt = filtered[i + 1][0] if i + 1 < len(filtered) else len(body)
        result.setdefault(fname, body[end:nxt].strip())

    # Neteja part_number: els MPN de Mouser no contenen comes; elimina la
    # cua ",XXXX" que a vegades apareix (codi de lot o data concatenada).
    pn = result.get("part_number", "")
    if "," in pn:
        result["part_number"] = pn.split(",")[0].strip()

    # Fallback: si 1P és buit, prova el camp P (MPN del fabricant).
    if not result.get("part_number") and result.get("mfr_part"):
        result["part_number"] = result["mfr_part"]

    return result


def fetch_component(code: str):
    """Retorna (component_dict, supplier_str) o llança una excepció."""
    code = code.strip()

    # LCSC barcode
    is_lcsc_bc = (code.startswith("{") and "pbn:" in code) or \
                 (code.startswith("^") and "Ñ" in code)
    if is_lcsc_bc:
        parsed = parse_barcode(code)
        sku = parsed.get("sku")
        if not sku:
            raise ValueError("No s'ha trobat el camp 'pc' (SKU) al codi LCSC.")
        return get_lcsc_data(sku), "LCSC"

    # Mouser barcode
    if code.startswith("[)>") or code.startswith(">[)>"):
        parsed = parse_barcode(code)

        # FIX: intenta múltiples camps en ordre de preferència
        # "part_number" (1P) és el SKU de Mouser; és el millor per cercar.
        # "mfr_part" (P) és el MPN del fabricant, segon candidat.
        # "order_number" (11K) és el número de comanda, no serveix per cercar.
        mpn = (parsed.get("part_number") or
               parsed.get("mfr_part") or "").strip()

        if not mpn:
            # Mostra el parse per depurar
            print(f"[MOUSER PARSE] {parsed}")
            raise ValueError(
                "No s'ha trobat el part number al codi Mouser.\n"
                f"Parse obtingut: {parsed}"
            )

        print(f"[MOUSER] Cercant: {mpn!r}  (parse complet: {parsed})")
        return get_mouser_data(mpn), "Mouser"

    # Farnell barcode
    if re.search(r'\(1P\)|\(10V\)|10V\d', code):
        parsed = parse_barcode(code)
        sku = parsed.get("sku", "").strip()
        if not sku:
            raise ValueError("No s'ha trobat el SKU al codi Farnell.")
        return get_farnell_by_sku(sku), "Farnell"

    # Entrada manual
    supplier = detect_supplier(code)
    if supplier == "farnell":  return get_farnell_by_sku(code), "Farnell"
    if supplier == "lcsc":     return get_lcsc_data(code), "LCSC"
    return get_mouser_data(code), "Mouser"


# ── Preus ─────────────────────────────────────────────────────────────────────

def parse_prices(price_unit) -> list:
    """Normalitza price_unit de qualsevol format de proveïdor."""
    if not price_unit:
        return []
    if isinstance(price_unit, list):
        result = []
        for entry in price_unit:
            if not isinstance(entry, dict):
                continue
            qty = (entry.get("quantity") or entry.get("Quantity") or
                   entry.get("qty") or "?")
            raw = str(entry.get("price") or entry.get("Price") or
                      entry.get("unit_price") or "?")
            raw = raw.replace("€", "").replace("$", "").replace("£", "") \
                     .replace(",", ".").strip()
            result.append({"quantity": qty, "price": raw})
        return result
    return [{"quantity": 1, "price": str(price_unit)}]


# ── Signals ───────────────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    finished = Signal(dict, str)
    error    = Signal(str)


# ── Estils (tema clar) ────────────────────────────────────────────────────────

STYLE = """
QMainWindow, QWidget#central { background-color: #f0f2f5; }
QLineEdit#searchBox {
    background-color: #ffffff; color: #1a1a2e;
    border: 2px solid #d0d5e0; border-radius: 10px;
    padding: 10px 16px; font-size: 15px;
}
QLineEdit#searchBox:focus { border-color: #4a7bdc; }
QPushButton#searchBtn {
    background-color: #4a7bdc; color: #ffffff;
    border: none; border-radius: 10px;
    font-size: 15px; font-weight: bold; min-height: 44px;
}
QPushButton#searchBtn:hover    { background-color: #3a6bcb; }
QPushButton#searchBtn:pressed  { background-color: #2a5bba; }
QPushButton#searchBtn:disabled { background-color: #c0c8dc; color: #8899bb; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: #e8eaf0; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #b0b8cc; border-radius: 4px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QFrame#card {
    background-color: #ffffff; border-radius: 14px; border: 1px solid #dde1ea;
}
QLabel#tagSupplier {
    background-color: #e8f0fe; color: #2a5bba;
    border-radius: 6px; padding: 2px 10px;
    font-size: 11px; font-weight: bold;
}
QLabel#tagAvail {
    background-color: #e6f4ea; color: #1e7e34;
    border-radius: 6px; padding: 2px 10px;
    font-size: 11px; font-weight: bold;
}
QPushButton#linkBtn {
    background-color: #f0f4ff; color: #4a7bdc;
    border: 1px solid #c8d4f0; border-radius: 8px;
    padding: 6px 16px; font-size: 13px;
}
QPushButton#linkBtn:hover { background-color: #dde8ff; }
QLabel#imgPlaceholder {
    background-color: #f0f2f5; border-radius: 10px;
    border: 1px solid #e0e4ec; color: #b0b8cc; font-size: 28px;
}
"""


# ── Widgets ───────────────────────────────────────────────────────────────────

class FieldRow(QWidget):
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 1, 0, 1)
        lay.setSpacing(10)

        lbl = QLabel(label + ":")
        lbl.setFixedWidth(130)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #7a8499; background: transparent;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

        val = QLabel(value or "—")
        val.setFont(QFont("Segoe UI", 10))
        val.setStyleSheet("color: #1a1a2e; background: transparent;")
        val.setWordWrap(True)
        val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lay.addWidget(lbl)
        lay.addWidget(val)


class PriceTableWidget(QWidget):
    def __init__(self, price_unit, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 4, 0, 4)
        main.setSpacing(10)

        lbl = QLabel("Preus:")
        lbl.setFixedWidth(130)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #7a8499; background: transparent;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
        main.addWidget(lbl)

        prices = parse_prices(price_unit)

        if not prices:
            val = QLabel("—")
            val.setFont(QFont("Segoe UI", 10))
            val.setStyleSheet("color: #1a1a2e; background: transparent;")
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
                price_str = f"{float(price):.4f}".rstrip("0").rstrip(".") + " €"
            except (ValueError, TypeError):
                price_str = f"{price} €"

            pill = QWidget()
            pill.setStyleSheet(
                "background-color: #f5f7ff; border-radius: 8px;"
                "border: 1px solid #d0d8f0;"
            )
            pill_lay = QVBoxLayout(pill)
            pill_lay.setContentsMargins(10, 5, 10, 5)
            pill_lay.setSpacing(1)

            qty_lbl = QLabel(f"≥ {qty} ut")
            qty_lbl.setFont(QFont("Segoe UI", 9))
            qty_lbl.setStyleSheet("color: #7a8499; background: transparent; border: none;")
            qty_lbl.setAlignment(Qt.AlignCenter)

            price_lbl = QLabel(price_str)
            price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            price_lbl.setStyleSheet("color: #2e7d32; background: transparent; border: none;")
            price_lbl.setAlignment(Qt.AlignCenter)

            pill_lay.addWidget(qty_lbl)
            pill_lay.addWidget(price_lbl)
            flow.addWidget(pill)

        flow.addStretch()
        main.addWidget(container, 1)


class ComponentCard(QFrame):
    def __init__(self, component: dict, supplier: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 35))
        self.setGraphicsEffect(shadow)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(20)

        self.img_label = QLabel("⏳")
        self.img_label.setObjectName("imgPlaceholder")
        self.img_label.setFixedSize(130, 130)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFont(QFont("Segoe UI", 28))
        outer.addWidget(self.img_label, 0, Qt.AlignTop)

        info = QVBoxLayout()
        info.setSpacing(5)

        header = QHBoxLayout()
        header.setSpacing(8)

        name_lbl = QLabel(component.get("name", "—"))
        name_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        name_lbl.setStyleSheet("color: #1a1a2e; background: transparent;")
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

        desc = QLabel(component.get("description", "") or "")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #5a6478; background: transparent; margin-bottom: 4px;")
        desc.setWordWrap(True)
        info.addWidget(desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #eaecf0; max-height: 1px; border: none;")
        info.addWidget(sep)

        for label, value in [
            ("Store name",  component.get("store_name")),
            ("Tipus",       component.get("type2")),
            ("Fabricant",   component.get("manufacturer")),
            ("Package",     component.get("package")),
        ]:
            info.addWidget(FieldRow(label, str(value) if value is not None else "—"))

        info.addWidget(PriceTableWidget(component.get("price_unit")))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        for label, key in [("🛒  Botiga", "store"), ("📄  Datasheet", "datasheet")]:
            raw = component.get(key)
            if isinstance(raw, list):
                raw = raw[0] if raw else None
            url = str(raw).strip() if raw is not None else ""
            if url and url.lower() not in ("none", "null", "n/a", ""):
                btn = QPushButton(label)
                btn.setObjectName("linkBtn")
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
                btn_row.addWidget(btn)

        info.addLayout(btn_row)
        outer.addLayout(info)

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
            req.setRawHeader(QByteArray(b"Accept"),
                             QByteArray(b"image/webp,image/apng,image/*,*/*;q=0.8"))
            req.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute, True)
            self._nam.get(req)
        else:
            self.img_label.setText("🖼️")

    def _on_image_loaded(self, reply):
        data = reply.readAll()
        pix = QPixmap()
        if pix.loadFromData(data):
            self.img_label.setText("")
            self.img_label.setStyleSheet(
                "background-color: #f0f2f5; border-radius: 10px;"
                "border: 1px solid #e0e4ec;"
            )
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
        root.setSpacing(14)

        title = QLabel("🔍  Component Lookup")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #1a1a2e;")
        root.addWidget(title)

        subtitle = QLabel(
            "Escaneja o introdueix un codi de barres / MPN / SKU  ·  "
            "Mouser, Farnell o LCSC"
        )
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #8899bb;")
        root.addWidget(subtitle)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setFixedHeight(46)
        self.search_box.setPlaceholderText(
            "p.ex.  C17902  ·  2988437  ·  LM317  ·  [)>06…  ·  ^pbnÑ…"
        )
        self.search_box.returnPressed.connect(self._on_search)

        self.search_btn = QPushButton("Cercar")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.setFixedSize(120, 46)
        self.search_btn.clicked.connect(self._on_search)

        search_row.addWidget(self.search_box)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        help_lbl = QLabel(
            "💡 &nbsp;"
            "<b style='color:#4a7bdc'>Mouser</b>: MPN o codi <code>[)&gt;</code> &nbsp;·&nbsp; "
            "<b style='color:#4a7bdc'>LCSC</b>: <code>C</code>+número o codi <code>^pbnÑ</code> &nbsp;·&nbsp; "
            "<b style='color:#4a7bdc'>Farnell</b>: 6–8 dígits o codi <code>(1P)</code>"
        )
        help_lbl.setFont(QFont("Segoe UI", 10))
        help_lbl.setStyleSheet("color: #aab0c0;")
        help_lbl.setTextFormat(Qt.RichText)
        root.addWidget(help_lbl)

        self.status_label = QLabel("Introdueix un codi i prem Cercar o Intro.")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #aab0c0;")
        root.addWidget(self.status_label)

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
        self.result_layout.setContentsMargins(0, 0, 12, 0)
        self.scroll.setWidget(self.result_widget)

        self.search_box.setFocus()

    def _on_search(self):
        code = self.search_box.text().strip()
        if not code:
            return

        self._clear_results()
        self.search_btn.setEnabled(False)
        self.status_label.setStyleSheet("color: #e8a020; font-size: 11px;")
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
        self.status_label.setStyleSheet("color: #2e7d32; font-size: 11px;")
        name = component.get("name", "")
        self.status_label.setText(f"✔  {name}  ·  Proveïdor: {supplier}")
        print(f"\n{'='*60}")
        for k, v in component.items():
            print(f"  {k}: {v!r}")
        print('='*60)
        self.result_layout.addWidget(ComponentCard(component, supplier))

    def _on_error(self, msg: str):
        self.search_btn.setEnabled(True)
        self.status_label.setStyleSheet("color: #c62828; font-size: 11px;")
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