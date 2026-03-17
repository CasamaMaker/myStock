
# """
# lcsc_stock_import.py
# ====================
# Importa albarans de LCSC al Google Sheet d'estoc (projecte mystock).

# Flux:
#   1. Backup del Google Sheet (CSV local o còpia Google Sheet al Drive)
#   2. Llegir albarà LCSC (.csv / .tsv)
#   3. Components nous      -> consulta API LCSC + afegeix fila completa
#   4. Components existents -> suma estoc + omple camps buits via API
#   5. Escriu al Google Sheet (amb confirmació manual per consola)

# Ús:
#   python lcsc_stock_import.py
# """

# import os
# import sys
# import csv
# import datetime
# from pathlib import Path

# # ── Mòduls del projecte ───────────────────────────────────────────────────────
# PROJECT_DIR = Path(__file__).parent
# if str(PROJECT_DIR) not in sys.path:
#     sys.path.insert(0, str(PROJECT_DIR))

# from configuration import Config
# from request_lcsc  import get_lcsc_data

# import gspread
# from google.oauth2.service_account import Credentials


# # =============================================================================
# #  CONFIGURACIÓ  ←  EDITA AQUÍ
# # =============================================================================

# # Ruta a l'albarà LCSC descarregat (.csv o .tsv)
# LCSC_BOM_FILE = "LCSC_Exported_20220929_014129.csv"

# # Si True, escriu al Google Sheet sense demanar confirmació
# SKIP_CONFIRM = False

# # Tipus de backup:
# #   "csv"    -> fitxer .csv local a la carpeta BACKUP_FOLDER
# #   "google" -> còpia del Google Sheet al Google Drive
# #   "both"   -> fa els dos alhora
# BACKUP_TYPE = "csv"

# # Carpeta local on es desen els backups CSV (es crea si no existeix)
# BACKUP_FOLDER = r"C:\Users\ecasamayor\Downloads"

# # Nom base del Google Sheet de backup (s'afegeix data i hora automàticament)
# BACKUP_GOOGLE_NAME = "backup_stock"

# # ID de la carpeta del Google Drive on es desaran els backups Google Sheet.
# # Ha d'estar compartida amb el service account (Editor).
# # L'ID és la part final de la URL de la carpeta:
# #   https://drive.google.com/drive/folders/  ← aquí
# BACKUP_DRIVE_FOLDER_ID = "1EfiweOrs20U8iacfr1ZJXA_XKSLjmjkw"


# # =============================================================================
# #  CONSTANTS INTERNES
# # =============================================================================

# TOTAL_COLS = Config.SUPPLIER_PRODUCT + 1   # 13 columnes (0..12)

# GSCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive",
# ]


# # =============================================================================
# #  GOOGLE SHEETS — autenticació i lectura/escriptura
# # =============================================================================

# def _creds_path() -> Path:
#     p = Path(Config.GOOGLE_CREDENTIALS_JSON)
#     return p if p.is_absolute() else PROJECT_DIR / p


# def get_gspread_client():
#     creds_path = _creds_path()
#     if not creds_path.exists():
#         raise FileNotFoundError(f"Credencials no trobades: {creds_path}")
#     creds = Credentials.from_service_account_file(str(creds_path), scopes=GSCOPES)
#     return gspread.authorize(creds)


# def fetch_sheet_rows(client) -> list:
#     sh   = client.open_by_key(Config.GOOGLE_SHEET_ID)
#     ws   = sh.sheet1
#     rows = ws.get_all_values()
#     print(f"  OK Sheet llegit: {len(rows)} files (capçalera inclosa)")
#     return rows


# def write_sheet_rows(client, rows: list):
#     sh = client.open_by_key(Config.GOOGLE_SHEET_ID)
#     ws = sh.sheet1
#     ws.clear()
#     ws.update(rows, value_input_option="USER_ENTERED")
#     print(f"  OK Sheet actualitzat: {len(rows)} files escrites")


# # =============================================================================
# #  BACKUP — CSV local
# # =============================================================================

# # def backup_sheet(client) -> tuple:
# #     """
# #     Desa una còpia .xlsx del Google Sheet en local.
# #     El format .xlsx s'obre directament a Google Sheets, Excel i LibreOffice.
# #     Retorna (nom_fitxer, llista_de_files).
# #     """
# #     try:
# #         import openpyxl
# #     except ImportError:
# #         raise ImportError(
# #             "Falta el paquet 'openpyxl'.\n"
# #             "Instal·la'l amb:  pip install openpyxl"
# #         )

# #     os.makedirs(BACKUP_FOLDER, exist_ok=True)
# #     ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# #     fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.xlsx")

# #     print("  Llegint sheet per fer backup...")
# #     rows = fetch_sheet_rows(client)

# #     wb = openpyxl.Workbook()
# #     ws = wb.active
# #     ws.title = "Stock"
# #     for row in rows:
# #         ws.append(row)

# #     wb.save(fname)
# #     size_kb = os.path.getsize(fname) / 1024
# #     print(f"  Backup desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
# #     return fname, rows


# def backup_sheet(client) -> tuple:
#     """
#     Desa una còpia CSV del Google Sheet en local.
#     Retorna (nom_fitxer, llista_de_files).
#     """
#     os.makedirs(BACKUP_FOLDER, exist_ok=True)
#     ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.csv")

#     print("  Llegint sheet per fer backup CSV...")
#     rows = fetch_sheet_rows(client)

#     with open(fname, "w", newline="", encoding="utf-8-sig") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)

#     size_kb = os.path.getsize(fname) / 1024
#     print(f"  Backup CSV desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
#     return fname, rows

# # # =============================================================================
# # #  BACKUP — Google Sheet al Drive
# # # =============================================================================

# # def backup_sheet_google(client) -> tuple:
# #     """
# #     Crea una còpia del Google Sheet a la carpeta BACKUP_DRIVE_FOLDER_ID del Drive.
# #     La carpeta ha d'estar compartida amb el service account com a Editor.
# #     Usa files.copy (còpia server-side, sense pujar dades, quota de la carpeta del teu Drive).
# #     Retorna (nom_del_nou_sheet, llista_de_files).
# #     """
# #     import requests as _req
# #     from google.auth.transport.requests import Request as _GAuthReq

# #     ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# #     new_name = f"{BACKUP_GOOGLE_NAME}_{ts}"

# #     print("  Llegint sheet per fer backup al Google Drive...")
# #     rows = fetch_sheet_rows(client)

# #     # Token d'accés del service account
# #     creds = Credentials.from_service_account_file(str(_creds_path()), scopes=GSCOPES)
# #     creds.refresh(_GAuthReq())
# #     headers = {
# #         "Authorization": f"Bearer {creds.token}",
# #         "Content-Type": "application/json",
# #     }
# #     drive_base = "https://www.googleapis.com/drive/v3/files"

# #     # files.copy: duplica l'arxiu original i el posa a BACKUP_DRIVE_FOLDER_ID
# #     resp = _req.post(
# #         f"{drive_base}/{Config.GOOGLE_SHEET_ID}/copy",
# #         headers=headers,
# #         params={"supportsAllDrives": "true"},
# #         json={
# #             "name":    new_name,
# #             "parents": [BACKUP_DRIVE_FOLDER_ID],
# #         },
# #         timeout=30,
# #     )

# #     if not resp.ok:
# #         raise RuntimeError(
# #             f"Error en files.copy [{resp.status_code}]:\n{resp.text}"
# #         )

# #     new_id  = resp.json()["id"]
# #     new_url = f"https://docs.google.com/spreadsheets/d/{new_id}"
# #     print(f"  Backup Google Sheet creat: '{new_name}'")
# #     print(f"  URL: {new_url}")
# #     print(f"  ({len(rows)} files copiades)")

# #     return new_name, rows


# # =============================================================================
# #  BACKUP — dispatcher segons BACKUP_TYPE
# # =============================================================================

# def do_backup(client) -> tuple:
#     """
#     Executa el backup segons la variable BACKUP_TYPE:
#       'csv'    -> backup_sheet()         (fitxer CSV local)
#       'google' -> backup_sheet_google()  (còpia Google Sheet al Drive del SA)
#       'both'   -> els dos alhora
#     Si el backup google falla definitivament, fa fallback a CSV automàticament.
#     Retorna sempre (referencia_backup, llista_de_files).
#     """
#     btype = BACKUP_TYPE.strip().lower()

#     if btype == "csv":
#         return backup_sheet(client)

#     elif btype == "google":
#         try:
#             return backup_sheet_google(client)
#         except RuntimeError as e:
#             print(f"\n  ERROR backup Google: {e}")
#             print("  Fent fallback a backup CSV local...\n")
#             return backup_sheet(client)

#     elif btype == "both":
#         print("  -- Backup CSV local --")
#         fname, rows = backup_sheet(client)
#         print("  -- Backup Google Drive --")
#         try:
#             gname, _ = backup_sheet_google(client)
#             ref = f"CSV: {fname}  |  Google: '{gname}'"
#         except RuntimeError as e:
#             print(f"  AVIS backup Google fallat: {e}")
#             ref = f"CSV: {fname}  (backup Google fallat)"
#         return ref, rows

#     else:
#         print(f"  AVIS: BACKUP_TYPE='{BACKUP_TYPE}' no reconegut. Usant 'csv' per defecte.")
#         return backup_sheet(client)


