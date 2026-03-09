# document name: ui_component_lookup.py
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_component_lookup.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
        MainWindow.resize(550, 441)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 0, 531, 51))
        self.root_verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.root_verticalLayout.setObjectName(u"root_verticalLayout")
        self.root_verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_search_row = QHBoxLayout()
        self.horizontalLayout_search_row.setObjectName(u"horizontalLayout_search_row")
        self.lineEdit_search_box = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_search_box.setObjectName(u"lineEdit_search_box")

        self.horizontalLayout_search_row.addWidget(self.lineEdit_search_box)

        self.pushButton_search_button = QPushButton(self.verticalLayoutWidget)
        self.pushButton_search_button.setObjectName(u"pushButton_search_button")

        self.horizontalLayout_search_row.addWidget(self.pushButton_search_button)


        self.root_verticalLayout.addLayout(self.horizontalLayout_search_row)

        self.widget_result = QWidget(self.centralwidget)
        self.widget_result.setObjectName(u"widget_result")
        self.widget_result.setGeometry(QRect(10, 60, 531, 291))
        self.layoutWidget = QWidget(self.widget_result)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 511, 275))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.widget_imatge = QWidget(self.layoutWidget)
        self.widget_imatge.setObjectName(u"widget_imatge")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_imatge.sizePolicy().hasHeightForWidth())
        self.widget_imatge.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.widget_imatge)

        self.verticalLayout_info = QVBoxLayout()
        self.verticalLayout_info.setObjectName(u"verticalLayout_info")
        self.verticalLayout_info.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_nomcompoennt = QLabel(self.layoutWidget)
        self.label_nomcompoennt.setObjectName(u"label_nomcompoennt")

        self.horizontalLayout_2.addWidget(self.label_nomcompoennt)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_tagSupplier = QLabel(self.layoutWidget)
        self.label_tagSupplier.setObjectName(u"label_tagSupplier")

        self.horizontalLayout_2.addWidget(self.label_tagSupplier)

        self.label_tagAvailability = QLabel(self.layoutWidget)
        self.label_tagAvailability.setObjectName(u"label_tagAvailability")

        self.horizontalLayout_2.addWidget(self.label_tagAvailability)


        self.verticalLayout_info.addLayout(self.horizontalLayout_2)

        self.label_description = QLabel(self.layoutWidget)
        self.label_description.setObjectName(u"label_description")

        self.verticalLayout_info.addWidget(self.label_description)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_info.addItem(self.verticalSpacer)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_storetext = QLabel(self.layoutWidget)
        self.label_storetext.setObjectName(u"label_storetext")

        self.horizontalLayout_3.addWidget(self.label_storetext)

        self.label_storevariable = QLabel(self.layoutWidget)
        self.label_storevariable.setObjectName(u"label_storevariable")

        self.horizontalLayout_3.addWidget(self.label_storevariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_tipostext = QLabel(self.layoutWidget)
        self.label_tipostext.setObjectName(u"label_tipostext")

        self.horizontalLayout_5.addWidget(self.label_tipostext)

        self.label_tiposvariable = QLabel(self.layoutWidget)
        self.label_tiposvariable.setObjectName(u"label_tiposvariable")

        self.horizontalLayout_5.addWidget(self.label_tiposvariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_fabricanttext = QLabel(self.layoutWidget)
        self.label_fabricanttext.setObjectName(u"label_fabricanttext")

        self.horizontalLayout_6.addWidget(self.label_fabricanttext)

        self.label_fabricantvariable = QLabel(self.layoutWidget)
        self.label_fabricantvariable.setObjectName(u"label_fabricantvariable")

        self.horizontalLayout_6.addWidget(self.label_fabricantvariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_packagetext = QLabel(self.layoutWidget)
        self.label_packagetext.setObjectName(u"label_packagetext")

        self.horizontalLayout_8.addWidget(self.label_packagetext)

        self.label_packagevariable = QLabel(self.layoutWidget)
        self.label_packagevariable.setObjectName(u"label_packagevariable")

        self.horizontalLayout_8.addWidget(self.label_packagevariable)


        self.verticalLayout_info.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_pricetext = QLabel(self.layoutWidget)
        self.label_pricetext.setObjectName(u"label_pricetext")

        self.horizontalLayout_9.addWidget(self.label_pricetext)

        self.widget_priceContainer = QWidget(self.layoutWidget)
        self.widget_priceContainer.setObjectName(u"widget_priceContainer")

        self.horizontalLayout_9.addWidget(self.widget_priceContainer)


        self.verticalLayout_info.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_botigalink = QLabel(self.layoutWidget)
        self.label_botigalink.setObjectName(u"label_botigalink")

        self.horizontalLayout_7.addWidget(self.label_botigalink)

        self.label_datasheetlink = QLabel(self.layoutWidget)
        self.label_datasheetlink.setObjectName(u"label_datasheetlink")

        self.horizontalLayout_7.addWidget(self.label_datasheetlink)


        self.verticalLayout_info.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_stocktext = QLabel(self.layoutWidget)
        self.label_stocktext.setObjectName(u"label_stocktext")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_stocktext.sizePolicy().hasHeightForWidth())
        self.label_stocktext.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.label_stocktext)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.lineEdit)

        self.label_storagetext = QLabel(self.layoutWidget)
        self.label_storagetext.setObjectName(u"label_storagetext")
        sizePolicy1.setHeightForWidth(self.label_storagetext.sizePolicy().hasHeightForWidth())
        self.label_storagetext.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.label_storagetext)

        self.lineEdit_storagevariable = QLineEdit(self.layoutWidget)
        self.lineEdit_storagevariable.setObjectName(u"lineEdit_storagevariable")
        sizePolicy2.setHeightForWidth(self.lineEdit_storagevariable.sizePolicy().hasHeightForWidth())
        self.lineEdit_storagevariable.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.lineEdit_storagevariable)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)


        self.verticalLayout_info.addLayout(self.horizontalLayout_4)


        self.horizontalLayout.addLayout(self.verticalLayout_info)

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 350, 521, 28))
        self.horizontalLayout_10 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.pushButton = QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_10.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_10.addWidget(self.pushButton_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 550, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_search_button.setText(QCoreApplication.translate("MainWindow", u"Cerca", None))
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
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi

