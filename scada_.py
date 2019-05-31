# -*- coding: utf-8 -*-
#coding: utf-8
import sys
import MySQLdb
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
import time
from PyQt4.QtGui import *
import threading
from designrecept import Ui_Dialog_Recept
from designzerno import Ui_Dialog_Zerno
from designdobavka import Ui_Dialog_Dobavka
import win_inet_pton
import logging
from  ConfigParser import *
from pyModbusTCP.client import ModbusClient
# from vizual import *
# from configroutine import *
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'log.log')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
qtCreatorFile = "design.ui"  # main window design ui
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
DEBUGFLAG=False
COUNTsilosdobavka=5 # от 0
COUNTsiloszerno=9 # от 0
COUNTsiloskorm=5 # от 0
OFFSETsiloszerno=18 #rg18
OFFSETsilosdobavka=28 # rg28
OFFSETsiloskorm=None
OFFSETflagstate=7 # rg7
LASTREGADDR=34
#SQL
IDPRODUCT=0
NAMEPRODUCT=1
IDZERNO=1
IDDOBAVKA=2
IDKORM=3
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
        self.idkorm=[]
        self.idzerno=[]
        self.iddobavka=[]
        self.idmaslo=[]
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Recept()
        self.ui.setupUi(self)
        for row in dbclient.get_product(IDKORM):
             self.idkorm.append(row[IDPRODUCT])
             self.ui.combo1.addItem(row[NAMEPRODUCT])
             self.ui.combo2.addItem(row[NAMEPRODUCT])
             self.ui.combo3.addItem(row[NAMEPRODUCT])
             self.ui.combo4.addItem(row[NAMEPRODUCT])
             self.ui.combo5.addItem(row[NAMEPRODUCT])
             self.ui.combo6.addItem(row[NAMEPRODUCT])
             self.ui.comboname.addItem(row[NAMEPRODUCT])
        for el in self.idkorm:
            print el
        for row in dbclient.get_product(IDZERNO):
            self.ui.combozerno.addItem(row[NAMEPRODUCT])
        for row in dbclient.get_product(IDDOBAVKA):
            self.ui.combodobavka.addItem(row[NAMEPRODUCT])
        self.ui.comboname.currentIndexChanged.connect(self.combonamechange)
        self.ui.combozerno.currentIndexChanged.connect(self.combozernochange)
        self.ui.combodobavka.currentIndexChanged.connect(self.combodobavkachange)
        self.newrecept={}
    def combonamechange(self):
        print unicode(self.ui.comboname.currentText())
    def combozernochange(self):
        print unicode(self.ui.combozerno.currentText())
    def combodobavkachange(self):
        print unicode(self.ui.combodobavka.currentText())
    def btnaddzernoclk(self):
        if unicode(self.combozerno.currentText()) is not "":
            # val=int(self.editzerno.getText())
            # if val is not 0:
            #     self.newrecept.append(str(self.combozerno.currentText()):val)
                pass

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

    def __init__(self, object, imgfalse, imgtrue, gif,flagonclick=False):
        self.imgfalse = imgfalse
        self.imgtrue = imgtrue
        self.qtobj = object

        if gif is not '':
            self.movie = QtGui.QMovie(gif)
        if flagonclick is True:
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
        # self.client = ModbusClient(PLCaddress, port=PLCport)
        self.client=ModbusClient()
        self.client.host(PLCaddress)
        self.client.port(PLCport)
        self.busy=False
        self.okconnection=False
    def checkconnecttcp(self):
        if not self.client.is_open():
            self.connect()
    def connect(self):
        self.okconnection = False
        while not self.okconnection:
            self.okconnection = self.client.open()
            wait(self)
        return   self.okconnection

    def disconnect(self):
        return self.client.close()
    def send(self,rgadr,val):
        self.checkconnect()
        wait(self)
        takeover(self)
        # rq = self.client.write_register(rgadr, val, unit=1)
        # write_single_register(reg_addr, reg_value)[source]
        self.client.write_single_register(rgadr,val)
        free(self)
    def read(self,rgadr):
        self.checkconnecttcp()
        wait(self)
        takeover(self)
        # read_holding_registers(reg_addr, reg_nb=1)
        # result= self.client.read_holding_registers(rgadr,1,unit=1)
        result=self.client.read_holding_registers(rgadr,1)
        free(self)
        # return result.getRegister(0)
        return result[0]
    def readcoil(self,bit):
        self.checkconnecttcp()
        wait(self)
        takeover(self)
            # type: (object) -> object
        # incoil=self.client.read_coils(bit,1,unit=0x01)
        # read_coils(bit_addr, bit_nb=1)
        incoil=self.client.read_coils(bit,1)
        free(self)
        # return incoil.bits[0]
        return incoil[0]
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
class plcrecept(object):
    def __init__(self):
        self.count=0
        self.selectkormnumbanka=0
        self.masloneed=0
        self.handdobavka=0
        self.step=0
        self.listzernoneed=plclist()
        self.listdobavkaneed = plclist()

    def setstep(self,num):
        self.step=num
    def stepnow(self,num):
        if self.step is num:
            return True
        else:
            return False
    def deccount(self):
        if self.count is not 0:
            self.count-=1

