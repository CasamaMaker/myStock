# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_addStock.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTextEdit, QVBoxLayout,
    QWidget)
import recursos_grafics_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(561, 431)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout_15 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout.addWidget(self.label)

        self.lineEdit_Id = QLineEdit(self.centralwidget)
        self.lineEdit_Id.setObjectName(u"lineEdit_Id")
        sizePolicy.setHeightForWidth(self.lineEdit_Id.sizePolicy().hasHeightForWidth())
        self.lineEdit_Id.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.lineEdit_Id)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.lineEdit_ManufacturerPN = QLineEdit(self.centralwidget)
        self.lineEdit_ManufacturerPN.setObjectName(u"lineEdit_ManufacturerPN")
        sizePolicy.setHeightForWidth(self.lineEdit_ManufacturerPN.sizePolicy().hasHeightForWidth())
        self.lineEdit_ManufacturerPN.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.lineEdit_ManufacturerPN)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_3.addWidget(self.label_4)

        self.lineEdit_Manufacturer = QLineEdit(self.centralwidget)
        self.lineEdit_Manufacturer.setObjectName(u"lineEdit_Manufacturer")
        sizePolicy.setHeightForWidth(self.lineEdit_Manufacturer.sizePolicy().hasHeightForWidth())
        self.lineEdit_Manufacturer.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.lineEdit_Manufacturer)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_4.addWidget(self.label_5)

        self.comboBox_Category = QComboBox(self.centralwidget)
        self.comboBox_Category.setObjectName(u"comboBox_Category")

        self.verticalLayout_4.addWidget(self.comboBox_Category)

        self.verticalLayout_4.setStretch(0, 1)

        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_5.addWidget(self.label_3)

        self.textEdit_Description = QTextEdit(self.centralwidget)
        self.textEdit_Description.setObjectName(u"textEdit_Description")

        self.verticalLayout_5.addWidget(self.textEdit_Description)

        self.verticalLayout_5.setStretch(0, 1)
        self.verticalLayout_5.setStretch(1, 1)

        self.verticalLayout_14.addLayout(self.verticalLayout_5)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_6.addWidget(self.label_6)

        self.comboBox_Supplier = QComboBox(self.centralwidget)
        self.comboBox_Supplier.setObjectName(u"comboBox_Supplier")

        self.verticalLayout_6.addWidget(self.comboBox_Supplier)

        self.verticalLayout_6.setStretch(0, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_7.addWidget(self.label_7)

        self.lineEdit_SupplierPN = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierPN.setObjectName(u"lineEdit_SupplierPN")
        sizePolicy.setHeightForWidth(self.lineEdit_SupplierPN.sizePolicy().hasHeightForWidth())
        self.lineEdit_SupplierPN.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.lineEdit_SupplierPN)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_7)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.centralwidget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_8.addWidget(self.label_8)

        self.lineEdit_SupplierCategory = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierCategory.setObjectName(u"lineEdit_SupplierCategory")
        sizePolicy.setHeightForWidth(self.lineEdit_SupplierCategory.sizePolicy().hasHeightForWidth())
        self.lineEdit_SupplierCategory.setSizePolicy(sizePolicy)

        self.verticalLayout_8.addWidget(self.lineEdit_SupplierCategory)

        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_8)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(self.centralwidget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_9.addWidget(self.label_9)

        self.lineEdit_Datasheet = QLineEdit(self.centralwidget)
        self.lineEdit_Datasheet.setObjectName(u"lineEdit_Datasheet")
        sizePolicy.setHeightForWidth(self.lineEdit_Datasheet.sizePolicy().hasHeightForWidth())
        self.lineEdit_Datasheet.setSizePolicy(sizePolicy)

        self.verticalLayout_9.addWidget(self.lineEdit_Datasheet)

        self.verticalLayout_9.setStretch(0, 1)
        self.verticalLayout_9.setStretch(1, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_9)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label_10 = QLabel(self.centralwidget)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_10.addWidget(self.label_10)

        self.lineEdit_SupplierLink = QLineEdit(self.centralwidget)
        self.lineEdit_SupplierLink.setObjectName(u"lineEdit_SupplierLink")
        sizePolicy.setHeightForWidth(self.lineEdit_SupplierLink.sizePolicy().hasHeightForWidth())
        self.lineEdit_SupplierLink.setSizePolicy(sizePolicy)

        self.verticalLayout_10.addWidget(self.lineEdit_SupplierLink)

        self.verticalLayout_10.setStretch(0, 1)
        self.verticalLayout_10.setStretch(1, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_10)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.centralwidget)
        self.label_11.setObjectName(u"label_11")
        sizePolicy1.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy1)
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_11.addWidget(self.label_11)

        self.lineEdit_Package = QLineEdit(self.centralwidget)
        self.lineEdit_Package.setObjectName(u"lineEdit_Package")
        sizePolicy.setHeightForWidth(self.lineEdit_Package.sizePolicy().hasHeightForWidth())
        self.lineEdit_Package.setSizePolicy(sizePolicy)

        self.verticalLayout_11.addWidget(self.lineEdit_Package)

        self.verticalLayout_11.setStretch(0, 1)
        self.verticalLayout_11.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_11)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.label_12 = QLabel(self.centralwidget)
        self.label_12.setObjectName(u"label_12")
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_12.addWidget(self.label_12)

        self.lineEdit_Stock = QLineEdit(self.centralwidget)
        self.lineEdit_Stock.setObjectName(u"lineEdit_Stock")
        sizePolicy.setHeightForWidth(self.lineEdit_Stock.sizePolicy().hasHeightForWidth())
        self.lineEdit_Stock.setSizePolicy(sizePolicy)

        self.verticalLayout_12.addWidget(self.lineEdit_Stock)

        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_12)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.label_13 = QLabel(self.centralwidget)
        self.label_13.setObjectName(u"label_13")
        sizePolicy1.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy1)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_13.addWidget(self.label_13)

        self.lineEdit_Storage = QLineEdit(self.centralwidget)
        self.lineEdit_Storage.setObjectName(u"lineEdit_Storage")
        sizePolicy.setHeightForWidth(self.lineEdit_Storage.sizePolicy().hasHeightForWidth())
        self.lineEdit_Storage.setSizePolicy(sizePolicy)

        self.verticalLayout_13.addWidget(self.lineEdit_Storage)

        self.verticalLayout_13.setStretch(0, 1)
        self.verticalLayout_13.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_13)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 20, 0, 0)
        self.pushButton_previous = QPushButton(self.centralwidget)
        self.pushButton_previous.setObjectName(u"pushButton_previous")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_previous.sizePolicy().hasHeightForWidth())
        self.pushButton_previous.setSizePolicy(sizePolicy2)
        icon = QIcon()
        icon.addFile(u":/logos/arrow_back_ios_new_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_previous.setIcon(icon)
        self.pushButton_previous.setIconSize(QSize(34, 34))
        self.pushButton_previous.setFlat(True)

        self.horizontalLayout_5.addWidget(self.pushButton_previous)

        self.pushButton_Nou = QPushButton(self.centralwidget)
        self.pushButton_Nou.setObjectName(u"pushButton_Nou")
        sizePolicy2.setHeightForWidth(self.pushButton_Nou.sizePolicy().hasHeightForWidth())
        self.pushButton_Nou.setSizePolicy(sizePolicy2)
        icon1 = QIcon()
        icon1.addFile(u":/logos/add_circle_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_Nou.setIcon(icon1)
        self.pushButton_Nou.setIconSize(QSize(34, 34))
        self.pushButton_Nou.setFlat(True)

        self.horizontalLayout_5.addWidget(self.pushButton_Nou)

        self.pushButton_safe = QPushButton(self.centralwidget)
        self.pushButton_safe.setObjectName(u"pushButton_safe")
        sizePolicy2.setHeightForWidth(self.pushButton_safe.sizePolicy().hasHeightForWidth())
        self.pushButton_safe.setSizePolicy(sizePolicy2)
        icon2 = QIcon()
        icon2.addFile(u":/logos/save_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_safe.setIcon(icon2)
        self.pushButton_safe.setIconSize(QSize(34, 34))
        self.pushButton_safe.setFlat(True)

        self.horizontalLayout_5.addWidget(self.pushButton_safe)

        self.pushButton_next = QPushButton(self.centralwidget)
        self.pushButton_next.setObjectName(u"pushButton_next")
        sizePolicy2.setHeightForWidth(self.pushButton_next.sizePolicy().hasHeightForWidth())
        self.pushButton_next.setSizePolicy(sizePolicy2)
        icon3 = QIcon()
        icon3.addFile(u":/logos/arrow_forward_ios_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_next.setIcon(icon3)
        self.pushButton_next.setIconSize(QSize(34, 34))
        self.pushButton_next.setFlat(True)

        self.horizontalLayout_5.addWidget(self.pushButton_next)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 2)
        self.horizontalLayout_5.setStretch(2, 2)
        self.horizontalLayout_5.setStretch(3, 1)

        self.verticalLayout_14.addLayout(self.horizontalLayout_5)

        self.verticalLayout_14.setStretch(0, 1)
        self.verticalLayout_14.setStretch(1, 2)
        self.verticalLayout_14.setStretch(2, 1)
        self.verticalLayout_14.setStretch(3, 1)
        self.verticalLayout_14.setStretch(4, 1)
        self.verticalLayout_14.setStretch(5, 1)

        self.verticalLayout_15.addLayout(self.verticalLayout_14)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 561, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Manufacturer P/N", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Manufacturer", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Category", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Supplier", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Supplier P/N", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Supplier Category", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Datasheet", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Supplier link", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Package", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Stock", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Storage", None))
        self.pushButton_previous.setText("")
        self.pushButton_Nou.setText("")
        self.pushButton_safe.setText("")
        self.pushButton_next.setText("")
    # retranslateUi

