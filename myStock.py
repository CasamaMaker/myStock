from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QHBoxLayout, QVBoxLayout, QSizePolicy, QHeaderView, 
    QTableWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from ui_main import Ui_MainWindow
import sys
import csv
import requests
import webbrowser
from typing import List, Optional, Dict, Tuple, Set
from dataclasses import dataclass
from PySide6.QtGui import QIcon
import recursos_grafics_rc


import gspread
from google.oauth2.service_account import Credentials

@dataclass
class FilterConfig:
    """Configuració d'un filtre"""
    column_index: int
    label_widget_name: str
    line_edit_name: str
    list_widget_name: str
    button_name: str
    tag_key: str
    enabled: bool = True


class Config:
    """Configuració centralitzada de columnes i visualització"""
    # Índexs de columnes - PARÀMETRES OBLIGATORIS
    STOCK = 0                   # ES MOSTRE EN LABEL
    STORAGE = 1                 # ES MOSTRE EN LABEL
    WEB = 7                     # S'OBRE LA WEB
    REFERENCE = 3               # PN o ID unic, PER identificar cada FILA
    TEXT_FILTER = 4             # COLUMNA EN LA QUAL APLICAREM EL FILTRE DE TEXT


    # ALTRES  - PARÀMETRES OPCIONALS - NOMÉS SÓN PER UTILITZAR DINS DE LA FUNCIÓ CONFIG
    TYPE = 2
    DESCRIPTION = 5
    PACKAGE = 6


    # DEFINIR ELS FILTRES
    FILTRE1 = TYPE
    FILTRE2 = PACKAGE
    FILTRE3 = STORAGE
    FILTRE4 = REFERENCE
    FILTRE5 = TEXT_FILTER

    

    
    # Columnes a mostrar a la taula i les seves amplades
    COLUMNS_TO_SHOW = [REFERENCE, TEXT_FILTER, PACKAGE, DESCRIPTION]
    COLUMNS_WIDTH = [110, 150, 70, 300]
    
    # Configuració de filtres (pots activar/desactivar els que vulguis)
    FILTERS_CONFIG = [
        FilterConfig(
            column_index=TYPE,
            label_widget_name="filter1_label",
            line_edit_name="filter1_lineEdit",
            list_widget_name="filter1_listWidget",
            button_name="filter1_pushButton",
            tag_key="filter1",
            # enabled=True  # Canvia a False per desactivar
            enabled='FILTRE1' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=PACKAGE,
            label_widget_name="filter2_label",
            line_edit_name="filter2_lineEdit",
            list_widget_name="filter2_listWidget",
            button_name="filter2_pushButton",
            tag_key="filter2",
            # enabled=True  # Canvia a False per desactivar
            enabled='FILTRE2' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=REFERENCE,
            label_widget_name="filter3_label",
            line_edit_name="filter3_lineEdit",
            list_widget_name="filter3_listWidget",
            button_name="filter3_pushButton",
            tag_key="filter3",
            # enabled=True  # Canvia a False per desactivar
            enabled='FILTRE3' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=DESCRIPTION,
            label_widget_name="filter4_label",
            line_edit_name="filter4_lineEdit",
            list_widget_name="filter4_listWidget",
            button_name="filter4_pushButton",
            tag_key="filter4",
            # enabled=False  # Canvia a False per desactivar
            enabled='FILTRE4' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=STOCK,
            label_widget_name="filter5_label",
            line_edit_name="filter5_lineEdit",
            list_widget_name="filter5_listWidget",
            button_name="filter5_pushButton",
            tag_key="filter5",
            # enabled=False  # Canvia a False per desactivar
            enabled='FILTRE5' in locals()  # False perquè està comentat
        ),
    ]

    # self.ui.listWidget_4.setVisible(False)
    
    
    FILTRER_AVAILABILITY = True     # amaga o desavilita els paràmetre de filtre NO disponibles --> True: amaga; False: desavilita

    # Google Sheet ID
    GOOGLE_SHEET_ID = "1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA"                # personal
    # GOOGLE_SHEET_ID = "1cbyUW76l9EDPyHaKr98ARRroAWqfM3ctaYlRFw9enBg"              ## grupeina 
    # GOOGLE_SHEET_ID = "13rzlU99m8AtWtMIPll6iB_1iJge1rUPmn_03aEMuvQk"              # Còpia multiplicada stock
    GOOGLE_CREDENTIALS_JSON = "credentials/mystock-482208-a553ed840217.json"        # personal
    # GOOGLE_CREDENTIALS_JSON = "credentials/model-folio-482716-e4-e9eb4cc77d58.json" ## grupeina 
    
    # Timeout per peticions HTTP (segons)
    REQUEST_TIMEOUT = 10


