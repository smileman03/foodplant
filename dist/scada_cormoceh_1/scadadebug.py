# -*- coding: utf-8 -*-
#coding: utf-8
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtSql import *
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from PyQt4.QtCore import QThread
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import threading
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtCore import QTimer
import logging
import MySQLdb
from designrecept import Ui_Dialog_Recept
from designzerno import Ui_Dialog_Zerno
from designdobavka import Ui_Dialog_Dobavka
from  ConfigParser import *
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'log.log')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
qtCreatorFile = "design.ui"  # main window design ui
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
from ConfigParser import SafeConfigParser


DEBUGFLAG=True

############  INI ###############
##
##

class CONFIG:
    ERROR_READ_INI=False
    ipaddrdb='localhost'
    namedb='cormoceh4'
    ipaddrplc='10.0.6.98'
    portplc='502'
    parser = SafeConfigParser()
    # parser = ConfigParser.SafeConfigParser()
    parser.read('.\config.ini')
    def __init__(self):
        if self.parser.has_section("PLC") is False:
            self.ERROR_READ_INI = True
        else:
            self.ipaddrplc = unicode(self.parser.get('PLC', 'PLC_IPADDRESS', '10.0.6.98'), 'utf8')
            self.portplc = unicode(self.parser.get('PLC', 'PLC_PORT', '502'), 'utf8')
        if self.parser.has_section("DATABASE") is False:
            self.ERROR_READ_INI = True
        else:
            self.ipaddrdb = unicode(self.parser.get('DATABASE', 'SQL_IPADDRESS', 'localhost'), 'utf8')
            self.namedb = unicode(self.parser.get('DATABASE', 'SQL_DATABASE', 'kormoceh4'), 'utf8')
##
##
############ END class INI ENDENDENDENDENDENDENDENDEND

############ class SQL ###############
##
##
class DB:
    def __init__(self,baseaddress_,user_,passw_,db_):
        if DEBUGFLAG is False:
            self.db = MySQLdb.connect(host=baseaddress_, user=user_, passwd=passw_, db=db_, charset='utf8')
        # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
        else:
            self.db=''
    def get_recepts(self):
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM recept"""
        self.cursor.execute(self.sql)
        return  self.cursor.fetchall()

    def get_product(self,id_product):
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM product where nGrp_Product="""+str(id_product) #1-зерно 2-добавки 3 -корм
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_bunker(self,id_ingridient): # Получить номер банки по Id продукта(Зерно =1, Добьавки=2, Комбикорм=3, Масло=4)
        self.cursor = self.db.cursor()
        self.sql = """SELECT Name FROM bunker WHERE nGrp_Bunker="""+str(id_ingridient)
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

##
##
############ END class SQL ENDENDENDENDENDENDENDENDEND


############ class PLC ###############
##
##

class PLC:
    def __init__(self,PLCadress,PLCport):
        if DEBUGFLAG is False:
            self.client = ModbusClient(PLCadress, port=PLCport)
            self.incoil = 0
        else:
            self.client=''
    def connect(self):
        if DEBUGFLAG is False:
            return self.client.connect()
        else:
            return False
    def disconnect(self):
        if DEBUGFLAG is False:
            return self.client.close()
        else:
            return False



##
##
############ END class PLC ENDENDENDENDENDENDENDENDEND

########### class objlevel2 #############
##
##

class obj2():
    pass



############ class obj ###############
##
##
class obj(QtCore.QObject):
    qtobj = 0
    movie = ''
    numbit = 0
    imgtrue = ''
    imgfalse = ''
    state = False
    instate = False

    def __init__(self, object, imgfalse, imgtrue, gif):
        self.imgfalse = imgfalse
        self.imgtrue = imgtrue
        self.qtobj = object
        if gif is not '':
            self.movie = QtGui.QMovie(gif)

        self.qtobj.mousePressEvent = self.onclicked_
    def onclicked_(self,event):
        if self.state is False:
            self.switch(1)
        else:
            self.switch(0)

    def start(self):
        if self.movie is not '':
            self.qtobj.setMovie(self.movie)
            self.movie.start()
        else:
            self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgtrue))
        self.state = True

    def stop(self):
        self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgfalse))
        self.state = False

    def switch(self, bit):
        if bit is 1:
            if self.state is False:
                self.start()
                #print("start " + str(bit))
        else:
            if self.state is True:
                self.stop()
                #print("stop "+str(bit))
##
##
############ END class obj ENDENDENDENDENDENDENDENDEND

