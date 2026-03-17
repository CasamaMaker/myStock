# """
# lcsc_stock_import.py
# ====================
# Importa albarans de LCSC al Google Sheet d'estoc (projecte mystock).

# Flux:
#   1. Backup del Google Sheet → fitxer JSON local
#   2. Llegir albarà LCSC (.csv / .tsv)
#   3. Components nous      → consulta API LCSC + afegeix fila completa
#   4. Components existents → suma estoc + omple camps buits via API
#   5. Escriu al Google Sheet (amb confirmació manual per consola)

# Ús:
#   python lcsc_stock_import.py lcsc_order.csv
#   python lcsc_stock_import.py lcsc_order.csv --yes   # salta confirmació
# """

# import os
# import sys
# import csv
# import json
# import datetime
# import argparse
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
# #  CONSTANTS
# # =============================================================================

# BACKUP_FOLDER = "backups"
# TOTAL_COLS    = Config.SUPPLIER_PRODUCT + 1   # 13 columnes (0..12)

# GSCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive",
# ]


# # =============================================================================
# #  GOOGLE SHEETS
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
# #  BACKUP
# # =============================================================================

# def backup_sheet(client) -> tuple:
#     """Desa còpia JSON del sheet. Retorna (nom_fitxer, llista_de_files)."""
#     os.makedirs(BACKUP_FOLDER, exist_ok=True)
#     ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.json")

#     print("  Llegint sheet per fer backup...")
#     rows = fetch_sheet_rows(client)

#     with open(fname, "w", encoding="utf-8") as f:
#         json.dump(rows, f, ensure_ascii=False, indent=2)

#     size_kb = os.path.getsize(fname) / 1024
#     print(f"  Backup desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
#     return fname, rows


# # =============================================================================
# #  LECTURA ALBARA LCSC
# # =============================================================================

# def read_lcsc_bom(filepath: str) -> list:
#     """
#     Llegeix l'albara LCSC. Auto-detecta separador TAB o COMA.
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
#     Construeix una fila nova combinant dades de l'albara i de l'API LCSC.
#     Prioritat: API > albara.

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
#       Col 9   STOCK            -> quantitat de l'albara
#       Col 10  STORAGE          -> buit (omplir manualment)
#       Col 11  DATASHEET        -> api['datasheet']  (pdfUrl)
#       Col 12  SUPPLIER_PRODUCT -> api['store']  (URL pagina LCSC)
#     """
#     row = [""] * TOTAL_COLS

#     try:
#         qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#     except ValueError:
#         qty = 0

#     row[Config.ID]                = new_id
#     row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
#     row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
#     row[Config.CATEGORY]          = ""
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
#     MAI sobreescriu un camp que ja te valor.
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

# def print_preview(data_rows: list, bom_parts: set, backup_file: str):
#     print("\nPreview dels components de l'albara (tal com quedaran al sheet):\n")
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

#     print(f"\n  Total files al sheet (sense capcalera): {len(data_rows)}")
#     print(f"  Backup disponible a: {backup_file}")


# # =============================================================================
# #  FLUX PRINCIPAL
# # =============================================================================

# def run(bom_file: str, skip_confirm: bool = False):

#     # ── PAS 1: Connexio i backup ───────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 1 -- Connectant a Google Sheets i fent backup")
#     print("=" * 58)

#     client = get_gspread_client()
#     print("  Client autenticat correctament")

#     backup_file, all_rows = backup_sheet(client)

#     header_row = all_rows[0] if all_rows else []
#     data_rows  = [list(r) for r in all_rows[1:]]   # copia editable

#     print(f"\n  Capcalera          : {header_row}")
#     print(f"  Components al stock: {len(data_rows)}")

#     # ── PAS 2: Llegir albara ───────────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 2 -- Llegint albara LCSC")
#     print("=" * 58)

#     bom_components = read_lcsc_bom(bom_file)

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

#     # Index del stock actual per LCSC Part Number (col SUPPLIER_PN = 5)
#     stock_by_lcsc = {}
#     for i, row in enumerate(data_rows):
#         if len(row) > Config.SUPPLIER_PN:
#             part = str(row[Config.SUPPLIER_PN]).strip()
#             if part:
#                 stock_by_lcsc[part] = i

#     print(f"  Components LCSC indexats al stock: {len(stock_by_lcsc)}")

#     stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
#     next_id = _next_id(data_rows)
#     print(f"  Proxim ID disponible: {next_id}\n")

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
#                 print(f"             AVIS: API no ha respost -- usant dades de l'albara")
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
#     print_preview(data_rows, bom_parts, backup_file)

