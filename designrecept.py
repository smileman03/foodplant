# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design_recept.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Dialog_recept(object):
    def setupUi(self, Dialog_recept):
        Dialog_recept.setObjectName(_fromUtf8("Dialog_recept"))
        Dialog_recept.resize(843, 563)
        self.groupBox = QGroupBox(Dialog_recept)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 841, 561))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.combozerno = QtWidgets.QComboBox(self.groupBox)
        self.combozerno.setGeometry(QtCore.QRect(460, 403, 171, 22))
        self.combozerno.setObjectName(_fromUtf8("combozerno"))
        self.linezerno = QtWidgets.QLineEdit(self.groupBox)
        self.linezerno.setGeometry(QtCore.QRect(630, 404, 61, 20))
        self.linezerno.setObjectName(_fromUtf8("linezerno"))
        self.combodobavka = QtWidgets.QComboBox(self.groupBox)
        self.combodobavka.setGeometry(QtCore.QRect(460, 453, 171, 22))
        self.combodobavka.setObjectName(_fromUtf8("combodobavka"))
        self.linedobavka = QtWidgets.QLineEdit(self.groupBox)
        self.linedobavka.setGeometry(QtCore.QRect(630, 454, 61, 20))
        self.linedobavka.setObjectName(_fromUtf8("linedobavka"))
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(460, 389, 91, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(460, 439, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.linekorm = QtWidgets.QLineEdit(self.groupBox)
        self.linekorm.setGeometry(QtCore.QRect(20, 400, 251, 20))
        self.linekorm.setObjectName(_fromUtf8("linekorm"))
        self.btnaddkorm = QtWidgets.QPushButton(self.groupBox)
        self.btnaddkorm.setGeometry(QtCore.QRect(270, 398, 75, 23))
        self.btnaddkorm.setObjectName(_fromUtf8("btnaddkorm"))
        self.linemaslo = QtWidgets.QLineEdit(self.groupBox)
        self.linemaslo.setGeometry(QtCore.QRect(460, 496, 113, 20))
        self.linemaslo.setObjectName(_fromUtf8("linemaslo"))
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(460, 482, 81, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(23, 16, 91, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(20, 385, 151, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(452, 15, 91, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.btnaddzerno = QtWidgets.QPushButton(self.groupBox)
        self.btnaddzerno.setGeometry(QtCore.QRect(690, 402, 75, 23))
        self.btnaddzerno.setObjectName(_fromUtf8("btnaddzerno"))
        self.btnadddobavka = QtWidgets.QPushButton(self.groupBox)
        self.btnadddobavka.setGeometry(QtCore.QRect(690, 452, 75, 23))
        self.btnadddobavka.setObjectName(_fromUtf8("btnadddobavka"))
        self.btnaddmaslo = QtWidgets.QPushButton(self.groupBox)
        self.btnaddmaslo.setGeometry(QtCore.QRect(571, 494, 75, 23))
        self.btnaddmaslo.setObjectName(_fromUtf8("btnaddmaslo"))
        self.btndelete = QtWidgets.QPushButton(self.groupBox)
        self.btndelete.setGeometry(QtCore.QRect(610, 370, 111, 23))
        self.btndelete.setObjectName(_fromUtf8("btndelete"))
        self.listwidgetkorm =QtWidgets.QListWidget(self.groupBox)
        self.listwidgetkorm.setGeometry(QtCore.QRect(10, 30, 431, 341))
        self.listwidgetkorm.setObjectName(_fromUtf8("listwidgetkorm"))
        self.tablerecept = QtWidgets.QTableWidget(self.groupBox)
        self.tablerecept.setGeometry(QtCore.QRect(450, 30, 371, 341))
        self.tablerecept.setColumnCount(2)
        self.tablerecept.setObjectName(_fromUtf8("tablerecept"))
        self.tablerecept.setRowCount(0)
        self.savebtn = QtWidgets.QPushButton(self.groupBox)
        self.savebtn.setGeometry(QtCore.QRect(740, 370, 75, 23))
        self.savebtn.setObjectName(_fromUtf8("savebtn"))
        self.label_allweight = QtWidgets.QLabel(self.groupBox)
        self.label_allweight.setGeometry(QtCore.QRect(681, 13, 151, 20))
        self.label_allweight.setObjectName(_fromUtf8("label_allweight"))

        self.retranslateUi(Dialog_recept)
        QtCore.QMetaObject.connectSlotsByName(Dialog_recept)

    def retranslateUi(self, Dialog_recept):
        Dialog_recept.setWindowTitle(_translate("Dialog_recept", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog_recept", "Рецепты", None))
        self.label.setText(_translate("Dialog_recept", "Зерновые", None))
        self.label_3.setText(_translate("Dialog_recept", "Добавки", None))
        self.btnaddkorm.setText(_translate("Dialog_recept", "Добавить", None))
        self.label_5.setText(_translate("Dialog_recept", "Масло", None))
        self.label_6.setText(_translate("Dialog_recept", "Комбикорм", None))
        self.label_7.setText(_translate("Dialog_recept", "Новый комбикорм", None))
        self.label_8.setText(_translate("Dialog_recept", "Рецепт", None))
        self.btnaddzerno.setText(_translate("Dialog_recept", "Добавить", None))
        self.btnadddobavka.setText(_translate("Dialog_recept", "Добавить", None))
        self.btnaddmaslo.setText(_translate("Dialog_recept", "Добавить", None))
        self.btndelete.setText(_translate("Dialog_recept", "Удалить позицию", None))
        self.savebtn.setText(_translate("Dialog_recept", "Применить", None))
        self.label_allweight.setText(_translate("Dialog_recept", "Общий вес:", None))