##########thread  Worker ###########
##
class Worker(QObject):
    finished = pyqtSignal()
    singal_= pyqtSignal(int,(int))
    _isRunning=False
    @pyqtSlot()
    def process(self):
        while  self._isRunning is True:

            for i in range(0, 98):
                incoil = PLC.read_coils(i + 112, 1, unit=0x01)
                self.singal_.emit(i,incoil.bits[0])
                print incoil.bits[0]
            # print 'FINISHED'
        # self.finished.emit()
    def stop(self):
        self._isRunning = False
##
########## END thread Worker ENDENDENDENDENDENDENDENDEND

########### Dialog recept class ###########
##
class Dialog_recept(QDialog,Ui_Dialog_Recept):
    def __init__(self,dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Recept()
        self.ui.setupUi(self)
        for row in dbclient.get_product(3):
             self.ui.combo1.addItem(row[1])
             self.ui.combo2.addItem(row[1])
             self.ui.combo3.addItem(row[1])
             self.ui.combo4.addItem(row[1])
             self.ui.combo5.addItem(row[1])
             self.ui.combo6.addItem(row[1])
##
########### END Dialog recept class ENDENDENDENDENDENDENDENDEND

########### Dialog recept class ###########
##
class Dialog_zerno(QDialog,Ui_Dialog_Zerno):
    def __init__(self,dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Zerno()
        self.ui.setupUi(self)
        # for row in get_product():
        #     print row[3]
        #     self.combozerno.addItem(row[3])
##
########### END Dialog recept class ENDENDENDENDENDENDENDENDEND

########### Dialog recept class ###########
##
class Dialog_dobavka(QDialog,Ui_Dialog_Dobavka):
    def __init__(self,dbclient,conf):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Dobavka()
        self.ui.setupUi(self)
        # self.combo1.addItem("123123")
        # self.combo1.addItem("14567")
        for row in dbclient.get_product(2):
             self.ui.combo1.addItem(row[1])
             self.ui.combo2.addItem(row[1])
             self.ui.combo3.addItem(row[1])
             self.ui.combo4.addItem(row[1])
             self.ui.combo5.addItem(row[1])
             self.ui.combo6.addItem(row[1])
##
########### END Dialog recept class ENDENDENDENDENDENDENDENDEND

########### class MyApp #######################
##
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    movies = []
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # self.QLabel.installEventFilter(self)
        self.connectflag = False
        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)

        self.connectbtn.clicked.connect(self.connectbtnclk)
        # self.connectbtn.clicked.connect(self.addreceptbtnclk)
        self.movies.insert(0, obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(1, obj(self.dobavkisilos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(2, obj(self.silos1dobavkaopen, "statusminifalse.png", "", "statusminitrue.png"))
        self.movies.insert(3, obj(self.silos1dobavkaclose, "statusminifalse.png", "", "statusminitrue.png"))
        self.movies.insert(4, obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(5, obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(6, obj(self.silos2dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(7, obj(self.silos2dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(8, obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(9, obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(10, obj(self.silos3dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(11, obj(self.silos3dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(12, obj(self.dobavkisilos4up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(13, obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(14, obj(self.silos4dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(15, obj(self.silos4dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(16, obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(17, obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(18, obj(self.silos5dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(19, obj(self.silos5dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(20, obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(21, obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(22, obj(self.silos6dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(23, obj(self.silos6dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(24, obj(self.flex1, "flex1stop.png", "flex1run.png", ''))
        self.movies.insert(25, obj(self.flex2, "flex2stop.png", "flex2run.png", ''))
        self.movies.insert(26, obj(self.flex3, "flex3stop.png", "flex3run.png", ''))
        self.movies.insert(27, obj(self.flex4, "flex4stop.png", "flex4run.png", ''))
        self.movies.insert(28, obj(self.flex5, "flex5stop.png", "flex5run.png", ''))
        self.movies.insert(29, obj(self.flex6, "flex6stop.png", "flex6run.png", ''))
        self.movies.insert(30, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(31, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(32, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button auto
        self.movies.insert(33, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button ruchno
        self.movies.insert(34, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button stop
        self.movies.insert(35, obj(self.flexload, "flexloadstop.png", "flexloadrun.png", ''))
        self.movies.insert(36, obj(self.bunkerloaddo, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(37, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # open shiber vesi knopka
        self.movies.insert(38, obj(self.ves3sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(39, obj(self.ves3sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(40, obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", ''))
        self.movies.insert(41, obj(self.mixersensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(42, obj(self.mixersensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(43, obj(self.mixer, "mixerstop.png", '', "mixerbegin.gif"))
        self.movies.insert(44, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # mixer2
        self.movies.insert(45, obj(self.mixerbunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(46, obj(self.mixershnek1, "shnek_hor_stop.gif", "", "shnek_hor_begin.gif"))
        self.movies.insert(47, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(48, obj(self.ves1sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(49, obj(self.ves1sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(50, obj(self.ves2sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(51, obj(self.ves2sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(52, obj(self.ves1bunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(53, obj(self.ves2bunkersens1, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(54, obj(self.ves2bunkersens2, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(55, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(56, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(57, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(58, obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", ""))
        self.movies.insert(59, obj(self.zernoshnek4, "shnek4zernostop.png", "shnek4zernorun.png", ""))
        self.movies.insert(60, obj(self.zernoshnek5, "shnek5zernostop.png", "shnek5zernorun.png", ""))
        self.movies.insert(61, obj(self.zernoshnek6, "shnek6zernostop.png", "shnek6zernorun.png", ""))
        self.movies.insert(62, obj(self.zernoshnek7, "shnek7zernostop.png", "shnek7zernorun.png", ""))
        self.movies.insert(63, obj(self.zernoshnek8, "shnek8zernostop.png", "shnek8zernorun.png", ""))
        self.movies.insert(64, obj(self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""))
        self.movies.insert(65, obj(self.zernoshnek10, "shnek10zernostop.png", "shnek10zernorun.png", ""))
        self.movies.insert(66, obj(self.drobilka1, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(67, obj(self.drobilka2, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(68, obj(self.ves2shnek, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(69, obj(self.ves1shnek1, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(70, obj(self.ves1shnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(71, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(72, obj(self.klapan1, "klapan1false.png", "klapan1true.png", ""))
        self.movies.insert(73, obj(self.klapan2, "klapan2false.png", "", "klapan2true.png"))
        self.movies.insert(74, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # stop
        self.movies.insert(75, obj(self.noria, "noriastop.png", "", "noriabegin.gif"))
        self.movies.insert(76, obj(self.terminator1, "terminator1stop.png", "", "terminator1.gif"))
        self.movies.insert(77, obj(self.terminator2, "terminator2stop.png", "", "terminator2.gif"))
        self.movies.insert(78, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserve
        self.movies.insert(79, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserve
        self.movies.insert(80, obj(self.silos1shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(81, obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(82, obj(self.silos2shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(83, obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(84, obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(85, obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(86, obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(87, obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(88, obj(self.silos1up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(89, obj(self.silos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(90, obj(self.silos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(91, obj(self.silos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(92, obj(self.silos3up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(93, obj(self.silos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(94, obj(self.silos4up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(95, obj(self.silos4do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(95, obj(self.silos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(96, obj(self.silos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(97, obj(self.silos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(98, obj(self.silos6do, "statusfalse.png", "statustrue.png", ""))

        self.editkorm.triggered.connect(self.receptbtnclk)
        self.editzerno.triggered.connect(self.zernobtnclk)
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        # self.dbclient=dbclient
        # for row in self.dbclient.get_recepts():
        #     self.comboBoxRecept.addItem(row[3])
    def dobavkabtnclk(self):
        dialogdobavka = Dialog_dobavka(self.dbclient,config)
        dialogdobavka.exec_()

    def zernobtnclk(self):
        dialogzerno = Dialog_zerno(self.dbclient)
        dialogzerno.exec_()

    def receptbtnclk(self):
        dialogrecept=Dialog_recept(self.dbclient)
        dialogrecept.exec_()

    def connectbtnclk(self):
        #here start recept work!
        pass

    def stopbtnclk(self):
        pass

    def startbtnclk(self):
        self.start()

    def changestatepic(self,index,bit):
        if index==41 and bit==1:
            self.movies[40].switch(bit)
        self.movies[index].switch(bit)


    def start(self):
        self.thread = QThread(self)
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.singal_.connect(self.changestatepic)
        self.thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker._isRunning=True
        self.thread.start()
##
##
########## END class MyApp ENDENDENDENDENDENDENDENDEND


#1. connect to PLC
    #2. connect to SQL
    #3. if allok call login form
    #4.if auth ok then worker.start()

config=CONFIG()
if config.ERROR_READ_INI is False:
     # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
     db=DB(config.ipaddrdb,"oper","Adelante",config.namedb)
     plc=PLC(config.ipaddrplc,config.portplc)

def main():

    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication

    form = MyApp()
    form.show()
    # for row in get_recepts():
    #     print row[3]
    #     form.comboBoxRecept.addItem(row[3])
    app.exec_()                        # and execute the app

if __name__ == "__main__":
    main()