#     # ── Confirmacio ────────────────────────────────────────────────────────────
#     if not skip_confirm:
#         print("\nVols escriure els canvis al Google Sheet? [s/N] ", end="", flush=True)
#         answer = input().strip().lower()
#         if answer not in ("s", "si", "si", "y", "yes"):
#             print("Operacio cancel-lada. No s'ha modificat res al sheet.")
#             print(f"El backup segueix disponible a: {backup_file}")
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
#     print(f"  Backup guardat a        : {backup_file}\n")


# # =============================================================================
# #  ENTRY POINT
# # =============================================================================

# def main():
#     parser = argparse.ArgumentParser(
#         description="Importa un albara LCSC al Google Sheet d'estoc (mystock)."
#     )
#     parser.add_argument(
#         "bom_file",
#         help="Ruta al fitxer albara LCSC (.csv o .tsv)"
#     )
#     parser.add_argument(
#         "--yes", "-y",
#         action="store_true",
#         help="Salta la confirmacio manual i escriu directament"
#     )
#     args = parser.parse_args()

#     if not os.path.isfile(args.bom_file):
#         print(f"ERROR: Fitxer no trobat: {args.bom_file}")
#         sys.exit(1)

#     run(bom_file=args.bom_file, skip_confirm=args.yes)


# if __name__ == "__main__":
#     main()














# """
# lcsc_stock_import.py
# ====================
# Importa albarans de LCSC al Google Sheet d'estoc (projecte mystock).

# Flux:
#   1. Backup del Google Sheet → fitxer JSON local
#   2. Llegir albarà LCSC (.csv / .tsv)
#   3. Components nous      → consulta API LCSC + afegeix fila completa
#   4. Components existents → suma estoc + omple camps buits via API
#   5. Escriu al Google Sheet (amb confirmació manual per consola)

# Ús:
#   python lcsc_stock_import.py lcsc_order.csv
#   python lcsc_stock_import.py lcsc_order.csv --yes   # salta confirmació
# """

# import os
# import sys
# import csv
# import datetime
# import argparse
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
# #  CONSTANTS
# # =============================================================================

# BACKUP_FOLDER = "backups"
# TOTAL_COLS    = Config.SUPPLIER_PRODUCT + 1   # 13 columnes (0..12)

# GSCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive",
# ]


# # =============================================================================
# #  GOOGLE SHEETS
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
# #  BACKUP
# # =============================================================================

# def backup_sheet(client) -> tuple:
#     """Desa còpia CSV del sheet. Retorna (nom_fitxer, llista_de_files)."""
#     os.makedirs(BACKUP_FOLDER, exist_ok=True)
#     ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.csv")

#     print("  Llegint sheet per fer backup...")
#     rows = fetch_sheet_rows(client)

#     with open(fname, "w", newline="", encoding="utf-8-sig") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)

#     size_kb = os.path.getsize(fname) / 1024
#     print(f"  Backup desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
#     return fname, rows


# # =============================================================================
# #  LECTURA ALBARA LCSC
# # =============================================================================

# def read_lcsc_bom(filepath: str) -> list:
#     """
#     Llegeix l'albara LCSC. Auto-detecta separador TAB o COMA.
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
#     Construeix una fila nova combinant dades de l'albara i de l'API LCSC.
#     Prioritat: API > albara.

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
#       Col 9   STOCK            -> quantitat de l'albara
#       Col 10  STORAGE          -> buit (omplir manualment)
#       Col 11  DATASHEET        -> api['datasheet']  (pdfUrl)
#       Col 12  SUPPLIER_PRODUCT -> api['store']  (URL pagina LCSC)
#     """
#     row = [""] * TOTAL_COLS

#     try:
#         qty = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
#     except ValueError:
#         qty = 0

#     row[Config.ID]                = new_id
#     row[Config.MANUFACTURER_PN]   = api.get("name")         or bom_row.get("Manufacture Part Number", "")
#     row[Config.MANUFACTURER_NAME] = api.get("manufacturer") or bom_row.get("Manufacturer", "")
#     row[Config.CATEGORY]          = ""
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
#     MAI sobreescriu un camp que ja te valor.
#     Retorna (row_actualitzat, nombre_de_camps_omplerts).
#     """
#     fill_map = {
#         Config.MANUFACTURER_PN:   api.get("name", ""),
#         Config.MANUFACTURER_NAME: api.get("manufacturer", ""),
#         Config.CATEGORY:          "",
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

# def print_preview(data_rows: list, bom_parts: set, backup_file: str):
#     print("\nPreview dels components de l'albara (tal com quedaran al sheet):\n")
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

