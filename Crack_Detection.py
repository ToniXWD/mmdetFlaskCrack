# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Crack_Detection.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(801, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(240, 480, 256, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.labelinput = QtWidgets.QLabel(self.centralwidget)
        self.labelinput.setGeometry(QtCore.QRect(11, 11, 371, 411))
        self.labelinput.setObjectName("labelinput")
        self.labelresult = QtWidgets.QLabel(self.centralwidget)
        self.labelresult.setGeometry(QtCore.QRect(407, 10, 371, 412))
        self.labelresult.setObjectName("labelresult")
        self.btnTest = QtWidgets.QPushButton(self.centralwidget)
        self.btnTest.setGeometry(QtCore.QRect(339, 430, 75, 23))
        self.btnTest.setObjectName("btnTest")
        self.btnInput = QtWidgets.QPushButton(self.centralwidget)
        self.btnInput.setGeometry(QtCore.QRect(140, 430, 80, 23))
        self.btnInput.setObjectName("btnInput")
        self.btnSave = QtWidgets.QPushButton(self.centralwidget)
        self.btnSave.setGeometry(QtCore.QRect(520, 430, 80, 23))
        self.btnSave.setObjectName("btnSave")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 801, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btnInput.clicked.connect(MainWindow.slot1)
        self.btnTest.clicked.connect(MainWindow.slot2)
        self.btnTest.pressed.connect(MainWindow.slot3)
        self.btnSave.clicked.connect(MainWindow.slot4)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelinput.setText(_translate("MainWindow", "输入图片"))
        self.labelresult.setText(_translate("MainWindow", "输出图片"))
        self.btnTest.setText(_translate("MainWindow", "确认提交"))
        self.btnInput.setText(_translate("MainWindow", "导入裂缝图片"))
        self.btnSave.setText(_translate("MainWindow", "下载分割结果"))