# # =============================================================================
# #  LECTURA ALBARA LCSC
# # =============================================================================

# def read_lcsc_bom(filepath: str) -> list:
#     """
#     Llegeix l'albarà LCSC. Auto-detecta separador TAB o COMA.
#     Retorna llista de dicts amb les claus originals LCSC:
#       'LCSC Part Number', 'Manufacture Part Number', 'Manufacturer',
#       'Package', 'Description', 'RoHS', 'Order Qty.', 'Unit Price'
#     """
#     with open(filepath, newline="", encoding="utf-8-sig") as f:
#         sample = f.read(4096)
#     sep = "\t" if sample.count("\t") > sample.count(",") else ","

#     rows = []
#     with open(filepath, newline="", encoding="utf-8-sig") as f:
#         reader = csv.DictReader(f, delimiter=sep)
#         for r in reader:
#             clean = {k.strip(): v.strip() for k, v in r.items() if k}
#             if clean.get("LCSC Part Number"):
#                 rows.append(clean)

#     sep_name = "TAB" if sep == "\t" else "COMA"
#     print(f"  Albara llegit: {len(rows)} components  (separador={sep_name})")
#     return rows


# # =============================================================================
# #  CONSTRUCCIO DE FILES
# # =============================================================================

# def _next_id(data_rows: list) -> int:
#     """Retorna el proxim ID unic (max existent + 1)."""
#     ids = []
#     for row in data_rows:
#         try:
#             ids.append(int(str(row[Config.ID]).strip()))
#         except (ValueError, IndexError):
#             pass
#     return max(ids, default=0) + 1


# def build_new_row(new_id: int, lcsc_part: str, bom_row: dict, api: dict) -> list:
#     """
#     Construeix una fila nova combinant dades de l'albarà i de l'API LCSC.
#     Prioritat: API > albarà.

#     Mapeig (configuration.py):
#       Col 0   ID                -> nou ID autogenerat
#       Col 1   MANUFACTURER_PN  -> api['name']         | bom MPN
#       Col 2   MANUFACTURER_NAME-> api['manufacturer'] | bom Manufacturer
#       Col 3   CATEGORY         -> api['type2']  (catalogName)
#       Col 4   SUPPLIER         -> 'LCSC'  (fix)
#       Col 5   SUPPLIER_PN      -> lcsc_part  (LCSC Part Number)
#       Col 6   SUPPLIER_CATEGORY-> api['type2']
#       Col 7   PACKAGE          -> api['package']      | bom Package
#       Col 8   DESCRIPTION      -> api['description']  | bom Description
#       Col 9   STOCK            -> quantitat de l'albarà
#       Col 10  STORAGE          -> buit (omplir manualment)
#       Col 11  DATASHEET        -> api['datasheet']  (pdfUrl)
#       Col 12  SUPPLIER_PRODUCT -> api['store']  (URL pàgina LCSC)
#     """
#     row = [""] * TOTAL_COLS

#     try:
#         qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#     except ValueError:
#         qty = 0

#     row[Config.ID]                = new_id
#     row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
#     row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
#     row[Config.CATEGORY]          = api.get("type2", "")
#     row[Config.SUPPLIER]          = "LCSC"
#     row[Config.SUPPLIER_PN]       = lcsc_part
#     row[Config.SUPPLIER_CATEGORY] = api.get("type2", "")
#     row[Config.PACKAGE]           = api.get("package")      or bom_row.get("Package", "")
#     row[Config.DESCRIPTION]       = api.get("description")  or bom_row.get("Description", "")
#     row[Config.STOCK]             = qty
#     row[Config.STORAGE]           = ""
#     row[Config.DATASHEET]         = api.get("datasheet", "")
#     row[Config.SUPPLIER_PRODUCT]  = api.get("store", f"https://www.lcsc.com/product-detail/{lcsc_part}.html")

#     return row


# def fill_empty_cols(row: list, api: dict) -> tuple:
#     """
#     Omple els camps BUITS d'una fila existent amb dades de l'API LCSC.
#     MAI sobreescriu un camp que ja té valor.
#     Retorna (row_actualitzat, nombre_de_camps_omplerts).
#     """
#     fill_map = {
#         Config.MANUFACTURER_PN:   api.get("name", ""),
#         Config.MANUFACTURER_NAME: api.get("manufacturer", ""),
#         Config.CATEGORY:          api.get("type2", ""),
#         Config.SUPPLIER_CATEGORY: api.get("type2", ""),
#         Config.PACKAGE:           api.get("package", ""),
#         Config.DESCRIPTION:       api.get("description", ""),
#         Config.DATASHEET:         api.get("datasheet", ""),
#         Config.SUPPLIER_PRODUCT:  api.get("store", ""),
#     }

#     while len(row) < TOTAL_COLS:
#         row.append("")

#     filled = 0
#     for col_i, val in fill_map.items():
#         if val and not str(row[col_i]).strip():
#             row[col_i] = val
#             filled += 1

#     return row, filled


# # =============================================================================
# #  PREVIEW
# # =============================================================================

# def print_preview(data_rows: list, bom_parts: set, backup_ref: str):
#     print("\nPreview dels components de l'albarà (tal com quedaran al sheet):\n")
#     print(f"  {'ID':>4}  {'LCSC Part':^12}  {'MPN':^22}  {'Fabricant':^20}  {'Qty':>5}  DS  Web")
#     print("  " + "-" * 82)

#     for row in data_rows:
#         if len(row) <= Config.SUPPLIER_PN:
#             continue
#         lcsc = str(row[Config.SUPPLIER_PN]).strip()
#         if lcsc not in bom_parts:
#             continue

#         rid = str(row[Config.ID])
#         mpn = str(row[Config.MANUFACTURER_PN])[:22]
#         mfr = str(row[Config.MANUFACTURER_NAME])[:20]
#         qty = str(row[Config.STOCK])
#         ds  = "SI" if len(row) > Config.DATASHEET        and row[Config.DATASHEET]        else "NO"
#         web = "SI" if len(row) > Config.SUPPLIER_PRODUCT and row[Config.SUPPLIER_PRODUCT] else "NO"
#         print(f"  {rid:>4}  {lcsc:<12}  {mpn:<22}  {mfr:<20}  {qty:>5}  {ds:^2}  {web:^3}")

#     print(f"\n  Total files al sheet (sense capçalera): {len(data_rows)}")
#     print(f"  Backup: {backup_ref}")


# # =============================================================================
# #  FLUX PRINCIPAL
# # =============================================================================

# def run():

#     # ── Validació fitxer albarà ────────────────────────────────────────────────
#     if not os.path.isfile(LCSC_BOM_FILE):
#         print(f"\nERROR: Fitxer albarà no trobat: '{LCSC_BOM_FILE}'")
#         print("       Comprova la variable LCSC_BOM_FILE a la secció CONFIGURACIÓ.")
#         sys.exit(1)

#     # ── PAS 1: Connexió i backup ───────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 1 -- Connectant a Google Sheets i fent backup")
#     print(f"          (tipus: {BACKUP_TYPE})")
#     print("=" * 58)

#     client = get_gspread_client()
#     print("  Client autenticat correctament")

#     backup_ref, all_rows = do_backup(client)

#     header_row = all_rows[0] if all_rows else []
#     data_rows  = [list(r) for r in all_rows[1:]]   # còpia editable

#     print(f"\n  Capçalera          : {header_row}")
#     print(f"  Components al stock: {len(data_rows)}")

#     # ── PAS 2: Llegir albarà ───────────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 2 -- Llegint albarà LCSC")
#     print("=" * 58)
#     print(f"  Fitxer: {LCSC_BOM_FILE}")

#     bom_components = read_lcsc_bom(LCSC_BOM_FILE)

#     print(f"\n  {'LCSC Part':^14}  {'MPN':^25}  {'Qty':>6}  {'Unit Price':>10}")
#     print("  " + "-" * 62)
#     for c in bom_components:
#         lp  = c.get("LCSC Part Number", "?")
#         mpn = c.get("Manufacture Part Number", "")[:25]
#         qty = c.get("Order Qty.", "?")
#         prc = c.get("Unit Price", "")
#         print(f"  {lp:<14}  {mpn:<25}  {qty:>6}  {prc:>10}")

#     # ── PAS 3: Processar components ────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 3 -- Processant components")
#     print("=" * 58)

#     # Índex del stock actual per LCSC Part Number (col SUPPLIER_PN = 5)
#     stock_by_lcsc = {}
#     for i, row in enumerate(data_rows):
#         if len(row) > Config.SUPPLIER_PN:
#             part = str(row[Config.SUPPLIER_PN]).strip()
#             if part:
#                 stock_by_lcsc[part] = i

#     print(f"  Components LCSC indexats al stock: {len(stock_by_lcsc)}")

#     stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
#     next_id = _next_id(data_rows)
#     print(f"  Pròxim ID disponible: {next_id}\n")

#     for bom_row in bom_components:
#         lcsc_part = bom_row.get("LCSC Part Number", "").strip()
#         if not lcsc_part:
#             continue

#         try:
#             qty_new = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#         except ValueError:
#             qty_new = 0

#         # ── CAS A: Component JA EXISTEIX ──────────────────────────────────────
#         if lcsc_part in stock_by_lcsc:
#             idx = stock_by_lcsc[lcsc_part]

