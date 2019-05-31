# -*- coding: utf-8 -*-
#coding: utf-8
import sys
import MySQLdb
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
import time
from PyQt4.QtGui import *
import threading
from designrecept import Ui_Dialog_recept
from designkorm import Ui_Dialog_Korm
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
DEBUGFLAG=True
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
COMMAND_INIT = 111
COMMAND_MIXER_ON=41
COMMAND_MIXER_OFF=40
COMMAND_MIXER_UNLOAD=42
COMMAND_LINE1_START=101
COMMAND_LINE1_STOP=100
COMMAND_LINE2_START=201
COMMAND_LINE2_STOP=200
COMMAND_VES1_START=11
COMMAND_VES2_START=22
COMMAND_VES3_START=11
COMMAND_VES1_UNLOAD=110
COMMAND_VES2_UNLOAD=220
COMMAND_VES3_UNLOAD=110
COMMAND_NORIA_INIT=100
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
# recept_ini = ConfigParser()
# recept_ini.read('.\\recepts.ini')
# print recept_ini.sections()
# -*- coding: utf-8 -*-
def saverecept2ini(dict):
    # parser.set('path', 'path', text.encode('utf8'))
    parser_= ConfigParser()
    receptinifile=open(".\\recepts.ini",'r+')
    parser_.read(receptinifile)
    parser_.add_section((dict["namekorm"]))
    for key in dict.keys():
        print dict.get(key)
        # parser_.set(dict["namekorm"], key, str(dict.get(key)).encode('utf8'))
    parser_.write(receptinifile)
    receptinifile.truncate()

def loadreceptnamelist():
    parser_ = ConfigParser()
    parser_.read(".\\recepts.ini")
    receptnamelist_ = parser_.sections()
    return receptnamelist_

def loadreceptfromini(name_):
    parser_=ConfigParser()
    parser_.read(".\\recepts.ini")
    receptlist_={}
    # for option in parser_.options(section_):
    #     receptlist_[section_][option] = parser_.get(section_, option)
    # print receptlist_.keys()
    receptlist_=dict(parser_.items(name_))

    # print parser_.sections()
    # print receptlist_.keys()
    # print receptlist_.values()
    return receptlist_

def loadrecepts():
    parser_ = ConfigParser()
    parser_.read(".\\recepts.ini")
    receptlist_ = {}
    for section in parser_.sections():
        receptlist_[section] = {}
        for option in parser_.options(section):
            receptlist_[section][option] = parser_.get(section, option)
    return receptlist_
class Dialog_recept(QDialog,Ui_Dialog_recept):
    def __init__(self, dbclient):
        # global recept_ini
        QDialog.__init__(self)
        self.ui = Ui_Dialog_recept()
        self.ui.setupUi(self)
        self.selectbankalst=[]
        self.receptlist={}
        self.kormbankalst=[]
        self.kormbankalst.append(obj(self.ui.siloskorm1, 'silos.png', 'silos_active.png', '',False,True))
        self.kormbankalst.append(obj(self.ui.siloskorm2, 'silos.png', 'silos_active.png', '',False,True))
        self.kormbankalst.append(obj(self.ui.siloskorm3, 'silos.png', 'silos_active.png', '',False,True))
        self.kormbankalst.append(obj(self.ui.siloskorm4, 'silos.png', 'silos_active.png', '',False,True))
        self.kormbankalst.append(obj(self.ui.siloskorm5, 'silos.png', 'silos_active.png', '',False,True))
        self.kormbankalst.append(obj(self.ui.siloskorm6, 'silos.png', 'silos_active.png', '',False,True))
        self.ui.addkormbtn.clicked.connect(self.addkormbtnclk)
        self.ui.clearallbtn.clicked.connect(self.clearallbtnclk)
    def addkormbtnclk(self):
        select=0
        for i in range(0,6):
            if self.kormbankalst[i].state==True:
                self.selectbankalst.append(i+1)
                select+=1
        if select!=0 and self.ui.namekormedit.text()!='':
            # str(self.ui.namekormedit.text()).encode('utf-8'),  parser.set('path', 'path', text.encode('utf8')) 'namekorm':(unicode(self.ui.namekormedit.text(),'utf8')),
            self.receptlist={  'namekorm':(unicode(self.ui.namekormedit.text()),'utf8'),
                            'zerno1':int(self.ui.zernoedit1.text()),'zerno2':int(self.ui.zernoedit2.text()),'zerno3':int(self.ui.zernoedit3.text()),
                            'zerno4':int(self.ui.zernoedit4.text()),'zerno5':int(self.ui.zernoedit5.text()),'zerno6':int(self.ui.zernoedit6.text()),
                            'zerno7':int(self.ui.zernoedit7.text()),'zerno8':int(self.ui.zernoedit8.text()),'zerno9':int(self.ui.zernoedit9.text()),
                            'zerno10':int(self.ui.zernoedit10.text()),'dobavka1':int(self.ui.dobavkaedit1.text()),'dobavka2':int(self.ui.dobavkaedit2.text()),
                            'dobavka3':int(self.ui.dobavkaedit3.text()),'dobavka4':int(self.ui.dobavkaedit4.text()),'dobavka5':int(self.ui.dobavkaedit5.text()),
                            'dobavka6':int(self.ui.dobavkaedit6.text()),'maslo':int(self.ui.masloedit.text()),'lekarstvo':int(self.ui.lekarstvoedit.text()),
                            'selectkorm':(self.selectbankalst)
                            }

            saverecept2ini(self.receptlist)
        else:
            print ("Не выбрана банка для изготовленного комбикорма или не введено имя для комбикорма")
    def  clearallbtnclk(self):
        print
        # print self.receptlist.values()
    # def readtoini(self):
    #     for section in self.config.sections():
    #         self.receptlist[section] = {}
    #         for option in self.config.options(section):
    #             self.receptlist[section][option] = self.config.get(section, option)
    # def savetoini(self):
    #     for key in self.

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
        # for row in dbclient.get_product(2):
        #      self.ui.combo1.addItem(row[1])
        #      self.ui.combo2.addItem(row[1])
        #      self.ui.combo3.addItem(row[1])
        #      self.ui.combo4.addItem(row[1])
        #      self.ui.combo5.addItem(row[1])
        #      self.ui.combo6.addItem(row[1])
        #      self.ui.comboname.addItem(row[1])
