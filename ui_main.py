# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTableView, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1084, 697)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(50, 0))
        self.frame.setMaximumSize(QSize(50, 16777215))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.btn_menu = QPushButton(self.frame)
        self.btn_menu.setObjectName(u"btn_menu")

        self.verticalLayout.addWidget(self.btn_menu)

        self.btn_load = QPushButton(self.frame)
        self.btn_load.setObjectName(u"btn_load")

        self.verticalLayout.addWidget(self.btn_load)

        self.btn_create = QPushButton(self.frame)
        self.btn_create.setObjectName(u"btn_create")

        self.verticalLayout.addWidget(self.btn_create)

        self.btn_rebuffer = QPushButton(self.frame)
        self.btn_rebuffer.setObjectName(u"btn_rebuffer")

        self.verticalLayout.addWidget(self.btn_rebuffer)

        self.btn_reset = QPushButton(self.frame)
        self.btn_reset.setObjectName(u"btn_reset")

        self.verticalLayout.addWidget(self.btn_reset)

        self.verticalSpacer = QSpacerItem(20, 384, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_exit = QPushButton(self.frame)
        self.btn_exit.setObjectName(u"btn_exit")

        self.verticalLayout.addWidget(self.btn_exit)


        self.horizontalLayout_2.addWidget(self.frame)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")

        self.horizontalLayout_2.addWidget(self.tableView)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1084, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.btn_menu.setText(QCoreApplication.translate("MainWindow", u"", None))
        self.btn_load.setText(QCoreApplication.translate("MainWindow", u"  Na\U0000010d\U000000edst datab\U000000e1zi", None))
        self.btn_create.setText(QCoreApplication.translate("MainWindow", u"  Doplnit unik\u00e1tn\u00ed filmy", None))
        self.btn_rebuffer.setText(QCoreApplication.translate("MainWindow", u"  Doplnit pr\U000000e1zdn\U000000e1 m\U000000edsta", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"  Reset", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"", None))
    # retranslateUi