#             while len(data_rows[idx]) < TOTAL_COLS:
#                 data_rows[idx].append("")

#             try:
#                 qty_old = int(float(str(data_rows[idx][Config.STOCK]).strip() or "0"))
#             except ValueError:
#                 qty_old = 0

#             qty_total = qty_old + qty_new
#             data_rows[idx][Config.STOCK] = qty_total

#             print(f"  [EXISTENT] {lcsc_part:<12}  estoc: {qty_old} + {qty_new} = {qty_total}")
#             stats["estoc_sumat"] += 1

#             # Comprovar si cal omplir camps buits
#             cols_to_check = [
#                 Config.MANUFACTURER_PN, Config.MANUFACTURER_NAME,
#                 Config.CATEGORY, Config.PACKAGE, Config.DESCRIPTION,
#                 Config.DATASHEET, Config.SUPPLIER_PRODUCT,
#             ]
#             needs_fill = any(
#                 not str(data_rows[idx][c]).strip()
#                 for c in cols_to_check if c < len(data_rows[idx])
#             )

#             if needs_fill:
#                 print(f"             -> Camps buits detectats, consultant API LCSC...")
#                 api = get_lcsc_data(lcsc_part)
#                 if api:
#                     data_rows[idx], n_filled = fill_empty_cols(data_rows[idx], api)
#                     print(f"             -> {n_filled} camps completats")
#                     stats["info_completada"] += 1
#                 else:
#                     print(f"             AVIS: API LCSC no ha retornat dades")
#                     stats["errors_api"] += 1

#         # ── CAS B: Component NOU ───────────────────────────────────────────────
#         else:
#             print(f"  [NOU]      {lcsc_part:<12}  consultant API LCSC...")
#             api = get_lcsc_data(lcsc_part)

#             if api:
#                 new_row = build_new_row(next_id, lcsc_part, bom_row, api)
#                 mfr = api.get("manufacturer", "?")
#                 mpn = api.get("name", "?")
#                 ds  = "amb datasheet" if api.get("datasheet") else "sense datasheet"
#                 print(f"             -> ID={next_id}  {mfr}  |  {mpn}  |  {ds}")
#             else:
#                 print(f"             AVIS: API no ha respost -- usant dades de l'albarà")
#                 new_row = build_new_row(next_id, lcsc_part, bom_row, {})
#                 stats["errors_api"] += 1

#             data_rows.append(new_row)
#             stock_by_lcsc[lcsc_part] = len(data_rows) - 1
#             next_id += 1
#             stats["nous"] += 1

#     print("\n" + "-" * 44)
#     print(f"  Nous components afegits   : {stats['nous']}")
#     print(f"  Estoc actualitzat (suma)  : {stats['estoc_sumat']}")
#     print(f"  Info completada via API   : {stats['info_completada']}")
#     print(f"  Errors / API no resposta  : {stats['errors_api']}")
#     print("-" * 44)

#     # ── Preview ────────────────────────────────────────────────────────────────
#     bom_parts = {r.get("LCSC Part Number", "").strip() for r in bom_components}
#     print_preview(data_rows, bom_parts, backup_ref)

#     # ── Confirmació ────────────────────────────────────────────────────────────
#     if not SKIP_CONFIRM:
#         print("\nVols escriure els canvis al Google Sheet? [s/N] ", end="", flush=True)
#         answer = input().strip().lower()
#         if answer not in ("s", "si", "y", "yes"):
#             print("Operació cancel·lada. No s'ha modificat res al sheet.")
#             print(f"El backup segueix disponible: {backup_ref}")
#             return

#     # ── PAS 4: Escriure al sheet ───────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 4 -- Escrivint al Google Sheet...")
#     print("=" * 58)

#     final_data = [header_row] + data_rows
#     write_sheet_rows(client, final_data)

#     print("\nCOMPLETAT!")
#     print(f"  Components al stock     : {len(data_rows)}")
#     print(f"  Nous afegits            : {stats['nous']}")
#     print(f"  Estoc actualitzat       : {stats['estoc_sumat']}")
#     print(f"  Backup                  : {backup_ref}\n")


# # =============================================================================
# #  ENTRY POINT
# # =============================================================================

# if __name__ == "__main__":
#     run()























# """
# nowstock_app.py
# ===============
# App d'escriptori PySide6 per importar albarans LCSC al Google Sheet d'estoc.
# Equivalent visual de lcsc_stock_import.py.

# Requisits:
#     pip install PySide6 gspread google-auth openpyxl

# Ús:
#     python nowstock_app.py
# """

# import os
# import sys
# import csv
# import datetime
# import threading
# from pathlib import Path

# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
#     QGroupBox, QComboBox, QFrame, QSizePolicy, QProgressBar,
#     QSplitter, QScrollArea,
# )
# from PySide6.QtCore import Qt, QThread, QObject, Signal, QSize
# from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QTextCursor

# # ── Ruta del projecte ──────────────────────────────────────────────────────────
# PROJECT_DIR = Path(__file__).parent
# if str(PROJECT_DIR) not in sys.path:
#     sys.path.insert(0, str(PROJECT_DIR))

# # ── Imports condicionals (poden no existir en entorn de prova) ─────────────────
# try:
#     from configuration import Config
#     from request_lcsc import get_lcsc_data
#     import gspread
#     from google.oauth2.service_account import Credentials
#     DEPS_OK = True
# except ImportError as _e:
#     DEPS_OK = False
#     _MISSING = str(_e)


# # =============================================================================
# #  ESTILS  (Qt Style Sheet)
# # =============================================================================

# APP_STYLE = """
# /* ── Base ──────────────────────────────────────────────────── */
# QMainWindow, QWidget {
#     background-color: #1a1d23;
#     color: #d0d4de;
#     font-family: 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', sans-serif;
#     font-size: 13px;
# }

# /* ── GroupBox ───────────────────────────────────────────────── */
# QGroupBox {
#     border: 1px solid #2e3340;
#     border-radius: 6px;
#     margin-top: 14px;
#     padding: 10px 12px 10px 12px;
#     font-size: 11px;
#     font-weight: 600;
#     letter-spacing: 0.08em;
#     color: #6b7280;
#     text-transform: uppercase;
# }
# QGroupBox::title {
#     subcontrol-origin: margin;
#     subcontrol-position: top left;
#     left: 12px;
#     padding: 0 4px;
#     background-color: #1a1d23;
# }

# /* ── LineEdit ───────────────────────────────────────────────── */
# QLineEdit {
#     background-color: #21252e;
#     border: 1px solid #2e3340;
#     border-radius: 5px;
#     padding: 6px 10px;
#     color: #d0d4de;
#     selection-background-color: #3b82f6;
# }
# QLineEdit:focus {
#     border-color: #3b82f6;
# }
# QLineEdit:disabled {
#     background-color: #1e2128;
#     color: #4b5263;
#     border-color: #252932;
# }
# QLineEdit[readOnly="true"] {
#     background-color: #1e2128;
#     color: #5a6175;
#     border-color: #252932;
# }

# /* ── ComboBox ───────────────────────────────────────────────── */
# QComboBox {
#     background-color: #21252e;
#     border: 1px solid #2e3340;
#     border-radius: 5px;
#     padding: 6px 10px;
#     color: #d0d4de;
#     min-width: 120px;
# }
# QComboBox:hover { border-color: #3b82f6; }
# QComboBox::drop-down {
#     border: none;
#     padding-right: 8px;
# }
# QComboBox::down-arrow {
#     image: none;
#     border-left: 4px solid transparent;
#     border-right: 4px solid transparent;
#     border-top: 5px solid #6b7280;
#     width: 0; height: 0;
# }
# QComboBox QAbstractItemView {
#     background-color: #21252e;
#     border: 1px solid #3b82f6;
#     selection-background-color: #1d4ed8;
#     color: #d0d4de;
# }

# /* ── Buttons ────────────────────────────────────────────────── */
# QPushButton {
#     background-color: #21252e;
#     border: 1px solid #2e3340;
#     border-radius: 5px;
#     padding: 6px 14px;
#     color: #9ca3af;
#     font-size: 12px;
# }
# QPushButton:hover {
#     background-color: #2a2f3a;
#     border-color: #4b5263;
#     color: #d0d4de;
# }
# QPushButton:pressed {
#     background-color: #1a1d23;
# }

# QPushButton#btn_run {
#     background-color: #1d4ed8;
#     border: 1px solid #2563eb;
#     color: #ffffff;
#     font-size: 13px;
#     font-weight: 600;
#     padding: 10px 28px;
#     border-radius: 6px;
#     letter-spacing: 0.03em;
# }
# QPushButton#btn_run:hover {
#     background-color: #2563eb;
#     border-color: #3b82f6;
# }
# QPushButton#btn_run:pressed {
#     background-color: #1e40af;
# }
# QPushButton#btn_run:disabled {
#     background-color: #1e2a45;
#     border-color: #1e2a45;
#     color: #3b5080;
# }

# QPushButton#btn_cancel {
#     background-color: #3f1a1a;
#     border: 1px solid #7f1d1d;
#     color: #fca5a5;
#     font-size: 12px;
#     padding: 6px 14px;
# }
# QPushButton#btn_cancel:hover {
#     background-color: #5c1f1f;
# }

