# # -*- coding: utf-8 -*-
# # ui_bom.py
# # Definició de la interfície del gestor de BoM.
# # Escrit manualment seguint el mateix patró que els fitxers generats
# # per Qt Designer del projecte (ui_component_lookup.py, etc.)

# from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
# from PySide6.QtWidgets import (
#     QApplication, QComboBox, QFrame, QGroupBox, QHBoxLayout,
#     QLabel, QLineEdit, QMainWindow, QMenuBar, QProgressBar,
#     QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
#     QTableWidget, QVBoxLayout, QWidget,
# )


# class Ui_BomWindow(object):
#     def setupUi(self, BomWindow):
#         if not BomWindow.objectName():
#             BomWindow.setObjectName("BomWindow")
#         BomWindow.resize(1120, 700)
#         BomWindow.setMinimumSize(800, 500)

#         self.centralwidget = QWidget(BomWindow)
#         self.centralwidget.setObjectName("centralwidget")

#         # ── Root layout ───────────────────────────────────────────────────────
#         self.root_layout = QVBoxLayout(self.centralwidget)
#         self.root_layout.setObjectName("root_layout")
#         self.root_layout.setContentsMargins(10, 10, 10, 6)
#         self.root_layout.setSpacing(6)

#         # ── Grup: selector de fitxer ─────────────────────────────────────────
#         self.grp_file = QGroupBox(self.centralwidget)
#         self.grp_file.setObjectName("grp_file")
#         self.grp_file_layout = QHBoxLayout(self.grp_file)
#         self.grp_file_layout.setObjectName("grp_file_layout")
#         self.grp_file_layout.setContentsMargins(8, 6, 8, 6)
#         self.grp_file_layout.setSpacing(6)

#         self.lbl_file = QLabel(self.grp_file)
#         self.lbl_file.setObjectName("lbl_file")
#         self.grp_file_layout.addWidget(self.lbl_file)

#         self.lineEdit_bom_path = QLineEdit(self.grp_file)
#         self.lineEdit_bom_path.setObjectName("lineEdit_bom_path")
#         self.grp_file_layout.addWidget(self.lineEdit_bom_path)

#         self.btn_browse = QPushButton(self.grp_file)
#         self.btn_browse.setObjectName("btn_browse")
#         self.btn_browse.setFixedWidth(80)
#         self.grp_file_layout.addWidget(self.btn_browse)

#         self.btn_load = QPushButton(self.grp_file)
#         self.btn_load.setObjectName("btn_load")
#         self.btn_load.setFixedWidth(100)
#         self.grp_file_layout.addWidget(self.btn_load)

#         self.root_layout.addWidget(self.grp_file)

#         # ── Grup: resum / estadístiques ──────────────────────────────────────
#         self.grp_stats = QGroupBox(self.centralwidget)
#         self.grp_stats.setObjectName("grp_stats")
#         self.grp_stats_layout = QHBoxLayout(self.grp_stats)
#         self.grp_stats_layout.setObjectName("grp_stats_layout")
#         self.grp_stats_layout.setContentsMargins(10, 6, 10, 6)
#         self.grp_stats_layout.setSpacing(0)

#         self.lbl_total = QLabel(self.grp_stats)
#         self.lbl_total.setObjectName("lbl_total")
#         self.grp_stats_layout.addWidget(self.lbl_total)

#         self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

#         self.lbl_ok = QLabel(self.grp_stats)
#         self.lbl_ok.setObjectName("lbl_ok")
#         self.grp_stats_layout.addWidget(self.lbl_ok)

#         self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

#         self.lbl_parcial = QLabel(self.grp_stats)
#         self.lbl_parcial.setObjectName("lbl_parcial")
#         self.grp_stats_layout.addWidget(self.lbl_parcial)

#         self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

#         self.lbl_falta = QLabel(self.grp_stats)
#         self.lbl_falta.setObjectName("lbl_falta")
#         self.grp_stats_layout.addWidget(self.lbl_falta)

#         self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

#         self.lbl_no_trobat = QLabel(self.grp_stats)
#         self.lbl_no_trobat.setObjectName("lbl_no_trobat")
#         self.grp_stats_layout.addWidget(self.lbl_no_trobat)

#         self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