class Dialog_korm(QDialog,Ui_Dialog_Korm):
    def __init__(self,dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Korm()
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

class objs(object):

    def __init__(self,*obj):
        self.list_=(obj)
        self.state=False
    def switch(self,bit):
        for i in range(0,len(self.list_)):
            self.state=self.list_[i].switch(bit)
class obj(QtCore.QObject):
    qtobj = 0
    movie = ''
    numbit = 0
    imgtrue = ''
    imgfalse = ''
    state = False
    instate = False

    def __init__(self, object, imgfalse,imgtrue,giftrue='', flaginvers=False,flagonclick=False):
        self.imgfalse = imgfalse
        self.imgtrue = imgtrue
        self.qtobj = object
        self.flaginverslogic=flaginvers
        if giftrue is not '':
            self.movie = QtGui.QMovie(giftrue)
        if flagonclick is True:
            self.qtobj.mousePressEvent = self.onclicked_
    def onclicked_(self, event):
        if self.state is False:
            self.switch(1)
        else:
            self.switch(0)
    def start(self):
        if self.flaginverslogic is False:
            if self.movie is not '':
                self.qtobj.setMovie(self.movie)
                self.movie.start()
            else:
                self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgtrue))
        else:
            self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgfalse))
        self.state = True
    def stop(self):
        if self.flaginverslogic is False:
            self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgfalse))
        else:
            if self.movie is not '':
                self.qtobj.setMovie(self.movie)
                self.movie.start()
            else:
                self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgtrue))
        self.state = False
    def switch(self, bit):
        if bit is 1:
            if self.state is False:
                self.start()
                # print("start " + str(bit))
        else:
            if self.state is True:
                self.stop()
                # print("stop "+str(bit))
        return self.state