# /* ── Log / Console ───────────────────────────────────────────── */
# QTextEdit#log_output {
#     background-color: #13151a;
#     border: 1px solid #252932;
#     border-radius: 6px;
#     color: #9ca3af;
#     font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
#     font-size: 12px;
#     padding: 8px;
#     selection-background-color: #1d4ed8;
# }

# /* ── ProgressBar ────────────────────────────────────────────── */
# QProgressBar {
#     background-color: #21252e;
#     border: 1px solid #2e3340;
#     border-radius: 4px;
#     height: 6px;
#     text-align: center;
#     color: transparent;
# }
# QProgressBar::chunk {
#     background-color: #3b82f6;
#     border-radius: 4px;
# }

# /* ── Separadors ─────────────────────────────────────────────── */
# QFrame[frameShape="4"],
# QFrame[frameShape="5"] {
#     color: #252932;
# }

# /* ── Label especials ──────────────────────────────────────────── */
# QLabel#title_label {
#     font-size: 20px;
#     font-weight: 700;
#     color: #e2e8f0;
#     letter-spacing: -0.02em;
# }
# QLabel#subtitle_label {
#     font-size: 11px;
#     color: #4b5263;
#     letter-spacing: 0.04em;
# }
# QLabel#status_label {
#     font-size: 12px;
#     color: #6b7280;
# }
# QLabel#status_label[status="ok"] {
#     color: #34d399;
# }
# QLabel#status_label[status="error"] {
#     color: #f87171;
# }
# QLabel#status_label[status="running"] {
#     color: #60a5fa;
# }
# """


# # =============================================================================
# #  WORKER  —  Executa la lògica en un thread secundari
# # =============================================================================

# class ImportWorker(QObject):
#     """Executa tot el flux d'importació fora del thread de la UI."""

#     log        = Signal(str, str)   # (text, tipus: 'info'|'ok'|'warn'|'error'|'head')
#     progress   = Signal(int)        # 0..100
#     finished   = Signal(bool, str)  # (éxit, missatge_final)

#     def __init__(self, bom_file: str, backup_type: str, skip_confirm: bool = True):
#         super().__init__()
#         self.bom_file     = bom_file
#         self.backup_type  = backup_type
#         self.skip_confirm = skip_confirm
#         self._abort       = False

#     def abort(self):
#         self._abort = True

#     # ── Shortcuts de log ──────────────────────────────────────────────────────
#     def _log(self, msg, t="info"):   self.log.emit(msg, t)
#     def _head(self, msg):            self.log.emit(msg, "head")
#     def _ok(self, msg):              self.log.emit(msg, "ok")
#     def _warn(self, msg):            self.log.emit(msg, "warn")
#     def _err(self, msg):             self.log.emit(msg, "error")

#     # ── Helpers Google Sheets ─────────────────────────────────────────────────
#     GSCOPES = [
#         "https://www.googleapis.com/auth/spreadsheets",
#         "https://www.googleapis.com/auth/drive",
#     ]
#     TOTAL_COLS = None  # s'assigna al run()

#     def _creds_path(self):
#         p = Path(Config.GOOGLE_CREDENTIALS_JSON)
#         return p if p.is_absolute() else PROJECT_DIR / p

#     def _get_client(self):
#         cp = self._creds_path()
#         if not cp.exists():
#             raise FileNotFoundError(f"Credencials no trobades: {cp}")
#         creds = Credentials.from_service_account_file(str(cp), scopes=self.GSCOPES)
#         return gspread.authorize(creds)

#     def _fetch_rows(self, client):
#         sh   = client.open_by_key(Config.GOOGLE_SHEET_ID)
#         rows = sh.sheet1.get_all_values()
#         self._ok(f"Sheet llegit: {len(rows)} files (capçalera inclosa)")
#         return rows

#     def _write_rows(self, client, rows):
#         sh = client.open_by_key(Config.GOOGLE_SHEET_ID)
#         ws = sh.sheet1
#         ws.clear()
#         ws.update(rows, value_input_option="USER_ENTERED")
#         self._ok(f"Sheet actualitzat: {len(rows)} files escrites")

#     # ── Backup CSV ────────────────────────────────────────────────────────────
#     def _backup_csv(self, client):
#         folder = getattr(Config, "BACKUP_FOLDER", str(Path.home() / "Downloads"))
#         os.makedirs(folder, exist_ok=True)
#         ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         fname = os.path.join(folder, f"backup_stock_{ts}.csv")
#         rows  = self._fetch_rows(client)
#         with open(fname, "w", newline="", encoding="utf-8-sig") as f:
#             csv.writer(f).writerows(rows)
#         size = os.path.getsize(fname) / 1024
#         self._ok(f"Backup CSV desat: {fname}  ({len(rows)} files, {size:.1f} KB)")
#         return fname, rows

#     # ── Backup Google ─────────────────────────────────────────────────────────
#     def _backup_google(self, client):
#         import requests as _req
#         from google.auth.transport.requests import Request as _GR
#         ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         new_name = f"backup_stock_{ts}"
#         rows     = self._fetch_rows(client)

#         drive_folder = getattr(Config, "BACKUP_DRIVE_FOLDER_ID", "")
#         creds = Credentials.from_service_account_file(str(self._creds_path()), scopes=self.GSCOPES)
#         creds.refresh(_GR())
#         headers = {
#             "Authorization": f"Bearer {creds.token}",
#             "Content-Type": "application/json",
#         }
#         resp = _req.post(
#             f"https://www.googleapis.com/drive/v3/files/{Config.GOOGLE_SHEET_ID}/copy",
#             headers=headers,
#             params={"supportsAllDrives": "true"},
#             json={"name": new_name, "parents": [drive_folder]},
#             timeout=30,
#         )
#         if not resp.ok:
#             raise RuntimeError(f"Error files.copy [{resp.status_code}]: {resp.text}")
#         new_id  = resp.json()["id"]
#         self._ok(f"Backup Google Sheet creat: '{new_name}'")
#         self._ok(f"URL: https://docs.google.com/spreadsheets/d/{new_id}")
#         return new_name, rows

#     def _do_backup(self, client):
#         bt = self.backup_type.strip().lower()
#         if bt == "csv":
#             return self._backup_csv(client)
#         elif bt == "google":
#             try:
#                 return self._backup_google(client)
#             except RuntimeError as e:
#                 self._warn(f"Backup Google fallat: {e}")
#                 self._warn("Fallback a backup CSV local...")
#                 return self._backup_csv(client)
#         elif bt == "both":
#             fname, rows = self._backup_csv(client)
#             try:
#                 gname, _ = self._backup_google(client)
#                 ref = f"CSV: {fname}  |  Google: '{gname}'"
#             except RuntimeError as e:
#                 self._warn(f"Backup Google fallat: {e}")
#                 ref = f"CSV: {fname}  (backup Google fallat)"
#             return ref, rows
#         else:
#             return self._backup_csv(client)

#     # ── Lectura albarà ────────────────────────────────────────────────────────
#     def _read_bom(self, filepath):
#         with open(filepath, newline="", encoding="utf-8-sig") as f:
#             sample = f.read(4096)
#         sep = "\t" if sample.count("\t") > sample.count(",") else ","
#         rows = []
#         with open(filepath, newline="", encoding="utf-8-sig") as f:
#             for r in csv.DictReader(f, delimiter=sep):
#                 clean = {k.strip(): v.strip() for k, v in r.items() if k}
#                 if clean.get("LCSC Part Number"):
#                     rows.append(clean)
#         sep_name = "TAB" if sep == "\t" else "COMA"
#         self._ok(f"Albarà llegit: {len(rows)} components  (separador={sep_name})")
#         return rows

#     # ── Construcció files ─────────────────────────────────────────────────────
#     @staticmethod
#     def _next_id(data_rows):
#         ids = []
#         for row in data_rows:
#             try:
#                 ids.append(int(str(row[Config.ID]).strip()))
#             except (ValueError, IndexError):
#                 pass
#         return max(ids, default=0) + 1

#     def _build_new_row(self, new_id, lcsc_part, bom_row, api):
#         TC = self.TOTAL_COLS
#         row = [""] * TC
#         try:
#             qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#         except ValueError:
#             qty = 0
#         row[Config.ID]                = new_id
#         row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
#         row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
#         row[Config.CATEGORY]          = api.get("type2", "")
#         row[Config.SUPPLIER]          = "LCSC"
#         row[Config.SUPPLIER_PN]       = lcsc_part
#         row[Config.SUPPLIER_CATEGORY] = api.get("type2", "")
#         row[Config.PACKAGE]           = api.get("package")      or bom_row.get("Package", "")
#         row[Config.DESCRIPTION]       = api.get("description")  or bom_row.get("Description", "")
#         row[Config.STOCK]             = qty
#         row[Config.STORAGE]           = ""
#         row[Config.DATASHEET]         = api.get("datasheet", "")
#         row[Config.SUPPLIER_PRODUCT]  = api.get("store", f"https://www.lcsc.com/product-detail/{lcsc_part}.html")
#         return row