class PLC(object):
    def __init__(self,mbclient):
        self.state=0
        self.cmd=0 # регистр команд
        self.ret=0 # регистр return ответа ПЛК
        self.mbclient=mbclient
        self.listplccoils=plclist()
        self.listplcrg16=plclist()
        self.recept = plcrecept()
    def send_cmd(self,cmd):
        self.send_ret(0)
        wreg = self.listplcrg16.getelement(0)
        breg=wreg&0xFF00
        self.mbclient.send(0,cmd|breg)
    def send_ret(self,val):
        wreg = self.listplcrg16.getelement(1)
        breg = wreg & 0xFF00
        self.mbclient.send(1,val|breg)
    def get_state(self):
        # wreg=self.listplcrg16.getelement(1)
        wreg=mbclient.read(1)
        # print "getstate >> "+str(wreg)
        if type(wreg) is  None:
            self.state = 0
        else:
            self.state = wreg & 0x00FF
    def waitstate(self,needstate_):
        needstate_=1000
        while self.state is  needstate_:

            self.get_state()
            delay(1000)
        print "state is now "+str(self.state)
        self.send_ret(0)
        print "state is now " + str(self.state)
class ThreadPullPLCList(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning=False
    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)
    def process(self):
        print "+thread ThreadPullPLCList started"
        while self._isRunning is True:
            listcoillocal_ = range(100)
            listweightzernolocal_=range(10)
            listweightdobavkalocal_ = range(6)
            for i in range(0,COUNTsiloszerno):
                listweightzernolocal_.insert(i,plcglobal.listplcrg16.getelement(i+OFFSETsiloszerno))
            plcglobal.recept.listzernoneed.pull(listweightzernolocal_)
            for i in range(0,COUNTsilosdobavka):
                listweightdobavkalocal_.insert(i, plcglobal.listplcrg16.getelement(i + OFFSETsilosdobavka))
            plcglobal.recept.listdobavkaneed.pull(listweightdobavkalocal_)
            for i in range(0, 6):
                for j in range(0, 15):
                    delay(1000)
                    listcoillocal_.insert( i*16+j,getbit(plcglobal.listplcrg16.getelement(i + OFFSETflagstate), j))
            plcglobal.listplccoils.pull(listcoillocal_)

        print "-thread ThreadPullPLCList done"
        self.finished.emit()
        def stop(self):
            self._isRunning = False
