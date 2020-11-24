# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design_dozakaz.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog_dozakaz(object):
    def setupUi(self, Dialog_dozakaz):
        Dialog_dozakaz.setObjectName(_fromUtf8("Dialog_dozakaz"))
        Dialog_dozakaz.resize(741, 405)
        self.groupBox = QtGui.QGroupBox(Dialog_dozakaz)
        self.groupBox.setGeometry(QtCore.QRect(-10, 0, 751, 401))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(29, 15, 91, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.table_factval = QtGui.QTableWidget(self.groupBox)
        self.table_factval.setGeometry(QtCore.QRect(20, 30, 361, 341))
        self.table_factval.setColumnCount(2)
        self.table_factval.setObjectName(_fromUtf8("table_factval"))
        self.table_factval.setRowCount(0)
        self.table_dozakazlist = QtGui.QTableWidget(self.groupBox)
        self.table_dozakazlist.setGeometry(QtCore.QRect(380, 30, 361, 341))
        self.table_dozakazlist.setColumnCount(2)
        self.table_dozakazlist.setObjectName(_fromUtf8("table_dozakazlist"))
        self.table_dozakazlist.setRowCount(0)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(380, 10, 91, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(670, 370, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(Dialog_dozakaz)
        QtCore.QMetaObject.connectSlotsByName(Dialog_dozakaz)

    def retranslateUi(self, Dialog_dozakaz):
        Dialog_dozakaz.setWindowTitle(_translate("Dialog_dozakaz", "Dialog", None))
        self.label_8.setText(_translate("Dialog_dozakaz", "Завешено", None))
        self.label_9.setText(_translate("Dialog_dozakaz", "Дозаказать", None))
        self.pushButton.setText(_translate("Dialog_dozakaz", "Заказать", None))