#     def _fill_empty(self, row, api):
#         fill_map = {
#             Config.MANUFACTURER_PN:   api.get("name", ""),
#             Config.MANUFACTURER_NAME: api.get("manufacturer", ""),
#             Config.CATEGORY:          api.get("type2", ""),
#             Config.SUPPLIER_CATEGORY: api.get("type2", ""),
#             Config.PACKAGE:           api.get("package", ""),
#             Config.DESCRIPTION:       api.get("description", ""),
#             Config.DATASHEET:         api.get("datasheet", ""),
#             Config.SUPPLIER_PRODUCT:  api.get("store", ""),
#         }
#         while len(row) < self.TOTAL_COLS:
#             row.append("")
#         filled = 0
#         for col_i, val in fill_map.items():
#             if val and not str(row[col_i]).strip():
#                 row[col_i] = val
#                 filled += 1
#         return row, filled

#     # ── RUN ───────────────────────────────────────────────────────────────────
#     def run(self):
#         if not DEPS_OK:
#             self._err(f"Falten dependències: {_MISSING}")
#             self.finished.emit(False, "Dependències no instal·lades.")
#             return

#         self.TOTAL_COLS = Config.SUPPLIER_PRODUCT + 1

#         try:
#             # ── PAS 1 ──────────────────────────────────────────────────────────
#             self._head("PAS 1 ── Connexió a Google Sheets i backup")
#             self.progress.emit(5)

#             client = self._get_client()
#             self._ok("Client Google autenticat correctament")
#             self.progress.emit(10)

#             backup_ref, all_rows = self._do_backup(client)
#             self.progress.emit(20)

#             header_row = all_rows[0] if all_rows else []
#             data_rows  = [list(r) for r in all_rows[1:]]
#             self._log(f"Components al stock actual: {len(data_rows)}")
#             self.progress.emit(25)

#             # ── PAS 2 ──────────────────────────────────────────────────────────
#             self._head("PAS 2 ── Llegint albarà LCSC")
#             bom_components = self._read_bom(self.bom_file)
#             self._log(f"Fitxer: {self.bom_file}")

#             for c in bom_components:
#                 lp  = c.get("LCSC Part Number", "?")
#                 mpn = c.get("Manufacture Part Number", "")
#                 qty = c.get("Order Qty.", "?")
#                 self._log(f"  {lp:<14}  {mpn:<28}  qty={qty}")
#             self.progress.emit(35)

#             # ── PAS 3 ──────────────────────────────────────────────────────────
#             self._head("PAS 3 ── Processant components")

#             stock_by_lcsc = {}
#             for i, row in enumerate(data_rows):
#                 if len(row) > Config.SUPPLIER_PN:
#                     part = str(row[Config.SUPPLIER_PN]).strip()
#                     if part:
#                         stock_by_lcsc[part] = i

#             stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
#             next_id = self._next_id(data_rows)
#             total   = len(bom_components)

#             for idx_bom, bom_row in enumerate(bom_components):
#                 if self._abort:
#                     self.finished.emit(False, "Operació cancel·lada per l'usuari.")
#                     return

#                 lcsc_part = bom_row.get("LCSC Part Number", "").strip()
#                 if not lcsc_part:
#                     continue

#                 try:
#                     qty_new = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#                 except ValueError:
#                     qty_new = 0

#                 pct = 35 + int((idx_bom / max(total, 1)) * 55)
#                 self.progress.emit(pct)

#                 if lcsc_part in stock_by_lcsc:
#                     # Existent
#                     i = stock_by_lcsc[lcsc_part]
#                     while len(data_rows[i]) < self.TOTAL_COLS:
#                         data_rows[i].append("")
#                     try:
#                         qty_old = int(float(str(data_rows[i][Config.STOCK]).strip() or "0"))
#                     except ValueError:
#                         qty_old = 0
#                     qty_total = qty_old + qty_new
#                     data_rows[i][Config.STOCK] = qty_total
#                     self._ok(f"[EXISTENT] {lcsc_part}  {qty_old} + {qty_new} = {qty_total}")
#                     stats["estoc_sumat"] += 1

#                     needs_fill = any(
#                         not str(data_rows[i][c]).strip()
#                         for c in [Config.MANUFACTURER_PN, Config.MANUFACTURER_NAME,
#                                   Config.CATEGORY, Config.PACKAGE, Config.DESCRIPTION,
#                                   Config.DATASHEET, Config.SUPPLIER_PRODUCT]
#                         if c < len(data_rows[i])
#                     )
#                     if needs_fill:
#                         self._log(f"           → Camps buits, consultant API...")
#                         api = get_lcsc_data(lcsc_part)
#                         if api:
#                             data_rows[i], nf = self._fill_empty(data_rows[i], api)
#                             self._ok(f"           → {nf} camps completats")
#                             stats["info_completada"] += 1
#                         else:
#                             self._warn(f"           → API LCSC sense resposta")
#                             stats["errors_api"] += 1
#                 else:
#                     # Nou
#                     self._log(f"[NOU]      {lcsc_part}  → consultant API LCSC...")
#                     api = get_lcsc_data(lcsc_part)
#                     if api:
#                         new_row = self._build_new_row(next_id, lcsc_part, bom_row, api)
#                         mfr = api.get("manufacturer", "?")
#                         mpn = api.get("name", "?")
#                         ds  = "✓ datasheet" if api.get("datasheet") else "· sense datasheet"
#                         self._ok(f"           → ID={next_id}  {mfr} | {mpn} | {ds}")
#                     else:
#                         self._warn(f"           → API sense resposta, usant dades de l'albarà")
#                         new_row = self._build_new_row(next_id, lcsc_part, bom_row, {})
#                         stats["errors_api"] += 1
#                     data_rows.append(new_row)
#                     stock_by_lcsc[lcsc_part] = len(data_rows) - 1
#                     next_id += 1
#                     stats["nous"] += 1

#             self.progress.emit(92)
#             self._head("Resum")
#             self._ok(f"Nous components afegits    : {stats['nous']}")
#             self._ok(f"Estoc actualitzat (suma)   : {stats['estoc_sumat']}")
#             self._ok(f"Info completada via API    : {stats['info_completada']}")
#             if stats["errors_api"]:
#                 self._warn(f"Errors / API no resposta   : {stats['errors_api']}")

#             # ── PAS 4 ──────────────────────────────────────────────────────────
#             self._head("PAS 4 ── Escrivint al Google Sheet")
#             final_data = [header_row] + data_rows
#             self._write_rows(client, final_data)
#             self.progress.emit(100)

#             resum = (
#                 f"Completat!  "
#                 f"Nous: {stats['nous']}  |  "
#                 f"Actualitzats: {stats['estoc_sumat']}  |  "
#                 f"Backup: {backup_ref}"
#             )
#             self.finished.emit(True, resum)

#         except Exception as exc:
#             import traceback
#             self._err(traceback.format_exc())
#             self.finished.emit(False, f"ERROR: {exc}")


# # =============================================================================
# #  FINESTRA PRINCIPAL
# # =============================================================================

# class LogWidget(QTextEdit):
#     """Àrea de log amb colors per tipus de missatge."""

#     COLORS = {
#         "info":  "#9ca3af",
#         "ok":    "#34d399",
#         "warn":  "#fbbf24",
#         "error": "#f87171",
#         "head":  "#60a5fa",
#     }

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setObjectName("log_output")
#         self.setReadOnly(True)

#     def append_msg(self, msg: str, tipo: str = "info"):
#         color = self.COLORS.get(tipo, "#9ca3af")
#         prefix = {
#             "ok":    "✓",
#             "warn":  "⚠",
#             "error": "✗",
#             "head":  "▶",
#         }.get(tipo, " ")
#         ts = datetime.datetime.now().strftime("%H:%M:%S")
#         html = (
#             f'<span style="color:#3f4557;">[{ts}]</span> '
#             f'<span style="color:{color};">{prefix} {msg}</span>'
#         )
#         self.append(html)
#         # Scroll automàtic al final
#         self.moveCursor(QTextCursor.End)


# class MainWindow(QMainWindow):

#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("nowStock · Importació LCSC")
#         self.setMinimumSize(820, 640)
#         self.resize(960, 700)
#         self._worker  = None
#         self._thread  = None
#         self._running = False
#         self._setup_ui()
#         self._refresh_config_panel()

#     # ── UI ────────────────────────────────────────────────────────────────────
#     def _setup_ui(self):
#         central = QWidget()
#         self.setCentralWidget(central)
#         root = QVBoxLayout(central)
#         root.setContentsMargins(20, 20, 20, 16)
#         root.setSpacing(16)

#         # ── Capçalera ──────────────────────────────────────────────────────────
#         hdr = QHBoxLayout()
#         hdr.setSpacing(16)

#         dot_container = QWidget()
#         dot_container.setFixedSize(36, 36)
#         dot_layout = QHBoxLayout(dot_container)
#         dot_layout.setContentsMargins(0, 0, 0, 0)
#         icon_lbl = QLabel("◈")
#         icon_lbl.setStyleSheet("color:#3b82f6; font-size:22px;")
#         dot_layout.addWidget(icon_lbl)
#         hdr.addWidget(dot_container)

#         titles = QVBoxLayout()
#         titles.setSpacing(2)
#         t1 = QLabel("nowStock")
#         t1.setObjectName("title_label")
#         t2 = QLabel("LCSC STOCK IMPORT TOOL")
#         t2.setObjectName("subtitle_label")
#         titles.addWidget(t1)
#         titles.addWidget(t2)
#         hdr.addLayout(titles)
#         hdr.addStretch()