#         self.lbl_dnp = QLabel(self.grp_stats)
#         self.lbl_dnp.setObjectName("lbl_dnp")
#         self.grp_stats_layout.addWidget(self.lbl_dnp)

#         self.grp_stats_layout.addStretch()

#         self.root_layout.addWidget(self.grp_stats)

#         # ── Barra d'accions: filtre + botons ─────────────────────────────────
#         self.action_layout = QHBoxLayout()
#         self.action_layout.setObjectName("action_layout")
#         self.action_layout.setSpacing(8)

#         self.lbl_filter = QLabel(self.centralwidget)
#         self.lbl_filter.setObjectName("lbl_filter")
#         self.action_layout.addWidget(self.lbl_filter)

#         self.combo_filter = QComboBox(self.centralwidget)
#         self.combo_filter.setObjectName("combo_filter")
#         self.combo_filter.setFixedWidth(200)
#         self.action_layout.addWidget(self.combo_filter)

#         self.action_layout.addItem(
#             QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#         )

#         self.btn_consume_all = QPushButton(self.centralwidget)
#         self.btn_consume_all.setObjectName("btn_consume_all")
#         self.btn_consume_all.setEnabled(False)
#         self.action_layout.addWidget(self.btn_consume_all)

#         self.root_layout.addLayout(self.action_layout)

#         # ── Taula de components ───────────────────────────────────────────────
#         self.tableWidget = QTableWidget(self.centralwidget)
#         self.tableWidget.setObjectName("tableWidget")
#         self.root_layout.addWidget(self.tableWidget, 1)

#         # ── Barra de progrés ─────────────────────────────────────────────────
#         self.progress_bar = QProgressBar(self.centralwidget)
#         self.progress_bar.setObjectName("progress_bar")
#         self.progress_bar.setValue(0)
#         self.progress_bar.setFixedHeight(5)
#         self.progress_bar.setTextVisible(False)
#         self.root_layout.addWidget(self.progress_bar)

#         # ── Chrome de la finestra ─────────────────────────────────────────────
#         BomWindow.setCentralWidget(self.centralwidget)

#         self.menubar = QMenuBar(BomWindow)
#         self.menubar.setObjectName("menubar")
#         BomWindow.setMenuBar(self.menubar)

#         self.statusbar = QStatusBar(BomWindow)
#         self.statusbar.setObjectName("statusbar")
#         BomWindow.setStatusBar(self.statusbar)

#         self.retranslateUi(BomWindow)
#         QMetaObject.connectSlotsByName(BomWindow)

#     # ── Separador visual vertical ────────────────────────────────────────────
#     @staticmethod
#     def _vsep(parent):
#         sep = QFrame(parent)
#         sep.setFrameShape(QFrame.VLine)
#         sep.setFrameShadow(QFrame.Sunken)
#         sep.setFixedWidth(16)
#         sep.setStyleSheet("color: #d0d0d0;")
#         return sep

#     def retranslateUi(self, BomWindow):
#         _tr = QCoreApplication.translate
#         BomWindow.setWindowTitle(_tr("BomWindow", "BoM — Bill of Materials", None))

#         self.grp_file.setTitle(_tr("BomWindow", "Fitxer BoM (KiCad CSV)", None))
#         self.lbl_file.setText(_tr("BomWindow", "Fitxer:", None))
#         self.lineEdit_bom_path.setPlaceholderText(
#             _tr("BomWindow", "Selecciona el fitxer BoM exportat de KiCad (.csv)…", None)
#         )
#         self.btn_browse.setText(_tr("BomWindow", "Cerca…", None))
#         self.btn_load.setText(_tr("BomWindow", "Carregar", None))

#         self.grp_stats.setTitle(_tr("BomWindow", "Resum", None))
#         self.lbl_total.setText(_tr("BomWindow", "Total: —", None))
#         self.lbl_ok.setText(_tr("BomWindow", "✓  OK: —", None))
#         self.lbl_parcial.setText(_tr("BomWindow", "⚠  Parcial: —", None))
#         self.lbl_falta.setText(_tr("BomWindow", "✗  Falta: —", None))
#         self.lbl_no_trobat.setText(_tr("BomWindow", "?  No trobat: —", None))
#         self.lbl_dnp.setText(_tr("BomWindow", "DNP: —", None))

