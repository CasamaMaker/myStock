# myStock — Revisió Completa del Projecte

> Revisió tècnica realitzada com a Senior Software Engineer.  
> Data: Març 2026 · Fitxers analitzats: 12

---

## 1. Anàlisi del Codi

### 1.1 Arquitectura General

El projecte és una aplicació d'escriptori PySide6 per gestionar l'estoc de components electrònics. Consta de tres finestres principals:

| Mòdul | Responsabilitat |
|---|---|
| `myStock.py` | Finestra principal: taula filtrable de components, connexió a Google Sheets |
| `nowStock.py` | Importació d'albarans LCSC al Google Sheet (~1.360 línies) |
| `component_lookup.py` | Consulta de components a Mouser, Farnell i LCSC via API |
| `configuration.py` | Configuració centralitzada de columnes, filtres i credencials |
| `request_*.py` | Wrappers d'API per Farnell, LCSC i Mouser |
| `ui_*.py` | Fitxers de UI generats per Qt Designer |

L'arquitectura és raonable per a un projecte personal/petit equip, però presenta problemes de separació de responsabilitats, seguretat i mantenibilitat que s'exposen a continuació.

---

### 1.2 Problemes Identificats per Mòdul

#### `configuration.py`
- **Rutes hardcoded a Windows** (`C:\Users\ecasamayor\...`) no portables.
- **Tres configuracions completes comentades** (personal, grupeina, personal-test) dins el mateix fitxer. Canviar de perfil obliga a comentar/descomentar blocs enormes de codi manualment.
- **`locals().get("FILTRE1")`** dins un `class body`: comportament no garantit entre versions de Python i molt fràgil.
- Reasignació redundant: `ID = ID`, `STOCK = STOCK` (no fa res útil).
- Typos en constants públiques: `COMPONENT_LOOPUP_BUTTON_VISIBILITY` (hauria de ser LOOKUP), `FILTRER_AVAILABILITY` (hauria de ser FILTER).

#### `request_general.py`
- **Codi executable al nivell de mòdul**: el bucle `for part in part_numbers: get_mouser_data(part)` s'executa cada vegada que s'importa el mòdul, fent centenars de crides API reals amb `time.sleep(2)` entremig. Qualsevol `import request_general` des d'un altre mòdul bloquejarà l'aplicació durant minuts.
- La funció `detect_supplier` és una còpia exacta de la que existeix a `component_lookup.py`.
- `parse_barcode` és una versió anterior/simplificada de la mateixa funció a `component_lookup.py`.

#### `request_farnell.py` / `request_mouser.py`
- **API keys hardcoded al codi font** (`API_KEY_FARNELL = "j8ez8wawuv2ka9r2bamn499r"`, `API_KEY_MOUSER = "34e727c3-..."`). Exposades si el repositori és públic.
- Missatge de debug `print("✅ Component trobat!\n")` que s'executa sempre en producció.

