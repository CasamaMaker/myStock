from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem
from PySide6.QtCore import Signal, Qt
from ui_main import Ui_MainWindow
import sys

import csv
import requests
from PySide6.QtWidgets import QTableWidgetItem, QListWidget, QAbstractItemView
import webbrowser


class TagWidget(QWidget):
    closed = Signal(str, str)  # per emetre el valor quan s'elimina

    def __init__(self, key, value):
    # def __init__(self, value):
        super().__init__()
        # print(key)
        self.key = key
        self.value = value

        # layout = QHBoxLayout(self)
        # layout.setContentsMargins(1, 0, 1, 0)  # afina una mica l'espai
        # layout.setSpacing(1)  # separació entre label i botó
        # # self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        # # self.adjustSize()

        # self.label = QLabel(f"{key} = <b>{value}</b>")
        # self.label.setStyleSheet("padding: 2px;")  # Opcional: per fer el tag més compacte
        
        # self.button = QPushButton("✖")
        # self.button.setFixedSize(16, 16)  # Més petit per no fer créixer el tag
        # self.button.clicked.connect(self.on_close)

        # layout.addWidget(self.label)
        # layout.addWidget(self.button)


        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 0, 1, 0)  # afina una mica l'espai
        layout.setSpacing(0)  # elimina l'espai entre l'etiqueta i el botó

        # Només el valor serà en negreta, el "key" es mostrarà normal
        # self.label = QLabel(f"{key} = <b>{value}</b>")
        self.label = QLabel(f"{value}")
        # self.label = QLabel(f"{key} = {value}")
        self.label.setStyleSheet("padding: 2px;")  # opcional: fer el tag més compacte

        # Crear un widget per agafar l'etiqueta i el botó junts
        tag_widget = QWidget(self)
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(0, 0, 0, 0)  # elimina els marges
        tag_layout.setSpacing(0)  # elimina l'espai entre els elements

        # Afegir l'etiqueta al layout del tag
        tag_layout.addWidget(self.label)

        # Crear el botó de tancar i afegir-lo al layout
        self.button = QPushButton("✖", tag_widget)  # La "X" no està en negreta
        # self.button = QPushButton("✕", tag_widget)  # La "X" no està en negreta
        self.button.setFixedSize(16, 16)  # fa el botó més petit

        # # Aplicar estils per fer la X més subtil
        # self.button.setStyleSheet("""
        #     QPushButton {
        #         font-size: 10px;  # Reduir la mida de la font
        #         font-weight: 100;  # Fer la font més lleugera
        #         color: rgba(0, 0, 0, 0.5);  # Color gris suau
        #         background: transparent;  # Eliminar el fons
        #         border: none;  # No mostrar cap contorn
        #     }
        #     QPushButton:hover {
        #         color: rgba(0, 0, 0, 0.7);  # Canviar el color quan es passa el ratolí per fer-ho més destacat
        #     }
        # """)


        self.button.clicked.connect(self.on_close)
        

        # Afegir el botó al layout del tag
        tag_layout.addWidget(self.button)

        # Afegir el widget del tag al layout principal
        layout.addWidget(tag_widget)


        # Mida automàtica segons contingut
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.adjustSize()

        # # Layout principal que fa de contenidor
        # self.main_layout = QVBoxLayout(self)
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_layout.setSpacing(0)

        # # Layout per als tags (horitzontal)
        # self.horizontal_layout = QHBoxLayout()
        # self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.horizontal_layout.setSpacing(5)  # Ajusta l'espai entre tags

        # # Afegir el layout horitzontal a la disposició principal
        # self.main_layout.addLayout(self.horizontal_layout)

        # # Crear el widget per al tag (etiqueta + botó)
        # tag_widget = QWidget(self)
        # tag_layout = QHBoxLayout(tag_widget)
        # tag_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar marges
        # tag_layout.setSpacing(0)

        # # Afegir l'etiqueta
        # # self.label = QLabel(f"{key} = <b>{value}</b>")
        # self.label = QLabel(f"{value}")
        # self.label.setStyleSheet("padding: 2px;")  # Fer el tag més compacte
        # tag_layout.addWidget(self.label)

        # # Afegir el botó de tancar
        # self.button = QPushButton("✖", tag_widget)
        # self.button.setFixedSize(16, 16)  # Mida petita per al botó
        # self.button.clicked.connect(self.on_close)
        # tag_layout.addWidget(self.button)

        # # Afegir el widget del tag al layout horitzontal
        # self.horizontal_layout.addWidget(tag_widget)

        # # Afegir un espaiador que permeti que els tags passin a la línia següent
        # self.horizontal_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # # Configurar la mida automàtica del widget
        # self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        # self.adjustSize()

        # self.setLayout(layout)
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
            /*QPushButton {
                font-size: 10px;  # Reduir la mida de la font
                font-weight: 100;  # Fer la font més lleugera
                color: rgba(0, 0, 0, 0.5);  # Color gris suau
                background: transparent;  # Eliminar el fons
                border: none;  # No mostrar cap contorn
            }
            QPushButton:hover {
                color: rgba(0, 0, 0, 0.7);  # Canviar el color quan es passa el ratolí per fer-ho més destacat
            }*/
        """)

    def on_close(self):
        print(f"Emetent el valor: {self.value}")  # Afegeix aquest print
        self.closed.emit(self.key, self.value)  # Avís al pare que s'ha eliminat
        self.setParent(None)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.stock_col = 0
        self.storage_col = 1
        self.type_col = 2
        self.lcscPN_col = 3
        self.manufacturePN_col = 4
        self.description_col = 5
        self.package_col = 6
        self.web_col = 7

        self.ui.pushButton.setFlat(True)
        self.ui.pushButton.clicked.connect(self.reset_llista_categoria)
        self.ui.pushButton_2.setFlat(True)
        self.ui.pushButton_2.clicked.connect(self.reset_llista_encapsulat)
        self.ui.pushButton_3.setFlat(True)
        self.ui.pushButton_3.clicked.connect(self.reset_llista_taula)
        self.ui.pushButton_4.clicked.connect(self.obre_arxiu_stock)
        self.ui.pushButton_5.clicked.connect(self.actualitza_google_sheet)
        # self.ui.pushButton_5.setText("↻")
        # Assignar el missatge que es mostrarà quan el cursor passi per sobre del botó

        self.ui.datasheetButton.setToolTip("Obre la web/datasheet")
        self.ui.pushButton_4.setToolTip("Obre l'arxiu")
        self.ui.pushButton_5.setToolTip("Actualiza les dades")
        self.ui.label_5.setToolTip("Components filtrats")
        self.ui.label_2.setToolTip("Stock del component")
        self.ui.stock_text.setToolTip("Stock del component")
        self.ui.stock_text.setEnabled(False)

        # self.setStyleSheet("background-color: #4A708B;")  # blau marí clar
        # self.setStyleSheet("""
        #                     QMainWindow {
        #                         background-color: #4A708B;
        #                     }
        #                     QWidget {
        #                         background-color: #4A708B;
        #                         color: white;  /* text en blanc */
        #                     }
        #                     QLineEdit {
        #                         background-color: #5A809B;
        #                         color: white;
        #                         border: 1px solid white;
        #                     }
        #                     QTableWidget {
        #                         background-color: #5A809B;
        #                         color: white;
        #                         gridline-color: white;
        #                     }
        #                     QTableCornerButton::section {
        #                         background-color: #3B5C73;  /* mateix color que la capçalera */
        #                         /*border: 1px solid white;*/
        #                     }
        #                     QHeaderView::section {
        #                         background-color: #3B5C73;
        #                         color: white;
        #                     }
        #                     QPushButton {
        #                         background-color: transparent;
        #                         border: none;
        #                         color: white;
                                
        #                     }
        #                     QPushButton:hover {
        #                         color: blue;
        #                     }
        #                 """)


        self.data_google_sheet = self.carrega_google_sheet()

        self.obtenir_tipos_component()
        self.obtenir_encapsulat_component()

        self.ui.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.listWidget_3.setSelectionMode(QAbstractItemView.MultiSelection)


        self.ui.lineEdit.textChanged.connect(self.filtrar_tipos_components)
        self.ui.lineEdit_3.textChanged.connect(self.filtrar_encapsulat_components)
        self.ui.lineEdit_4.textChanged.connect(self.filtrar_text_taula)
        self.text_filtre_taula = []
        # self.llistaFiltres = []
        self.ui.lineEdit_5.textChanged.connect(self.filtre_partNumber)
        self.text_filtre_partNumber = []
        
        # Filtratge de búsqueda
        self.ui.listWidget.itemClicked.connect(self.categoria_component_seleccionada)
        self.ui.listWidget_3.itemClicked.connect(self.encapsulat_component_seleccionat)

        # Selecció de component
        self.ui.tableWidget.itemSelectionChanged.connect(self.info_stock)
        # self.ui.tableWidget.selectedItems

        self.ui.datasheetButton.pressed.connect(self.goDatasheet)



        # Eliminar l'espai de distribució automàtica en el layout
        self.ui.horizontalLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Crear els tags i afegir-los al layout
        # tag1 = TagWidget("Memory Type", "Flash")
        # tag1.closed.connect(self.on_tag_closed)  # Connecta el senya
        # self.ui.horizontalLayout.addWidget(tag1)

        # tag2 = TagWidget("Component Type", "Resistence")
        # self.ui.horizontalLayout.addWidget(tag2)
        self.tag_widgets = []  # Llista per emmagatzemar els TagWidget

        filterVisualization = True # tag1_list0
        if filterVisualization: # tag1_list0
            self.ui.listWidget_4.setVisible(False)   # list
            self.ui.widget.setVisible(True)          # tag
        else:
            self.ui.listWidget_4.setVisible(False)   # list
            self.ui.widget.setVisible(True)          # tag

        self.ui.pushButton_3.setVisible(False) 

        self.carregar_google_sheets_a_tablewidget()

        self.ui.statusbar.showMessage("Iniciat", 2000)  # 2000 ms = 2 segons

    def carrega_google_sheet(self):
        "carrega les dades des de l'arxiu de google sheets"
        try:
            # URL del Google Sheet (convertida a formato CSV)
            google_sheet_id = "1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA" #"1aBQq8viig-m8QpupEm3EGmwK_aMGMgW3kNIPjLNPpkY"
            self.csv_url = f"https://docs.google.com/spreadsheets/d/{google_sheet_id}/export?format=csv"

            # self.ui.pushButton_4.clicked.connect(self.obre_arxiu_stock)
            
            # Realizar la petición HTTP
            response = requests.get(self.csv_url)
            response.raise_for_status()  # Lanza excepción si hay error HTTP
            
            # Decodificar el contenido CSV
            csv_content = response.content.decode('utf-8')
            csv_reader = csv.reader(csv_content.splitlines())
            
            # Convertir a lista para poder trabajar con los datos
            data = list(csv_reader)
            
            if not data:
                print("No s'han trovat dades a Google Sheet")
                return
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error al accedir a Google Sheet: {e}")
            self.ui.statusbar.showMessage(f"Error al accedir a Google Sheet: {e}", 2000)  # 2000 ms = 2 segons

    def actualitza_google_sheet(self):
        "torna a carregar les dades des de l'arxiu de google sheets"
        self.data_google_sheet = self.carrega_google_sheet()
        self.carregar_google_sheets_a_tablewidget()

    def obre_arxiu_stock(self):
        "obra l'arxiu de google sheets"
        webbrowser.open_new_tab(f"https://docs.google.com/spreadsheets/d/1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA")

    def obtenir_tipos_component(self):
        "inici - defineix la llista dels diferents tipus de components que existeixen"
        self.tipos_components = []
        data_colums = self.type_col

        self.tipos_components = {fila[data_colums] for fila in self.data_google_sheet [1:]}
        self.tipos_components = sorted(list(self.tipos_components))

        self.ui.listWidget.clear()
        # self.tipos_components = ["RESISTOR", "CAPACITOR", "MOSFET"]
        self.ui.listWidget.addItems(self.tipos_components)
        # Selecciona una opció per defecte
        self.type_selected = []
        # self.ui.listWidget.setCurrentRow(self.tipos_components.index(self.type_selected))

        text = self.ui.label.text()
        self.ui.label.setText(text + " ["+str(len(self.tipos_components))+"]")

    def obtenir_encapsulat_component(self):
        "inici - defineix la llista dels diferents tipus d'encapsulats que existeixen"
        self.encapsulat_components = []
        data_colums = self.package_col

        self.encapsulat_components = {fila[data_colums] for fila in self.data_google_sheet[1:]}
        self.encapsulat_components = sorted(list(self.encapsulat_components))

        self.ui.listWidget_3.clear()
        self.ui.listWidget_3.addItems(self.encapsulat_components)

        self.package_selected = []

        text = self.ui.label_4.text()
        self.ui.label_4.setText(text + " ["+str(len(self.encapsulat_components))+"]")

    def filtrar_tipos_components(self):
        'Aplica filtre per mostrar la llista de tipos de components --- filtrant pel text o per una selecció en una altre llista'

        # actualitza els valors que es mostren a la llista, segons el text, PERO no es selecciona cap item
        text_filtre_llista = self.ui.lineEdit.text()
        filtre_tipos_components= [component for component in self.tipos_components if text_filtre_llista.lower() in component.lower()]
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(filtre_tipos_components)


        # mante senyalitzar els items seleccionats
        for idx in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(idx)
            if item.text() in self.type_selected:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def filtrar_encapsulat_components(self):
        'defineix la llista d\'encapsultats de components --- filtrant pel text o per una selecció en una altre llista'
        # if filterType == "textChanged":
        text_filtre_llista = self.ui.lineEdit_3.text()
        filtre_encapsulat_components = [encapsulat for encapsulat in self.encapsulat_components if text_filtre_llista.lower() in encapsulat.lower()]
        self.ui.listWidget_3.clear()
        self.ui.listWidget_3.addItems(filtre_encapsulat_components)


        # mante senyalitzar els items seleccionats
        for idx in range(self.ui.listWidget_3.count()):
            item = self.ui.listWidget_3.item(idx)
            if item.text() in self.package_selected:
                item.setSelected(True)
            else:
                item.setSelected(False)



        # # elif filterType == "itemClicked":
        # categoria_component_seleccionat = self.ui.listWidget.currentItem()

        # if categoria_component_seleccionat:  # Comprovar que no és None
        #     categoria_text = categoria_component_seleccionat.text()
            
        #     filtre_encapsulat_components = list(set([
        #         fila[self.package_col]
        #         for fila in self.data_google_sheet
        #         if fila[self.type_col] == categoria_text]))
        # # else:
        # #     filtre_encapsulat_components = self.encapsulat_components   

    def carregar_google_sheets_a_tablewidget(self):
        "carregar les dades filtrades a la taula"
        # Definir las columnas específicas que queremos mostrar
        columnas_deseadas = [self.lcscPN_col, self.manufacturePN_col, self.package_col, self.storage_col, self.description_col]

        dades_filtrades = self.data_google_sheet
        headers_filtrats = [dades_filtrades[0][titol] for titol in columnas_deseadas]   

        # Filtrar els components seleccionats
        if hasattr(self, "type_selected"):
            if self.type_selected:
                dades_filtrades = [fila for fila in dades_filtrades if fila[self.type_col] in self.type_selected]

        if hasattr(self, "package_selected"):
            if self.package_selected:
                dades_filtrades = [fila for fila in dades_filtrades if fila[self.package_col] in self.package_selected]

        if hasattr(self, "text_filtre_taula"):
            if self.text_filtre_taula:
                dades_filtrades = [fila for fila in dades_filtrades if any(self.text_filtre_taula.lower() in str(cel).lower() for cel in fila)]

        if hasattr(self, "text_filtre_partNumber"):
            if self.text_filtre_partNumber:
                dades_filtrades = [fila for fila in dades_filtrades if  self.text_filtre_partNumber.lower() in str(fila[self.manufacturePN_col]).lower()]

        self.llista_filtres()

        # Filtrar les columnes que desitgem mostrar
        if dades_filtrades:
            if dades_filtrades[0][self.lcscPN_col] in headers_filtrats:
                # print("hi ha headers")
                # dades_filtrades.pop(0)   # treu la primera fila
                # dades_a_imprimir = dades_filtrades[1:]

                dades_a_imprimir = [
                [fila[i] for i in columnas_deseadas]
                for fila in dades_filtrades[1:]
            ]
            else:
                # print("NO hi ha headers")
                dades_a_imprimir = [
                [fila[i] for i in columnas_deseadas]
                for fila in dades_filtrades
            ]

            # PASO 2: Configurar el QTableWidget con el número correcto de filas filtradas
            num_rows_filtradas = len(dades_a_imprimir)
            self.ui.label_5.setText(str(num_rows_filtradas))
            self.ui.tableWidget.setRowCount(num_rows_filtradas)
            self.ui.tableWidget.setColumnCount(len(columnas_deseadas))  # 3 columnas específicas
            
            # Establecer encabezados de columna
            self.ui.tableWidget.setHorizontalHeaderLabels(headers_filtrats)

            for num_fila, data_fila in enumerate(dades_a_imprimir):
                for num_col, data_col in enumerate(data_fila):
                    item = QTableWidgetItem(str(data_col))
                    # print(str(data_col))  # Això mostra el contingut real
                    self.ui.tableWidget.setItem(num_fila, num_col, item)

            # Ajustar el ancho de las columnas al contenido
            self.ui.tableWidget.resizeColumnsToContents()

        else:
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0)
            self.ui.label_5.setText("0")
            self.ui.statusbar.showMessage("No hi ha valors corresponent al filtre", 2000)

    def llista_filtres(self):
        "es mostren els filtres aplicats"
        self.llistaFiltres = []

        # Esborrem tots els tags
        self.close_all_tags()

        self.tag_widgets = []  # Llista per emmagatzemar els TagWidget
        print("hola")
        if self.type_selected:
            print("llista_filtres type_selected", self.type_selected)
            self.llistaFiltres += self.type_selected
            for item in self.type_selected:
                self.creaTag("type", item)
        if self.package_selected:
            self.llistaFiltres += self.package_selected
            for item in self.package_selected:
                self.creaTag("package", item)
        if self.text_filtre_taula:
            print("llista_filtres text_filtre_taula", self.text_filtre_taula)
            self.llistaFiltres.append(self.text_filtre_taula)
            self.creaTag("text", self.text_filtre_taula)
        if self.text_filtre_partNumber:
            self.llistaFiltres.append(self.text_filtre_partNumber)
            self.creaTag("partNumber", self.text_filtre_partNumber)

        # Mostre la llista amb el filtres aplicats
        self.ui.listWidget_4.clear()
        self.ui.listWidget_4.addItems(self.llistaFiltres)

    def creaTag(self, key, value):
        "Creació dels tags amb les dades rebudes"
        tag1 = TagWidget(key, value)
        tag1.closed.connect(self.on_tag_closed)  # Connecta el senyal de tancament
        self.ui.horizontalLayout.addWidget(tag1)
        self.tag_widgets.append(tag1)  # Afegim cada TagWidget a la llista
        # print(">>>", self.tag_widgets)

    def close_all_tags(self):
        "Tanca tots els tags, això es fa quan s'actualitza la llista de filtres"

        print("tanca toot", self.tag_widgets)
        # Emetem la senyal de tancament per a tots els tags
        for tag in self.tag_widgets:
            tag.close()  # Això tanca el tag

    def on_tag_closed(self, key, value):
        "S'ha tancat un objecte tag i ens revota aqui, i esborrem el item de la llista"

        print(f"El tag amb la clau '{key}'ha estat tancat...'{value}'")
        # print(">>", key)
        if key == "type":
            self.type_selected.remove(value)

        if key == "package":
            self.package_selected.remove(value)

        if key == "text":
            self.text_filtre_taula.clear()

        if key == "partNumber":
            self.text_filtre_partNumber.clear()


        self.llista_filtres()



        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            # print(".............", item, value)
            if item.text() == value:
                # print(i, "zzzzz ", item.text())
                item.setSelected(False)
                break

    def obtenir_info_seleccio(self, columna):
        fila_index = self.ui.tableWidget.currentRow()
        valor_buscat = self.ui.tableWidget.item(fila_index, 0).text()
        # print(fila_index, valor_buscat)

        # if not fila_index:
        #     return

        for fila in self.data_google_sheet:
            if valor_buscat in fila[self.lcscPN_col]:
                # print(fila[7].strip())
                # self.ui.stock_text.setPlainText(fila[0])
                print(">", valor_buscat, fila[columna])#.strip())
                return fila[columna]

    def info_stock(self):
        self.ui.stock_text.setText(self.obtenir_info_seleccio(self.stock_col))
 
    def categoria_component_seleccionada(self):
        '''S'arriba aquí quan es presion un item a la lista de tipos de components'''
        # actualitza llista de tipos de components seleccionats
        pressionat= self.ui.listWidget.currentItem().text()
        if pressionat in self.type_selected:
            self.type_selected.remove(pressionat)
        else:
            self.type_selected.append(pressionat)

        # print("type_selected", self.type_selected)

        # un cop seleccionat l'item, esborrem el textEdit
        self.ui.lineEdit.setText("")

        # Actualitzem llista de components segons filtre
        self.filtrar_tipos_components()
        
        # Actualizem taula valors segons nou filtre
        self.carregar_google_sheets_a_tablewidget()

        self.filtrar_encapsulat_components()

    def reset_llista_categoria(self):
        # print("hola")
        self.type_selected.clear()
        self.filtrar_tipos_components()
        self.carregar_google_sheets_a_tablewidget()

    def encapsulat_component_seleccionat(self, item):

        # actualitza llista de tipos de components seleccionats
        pressionat= self.ui.listWidget_3.currentItem().text()
        if pressionat in self.package_selected:
            self.package_selected.remove(pressionat)
        else:
            self.package_selected.append(pressionat)

        # print("package_selected", self.package_selected)
        # self.package_selected = item.text()

        self.ui.lineEdit_3.setText("")
        self.filtrar_encapsulat_components()

        self.carregar_google_sheets_a_tablewidget()

        self.filtrar_tipos_components()

    def reset_llista_encapsulat(self):
        # print("hola")
        self.package_selected.clear()
        self.filtrar_encapsulat_components()
        self.carregar_google_sheets_a_tablewidget()

    def filtrar_text_taula(self):
        self.text_filtre_taula = self.ui.lineEdit_4.text()
        self.carregar_google_sheets_a_tablewidget()

    def reset_llista_taula(self):
        "resetaja  el filtre de text total"
        print("reset_llista_taula")
        self.ui.lineEdit_4.clear()  # neteja el camp de text
        self.text_filtre_taula = "" # assegura que la variable també està buida
        self.carregar_google_sheets_a_tablewidget()

    def filtre_partNumber(self):
        self.text_filtre_partNumber = self.ui.lineEdit_5.text()
        print(self.text_filtre_partNumber)
        self.carregar_google_sheets_a_tablewidget()

    def goDatasheet(self):
        # print(self.obtenir_info_seleccio(self.web_col))
        web = self.obtenir_info_seleccio(self.web_col)
        # print(web)

        if web:
            if web.startswith(("http://", "https://")):
                webbrowser.open_new_tab(web)
            else:
                print("No és una web")
                self.ui.statusbar.showMessage("No hi ha web", 2000)  # 2000 ms = 2 segons

        # items = self.ui.tableWidget.selectedItems()
        # if items:  # si hi ha alguna cel·la seleccionada
        #     for item in items:
        #         print(item.text())


        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())