class TagWidget(QWidget):
    """Widget personalitzat per mostrar tags amb botó de tancament"""
    closed = Signal(str, str)

    def __init__(self, key: str, value: str):
        super().__init__()
        self.key = key
        self.value = value
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfície del tag"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 0, 1, 0)
        layout.setSpacing(0)

        # Etiqueta amb el valor
        self.label = QLabel(f"{self.value}")
        self.label.setStyleSheet("padding: 2px;")

        # Widget contenidor
        tag_widget = QWidget(self)
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(0)

        tag_layout.addWidget(self.label)

        # Botó de tancament
        self.button = QPushButton("✖", tag_widget)
        self.button.setFixedSize(16, 16)
        self.button.clicked.connect(self._on_close)
        tag_layout.addWidget(self.button)

        layout.addWidget(tag_widget)

        # Configuració de mida
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.adjustSize()

        # Estils
        self.setStyleSheet("""
            QWidget {
                background-color: #444;
                color: white;
                border-radius: 10px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-weight: light;
            }
            QPushButton:hover {
                color: black;
            }
        """)

    def _on_close(self):
        """Gestiona l'event de tancament del tag"""
        self.closed.emit(self.key, self.value)
        self.setParent(None)


class FilterManager:
    """Gestiona els filtres de les llistes"""
    
    def __init__(self):
        self.selected_items: List[str] = []
        self.available_items: List[str] = []
    
    def toggle_item(self, item: str):
        """Afegeix o elimina un item de la selecció"""
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.append(item)
    
    def clear_selection(self):
        """Neteja la selecció"""
        self.selected_items.clear()
    
    def filter_by_text(self, text: str) -> List[str]:
        """Filtra els items disponibles per text"""
        if not text:
            return self.available_items
        return [item for item in self.available_items 
                if text.lower() in item.lower()]


