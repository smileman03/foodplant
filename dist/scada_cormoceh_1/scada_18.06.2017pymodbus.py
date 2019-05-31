# -*- coding: utf-8 -*-
#coding: utf-8
import sys
import MySQLdb
from PyQt4 import QtCore, QtGui, uic
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from PyQt4.QtCore import QThread
import time
from PyQt4.QtGui import *
import threading
from designrecept import Ui_Dialog_Recept
from designzerno import Ui_Dialog_Zerno
from designdobavka import Ui_Dialog_Dobavka
import logging
from  ConfigParser import *
# from vizual import *
# from configroutine import *
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'log.log')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
qtCreatorFile = "design.ui"  # main window design ui
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

DEBUGFLAG=False

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
class DB:
    def __init__(self,baseaddress_,user_,passw_,db_):
        self.db = MySQLdb.connect(host=baseaddress_, user=user_, passwd=passw_, db=db_, charset='utf8')
        # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
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
             self.ui.comboname.addItem(row[1])
        self.ui.comboname.currentIndexChanged.connect(self.combonamechange)
    def combonamechange(self):
        print unicode(self.ui.comboname.currentText())
        # for i in range(self.ui.comboname.count()):
        #     print unicode(self.ui.comboname.itemText(i))
class Dialog_zerno(QDialog,Ui_Dialog_Zerno):
    def __init__(self,dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Zerno()
        self.ui.setupUi(self)
        # for row in get_product():
        #     print row[3]
        #     self.combozerno.addItem(row[3])
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
             self.ui.comboname.addItem(row[1])
def takeover(object):
    object.busy=True
def free(object):
    object.busy=False
def wait(object):
    while(object.busy is True):
        delay(10)
def delay(tick):
    for i in range(0,tick):
        pass
def getbit(reg16, indexbit):
    if reg16 & (1 << indexbit) is not 0:
        return 1
    else:
        return 0
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
        if DEBUGFLAG is True:
            self.qtobj.mousePressEvent = self.onclicked_

    def onclicked_(self, event):
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
class MBclient(object):
    def __init__(self,PLCaddress,PLCport):
        self.client = ModbusClient(PLCaddress, port=PLCport)
        self.busy=False

    def connect(self):
        return self.client.connect()
    def disconnect(self):
        return self.client.close()
    def send(self,rgadr,val):
        wait(self)
        takeover(self)
        rq = self.client.write_register(rgadr, val, unit=1)
        free(self)
    def read(self,rgadr):
        wait(self)
        takeover(self)
        result= self.client.read_holding_registers(rgadr,1,unit=1)
        free(self)
        return result.getRegister(0)
    def readcoil(self,bit):
        wait(self)
        takeover(self)
            # type: (object) -> object
        incoil=self.client.read_coils(bit,1,unit=0x01)
        free(self)
        return incoil.bits[0]
    def getbyteL(self,word):
        HH=0b00001111
        return word&HH
    def getbyteH(self,word):
        LL=0b11110000
        return word&LL

class plclist(object):
    def __init__(self):
        self.list = []
        self.busy = False
        self.init = False

    def reinit(self):
        wait(self)
        takeover(self)
        del self.list[:]
        free(self)

    def pull(self, list_):
        wait(self)
        takeover(self)
        self.list = list_
        free(self)
        self.init = True

    def getelement(self, index_):
        wait(self)
        takeover(self)
        if self.init is True:
            free(self)
            return self.list[index_]
        else:
            free(self)
            return 0
class PLC(object):
    def __init__(self,mbclient):
        self.step=0
        self.count=0
        self.state=0
        self.cmd=0
        self.ret=0
        self.mbclient=mbclient
        self.listplccoils=plclist()
        self.listplcrg16=plclist()
    def send_cmd(self,cmd):
        wreg = self.mbclient.read(0)
        breg=wreg&0xF0
        self.mbclient.send(0,cmd|breg)
    def send_ret(self,val):
        wreg = self.mbclient.read(1)
        breg = wreg & 0xF0
        self.mbclient.send(1,val|breg)
    def get_state(self):
        wreg=self.mbclient.read(1)
        # print "getstate >> "+str(wreg)
        if type(wreg) is  None:
            self.state = 0
        else:
            self.state = wreg & 0x0F
# class ThreadPullPLCList(QtCore.QObject):
#     finished = QtCore.pyqtSignal()
#     s4 = QtCore.pyqtSignal(int)
#     _isRunning=False
#     @QtCore.pyqtSlot()
#     def __init__(self):
#         QtCore.QObject.__init__(self)
#     def process(self):
#         print "=thread ThreadPullPLCList started"
#         while self._isRunning is True:
#             for i in range(0, 6):
#                 for j in range(0, 15):
#                     self.plc.liststate[i * 16 + j] = getbit(self.plc.listrg16[i + 7], j)
#         delay(1000)
#         def stop(self):
#             self._isRunning = False
class ThreadGetPLC(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    s0 = QtCore.pyqtSignal(int)
    _isRunning=False
    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)
    def process(self):
        print "+thread ThreadGetPLC started"
        while self._isRunning is True:
            listrg16local_ = range(34)
            listcoillocal_ = range(100)
            for i in range(0,34):
                delay(1000)
                listrg16local_.insert(i, mbclient.read(i))
            plcglobal.listplcrg16.pull(listrg16local_)
            for i in range(0, 6):
                for j in range(0, 15):
                    delay(1000)
                    listcoillocal_.insert( i*16+j,getbit(plcglobal.listplcrg16.getelement(i + 7), j))
            plcglobal.listplccoils.pull(listcoillocal_)
    def stop(self):
        self._isRunning = False
class ThreadVisual1Level(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    s1= QtCore.pyqtSignal(int,int)
    _isRunning=False
    @QtCore.pyqtSlot()
    def __init__(self,plc):
        QtCore.QObject.__init__(self)
        self.plc=plc
    def process(self):
        print "+thread ThreadVisual1Level started"
        while  self._isRunning is True:
            for i in range(0,98):
                delay(10000)
                self.s1.emit(i,plcglobal.listplccoils.getelement(i))
        print '-thread ThreadVisual1Level FINISHED'
        self.finished.emit()
    def stop(self):
        self._isRunning = False
class ThreadVizual2level(QtCore.QObject):# визулизация шиберов- по состоянию концевиков
    finished = QtCore.pyqtSignal()
    s3= QtCore.pyqtSignal()
    _isRunning=False
    @QtCore.pyqtSlot()
    def process(self):
        print "+thread ThreadVizual2level started"
        while  self._isRunning is True:
            self.s3.emit()
            delay(10000)
            # print 'FINISHED'
        # self.finished.emit()
    def stop(self):
        self._isRunning = False
class ThreadWorkZames(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    s2 = QtCore.pyqtSignal()
    _isRunning=False
    def __init__(self,plc_,mbclient_):
        QtCore.QObject.__init__(self)
        self.mbclient=mbclient_
        self.plc=plc_
    @QtCore.pyqtSlot()
    def process(self):
        print "=thread ThreadWorkZames started"
        while  self._isRunning is True:
            delay(10000)
            plcglobal.get_state()
            print "step case is " + str(self.plc.step)
            if self.plc.step is 0:
                print "step 0"
                if self.plc.state is 1:
                    for i in range(0,33):
                        print "plcglobal.listplcrg16["+str(i)+"]= "+str(plcglobal.listplcrg16.list[i])
                        print self.mbclient.read(i)
                    # while(self.plc.listrg16[32] is not 255):
                    #     pass

                    print 'plcglobal.listrg16[1]=' + str(plcglobal.listplcrg16.list[1])
                    print 'plcstate=' + str(plcglobal.state)
                    # while(plcglobal.listrg16[33] is not 255):
                    #     pass
                    mbclient.send(1, 0)
                    self.s2.emit()
                    self.plc.step=1
                    self.plc.send_ret(0)  # обнуляем ret
                else:
                    pass
                     # print("ПЛК занят, ожидание ПЛК")
            if self.plc.step is 1:
                print "step 1"
                if self.plc.state is 1:
                    self.plc.send_ret(0)# обнуляем ret
                    self.plc.count-=1
                    if self.plc.count is 0:
                        self.plc.step=3
                    else:
                        self.plc.step=0
            if self.plc.step is 3:
                print "step 3"
                print("Цикл отправки команд на замес закончен")
                self._isRunning=False
                self.stop()
        print "thread ThreadWorkZames is done"
    def stop(self):
        self._isRunning = False
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    movies = []
    moviesL2=[]
    def __init__(self,dbclient,mbclient,plc_):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.connectflag = False
        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)
        self.connectbtn.clicked.connect(self.connectbtnclk)
        self.mbclient=mbclient
        self.plc=plc_
        self.moviesL2.insert(0, obj(self.ves1shiber, "vesishiberclose.png", "vesishiberopen.png", ""))
        self.moviesL2.insert(1, obj(self.ves2shiber, "vesishiberclose.png", "vesishiberopen.png", ""))
        self.moviesL2.insert(2, obj(self.ves3shiber, "vesishiberclose.png", "vesishiberopen.png", ""))
        self.moviesL2.insert(3, obj(self.silos1dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "") )
        self.moviesL2.insert(4, obj(self.silos2dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(5, obj(self.silos3dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(6, obj(self.silos4dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(7, obj(self.silos5dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(8, obj(self.silos6dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(9, obj(self.silos1shiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(10, obj(self.silos2shiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(11, obj(self.silos4shiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        self.moviesL2.insert(12, obj(self.silos5shiber, "silosshiberclose.png", "silosshiberopen.png", ""))
        # reg7 PLC1 (dobavki)
        self.movies.insert(0, obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(1, obj(self.dobavkisilos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(2, obj(self.silos1dobavkaopen, "statusminifalse.png", "", "statusminitrue.png"))
        self.movies.insert(3, obj(self.silos1dobavkaclose, "statusminifalse.png", "", "statusminitrue.png"))
        self.movies.insert(4, obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(5, obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(6, obj(self.silos2dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(7, obj(self.silos2dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(8, obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", ""))
        #reg7 PLC2(dobavki)
        self.movies.insert(9, obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(10, obj(self.silos3dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(11, obj(self.silos3dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(12, obj(self.dobavkisilos4up, "statusfalse.png", "statu9strue.png", ""))
        self.movies.insert(13, obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(14, obj(self.silos4dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(15, obj(self.silos4dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        #reg8 PLC3(dobavki)
        self.movies.insert(16, obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(17, obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(18, obj(self.silos5dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(19, obj(self.silos5dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(20, obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(21, obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(22, obj(self.silos6dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(23, obj(self.silos6dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        #reg8 PLC4 dobavki
        self.movies.insert(24, obj(self.flex1, "flex1stop.png", "flex1run.png", ''))
        self.movies.insert(25, obj(self.flex2, "flex2stop.png", "flex2run.png", ''))
        self.movies.insert(26, obj(self.flex3, "flex3stop.png", "flex3run.png", ''))
        self.movies.insert(27, obj(self.flex4, "flex4stop.png", "flex4run.png", ''))
        self.movies.insert(28, obj(self.flex5, "flex5stop.png", "flex5run.png", ''))
        self.movies.insert(29, obj(self.flex6, "flex6stop.png", "flex6run.png", ''))
        self.movies.insert(30, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        self.movies.insert(31, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        #reg9 PLC5 dobavki
        self.movies.insert(32, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button auto
        self.movies.insert(33, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button ruchno
        self.movies.insert(34, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # button stop
        self.movies.insert(35, obj(self.flexload, "flexloadstop.png", "flexloadrun.png", ''))
        self.movies.insert(36, obj(self.bunkerloaddo, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(37, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # open shiber vesi knopka
        self.movies.insert(38, obj(self.ves3sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(39, obj(self.ves3sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(40, obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", ''))
        #reg9 PLC6(mixer)
        self.movies.insert(41, obj(self.mixersensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(42, obj(self.mixersensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(43, obj(self.mixer, "mixerstop.png", '', "mixerbegin.gif"))
        self.movies.insert(44, obj(self.mixer_2, "mixer2_stop.png", "", "mixer2_run"))  # mixer2
        self.movies.insert(45, obj(self.mixerbunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(46, obj(self.mixershnek1, "shnek_hor_stop.gif", "", "shnek_hor_begin.gif"))
        self.movies.insert(78, obj(self.mixershnek2, "shnek_nakl_stop.gif",  "","shnek_nakl_begin.gif")) #
        #reg10 PLC7 (zerno)
        self.movies.insert(48, obj(self.ves1sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(49, obj(self.ves1sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(50, obj(self.ves2sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(51, obj(self.ves2sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(52, obj(self.ves1bunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(53, obj(self.ves2bunkersens1, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(54, obj(self.ves2bunkersens2, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(55, obj(self.autokombikorm, "statusfalse.png", "statustrue.png", ""))  # auto button
        #reg10 PLC8(zerno)
        self.movies.insert(56, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv shnek1
        self.movies.insert(57, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv shnek2
        self.movies.insert(58, obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", ""))
        self.movies.insert(59, obj(self.zernoshnek4, "shnek4zernostop.png", "shnek4zernorun.png", ""))
        self.movies.insert(60, obj(self.zernoshnek5, "shnek5zernostop.png", "shnek5zernorun.png", ""))
        self.movies.insert(61, obj(self.zernoshnek6, "shnek6zernostop.png", "shnek6zernorun.png", ""))
        self.movies.insert(62, obj(self.zernoshnek7, "shnek7zernostop.png", "shnek7zernorun.png", ""))
        self.movies.insert(63, obj(self.zernoshnek8, "shnek8zernostop.png", "shnek8zernorun.png", ""))
        #reg11 PLC9 (zerno)
        self.movies.insert(64, obj(self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""))
        self.movies.insert(65, obj(self.zernoshnek10, "shnek10zernostop.png", "shnek10zernorun.png", ""))
        self.movies.insert(66, obj(self.drobilka1, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(67, obj(self.drobilka2, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(68, obj(self.ves2shnek, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(69, obj(self.ves1shnek1, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(70, obj(self.ves1shnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(71, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserv
        #reg11 PLC10(kombikorm)
        self.movies.insert(72, obj(self.klapan1, "klapan1false.png", "klapan1true.png", ""))
        self.movies.insert(73, obj(self.klapan2, "klapan2false.png", "", "klapan2true.png"))
        self.movies.insert(74, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # stop
        self.movies.insert(75, obj(self.noria, "noriastop.png", "", "noriabegin.gif"))
        self.movies.insert(76, obj(self.terminator1, "terminator1stop.png", "", "terminator1.gif"))
        self.movies.insert(77, obj(self.terminator2, "terminator2stop.png", "", "terminator2.gif"))
        self.movies.insert(78, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserve
        self.movies.insert(79, obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  # reserve
        #reg12 PLC11(kombikorm)
        self.movies.insert(80, obj(self.silos1shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(81, obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(82, obj(self.silos2shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(83, obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(84, obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(85, obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(86, obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(87, obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        #reg12 PLC12(kombikorm)
        self.movies.insert(88, obj(self.silos1up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(89, obj(self.silos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(90, obj(self.silos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(91, obj(self.silos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(92, obj(self.silos3up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(93, obj(self.silos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(94, obj(self.silos4up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(95, obj(self.silos4do, "statusfalse.png", "statustrue.png", ""))
        #reg13 PLC13(kombokorm)
        self.movies.insert(95, obj(self.silos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(96, obj(self.silos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(97, obj(self.silos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(98, obj(self.silos6do, "statusfalse.png", "statustrue.png", ""))
        #reg13 PLC14
        self.movies.insert(99, obj(self.autokombikorm, "statusfalse.png","statustrue.png", ""))
        self.movies.insert(100, obj(self.ruchnokombikorm, "statusfalse.png","statustrue.png", ""))
       # self.movies.insert(101, obj(self.autoruchnokombikorm, "statusfalse.png","statustrue.png", ""))

        self.editkorm.triggered.connect(self.receptbtnclk)
        self.editzerno.triggered.connect(self.zernobtnclk)
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        self.startThreadVisual1Level(QThread(self),self.plc)
        self.startThreadVizual2level(QThread(self))
        self.startThreadGetPLC(QThread(self))
        if dbclient is not False:
            self.dbclient=dbclient
            for row in self.dbclient.get_recepts():
                self.comboBoxRecept.addItem(row[3])
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
        pass
    def stopbtnclk(self):
        pass
    def startbtnclk(self):
        self.threadzames = QThread(self)
        self.workerzames = ThreadWorkZames(self.plc,self.mbclient)
        self.workerzames.moveToThread(self.threadzames)
        self.workerzames.s2.connect(self.sendzames)
        self.threadzames.started.connect(self.workerzames.process)
        self.workerzames.finished.connect(self.threadzames.quit)
        self.workerzames.finished.connect(self.workerzames.deleteLater)
        self.threadzames.finished.connect(self.threadzames.deleteLater)
        self.workerzames._isRunning = True
        self.threadzames.start()
        print "START CLICK!"
    def startThreadVisual1Level(self,thread,plc):
        print "Try start thread visual1level"
        self.thread1 = thread
        self.visual1level = ThreadVisual1Level(plc)
        self.visual1level.moveToThread(self.thread1)
        self.visual1level.s1.connect(self.visual1levelslot)
        self.thread1.started.connect(self.visual1level.process)
        self.visual1level.finished.connect(self.thread1.quit)
        self.visual1level.finished.connect(self.visual1level.deleteLater)
        self.thread1.finished.connect(self.thread1.deleteLater)
        self.visual1level._isRunning = True
        self.thread1.start()
    def startThreadVizual2level(self,thread):
        print "Try start thread visual2level"
        self.thread2 = thread  # визулизация шиберов- по состоянию концевиков
        self.vizual2level = ThreadVizual2level()
        self.vizual2level.moveToThread(self.thread2)
        self.vizual2level.s3.connect(self.visual2levelslot)
        self.thread2.started.connect(self.vizual2level.process)
        self.vizual2level.finished.connect(self.thread2.quit)
        self.vizual2level.finished.connect(self.vizual2level.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.vizual2level._isRunning = True  # визулизация шиберов- по состоянию концевиков
        self.thread2.start()
    def startThreadGetPLC(self,thread):
        print "Try start thread ThreadGetPLC"
        self.thread3 = thread
        self.getplc = ThreadGetPLC()
        self.getplc.moveToThread(self.thread3)
        self.getplc.s0.connect(self.getstateplcslot)
        self.thread3.started.connect(self.getplc.process)
        self.getplc._isRunning = True
        self.thread3.start()
    def visual1levelslot(self,index,bit):
         self.movies[index].switch(bit)
    def visual2levelslot(self): # визулизация шиберов- по состоянию концевиков
        def shiber_switch(obj1,obj2,obj3):
            if obj2.state is True:  #если включен концевик "открыто"
                obj1.switch(1)      # открыть шибер
            if obj3.state is True: #если включен концевик "закрыто"
                obj1.switch(0)   # закрыть шибер

        shiber_switch(self.moviesL2[0],self.movies[48],self.movies[49])
        shiber_switch(self.moviesL2[1], self.movies[50], self.movies[51])
        shiber_switch(self.moviesL2[2], self.movies[38], self.movies[39])
        shiber_switch(self.moviesL2[3], self.movies[2], self.movies[3])
        shiber_switch(self.moviesL2[4], self.movies[6], self.movies[7])
        shiber_switch(self.moviesL2[5], self.movies[10], self.movies[11])
        shiber_switch(self.moviesL2[6], self.movies[14], self.movies[15])
        shiber_switch(self.moviesL2[7], self.movies[18], self.movies[19])
        shiber_switch(self.moviesL2[8], self.movies[22], self.movies[23])
        shiber_switch(self.moviesL2[9], self.movies[80], self.movies[81])
        shiber_switch(self.moviesL2[10], self.movies[82], self.movies[83])
        shiber_switch(self.moviesL2[11], self.movies[84], self.movies[85])
        shiber_switch(self.moviesL2[12], self.movies[86], self.movies[87])
        shiber_switch(self.movies[40],   self.movies[41], self.movies[42])
    def sendzames(self):
        print('send go')
        # self.mbclient.send(18, self.zernoedit3)
        # self.mbclient.send(19, self.zernoedit4)
        # self.mbclient.send(20, self.zernoedit5)
        # self.mbclient.send(21, self.zernoedit6)
        # self.mbclient.send(22, self.zernoedit7)
        # self.mbclient.send(23, self.zernoedit8)
        # self.mbclient.send(24, self.zernoedit9)
        # self.mbclient.send(25, self.zernoedit10)
        # self.mbclient.send(26, self.dobavkaedit1)
        # self.mbclient.send(27, self.dobavkaedit2)
        # self.mbclient.send(28, self.dobavkaedit3)
        # self.mbclient.send(29, self.dobavkaedit4)
        # self.mbclient.send(30, self.dobavkaedit5)
        # self.mbclient.send(31, self.dobavkaedit6)
        # self.mbclient.send(32, self.masloedit)
        self.plc.count=1
        self.mbclient.send(18, 110)
        self.mbclient.send(19, 220)
        self.mbclient.send(20, 330)
        self.mbclient.send(21, 440)
        self.mbclient.send(22, 550)
        self.mbclient.send(23, 660)
        self.mbclient.send(24, 770)
        self.mbclient.send(25, 880)
        #
        #
        # self.mbclient.send(0, 1)  # запись в регистр dbcmd - команда для ПЛК на замес
        # self.mbclient.send(1, 0)  # запись в регистр ret - 0
    def getstateplcslot(self, i):
        self.plc.listrg16.insert(i, self.mbclient.read(i))

config=CONFIG()
if config.ERROR_READ_INI is False:
     # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
     if DEBUGFLAG is False:
         db=DB(config.ipaddrdb,"root","root",config.namedb)
         # mbclient=MBclient(config.ipaddrplc,config.portplc)
         mbclient=MBclient('10.0.6.10','502')
         print mbclient.read(0)
         plcglobal = PLC(mbclient)
     else:
         db = DB(config.ipaddrdb,"root","root",config.namedb)
         mbclient= False
         plcglobal=False
def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MyApp(db,mbclient,plcglobal)
    form.show()
    app.exec_()                        # and execute the app

if __name__ == "__main__":
    main()