#         self.lbl_filter.setText(_tr("BomWindow", "Filtre:", None))
#         self.btn_consume_all.setText(_tr("BomWindow", "Consumir tot l'estoc", None))









































# -*- coding: utf-8 -*-
# ui_bom.py
# Definició de la interfície del gestor de BoM.
# Escrit manualment seguint el mateix patró que els fitxers generats
# per Qt Designer del projecte (ui_component_lookup.py, etc.)

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTableWidget, QVBoxLayout, QWidget,
)


class Ui_BomWindow(object):
    def setupUi(self, BomWindow):
        if not BomWindow.objectName():
            BomWindow.setObjectName("BomWindow")
        BomWindow.resize(1200, 720)
        BomWindow.setMinimumSize(860, 520)

        self.centralwidget = QWidget(BomWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ── Root layout ───────────────────────────────────────────────────────
        self.root_layout = QVBoxLayout(self.centralwidget)
        self.root_layout.setObjectName("root_layout")
        self.root_layout.setContentsMargins(10, 10, 10, 6)
        self.root_layout.setSpacing(6)

        # ── Grup: selector de fitxer ─────────────────────────────────────────
        self.grp_file = QGroupBox(self.centralwidget)
        self.grp_file.setObjectName("grp_file")
        self.grp_file_layout = QHBoxLayout(self.grp_file)
        self.grp_file_layout.setContentsMargins(8, 6, 8, 6)
        self.grp_file_layout.setSpacing(6)

        self.lbl_file = QLabel(self.grp_file)
        self.lbl_file.setObjectName("lbl_file")
        self.grp_file_layout.addWidget(self.lbl_file)

        self.lineEdit_bom_path = QLineEdit(self.grp_file)
        self.lineEdit_bom_path.setObjectName("lineEdit_bom_path")
        self.grp_file_layout.addWidget(self.lineEdit_bom_path)

        self.btn_browse = QPushButton(self.grp_file)
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setFixedWidth(80)
        self.grp_file_layout.addWidget(self.btn_browse)

        self.btn_load = QPushButton(self.grp_file)
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setFixedWidth(100)
        self.grp_file_layout.addWidget(self.btn_load)

        self.root_layout.addWidget(self.grp_file)

        # ── Grup: resum / estadístiques ──────────────────────────────────────
        self.grp_stats = QGroupBox(self.centralwidget)
        self.grp_stats.setObjectName("grp_stats")
        self.grp_stats_layout = QHBoxLayout(self.grp_stats)
        self.grp_stats_layout.setContentsMargins(10, 5, 10, 5)
        self.grp_stats_layout.setSpacing(0)

        self.lbl_total = QLabel(self.grp_stats)
        self.lbl_total.setObjectName("lbl_total")
        self.grp_stats_layout.addWidget(self.lbl_total)

        self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

        self.lbl_ok = QLabel(self.grp_stats)
        self.lbl_ok.setObjectName("lbl_ok")
        self.grp_stats_layout.addWidget(self.lbl_ok)

        self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

        self.lbl_parcial = QLabel(self.grp_stats)
        self.lbl_parcial.setObjectName("lbl_parcial")
        self.grp_stats_layout.addWidget(self.lbl_parcial)

        self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

        self.lbl_falta = QLabel(self.grp_stats)
        self.lbl_falta.setObjectName("lbl_falta")
        self.grp_stats_layout.addWidget(self.lbl_falta)

        self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

        self.lbl_no_trobat = QLabel(self.grp_stats)
        self.lbl_no_trobat.setObjectName("lbl_no_trobat")
        self.grp_stats_layout.addWidget(self.lbl_no_trobat)

        self.grp_stats_layout.addWidget(self._vsep(self.grp_stats))

        self.lbl_dnp = QLabel(self.grp_stats)
        self.lbl_dnp.setObjectName("lbl_dnp")
        self.grp_stats_layout.addWidget(self.lbl_dnp)

        self.grp_stats_layout.addStretch()
        self.root_layout.addWidget(self.grp_stats)

        # ── Barra d'accions: filtre | selecció | consum ───────────────────────
        self.action_layout = QHBoxLayout()
        self.action_layout.setSpacing(6)

        # Filtre per estat
        self.lbl_filter = QLabel(self.centralwidget)
        self.lbl_filter.setObjectName("lbl_filter")
        self.action_layout.addWidget(self.lbl_filter)

        self.combo_filter = QComboBox(self.centralwidget)
        self.combo_filter.setObjectName("combo_filter")
        self.combo_filter.setFixedWidth(210)
        self.action_layout.addWidget(self.combo_filter)

        self.action_layout.addWidget(self._vsep(self.centralwidget))

        # Botons de selecció de checkboxes
        self.btn_select_all = QPushButton(self.centralwidget)
        self.btn_select_all.setObjectName("btn_select_all")
        self.btn_select_all.setFixedWidth(126)
        self.btn_select_all.setEnabled(False)
        self.action_layout.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton(self.centralwidget)
        self.btn_deselect_all.setObjectName("btn_deselect_all")
        self.btn_deselect_all.setFixedWidth(126)
        self.btn_deselect_all.setEnabled(False)
        self.action_layout.addWidget(self.btn_deselect_all)

        # Espaiat flexible
        self.action_layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        # Comptador dinàmic de seleccionats
        self.lbl_selected_count = QLabel(self.centralwidget)
        self.lbl_selected_count.setObjectName("lbl_selected_count")
        self.action_layout.addWidget(self.lbl_selected_count)

        # Botó principal de consum
        self.btn_consume_selected = QPushButton(self.centralwidget)
        self.btn_consume_selected.setObjectName("btn_consume_selected")
        self.btn_consume_selected.setEnabled(False)
        self.btn_consume_selected.setFixedWidth(190)
        self.action_layout.addWidget(self.btn_consume_selected)

        self.root_layout.addLayout(self.action_layout)

        # ── Taula de components ───────────────────────────────────────────────
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.root_layout.addWidget(self.tableWidget, 1)

        # ── Barra de progrés ─────────────────────────────────────────────────
        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.root_layout.addWidget(self.progress_bar)

        # ── Chrome de la finestra ─────────────────────────────────────────────
        BomWindow.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(BomWindow)
        self.menubar.setObjectName("menubar")
        BomWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(BomWindow)
        self.statusbar.setObjectName("statusbar")
        BomWindow.setStatusBar(self.statusbar)

        self.retranslateUi(BomWindow)
        QMetaObject.connectSlotsByName(BomWindow)

    # ── Helpers de layout ─────────────────────────────────────────────────────
    @staticmethod
    def _vsep(parent):
        sep = QFrame(parent)
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setFixedWidth(14)
        sep.setStyleSheet("color: #d0d0d0;")
        return sep

    def retranslateUi(self, BomWindow):
        _tr = QCoreApplication.translate
        BomWindow.setWindowTitle(_tr("BomWindow", "BoM — Bill of Materials", None))

        self.grp_file.setTitle(_tr("BomWindow", "Fitxer BoM (KiCad CSV)", None))
        self.lbl_file.setText(_tr("BomWindow", "Fitxer:", None))
        self.lineEdit_bom_path.setPlaceholderText(
            _tr("BomWindow", "Selecciona el fitxer BoM exportat de KiCad (.csv)…", None)
        )
        self.btn_browse.setText(_tr("BomWindow", "Cerca…", None))
        self.btn_load.setText(_tr("BomWindow", "Carregar", None))

        self.grp_stats.setTitle(_tr("BomWindow", "Resum", None))
        self.lbl_total.setText(_tr("BomWindow", "Total: —", None))
        self.lbl_ok.setText(_tr("BomWindow", "✓  OK: —", None))
        self.lbl_parcial.setText(_tr("BomWindow", "⚠  Parcial: —", None))
        self.lbl_falta.setText(_tr("BomWindow", "✗  Falta: —", None))
        self.lbl_no_trobat.setText(_tr("BomWindow", "?  No trobat: —", None))
        self.lbl_dnp.setText(_tr("BomWindow", "—  DNP: —", None))

        self.lbl_filter.setText(_tr("BomWindow", "Filtre:", None))
        self.btn_select_all.setText(_tr("BomWindow", "☑  Seleccionar tots", None))
        self.btn_deselect_all.setText(_tr("BomWindow", "☐  Desseleccionar", None))
        self.lbl_selected_count.setText("")
        self.btn_consume_selected.setText(
            _tr("BomWindow", "▼  Restar seleccionats", None)
        )