class MainWindow(QMainWindow):
    """Finestra principal de l'aplicació"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Diccionari de gestors de filtres per cada filtre configurat
        self.filters: Dict[str, FilterManager] = {}
        
        # Filtres de text
        self.text_filter_general = ""
        self.text_filter_part_number = ""
        
        # Widgets de tags
        self.tag_widgets: List[TagWidget] = []
        
        # Dades del Google Sheet
        self.data_google_sheet: List[List[str]] = []
        
        self._setup_filters()
        self._setup_ui()
        self._load_data()

    def _setup_filters(self):
        """Configura els filtres segons la configuració"""
        for filter_config in Config.FILTERS_CONFIG:
            if filter_config.enabled:
                # Crear el gestor de filtre
                self.filters[filter_config.tag_key] = FilterManager()
            else:
                # Amagar els widgets del filtre desactivat
                self._hide_filter_widgets(filter_config)

    def _hide_filter_widgets(self, filter_config: FilterConfig):
        """Amaga els widgets d'un filtre desactivat"""
        widgets_to_hide = [
            filter_config.label_widget_name,
            filter_config.line_edit_name,
            filter_config.list_widget_name,
            filter_config.button_name
        ]
        
        for widget_name in widgets_to_hide:
            widget = getattr(self.ui, widget_name, None)
            if widget:
                widget.setVisible(False)

    def _setup_ui(self):
        """Configura la interfície d'usuari"""
        # Configurar botons i senyals per cada filtre activat
        for filter_config in Config.FILTERS_CONFIG:
            if not filter_config.enabled:
                continue
            
            # Obtenir widgets
            button = getattr(self.ui, filter_config.button_name)
            line_edit = getattr(self.ui, filter_config.line_edit_name)
            list_widget = getattr(self.ui, filter_config.list_widget_name)
            
            # Configurar botó reset
            button.setFlat(True)
            button.clicked.connect(
                lambda checked=False, fc=filter_config: self._reset_filter(fc)
            )
            
            # Configurar mode de selecció múltiple
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            
            # Connectar senyals de text
            line_edit.textChanged.connect(
                lambda text, fc=filter_config: self._filter_list(fc, text)
            )
            
            # Connectar senyals de selecció
            list_widget.itemClicked.connect(
                lambda item, fc=filter_config: self._on_list_item_clicked(fc)
            )
        
        # Icona principal
        # self.setWindowIcon(QIcon("img\inventory.ico"))
        self.setWindowIcon(QIcon(":/logos/inventory_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg")
)

        # Botons d'acció
        self.ui.pushButton_4.clicked.connect(self._open_google_sheet)
        self.ui.pushButton_5.clicked.connect(self._refresh_data)
        self.ui.datasheetButton.clicked.connect(self._open_datasheet)
        
        # Botó per esborrar tots els filtres
        self.ui.clear_all_pushButton.clicked.connect(self._clear_all_filters)
        
        # Configurar tooltips
        self._setup_tooltips()
        
        # Connectar senyals de filtres de text
        self.ui.filterG_lineEdit.textChanged.connect(self._filter_general_text)
        self.ui.FilterPN_lineEdit.textChanged.connect(self._filter_part_number)
        
        # Connectar senyal de selecció de taula
        self.ui.tableWidget.itemSelectionChanged.connect(self._update_stock_info)
        
        # Configurar layout de tags
        self.ui.horizontalLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.ui.listWidget_4.setVisible(False)

    def _setup_tooltips(self):
        """Configura els tooltips"""
        self.ui.datasheetButton.setToolTip("Obre la web/datasheet")
        self.ui.pushButton_4.setToolTip("Obre l'arxiu")
        self.ui.pushButton_5.setToolTip("Actualitza les dades")
        self.ui.label_5.setToolTip("Components filtrats")
        self.ui.label_2.setToolTip("Stock del component")
        self.ui.stock_text.setToolTip("Stock del component")
        self.ui.stock_text.setEnabled(False)

    def _load_data(self):
        """Carrega les dades inicials"""
        self.data_google_sheet = self._fetch_google_sheet()
        
        if not self.data_google_sheet:
            self._show_status_message("Error carregant dades", 3000)
            return
        
        self._populate_all_filter_lists()
        self._update_table()
        self._show_status_message("Iniciat correctament", 2000)

    # def _fetch_google_sheet(self) -> List[List[str]]:
    #     """Carrega les dades des del Google Sheet"""
    #     try:
    #         csv_url = (
    #             f"https://docs.google.com/spreadsheets/d/"
    #             f"{Config.GOOGLE_SHEET_ID}/export?format=csv"
    #         )
            
    #         response = requests.get(csv_url, timeout=Config.REQUEST_TIMEOUT)
    #         response.raise_for_status()
            
    #         csv_content = response.content.decode('utf-8')
    #         csv_reader = csv.reader(csv_content.splitlines())
    #         data = list(csv_reader)
            
    #         if not data:
    #             print("No s'han trobat dades al Google Sheet")
    #             return []
            
    #         return data
            
    #     except requests.exceptions.RequestException as e:
    #         error_msg = f"Error al accedir a Google Sheet: {e}"
    #         print(error_msg)
    #         self._show_status_message(error_msg, 3000)
    #         return []

    def _fetch_google_sheet(self, worksheet_name: str = None) -> List[List[str]]:
        """
        Carrega les dades des del Google Sheet via Google Sheets API.
        
        Args:
            worksheet_name: Nom de la pestanya a carregar. Si és None, carrega la primera.
        
        Returns:
            Llista de llistes amb les dades del full de càlcul, o llista buida si hi ha error.
        """
        import gspread
        from google.oauth2.service_account import Credentials
        import json
        import os
        
        service_email = "desconegut"
        
        try:
            # Validació de configuració
            if not Config.GOOGLE_CREDENTIALS_JSON:
                raise ValueError("No s'ha configurat GOOGLE_CREDENTIALS_JSON")
            if not Config.GOOGLE_SHEET_ID:
                raise ValueError("No s'ha configurat GOOGLE_SHEET_ID")
            
            # Verificar que el fitxer existeix i es pot llegir
            creds_path = Config.GOOGLE_CREDENTIALS_JSON
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"No existeix el fitxer: {creds_path}")
            
            if not os.access(creds_path, os.R_OK):
                raise PermissionError(f"No es pot llegir el fitxer local: {creds_path}")
            
            print(f"✓ Fitxer de credencials accessible: {creds_path}")
            
            # Llegir el service account email
            try:
                with open(creds_path, 'r', encoding='utf-8') as f:
                    creds_data = json.load(f)
                    service_email = creds_data.get('client_email', 'No trobat')
                    print(f"Service Account: {service_email}")
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise ValueError(f"El fitxer JSON no és vàlid: {e}")
            
            # Àmbits amb permisos complets
            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            
            # Autenticació
            print(f"Carregant credencials...")
            creds = Credentials.from_service_account_file(
                creds_path,
                scopes=SCOPES
            )
            print("✓ Credencials carregades correctament")
            
            client = gspread.authorize(creds)
            print("✓ Client autoritzat")
            
        except (FileNotFoundError, ValueError) as e:
            print(f"Error de configuració: {e}")
            self._show_status_message(str(e), 5000)
            return []
        
        except PermissionError as e:
            print(f"Error de permisos del fitxer local: {e}")
            print("\nSOLUCIONS:")
            print(f'1. icacls "{creds_path}" /grant:r "%USERNAME%:(F)"')
            print("2. Mou el fitxer JSON a una ubicació sense restriccions")
            self._show_status_message("Error de permisos del fitxer JSON local", 5000)
            return []
        
        except Exception as e:
            print(f"Error en autenticació: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self._show_status_message("Error en autenticació", 5000)
            return []
        
        # Ara intentem accedir al Google Sheet (fora del try anterior)
        try:
            print(f"Accedint al Google Sheet ID: {Config.GOOGLE_SHEET_ID}")
            sheet = client.open_by_key(Config.GOOGLE_SHEET_ID)
            print(f"✓ Connexió establerta amb '{sheet.title}'")
            
            # Selecció de la pestanya
            if worksheet_name:
                worksheet = sheet.worksheet(worksheet_name)
            else:
                worksheet = sheet.sheet1
            
            print(f"✓ Llegint pestanya: {worksheet.title}")
            
            # Obtenció de dades
            data = worksheet.get_all_values()
            
            if not data:
                msg = "El Google Sheet està buit"
                print(f"Avís: {msg}")
                self._show_status_message(msg, 3000)
                return []
            
            print(f"✓ S'han carregat {len(data)} files del Google Sheet")
            return data
        
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"Error: Google Sheet no trobat")
            print(f"Sheet ID: {Config.GOOGLE_SHEET_ID}")
            print(f"Service Account: {service_email}")
            print(f"\nVerifica:")
            print(f"1. Que el Google Sheet existeix: https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEET_ID}")
            print(f"2. Que està compartit amb: {service_email}")
            print(f"3. Que el service account té permisos d'Editor (no només Lector)")
            print(f"\nDetalls de l'error: {e}")
            self._show_status_message("Google Sheet no trobat o sense accés", 5000)
            return []
        
        except gspread.exceptions.WorksheetNotFound:
            error_msg = f"Pestanya '{worksheet_name}' no trobada"
            print(f"Error: {error_msg}")
            self._show_status_message(error_msg, 5000)
            return []
        
        except gspread.exceptions.APIError as e:
            error_code = getattr(e.response, 'status_code', 'desconegut')
            print(f"Error: API Error (codi {error_code})")
            print(f"Missatge: {e}")
            
            if error_code == 403:
                print(f"\n=== PROBLEMA DE PERMISOS ===")
                print(f"El service account NO TÉ ACCÉS al Google Sheet")
                print(f"\nPas a pas per solucionar-ho:")
                print(f"1. Obre: https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEET_ID}")
                print(f"2. Clica el botó 'Compartir' (dalt a la dreta)")
                print(f"3. Afegeix aquest email: {service_email}")
                print(f"4. Dona-li permisos d'EDITOR")
                print(f"5. Clica 'Enviar' o 'Compartir'")
            
            self._show_status_message(f"Error API Google Sheets ({error_code})", 5000)
            return []
        
        except Exception as e:
            print(f"Error inesperat en accedir al Google Sheet: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self._show_status_message("Error inesperat", 5000)
            return []

    def _populate_all_filter_lists(self):
        """Omple totes les llistes de filtres amb valors únics"""
        if not self.data_google_sheet or len(self.data_google_sheet) < 2:
            return
        
        for filter_config in Config.FILTERS_CONFIG:
            if filter_config.enabled:
                self._populate_single_filter(filter_config)

    def _populate_single_filter(self, filter_config: FilterConfig):
        """Omple un filtre individual"""
        filter_manager = self.filters[filter_config.tag_key]
        list_widget = getattr(self.ui, filter_config.list_widget_name)
        label_widget = getattr(self.ui, filter_config.label_widget_name)
        
        # Obtenir valors únics
        unique_items = {row[filter_config.column_index] 
                       for row in self.data_google_sheet[1:]}
        filter_manager.available_items = sorted(list(unique_items))
        
        # Omplir llista
        list_widget.clear()
        list_widget.addItems(filter_manager.available_items)
        
        # Actualitzar etiqueta
        header_text = self.data_google_sheet[0][filter_config.column_index]
        label_widget.setText(f"{header_text} [{len(filter_manager.available_items)}]")

    def _get_available_values_for_filter(self, filter_config: FilterConfig) -> Set[str]:
        """Obté els valors disponibles per un filtre segons les dades filtrades"""
        # Aplicar tots els filtres EXCEPTE el filtre actual
        filtered = self.data_google_sheet[1:]
        
        for other_config in Config.FILTERS_CONFIG:
            if not other_config.enabled:
                continue
            
            # Saltar el filtre actual
            if other_config.tag_key == filter_config.tag_key:
                continue
            
            # Aplicar els altres filtres de llista
            other_manager = self.filters[other_config.tag_key]
            if other_manager.selected_items:
                filtered = [row for row in filtered 
                           if row[other_config.column_index] in other_manager.selected_items]
        
        # Aplicar filtres de text
        if self.text_filter_general:
            filtered = [row for row in filtered 
                       if any(self.text_filter_general.lower() in str(cell).lower() 
                             for cell in row)]
        
        if self.text_filter_part_number:
            filtered = [row for row in filtered 
                       if self.text_filter_part_number.lower() 
                       in str(row[Config.TEXT_FILTER]).lower()]
        
        # Retornar els valors únics disponibles per aquest filtre
        return {row[filter_config.column_index] for row in filtered}

    def _update_filter_availability(self):
        """Actualitza la disponibilitat visual de tots els filtres"""
        for filter_config in Config.FILTERS_CONFIG:
            if not filter_config.enabled:
                continue
            
            # Obtenir valors disponibles segons els filtres actius
            available_values = self._get_available_values_for_filter(filter_config)
            
            # Actualitzar l'aparença del list_widget
            list_widget = getattr(self.ui, filter_config.list_widget_name)
            
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_text = item.text()
                
                if item_text in available_values:
                    

                    if Config.FILTRER_AVAILABILITY:
                        # Item disponible - visible
                        item.setHidden(False)
                    else:
                        # Item disponible - color normal
                        item.setForeground(QColor(0, 0, 0))  # Negre per temes clars
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                else:


                    if Config.FILTRER_AVAILABILITY:
                        # Item no disponible - invisible
                        item.setHidden(True)
                    else:
                        # Item no disponible - gris clar i deshabilitat
                        item.setForeground(QColor(180, 180, 180))  # Gris clar
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)

    def _filter_list(self, filter_config: FilterConfig, text: str):
        """Filtra una llista per text"""
        filter_manager = self.filters[filter_config.tag_key]
        list_widget = getattr(self.ui, filter_config.list_widget_name)
        
        filtered_items = filter_manager.filter_by_text(text)
        list_widget.clear()
        list_widget.addItems(filtered_items)
        
        # Mantenir items seleccionats
        for idx in range(list_widget.count()):
            item = list_widget.item(idx)
            if item.text() in filter_manager.selected_items:
                item.setSelected(True)
        
        # Actualitzar disponibilitat visual
        self._update_filter_availability()

    def _on_list_item_clicked(self, filter_config: FilterConfig):
        """Gestiona el clic en un item de la llista"""
        filter_manager = self.filters[filter_config.tag_key]
        list_widget = getattr(self.ui, filter_config.list_widget_name)
        line_edit = getattr(self.ui, filter_config.line_edit_name)
        
        current_item = list_widget.currentItem()
        if not current_item:
            return
        
        filter_manager.toggle_item(current_item.text())
        line_edit.setText("")
        
        self._filter_list(filter_config, "")
        self._update_table()

    def _reset_filter(self, filter_config: FilterConfig):
        """Reseteja un filtre"""
        filter_manager = self.filters[filter_config.tag_key]
        list_widget = getattr(self.ui, filter_config.list_widget_name)
        
        filter_manager.clear_selection()
        self._filter_list(filter_config, "")
        self._update_table()

    def _filter_general_text(self):
        """Filtra per text general"""
        new_text = self.ui.filterG_lineEdit.text()
        
        # Només actualitzar si el text ha canviat realment
        if new_text != self.text_filter_general:
            self.text_filter_general = new_text
            self._update_table()

    def _filter_part_number(self):
        """Filtra per part number"""
        new_text = self.ui.FilterPN_lineEdit.text()
        
        # Només actualitzar si el text ha canviat realment
        if new_text != self.text_filter_part_number:
            self.text_filter_part_number = new_text
            self._update_table()

    def _clear_all_filters(self):
        """Esborra tots els filtres aplicats"""
        # Bloquejar senyals per evitar múltiples actualitzacions
        self.ui.filterG_lineEdit.blockSignals(True)
        self.ui.FilterPN_lineEdit.blockSignals(True)
        
        # Esborrar tots els filtres de llista
        for filter_config in Config.FILTERS_CONFIG:
            if filter_config.enabled:
                filter_manager = self.filters[filter_config.tag_key]
                filter_manager.clear_selection()
                
                list_widget = getattr(self.ui, filter_config.list_widget_name)
                line_edit = getattr(self.ui, filter_config.line_edit_name)
                
                # Bloquejar senyals temporalment
                line_edit.blockSignals(True)
                
                # Deseleccionar tots els items
                for i in range(list_widget.count()):
                    list_widget.item(i).setSelected(False)
                
                # Netejar el camp de text
                line_edit.clear()
                line_edit.blockSignals(False)
        
        # Esborrar filtres de text
        self.text_filter_general = ""
        self.ui.filterG_lineEdit.clear()
        
        self.text_filter_part_number = ""
        self.ui.FilterPN_lineEdit.clear()
        
        # Desbloquejar senyals
        self.ui.filterG_lineEdit.blockSignals(False)
        self.ui.FilterPN_lineEdit.blockSignals(False)
        
        # Actualitzar la taula UNA SOLA VEGADA
        self._update_table()
        
        self._show_status_message("Tots els filtres esborrats", 2000)

    def _update_table(self):
        """Actualitza la taula amb les dades filtrades"""
        filtered_data = self._apply_filters()
        
        if not filtered_data:
            self._clear_table()
            self._show_status_message("No hi ha valors corresponents al filtre", 2000)
            # Actualitzar disponibilitat dels filtres encara que no hi hagi resultats
            self._update_filter_availability()
            return
        
        self._populate_table(filtered_data)
        self._update_filter_tags()
        
        # NOVA FUNCIONALITAT: Actualitzar la disponibilitat dels altres filtres
        self._update_filter_availability()

    def _apply_filters(self) -> List[List[str]]:
        """Aplica tots els filtres a les dades"""
        filtered = self.data_google_sheet[1:]  # Saltar capçalera
        
        # Aplicar tots els filtres de llista configurats
        for filter_config in Config.FILTERS_CONFIG:
            if not filter_config.enabled:
                continue
            
            filter_manager = self.filters[filter_config.tag_key]
            if filter_manager.selected_items:
                filtered = [row for row in filtered 
                           if row[filter_config.column_index] in filter_manager.selected_items]
        
        # Filtrar per text general
        if self.text_filter_general:
            filtered = [row for row in filtered 
                       if any(self.text_filter_general.lower() in str(cell).lower() 
                             for cell in row)]
        
        # Filtrar per part number
        if self.text_filter_part_number:
            filtered = [row for row in filtered 
                       if self.text_filter_part_number.lower() 
                       in str(row[Config.TEXT_FILTER]).lower()]
        
        return filtered

    def _populate_table(self, data: List[List[str]]):
        """Omple la taula amb les dades"""
        # Extreure només les columnes a mostrar
        display_data = [[row[i] for i in Config.COLUMNS_TO_SHOW] for row in data]
        headers = [self.data_google_sheet[0][i] for i in Config.COLUMNS_TO_SHOW]
        
        # Configurar taula
        self.ui.tableWidget.setRowCount(len(display_data))
        self.ui.tableWidget.setColumnCount(len(Config.COLUMNS_TO_SHOW))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        
        # Omplir dades
        for row_idx, row_data in enumerate(display_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.ui.tableWidget.setItem(row_idx, col_idx, item)
        
        # Configurar amplades
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        for idx, width in enumerate(Config.COLUMNS_WIDTH):
            self.ui.tableWidget.setColumnWidth(idx, width)
        
        # Actualitzar comptador
        self.ui.label_5.setText(str(len(display_data)))

    def _clear_table(self):
        """Neteja la taula"""
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(0)
        self.ui.label_5.setText("0")

    def _update_filter_tags(self):
        """Actualitza els tags de filtres visibles"""
        self._clear_all_tags()
        
        all_filters = []
        
        # Crear tags per cada filtre de llista actiu
        for filter_config in Config.FILTERS_CONFIG:
            if not filter_config.enabled:
                continue
            
            filter_manager = self.filters[filter_config.tag_key]
            for item in filter_manager.selected_items:
                self._create_tag(filter_config.tag_key, item)
                all_filters.append(item)
        
        # Crear tags per filtres de text
        if self.text_filter_general:
            self._create_tag("text", self.text_filter_general)
            all_filters.append(self.text_filter_general)
        
        if self.text_filter_part_number:
            self._create_tag("partNumber", self.text_filter_part_number)
            all_filters.append(self.text_filter_part_number)
        
        # Actualitzar llista de filtres
        self.ui.listWidget_4.clear()
        self.ui.listWidget_4.addItems(all_filters)

    def _create_tag(self, key: str, value: str):
        """Crea un nou tag"""
        tag = TagWidget(key, value)
        tag.closed.connect(self._on_tag_closed)
        self.ui.horizontalLayout.addWidget(tag)
        self.tag_widgets.append(tag)

    def _clear_all_tags(self):
        """Elimina tots els tags"""
        for tag in self.tag_widgets:
            tag.close()
        self.tag_widgets.clear()

    def _on_tag_closed(self, key: str, value: str):
        """Gestiona el tancament d'un tag"""
        # Flag per indicar si s'ha fet algun canvi
        changed = False
        
        # Gestionar filtres de text
        if key == "text":
            if self.text_filter_general:  # Només canviar si hi ha text
                self.text_filter_general = ""
                self.ui.filterG_lineEdit.blockSignals(True)  # Bloquejar senyal temporalment
                self.ui.filterG_lineEdit.clear()
                self.ui.filterG_lineEdit.blockSignals(False)
                changed = True
        elif key == "partNumber":
            if self.text_filter_part_number:  # Només canviar si hi ha text
                self.text_filter_part_number = ""
                self.ui.FilterPN_lineEdit.blockSignals(True)  # Bloquejar senyal temporalment
                self.ui.FilterPN_lineEdit.clear()
                self.ui.FilterPN_lineEdit.blockSignals(False)
                changed = True
        else:
            # Gestionar filtres de llista
            for filter_config in Config.FILTERS_CONFIG:
                if filter_config.enabled and filter_config.tag_key == key:
                    filter_manager = self.filters[filter_config.tag_key]
                    if value in filter_manager.selected_items:
                        filter_manager.selected_items.remove(value)
                        changed = True
                    
                    list_widget = getattr(self.ui, filter_config.list_widget_name)
                    self._deselect_item(list_widget, value)
                    break
        
        # Només actualitzar si realment s'ha fet algun canvi
        if changed:
            self._update_table()

    def _deselect_item(self, list_widget, value: str):
        """Deselecciona un item d'una llista"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() == value:
                item.setSelected(False)
                break

    def _get_selected_row_data(self, column: int) -> Optional[str]:
        """Obté el valor d'una columna de la fila seleccionada"""
        row_index = self.ui.tableWidget.currentRow()
        if row_index < 0:
            return None
        
        reference = self.ui.tableWidget.item(row_index, 0).text()
        
        for row in self.data_google_sheet[1:]:
            if reference == row[Config.REFERENCE]:
                return row[column]
        
        return None

    def _update_stock_info(self):
        """Actualitza la informació d'stock"""
        stock = self._get_selected_row_data(Config.STOCK)
        storage = self._get_selected_row_data(Config.STORAGE)
        
        if stock:
            self.ui.stock_text.setText(stock)
        if storage:
            self.ui.label_9.setText(storage)

    def _open_datasheet(self):
        """Obre el datasheet del component seleccionat"""
        web = self._get_selected_row_data(Config.WEB)
        
        if not web:
            self._show_status_message("No hi ha web disponible", 2000)
            return
        
        if web.startswith(("http://", "https://")):
            webbrowser.open_new_tab(web)
        else:
            self._show_status_message("URL invàlida", 2000)

    # def _open_google_sheet(self):
    #     """Obre el Google Sheet en una nova pestanya"""
    #     url = f"https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEET_ID}"
    #     webbrowser.open_new_tab(url)

    def _open_google_sheet(self):
        """Obre el Google Sheet en una nova pestanya a la fila del component seleccionat"""
        base_url = f"https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEET_ID}"
        gid = "1061024957"  # ID de la pestanya correcta
        
        # Intentar obtenir el component seleccionat
        row_index = self.ui.tableWidget.currentRow()
        
        if row_index < 0:
            # Si no hi ha selecció, obrir el sheet normalment
            url = f"{base_url}/edit#gid={gid}"
            webbrowser.open_new_tab(url)
            return
        
        # Obtenir el LCSC PN del component seleccionat
        reference = self.ui.tableWidget.item(row_index, 0).text()
        
        # Buscar la fila corresponent al Google Sheet
        sheet_row = None
        for idx, row in enumerate(self.data_google_sheet, start=1):
            if idx == 1:  # Saltar capçalera
                continue
            if row[Config.REFERENCE] == reference:
                sheet_row = idx #+ 1  # +1 perquè Google Sheets comença a 1, no a 0
                break
        
        if sheet_row:
            # Seleccionar tota la fila del component
            url = f"{base_url}/edit#gid={gid}&range={sheet_row}:{sheet_row}"
            webbrowser.open_new_tab(url)
            self._show_status_message(f"Obrint Google Sheet a la fila {sheet_row}", 2000)
        else:
            # Si no es troba la fila, obrir normalment
            url = f"{base_url}/edit#gid={gid}"
            webbrowser.open_new_tab(url)
            self._show_status_message("Component no trobat al Google Sheet", 2000)

    def _refresh_data(self):
        """Actualitza les dades del Google Sheet"""
        self.data_google_sheet = self._fetch_google_sheet()
        if self.data_google_sheet:
            self._populate_all_filter_lists()
            self._update_table()
            self._show_status_message("Dades actualitzades", 2000)

    def _show_status_message(self, message: str, duration: int = 2000):
        """Mostra un missatge a la barra d'estat"""
        self.ui.statusbar.showMessage(message, duration)


def main():
    """Punt d'entrada de l'aplicació"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