#     print(f"\n  Total files al sheet (sense capcalera): {len(data_rows)}")
#     print(f"  Backup disponible a: {backup_file}")


# # =============================================================================
# #  FLUX PRINCIPAL
# # =============================================================================

# def run(bom_file: str, skip_confirm: bool = False):

#     # ── PAS 1: Connexio i backup ───────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 1 -- Connectant a Google Sheets i fent backup")
#     print("=" * 58)

#     client = get_gspread_client()
#     print("  Client autenticat correctament")

#     backup_file, all_rows = backup_sheet(client)

#     header_row = all_rows[0] if all_rows else []
#     data_rows  = [list(r) for r in all_rows[1:]]   # copia editable

#     print(f"\n  Capcalera          : {header_row}")
#     print(f"  Components al stock: {len(data_rows)}")

#     # ── PAS 2: Llegir albara ───────────────────────────────────────────────────
#     print("\n" + "=" * 58)
#     print(" PAS 2 -- Llegint albara LCSC")
#     print("=" * 58)

#     bom_components = read_lcsc_bom(bom_file)

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

#     # Index del stock actual per LCSC Part Number (col SUPPLIER_PN = 5)
#     stock_by_lcsc = {}
#     for i, row in enumerate(data_rows):
#         if len(row) > Config.SUPPLIER_PN:
#             part = str(row[Config.SUPPLIER_PN]).strip()
#             if part:
#                 stock_by_lcsc[part] = i

#     print(f"  Components LCSC indexats al stock: {len(stock_by_lcsc)}")

#     stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
#     next_id = _next_id(data_rows)
#     print(f"  Proxim ID disponible: {next_id}\n")

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
#                 print(f"             AVIS: API no ha respost -- usant dades de l'albara")
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
#     print_preview(data_rows, bom_parts, backup_file)

#     # ── Confirmacio ────────────────────────────────────────────────────────────
#     if not skip_confirm:
#         print("\nVols escriure els canvis al Google Sheet? [s/N] ", end="", flush=True)
#         answer = input().strip().lower()
#         if answer not in ("s", "si", "si", "y", "yes"):
#             print("Operacio cancel-lada. No s'ha modificat res al sheet.")
#             print(f"El backup segueix disponible a: {backup_file}")
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
#     print(f"  Backup guardat a        : {backup_file}\n")


# # =============================================================================
# #  ENTRY POINT
# # =============================================================================

# def main():
#     parser = argparse.ArgumentParser(
#         description="Importa un albara LCSC al Google Sheet d'estoc (mystock)."
#     )
#     parser.add_argument(
#         "bom_file",
#         help="Ruta al fitxer albara LCSC (.csv o .tsv)"
#     )
#     parser.add_argument(
#         "--yes", "-y",
#         action="store_true",
#         help="Salta la confirmacio manual i escriu directament"
#     )
#     args = parser.parse_args()

#     if not os.path.isfile(args.bom_file):
#         print(f"ERROR: Fitxer no trobat: {args.bom_file}")
#         sys.exit(1)

#     run(bom_file=args.bom_file, skip_confirm=args.yes)


# if __name__ == "__main__":
#     main()






# # python lcsc_stock_import.py lcsc_order.csv





























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
# LCSC_BOM_FILE = "LCSC_Exported_20220929_014129.csv "#"lcsc_order.csv"

# # Si True, escriu al Google Sheet sense demanar confirmació
# SKIP_CONFIRM = False

# # Tipus de backup:
# #   "csv"    -> fitxer .csv local a la carpeta BACKUP_FOLDER
# #   "google" -> còpia del Google Sheet al Google Drive
# #   "both"   -> fa els dos alhora
# BACKUP_TYPE = "csv"

# # Carpeta local on es desen els backups CSV (es crea si no existeix)
# BACKUP_FOLDER = "C:/Users/ecasamayor/Downloads/backups"

# # Nom base del Google Sheet de backup (s'afegeix data i hora automàticament)
# BACKUP_GOOGLE_NAME = "backup_stock"


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


# # =============================================================================
# #  BACKUP — Google Sheet al Drive
# # =============================================================================

# def backup_sheet_google(client) -> tuple:
#     """
#     Crea una còpia del Google Sheet directament al Google Drive
#     com un nou Google Sheet (format natiu, no CSV).
#     El fitxer nou es desa a la mateixa carpeta que l'original al Drive.
#     Retorna (nom_del_nou_sheet, llista_de_files).
#     """
#     ts         = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     new_name   = f"{BACKUP_GOOGLE_NAME}_{ts}"

#     print("  Llegint sheet per fer backup al Google Drive...")
#     rows = fetch_sheet_rows(client)

