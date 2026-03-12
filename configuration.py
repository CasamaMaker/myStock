
from dataclasses import dataclass

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
    
    
    # Columnes del fitxer d'estoc
    # POTS MODIFICAR NOM I PARÀMETRE
    ID = 0
    MANUFACTURER_PN = 1
    MANUFACTURER_NAME = 2
    CATEGORY = 3
    SUPPLIER = 4
    SUPPLIER_PN = 5
    SUPPLIER_CATEGORY = 6
    PACKAGE = 7
    DESCRIPTION = 8
    STOCK = 9
    STORAGE = 10
    DATASHEET = 11
    SUPPLIER_PRODUCT = 12




    # Paràmetres obligatoris per funcionar - columnes
    # MODIFICA NOMÉS EL PARÀMETRE
    ID = ID                                 # número unic identificatiu de cada component
    STOCK = STOCK                           # estoc existent
    STORAGE = STORAGE                       # localització del component
    WEB = DATASHEET                         # link d'una web, ja sigui del datasheet o la web on comprar o un tutorial
    REFERENCE = SUPPLIER_PN                 # nom del component
    





    # Defineix els diferents filtres
    # MODIFICA NOMÉS EL PARÀMETRE, els que es deixin comentats es deshabiliten
    FILTRE1 = CATEGORY
    FILTRE2 = SUPPLIER_CATEGORY
    FILTRE3 = PACKAGE
    FILTRE4 = SUPPLIER
    FILTRE5 = MANUFACTURER_NAME

    TEXT_FILTER = MANUFACTURER_PN           # columna que volem utilitzar el filtre de text




    
    # Columnes a mostrar a la taula de components filtrats i les seves amplades
    # MODIFICA NOMÉS EL PARÀMETRE 
    COLUMNS_TO_SHOW = [ID, REFERENCE, PACKAGE, DESCRIPTION, MANUFACTURER_PN, MANUFACTURER_NAME]
    COLUMNS_WIDTH = [50, 150, 80, 300, 150, 150]


    # Configuració de filtres
    # NO MODIFICAR
    FILTERS_CONFIG = [
        FilterConfig(
            column_index=FILTRE1,
            label_widget_name=  "filter1_label",
            line_edit_name=     "filter1_lineEdit",
            list_widget_name=   "filter1_listWidget",
            button_name=        "filter1_pushButton",
            tag_key=            "filter1",
            enabled='FILTRE1' in locals()
        ),
        FilterConfig(
            column_index=FILTRE2,
            label_widget_name="filter2_label",
            line_edit_name="filter2_lineEdit",
            list_widget_name="filter2_listWidget",
            button_name="filter2_pushButton",
            tag_key="filter2",
            # enabled=True  # Canvia a False per desactivar
            enabled='FILTRE2' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=FILTRE3,
            label_widget_name="filter3_label",
            line_edit_name="filter3_lineEdit",
            list_widget_name="filter3_listWidget",
            button_name="filter3_pushButton",
            tag_key="filter3",
            # enabled=True  # Canvia a False per desactivar
            enabled='FILTRE3' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=FILTRE4,
            label_widget_name="filter4_label",
            line_edit_name="filter4_lineEdit",
            list_widget_name="filter4_listWidget",
            button_name="filter4_pushButton",
            tag_key="filter4",
            # enabled=False  # Canvia a False per desactivar
            enabled='FILTRE4' in locals()  # False perquè està comentat
        ),
        FilterConfig(
            column_index=FILTRE5,
            label_widget_name="filter5_label",
            line_edit_name="filter5_lineEdit",
            list_widget_name="filter5_listWidget",
            button_name="filter5_pushButton",
            tag_key="filter5",
            # enabled=False  # Canvia a False per desactivar
            enabled='FILTRE5' in locals()  # False perquè està comentat
        ),
    ]

    
    # amaga o desavilita els paràmetre de filtre NO disponibles --> True: amaga; False: deshabilita
    # MODIFICA NOMÉS EL PARÀMETRE 
    FILTRER_AVAILABILITY = True     


    # Google Sheet and credentials
    # GOOGLE_SHEET_ID = "1jTJQL-PM7Uq1Gvns65RWnZOWWBl-359ZsKDoc6suoGQ"                # personal Stock22
    # GOOGLE_CREDENTIALS_JSON = "credentials/mystock-482208-9ff7a94ae596.json"        # personal2

    GOOGLE_SHEET_ID = "1cbyUW76l9EDPyHaKr98ARRroAWqfM3ctaYlRFw9enBg"              ## grupeina
    GOOGLE_CREDENTIALS_JSON = "credentials/model-folio-482716-e4-ef9a987e1f30.json"        # personal2
    

    # Timeout per peticions HTTP (segons)
    # MODIFICA NOMÉS EL PARÀMETRE 
    REQUEST_TIMEOUT = 10