#### `myStock.py`
- **`_fetch_google_sheet` bloqueja el thread de la UI**: la càrrega inicial i el refresc es fan al thread principal. Amb una connexió lenta, la finestra es queda congelada.
- `gspread` s'importa dues vegades: a nivell de mòdul (línia 22) i dins `_fetch_google_sheet` (línia 319).
- `print(row_index)` de debug deixat al mètode `_open_google_sheet`.
- `import traceback` dins un bloc `except` (import tardà, hauria d'anar a dalt).
- La funció `resource_path` és una còpia idèntica de la que hi ha a `component_lookup.py`.
- `_open_addstock` té un docstring que diu "albarans LCSC", copiat i enganxat per error.

#### `component_lookup.py`
- `print(avail)` de debug dins `is_out_of_stock`, s'executa a cada cerca.
- `self._nam = QNetworkAccessManager()` es recrea en cada cerca d'imatge sense destruir l'anterior, creant una fuita de memòria potencial en usos intensius.
- El `StockChecker` duplica part de la lògica de lectura de Google Sheets present a `myStock.py`.

#### `nowStock.py`
- El fitxer té 1.360 línies. Conté la UI, la lògica de negoci, els workers de threading i els colors/estils tots junts.

---

## 2. Aclariments / Dubtes

Abans de proposar canvis arquitectònics, seria útil confirmar:

1. **Multiusuari**: El projecte "grupeina" (comentat a `configuration.py`) és un desplegament per a un equip diferent? Está previst que el mateix codi serveixi múltiples perfils d'usuari/organització?
2. **`request_general.py`**: Aquest fitxer sembla ser un script de testing/proves que mai s'hauria d'importar com a mòdul. Es pot eliminar o s'utilitza com a entrada independent?
3. **Google Sheets vs. base de dades local**: Hi ha intenció de migrar l'estoc a una BD local (SQLite) o Google Sheets és el backend definitiu?
4. **Distribució**: L'app s'empaqueta amb PyInstaller (hi ha `sys._MEIPASS`)? En quines plataformes (Windows only, per les rutes, o també macOS/Linux)?

---

## 3. Propostes de Millora del Codi

### 3.1 Seguretat

| ID | Descripció | Motiu | Impacte | Dificultat |
|---|---|---|---|---|
| **IMP-001** | Moure les API keys i credencials a un fitxer `.env` o `secrets.toml`, llegit amb `python-dotenv` o `tomllib`. Afegir `.env` al `.gitignore`. | Les API keys estan exposades al codi font. Si el repo és públic o es comparteix, les claus queden compromeses. | **Alt** | Baixa |
| **IMP-002** | Moure les rutes de `BACKUP_FOLDER` i `LCSC_BOM_FOLDER` al fitxer `.env` o a un fitxer de configuració de l'usuari (`~/.mystock/config.toml`). | Rutes hardcoded amb nom d'usuari de Windows: no funciona en cap altra màquina. | **Alt** | Baixa |

### 3.2 Arquitectura i Estructura

| ID | Descripció | Motiu | Impacte | Dificultat |
|---|---|---|---|---|
| **IMP-003** | Implementar un sistema de **perfils de configuració**: un fitxer `profiles/personal.toml`, `profiles/grupeina.toml`, etc., i una variable d'entorn `MYSTOCK_PROFILE` o argument de línia de comandes per seleccionar-lo. Eliminar les configuracions comentades de `configuration.py`. | Tres blocs de configuració comentats al mateix fitxer fan el codi il·legible i propens a errors en canviar de perfil. | **Alt** | Mitja |
| **IMP-004** | Eliminar el codi executable al nivell de mòdul de `request_general.py` (el bucle `for part in part_numbers`), o convertir el fitxer en un script independent amb `if __name__ == "__main__"` correctament. | Importar el mòdul des de qualsevol lloc executa centenars de crides API amb sleeps. Pot trencar l'app silenciosament si s'importa per error. | **Alt** | Baixa |
| **IMP-005** | Extreure `resource_path()` a un mòdul `utils.py` compartit. | La funció és idèntica a `myStock.py` i `component_lookup.py`. Qualsevol canvi s'ha de fer dos cops. | Mig | Baixa |
| **IMP-006** | Extreure `detect_supplier()` i `parse_barcode()` a un mòdul `barcode_parser.py` o `supplier_utils.py`. | Duplicades entre `request_general.py` i `component_lookup.py`, amb versions lleugerament divergents. | Mig | Baixa |
| **IMP-007** | Dividir `nowStock.py` en almenys tres fitxers: `nowstock_ui.py` (layout), `nowstock_logic.py` (processament d'albarans, matching amb sheet) i `nowstock_workers.py` (QThread workers). | 1.360 línies en un sol fitxer és difícil de navegar, testar i mantenir. | Mig | Mitja |
| **IMP-008** | Extreure la lògica de lectura/escriptura de Google Sheets a una classe `GoogleSheetRepository` compartida entre `myStock.py`, `component_lookup.py` i `nowStock.py`. | Tres mòduls fan autenticació i lectura de Google Sheets de forma independent amb codi similar. | **Alt** | Mitja |

### 3.3 Rendiment i Estabilitat

| ID | Descripció | Motiu | Impacte | Dificultat |
|---|---|---|---|---|
| **IMP-009** | Moure `_fetch_google_sheet` i `_refresh_data` a un `QThread` o usar `QRunnable` + `QThreadPool`. Mostrar un spinner/progressbar durant la càrrega. | La càrrega de dades bloqueja el thread principal de la UI. Amb connexió lenta, la finestra es queda congelada. | **Alt** | Mitja |
| **IMP-010** | Instanciar `QNetworkAccessManager` una sola vegada al constructor de la finestra i reutilitzar-lo. | Crear un nou `_nam` en cada cerca d'imatge pot provocar fuites de memòria si l'usuari fa moltes cerques ràpides. | Baix | Baixa |
| **IMP-011** | Afegir **debounce** (ex: `QTimer` de 300ms) als filtres de text `filterG_lineEdit` i `FilterPN_lineEdit`. | Cada tecla premuda dispara `_update_table()` que refiltra totes les dades. En datasets grans, pot generar lag visible. | Mig | Baixa |

### 3.4 Neteja de Codi

| ID | Descripció | Motiu | Impacte | Dificultat |
|---|---|---|---|---|
| **IMP-012** | Eliminar tots els `print()` de debug: `print(avail)` a `is_out_of_stock`, `print(row_index)` a `_open_google_sheet`, `print("✅ Component trobat!")` a `request_farnell.py`, etc. Substituir per `logging.debug(...)`. | Els prints de debug contaminen la sortida en producció i dificulten el diagnòstic d'errors reals. | Mig | Baixa |
| **IMP-013** | Implementar un sistema de logging centralitzat (`import logging`) amb nivells DEBUG/INFO/WARNING/ERROR i opció d'escriure a fitxer rotatiu. | Sense logging, no hi ha traça quan l'app falla en un client. | Mig | Baixa |
| **IMP-014** | Corregir typos en constants públiques de `Config`: `LOOPUP` → `LOOKUP`, `FILTRER` → `FILTER`. | Typos en l'API pública de `Config` propaguen l'error a tot el codebase. | Baix | Baixa |
| **IMP-015** | Eliminar la reasignació redundant `ID = ID`, `STOCK = STOCK`, etc. a `configuration.py`, i l'import doble de `gspread` a `myStock.py`. | Codi mort que confon el lector. | Baix | Baixa |
| **IMP-016** | Reemplaçar el `locals().get("FILTRE1")` a `configuration.py` per un patró explícit amb `getattr(Config, "FILTRE1", None)` o definir els filtres com a diccionari. | `locals()` dins un `class body` és un patró poc clar, difícil de debugar i pot tenir comportaments inesperats. | Mig | Baixa |

### 3.5 Bones Pràctiques

| ID | Descripció | Motiu | Impacte | Dificultat |
|---|---|---|---|---|
| **IMP-017** | Afegir **type hints** complets a les funcions de `request_*.py` (retornen `Optional[dict]` però no ho declaren). | Millora la documentació implícita i permet que els IDEs detectin errors de tipus. | Baix | Baixa |
| **IMP-018** | Afegir un `requirements.txt` o `pyproject.toml` amb les dependències exactes (`PySide6`, `gspread`, `google-auth`, `requests`). | Sense fitxer de dependències, instal·lar l'app en una màquina nova és un procés de prova i error. | Mig | Baixa |

---

## 4. Noves Funcionalitats (Brainstorming)

| ID | Funcionalitat | Descripció | Impacte | Dificultat |
|---|---|---|---|---|
| **FEAT-001** | **Alerta d'estoc mínim** | Definir un estoc mínim per component (nova columna al sheet o fitxer local). La taula principal ressalta en vermell les files on `STOCK < mínim`. Opció d'exportar la llista de components a reposar. | Alt | Mitja |
| **FEAT-002** | **Historial de moviments** | Cada canvi d'estoc (importació d'albaran, modificació manual) registra una entrada a una pestanya "Historial" del Google Sheet: data, quantitat, motiu, usuari. | Alt | Mitja |
| **FEAT-003** | **Escaneig de codi de barres per webcam** | Integrar `pyzbar` + `OpenCV` per llegir codis de barres directament des de la càmera, sense necessitat de pistola lectora. | Alt | Alta |
| **FEAT-004** | **Exportació de BOM** | Des de la vista filtrada, exportar la llista actual a CSV/XLSX amb format compatible amb KiCad o Altium. | Alt | Baixa |
| **FEAT-005** | **Cerca multi-proveïdor paral·lela** | Al `component_lookup`, fer les tres crides (Mouser, LCSC, Farnell) en paral·lel (`threading` o `asyncio`) i mostrar el primer resultat que arribi. Redueix el temps d'espera. | Mig | Mitja |
| **FEAT-006** | **Mode offline / caché local** | Guardar un `cache.json` amb les cerques de components recents. Si l'app no té connexió, servir el resultat de la caché amb indicador visual. | Mig | Mitja |
| **FEAT-007** | **Càlcul de valor d'estoc** | Afegir columna de preu unitari al sheet. La vista principal mostra el valor total de l'estoc (estoc × preu) per component i un total general. | Mig | Mitja |
| **FEAT-008** | **Drag & Drop de fitxers BOM** | Permetre arrossegar un fitxer CSV/XLSX de BOM a la finestra principal per veure quins components tenim i quins falten. | Alt | Alta |

---

## 5. Benchmark / Competència

### 5.1 Aplicacions Similars

| Aplicació | Tipus | Plataforma | Funcionalitats Destacades |
|---|---|---|---|
| **Partkeepr** | Open source, web | Self-hosted | Gestió de components, estocs mínims, projectes, proveïdors, emmagatzematge jeràrquic, integració Octopart |
| **Inventree** | Open source, web | Self-hosted (Docker) | API REST completa, BOM per projecte, ordres de compra, barcode/QR natiu, plugins, app mòbil |
| **KiCost** | Script Python | Multiplataforma | Consulta de preus multi-proveïdor (Mouser, Farnell, LCSC, DigiKey) des d'una BOM de KiCad |
| **Octopart** | SaaS web | Cloud | Agregador de preus i disponibilitat de components, API pública |
| **Bomist** | SaaS web | Cloud | Gestió de BOM, seguiment de preus, alertes de disponibilitat |
| **LCSC BOM Tool** | Web integrada | Cloud (LCSC) | Importació de BOM, disponibilitat i preus a LCSC |

### 5.2 Funcionalitats Clau dels Competidors

- **Inventree**: el seu model de dades separa clarament "Part" (component abstracte), "Stock Location" (emmagatzematge físic jeràrquic) i "Stock Item" (unitat física concreta). Permet múltiples emmagatzematges del mateix component.
- **Partkeepr**: gestió de categories en arbre, emmagatzematge jeràrquic (armari → calaix → posició), i càlcul automàtic del valor d'inventari.
- **KiCost**: cerca de preus en paral·lel a múltiples proveïdors i comparació de preus per quantitat en una mateixa vista.
- **Inventree + Bomist**: alertes d'estoc mínim configurables per component, amb notificació per email.

---

## 6. Propostes Basades en Competència

| ID | Funcionalitat | Inspiració | Descripció | Impacte | Dificultat |
|---|---|---|---|---|---|
| **COMP-001** | **Emmagatzematge jeràrquic** | Partkeepr, Inventree | Estructura l'emmagatzematge com a arbre: Lloc → Prestatgeria → Calaix → Posició. El camp `STORAGE` actual és text lliure; amb jerarquia es pot filtrar per contenidor i veure tot el contingut d'un calaix. | Alt | Alta |
| **COMP-002** | **Vista de comparació de preus multi-proveïdor** | KiCost, Octopart | Al `component_lookup`, mostrar simultàniament els preus de Mouser, LCSC i Farnell per al mateix component (cerca per MPN). L'usuari veu d'un cop d'ull on és més barat. | Alt | Mitja |
| **COMP-003** | **Gestió de projectes / BOM** | Inventree, Bomist | Crear "projectes" que associen una BOM a l'estoc. L'app mostra quants projectes es poden muntar amb l'estoc actual i quins components falten. | Alt | Alta |
| **COMP-004** | **Ordres de compra** | Inventree | Generar una ordre de compra (CSV o directe a la web del proveïdor) a partir dels components amb estoc per sota del mínim o els que falten per un projecte. | Alt | Alta |
| **COMP-005** | **API REST local** | Inventree | Exposar una API REST senzilla (FastAPI) perquè eines externes (scripts de KiCad, Jupyter, etc.) puguin consultar i actualitzar l'estoc sense obrir la GUI. | Mig | Alta |
| **COMP-006** | **Alertes per email/Telegram** | Inventree, Bomist | Enviar una notificació quan un component baixa de l'estoc mínim o quan s'esgota completament. Implementació senzilla amb `smtplib` o bot de Telegram. | Mig | Mitja |

---

## 7. Resum Prioritzat d'Accions

### 🔴 Prioritat Alta (fer primer)

1. **IMP-001 + IMP-002** — Treure les API keys i rutes hardcoded del codi. Risc de seguretat i no-portabilitat immediats.
2. **IMP-004** — Eliminar el codi executable al mòdul `request_general.py`. Pot trencar l'app silenciosament.
3. **IMP-009** — Threading per a la càrrega de Google Sheets. L'experiència d'usuari queda bloquejada sense això.

### 🟡 Prioritat Mitja (millores de qualitat)

4. **IMP-003** — Sistema de perfils de configuració. Allibera el codi de les tres configs comentades.
5. **IMP-008** — Classe `GoogleSheetRepository` compartida. Elimina duplicació de lògica d'autenticació.
6. **IMP-012 + IMP-013** — Substituir prints per `logging`. Necessari per diagnosticar errors en producció.
7. **IMP-007** — Dividir `nowStock.py`.

### 🟢 Prioritat Baixa (millores menors)

8. **IMP-005 + IMP-006** — Mòduls utils compartits.
9. **IMP-014 + IMP-015** — Neteja de typos i codi mort.
10. **IMP-018** — Afegir `requirements.txt`.

---

*Document generat per revisió de codebase · myStock project*