#         # Badge estat deps
#         self.lbl_deps = QLabel()
#         self.lbl_deps.setObjectName("status_label")
#         if DEPS_OK:
#             self.lbl_deps.setText("● Dependències OK")
#             self.lbl_deps.setProperty("status", "ok")
#         else:
#             self.lbl_deps.setText("● Falten dependències")
#             self.lbl_deps.setProperty("status", "error")
#         self.lbl_deps.setStyleSheet(
#             f"color: {'#34d399' if DEPS_OK else '#f87171'}; font-size:11px;"
#         )
#         hdr.addWidget(self.lbl_deps)

#         root.addLayout(hdr)

#         # ── Separador ─────────────────────────────────────────────────────────
#         sep = QFrame(); sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("color:#252932;")
#         root.addWidget(sep)

#         # ── Cos principal (2 columnes) ─────────────────────────────────────────
#         body = QHBoxLayout()
#         body.setSpacing(16)

#         # ─ Columna esquerra (configuració) ─
#         left = QVBoxLayout()
#         left.setSpacing(12)

#         # Fitxer albarà
#         grp_bom = QGroupBox("Albarà LCSC")
#         gbom_lay = QVBoxLayout(grp_bom)
#         gbom_lay.setSpacing(8)

#         row_file = QHBoxLayout()
#         row_file.setSpacing(8)
#         self.le_bom = QLineEdit()
#         self.le_bom.setPlaceholderText("Selecciona el fitxer .csv / .tsv de l'albarà...")
#         self.le_bom.textChanged.connect(self._on_bom_changed)
#         btn_browse = QPushButton("Cerca…")
#         btn_browse.setFixedWidth(72)
#         btn_browse.clicked.connect(self._browse_bom)
#         row_file.addWidget(self.le_bom)
#         row_file.addWidget(btn_browse)
#         gbom_lay.addLayout(row_file)

#         self.lbl_bom_info = QLabel("Cap fitxer seleccionat")
#         self.lbl_bom_info.setStyleSheet("color:#4b5263; font-size:11px;")
#         gbom_lay.addWidget(self.lbl_bom_info)

#         left.addWidget(grp_bom)

#         # Tipus de backup
#         grp_backup = QGroupBox("Tipus de Backup")
#         gbk_lay = QVBoxLayout(grp_backup)
#         gbk_lay.setSpacing(8)

#         row_bk = QHBoxLayout()
#         row_bk.setSpacing(8)
#         lbl_bk = QLabel("Mode:")
#         lbl_bk.setStyleSheet("color:#6b7280; font-size:12px;")
#         self.combo_backup = QComboBox()
#         self.combo_backup.addItems(["csv", "google", "both"])
#         self.combo_backup.setCurrentText("csv")
#         self.combo_backup.setToolTip(
#             "csv    → fitxer CSV local\n"
#             "google → còpia al Google Drive\n"
#             "both   → els dos"
#         )
#         row_bk.addWidget(lbl_bk)
#         row_bk.addWidget(self.combo_backup)
#         row_bk.addStretch()
#         gbk_lay.addLayout(row_bk)

#         left.addWidget(grp_backup)

#         # Config (read-only, des de Config)
#         grp_cfg = QGroupBox("Configuració (configuration.py)")
#         gcfg_lay = QVBoxLayout(grp_cfg)
#         gcfg_lay.setSpacing(6)

#         self._cfg_fields = {}
#         cfg_items = [
#             ("Sheet ID",         "GOOGLE_SHEET_ID"),
#             ("Credencials JSON", "GOOGLE_CREDENTIALS_JSON"),
#             ("Carpeta backup",   "BACKUP_FOLDER"),
#         ]
#         for label, attr in cfg_items:
#             row = QHBoxLayout()
#             lbl = QLabel(label + ":")
#             lbl.setFixedWidth(110)
#             lbl.setStyleSheet("color:#6b7280; font-size:11px;")
#             le  = QLineEdit()
#             le.setReadOnly(True)
#             le.setStyleSheet(
#                 "background:#1e2128; color:#5a6175; border:1px solid #252932;"
#                 "border-radius:4px; padding:4px 8px; font-size:11px;"
#             )
#             self._cfg_fields[attr] = le
#             row.addWidget(lbl)
#             row.addWidget(le)
#             gcfg_lay.addLayout(row)

#         left.addWidget(grp_cfg)
#         left.addStretch()

#         # ─ Columna dreta (log) ─
#         right = QVBoxLayout()
#         right.setSpacing(8)

#         lbl_log = QLabel("Registre d'execució")
#         lbl_log.setStyleSheet("color:#6b7280; font-size:11px; font-weight:600; letter-spacing:0.08em;")
#         right.addWidget(lbl_log)

#         self.log_view = LogWidget()
#         self.log_view.setMinimumHeight(300)
#         right.addWidget(self.log_view, 1)

#         btn_clear = QPushButton("Netejar registre")
#         btn_clear.setFixedWidth(130)
#         btn_clear.clicked.connect(self.log_view.clear)
#         btn_clear.setStyleSheet("font-size:11px; padding:4px 10px;")
#         right.addWidget(btn_clear, 0, Qt.AlignRight)

#         body.addLayout(left, 2)
#         body.addLayout(right, 3)
#         root.addLayout(body, 1)

#         # ── Barra inferior (progrés + botons) ─────────────────────────────────
#         sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
#         sep2.setStyleSheet("color:#252932;")
#         root.addWidget(sep2)

#         bot = QVBoxLayout()
#         bot.setSpacing(8)

#         self.progress_bar = QProgressBar()
#         self.progress_bar.setValue(0)
#         self.progress_bar.setFixedHeight(6)
#         bot.addWidget(self.progress_bar)

#         row_bot = QHBoxLayout()
#         row_bot.setSpacing(12)

#         self.lbl_status = QLabel("Preparat.")
#         self.lbl_status.setObjectName("status_label")
#         self.lbl_status.setStyleSheet("color:#4b5263; font-size:12px;")
#         row_bot.addWidget(self.lbl_status, 1)

#         self.btn_cancel = QPushButton("Cancel·la")
#         self.btn_cancel.setObjectName("btn_cancel")
#         self.btn_cancel.setEnabled(False)
#         self.btn_cancel.clicked.connect(self._cancel_run)
#         row_bot.addWidget(self.btn_cancel)

#         self.btn_run = QPushButton("▶  Importar")
#         self.btn_run.setObjectName("btn_run")
#         self.btn_run.setEnabled(False)
#         self.btn_run.clicked.connect(self._start_run)
#         row_bot.addWidget(self.btn_run)

#         bot.addLayout(row_bot)
#         root.addLayout(bot)

#     # ── Config panel ──────────────────────────────────────────────────────────
#     def _refresh_config_panel(self):
#         if not DEPS_OK:
#             for le in self._cfg_fields.values():
#                 le.setText("(dependències no disponibles)")
#             return
#         for attr, le in self._cfg_fields.items():
#             val = getattr(Config, attr, "(no definit)")
#             le.setText(str(val))

#     # ── Browse BOM ────────────────────────────────────────────────────────────
#     def _browse_bom(self):
#         path, _ = QFileDialog.getOpenFileName(
#             self, "Selecciona albarà LCSC",
#             str(Path.home()),
#             "Fitxers CSV/TSV (*.csv *.tsv);;Tots els fitxers (*)"
#         )
#         if path:
#             self.le_bom.setText(path)

#     def _on_bom_changed(self, text):
#         p = Path(text.strip())
#         if p.is_file():
#             size_kb = p.stat().st_size / 1024
#             self.lbl_bom_info.setText(
#                 f"{p.name}  ·  {size_kb:.1f} KB  ·  {p.parent}"
#             )
#             self.lbl_bom_info.setStyleSheet("color:#34d399; font-size:11px;")
#             self.btn_run.setEnabled(DEPS_OK and not self._running)
#         else:
#             self.lbl_bom_info.setText("Fitxer no trobat")
#             self.lbl_bom_info.setStyleSheet("color:#f87171; font-size:11px;")
#             self.btn_run.setEnabled(False)

#     # ── Run ───────────────────────────────────────────────────────────────────
#     def _start_run(self):
#         bom_file = self.le_bom.text().strip()
#         if not Path(bom_file).is_file():
#             self.lbl_status.setText("Selecciona un fitxer vàlid primer.")
#             return

#         self._running = True
#         self.btn_run.setEnabled(False)
#         self.btn_cancel.setEnabled(True)
#         self.progress_bar.setValue(0)
#         self.lbl_status.setStyleSheet("color:#60a5fa; font-size:12px;")
#         self.lbl_status.setText("Executant…")

#         backup_type = self.combo_backup.currentText()

#         self._worker = ImportWorker(bom_file, backup_type, skip_confirm=True)
#         self._thread = QThread()
#         self._worker.moveToThread(self._thread)

#         self._thread.started.connect(self._worker.run)
#         self._worker.log.connect(self._on_log)
#         self._worker.progress.connect(self.progress_bar.setValue)
#         self._worker.finished.connect(self._on_finished)
#         self._worker.finished.connect(self._thread.quit)
#         self._thread.finished.connect(self._cleanup_thread)

#         self._thread.start()