#     # Crear nou Google Sheet buit amb el nom de backup
#     new_sh = client.create(new_name)
#     new_ws = new_sh.sheet1

#     # Escriure totes les dades
#     if rows:
#         new_ws.update(rows, value_input_option="USER_ENTERED")

#     # Construir URL del nou sheet per mostrar-la
#     new_url = f"https://docs.google.com/spreadsheets/d/{new_sh.id}"
#     print(f"  Backup Google Sheet creat: '{new_name}'")
#     print(f"  URL: {new_url}")
#     print(f"  ({len(rows)} files copiades)")

#     # NOTA: per defecte el nou sheet es crea a "Els meus fitxers" del
#     # service account, no a la mateixa carpeta que l'original.
#     # Per moure'l a una carpeta específica del teu Drive, comparteix
#     # la carpeta amb el service account i descomenta el bloc següent:
#     #
#     # BACKUP_FOLDER_DRIVE_ID = "ID_DE_LA_CARPETA_DEL_DRIVE"
#     # import requests as _req
#     # from google.auth.transport.requests import Request as _GReq
#     # creds = Credentials.from_service_account_file(str(_creds_path()), scopes=GSCOPES)
#     # creds.refresh(_GReq())
#     # _req.post(
#     #     f"https://www.googleapis.com/drive/v3/files/{new_sh.id}",
#     #     headers={"Authorization": f"Bearer {creds.token}"},
#     #     params={"addParents": BACKUP_FOLDER_DRIVE_ID, "removeParents": "root"},
#     # )

#     return new_name, rows


# # =============================================================================
# #  BACKUP — dispatcher segons BACKUP_TYPE
# # =============================================================================

# def do_backup(client) -> tuple:
#     """
#     Executa el backup segons la variable BACKUP_TYPE:
#       'csv'    -> backup_sheet()         (fitxer CSV local)
#       'google' -> backup_sheet_google()  (còpia Google Sheet al Drive)
#       'both'   -> els dos alhora
#     Retorna sempre (referencia_backup, llista_de_files).
#     """
#     btype = BACKUP_TYPE.strip().lower()

#     if btype == "csv":
#         return backup_sheet(client)

#     elif btype == "google":
#         return backup_sheet_google(client)

#     elif btype == "both":
#         print("  -- Backup CSV local --")
#         fname, rows = backup_sheet(client)
#         print("  -- Backup Google Drive --")
#         gname, _    = backup_sheet_google(client)
#         ref = f"CSV: {fname}  |  Google: '{gname}'"
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


















# # https://drive.google.com/drive/folders/1EfiweOrs20U8iacfr1ZJXA_XKSLjmjkw?usp=sharing




"""
lcsc_stock_import.py
====================
Importa albarans de LCSC al Google Sheet d'estoc (projecte mystock).

Flux:
  1. Backup del Google Sheet (CSV local o còpia Google Sheet al Drive)
  2. Llegir albarà LCSC (.csv / .tsv)
  3. Components nous      -> consulta API LCSC + afegeix fila completa
  4. Components existents -> suma estoc + omple camps buits via API
  5. Escriu al Google Sheet (amb confirmació manual per consola)

Ús:
  python lcsc_stock_import.py
"""

import os
import sys
import csv
import datetime
from pathlib import Path

# ── Mòduls del projecte ───────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from configuration import Config
from request_lcsc  import get_lcsc_data

import gspread
from google.oauth2.service_account import Credentials


# =============================================================================
#  CONFIGURACIÓ  ←  EDITA AQUÍ
# =============================================================================

# Ruta a l'albarà LCSC descarregat (.csv o .tsv)
LCSC_BOM_FILE = "LCSC_Exported_20220929_014129.csv"

# Si True, escriu al Google Sheet sense demanar confirmació
SKIP_CONFIRM = False

# Tipus de backup:
#   "csv"    -> fitxer .csv local a la carpeta BACKUP_FOLDER
#   "google" -> còpia del Google Sheet al Google Drive
#   "both"   -> fa els dos alhora
BACKUP_TYPE = "csv"

# Carpeta local on es desen els backups CSV (es crea si no existeix)
BACKUP_FOLDER = r"C:\Users\ecasamayor\Downloads"

# Nom base del Google Sheet de backup (s'afegeix data i hora automàticament)
BACKUP_GOOGLE_NAME = "backup_stock"

# ID de la carpeta del Google Drive on es desaran els backups Google Sheet.
# Ha d'estar compartida amb el service account (Editor).
# L'ID és la part final de la URL de la carpeta:
#   https://drive.google.com/drive/folders/  ← aquí
BACKUP_DRIVE_FOLDER_ID = "1EfiweOrs20U8iacfr1ZJXA_XKSLjmjkw"


