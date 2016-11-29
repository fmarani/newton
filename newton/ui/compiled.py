# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newton.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Newton(object):
    def setupUi(self, Newton):
        Newton.setObjectName("Newton")
        Newton.resize(415, 773)
        self.centralwidget = QtWidgets.QWidget(Newton)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 411, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_3 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(0, 40, 411, 711))
        self.listView.setObjectName("listView")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(0, 40, 411, 91))
        self.listWidget.setObjectName("listWidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(60, 60, 311, 31))
        self.textBrowser.setObjectName("textBrowser")
        Newton.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Newton)
        self.statusbar.setObjectName("statusbar")
        Newton.setStatusBar(self.statusbar)

        self.retranslateUi(Newton)
        QtCore.QMetaObject.connectSlotsByName(Newton)

    def retranslateUi(self, Newton):
        _translate = QtCore.QCoreApplication.translate
        Newton.setWindowTitle(_translate("Newton", "Newton"))
        self.pushButton_3.setText(_translate("Newton", "Home"))
        self.pushButton_2.setText(_translate("Newton", "Notifications"))
        self.pushButton.setText(_translate("Newton", "Write"))
        self.textBrowser.setHtml(_translate("Newton", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This is a <span style=\" font-weight:600;\">tweet</span> message</p></body></html>"))