class ThreadGetPLC(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning=False
    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)
    def process(self):
        print "+thread ThreadGetPLC started"
        while self._isRunning is True:
            mbclient.checkconnecttcp()
            listrg16local_ = range(LASTREGADDR)
            for i in range(0,LASTREGADDR):
                delay(1000)
                listrg16local_.insert(i, mbclient.read(i))
            plcglobal.listplcrg16.pull(listrg16local_)
        print "-thread ThreadGetPLC done"
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
        print "+thread ThreadVizual2level done"
        self.finished.emit()
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
        print "+thread ThreadWorkZames started"
        while  self._isRunning is True:
            print "Ждем необходимый статус ПЛК  <Ожидание команды>"
            plcglobal.waitstate(1)
            print "ПЛК в статусе  <Ожидание команды> !"
            self.s2.emit()
            plcglobal.send_cmd(111)
            print "Отправлен Пакет данных для рецепта"
            print "Отправлена команда перенастроить <Приемка комбикорма>"
            print "Ожидание ответа от ПЛК"
            plcglobal.waitstate(1)
            print "Получен ответ от ПЛК <Приемка комбикорма перенастроена>"
            while(plcglobal.recept.count is not 0):
                print "Отправлена команда на изготовление рецепта"
                plcglobal.send_cmd(1)
                print "Ожидание ответа от ПЛК"
                plcglobal.waitstate(1)
                print "ПЛК завершил завешивание, ПЛК ожидает команду"
                plcglobal.recept.deccount()
            print "Отправлена команда ПЛК <Конец сессии>"
            plcglobal.send_cmd(222)
            print "Ожидание ответа от ПЛК"
            plcglobal.waitstate(1)
            print "Получен ответ от ПЛК <Конец сессии>"
            print "Счетчик <Количество замесов> достиг нуля- изготовление рецепта завершено!"
            self._isRunning = False
            # plcglobal.get_state()
            # print "step case is " + str(plcglobal.recept.step)
            # if plcglobal.recept.stepnow(0):
            #     print "step 0"
            #     if plcglobal.state is 1:
            #         # print 'plcglobal.listrg16[1]=' + str(plcglobal.listplcrg16.list[1])
            #         print 'plcstate=' + str(plcglobal.state)
            #         self.s2.emit()
            #         if plcglobal.recept.count is 0:
            #             plcglobal.recept.setstep(3)
            #         if plcglobal.recept.selectkormnumbanka is 0:
            #             plcglobal.recept.setstep(3)
            #         plcglobal.send_cmd(2)
            #         print "Ожидание ответа на <Установить № Банки комбикорма> от ПЛК"
            #         while plcglobal.state is not 2:
            #             delay(1000)
            #         print "<Установить № Банки комбикорма от ПЛК> - успешно "
            #         plcglobal.send_cmd(1)
            #         plcglobal.recept.setstep(1)
            #         plcglobal.send_ret(0)  # обнуляем ret
            #     else:
            #         pass
            #          # print("ПЛК занят, ожидание ПЛК")
            # if plcglobal.recept.stepnow(1):
            #     print "step 1"
            #     if plcglobal.state is 1:
            #         plcglobal.send_ret(0)# обнуляем ret
            #         plcglobal.recept.deccount()
            #         if plcglobal.recept.count is 0:
            #             plcglobal.recept.setstep(3)
            #         else:
            #             plcglobal.recept.setstep(0)
            # if plcglobal.recept.stepnow(3):
            #     print "step 3"
            #     print("Цикл отправки команд на замес закончен")

                # self._isRunning=False
                # plcglobal.recept.setstep(0)
        self.finished.emit()
        print "-thread ThreadWorkZames is done"
    def stop(self):
        self._isRunning = False
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    movies = []
    moviesL2=[]
    def __init__(self,dbclient,mbclient,plc_):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)
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

        self.interface_=[]
        self.interface_.append(obj(self.siloskorm1, "silos.png","silos_active.png", "",True))
        self.interface_.append(obj(self.siloskorm2, "silos.png", "silos_active.png", "",True))
        self.interface_.append(obj(self.siloskorm3, "silos.png", "silos_active.png", "",True))
        self.interface_.append(obj(self.siloskorm4, "silos.png", "silos_active.png", "",True))
        self.interface_.append(obj(self.siloskorm5, "silos.png", "silos_active.png", "",True))
        self.interface_.append(obj(self.siloskorm6, "silos.png", "silos_active.png", "",True))
        # self.reinitmbtcp()
        self.editkorm.triggered.connect(self.receptbtnclk)
        self.editzerno.triggered.connect(self.zernobtnclk)
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        self.actionexit.triggered.connect(self.exitclk)
        self.activethreads=[]
        self.startThreadVisual1Level(QThread(self),self.plc)
        self.startThreadVizual2level(QThread(self))
        self.startThreadGetPLC(QThread(self))
        self.startThreadPullPLCList(QThread(self))

        if dbclient is not False:
            self.dbclient=dbclient
        for row in self.dbclient.get_product(IDKORM):
            self.comboBoxRecept.addItem(row[NAMEPRODUCT])
    def reinitmbtcp(self):
        self.mbclient.checkconnect()
    def exitclk(self):
        for i in range(0,len(self.activethreads)):
            self.activethreads[i]._isRunning=False
        pass
        sys.exit()
    def dobavkabtnclk(self):
        dialogdobavka = Dialog_dobavka(self.dbclient,config)
        dialogdobavka.exec_()
    def zernobtnclk(self):
        dialogzerno = Dialog_zerno(self.dbclient)
        dialogzerno.exec_()
    def receptbtnclk(self):
        dialogrecept=Dialog_recept(self.dbclient)
        dialogrecept.exec_()
    def stopbtnclk(self):
        pass
    def startbtnclk(self):
        self.startThreadWorkZames(QThread(self))
        print "START CLICK!"
    def startThreadVisual1Level(self,thread_,plc):
        print "Try start thread visual1level"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.visual1level = ThreadVisual1Level(plc)
        self.visual1level.moveToThread(thread)
        self.visual1level.s1.connect(self.visual1levelslot)
        thread.started.connect(self.visual1level.process)
        self.visual1level.finished.connect(thread.quit)
        self.visual1level.finished.connect(self.visual1level.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.visual1level._isRunning = True
        thread.start()
    def startThreadVizual2level(self,thread_):# визулизация шиберов- по состоянию концевиков
        print "Try start thread visual2level"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.vizual2level = ThreadVizual2level()
        self.vizual2level.moveToThread(thread)
        self.vizual2level.s3.connect(self.visual2levelslot)
        thread.started.connect(self.vizual2level.process)
        self.vizual2level.finished.connect(thread.quit)
        self.vizual2level.finished.connect(self.vizual2level.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.vizual2level._isRunning = True  # визулизация шиберов- по состоянию концевиков
        thread.start()
    def startThreadGetPLC(self,thread_):
        print "Try start thread ThreadGetPLC"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.getplc = ThreadGetPLC()
        self.getplc.moveToThread(thread)
        thread.started.connect(self.getplc.process)
        self.getplc.finished.connect(thread.quit)
        self.getplc.finished.connect(self.vizual2level.deleteLater)
        thread.finished.connect(thread.deleteLater)

        self.getplc._isRunning = True
        thread.start()
    def startThreadPullPLCList(self,thread_):
        print "Try start thread ThreadPullPLCList"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.pullplclist = ThreadPullPLCList()
        self.pullplclist.moveToThread(thread)
        thread.started.connect(self.pullplclist.process)
        self.pullplclist.finished.connect(thread.quit)
        self.pullplclist.finished.connect(self.pullplclist.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.pullplclist._isRunning = True
        thread.start()
    def startThreadWorkZames(self,thread_):
        print "Try start thread ThreadWorkZames"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.workerzames = ThreadWorkZames(self.plc, self.mbclient)
        self.workerzames.moveToThread(thread)
        self.workerzames.s2.connect(self.workzamesslot)
        thread.started.connect(self.workerzames.process)
        self.workerzames.finished.connect(thread.quit)
        self.workerzames.finished.connect(self.workerzames.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.workerzames._isRunning = True
        thread.start()
    def visual1levelslot(self,index,bit):

        self.movies[index].switch(bit)
        if self.mbclient.okconnection:
            self.connectstatuslabel.setText(u"Соединение с ПЛК..Соединено")
            if self.plc.state is  0:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК занят <" + str(self.plc.state)+u">")
            if self.plc.state is  1:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК ждет команды на взвешивание <" + str(self.plc.state)+u">")
            if self.plc.state is  2:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК настроил приемку зерна <" + str(self.plc.state)+u">")
        else:
            self.connectstatuslabel.setText(u"Соединение с ПЛК..Разорвано")
            self.plcstatuslabel.setText(u"Статус ПЛК..Неизвестно")

        self.labelbanka3.setText(str(self.plc.recept.listzernoneed.getelement(2)))
        self.labelbanka4.setText(str(self.plc.recept.listzernoneed.getelement(3)))
        self.labelbanka5.setText(str(self.plc.recept.listzernoneed.getelement(4)))
        self.labelbanka6.setText(str(self.plc.recept.listzernoneed.getelement(5)))
        self.labelbanka7.setText(str(self.plc.recept.listzernoneed.getelement(6)))
        self.labelbanka8.setText(str(self.plc.recept.listzernoneed.getelement(7)))
        self.labelbanka9.setText(str(self.plc.recept.listzernoneed.getelement(8)))
        self.labelbanka10.setText(str(self.plc.recept.listzernoneed.getelement(9)))

        self.labelbanka11.setText(str(self.plc.recept.listdobavkaneed.getelement(2)))
        self.labelbanka12.setText(str(self.plc.recept.listdobavkaneed.getelement(3)))
        self.labelbanka13.setText(str(self.plc.recept.listdobavkaneed.getelement(4)))
        self.labelbanka14.setText(str(self.plc.recept.listdobavkaneed.getelement(5)))
        self.labelbanka15.setText(str(self.plc.recept.listdobavkaneed.getelement(6)))
        self.labelbanka16.setText(str(self.plc.recept.listdobavkaneed.getelement(7)))
        self.labelbanka17.setText(str(self.plc.recept.masloneed))

        # if self.plc.state is 0 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ожидание команды")
        # if self.plc.state is 1 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Закончил загрузку весов")
        # if self.plc.state is 2 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ошибка")
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
    def workzamesslot(self):
        print('start! slot from threadPLCZames signal_')
        self.plc.recept.selectkormnumbanka=0

        print "select kormsilos = "+str(self.plc.recept.selectkormnumbanka)
        self.plc.recept.count=1
        for i in range(0, 5):
            if self.interface_[i].state is True:
                self.plc.recept.selectkormnumbanka = i + 1
                break
            else:
                self.plc.recept.selectkormnumbanka = 0
                self.plc.recept.count=0
        self.mbclient.send(18, int(self.zernoedit3.text()))
        self.mbclient.send(19, int(self.zernoedit4.text()))
        self.mbclient.send(20, int(self.zernoedit5.text()))
        self.mbclient.send(21, int(self.zernoedit6.text()))
        self.mbclient.send(22, int(self.zernoedit7.text()))
        self.mbclient.send(23, int(self.zernoedit8.text()))
        self.mbclient.send(24, int(self.zernoedit9.text()))
        self.mbclient.send(25, int(self.zernoedit10.text()))
        self.mbclient.send(26, int(self.dobavkaedit1.text()))
        self.mbclient.send(27, int(self.dobavkaedit2.text()))
        self.mbclient.send(28, int(self.dobavkaedit3.text()))
        self.mbclient.send(29, int(self.dobavkaedit4.text()))
        self.mbclient.send(30, int(self.dobavkaedit5.text()))
        self.mbclient.send(31, int(self.dobavkaedit6.text()))
        self.mbclient.send(32, int(self.masloedit.text()))
        self.mbclient.send()
        # self.mbclient.send(18, 110)
        # self.mbclient.send(19, 220)
        # self.mbclient.send(20, 330)
        # self.mbclient.send(21, 440)
        # self.mbclient.send(22, 550)
        # self.mbclient.send(23, 660)
        # self.mbclient.send(24, 770)
        # self.mbclient.send(25, 880)
        #
        #
        # self.mbclient.send(0, 1)  # запись в регистр dbcmd - команда для ПЛК на замес
        # self.mbclient.send(1, 0)  # запись в регистр ret - 0
    # def onclicksiloskorm1:
    #     self.siloskorm1.
config=CONFIG()
if config.ERROR_READ_INI is False:
     # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
     if DEBUGFLAG is False:
         db=DB(config.ipaddrdb,"root","root",config.namedb)
         # mbclient=MBclient(config.ipaddrplc,config.portplc)
         mbclient=MBclient('10.0.6.10','502')
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