#     def _cancel_run(self):
#         if self._worker:
#             self._worker.abort()
#         self.lbl_status.setStyleSheet("color:#fbbf24; font-size:12px;")
#         self.lbl_status.setText("Cancel·lant…")
#         self.btn_cancel.setEnabled(False)

#     def _on_log(self, msg: str, tipo: str):
#         self.log_view.append_msg(msg, tipo)

#     def _on_finished(self, success: bool, msg: str):
#         self._running = False
#         self.btn_cancel.setEnabled(False)
#         self.btn_run.setEnabled(True)
#         if success:
#             self.lbl_status.setStyleSheet("color:#34d399; font-size:12px;")
#             self.progress_bar.setValue(100)
#         else:
#             self.lbl_status.setStyleSheet("color:#f87171; font-size:12px;")
#         self.lbl_status.setText(msg)

#     def _cleanup_thread(self):
#         self._thread  = None
#         self._worker  = None


# # =============================================================================
# #  ENTRY POINT
# # =============================================================================

# def main():
#     app = QApplication(sys.argv)
#     app.setStyleSheet(APP_STYLE)

#     # Paleta base fosca
#     palette = QPalette()
#     palette.setColor(QPalette.Window,          QColor("#1a1d23"))
#     palette.setColor(QPalette.WindowText,      QColor("#d0d4de"))
#     palette.setColor(QPalette.Base,            QColor("#21252e"))
#     palette.setColor(QPalette.AlternateBase,   QColor("#1e2128"))
#     palette.setColor(QPalette.Text,            QColor("#d0d4de"))
#     palette.setColor(QPalette.Button,          QColor("#21252e"))
#     palette.setColor(QPalette.ButtonText,      QColor("#d0d4de"))
#     palette.setColor(QPalette.Highlight,       QColor("#1d4ed8"))
#     palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
#     app.setPalette(palette)

#     win = MainWindow()
#     win.show()
#     sys.exit(app.exec())


# if __name__ == "__main__":

    # main()




















"""
nowstock_app.py
===============
App d'escriptori PySide6 per importar albarans LCSC al Google Sheet d'estoc.
Estil Windows flat, clar i senzill.

Requisits:
    pip install PySide6 gspread google-auth

Ús:
    python nowstock_app.py
"""

import os
import sys
import csv
import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
    QGroupBox, QFrame, QProgressBar,
)
from PySide6.QtCore import Qt, QThread, QObject, Signal
from PySide6.QtGui import QTextCursor

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
    padding: 10px 10px 10px 10px;
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
    background-color: #f5f5f5;
    color: #888888;
    border-color: #d0d0d0;
}

QPushButton {
    background-color: #e1e1e1;
    border: 1px solid #ababab;
    border-radius: 0px;
    padding: 5px 16px;
    color: #1a1a1a;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #cce4f7;
    border-color: #0078d4;
}
QPushButton:pressed  { background-color: #bbd3e9; }
QPushButton:disabled {
    background-color: #f0f0f0;
    color: #a0a0a0;
    border-color: #d0d0d0;
}

QPushButton#btn_run {
    background-color: #0078d4;
    border: 1px solid #006cbe;
    color: #ffffff;
    font-weight: 600;
    padding: 6px 24px;
}
QPushButton#btn_run:hover   { background-color: #106ebe; }
QPushButton#btn_run:pressed { background-color: #005a9e; }
QPushButton#btn_run:disabled {
    background-color: #cccccc;
    border-color: #bbbbbb;
    color: #888888;
}

QPushButton#btn_cancel {
    background-color: #e1e1e1;
    border: 1px solid #ababab;
    color: #c42b1c;
}
QPushButton#btn_cancel:hover {
    background-color: #fde7e9;
    border-color: #c42b1c;
}
QPushButton#btn_cancel:disabled {
    color: #a0a0a0;
    background-color: #f0f0f0;
    border-color: #d0d0d0;
}

QTextEdit#log_output {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 0px;
    color: #1a1a1a;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 12px;
    padding: 6px;
    selection-background-color: #0078d4;
}

QProgressBar {
    background-color: #e1e1e1;
    border: 1px solid #ababab;
    border-radius: 0px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 0px;
}

