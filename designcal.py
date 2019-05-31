# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cal_dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Dialog_Cal(object):
    def setupUi(self, Dialog_Cal):
        Dialog_Cal.setObjectName(_fromUtf8("Dialog_Cal"))
        Dialog_Cal.resize(174, 217)
        self.groupBox = QtGui.QGroupBox(Dialog_Cal)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 171, 71))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.calves1btn = QtGui.QPushButton(self.groupBox)
        self.calves1btn.setGeometry(QtCore.QRect(88, 20, 81, 23))
        self.calves1btn.setObjectName(_fromUtf8("calves1btn"))
        self.editves1 = QtGui.QLineEdit(self.groupBox)
        self.editves1.setGeometry(QtCore.QRect(3, 20, 81, 20))
        self.editves1.setObjectName(_fromUtf8("editves1"))
        self.btnves1tara = QtGui.QPushButton(self.groupBox)
        self.btnves1tara.setGeometry(QtCore.QRect(10, 40, 75, 21))
        self.btnves1tara.setObjectName(_fromUtf8("btnves1tara"))
        self.groupBox_3 = QtGui.QGroupBox(Dialog_Cal)
        self.groupBox_3.setGeometry(QtCore.QRect(0, 70, 171, 71))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.calves2btn = QtGui.QPushButton(self.groupBox_3)
        self.calves2btn.setGeometry(QtCore.QRect(88, 20, 81, 23))
        self.calves2btn.setObjectName(_fromUtf8("calves2btn"))
        self.editves2 = QtGui.QLineEdit(self.groupBox_3)
        self.editves2.setGeometry(QtCore.QRect(3, 20, 81, 20))
        self.editves2.setObjectName(_fromUtf8("editves2"))
        self.btnves2tara = QtGui.QPushButton(self.groupBox_3)
        self.btnves2tara.setGeometry(QtCore.QRect(10, 40, 75, 21))
        self.btnves2tara.setObjectName(_fromUtf8("btnves2tara"))
        self.groupBox_4 = QtGui.QGroupBox(Dialog_Cal)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 140, 171, 71))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.calves3btn = QtGui.QPushButton(self.groupBox_4)
        self.calves3btn.setGeometry(QtCore.QRect(88, 20, 81, 23))
        self.calves3btn.setObjectName(_fromUtf8("calves3btn"))
        self.editves3 = QtGui.QLineEdit(self.groupBox_4)
        self.editves3.setGeometry(QtCore.QRect(3, 20, 81, 20))
        self.editves3.setObjectName(_fromUtf8("editves3"))
        self.btnves3tara = QtGui.QPushButton(self.groupBox_4)
        self.btnves3tara.setGeometry(QtCore.QRect(10, 40, 75, 21))
        self.btnves3tara.setObjectName(_fromUtf8("btnves3tara"))

        self.retranslateUi(Dialog_Cal)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Cal)

    def retranslateUi(self, Dialog_Cal):
        Dialog_Cal.setWindowTitle(_translate("Dialog_Cal", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog_Cal", "Весы1", None))
        self.calves1btn.setText(_translate("Dialog_Cal", "Калибровать", None))
        self.btnves1tara.setText(_translate("Dialog_Cal", "Тара", None))
        self.groupBox_3.setTitle(_translate("Dialog_Cal", "Весы2", None))
        self.calves2btn.setText(_translate("Dialog_Cal", "Калибровать", None))
        self.btnves2tara.setText(_translate("Dialog_Cal", "Тара", None))
        self.groupBox_4.setTitle(_translate("Dialog_Cal", "Весы3", None))
        self.calves3btn.setText(_translate("Dialog_Cal", "Калибровать", None))
        self.btnves3tara.setText(_translate("Dialog_Cal", "Тара", None))