# =============================================================================
#  CONSTANTS INTERNES
# =============================================================================

TOTAL_COLS = Config.SUPPLIER_PRODUCT + 1   # 13 columnes (0..12)

GSCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# =============================================================================
#  GOOGLE SHEETS — autenticació i lectura/escriptura
# =============================================================================

def _creds_path() -> Path:
    p = Path(Config.GOOGLE_CREDENTIALS_JSON)
    return p if p.is_absolute() else PROJECT_DIR / p


def get_gspread_client():
    creds_path = _creds_path()
    if not creds_path.exists():
        raise FileNotFoundError(f"Credencials no trobades: {creds_path}")
    creds = Credentials.from_service_account_file(str(creds_path), scopes=GSCOPES)
    return gspread.authorize(creds)


def fetch_sheet_rows(client) -> list:
    sh   = client.open_by_key(Config.GOOGLE_SHEET_ID)
    ws   = sh.sheet1
    rows = ws.get_all_values()
    print(f"  OK Sheet llegit: {len(rows)} files (capçalera inclosa)")
    return rows


def write_sheet_rows(client, rows: list):
    sh = client.open_by_key(Config.GOOGLE_SHEET_ID)
    ws = sh.sheet1
    ws.clear()
    ws.update(rows, value_input_option="USER_ENTERED")
    print(f"  OK Sheet actualitzat: {len(rows)} files escrites")


# =============================================================================
#  BACKUP — CSV local
# =============================================================================

# def backup_sheet(client) -> tuple:
#     """
#     Desa una còpia .xlsx del Google Sheet en local.
#     El format .xlsx s'obre directament a Google Sheets, Excel i LibreOffice.
#     Retorna (nom_fitxer, llista_de_files).
#     """
#     try:
#         import openpyxl
#     except ImportError:
#         raise ImportError(
#             "Falta el paquet 'openpyxl'.\n"
#             "Instal·la'l amb:  pip install openpyxl"
#         )

#     os.makedirs(BACKUP_FOLDER, exist_ok=True)
#     ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.xlsx")

#     print("  Llegint sheet per fer backup...")
#     rows = fetch_sheet_rows(client)

#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Stock"
#     for row in rows:
#         ws.append(row)

#     wb.save(fname)
#     size_kb = os.path.getsize(fname) / 1024
#     print(f"  Backup desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
#     return fname, rows