QLabel#lbl_title   { font-size: 15px; font-weight: 600; color: #1a1a1a; }
QLabel#lbl_section { font-size: 12px; font-weight: 600; color: #444444; }
QLabel#lbl_status  { font-size: 12px; color: #555555; }
"""


# =============================================================================
#  WORKER
# =============================================================================

class ImportWorker(QObject):
    log      = Signal(str, str)
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, bom_file: str):
        super().__init__()
        self.bom_file = bom_file
        self._abort   = False

    def abort(self):
        self._abort = True

    def _log(self, msg, t="info"): self.log.emit(msg, t)
    def _ok(self, msg):            self.log.emit(msg, "ok")
    def _warn(self, msg):          self.log.emit(msg, "warn")
    def _err(self, msg):           self.log.emit(msg, "error")
    def _head(self, msg):          self.log.emit(msg, "head")

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
        self._ok(f"Sheet llegit: {len(rows)} files (capçalera inclosa)")
        return rows

    def _write_rows(self, client, rows):
        ws = client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1
        ws.clear()
        ws.update(rows, value_input_option="USER_ENTERED")
        self._ok(f"Sheet actualitzat: {len(rows)} files escrites")

    def _backup_csv(self, client):
        folder = getattr(Config, "BACKUP_FOLDER", str(Path.home() / "Downloads"))
        os.makedirs(folder, exist_ok=True)
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(folder, f"backup_stock_{ts}.csv")
        rows  = self._fetch_rows(client)
        with open(fname, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
        size = os.path.getsize(fname) / 1024
        self._ok(f"Backup desat: {fname}  ({len(rows)} files, {size:.1f} KB)")
        return fname, rows

    def _read_bom(self, filepath):
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            sample = f.read(4096)
        sep = "\t" if sample.count("\t") > sample.count(",") else ","
        rows = []
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=sep):
                clean = {k.strip(): v.strip() for k, v in r.items() if k}
                if clean.get("LCSC Part Number"):
                    rows.append(clean)
        self._ok(f"Albarà llegit: {len(rows)} components  (sep={'TAB' if sep==chr(9) else 'COMA'})")
        return rows

    @staticmethod
    def _next_id(data_rows):
        ids = []
        for row in data_rows:
            try:
                ids.append(int(str(row[Config.ID]).strip()))
            except (ValueError, IndexError):
                pass
        return max(ids, default=0) + 1

    def _build_new_row(self, new_id, lcsc_part, bom_row, api):
        tc  = Config.SUPPLIER_PRODUCT + 1
        row = [""] * tc
        try:
            qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
        except ValueError:
            qty = 0
        row[Config.ID]                = new_id
        row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
        row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
        row[Config.CATEGORY]          = api.get("type2", "")
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

    def _fill_empty(self, row, api):
        tc = Config.SUPPLIER_PRODUCT + 1
        fill_map = {
            Config.MANUFACTURER_PN:   api.get("name", ""),
            Config.MANUFACTURER_NAME: api.get("manufacturer", ""),
            Config.CATEGORY:          api.get("type2", ""),
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
            self._err(f"Falten dependències: {_MISSING}")
            self.finished.emit(False, "Dependències no instal·lades.")
            return
        try:
            tc = Config.SUPPLIER_PRODUCT + 1

            # PAS 1
            self._head("PAS 1 — Connexió i backup")
            self.progress.emit(5)
            client = self._get_client()
            self._ok("Client Google autenticat")
            self.progress.emit(10)
            backup_ref, all_rows = self._backup_csv(client)
            self.progress.emit(20)
            header_row = all_rows[0] if all_rows else []
            data_rows  = [list(r) for r in all_rows[1:]]
            self._log(f"Components al stock actual: {len(data_rows)}")
            self.progress.emit(25)

            # PAS 2
            self._head("PAS 2 — Llegint albarà LCSC")
            bom_components = self._read_bom(self.bom_file)
            for c in bom_components:
                lp  = c.get("LCSC Part Number", "?")
                mpn = c.get("Manufacture Part Number", "")
                qty = c.get("Order Qty.", "?")
                self._log(f"  {lp:<14}  {mpn:<28}  qty={qty}")
            self.progress.emit(35)

            # PAS 3
            self._head("PAS 3 — Processant components")
            stock_by_lcsc = {}
            for i, row in enumerate(data_rows):
                if len(row) > Config.SUPPLIER_PN:
                    part = str(row[Config.SUPPLIER_PN]).strip()
                    if part:
                        stock_by_lcsc[part] = i

            stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
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

                self.progress.emit(35 + int((idx_bom / max(total, 1)) * 55))

                if lcsc_part in stock_by_lcsc:
                    i = stock_by_lcsc[lcsc_part]
                    while len(data_rows[i]) < tc:
                        data_rows[i].append("")
                    try:
                        qty_old = int(float(str(data_rows[i][Config.STOCK]).strip() or "0"))
                    except ValueError:
                        qty_old = 0
                    qty_total = qty_old + qty_new
                    data_rows[i][Config.STOCK] = qty_total
                    self._ok(f"[EXISTENT] {lcsc_part}  {qty_old} + {qty_new} = {qty_total}")
                    stats["estoc_sumat"] += 1

                    needs_fill = any(
                        not str(data_rows[i][c]).strip()
                        for c in [Config.MANUFACTURER_PN, Config.MANUFACTURER_NAME,
                                  Config.CATEGORY, Config.PACKAGE, Config.DESCRIPTION,
                                  Config.DATASHEET, Config.SUPPLIER_PRODUCT]
                        if c < len(data_rows[i])
                    )
                    if needs_fill:
                        self._log("          → Camps buits, consultant API...")
                        api = get_lcsc_data(lcsc_part)
                        if api:
                            data_rows[i], nf = self._fill_empty(data_rows[i], api)
                            self._ok(f"          → {nf} camps completats")
                            stats["info_completada"] += 1
                        else:
                            self._warn("          → API LCSC sense resposta")
                            stats["errors_api"] += 1
                else:
                    self._log(f"[NOU]      {lcsc_part}  → consultant API LCSC...")
                    api = get_lcsc_data(lcsc_part)
                    if api:
                        new_row = self._build_new_row(next_id, lcsc_part, bom_row, api)
                        mfr = api.get("manufacturer", "?")
                        mpn = api.get("name", "?")
                        ds  = "amb datasheet" if api.get("datasheet") else "sense datasheet"
                        self._ok(f"          → ID={next_id}  {mfr}  |  {mpn}  |  {ds}")
                    else:
                        self._warn("          → API sense resposta, usant dades de l'albarà")
                        new_row = self._build_new_row(next_id, lcsc_part, bom_row, {})
                        stats["errors_api"] += 1
                    data_rows.append(new_row)
                    stock_by_lcsc[lcsc_part] = len(data_rows) - 1
                    next_id += 1
                    stats["nous"] += 1

            self.progress.emit(92)
            self._head("Resum")
            self._ok(f"Nous components afegits  : {stats['nous']}")
            self._ok(f"Estoc actualitzat (suma) : {stats['estoc_sumat']}")
            self._ok(f"Info completada via API  : {stats['info_completada']}")
            if stats["errors_api"]:
                self._warn(f"Errors / API no resposta : {stats['errors_api']}")

            # PAS 4
            self._head("PAS 4 — Escrivint al Google Sheet")
            self._write_rows(client, [header_row] + data_rows)
            self.progress.emit(100)

            self.finished.emit(True,
                f"Completat.  Nous: {stats['nous']}  |  "
                f"Actualitzats: {stats['estoc_sumat']}  |  "
                f"Backup: {backup_ref}"
            )
        except Exception as exc:
            import traceback
            self._err(traceback.format_exc())
            self.finished.emit(False, f"ERROR: {exc}")


# =============================================================================
#  LOG WIDGET
# =============================================================================

class LogWidget(QTextEdit):
    COLORS = {
        "info":  "#1a1a1a",
        "ok":    "#107c10",
        "warn":  "#9a5a00",
        "error": "#c42b1c",
        "head":  "#0078d4",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_output")
        self.setReadOnly(True)

    def append_msg(self, msg: str, tipo: str = "info"):
        color  = self.COLORS.get(tipo, "#1a1a1a")
        prefix = {"ok": "✓", "warn": "⚠", "error": "✗", "head": "▶"}.get(tipo, " ")
        ts     = datetime.datetime.now().strftime("%H:%M:%S")
        html   = (
            f'<span style="color:#888888;">[{ts}]</span>&nbsp;'
            f'<span style="color:{color};">{prefix} {msg}</span>'
        )
        self.append(html)
        self.moveCursor(QTextCursor.End)


# =============================================================================
#  FINESTRA PRINCIPAL
# =============================================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("myStock")
        self.setMinimumSize(640, 460)
        self.resize(780, 520)
        self._worker  = None
        self._thread  = None
        self._running = False
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        # ── Capçalera ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        lbl_title = QLabel("Importació albarà LCSC")
        lbl_title.setObjectName("lbl_title")
        hdr.addWidget(lbl_title)
        hdr.addStretch()

        if DEPS_OK:
            badge = QLabel("● Connectat")
            badge.setStyleSheet("color:#107c10; font-size:12px;")
        else:
            badge = QLabel("● Dependències no disponibles")
            badge.setStyleSheet("color:#c42b1c; font-size:12px;")
        hdr.addWidget(badge)
        root.addLayout(hdr)

        root.addWidget(self._hsep())

        # ── Selector fitxer albarà ─────────────────────────────────────────────
        grp = QGroupBox()
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(6)
        grp_lay.setContentsMargins(10, 8, 10, 8)

        lbl_sec = QLabel("Fitxer d'albarà")
        lbl_sec.setObjectName("lbl_section")
        grp_lay.addWidget(lbl_sec)

        row_file = QHBoxLayout()
        row_file.setSpacing(6)
        self.le_bom = QLineEdit()
        self.le_bom.setPlaceholderText("Selecciona el fitxer .csv o .tsv de la comanda LCSC…")
        self.le_bom.textChanged.connect(self._on_bom_changed)
        btn_browse = QPushButton("Cerca…")
        btn_browse.setFixedWidth(72)
        btn_browse.clicked.connect(self._browse_bom)
        row_file.addWidget(self.le_bom)
        row_file.addWidget(btn_browse)
        grp_lay.addLayout(row_file)

        self.lbl_file_info = QLabel("Cap fitxer seleccionat.")
        self.lbl_file_info.setStyleSheet("color:#888888; font-size:11px;")
        grp_lay.addWidget(self.lbl_file_info)

        root.addWidget(grp)

        root.addWidget(self._hsep())

        # ── Registre d'execució ───────────────────────────────────────────────
        lbl_log = QLabel("Registre d'execució")
        lbl_log.setObjectName("lbl_section")
        root.addWidget(lbl_log)

        self.log_view = LogWidget()
        root.addWidget(self.log_view, 1)

        # ── Progrés ───────────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)

        root.addWidget(self._hsep())

        # ── Botons ────────────────────────────────────────────────────────────
        bot = QHBoxLayout()
        bot.setSpacing(6)

        self.lbl_status = QLabel("Preparat.")
        self.lbl_status.setObjectName("lbl_status")
        bot.addWidget(self.lbl_status, 1)

        btn_clear = QPushButton("Netejar registre")
        btn_clear.clicked.connect(self.log_view.clear)
        bot.addWidget(btn_clear)

        self.btn_cancel = QPushButton("Cancel·la")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.clicked.connect(self._cancel_run)
        bot.addWidget(self.btn_cancel)

        self.btn_run = QPushButton("Importar")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setEnabled(False)
        self.btn_run.setFixedWidth(100)
        self.btn_run.clicked.connect(self._start_run)
        bot.addWidget(self.btn_run)

        root.addLayout(bot)

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _hsep():
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet("background-color:#d0d0d0; border:none;")
        return f

    def _default_bom_folder(self) -> str:
        """Carpeta predefinida per al diàleg de cerca d'albarans."""
        # 1. Atribut específic LCSC_BOM_FOLDER a Config
        folder = getattr(Config, "LCSC_BOM_FOLDER", None)
        if folder and Path(folder).is_dir():
            return str(folder)
        # 2. Fallback: BACKUP_FOLDER
        folder = getattr(Config, "BACKUP_FOLDER", None)
        if folder and Path(folder).is_dir():
            return str(folder)
        # 3. Downloads de l'usuari
        return str(Path.home() / "Downloads")

    # ── Browse ────────────────────────────────────────────────────────────────
    def _browse_bom(self):
        start = self._default_bom_folder()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona albarà LCSC",
            start,
            "Fitxers CSV/TSV (*.csv *.tsv);;Tots els fitxers (*)"
        )
        if path:
            self.le_bom.setText(path)

    def _on_bom_changed(self, text):
        p = Path(text.strip())
        if p.is_file():
            size_kb = p.stat().st_size / 1024
            self.lbl_file_info.setText(f"{p.name}   ·   {size_kb:.1f} KB   ·   {p.parent}")
            self.lbl_file_info.setStyleSheet("color:#107c10; font-size:11px;")
            self.btn_run.setEnabled(DEPS_OK and not self._running)
        else:
            msg = "Fitxer no trobat." if text.strip() else "Cap fitxer seleccionat."
            col = "#c42b1c" if text.strip() else "#888888"
            self.lbl_file_info.setText(msg)
            self.lbl_file_info.setStyleSheet(f"color:{col}; font-size:11px;")
            self.btn_run.setEnabled(False)

    # ── Run / Cancel ──────────────────────────────────────────────────────────
    def _start_run(self):
        bom_file = self.le_bom.text().strip()
        if not Path(bom_file).is_file():
            self.lbl_status.setText("Selecciona un fitxer vàlid primer.")
            return

        self._running = True
        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setStyleSheet("color:#0078d4; font-size:12px;")
        self.lbl_status.setText("Executant…")

        self._worker = ImportWorker(bom_file)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._on_log)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _cancel_run(self):
        if self._worker:
            self._worker.abort()
        self.lbl_status.setStyleSheet("color:#9a5a00; font-size:12px;")
        self.lbl_status.setText("Cancel·lant…")
        self.btn_cancel.setEnabled(False)

    def _on_log(self, msg: str, tipo: str):
        self.log_view.append_msg(msg, tipo)

    def _on_finished(self, success: bool, msg: str):
        self._running = False
        self.btn_cancel.setEnabled(False)
        self.btn_run.setEnabled(Path(self.le_bom.text().strip()).is_file())
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