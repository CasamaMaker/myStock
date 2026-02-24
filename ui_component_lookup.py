# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_component_lookup.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(717, 559)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 0, 681, 161))
        self.root_verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.root_verticalLayout.setObjectName(u"root_verticalLayout")
        self.root_verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_title = QLabel(self.verticalLayoutWidget)
        self.label_title.setObjectName(u"label_title")

        self.root_verticalLayout.addWidget(self.label_title)

        self.label_subtitle = QLabel(self.verticalLayoutWidget)
        self.label_subtitle.setObjectName(u"label_subtitle")

        self.root_verticalLayout.addWidget(self.label_subtitle)

        self.horizontalLayout_search_row = QHBoxLayout()
        self.horizontalLayout_search_row.setObjectName(u"horizontalLayout_search_row")
        self.lineEdit_search_box = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_search_box.setObjectName(u"lineEdit_search_box")

        self.horizontalLayout_search_row.addWidget(self.lineEdit_search_box)

        self.pushButton_search_button = QPushButton(self.verticalLayoutWidget)
        self.pushButton_search_button.setObjectName(u"pushButton_search_button")

        self.horizontalLayout_search_row.addWidget(self.pushButton_search_button)


        self.root_verticalLayout.addLayout(self.horizontalLayout_search_row)

        self.label_help = QLabel(self.verticalLayoutWidget)
        self.label_help.setObjectName(u"label_help")

        self.root_verticalLayout.addWidget(self.label_help)

        self.label_status = QLabel(self.verticalLayoutWidget)
        self.label_status.setObjectName(u"label_status")

        self.root_verticalLayout.addWidget(self.label_status)

        self.widget_result = QWidget(self.centralwidget)
        self.widget_result.setObjectName(u"widget_result")
        self.widget_result.setGeometry(QRect(20, 170, 681, 291))
        self.verticalLayoutWidget_2 = QWidget(self.widget_result)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(-1, -1, 681, 291))
        self.verticalLayout_result = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_result.setObjectName(u"verticalLayout_result")
        self.verticalLayout_result.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget_imatge = QWidget(self.verticalLayoutWidget_2)
        self.widget_imatge.setObjectName(u"widget_imatge")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_imatge.sizePolicy().hasHeightForWidth())
        self.widget_imatge.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.widget_imatge)

        self.verticalLayout_info = QVBoxLayout()
        self.verticalLayout_info.setObjectName(u"verticalLayout_info")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_nomcompoennt = QLabel(self.verticalLayoutWidget_2)
        self.label_nomcompoennt.setObjectName(u"label_nomcompoennt")

        self.horizontalLayout_2.addWidget(self.label_nomcompoennt)

        self.label_tagSupplier = QLabel(self.verticalLayoutWidget_2)
        self.label_tagSupplier.setObjectName(u"label_tagSupplier")

        self.horizontalLayout_2.addWidget(self.label_tagSupplier)

        self.label_tagAvailability = QLabel(self.verticalLayoutWidget_2)
        self.label_tagAvailability.setObjectName(u"label_tagAvailability")

        self.horizontalLayout_2.addWidget(self.label_tagAvailability)


        self.verticalLayout_info.addLayout(self.horizontalLayout_2)

        self.label_description = QLabel(self.verticalLayoutWidget_2)
        self.label_description.setObjectName(u"label_description")

        self.verticalLayout_info.addWidget(self.label_description)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.verticalLayout_info.addItem(self.verticalSpacer)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_storetext = QLabel(self.verticalLayoutWidget_2)
        self.label_storetext.setObjectName(u"label_storetext")

        self.horizontalLayout_3.addWidget(self.label_storetext)

        self.label_storevariable = QLabel(self.verticalLayoutWidget_2)
        self.label_storevariable.setObjectName(u"label_storevariable")

        self.horizontalLayout_3.addWidget(self.label_storevariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_tipostext = QLabel(self.verticalLayoutWidget_2)
        self.label_tipostext.setObjectName(u"label_tipostext")

        self.horizontalLayout_5.addWidget(self.label_tipostext)

        self.label_tiposvariable = QLabel(self.verticalLayoutWidget_2)
        self.label_tiposvariable.setObjectName(u"label_tiposvariable")

        self.horizontalLayout_5.addWidget(self.label_tiposvariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_fabricanttext = QLabel(self.verticalLayoutWidget_2)
        self.label_fabricanttext.setObjectName(u"label_fabricanttext")

        self.horizontalLayout_6.addWidget(self.label_fabricanttext)

        self.label_fabricantvariable = QLabel(self.verticalLayoutWidget_2)
        self.label_fabricantvariable.setObjectName(u"label_fabricantvariable")

        self.horizontalLayout_6.addWidget(self.label_fabricantvariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_packagetext = QLabel(self.verticalLayoutWidget_2)
        self.label_packagetext.setObjectName(u"label_packagetext")

        self.horizontalLayout_8.addWidget(self.label_packagetext)

        self.label_packagevariable = QLabel(self.verticalLayoutWidget_2)
        self.label_packagevariable.setObjectName(u"label_packagevariable")

        self.horizontalLayout_8.addWidget(self.label_packagevariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_pricetext = QLabel(self.verticalLayoutWidget_2)
        self.label_pricetext.setObjectName(u"label_pricetext")

        self.horizontalLayout_9.addWidget(self.label_pricetext)

        self.widget_priceContainer = QWidget(self.verticalLayoutWidget_2)
        self.widget_priceContainer.setObjectName(u"widget_priceContainer")

        self.horizontalLayout_9.addWidget(self.widget_priceContainer)


        self.verticalLayout_info.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_botigalink = QLabel(self.verticalLayoutWidget_2)
        self.label_botigalink.setObjectName(u"label_botigalink")

        self.horizontalLayout_7.addWidget(self.label_botigalink)

        self.label_datasheetlink = QLabel(self.verticalLayoutWidget_2)
        self.label_datasheetlink.setObjectName(u"label_datasheetlink")

        self.horizontalLayout_7.addWidget(self.label_datasheetlink)


        self.verticalLayout_info.addLayout(self.horizontalLayout_7)


        self.horizontalLayout.addLayout(self.verticalLayout_info)


        self.verticalLayout_result.addLayout(self.horizontalLayout)

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 470, 681, 22))
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_stocktext = QLabel(self.horizontalLayoutWidget)
        self.label_stocktext.setObjectName(u"label_stocktext")

        self.horizontalLayout_4.addWidget(self.label_stocktext)

        self.lineEdit = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_4.addWidget(self.lineEdit)

        self.label_storagetext = QLabel(self.horizontalLayoutWidget)
        self.label_storagetext.setObjectName(u"label_storagetext")

        self.horizontalLayout_4.addWidget(self.label_storagetext)

        self.lineEdit_storagevariable = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_storagevariable.setObjectName(u"lineEdit_storagevariable")

        self.horizontalLayout_4.addWidget(self.lineEdit_storagevariable)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 717, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow", u"Component llockup", None))
        self.label_subtitle.setText(QCoreApplication.translate("MainWindow", u"Subtitol", None))
        self.pushButton_search_button.setText(QCoreApplication.translate("MainWindow", u"Cerca", None))
        self.label_help.setText(QCoreApplication.translate("MainWindow", u"help_lbl", None))
        self.label_status.setText(QCoreApplication.translate("MainWindow", u"status_label", None))
        self.label_nomcompoennt.setText(QCoreApplication.translate("MainWindow", u"nom component", None))
        self.label_tagSupplier.setText(QCoreApplication.translate("MainWindow", u"tag supplier", None))
        self.label_tagAvailability.setText(QCoreApplication.translate("MainWindow", u"tag availability", None))
        self.label_description.setText(QCoreApplication.translate("MainWindow", u"description", None))
        self.label_storetext.setText(QCoreApplication.translate("MainWindow", u"Store name", None))
        self.label_storevariable.setText(QCoreApplication.translate("MainWindow", u"C15674652", None))
        self.label_tipostext.setText(QCoreApplication.translate("MainWindow", u"Tipus", None))
        self.label_tiposvariable.setText(QCoreApplication.translate("MainWindow", u"Zeneer diode", None))
        self.label_fabricanttext.setText(QCoreApplication.translate("MainWindow", u"Fabricant", None))
        self.label_fabricantvariable.setText(QCoreApplication.translate("MainWindow", u"onsemi", None))
        self.label_packagetext.setText(QCoreApplication.translate("MainWindow", u"Package", None))
        self.label_packagevariable.setText(QCoreApplication.translate("MainWindow", u"SOD-23", None))
        self.label_pricetext.setText(QCoreApplication.translate("MainWindow", u"Preus", None))
        self.label_botigalink.setText(QCoreApplication.translate("MainWindow", u"Botiga", None))
        self.label_datasheetlink.setText(QCoreApplication.translate("MainWindow", u"Datasheet", None))
        self.label_stocktext.setText(QCoreApplication.translate("MainWindow", u"stock-text", None))
        self.lineEdit.setText(QCoreApplication.translate("MainWindow", u"stock-variable", None))
        self.label_storagetext.setText(QCoreApplication.translate("MainWindow", u"storage-variable", None))
        self.lineEdit_storagevariable.setText(QCoreApplication.translate("MainWindow", u"stock-variable", None))
    # retranslateUi