def backup_sheet(client) -> tuple:
    """
    Desa una còpia CSV del Google Sheet en local.
    Retorna (nom_fitxer, llista_de_files).
    """
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(BACKUP_FOLDER, f"backup_stock_{ts}.csv")

    print("  Llegint sheet per fer backup CSV...")
    rows = fetch_sheet_rows(client)

    with open(fname, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    size_kb = os.path.getsize(fname) / 1024
    print(f"  Backup CSV desat: {fname}  ({len(rows)} files, {size_kb:.1f} KB)")
    return fname, rows

# # =============================================================================
# #  BACKUP — Google Sheet al Drive
# # =============================================================================

# def backup_sheet_google(client) -> tuple:
#     """
#     Crea una còpia del Google Sheet a la carpeta BACKUP_DRIVE_FOLDER_ID del Drive.
#     La carpeta ha d'estar compartida amb el service account com a Editor.
#     Usa files.copy (còpia server-side, sense pujar dades, quota de la carpeta del teu Drive).
#     Retorna (nom_del_nou_sheet, llista_de_files).
#     """
#     import requests as _req
#     from google.auth.transport.requests import Request as _GAuthReq

#     ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     new_name = f"{BACKUP_GOOGLE_NAME}_{ts}"

#     print("  Llegint sheet per fer backup al Google Drive...")
#     rows = fetch_sheet_rows(client)

#     # Token d'accés del service account
#     creds = Credentials.from_service_account_file(str(_creds_path()), scopes=GSCOPES)
#     creds.refresh(_GAuthReq())
#     headers = {
#         "Authorization": f"Bearer {creds.token}",
#         "Content-Type": "application/json",
#     }
#     drive_base = "https://www.googleapis.com/drive/v3/files"

#     # files.copy: duplica l'arxiu original i el posa a BACKUP_DRIVE_FOLDER_ID
#     resp = _req.post(
#         f"{drive_base}/{Config.GOOGLE_SHEET_ID}/copy",
#         headers=headers,
#         params={"supportsAllDrives": "true"},
#         json={
#             "name":    new_name,
#             "parents": [BACKUP_DRIVE_FOLDER_ID],
#         },
#         timeout=30,
#     )

#     if not resp.ok:
#         raise RuntimeError(
#             f"Error en files.copy [{resp.status_code}]:\n{resp.text}"
#         )

#     new_id  = resp.json()["id"]
#     new_url = f"https://docs.google.com/spreadsheets/d/{new_id}"
#     print(f"  Backup Google Sheet creat: '{new_name}'")
#     print(f"  URL: {new_url}")
#     print(f"  ({len(rows)} files copiades)")

#     return new_name, rows


# =============================================================================
#  BACKUP — dispatcher segons BACKUP_TYPE
# =============================================================================

def do_backup(client) -> tuple:
    """
    Executa el backup segons la variable BACKUP_TYPE:
      'csv'    -> backup_sheet()         (fitxer CSV local)
      'google' -> backup_sheet_google()  (còpia Google Sheet al Drive del SA)
      'both'   -> els dos alhora
    Si el backup google falla definitivament, fa fallback a CSV automàticament.
    Retorna sempre (referencia_backup, llista_de_files).
    """
    btype = BACKUP_TYPE.strip().lower()

    if btype == "csv":
        return backup_sheet(client)

    elif btype == "google":
        try:
            return backup_sheet_google(client)
        except RuntimeError as e:
            print(f"\n  ERROR backup Google: {e}")
            print("  Fent fallback a backup CSV local...\n")
            return backup_sheet(client)

    elif btype == "both":
        print("  -- Backup CSV local --")
        fname, rows = backup_sheet(client)
        print("  -- Backup Google Drive --")
        try:
            gname, _ = backup_sheet_google(client)
            ref = f"CSV: {fname}  |  Google: '{gname}'"
        except RuntimeError as e:
            print(f"  AVIS backup Google fallat: {e}")
            ref = f"CSV: {fname}  (backup Google fallat)"
        return ref, rows

    else:
        print(f"  AVIS: BACKUP_TYPE='{BACKUP_TYPE}' no reconegut. Usant 'csv' per defecte.")
        return backup_sheet(client)


# =============================================================================
#  LECTURA ALBARA LCSC
# =============================================================================

def read_lcsc_bom(filepath: str) -> list:
    """
    Llegeix l'albarà LCSC. Auto-detecta separador TAB o COMA.
    Retorna llista de dicts amb les claus originals LCSC:
      'LCSC Part Number', 'Manufacture Part Number', 'Manufacturer',
      'Package', 'Description', 'RoHS', 'Order Qty.', 'Unit Price'
    """
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
    sep = "\t" if sample.count("\t") > sample.count(",") else ","

    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=sep)
        for r in reader:
            clean = {k.strip(): v.strip() for k, v in r.items() if k}
            if clean.get("LCSC Part Number"):
                rows.append(clean)

    sep_name = "TAB" if sep == "\t" else "COMA"
    print(f"  Albara llegit: {len(rows)} components  (separador={sep_name})")
    return rows


# =============================================================================
#  CONSTRUCCIO DE FILES
# =============================================================================

def _next_id(data_rows: list) -> int:
    """Retorna el proxim ID unic (max existent + 1)."""
    ids = []
    for row in data_rows:
        try:
            ids.append(int(str(row[Config.ID]).strip()))
        except (ValueError, IndexError):
            pass
    return max(ids, default=0) + 1


def build_new_row(new_id: int, lcsc_part: str, bom_row: dict, api: dict) -> list:
    """
    Construeix una fila nova combinant dades de l'albarà i de l'API LCSC.
    Prioritat: API > albarà.

    Mapeig (configuration.py):
      Col 0   ID                -> nou ID autogenerat
      Col 1   MANUFACTURER_PN  -> api['name']         | bom MPN
      Col 2   MANUFACTURER_NAME-> api['manufacturer'] | bom Manufacturer
      Col 3   CATEGORY         -> api['type2']  (catalogName)
      Col 4   SUPPLIER         -> 'LCSC'  (fix)
      Col 5   SUPPLIER_PN      -> lcsc_part  (LCSC Part Number)
      Col 6   SUPPLIER_CATEGORY-> api['type2']
      Col 7   PACKAGE          -> api['package']      | bom Package
      Col 8   DESCRIPTION      -> api['description']  | bom Description
      Col 9   STOCK            -> quantitat de l'albarà
      Col 10  STORAGE          -> buit (omplir manualment)
      Col 11  DATASHEET        -> api['datasheet']  (pdfUrl)
      Col 12  SUPPLIER_PRODUCT -> api['store']  (URL pàgina LCSC)
    """
    row = [""] * TOTAL_COLS

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


