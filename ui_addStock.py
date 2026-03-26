# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_addStock.ui'
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(567, 424)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.pushButton_previous = QPushButton(self.centralwidget)
        self.pushButton_previous.setObjectName(u"pushButton_previous")
        self.pushButton_previous.setGeometry(QRect(50, 300, 75, 23))
        self.pushButton_safe = QPushButton(self.centralwidget)
        self.pushButton_safe.setObjectName(u"pushButton_safe")
        self.pushButton_safe.setGeometry(QRect(230, 300, 75, 23))
        self.pushButton_next = QPushButton(self.centralwidget)
        self.pushButton_next.setObjectName(u"pushButton_next")
        self.pushButton_next.setGeometry(QRect(340, 300, 75, 23))
        self.pushButton_Nou = QPushButton(self.centralwidget)
        self.pushButton_Nou.setObjectName(u"pushButton_Nou")
        self.pushButton_Nou.setGeometry(QRect(140, 300, 75, 23))
        self.lineEdit_Id = QLineEdit(self.centralwidget)
        self.lineEdit_Id.setObjectName(u"lineEdit_Id")
        self.lineEdit_Id.setGeometry(QRect(30, 30, 113, 20))
        self.lineEdit_ManufacturerPN = QLineEdit(self.centralwidget)
        self.lineEdit_ManufacturerPN.setObjectName(u"lineEdit_ManufacturerPN")
        self.lineEdit_ManufacturerPN.setGeometry(QRect(160, 30, 113, 20))
        self.lineEdit_Manufacturer = QLineEdit(self.centralwidget)
        self.lineEdit_Manufacturer.setObjectName(u"lineEdit_Manufacturer")
        self.lineEdit_Manufacturer.setGeometry(QRect(280, 30, 113, 20))
        self.lineEdit_Category = QLineEdit(self.centralwidget)
        self.lineEdit_Category.setObjectName(u"lineEdit_Category")
        self.lineEdit_Category.setGeometry(QRect(400, 30, 113, 20))
        self.lineEdit_Description = QLineEdit(self.centralwidget)
        self.lineEdit_Description.setObjectName(u"lineEdit_Description")
        self.lineEdit_Description.setGeometry(QRect(30, 60, 481, 20))
        self.lineEdit_Supplier = QLineEdit(self.centralwidget)
        self.lineEdit_Supplier.setObjectName(u"lineEdit_Supplier")
        self.lineEdit_Supplier.setGeometry(QRect(50, 90, 113, 20))
        self.lineEdit_SupplierPN = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierPN.setObjectName(u"lineEdit_SupplierPN")
        self.lineEdit_SupplierPN.setGeometry(QRect(180, 90, 113, 20))
        self.lineEdit_SupplierCategory = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierCategory.setObjectName(u"lineEdit_SupplierCategory")
        self.lineEdit_SupplierCategory.setGeometry(QRect(300, 90, 113, 20))
        self.lineEdit_Datasheet = QLineEdit(self.centralwidget)
        self.lineEdit_Datasheet.setObjectName(u"lineEdit_Datasheet")
        self.lineEdit_Datasheet.setGeometry(QRect(22, 120, 231, 20))
        self.lineEdit_SupplierLink = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierLink.setObjectName(u"lineEdit_SupplierLink")
        self.lineEdit_SupplierLink.setGeometry(QRect(270, 120, 261, 20))
        self.lineEdit_Package = QLineEdit(self.centralwidget)
        self.lineEdit_Package.setObjectName(u"lineEdit_Package")
        self.lineEdit_Package.setGeometry(QRect(40, 150, 113, 20))
        self.lineEdit_Stock = QLineEdit(self.centralwidget)
        self.lineEdit_Stock.setObjectName(u"lineEdit_Stock")
        self.lineEdit_Stock.setGeometry(QRect(170, 150, 113, 20))
        self.lineEdit_Storage = QLineEdit(self.centralwidget)
        self.lineEdit_Storage.setObjectName(u"lineEdit_Storage")
        self.lineEdit_Storage.setGeometry(QRect(290, 150, 113, 20))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 567, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_previous.setText(QCoreApplication.translate("MainWindow", u"Previous", None))
        self.pushButton_safe.setText(QCoreApplication.translate("MainWindow", u"Safe", None))
        self.pushButton_next.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.pushButton_Nou.setText(QCoreApplication.translate("MainWindow", u"Nou", None))
    # retranslateUi

