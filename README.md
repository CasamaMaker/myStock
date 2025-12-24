# myStock
descktop app for stock control from ddbb google sheets


# 📦 MyStock - Gestor d'Inventari de Components Electrònics

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

*Una aplicació d'escriptori potent i intuïtiva per gestionar el teu inventari de components electrònics*

[Característiques](#-característiques) •
[Instal·lació](#-installació) •
[Configuració](#️-configuració) •
[Ús](#-ús) •
[Contribuir](#-contribuir)

</div>

---

## 📖 Descripció

**MyStock** és una aplicació d'escriptori desenvolupada amb Python i PySide6 (Qt6) que et permet gestionar de manera eficient el teu inventari de components electrònics. Les dades es sincronitzen directament amb un **Google Sheet**, permetent accés multiusuari i actualitzacions en temps real.

L'aplicació està dissenyada especialment per a makers, enginyers, estudiants i aficionats a l'electrònica que necessiten mantenir un control precís del seu stock de components.

---

## ✨ Característiques

### 🔍 **Sistema de filtratge avançat**
- **Filtres dinàmics múltiples**: Filtra per tipus de component, encapsulat, ubicació d'emmagatzematge i més
- **Filtre de text general**: Cerca qualsevol valor en totes les columnes simultàniament
- **Filtre per Part Number**: Cerca específica per número de fabricant
- **Filtres intel·ligents**: Els filtres es desactiven visualment quan no hi ha resultats disponibles
- **Tags visuals**: Cada filtre actiu es mostra com un tag que pots eliminar amb un clic

### 📊 **Visualització intel·ligent**
- **Taula configurable**: Mostra només les columnes que necessites
- **Informació detallada**: Visualitza stock, ubicació i descripció del component seleccionat
- **Amplades personalitzables**: Ajusta l'amplada de cada columna segons les teves necessitats
- **Comptador de resultats**: Visualitza quants components coincideixen amb els teus filtres

### ☁️ **Integració amb Google Sheets**
- **Sincronització automàtica**: Les dades es carreguen directament des de Google Sheets via API
- **Actualització en temps real**: Refresca les dades amb un sol clic
- **Accés ràpid**: Obre el Google Sheet directament des de l'aplicació
- **Multiusuari**: Diversos usuaris poden actualitzar el Google Sheet simultàniament

### 🔗 **Accés ràpid a datasheets**
- **Obertura automàtica**: Clica un botó i obre el datasheet o web del component al navegador
- **URLs personalitzables**: Cada component pot tenir el seu propi enllaç

### ⚙️ **Configuració flexible**
- **Filtres opcionals**: Activa o desactiva filtres segons les teves necessitats
- **Columnes personalitzables**: Defineix quines columnes del Google Sheet vols visualitzar
- **Fàcil adaptació**: Adapta l'aplicació a l'estructura del teu inventari

---

## 🖼️ Captures de pantalla

### Interfície principal
![Captura principal](docs/images/screenshot_main.png)
*Vista principal amb filtres actius i taula de components*

### Sistema de filtres
![Filtres](docs/images/screenshot_filters.png)
*Filtres dinàmics amb tags visuals*

### Detall del component
![Detall](docs/images/screenshot_detail.png)
*Informació detallada del component seleccionat*

---

## 🎯 Cas d'ús

Imagina que estàs treballant en un projecte i necessites un **regulador de voltatge de 3.3V en format SOT-23**:

1. 🔍 Aplica el filtre **Tipus**: "Regulador de voltatge"
2. 📦 Aplica el filtre **Package**: "SOT-23"
3. ⚡ Filtra per voltatge amb el cercador general: "3.3V"
4. ✅ **Resultats instantanis**: veus tots els reguladors de 3.3V en SOT-23 que tens en stock
5. 📍 **Ubicació**: l'aplicació et mostra on està emmagatzemat cada component
6. 📊 **Stock**: veus quantes unitats tens disponibles
7. 📄 **Datasheet**: obre el datasheet amb un clic per verificar les especificacions

---

## 🛠️ Tecnologies utilitzades

| Tecnologia | Propòsit |
|------------|----------|
| **Python 3.8+** | Llenguatge de programació principal |
| **PySide6 (Qt6)** | Framework d'interfície gràfica |
| **gspread** | Llibreria per interactuar amb Google Sheets API |
| **google-auth** | Autenticació amb Google Cloud |
| **requests** | Peticions HTTP |
| **Qt Designer** | Disseny de la interfície d'usuari |

---

## 📋 Requisits previs

Abans d'instal·lar MyStock, assegura't de tenir:

- **Python 3.8 o superior** instal·lat
- Un compte de **Google Cloud** (gratuït)
- Un **Google Sheet** preparat amb el teu inventari
- Connexió a internet (per sincronitzar amb Google Sheets)

---

## 🏗️ Estructura del projecte
```
mystock/
│
├── main.py                           # Fitxer principal de l'aplicació
├── ui_main.py                        # Interfície generada per Qt Designer
├── ui_main.ui                        # Fitxer de disseny Qt Designer
├── recursos_grafics.qrc              # Fitxer de recursos Qt
├── recursos_grafics_rc.py            # Recursos compilats
│
├── credentials/                      # Carpeta per credencials (NO pujar a Git)
│   └── mystock-service-account.json  # Credencials del service account
│
├── docs/                             # Documentació
│   └── images/                       # Captures de pantalla
│
├── requirements.txt                  # Dependències del projecte
├── .gitignore                        # Fitxers a ignorar per Git
├── README.md                         # Aquest fitxer
└── LICENSE                           # Llicència del projecte
```

---

## 🎨 Característiques visuals

- **Interfície moderna**: Disseny net i intuïtiu amb Qt6
- **Tags interactius**: Visualització clara dels filtres actius
- **Feedback visual**: Colors i estats que indiquen disponibilitat
- **Responsive**: S'adapta a diferents mides de pantalla
- **Mode fosc compatible**: Integració amb el tema del sistema operatiu

---

## 📈 Roadmap

- [ ] Exportació de dades a CSV/Excel
- [ ] Gràfics d'estadístiques d'inventari
- [ ] Sistema d'alertes per stock baix
- [ ] Historial de moviments de components
- [ ] Mode offline amb sincronització posterior
- [ ] Suport per múltiples Google Sheets
- [ ] Escàner de codis de barres
- [ ] App mòbil complementària

---

## 🤝 Contribuir

Les contribucions són benvingudes! Si vols millorar MyStock:

1. 🍴 Fes un fork del projecte
2. 🌿 Crea una branca per a la teva funcionalitat (`git checkout -b feature/nova-funcionalitat`)
3. 💾 Fes commit dels teus canvis (`git commit -m 'Afegeix nova funcionalitat'`)
4. 📤 Puja la branca (`git push origin feature/nova-funcionalitat`)
5. 🔀 Obre un Pull Request

### Àrees on pots contribuir

- 🐛 Reportar bugs
- 💡 Proposar noves funcionalitats
- 📝 Millorar la documentació
- 🌍 Traduir l'aplicació a altres idiomes
- 🎨 Millorar el disseny de la interfície

---

## 📄 Llicència

Aquest projecte està llicenciat sota la llicència MIT. Consulta el fitxer [LICENSE](LICENSE) per a més detalls.

---

## 👨‍💻 Autor

**El teu nom**
- GitHub: [@CasamaMaker](https://github.com/el-teu-usuari)
- Email: el-teu-email@example.com

---

## 🙏 Agraïments

- Gràcies a la comunitat de **Qt** i **PySide6** per l'excel·lent framework
- Gràcies a **Google** per proporcionar l'API de Google Sheets
- Inspirat per la necessitat de gestionar eficientment inventaris de components electrònics

---

## 📞 Suport

Si tens preguntes o problemes:

1. 📖 Consulta la [documentació](#️-configuració)
2. 🐛 Obre un [issue](https://github.com/el-teu-usuari/mystock/issues)
3. 💬 Contacta per email

---

<div align="center">

**⭐ Si aquest projecte t'ha estat útil, considera donar-li una estrella! ⭐**

Made with ❤️ and ☕ by [El teu nom]

</div>

## ⚙️ Configuració

### 1. 📋 Google Sheets API

#### 1.1 Crear un projecte a Google Cloud

1. Ves a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nou projecte o selecciona'n un d'existent
3. Al menú lateral, ves a **APIs & Services** > **Library**
4. Cerca i activa les següents APIs:
   - **Google Sheets API**
   - **Google Drive API**

#### 1.2 Crear un Service Account

1. Ves a **APIs & Services** > **Credentials**
2. Clica **Create Credentials** > **Service Account**
3. Omple els detalls del service account:
   - **Nom**: `mystock-service` (o el que prefereixis)
   - **Descripció**: Service account per accedir al Google Sheet d'inventari
4. Clica **Create and Continue**
5. Salta els passos opcionals i clica **Done**

#### 1.3 Generar les credencials JSON

1. A la llista de Service Accounts, clica sobre el que acabes de crear
2. Ves a la pestanya **Keys**
3. Clica **Add Key** > **Create new key**
4. Selecciona **JSON** i clica **Create**
5. Es descarregarà un fitxer JSON amb aquest format:
```json
   {
     "type": "service_account",
     "project_id": "mystock-482208",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "mystock-service@mystock-482208.iam.gserviceaccount.com",
     ...
   }
```

#### 1.4 Configurar les credencials al projecte

1. Crea una carpeta `credentials/` a l'arrel del projecte:
```bash
   mkdir credentials
```

2. Mou el fitxer JSON descarregat a aquesta carpeta i renombra'l:
```
   credentials/mystock-482208-a553ed840217.json
```

3. **IMPORTANT**: Afegeix aquesta carpeta al `.gitignore` per evitar pujar les credencials al repositori:
```bash
   echo "credentials/" >> .gitignore
```

#### 1.5 Compartir el Google Sheet amb el Service Account

1. Obre el teu Google Sheet
2. Clica el botó **Compartir** (dalt a la dreta)
3. Afegeix l'email del service account (el trobaràs al fitxer JSON, camp `client_email`):
```
   mystock-service@mystock-482208.iam.gserviceaccount.com
```
4. Dona-li permisos d'**Editor**
5. Desmarca "Notificar a les persones" (és un compte de servei, no cal)
6. Clica **Compartir** o **Enviar**

---

### 2. 🔧 Configuració del fitxer `main.py`

Tots els paràmetres de configuració es troben a la classe `Config` al començament del fitxer:
```python
class Config:
    """Configuració centralitzada de columnes i visualització"""
    
    # Google Sheet ID (obté'l de la URL del teu Google Sheet)
    GOOGLE_SHEET_ID = "1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA"
    
    # Ruta al fitxer de credencials JSON
    GOOGLE_CREDENTIALS_JSON = "credentials/mystock-482208-a553ed840217.json"
    
    # Timeout per peticions HTTP (segons)
    REQUEST_TIMEOUT = 10
```

#### 2.1 Obtenir el Google Sheet ID

El Google Sheet ID es troba a la URL del teu full de càlcul:
```
https://docs.google.com/spreadsheets/d/1U3H3R8ggRW-nEao_R1RXQ-l8WJdiGkXbWTSRkL0peRA/edit
                                        └────────────────────────────────────────┘
                                                    Aquest és el Sheet ID
```

#### 2.2 Configurar les columnes

La classe `Config` defineix els índexs de les columnes del Google Sheet:
```python
# Índexs de columnes (comencen en 0)
STOCK = 0           # Columna A: Quantitat en stock
STORAGE = 1         # Columna B: Ubicació d'emmagatzematge
TYPE = 2            # Columna C: Tipus de component
LCSC_PN = 3         # Columna D: Part Number LCSC
MANUFACTURE_PN = 4  # Columna E: Part Number del fabricant
DESCRIPTION = 5     # Columna F: Descripció del component
PACKAGE = 6         # Columna G: Encapsulat (package)
WEB = 7             # Columna H: URL del datasheet/web
```

**⚠️ IMPORTANT**: Si el teu Google Sheet té un ordre diferent de columnes, ajusta aquests índexs en conseqüència.

#### 2.3 Configurar columnes visibles a la taula

Pots triar quines columnes mostrar i amb quina amplada:
```python
# Columnes a mostrar i les seves amplades (en píxels)
COLUMNS_TO_SHOW = [LCSC_PN, MANUFACTURE_PN, PACKAGE, DESCRIPTION]
COLUMNS_WIDTH = [110, 150, 70, 300]
```

---

### 3. 🎛️ Configuració dels filtres

Els filtres es configuren mitjançant la llista `FILTERS_CONFIG` dins la classe `Config`:
```python
FILTERS_CONFIG = [
    FilterConfig(
        column_index=TYPE,              # Columna que filtra
        label_widget_name="filter1_label",
        line_edit_name="filter1_lineEdit",
        list_widget_name="filter1_listWidget",
        button_name="filter1_pushButton",
        tag_key="filter1",
        enabled=True                    # True per activar, False per desactivar
    ),
    FilterConfig(
        column_index=PACKAGE,
        label_widget_name="filter2_label",
        line_edit_name="filter2_lineEdit",
        list_widget_name="filter2_listWidget",
        button_name="filter2_pushButton",
        tag_key="filter2",
        enabled=True
    ),
    # ... més filtres ...
]
```

#### 3.1 Activar o desactivar filtres

Per **desactivar** un filtre, canvia `enabled=True` a `enabled=False`:
```python
FilterConfig(
    column_index=STOCK,
    # ... altres paràmetres ...
    enabled=False  # Aquest filtre estarà ocult
),
```

#### 3.2 Afegir un nou filtre

Per afegir un nou filtre:

1. **Afegeix els widgets a la interfície** (`ui_main.ui` amb Qt Designer):
   - Un `QLabel` (ex: `filter5_label`)
   - Un `QLineEdit` (ex: `filter5_lineEdit`)
   - Un `QListWidget` (ex: `filter5_listWidget`)
   - Un `QPushButton` (ex: `filter5_pushButton`)

2. **Afegeix la configuració** a `FILTERS_CONFIG`:
```python
   FilterConfig(
       column_index=DESCRIPTION,  # Filtra per descripció
       label_widget_name="filter5_label",
       line_edit_name="filter5_lineEdit",
       list_widget_name="filter5_listWidget",
       button_name="filter5_pushButton",
       tag_key="filter5",
       enabled=True
   ),
```

---

### 4. 🎨 Recursos gràfics (icones)

El projecte utilitza un fitxer de recursos Qt per a les icones:
```python
import recursos_grafics_rc
```

#### 4.1 Regenerar el fitxer de recursos

Si modifiques el fitxer `recursos_grafics.qrc`, regenera el fitxer Python:
```bash
pyside6-rcc recursos_grafics.qrc -o recursos_grafics_rc.py
```

---

### 5. ✅ Verificació de la configuració

Abans d'executar l'aplicació, verifica:

- [ ] El fitxer de credencials JSON està a `credentials/`
- [ ] El Google Sheet està compartit amb el service account
- [ ] El service account té permisos d'**Editor**
- [ ] El `GOOGLE_SHEET_ID` és correcte
- [ ] Els índexs de columnes coincideixen amb el teu Google Sheet
- [ ] La carpeta `credentials/` està al `.gitignore`

---

### 6. 🐛 Solució de problemes

#### Error: "Google Sheet no trobat o sense accés"

**Causa**: El service account no té accés al Google Sheet

**Solució**:
1. Obre el Google Sheet
2. Verifica que l'email del service account està a la llista de persones amb accés
3. Assegura't que té permisos d'**Editor** (no només Lector)

#### Error: "No existeix el fitxer: credentials/..."

**Causa**: El fitxer de credencials no està a la ubicació correcta

**Solució**:
1. Verifica que el fitxer JSON està dins la carpeta `credentials/`
2. Comprova que el nom del fitxer coincideix amb `GOOGLE_CREDENTIALS_JSON` a `Config`

#### Error: "El fitxer JSON no és vàlid"

**Causa**: El fitxer de credencials està corrupte o és incorrecte

**Solució**:
1. Torna a descarregar el fitxer JSON de Google Cloud Console
2. Verifica que és un fitxer JSON vàlid (obre'l amb un editor de text)

#### Els filtres no es mostren o estan desactivats

**Causa**: El filtre està marcat com `enabled=False` a la configuració

**Solució**:
1. Obre `main.py`
2. Cerca `FILTERS_CONFIG` dins la classe `Config`
3. Canvia `enabled=False` a `enabled=True` per al filtre desitjat