def fill_empty_cols(row: list, api: dict) -> tuple:
    """
    Omple els camps BUITS d'una fila existent amb dades de l'API LCSC.
    MAI sobreescriu un camp que ja té valor.
    Retorna (row_actualitzat, nombre_de_camps_omplerts).
    """
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

    while len(row) < TOTAL_COLS:
        row.append("")

    filled = 0
    for col_i, val in fill_map.items():
        if val and not str(row[col_i]).strip():
            row[col_i] = val
            filled += 1

    return row, filled


# =============================================================================
#  PREVIEW
# =============================================================================

def print_preview(data_rows: list, bom_parts: set, backup_ref: str):
    print("\nPreview dels components de l'albarà (tal com quedaran al sheet):\n")
    print(f"  {'ID':>4}  {'LCSC Part':^12}  {'MPN':^22}  {'Fabricant':^20}  {'Qty':>5}  DS  Web")
    print("  " + "-" * 82)

    for row in data_rows:
        if len(row) <= Config.SUPPLIER_PN:
            continue
        lcsc = str(row[Config.SUPPLIER_PN]).strip()
        if lcsc not in bom_parts:
            continue

        rid = str(row[Config.ID])
        mpn = str(row[Config.MANUFACTURER_PN])[:22]
        mfr = str(row[Config.MANUFACTURER_NAME])[:20]
        qty = str(row[Config.STOCK])
        ds  = "SI" if len(row) > Config.DATASHEET        and row[Config.DATASHEET]        else "NO"
        web = "SI" if len(row) > Config.SUPPLIER_PRODUCT and row[Config.SUPPLIER_PRODUCT] else "NO"
        print(f"  {rid:>4}  {lcsc:<12}  {mpn:<22}  {mfr:<20}  {qty:>5}  {ds:^2}  {web:^3}")

    print(f"\n  Total files al sheet (sense capçalera): {len(data_rows)}")
    print(f"  Backup: {backup_ref}")


# =============================================================================
#  FLUX PRINCIPAL
# =============================================================================