class mbclient1(object):
    def __init__(self,PLCaddress,PLCport):
        # self.client = ModbusClient(PLCaddress, port=PLCport)
        self.client=ModbusClient()
        self.client.host(PLCaddress)
        self.client.port(PLCport)
        self.busy=False
        self.okconnection=False
    def checkconnecttcp(self):
        if not self.client.is_open():
            try:
                self.connect()
            except (AttributeError, TypeError,self.client.last_error()) as err:
                print err
    def connect(self):
        self.okconnection = False
        while not self.okconnection:
            try:
                self.okconnection = self.client.open()
                wait(self)
            except (AttributeError, TypeError,self.client.last_error()) as err:
                print err
                return False
        return   self.okconnection

    def disconnect(self):
        return self.client.close()
    def send(self,rgadr,val):
        self.checkconnecttcp()
        wait(self)
        takeover(self)
        # rq = self.client.write_register(rgadr, val, unit=1)
        # write_single_register(reg_addr, reg_value)[source]
        try:
            self.client.write_single_register(rgadr,val)
        except (AttributeError, TypeError) as err:
            print  "Error write holding register with addr " + str(rgadr)+" "
            print err
        free(self)
    def read(self,rgadr):
        try:
            self.checkconnecttcp()
        except (AttributeError, TypeError,self.client.last_error()) as err:
            print (err)
        wait(self)
        takeover(self)
        # read_holding_registers(reg_addr, reg_nb=1)
        # result= self.client.read_holding_registers(rgadr,1,unit=1)
        try:
            result=self.client.read_holding_registers(rgadr,1)
        except (AttributeError, TypeError,self.client.last_error()):print self.client.last_error()+"Error read holding register with addr "+str(rgadr)
        free(self)
        # return result.getRegister(0)
        try:
            return result[0]
        except (AttributeError, TypeError) as e:
            return 0
    def readcoil(self,bit):
        self.checkconnecttcp()
        wait(self)
        takeover(self)
            # type: (object) -> object
        # incoil=self.client.read_coils(bit,1,unit=0x01)
        # read_coils(bit_addr, bit_nb=1)
        try:
            incoil=self.client.read_coils(bit,1)
        except (AttributeError, TypeError,self.client.last_error()):
            print self.client.last_error() + "Error read coil with number " + str(bit)
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
        self.selectkormnumbanka=[]
        self.masloneed=0
        self.handdobavka=0
        self.step=0
        self.listzernoneed=plclist()
        self.listdobavkaneed = plclist()
        self.receptlist={}
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
    def __init__(self,mbclient1):
        self.cmd=0 # регистр команд
        self.ret=0 # регистр return ответа ПЛК
        self.mbclient1=mbclient1
        self.listplccoils=plclist()
        self.listplcrg16=plclist()
        self.recept = plcrecept()
        self.countqueue=0
        self.steptext=''
        self.needstate=1
        self.recept.receptlist=loadrecepts()
    def send_cmd(self,cmd):
        # self.send_ret(0)
        # wreg = self.listplcrg16.getelement(0)
        wreg=mbclient1.read(0)
        breg=wreg&0xFF00
        self.mbclient1.send(0,cmd|breg)
    def send_cmd_val(self,cmd,val):
        self.mbclient1.send(0,cmd+(val<<8))
    def send_ret(self,val):
        # wreg = self.listplcrg16.getelement(1)
        wreg=mbclient1.read(1)
        breg = wreg & 0xFF00
        mbclient1.send(1,val|breg)
    def get_ret(self):
        # wreg=self.listplcrg16.getelement(1)
        # print "getstate >> "+str(wreg)
        wreg = mbclient1.read(1)
        if type(wreg) is  None:
            self.ret = 0
        else:
            self.ret = wreg & 0x00FF
    def waitret(self):
        while (True):
            answer = mbclient1.read(0) & 0x00FF
            delay(10000)
            if answer == 0:
                print "answer" + str(answer)
                break
        # rg = mbclient1.read(0)
    def addqueue(self):
        self.countqueue+=1
    def decqueue(self):
        self.countqueue-=1
    def nullqueue(self):
        self.countqueue=0

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
            for i in range(0,COUNTsiloszerno+1):
                listweightzernolocal_.insert(i,plcglobal1.listplcrg16.getelement(i+OFFSETsiloszerno))
            plcglobal1.recept.listzernoneed.pull(listweightzernolocal_)
            for i in range(0,COUNTsilosdobavka+1):
                listweightdobavkalocal_.insert(i, plcglobal1.listplcrg16.getelement(i + OFFSETsilosdobavka))
            plcglobal1.recept.listdobavkaneed.pull(listweightdobavkalocal_)
            for i in range(0, 7):
                for j in range(0, 16):
                    delay(1000)
                    listcoillocal_.insert( i*16+j,getbit(plcglobal1.listplcrg16.getelement(i + OFFSETflagstate), j))
            plcglobal1.listplccoils.pull(listcoillocal_)
            # plcglobal1.get_state()
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
            mbclient1.checkconnecttcp()
            listrg16local_ = range(LASTREGADDR+1)
            for i in range(0,LASTREGADDR+1):
                delay(1000)
                try:
                    listrg16local_.insert(i, mbclient1.read(i))
                except TypeError:
                    print "Type_error"
            plcglobal1.listplcrg16.pull(listrg16local_)
        print "-thread ThreadGetPLC done"
    def stop(self):
        self._isRunning = False
