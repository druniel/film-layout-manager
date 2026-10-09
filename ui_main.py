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
        self.verticalLayout.setSpacing(0)
        
        self.lang_layout = QVBoxLayout()
        self.lang_layout.setSpacing(0)
        self.lang_layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_top = QFrame(self.frame)
        self.line_top.setFrameShape(QFrame.Shape.HLine)
        self.line_top.setStyleSheet("color: rgba(255, 255, 255, 0.2);")
        self.lang_layout.addWidget(self.line_top)
        self.widget_lang_expanded = QWidget(self.frame)
        self.horizontalLayout_lang = QHBoxLayout(self.widget_lang_expanded)
        self.horizontalLayout_lang.setSpacing(0)
        self.horizontalLayout_lang.setContentsMargins(0, 0, 0, 0)
        self.btn_cz = QPushButton("CZ", self.widget_lang_expanded)
        self.btn_cz.setObjectName(u"btn_cz")
        self.btn_cz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.line_vertical = QFrame(self.widget_lang_expanded)
        self.line_vertical.setFrameShape(QFrame.Shape.VLine)
        self.line_vertical.setStyleSheet("color: white; background-color: white;")
        self.btn_sk = QPushButton("SK", self.widget_lang_expanded)
        self.btn_sk.setObjectName(u"btn_sk")
        self.btn_sk.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.horizontalLayout_lang.addWidget(self.btn_cz)
        self.horizontalLayout_lang.addWidget(self.line_vertical)
        self.horizontalLayout_lang.addWidget(self.btn_sk)
        self.lang_layout.addWidget(self.widget_lang_expanded)
        self.btn_lang_collapsed = QPushButton("CZ", self.frame)
        self.btn_lang_collapsed.setObjectName(u"btn_lang_collapsed")
        font = QFont()
        font.setBold(True)
        self.btn_lang_collapsed.setFont(font)
        self.lang_layout.addWidget(self.btn_lang_collapsed)
        self.line_bottom = QFrame(self.frame)
        self.line_bottom.setFrameShape(QFrame.Shape.HLine)
        self.line_bottom.setStyleSheet("color: rgba(255, 255, 255, 0.2);")
        self.lang_layout.addWidget(self.line_bottom)
        self.verticalLayout.addLayout(self.lang_layout)
        
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
        
        self.btn_send = QPushButton(self.frame)
        self.btn_send.setObjectName(u"btn_send")
        
        self.verticalLayout.addWidget(self.btn_send)

        self.verticalSpacer = QSpacerItem(20, 384, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_exit = QPushButton(self.frame)
        self.btn_exit.setObjectName(u"btn_exit")

        self.verticalLayout.addWidget(self.btn_exit)


        self.horizontalLayout_2.addWidget(self.frame)
        
        self.verticalLayout_right = QVBoxLayout()
        self.verticalLayout_right.setSpacing(0)
        self.verticalLayout_right.setContentsMargins(0, 0, 0, 0)

        self.checkbox_container = QWidget(self.centralwidget)
        self.checkbox_container.setMinimumHeight(35)
        self.checkbox_layout = QHBoxLayout(self.checkbox_container)
        self.checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox_layout.setSpacing(0)

        self.verticalLayout_right.addWidget(self.checkbox_container)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")
        
        self.verticalLayout_right.addWidget(self.tableView)
        self.horizontalLayout_2.addLayout(self.verticalLayout_right)

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
        self.btn_send.setText(QCoreApplication.translate("MainWindow", u"  Odeslat do CMS", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"", None))
    # retranslateUi