def run():

    # ── Validació fitxer albarà ────────────────────────────────────────────────
    if not os.path.isfile(LCSC_BOM_FILE):
        print(f"\nERROR: Fitxer albarà no trobat: '{LCSC_BOM_FILE}'")
        print("       Comprova la variable LCSC_BOM_FILE a la secció CONFIGURACIÓ.")
        sys.exit(1)

    # ── PAS 1: Connexió i backup ───────────────────────────────────────────────
    print("\n" + "=" * 58)
    print(" PAS 1 -- Connectant a Google Sheets i fent backup")
    print(f"          (tipus: {BACKUP_TYPE})")
    print("=" * 58)

    client = get_gspread_client()
    print("  Client autenticat correctament")

    backup_ref, all_rows = do_backup(client)

    header_row = all_rows[0] if all_rows else []
    data_rows  = [list(r) for r in all_rows[1:]]   # còpia editable

    print(f"\n  Capçalera          : {header_row}")
    print(f"  Components al stock: {len(data_rows)}")

    # ── PAS 2: Llegir albarà ───────────────────────────────────────────────────
    print("\n" + "=" * 58)
    print(" PAS 2 -- Llegint albarà LCSC")
    print("=" * 58)
    print(f"  Fitxer: {LCSC_BOM_FILE}")

    bom_components = read_lcsc_bom(LCSC_BOM_FILE)

    print(f"\n  {'LCSC Part':^14}  {'MPN':^25}  {'Qty':>6}  {'Unit Price':>10}")
    print("  " + "-" * 62)
    for c in bom_components:
        lp  = c.get("LCSC Part Number", "?")
        mpn = c.get("Manufacture Part Number", "")[:25]
        qty = c.get("Order Qty.", "?")
        prc = c.get("Unit Price", "")
        print(f"  {lp:<14}  {mpn:<25}  {qty:>6}  {prc:>10}")

    # ── PAS 3: Processar components ────────────────────────────────────────────
    print("\n" + "=" * 58)
    print(" PAS 3 -- Processant components")
    print("=" * 58)

    # Índex del stock actual per LCSC Part Number (col SUPPLIER_PN = 5)
    stock_by_lcsc = {}
    for i, row in enumerate(data_rows):
        if len(row) > Config.SUPPLIER_PN:
            part = str(row[Config.SUPPLIER_PN]).strip()
            if part:
                stock_by_lcsc[part] = i

    print(f"  Components LCSC indexats al stock: {len(stock_by_lcsc)}")

    stats   = {"nous": 0, "estoc_sumat": 0, "info_completada": 0, "errors_api": 0}
    next_id = _next_id(data_rows)
    print(f"  Pròxim ID disponible: {next_id}\n")

    for bom_row in bom_components:
        lcsc_part = bom_row.get("LCSC Part Number", "").strip()
        if not lcsc_part:
            continue

        try:
            qty_new = int(float(bom_row.get("Order Qty.", "0").replace(",", "")))
        except ValueError:
            qty_new = 0

        # ── CAS A: Component JA EXISTEIX ──────────────────────────────────────
        if lcsc_part in stock_by_lcsc:
            idx = stock_by_lcsc[lcsc_part]

            while len(data_rows[idx]) < TOTAL_COLS:
                data_rows[idx].append("")

            try:
                qty_old = int(float(str(data_rows[idx][Config.STOCK]).strip() or "0"))
            except ValueError:
                qty_old = 0

            qty_total = qty_old + qty_new
            data_rows[idx][Config.STOCK] = qty_total

            print(f"  [EXISTENT] {lcsc_part:<12}  estoc: {qty_old} + {qty_new} = {qty_total}")
            stats["estoc_sumat"] += 1

            # Comprovar si cal omplir camps buits
            cols_to_check = [
                Config.MANUFACTURER_PN, Config.MANUFACTURER_NAME,
                Config.CATEGORY, Config.PACKAGE, Config.DESCRIPTION,
                Config.DATASHEET, Config.SUPPLIER_PRODUCT,
            ]
            needs_fill = any(
                not str(data_rows[idx][c]).strip()
                for c in cols_to_check if c < len(data_rows[idx])
            )

            if needs_fill:
                print(f"             -> Camps buits detectats, consultant API LCSC...")
                api = get_lcsc_data(lcsc_part)
                if api:
                    data_rows[idx], n_filled = fill_empty_cols(data_rows[idx], api)
                    print(f"             -> {n_filled} camps completats")
                    stats["info_completada"] += 1
                else:
                    print(f"             AVIS: API LCSC no ha retornat dades")
                    stats["errors_api"] += 1

        # ── CAS B: Component NOU ───────────────────────────────────────────────
        else:
            print(f"  [NOU]      {lcsc_part:<12}  consultant API LCSC...")
            api = get_lcsc_data(lcsc_part)

            if api:
                new_row = build_new_row(next_id, lcsc_part, bom_row, api)
                mfr = api.get("manufacturer", "?")
                mpn = api.get("name", "?")
                ds  = "amb datasheet" if api.get("datasheet") else "sense datasheet"
                print(f"             -> ID={next_id}  {mfr}  |  {mpn}  |  {ds}")
            else:
                print(f"             AVIS: API no ha respost -- usant dades de l'albarà")
                new_row = build_new_row(next_id, lcsc_part, bom_row, {})
                stats["errors_api"] += 1

            data_rows.append(new_row)
            stock_by_lcsc[lcsc_part] = len(data_rows) - 1
            next_id += 1
            stats["nous"] += 1

    print("\n" + "-" * 44)
    print(f"  Nous components afegits   : {stats['nous']}")
    print(f"  Estoc actualitzat (suma)  : {stats['estoc_sumat']}")
    print(f"  Info completada via API   : {stats['info_completada']}")
    print(f"  Errors / API no resposta  : {stats['errors_api']}")
    print("-" * 44)

    # ── Preview ────────────────────────────────────────────────────────────────
    bom_parts = {r.get("LCSC Part Number", "").strip() for r in bom_components}
    print_preview(data_rows, bom_parts, backup_ref)

    # ── Confirmació ────────────────────────────────────────────────────────────
    if not SKIP_CONFIRM:
        print("\nVols escriure els canvis al Google Sheet? [s/N] ", end="", flush=True)
        answer = input().strip().lower()
        if answer not in ("s", "si", "y", "yes"):
            print("Operació cancel·lada. No s'ha modificat res al sheet.")
            print(f"El backup segueix disponible: {backup_ref}")
            return

    # ── PAS 4: Escriure al sheet ───────────────────────────────────────────────
    print("\n" + "=" * 58)
    print(" PAS 4 -- Escrivint al Google Sheet...")
    print("=" * 58)

    final_data = [header_row] + data_rows
    write_sheet_rows(client, final_data)

    print("\nCOMPLETAT!")
    print(f"  Components al stock     : {len(data_rows)}")
    print(f"  Nous afegits            : {stats['nous']}")
    print(f"  Estoc actualitzat       : {stats['estoc_sumat']}")
    print(f"  Backup                  : {backup_ref}\n")


# =============================================================================
#  ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run()