class ThreadVisual1Level(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    vesisignal=QtCore.pyqtSignal(int,int,int)
    s1= QtCore.pyqtSignal(int,int)
    _isRunning=False
    @QtCore.pyqtSlot()
    def __init__(self,plc):
        QtCore.QObject.__init__(self)
        self.plc=plc
    def process(self):
        print "+thread ThreadVisual1Level started"
        while  self._isRunning is True:
            for i in range(0,98+1):
                delay(10000)
                self.s1.emit(i,plcglobal1.listplccoils.getelement(i))
                self.vesisignal.emit(plcglobal1.listplcrg16.getelement(4),plcglobal1.listplcrg16.getelement(5),plcglobal1.listplcrg16.getelement(6))
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
class ThreadPowerOnSystem(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False
    def __init__(self, plc_, mbclient1_):
        QtCore.QObject.__init__(self)
    @QtCore.pyqtSlot()
    def process(self):
        plcglobal1.send_cmd(101)  # Включение линии1
        plcglobal1.waitret()
        plcglobal1.send_cmd(201)  # Включение линии2
        plcglobal1.waitret()
        plcglobal1.send_cmd(41)  # Включение миксера
    def stop(self):
        self._isRunning = False

class ThreadWorkZames(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    startsession = QtCore.pyqtSignal()
    getrecept=  QtCore.pyqtSignal()
    endsession= QtCore.pyqtSignal()
    _isRunning=False
    def __init__(self,plc_,mbclient1_):
        QtCore.QObject.__init__(self)
        # self.mbclient1=mbclient1_
        # self.plc=plc_
    @QtCore.pyqtSlot()
    def process(self):
        print "+thread ThreadWorkZames started"
        while  self._isRunning is True:
            answer=0
            print "Команда инициализации ПЛК для изготовления рецепта"
            plcglobal1.waitret()
            plcglobal1.send_cmd(COMMAND_INIT) # команда нинициализации флагов плк1
            plcglobal2.waitret()
            plcglobal2.send_cmd(COMMAND_INIT) # команда нинициализации флагов плк2
            plcglobal2.waitret()
            plcglobal2.send_cmd(COMMAND_NORIA_INIT) # настрока линии нория
            print "Получаем рецепт"
            self.getrecept.emit() # Взять текущий рецепт из очереди и заполнить все edit'ы согласно текущему рецепту
            self.startsession.emit() # Отправка рецепта в ПЛК1(весы1 и весы2) и ПЛК2(весы3)
            print "Отправлена команда перенастроить <Приемка комбикорма>"
            # print "Send  =Begin work= and wait answer"
            # print "Receive =Begin work= "+str(plcglobal1.ret)
            # print "Отправлен Пакет данных для рецепта"
            # listsilosdobavka = [88, 90, 92, 94, 96, 98]
            # i=0
            # print "Проверка статуса выбранного силоса "+str(plcglobal1.recept.selectkormnumbanka[i])
            # if(listplccoils=listsilosdobavka[plcglobal1.recept.selectkormnumbanka[i]])

            while(plcglobal1.recept.count is not 0):

                plcglobal1.waitret()
                plcglobal1.send_cmd(COMMAND_VES1_START)

                plcglobal1.waitret()
                plcglobal1.send_cmd(COMMAND_VES2_START)

                plcglobal2.waitret()
                plcglobal2.send_cmd(COMMAND_VES3_START)

                mixerreadyunload = mbclient1.readcoil(291)
                if mixerreadyunload==True:
                    plcglobal1.waitret()
                    plcglobal1.send_cmd(COMMAND_MIXER_UNLOAD)

                mixerreadytoload=mbclient1.readcoil(290)
                if mixerreadytoload==True:
                    plcglobal1.waitret()
                    plcglobal1.send_cmd(COMMAND_VES1_UNLOAD)
                    plcglobal1.waitret()
                    plcglobal1.send_cmd(COMMAND_VES2_UNLOAD)
                    plcglobal2.waitret()
                    plcglobal2.send_cmd(COMMAND_VES3_UNLOAD)
                    plcglobal2.wait_ret()

                plcglobal1.recept.deccount()


            # print "Отправлена команда ПЛК <Конец сессии>"
            # plcglobal1.send_cmd(102)
            # print "Ожидание ответа от ПЛК"
            # plcglobal1.waitret()
            # print "Получен ответ от ПЛК <Конец сессии>"
            # print "Send =End work="
            # plcglobal1.send_cmd_val(103,0)
            # answer = mbclient1.read(1) & 0x00FF
            # plcglobal1.waitret()
            # print "Получен ответ =End work="
        print "Счетчик <Количество замесов> достиг нуля- изготовление рецепта завершено!"
        self._isRunning = False
        self.endsession.emit()
        self.finished.emit()
        print "-thread ThreadWorkZames is done"
    def stop(self):
        self._isRunning = False
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    movies = []
    moviesL2=[]
    def __init__(self,dbclient):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)
        self.addtoqueuebtn.clicked.connect(self.addqueuebtnclk)

        self.dbclient=dbclient
        # self.tableview.setRowCount(2)
        # self.tableView.setColumnCount(2)
        # loadfromini('korm999')

        self.moviesL2.insert(0, objs(obj(self.ves1shiber, "vesishiberclose.png", "vesishiberopen.png", "")))
        self.moviesL2.insert(1,  objs(obj(self.ves2shiber, "vesishiberclose.png", "vesishiberopen.png", "")))
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
        self.movies.insert(0, objs(obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png")))
        self.movies.insert(1, objs(obj(self.dobavkisilos1do, "statusfalse.png", "statustrue.png")))
        self.movies.insert(2, objs(obj(self.silos1dobavkaopen, "statusminifalse.png",  "statusminitrue.png"),obj(self.silos1dobavkashiber, "silosshiberclose.png", "silosshiberopen.png")))
        self.movies.insert(3, objs( obj(self.silos1dobavkaclose, "statusminifalse.png", "statusminitrue.png"),obj(self.silos1dobavkashiber, "silosshiberopen.png", "silosshiberclose.png" )))
        self.movies.insert(4, objs( obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png" )))
        self.movies.insert(5, objs( obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png")))
        self.movies.insert(6, objs( obj(self.silos2dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos2dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(7, objs( obj(self.silos2dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos2dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(8, objs(obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", "")))
        #reg7 PLC2(dobavki)
        self.movies.insert(9,  objs(obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(10, objs( obj(self.silos3dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos3dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(11, objs(obj(self.silos3dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos3dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(12, objs(obj(self.dobavkisilos4up, "statusfalse.png", "statu9strue.png", "")))
        self.movies.insert(13, objs(obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(14, objs( obj(self.silos4dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos4dobavkashiber, "statusminitrue.png", "statusminifalse.png", '')))
        self.movies.insert(15, objs( obj(self.silos4dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos4dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        #reg8 PLC3(dobavki)
        self.movies.insert(16, objs( obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(17, objs(obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(18, objs( obj(self.silos5dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos5dobavkashiber, "statusminitrue.png", "statusminifalse.png", '')))
        self.movies.insert(19, objs( obj(self.silos5dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos5dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(20, objs( obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(21, objs(obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(22, objs( obj(self.silos6dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos6dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(23, objs(obj(self.silos6dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),obj(self.silos6dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        #reg8 PLC4 dobavki
        self.movies.insert(24,objs( obj(self.flex1, "flex1stop.png", "flex1run.png", ''), obj(self.flex1_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(25,objs( obj(self.flex2, "flex2stop.png", "flex2run.png", ''), obj(self.flex2_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(26,objs( obj(self.flex3, "flex3stop.png", "flex3run.png", ''), obj(self.flex3_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(27,objs( obj(self.flex4, "flex4stop.png", "flex4run.png", ''), obj(self.flex4_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(28,objs( obj(self.flex5, "flex5stop.png", "flex5run.png", ''), obj(self.flex5_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(29,objs( obj(self.flex6, "flex6stop.png", "flex6run.png", ''), obj(self.flex6_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(30,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))) # reserv
        self.movies.insert(31,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))) # reserv
        #reg9 PLC5 dobavki
        self.movies.insert(32,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # button auto
        self.movies.insert(33,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")) ) # button ruchno
        self.movies.insert(34, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")) ) # button stop
        self.movies.insert(35,objs( obj(self.flexload, "flexloadstop.png", "flexloadrun.png", ''),obj(self.motorflexload, "motor.gif", "", 'motor_active.gif')))
        self.movies.insert(36,objs( obj(self.bunkerloaddo, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(37,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")) ) # open shiber vesi knopka
        self.movies.insert(38,objs( obj(self.ves3sensopen, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(39,objs( obj(self.ves3sensclose, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(40,objs( obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", '')))
        #reg9 PLC6(mixer)
        self.movies.insert(41,objs( obj(self.mixersensopen, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(42,objs( obj(self.mixersensclose, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(43,objs( obj(self.mixer, "mixerstop.png", '', "mixerbegin.gif")))
        self.movies.insert(44,objs( obj(self.mixer_2, "mixer2_stop.png", "", "mixer2_run")) )# mixer2
        self.movies.insert(45,objs( obj(self.mixerbunkersens, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(46,objs( obj(self.mixershnek1, "shnek_hor_stop.gif", "", "shnek_hor_begin.gif")))
        self.movies.insert(78,objs( obj(self.mixershnek2, "shnek_nakl_stop.gif",  "","shnek_nakl_begin.gif"))) #
        #reg10 PLC7 (zerno)
        self.movies.insert(48,objs( obj(self.ves1sensopen, "statusfalse.png", "statustrue.png", ''))) #,obj(self.ves1shiber, "", "vesishberopen.png", ''),obj(self.ves1shiber_2, "", "", 'motor_active.gif',True)
        self.movies.insert(49,objs( obj(self.ves1sensclose, "statusfalse.png", "statustrue.png", ''))) #,obj(self.ves1shiber, "", "statustrue.png", ''),obj(self.ves1shiber_2, "", "", 'motor_active.gif',True)
        self.movies.insert(50,objs( obj(self.ves2sensopen, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(51,objs( obj(self.ves2sensclose, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(52,objs( obj(self.ves1bunkersens, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(53,objs( obj(self.ves2bunkersens1, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(54,objs( obj(self.ves2bunkersens2, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(55,objs( obj(self.autokombikorm, "statusfalse.png", "statustrue.png", "")))  # auto button
        #reg10 PLC8(zerno)
        self.movies.insert(56,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")) ) # reserv shnek1
        self.movies.insert(57,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")) ) # reserv shnek2
        self.movies.insert(58,objs( obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", "") ,obj(self.zernoshnek3_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(59,objs( obj(self.zernoshnek4, "shnek4zernostop.png", "shnek4zernorun.png", ""),obj(self.zernoshnek4_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(60,objs( obj(self.zernoshnek5, "shnek5zernostop.png", "shnek5zernorun.png", ""),obj(self.zernoshnek5_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(61,objs( obj(self.zernoshnek6, "shnek6zernostop.png", "shnek6zernorun.png", ""),obj(self.zernoshnek6_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(62,objs( obj(self.zernoshnek7, "shnek7zernostop.png", "shnek7zernorun.png", ""),obj(self.zernoshnek7_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(63,objs(obj(self.zernoshnek8, "shnek8zernostop.png", "shnek8zernorun.png", ""),obj(self.zernoshnek8_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        #reg11 PLC9 (zerno) (self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""),obj(self.zernoshnek9_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")
        self.movies.insert(64,objs (obj(self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""),obj(self.zernoshnek9_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(65,objs( obj(self.zernoshnek10, "shnek10zernostop.png", "shnek10zernorun.png", ""),obj(self.zernoshnek10_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(66, objs(obj(self.drobilka1, "drobilka_off.png", "", "drobilkabegin")))
        self.movies.insert(67,objs( obj(self.drobilka2, "drobilka_off.png", "", "drobilkabegin")))
        self.movies.insert(68,objs( obj(self.ves2shnek, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(69,objs( obj(self.ves1shnek1, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(70,objs( obj(self.ves1shnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(71,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        #reg11 PLC10(kombikorm)
        self.movies.insert(72, objs(obj(self.klapan1, "klapan1false.png", "klapan1true.png", "")))
        self.movies.insert(73,objs( obj(self.klapan2, "klapan2false.png", "", "klapan2true.png")))
        self.movies.insert(74,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))  )# stop
        self.movies.insert(75, objs(obj(self.noria, "noriastop.png", "", "noriabegin.gif")))
        self.movies.insert(76, objs(obj(self.terminator1, "terminator1stop.png", "", "terminator1.gif")))
        self.movies.insert(77,objs( obj(self.terminator2, "terminator2stop.png", "", "terminator2.gif")))
        self.movies.insert(78, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserve
        self.movies.insert(79,objs( obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserve
        #reg12 PLC11(kombikorm)
        self.movies.insert(80,objs( obj(self.silos1shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(81,objs( obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(82,objs( obj(self.silos2shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(83, objs(obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(84, objs(obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(85, objs(obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(86,objs( obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(87,objs( obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        #reg12 PLC12(kombikorm)
        self.movies.insert(88,objs( obj(self.silos1up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(89,objs( obj(self.silos1do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(90,objs( obj(self.silos2up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(91,objs( obj(self.silos2do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(92, objs(obj(self.silos3up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(93, objs(obj(self.silos3do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(94, objs(obj(self.silos4up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(95,objs( obj(self.silos4do, "statusfalse.png", "statustrue.png", "")))
        #reg13 PLC13(kombokorm)
        self.movies.insert(96, objs(obj(self.silos5up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(97,objs( obj(self.silos5do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(98,objs( obj(self.silos6up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(99,objs( obj(self.silos6do, "statusfalse.png", "statustrue.png", "")))
        #reg13 PLC14
        self.movies.insert(100,objs(obj(self.autokombikorm, "statusfalse.png","statustrue.png", "")))
        self.movies.insert(101,objs( obj(self.ruchnokombikorm, "statusfalse.png","statustrue.png", "")))
       # self.movies.insert(101, obj(self.autoruchnokombikorm, "statusfalse.png","statustrue.png", ""))

        self.interface_=[]
        self.interface_.append(obj(self.siloskorm1, "silos.png","silos_active.png", "",False,True))
        self.interface_.append(obj(self.siloskorm2, "silos.png", "silos_active.png", "",False,True))
        self.interface_.append(obj(self.siloskorm3, "silos.png", "silos_active.png", "",False,True))
        self.interface_.append(obj(self.siloskorm4, "silos.png", "silos_active.png", "",False,True))
        self.interface_.append(obj(self.siloskorm5, "silos.png", "silos_active.png", "",False,True))
        self.interface_.append(obj(self.siloskorm6, "silos.png", "silos_active.png", "",False,True))
        # self.reinitmbtcp()
        self.editkorm.triggered.connect(self.kormtbtnclk)
        self.editzerno.triggered.connect(self.zernobtnclk)
        self.editrecept.triggered.connect(self.receptbtnclk)
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        self.actionexit.triggered.connect(self.exitclk)
        self.activethreads=[]
        if DEBUGFLAG==False:
            self.startThreadVisual1Level(QThread(self),self.plc)
            self.startThreadVizual2level(QThread(self))
            self.startThreadGetPLC(QThread(self))
            self.startThreadPullPLCList(QThread(self))
        else:
            pass

        # for i in range(0,len(loadreceptnamelist())):
        #     self.comboBoxRecept.addItem(loadreceptnamelist)
        # if dbclient is not False:
        #     self.dbclient=dbclient
        # for row in self.dbclient.get_product(IDKORM):
        #     self.comboBoxRecept.addItem(row[NAMEPRODUCT])
        self.connect(self.comboBoxRecept, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.comboboxchangedslot)
        self.comboBoxRecept.addItems(plcglobal1.recept.receptlist.keys())
        self.comboBoxRecept.blockSignals(False)
        self.delbtn.clicked.connect(self.deleteallrow)
        # self.addtoqueuebtn.clicked.connect(self.addqueuebtnclk)
        self.tableWidget.setColumnWidth(0,210)
        self.tableWidget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(u"Наименование комбикорма" ))
        self.tableWidget.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem(u"Кол-во замесов"))
        self.currentrow=0
        self.tableWidget.itemSelectionChanged.connect(self.getselectrow)
    def getselectrow(self):
        # items= self.tableWidget.selectedItems()
        # print str(items[0].text())
        # selectrownum=self.tableWidget.selected
        pass
    def deleteallrow(self):
        plcglobal1.nullqueue()
        # for i in range(0,self.currentrow+1):
        #     self.tableWidget.removeRow(0)
        self.currentrow=0
        self.tableWidget.setRowCount(0) #обнулить таблицу
        self.tableWidget.setRowCount(10)
        # indexes = table.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())
    def addqueuebtnclk(self):
        # self.tableWidget.Add ()
        plcglobal1.addqueue()
        count=self.kormneedcount.text()
        # count=self.kormneedcount.Text()
        name=self.comboBoxRecept.currentText()
        if  name!='' and (count!='0' and count!=''):
            newitem=QTableWidgetItem(name)
            self.tableWidget.setItem(self.currentrow,0 ,newitem)
            newitem=QTableWidgetItem(count)
            self.tableWidget.setItem(self.currentrow, 1, newitem)
            self.currentrow+=1
            print self.currentrow
            if self.currentrow>9:
                self.tableWidget.setRowCount(self.currentrow + 1)
    def comboboxchangedslot(self):
        self.loadrecept((str(self.comboBoxRecept.currentText()).encode('utf-8')))
    def loadrecept(self,name):
        namerecept=''
        namerecept=name
        current_recept={}
        current_recept=plcglobal1.recept.receptlist.get(namerecept)
        print current_recept.items()
        print "Выбран рецепт "+ current_recept.get('namekorm')

        self.zernoedit3.setText( current_recept.get('zerno3'))
        self.zernoedit4.setText( current_recept.get('zerno4'))
        self.zernoedit5.setText( current_recept.get('zerno5'))
        self.zernoedit6.setText( current_recept.get('zerno6'))
        self.zernoedit7.setText( current_recept.get('zerno7'))
        self.zernoedit8.setText( current_recept.get('zerno8'))
        self.zernoedit9.setText( current_recept.get('zerno9'))
        self.zernoedit10.setText( current_recept.get('zerno10'))
        self.dobavkaedit1.setText(current_recept.get('dobavka1'))
        self.dobavkaedit2.setText(current_recept.get('dobavka2'))
        self.dobavkaedit3.setText(current_recept.get('dobavka3'))
        self.dobavkaedit4.setText(current_recept.get('dobavka4'))
        self.dobavkaedit5.setText(current_recept.get('dobavka5'))
        self.dobavkaedit6.setText(current_recept.get('dobavka6'))
        self.masloedit.setText(current_recept.get('maslo'))
        somelistrecept=[]
        somelistrecept=current_recept.get('selectkorm')
        print somelistrecept
        for i in range(0,6):
            if str(i+1) in (somelistrecept):
                self.interface_[i].switch(1)
            else:
                self.interface_[i].switch(0)

        # self.zernoedit3.setText
        # print self.plc.recept.receptlist.values()
    def reinitmbtcp(self):
        self.mbclient1.checkconnect()
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
    def kormtbtnclk(self):
        dialogrecept = Dialog_korm(self.dbclient)
        dialogrecept.exec_()
    def stopbtnclk(self):
        pass
    def startbtnclk(self):
        # self.plc.recept.count = 1
        print "START CLICK!"
                # print "select silos for kombikorm" + str(self.plc.recept.selectkormnumbanka)
        # print self.plc.recept.count
        # plcglobal1.send_cmd(41)    #Включение Нории
        # plcglobal1.waitret()
        # plcglobal1.send_cmd_val(101, plcglobal1.recept.selectkormnumbanka[0])

        # plcglobal1.send_cmd(101)  # Включение линии1
        # plcglobal1.waitret()
        # plcglobal1.send_cmd(201)  # Включение линии2
        # plcglobal1.waitret()
        # plcglobal1.send_cmd(41)  # Включение миксера
        # plcglobal1.waitret()
        #
        self.startThreadWorkZames(QThread(self))
            # else:
            #     self.plc.recept.selectkormnumbanka = 0
            #     self.plc.recept.count = 0
            #     print "no select silos for kombikorm"
        # cell = self.tableWidget.item(0, 1).text()

    def vesivisuallevel1slot(self,vesi1,vesi2,vesi3):
        self.labelves1.setText(str(vesi1))
        self.labelves2.setText(str(vesi2))
        self.labelves3.setText(str(vesi3))
    def startThreadVisual1Level(self,thread_,plc):
        print "Try start thread visual1level"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.visual1level = ThreadVisual1Level(plc)
        self.visual1level.moveToThread(thread)
        self.visual1level.s1.connect(self.visual1levelslot)
        self.visual1level.vesisignal.connect(self.vesivisuallevel1slot)
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
        # thread.start()
    def startThreadGetPLC(self,thread_):
        print "Try start thread ThreadGetPLC"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        print type(self.activethreads[-1])
        self.getplc = ThreadGetPLC()
        self.getplc.moveToThread(thread)
        thread.started.connect(self.getplc.process)
        self.getplc.finished.connect(thread.quit)
        self.getplc.finished.connect(self.getplc.deleteLater)
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
        self.workerzames = ThreadWorkZames(self.plc, self.mbclient1)
        self.workerzames.moveToThread(thread)
        self.workerzames.startsession.connect(self.workzamesstartslot)
        self.workerzames.getrecept.connect(self.workzamesgetreceptslot)
        self.workerzames.endsession.connect(self.workzamesendslot)
        thread.started.connect(self.workerzames.process)
        self.workerzames.finished.connect(thread.quit)
        self.workerzames.finished.connect(self.workerzames.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.workerzames._isRunning = True
        thread.start()
    def visual1levelslot(self,index,bit):
        self.movies[index].switch(bit)
        if self.mbclient1.okconnection:
            self.connectstatuslabel.setText(u"Соединение с ПЛК..Соединено")
            if self.plc.ret is  0:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК занят <" + str(self.plc.ret)+u">")
            if self.plc.ret is  1:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК ждет команды на взвешивание <" + str(self.plc.ret)+u">")
            if self.plc.ret is  2:
                self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК настроил приемку зерна <" + str(self.plc.ret)+u">")
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

        # if self.plc.state is 0 and self.mbclient1.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ожидание команды")
        # if self.plc.state is 1 and self.mbclient1.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Закончил загрузку весов")
        # if self.plc.state is 2 and self.mbclient1.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ошибка")
    def visual2levelslot(self): # визулизация шиберов- по состоянию концевиков
        def shiber_switch(obj1,obj2,obj3):
            if obj2.state is True and  obj3.state is False:  #если включен концевик "открыто"
                obj1.switch(1)      # открыть шибер
            if obj2.state is False and obj3.state is True: #если включен концевик "закрыто"
                obj1.switch(0)   # закрыть шибер
            if obj2.state is False and   obj3.state is False:
                pass
            if obj2.state is True and   obj3.state is True:
                pass
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
        # pass
    def workzamesstartslot(self):
        print('start! slot from threadPLCZames signal_')
        # self.plc.recept.selectkormnumbanka=2

        # print "select kormsilos = "+str(self.plc.recept.selectkormnumbanka)

        # self.plc.recept.selectkormnumbanka=2
        self.mbclient1.send(20, int(self.zernoedit3.text()))
        self.mbclient1.send(21, int(self.zernoedit4.text()))
        self.mbclient1.send(22, int(self.zernoedit5.text()))
        self.mbclient1.send(23, int(self.zernoedit6.text()))
        self.mbclient1.send(24, int(self.zernoedit7.text()))
        self.mbclient1.send(25, int(self.zernoedit8.text()))
        self.mbclient1.send(26, int(self.zernoedit9.text()))
        self.mbclient1.send(27, int(self.zernoedit10.text()))
        self.mbclient1.send(28, int(self.dobavkaedit1.text()))
        self.mbclient1.send(29, int(self.dobavkaedit2.text()))
        self.mbclient1.send(30, int(self.dobavkaedit3.text()))
        self.mbclient1.send(31, int(self.dobavkaedit4.text()))
        self.mbclient1.send(32, int(self.dobavkaedit5.text()))
        self.mbclient1.send(33, int(self.dobavkaedit6.text()))
        self.mbclient1.send(34, int(self.masloedit.text()))
        # self.mbclient1.send()
        # self.mbclient1.send(18, 110)
        # self.mbclient1.send(19, 220)
        # self.mbclient1.send(20, 330)
        # self.mbclient1.send(21, 440)
        # self.mbclient1.send(22, 550)
        # self.mbclient1.send(23, 660)
        # self.mbclient1.send(24, 770)
        # self.mbclient1.send(25, 880)
        #
        #
        # self.mbclient1.send(0, 1)  # запись в регистр dbcmd - команда для ПЛК на замес
        # self.mbclient1.send(1, 0)  # запись в регистр ret - 0
    def workzamesendslot(self):
        print ("Endsession  emited")
        self.tableWidget.removeRow(0)
        plcglobal1.decqueue()
    def workzamesgetreceptslot(self):
        self.loadrecept(str(self.tableWidget.item(0, 0).text()))
        plcglobal1.recept.count = int(self.tableWidget.item(0, 1).text())
        plcglobal1.recept.selectkormnumbanka = []
        for i in range(0, 6):
            if self.interface_[i].state is True: # выделенную банку
                plcglobal1.recept.selectkormnumbanka.append(i + 1) # помещаем в список банок для комбикорма

# print plcglobal1.recept.receptlist.keys()
# print plcglobal1.recept.receptlist.values()
config=CONFIG()
db = DB(config.ipaddrdb, "root", "root", config.namedb)
DEBUGFLAG=True
if config.ERROR_READ_INI is False:
    # self.db = MySQLdb.coect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
    if DEBUGFLAG is False:
        # mbclient1=mbclient1(config.ipaddrplc,config.portplc)
        mbclient1 = mbclient('10.0.6.10', '502')
        mbclient2 = mbclient('10.0.6.97', '503')
        plcglobal1 = PLC(mbclient1)
        plcglobal2 = PLC(mbclient2)
    else:
        mbclient1 = False
        mbclient2 = False
        plcglobal1 = PLC(mbclient1)
        plcglobal2 = PLC(mbclient2)
def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MyApp(db)
    form.show()
    app.exec_()                        # and execute the app


if __name__ == "__main__":
    main()
