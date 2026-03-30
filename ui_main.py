# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLayout, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)
import recursos_grafics_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(820, 610)
        MainWindow.setIconSize(QSize(34, 34))
        MainWindow.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.listWidget_4 = QListWidget(self.centralwidget)
        self.listWidget_4.setObjectName(u"listWidget_4")
        self.listWidget_4.setGeometry(QRect(650, 140, 51, 91))
        self.verticalLayoutWidget_6 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_6.setObjectName(u"verticalLayoutWidget_6")
        self.verticalLayoutWidget_6.setGeometry(QRect(0, 0, 801, 581))
        self.verticalLayout_6 = QVBoxLayout(self.verticalLayoutWidget_6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.filter1_label = QLabel(self.verticalLayoutWidget_6)
        self.filter1_label.setObjectName(u"filter1_label")

        self.verticalLayout.addWidget(self.filter1_label)

        self.filter1_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filter1_lineEdit.setObjectName(u"filter1_lineEdit")

        self.verticalLayout.addWidget(self.filter1_lineEdit)

        self.filter1_listWidget = QListWidget(self.verticalLayoutWidget_6)
        self.filter1_listWidget.setObjectName(u"filter1_listWidget")

        self.verticalLayout.addWidget(self.filter1_listWidget)

        self.filter1_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.filter1_pushButton.setObjectName(u"filter1_pushButton")
        font = QFont()
        font.setPointSize(8)
        self.filter1_pushButton.setFont(font)

        self.verticalLayout.addWidget(self.filter1_pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.filter2_label = QLabel(self.verticalLayoutWidget_6)
        self.filter2_label.setObjectName(u"filter2_label")

        self.verticalLayout_2.addWidget(self.filter2_label)

        self.filter2_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filter2_lineEdit.setObjectName(u"filter2_lineEdit")

        self.verticalLayout_2.addWidget(self.filter2_lineEdit)

        self.filter2_listWidget = QListWidget(self.verticalLayoutWidget_6)
        self.filter2_listWidget.setObjectName(u"filter2_listWidget")

        self.verticalLayout_2.addWidget(self.filter2_listWidget)

        self.filter2_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.filter2_pushButton.setObjectName(u"filter2_pushButton")

        self.verticalLayout_2.addWidget(self.filter2_pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.filter3_label = QLabel(self.verticalLayoutWidget_6)
        self.filter3_label.setObjectName(u"filter3_label")

        self.verticalLayout_3.addWidget(self.filter3_label)

        self.filter3_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filter3_lineEdit.setObjectName(u"filter3_lineEdit")

        self.verticalLayout_3.addWidget(self.filter3_lineEdit)

        self.filter3_listWidget = QListWidget(self.verticalLayoutWidget_6)
        self.filter3_listWidget.setObjectName(u"filter3_listWidget")

        self.verticalLayout_3.addWidget(self.filter3_listWidget)

        self.filter3_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.filter3_pushButton.setObjectName(u"filter3_pushButton")

        self.verticalLayout_3.addWidget(self.filter3_pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.filter4_label = QLabel(self.verticalLayoutWidget_6)
        self.filter4_label.setObjectName(u"filter4_label")

        self.verticalLayout_4.addWidget(self.filter4_label)

        self.filter4_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filter4_lineEdit.setObjectName(u"filter4_lineEdit")

        self.verticalLayout_4.addWidget(self.filter4_lineEdit)

        self.filter4_listWidget = QListWidget(self.verticalLayoutWidget_6)
        self.filter4_listWidget.setObjectName(u"filter4_listWidget")

        self.verticalLayout_4.addWidget(self.filter4_listWidget)

        self.filter4_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.filter4_pushButton.setObjectName(u"filter4_pushButton")

        self.verticalLayout_4.addWidget(self.filter4_pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.filter5_label = QLabel(self.verticalLayoutWidget_6)
        self.filter5_label.setObjectName(u"filter5_label")

        self.verticalLayout_5.addWidget(self.filter5_label)

        self.filter5_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filter5_lineEdit.setObjectName(u"filter5_lineEdit")

        self.verticalLayout_5.addWidget(self.filter5_lineEdit)

        self.filter5_listWidget = QListWidget(self.verticalLayoutWidget_6)
        self.filter5_listWidget.setObjectName(u"filter5_listWidget")

        self.verticalLayout_5.addWidget(self.filter5_listWidget)

        self.filter5_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.filter5_pushButton.setObjectName(u"filter5_pushButton")

        self.verticalLayout_5.addWidget(self.filter5_pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.datasheetButton = QPushButton(self.verticalLayoutWidget_6)
        self.datasheetButton.setObjectName(u"datasheetButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datasheetButton.sizePolicy().hasHeightForWidth())
        self.datasheetButton.setSizePolicy(sizePolicy)
        self.datasheetButton.setMinimumSize(QSize(41, 41))
        font1 = QFont()
        font1.setPointSize(18)
        self.datasheetButton.setFont(font1)
        icon = QIcon()
        icon.addFile(u":/logos/link_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.datasheetButton.setIcon(icon)
        self.datasheetButton.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.datasheetButton)

        self.pushButton_5 = QPushButton(self.verticalLayoutWidget_6)
        self.pushButton_5.setObjectName(u"pushButton_5")
        sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy)
        self.pushButton_5.setMinimumSize(QSize(41, 41))
        font2 = QFont()
        font2.setPointSize(20)
        self.pushButton_5.setFont(font2)
        icon1 = QIcon()
        icon1.addFile(u":/logos/autorenew_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_5.setIcon(icon1)
        self.pushButton_5.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.pushButton_5)

        self.pushButton_4 = QPushButton(self.verticalLayoutWidget_6)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)
        self.pushButton_4.setMinimumSize(QSize(41, 41))
        self.pushButton_4.setFont(font1)
        icon2 = QIcon()
        icon2.addFile(u":/logos/file_open_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_4.setIcon(icon2)
        self.pushButton_4.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.pushButton_4)

        self.pushButton_6 = QPushButton(self.verticalLayoutWidget_6)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy)
        self.pushButton_6.setMinimumSize(QSize(41, 41))
        self.pushButton_6.setFont(font2)
        icon3 = QIcon()
        icon3.addFile(u":/logos/frame_inspect_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_6.setIcon(icon3)
        self.pushButton_6.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.verticalLayoutWidget_6)
        self.pushButton_7.setObjectName(u"pushButton_7")
        sizePolicy.setHeightForWidth(self.pushButton_7.sizePolicy().hasHeightForWidth())
        self.pushButton_7.setSizePolicy(sizePolicy)
        self.pushButton_7.setMinimumSize(QSize(41, 41))
        self.pushButton_7.setFont(font2)
        icon4 = QIcon()
        icon4.addFile(u":/logos/note_add_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_7.setIcon(icon4)
        self.pushButton_7.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.pushButton_7)

        self.pushButton_8 = QPushButton(self.verticalLayoutWidget_6)
        self.pushButton_8.setObjectName(u"pushButton_8")
        sizePolicy.setHeightForWidth(self.pushButton_8.sizePolicy().hasHeightForWidth())
        self.pushButton_8.setSizePolicy(sizePolicy)
        self.pushButton_8.setMinimumSize(QSize(41, 41))
        self.pushButton_8.setFont(font2)
        self.pushButton_8.setIcon(icon4)
        self.pushButton_8.setIconSize(QSize(34, 34))

        self.verticalLayout_9.addWidget(self.pushButton_8)


        self.horizontalLayout_2.addLayout(self.verticalLayout_9)


        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.widget = QWidget(self.verticalLayoutWidget_6)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 30))
        self.horizontalLayoutWidget = QWidget(self.widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 781, 31))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_6.addWidget(self.widget)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.filterG_label = QLabel(self.verticalLayoutWidget_6)
        self.filterG_label.setObjectName(u"filterG_label")

        self.verticalLayout_7.addWidget(self.filterG_label)

        self.filterG_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.filterG_lineEdit.setObjectName(u"filterG_lineEdit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.filterG_lineEdit.sizePolicy().hasHeightForWidth())
        self.filterG_lineEdit.setSizePolicy(sizePolicy1)

        self.verticalLayout_7.addWidget(self.filterG_lineEdit)


        self.horizontalLayout_4.addLayout(self.verticalLayout_7)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.FilterPN_label = QLabel(self.verticalLayoutWidget_6)
        self.FilterPN_label.setObjectName(u"FilterPN_label")

        self.verticalLayout_8.addWidget(self.FilterPN_label)

        self.FilterPN_lineEdit = QLineEdit(self.verticalLayoutWidget_6)
        self.FilterPN_lineEdit.setObjectName(u"FilterPN_lineEdit")
        sizePolicy1.setHeightForWidth(self.FilterPN_lineEdit.sizePolicy().hasHeightForWidth())
        self.FilterPN_lineEdit.setSizePolicy(sizePolicy1)

        self.verticalLayout_8.addWidget(self.FilterPN_lineEdit)


        self.horizontalLayout_4.addLayout(self.verticalLayout_8)

        self.clear_all_pushButton = QPushButton(self.verticalLayoutWidget_6)
        self.clear_all_pushButton.setObjectName(u"clear_all_pushButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.clear_all_pushButton.sizePolicy().hasHeightForWidth())
        self.clear_all_pushButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.clear_all_pushButton)

        self.label_7 = QLabel(self.verticalLayoutWidget_6)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(41, 41))
        self.label_7.setFont(font2)
        self.label_7.setPixmap(QPixmap(u":/logos/content_paste_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg"))

        self.horizontalLayout_4.addWidget(self.label_7)

        self.label_5 = QLabel(self.verticalLayoutWidget_6)
        self.label_5.setObjectName(u"label_5")
        sizePolicy2.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy2)
        self.label_5.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_4.addWidget(self.label_5)

        self.label_8 = QLabel(self.verticalLayoutWidget_6)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(41, 41))
        self.label_8.setFont(font2)
        self.label_8.setPixmap(QPixmap(u":/logos/inventory_2_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg"))

        self.horizontalLayout_4.addWidget(self.label_8)

        self.label_9 = QLabel(self.verticalLayoutWidget_6)
        self.label_9.setObjectName(u"label_9")
        sizePolicy2.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy2)
        self.label_9.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.label_9)

        self.label_2 = QLabel(self.verticalLayoutWidget_6)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(41, 41))
        self.label_2.setFont(font2)
        self.label_2.setPixmap(QPixmap(u":/logos/archive_34dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg"))

        self.horizontalLayout_4.addWidget(self.label_2)

        self.stock_text = QLineEdit(self.verticalLayoutWidget_6)
        self.stock_text.setObjectName(u"stock_text")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(30)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.stock_text.sizePolicy().hasHeightForWidth())
        self.stock_text.setSizePolicy(sizePolicy3)
        self.stock_text.setMinimumSize(QSize(30, 0))

        self.horizontalLayout_4.addWidget(self.stock_text)


        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tableWidget = QTableWidget(self.verticalLayoutWidget_6)
        self.tableWidget.setObjectName(u"tableWidget")

        self.horizontalLayout_3.addWidget(self.tableWidget)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setEnabled(False)
        self.menubar.setGeometry(QRect(0, 0, 820, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"myStock", None))
        self.filter1_label.setText(QCoreApplication.translate("MainWindow", u"Filter 1", None))
        self.filter1_pushButton.setText(QCoreApplication.translate("MainWindow", u" reset", None))
        self.filter2_label.setText(QCoreApplication.translate("MainWindow", u"Filter 2", None))
        self.filter2_pushButton.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.filter3_label.setText(QCoreApplication.translate("MainWindow", u"Filter 3", None))
        self.filter3_pushButton.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.filter4_label.setText(QCoreApplication.translate("MainWindow", u"Filter 4", None))
        self.filter4_pushButton.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.filter5_label.setText(QCoreApplication.translate("MainWindow", u"Filter 5", None))
        self.filter5_pushButton.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.datasheetButton.setText("")
        self.pushButton_5.setText("")
        self.pushButton_4.setText("")
        self.pushButton_6.setText("")
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.filterG_label.setText(QCoreApplication.translate("MainWindow", u"Filtre general", None))
        self.FilterPN_label.setText(QCoreApplication.translate("MainWindow", u"Filtre Manufacture PN", None))
        self.clear_all_pushButton.setText(QCoreApplication.translate("MainWindow", u"Reset all filters", None))
        self.label_7.setText("")
        self.label_5.setText("")
        self.label_8.setText("")
        self.label_9.setText("")
        self.label_2.setText("")
    # retranslateUi

