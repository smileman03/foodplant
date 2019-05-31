# -*- coding: utf-8 -*-
# coding: utf-8
import sys
import traceback
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
from designcal import Ui_Dialog_Cal
import win_inet_pton
import logging
from  ConfigParser import *
from pyModbusTCP.client import ModbusClient
import datetime
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import *

# from vizual import *
# from configroutine import *
logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'log.log')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
qtCreatorFile = "designcormoceh.ui"  # main window design ui
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
DEBUGFLAG = False
COUNTsilosdobavka = 5  # от 0
COUNTsiloszerno = 9  # от 0
COUNTsiloskorm = 5  # от 0
OFFSETsiloszerno = 37  # rg37
OFFSETsilosdobavka = 47  # rg28
OFFSETsilosmaslo = 53
OFFSETsiloskorm = None
OFFSETflagstate = 7  # rg7
LASTREGADDR = 54
# SQL
IDPRODUCT = 0
NAMEPRODUCT = 1
IDZERNO = 1
IDDOBAVKA = 2
IDKORM = 3

REG_ERROR = 14
REG_STATUS = 36
REG_CMD = 0

VES1INDEX = 4
VES2INDEX = 5
VES3INDEX = 6

VESMAX = 15
# DBSTATUS
VES1READYUNLOAD = 0
VES2READYUNLOAD = 1
VES3READYUNLOAD = 2
VES1READYLOAD = 3
VES2READYLOAD = 4
VES3READYLOAD = 5
MIXERREADYLOAD = 6
MIXERREADYUNLOAD = 7
# DBSTATUS2

NORIAREADYLOAD = 8
LINE1READYLOAD = 9
LINE2READYLOAD = 10
DOPDOBAVKAREADY = 11
MASLOREADY = 12  # МАСЛО ЗАГРУЖЕНО

COMMAND_SHNEKMIXER_ON = 51
COMMAND_SHNEKMIXER_OFF = 50
COMMAND_INIT = 111
COMMAND_MIXER_ON = 41
COMMAND_MIXER_OFF = 40
COMMAND_MIXER_UNLOAD = 42
COMMAND_LINE1_START = 101
COMMAND_LINE1_STOP = 100
COMMAND_LINE2_START = 201
COMMAND_LINE2_STOP = 200
COMMAND_VES12_START = 11
COMMAND_VES3_START = 13
COMMAND_DOPDOBAVKA_START = 14
COMMAND_OIL_START = 15
COMMAND_OIL_STOP = 16
COMMAND_OIL_START_HAND = 17

COMMAND_VES1_UNLOAD = 110
COMMAND_VES2_UNLOAD = 120
COMMAND_VES3_UNLOAD = 130
# COMMAND_VES3_UNLOAD_HAND = 131
COMMAND_NORIA_INIT = 199
COMMAND_NORIA_STOP = 198
COMMAND_ZERO_WEIGHT1 = 31
COMMAND_ZERO_WEIGHT2 = 32
COMMAND_ZERO_WEIGHT3 = 33
COMMAND_CAL_WEIGHT1 = 34
COMMAND_CAL_WEIGHT2 = 35
COMMAND_CAL_WEIGHT3 = 36
COMMAND_STOP = 1
COMMAND_PAUSE = 2


class CONFIG:
    ERROR_READ_INI = False
    ipaddrdb = 'localhost'
    namedb = 'cormoceh4'
    ipaddrplc = '10.0.6.98'
    portplc = '502'
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
    def __init__(self, baseaddress_, user_, passw_, db_):
        self.db = MySQLdb.connect(host=baseaddress_, user=user_, passwd=passw_, db=db_, charset='utf8')
        # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')

    def get_recepts(self):
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM recept"""
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_zerno(self):  # Получить список зерна
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM product where nGrp_Product=""" + str(1)  # 1-зерно 2-добавки 3 -корм
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_dobavka(self):  # Получить список добавок
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM product where nGrp_Product=""" + str(2)  # 1-зерно 2-добавки 3 -корм
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_korm(self):  # Получить список комбинорма
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM product where nGrp_Product=""" + str(3)  # 1-зерно 2-добавки 3 -корм
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_bunker(self,id_ingridient):  # Получить номер банки по Id продукта(Зерно =1, Добавки=2, Комбикорм=3, Масло=4)
        self.cursor = self.db.cursor()
        self.sql = """SELECT Name FROM bunker WHERE nGrp_Bunker=""" + str(id_ingridient)
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def get_product(self, id_banka):
        self.cursor = self.db.cursor()
        self.sql = """SELECT nProduct,Name FROM `kormoceh4`.`product` a, `prod_bunker` b  WHERE a.`nRec` = b.nProduct and  b.nBunker= """ + str(id_banka)
        self.cursor.execute(self.sql)

        for row in self.cursor.fetchall():
            pass
        return row
    def save_product(self,id_banka,id_product):
        cursor = self.db.cursor()
        sql = """UPDATE `prod_bunker` SET `nProduct` = %s  WHERE `prod_bunker`.`nBunker` = %s """
        # sql = """UPDATE `prod_bunker` SET `nProduct` = 3  WHERE `prod_bunker`.`nBunker` = 3 """
        cursor.execute(sql,(id_product,id_banka))
        self.db.commit()
    def get_id_product(self,Name):

        cursor = self.db.cursor()
        sql = """SELECT * FROM `kormoceh4`.`product` WHERE `product`.`Name` = %s """
        cursor.execute(sql,(Name))
        rows =  cursor.fetchall()
        for row in rows:
            pass
        return row[0]
# recept_ini = ConfigParser()
# recept_ini.read('.\\recepts.ini')
# print recept_ini.sections()
# -*- coding: utf-8 -*-
def saverecept2ini(dict):
    # parser.set('path', 'path', text.encode('utf8'))
    parser_ = ConfigParser()
    receptinifile = open(".\\recepts.ini", 'r+')
    parser_.read(receptinifile)
    parser_.add_section(dict["namekorm"])
    for key in dict.keys():
        print dict.get(key)
        parser_.set(dict["namekorm"], key, str(dict.get(key)).encode('utf8'))
    parser_.write(receptinifile)
    receptinifile.truncate()


def loadreceptnamelist():
    parser_ = ConfigParser()
    parser_.read(".\\recepts.ini")
    receptnamelist_ = parser_.sections()
    return receptnamelist_


def loadreceptfromini(name_):
    parser_ = ConfigParser()
    parser_.read(".\\recepts.ini")
    receptlist_ = {}
    # for option in parser_.options(section_):
    #     receptlist_[section_][option] = parser_.get(section_, option)
    # print receptlist_.keys()
    receptlist_ = dict(parser_.items(name_))

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


class Dialog_recept(QDialog, Ui_Dialog_recept):
    def __init__(self, dbclient):
        # global recept_ini
        QDialog.__init__(self)
        self.ui = Ui_Dialog_recept()
        self.ui.setupUi(self)
        self.selectbankalst = []
        self.receptlist = {}
        self.kormbankalst = []
        self.kormbankalst.append(obj(self.ui.siloskorm1, 'silos.png', 'silos_active.png', '', False, True))
        self.kormbankalst.append(obj(self.ui.siloskorm2, 'silos.png', 'silos_active.png', '', False, True))
        self.kormbankalst.append(obj(self.ui.siloskorm3, 'silos.png', 'silos_active.png', '', False, True))
        self.kormbankalst.append(obj(self.ui.siloskorm4, 'silos.png', 'silos_active.png', '', False, True))
        self.kormbankalst.append(obj(self.ui.siloskorm5, 'silos.png', 'silos_active.png', '', False, True))
        self.kormbankalst.append(obj(self.ui.siloskorm6, 'silos.png', 'silos_active.png', '', False, True))
        self.ui.addkormbtn.clicked.connect(self.addkormbtnclk)
        self.ui.clearallbtn.clicked.connect(self.clearallbtnclk)

    def addkormbtnclk(self):
        select = 0
        for i in range(0, 6):
            if self.kormbankalst[i].state == True:
                self.selectbankalst.append(i + 1)
                select += 1
        if select != 0 and self.ui.namekormedit.text() != '':
            # str(self.ui.namekormedit.text()).encode('utf-8'),  parser.set('path', 'path', text.encode('utf8')) 'namekorm':(unicode(self.ui.namekormedit.text(),'utf8')),
            self.receptlist = {'namekorm': (unicode(self.ui.namekormedit.text(), 'utf-8')),
                               'zerno1': int(self.ui.zernoedit1.text()), 'zerno2': int(self.ui.zernoedit2.text()),
                               'zerno3': int(self.ui.zernoedit3.text()),
                               'zerno4': int(self.ui.zernoedit4.text()), 'zerno5': int(self.ui.zernoedit5.text()),
                               'zerno6': int(self.ui.zernoedit6.text()),
                               'zerno7': int(self.ui.zernoedit7.text()), 'zerno8': int(self.ui.zernoedit8.text()),
                               'zerno9': int(self.ui.zernoedit9.text()),
                               'zerno10': int(self.ui.zernoedit10.text()), 'dobavka1': int(self.ui.dobavkaedit1.text()),
                               'dobavka2': int(self.ui.dobavkaedit2.text()),
                               'dobavka3': int(self.ui.dobavkaedit3.text()),
                               'dobavka4': int(self.ui.dobavkaedit4.text()),
                               'dobavka5': int(self.ui.dobavkaedit5.text()),
                               'dobavka6': int(self.ui.dobavkaedit6.text()), 'maslo': int(self.ui.masloedit.text()),
                               'lekarstvo': int(self.ui.lekarstvoedit.text()),
                               'selectkorm': (self.selectbankalst)
                               }

            saverecept2ini(self.receptlist)
        else:
            print (str(datetime.datetime.now())+"--Не выбрана банка для изготовленного комбикорма или не введено имя для комбикорма")

    def clearallbtnclk(self):
        print
        # print self.receptlist.values()
        # def readtoini(self):
        #     for section in self.config.sections():
        #         self.receptlist[section] = {}
        #         for option in self.config.options(section):
        #             self.receptlist[section][option] = self.config.get(section, option)
        # def savetoini(self):
        #     for key in self.


class Dialog_zerno(QDialog, Ui_Dialog_Zerno):
    def __init__(self, dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Zerno()
        self.ui.setupUi(self)
        # for row in get_product():
        #     print row[3]
        #     self.combozerno.addItem(row[3])
        zerno_ = range(20)
        self.dbclient = dbclient
        self.ui.savebankabtn.clicked.connect(self.btnapplyclk)

        for i in range(1, 11):
            zerno_[i] = self.dbclient.get_product(i)
            print str(zerno_[i][0]) + " " + zerno_[i][1]  # zerno[0] - nRec zerno[1] - Name

        # self.comboboxlist=range(10)
        # self.comboboxlist.insert(1, self.ui.combo1)
        # self.comboboxlist.insert(2, self.ui.combo2)
        # self.comboboxlist.insert(3, self.ui.combo3)
        # self.comboboxlist.insert(4, self.ui.combo4)
        # self.comboboxlist.insert(5, self.ui.combo5)
        # self.comboboxlist.insert(6, self.ui.combo6)
        # self.comboboxlist.insert(7, self.ui.combo7)
        # self.comboboxlist.insert(8, self.ui.combo8)
        # self.comboboxlist.insert(9, self.ui.combo9)
        # self.comboboxlist.insert(10, self.ui.combo10)
        # for row in dbclient.get_zerno():
        #     for i in range(1,11):
        #         self.comboboxlist[i].addItem(row[1])

        self.labellist = range(10)
        self.labellist.insert(1, self.ui.labelbanka1)

        self.labellist.insert(2, self.ui.labelbanka2)
        self.labellist.insert(3, self.ui.labelbanka3)
        self.labellist.insert(4, self.ui.labelbanka4)
        self.labellist.insert(5, self.ui.labelbanka5)
        self.labellist.insert(6, self.ui.labelbanka6)
        self.labellist.insert(7, self.ui.labelbanka7)
        self.labellist.insert(8, self.ui.labelbanka8)
        self.labellist.insert(9, self.ui.labelbanka9)
        self.labellist.insert(10, self.ui.labelbanka10)
        self.combolist = range(10)
        self.combolist.insert(1, self.ui.comboBox_1)
        self.combolist.insert(2, self.ui.comboBox_2)
        self.combolist.insert(3, self.ui.comboBox_3)
        self.combolist.insert(4, self.ui.comboBox_4)
        self.combolist.insert(5, self.ui.comboBox_5)
        self.combolist.insert(6, self.ui.comboBox_6)
        self.combolist.insert(7, self.ui.comboBox_7)
        self.combolist.insert(8, self.ui.comboBox_8)
        self.combolist.insert(9, self.ui.comboBox_9)
        self.combolist.insert(10,self.ui.comboBox_10)
        for i in range(1, 11):
            self.labellist[i].setText(zerno_[i][1])
        for row in dbclient.get_zerno():
            for i in range(1,11):
                self.combolist[i].addItem(row[1])
        self.connect(self.combolist[1], QtCore.SIGNAL("currentIndexChanged(const  QString&)"),lambda : self.comboslot(1) )  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[2], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda : self.comboslot(2))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[3], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda : self.comboslot(3))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[4], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda : self.comboslot(4))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[5], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(5))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[6], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(6))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[7], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(7))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[8], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(8))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[9], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(9))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[10], QtCore.SIGNAL("currentIndexChanged(const QString&)"),lambda: self.comboslot(10))  # lambda who=i: self.comboslot(who)
    def comboslot(self,i):
        print "Силос <ЗЕРНО>  №"+str(i)
        self.labellist[i].setText(self.combolist[i].currentText())
    def btnapplyclk(self):
        print "Сохранение изменений!"
        # print unicode(self.ui.labelbanka1.text())
        for i in range(1,11):
            nameprod = unicode(self.labellist[i].text())
            prod=self.dbclient.get_id_product(nameprod.encode('utf8'))
            self.dbclient.save_product(i,prod)



class Dialog_dobavka(QDialog, Ui_Dialog_Dobavka):
    def __init__(self, dbclient, conf):
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


class Dialog_korm(QDialog, Ui_Dialog_Korm):
    def __init__(self, dbclient):
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


class Dialog_calibration(QDialog, ):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Cal()
        self.ui.setupUi(self)

def takeover(object):
    object.busy = True

def free(object):
    object.busy = False

def wait(object):
    while (object.busy is True):
        delay(10)

def delay(tick):
    for i in range(0, tick):
        pass

def getbit(reg16, indexbit):
    if reg16 & (1 << indexbit) is not 0:
        return 1
    else:
        return 0

class objs(object):
    def __init__(self, *obj):
        self.list_ = (obj)
        self.state = False

    def switch(self, bit):
        for i in range(0, len(self.list_)):
            self.state = self.list_[i].switch(bit)

class obj(QtCore.QObject):
    qtobj = 0
    movie = ''
    numbit = 0
    imgtrue = ''
    imgfalse = ''
    state = False
    instate = False

    def __init__(self, object, imgfalse, imgtrue, giftrue='', flaginvers=False, flagonclick=False):
        self.imgfalse = imgfalse
        self.imgtrue = imgtrue
        self.qtobj = object
        self.flaginverslogic = flaginvers
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

class mbclient(object):
    def __init__(self, PLCaddress, PLCport):
        # self.client = ModbusClient(PLCaddress, port=PLCport)
        self.client = ModbusClient()
        self.plcaddr=PLCaddress
        self.port=PLCport
        self.client.host(PLCaddress)
        self.client.port(PLCport)
        self.client.timeout = 5000
        self.busy = False
        self.okconnection = False
        self.connect()
    def checkconnecttcp(self):
        if not self.client.is_open():
            logging.info(str(datetime.datetime.now())+'!!!!!!!!!!!! No connection !!!!!!!!!!!!!!!')
            print str(datetime.datetime.now())+('!!!!!!!!!!!! No connection !!!!!!!!!!!!!!!')
            self.connect()
        else:
            # print "Ok connection"
            pass

    def connect(self):

        self.okconnection = False
        self.client = ModbusClient()
        self.client.host(self.plcaddr)
        self.client.port(self.port)
        self.client.timeout = 5000
        while not self.okconnection == True:
            try:
                self.client.close()
                self.okconnection = self.client.open()
                # self.client.auto_open()
                # wait(self)
            except Exception as err:
                print str(datetime.datetime.now())+"--Ошибка подключения "+ str(err)
                logging.error(traceback.format_exc())

        # print self.client.__sock
        return self.okconnection

    def disconnect(self):
        return self.client.close()

    def send(self, rgadr, val):
        self.checkconnecttcp()
        is_Ok=False

        # rq = self.client.write_register(rgadr, val, unit=1)
        # write_single_register(reg_addr, reg_value)[source]
        while(is_Ok==False):
            try:
                wait(self)
                takeover(self)
                is_Ok=self.client.write_single_register(rgadr, val)
            except Exception as err:
                print  str(datetime.datetime.now())+"--Ошибка записи регистра с номером : " + str(rgadr) + " Ошибка:"+str(err)
                logging.error(traceback.format_exc())
            finally:
                free(self)
        return is_Ok
    def read(self, rgadr):

        self.checkconnecttcp()
        wait(self)
        takeover(self)
        result = 0
        # read_holding_registers(reg_addr, reg_nb=1)
        # result= self.client.read_holding_registers(rgadr,1,unit=1)
        try:
            result = self.client.read_holding_registers(rgadr, 1)
        except Exception as err:
            print str(datetime.datetime.now())+"--Ошибка чтения регистра " + str(err)
            logging.error(traceback.format_exc())
        finally:
            free(self)
            # return result.getRegister(0)
            if isinstance(result, list):
                return result[0]
            else:
                return 0

    def readcoil(self, bit):
        self.checkconnecttcp()
        wait(self)
        takeover(self)
        # type: (object) -> object
        # incoil=self.client.read_coils(bit,1,unit=0x01)
        # read_coils(bit_addr, bit_nb=1)
        try:
            incoil = self.client.read_coils(bit, 1)
        except (AttributeError, TypeError, self.client.last_error()):
            print self.client.last_error() + "Error read coil with number " + str(bit)
            # free(self)
            # return False
        free(self)
        return incoil[0]
        # return incoil[0]

    def getbyteL(self, word):
        HH = 0b00001111
        return word & HH

    def getbyteH(self, word):
        LL = 0b11110000
        return word & LL

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
        self.count = 0
        self.needcount  = 0
        self.selectkormnumbanka = []
        self.nowkormnumbanka = 0
        self.masloneed = 0
        self.handdobavka = 0
        self.step = 0
        self.zakaz = plclist()
        self.listzernoneed = plclist()
        self.listdobavkaneed = plclist()
        self.receptlist = {}
        self.stages = plclist()
        self.two_stage = False
        self.indexmuchdobavka = 0
        self.getzakazcomplete = False  # Для процедуры заполнения массива zakaz, для предотвращения рассинхрона
        self.commands = []
        self.endciclecomplete= False
    def setstep(self, num):
        self.step = num

    def stepnow(self, num):
        if self.step is num:
            return True
        else:
            return False

    def deccount(self):
        if self.count is not 0:
            self.count -= 1

class PLC(object):
    def __init__(self, mbclient):
        self.cmd = 0  # регистр команд
        self.ret = 0  # регистр return ответа ПЛК
        self.mbclient = mbclient
        self.listplccoils = plclist()
        self.listplcrg16 = plclist()
        self.recept = plcrecept()
        self.countqueue = 0
        self.steptext = ''
        self.needstate = 1
        self.recept.receptlist = loadrecepts()
        self.status = 0
        self.tick = False
        self.kormbankauplevel=[88,90,92,94,96,98]

    def send_cmd(self, cmd):
        # self.send_ret(0)
        # wreg = self.listplcrg16.getelement(0)
        wreg = mbclient.read(0)
        breg = wreg & 0xFF00
        self.mbclient.send(0, cmd | breg)


    def send_cmd_val(self, cmd, val):
        self.mbclient.send(0, cmd + (val << 8))

    def send_ret(self, val):
        # wreg = self.listplcrg16.getelement(1)
        wreg = mbclient.read(1)
        breg = wreg & 0xFF00
        mbclient.send(1, val | breg)

    def get_ret(self):
        # wreg=self.listplcrg16.getelement(1)
        # print "getstate >> "+str(wreg)
        wreg = mbclient.read(1)
        if type(wreg) is None:
            self.ret = 0
        else:
            self.ret = wreg & 0x00FF

    def waitret(self):
        while (True):
            answer = mbclient.read(0) & 0x00FF
            delay(10000)
            if answer == 0:
                print str(datetime.datetime.now())+"--answer" + str(answer)
                break
                # rg = mbclient.read(0)

    def addqueue(self):
        self.countqueue += 1

    def decqueue(self):
        self.countqueue -= 1

    def nullqueue(self):
        self.countqueue = 0

class ThreadPullPLCList(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)

    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadPullPLCList started"
        while self._isRunning is True:
            listcoillocal_ = range(100)
            listweightzernolocal_ = range(10)
            listweightdobavkalocal_ = range(6)
            for i in range(0, COUNTsiloszerno + 1):
                listweightzernolocal_.insert(i, plcglobal.listplcrg16.getelement(i + OFFSETsiloszerno))
            plcglobal.recept.listzernoneed.pull(listweightzernolocal_)
            for i in range(0, COUNTsilosdobavka + 1):
                listweightdobavkalocal_.insert(i, plcglobal.listplcrg16.getelement(i + OFFSETsilosdobavka))
            plcglobal.recept.listdobavkaneed.pull(listweightdobavkalocal_)
            plcglobal.recept.masloneed = plcglobal.listplcrg16.getelement(OFFSETsilosmaslo)
            for i in range(0, 7):
                for j in range(0, 16):
                    delay(1000)
                    listcoillocal_.insert(i * 16 + j, getbit(plcglobal.listplcrg16.getelement(i + OFFSETflagstate), j))
            plcglobal.listplccoils.pull(listcoillocal_)
            # plcglobal.get_state()
        print str(datetime.datetime.now())+"---thread ThreadPullPLCList done"
        self.finished.emit()

        def stop(self):
            self._isRunning = False

class ThreadGetPLC(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)

    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadGetPLC started"
        while self._isRunning is True:
            # mbclient.checkconnecttcp()
            listrg16local_ = range(LASTREGADDR + 1)
            plcglobal.status = mbclient.read(REG_STATUS)
            for i in range(0, LASTREGADDR + 1):
                delay(1000)
                try:
                    listrg16local_.insert(i, mbclient.read(i))
                except Exception as err:
                    print str(datetime.datetime.now())+"--Error in ThreadGetPLC "+str(err)
            plcglobal.listplcrg16.pull(listrg16local_)
        print str(datetime.datetime.now())+"---thread ThreadGetPLC done"

    def stop(self):
        self._isRunning = False

class ThreadVisual1Level(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    vesisignal = QtCore.pyqtSignal(int, int, int)
    s1 = QtCore.pyqtSignal(int, int)
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self, plc):
        QtCore.QObject.__init__(self)
        self.plc = plc

    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadVisual1Level started"
        while self._isRunning is True:

            for i in range(0, 109 + 1):
                delay(10000)
                self.s1.emit(i, plcglobal.listplccoils.getelement(i))
                self.vesisignal.emit(plcglobal.listplcrg16.getelement(VES1INDEX),
                                     plcglobal.listplcrg16.getelement(VES2INDEX),
                                     plcglobal.listplcrg16.getelement(VES3INDEX))

            if plcglobal.listplccoils.list[72]==True:
                if plcglobal.listplccoils.list[80]==True:
                    plcglobal.recept.nowkormnumbanka = 1
                else:
                    if  plcglobal.listplccoils.list[82]==True:
                        plcglobal.recept.nowkormnumbanka = 2
                    else:
                        plcglobal.recept.nowkormnumbanka = 3

            if plcglobal.listplccoils.list[73] == True:
                if plcglobal.listplccoils.list[84]==True:
                    plcglobal.recept.nowkormnumbanka = 4
                else:
                    if  plcglobal.listplccoils.list[86]==True:
                        plcglobal.recept.nowkormnumbanka = 5
                    else:
                        plcglobal.recept.nowkormnumbanka = 6

        print str(datetime.datetime.now())+'---thread ThreadVisual1Level FINISHED'
        self.finished.emit()

    def stop(self):
        self._isRunning = False

class ThreadVizual2level(QtCore.QObject):  # визулизация шиберов- по состоянию концевиков
    finished = QtCore.pyqtSignal()
    s3 = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadVizual2level started"
        while self._isRunning is True:
            self.s3.emit()
            delay(10000)
            # print 'FINISHED'
        print str(datetime.datetime.now())+"--+thread ThreadVizual2level done"
        self.finished.emit()

    def stop(self):
        self._isRunning = False

class ThreadPowerOnSystem(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    def __init__(self, plc_, mbclient_):
        QtCore.QObject.__init__(self)

    @QtCore.pyqtSlot()
    def process(self):
        plcglobal.send_cmd(101)  # Включение линии1
        plcglobal.waitret()
        plcglobal.send_cmd(201)  # Включение линии2
        plcglobal.waitret()
        plcglobal.send_cmd(41)  # Включение миксера

    def stop(self):
        self._isRunning = False

class ThreadWeight(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    def __init__(self):
        QtCore.QObject.__init__(self)

    @QtCore.pyqtSlot()
    def process(self):
        while self._isRunning==True:
            pass
        self.finished.emit()
    def stop(self):
        self._isRunning = False


class ThreadSendCmd(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    def __init__(self, cmd):
        QtCore.QObject.__init__(self)
        self.cmd = cmd

    @QtCore.pyqtSlot()
    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadSendCmd started  cmd= " + str(self.cmd)
        plcglobal.waitret()
        plcglobal.send_cmd(self.cmd)
        self.finished.emit()

    def stop(self):
        self._isRunning = False


class ThreadWorkZames(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    startcicle = QtCore.pyqtSignal()
    getrecept = QtCore.pyqtSignal()
    endcicle = QtCore.pyqtSignal()
    starttimer = QtCore.pyqtSignal(int)
    checklevelkorm = QtCore.pyqtSignal()
    changenoria = QtCore.pyqtSignal(int)
    newcicle = False
    zames_complete = False
    _isRunning = False
    session_begin = False
    session_end = False


    def __init__(self, plc_, mbclient_):
        QtCore.QObject.__init__(self)
        # self.mbclient=mbclient_
        # self.plc=plc_

    @QtCore.pyqtSlot()
    def process(self):
        print str(datetime.datetime.now())+"--+thread ThreadWorkZames started"
        # f = open('c:\\stages.txt', 'w')
        # >> > f.write('HelloWorld!')
        # >> > f.()
        while self._isRunning is True:


            ves1 = plcglobal.listplcrg16.getelement(VES1INDEX)
            ves2 = plcglobal.listplcrg16.getelement(VES2INDEX)
            ves3 = plcglobal.listplcrg16.getelement(VES3INDEX)
            if ves2 > VESMAX | ves3 > VESMAX:
                print str(datetime.datetime.now())+"--Достигнуто максимальное значение весов, обнулите"
            print str(datetime.datetime.now())+ "--Ожидание обнуления весов"
            while ves2 > VESMAX and ves3 > VESMAX:
                ves1 = plcglobal.listplcrg16.getelement(VES1INDEX)
                ves2 = plcglobal.listplcrg16.getelement(VES2INDEX)
                ves3 = plcglobal.listplcrg16.getelement(VES3INDEX)
            print str(datetime.datetime.now())+ "--весы обнулены"

            plcglobal.waitret()
            # plcglobal.send_cmd(COMMAND_MIXER_UNLOAD)
            plcglobal.waitret()
            plcglobal.send_cmd(COMMAND_INIT)

            plcglobal.waitret()
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT1)
            plcglobal.waitret()
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT2)
            plcglobal.waitret()
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT3)
            plcglobal.waitret()
            plcglobal.send_cmd(COMMAND_LINE2_START)

            # def noriainit(num_banka):
            #     # self.startThreadCmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
            #     pass

            # dbstatus = mbclient.read(REG_STATUS)
            # noriaready = getbit(dbstatus, NORIAREADYLOAD)
            # while(noriaready!=1):
            #     noriaready = getbit(dbstatus, NORIAREADYLOAD)
            # plcglobal.waitret()
            # plcglobal.send_cmd_val(COMMAND_NORIA_INIT,plcglobal.recept.selectkormnumbanka[0])
            self.session_begin = True
            plcglobal.recept.count = 0
            print str(datetime.datetime.now())+"--session begin"
            self.newcicle=True
            while self.session_begin == True:
                if self.newcicle==True :    # Если текущий счетчик замесов обнулен
                    print  str(datetime.datetime.now())+"--plcglobal.recept.count =0, заполняем editы согласно очереди"
                    self.getrecept.emit()  # Взять текущий рецепт из очереди и заполнить все edit'ы согласно текущему рецепту
                    plcglobal.recept.getzakazcomplete = False
                    self.startcicle.emit()  # plcglobal.recept.zakaz.pull() заполняем массив заказа
                    # f.write("Session emit")
                    dobavka = range(6)
                    alldobavka = 0
                    MAX_DOBAVKA = 900
                    MAX_ONE_DOBAVKA = 300
                    while plcglobal.recept.getzakazcomplete != True:
                        pass
                    plcglobal.recept.getzakazcomplete = False
                    for i in range(0, 6):
                        dobavka[i] = plcglobal.recept.zakaz.getelement(i + 8)  # Отправка рецепта добавок с 28 по 33
                        print plcglobal.recept.zakaz.getelement(i)
                        print dobavka[i]
                        alldobavka += dobavka[i]
                    print "all dobavka" + str(alldobavka)
                    # print plcglobal.recept.selectkormnumbanka[0]

                    if alldobavka > MAX_DOBAVKA:
                        plcglobal.recept.two_stage = True
                    else:
                        plcglobal.recept.two_stage = False

                # print "session begin"
                    if plcglobal.recept.two_stage == True:
                        print str(datetime.datetime.now())+"--Отправка рецепта зерно и добавки(половинный)"
                        for i in range(8, 14):
                            if i != plcglobal.recept.indexmuchdobavka:
                                print plcglobal.recept.zakaz.getelement(i) / 2
                                mbclient.send(i + 20, plcglobal.recept.zakaz.getelement(i) / 2)  # Отправка рецепта добавок с 28 по 33
                        for i in range(0, 8):
                            print plcglobal.recept.zakaz.getelement(i) / 2
                            mbclient.send(i + 20, plcglobal.recept.zakaz.getelement(i) / 2)  # Отправка рецепта зерна
                        plcglobal.recept.count = plcglobal.recept.count * 2
                        # print "Mul ="+str(plcglobal.recept.count)
                    else:
                        print str(datetime.datetime.now())+"--Отправка рецепта добавка и зерно(все)"
                        for i in range(8, 14):
                            print plcglobal.recept.zakaz.getelement(i)
                            mbclient.send(i + 20,plcglobal.recept.zakaz.getelement(i))  # Отправка рецепта добавок с 28 по 33
                        for i in range(0, 8):
                            print plcglobal.recept.zakaz.getelement(i)
                            mbclient.send(i + 20, plcglobal.recept.zakaz.getelement(i))  # Отправка рецепта зерна


                    print str(datetime.datetime.now())+"--while plcglobal.recept.count !=0"
                    print str(datetime.datetime.now())+ "--count = "+ str(plcglobal.recept.count)
                    logging.info(str(datetime.datetime.now())+"==! count = "+str(plcglobal.recept.count))
                    # plcglobal.recept.stages.reinit()
                    logging.info(str(datetime.datetime.now())+"==! zames start! ")
                    self.checklevelkorm.emit()
                    self.newcicle=False
                # while(plcglobal.recept.count>0):

                dbstatus=mbclient.read(REG_STATUS)
                ves2readyload = getbit(dbstatus, VES2READYLOAD)
                ves3readyload = getbit(dbstatus, VES3READYLOAD)
                mixerreadyload = getbit(dbstatus, MIXERREADYLOAD)
                mixerreadyunload = getbit(dbstatus,MIXERREADYUNLOAD)
                line1readyload = getbit(dbstatus, LINE1READYLOAD)
                line2readyload = getbit(dbstatus, LINE2READYLOAD)
                ves2readyunload = getbit(dbstatus, VES2READYUNLOAD)
                ves3readyunload = getbit(dbstatus, VES3READYUNLOAD)
                oilready=getbit(dbstatus,MASLOREADY)
                noriaready = getbit(dbstatus, NORIAREADYLOAD)
                delay(1000)
                #
                # if noriaready == 1 and plcglobal.recept.selectkormnumbanka[0]!=0:
                #     pass

                if ves2readyload == 1:
                    # if COMMAND_VES12_START not in plcglobal.recept.stages.list or plcglobal.recept.count > 1:
                    delay(1000)

                    if plcglobal.recept.count<=0:
                        # self.session_begin=False
                        # print str(datetime.datetime.now())+"--session_begin=False"
                        # print str(datetime.datetime.now()) + "--Done"
                        print "end count= " + str(plcglobal.recept.count)
                        print str(datetime.datetime.now()) + "--Счетчик <Количество замесов> достиг нуля- изготовление цикла(рецепта) завершено! Переход к следующему циклу"
                        plcglobal.recept.endciclecomplete = False
                        self.endcicle.emit()  # следующий цикл замесов (следующий рецепт)
                        print   str(datetime.datetime.now()) + "--Ожидание исполнения endcicle.emit "
                        while(plcglobal.recept.endciclecomplete==False):
                            pass
                        print   str(datetime.datetime.now()) + "--endcicle.emit завершено"
                        plcglobal.recept.endciclecomplete = False
                        if plcglobal.countqueue <= 0:
                            self.session_end=True
                        else:
                            self.newcicle=True
                    else:
                        plcglobal.waitret()
                        plcglobal.send_cmd(COMMAND_VES12_START)
                        print (str(datetime.datetime.now())+"--COMMAND_VES12_START")
                        logging.info(str(datetime.datetime.now())+"==!COMMAND_VES12_START")
                        plcglobal.recept.stages.list.append(COMMAND_VES12_START)

                        # if plcglobal.recept.count > 0:
                            # if plcglobal.recept.count == 1:
                            #     if plcglobal.countqueue > 1:
                            #         self.newcicle=True
                            #         print str(datetime.datetime.now()) +"--<Количество замесов>  равно 1 И <Количество циклов> больше 1, готовим следующий цикл"
                            #     else:
                            #         self.newcicle = False
                            #         print str(datetime.datetime.now()) + "--<Количество замесов>  равно 1 И <Количество циклов> меньше или равно 1, НЕ готовим следующий цикл"
                        plcglobal.recept.count = plcglobal.recept.count - 1
                        print str(datetime.datetime.now()) + "--plglobal.recept.count =" + str(plcglobal.recept.count)
                        self.checklevelkorm.emit()

                            # self.checklevelkorm.emit()
                if noriaready == 1 and plcglobal.recept.selectkormnumbanka[0] != plcglobal.recept.nowkormnumbanka:
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))

                if ves3readyload == 1:
                    # if  plcglobal.recept.count>1 or COMMAND_VES3_START not in plcglobal.recept.stages.list:
                    # if COMMAND_VES3_START not in plcglobal.recept.stages.list:
                    delay(1000)
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_VES3_START)
                    print (str(datetime.datetime.now())+"--COMMAND_VES3_START")
                    logging.info(str(datetime.datetime.now())+"==!COMMAND_VES3_START")
                    plcglobal.recept.stages.list.append(COMMAND_VES3_START)
                if ves2readyunload == 1 and line2readyload == 1 and mixerreadyload==1 and COMMAND_VES2_UNLOAD not in plcglobal.recept.stages.list :
                    delay(1000)
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_VES2_UNLOAD)

                    print (str(datetime.datetime.now())+"--COMMAND_VES2_UNLOAD")
                    logging.info(str(datetime.datetime.now())+"==!COMMAND_VES2_UNLOAD")
                    plcglobal.recept.stages.list.append(COMMAND_VES2_UNLOAD)
                    plcglobal.tick=False
                    self.starttimer.emit(60000)  # таймер 1 минута 60000 милисекунд
                    # self.starttimer.emit(300)
                    if plcglobal.recept.count > 0:
                        if plcglobal.recept.count == 1:
                            if plcglobal.countqueue > 1:
                                self.newcicle = True
                                print str(datetime.datetime.now()) + "--<Количество замесов>  равно 1 И <Количество циклов> больше 1, готовим следующий цикл"
                            else:
                                self.newcicle = False
                                print str(datetime.datetime.now()) + "--<Количество замесов>  равно 1 И <Количество циклов> меньше или равно 1, НЕ готовим следующий цикл"
                if ves3readyunload == 1 and plcglobal.tick==True  and COMMAND_VES2_UNLOAD in plcglobal.recept.stages.list and COMMAND_VES3_UNLOAD not in plcglobal.recept.stages.list:
                    delay(1000)
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_VES3_UNLOAD)
                    print str(datetime.datetime.now())+("--COMMAND_VES3_UNLOAD")
                    logging.info(str(datetime.datetime.now())+"==!COMMAND_VES3_UNLOAD")
                    plcglobal.recept.stages.list.append(COMMAND_VES3_UNLOAD)
                    print str(datetime.datetime.now())+("--COMMAND_OIL_START")
                    logging.info(str(datetime.datetime.now())+"==!COMMAND_OIL_START")
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_OIL_START)
                    plcglobal.recept.stages.list.append(COMMAND_OIL_START)
                if mixerreadyunload == 1  and COMMAND_MIXER_UNLOAD not in plcglobal.recept.stages.list  and oilready == 1 and COMMAND_VES3_UNLOAD in plcglobal.recept.stages.list:
                # if mixerreadyunload == 1 and COMMAND_MIXER_UNLOAD not in plcglobal.recept.stages.list:
                    print str(datetime.datetime.now())+ "--mixerreadyunload = "+str(mixerreadyunload)
                    plcglobal.tick = False
                    plcglobal.waitret()
                    plcglobal.send_cmd(COMMAND_MIXER_UNLOAD)
                    # f.write("COMMAND_MIXER_UNLOAD")
                    plcglobal.recept.stages.list.append(COMMAND_MIXER_UNLOAD)
                    print str(datetime.datetime.now()) +"--ВЫГРУЗИЛ!"
                    logging.info(str(datetime.datetime.now())+"==!COMMAND_MIXER_UNLOAD")
                    # self.session_begin=False

                    # plcglobal.recept.stages.reinit()
                    # plcglobal.recept.stages.list.remove(COMMAND_VES3_UNLOAD)
                    plcglobal.recept.stages.list.remove(COMMAND_VES3_UNLOAD)
                    plcglobal.recept.stages.list.remove(COMMAND_VES2_UNLOAD)
                    plcglobal.recept.stages.list.remove(COMMAND_MIXER_UNLOAD)
                    # plcglobal.recept.stages.list.remove(COMMAND_VES3_START)
                    if self.session_end==True:
                        print str(datetime.datetime.now()) + "Счетчик <Количество циклов> достиг нуля- сессия завершена; countcicle = " + str(plcglobal.countqueue)
                        self.session_begin = False
                        self._isRunning = False
                        self.newcicle = False
        self._isRunning = False
        self.finished.emit()
        print str(datetime.datetime.now())+"-thread ThreadWorkZames is done"

    def stop(self):
        self._isRunning = False


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    movies = []
    moviesL2 = []

    def __init__(self, dbclient):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)
        self.pausebtn.clicked.connect(self.pausebtnclk)
        self.addtoqueuebtn.clicked.connect(self.addqueuebtnclk)

        self.dbclient = dbclient
        # self.tableview.setRowCount(2)
        # self.tableView.setColumnCount(2)
        # loadfromini('korm999')
        self.zeroves1btn.clicked.connect(self.zeroves1btnclk)
        self.zeroves2btn.clicked.connect(self.zeroves2btnclk)
        self.zeroves3btn.clicked.connect(self.zeroves3btnclk)
        self.moviesL2.insert(0, objs( obj(self.ves1shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves1,"","lineves1.png","")))
        self.moviesL2.insert(1, objs( obj(self.ves2shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves2,"","lineves2.png","")))
        self.moviesL2.insert(2, objs( obj(self.ves3shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves3,"","line3mixer.png","")))
        self.moviesL2.insert(3, objs( obj(self.silos1dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(4, objs( obj(self.silos2dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(5, objs( obj(self.silos3dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(6, objs( obj(self.silos4dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(7, objs( obj(self.silos5dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(8, objs( obj(self.silos6dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(9, objs( obj(self.silos1shiber, "silosshiberclose.png", "silosshiberopen.png", ""))) # комбикорм
        self.moviesL2.insert(10, objs( obj(self.silos2shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(11, objs( obj(self.silos4shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(12, objs( obj(self.silos5shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(13, objs( obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", ''),obj(self.linemixerbunker,"","linemixerbunker.png","")))


        # reg0Low  cmd
        # reg0High value
        # reg1Low  Ret
        # reg1High Auto Ruchno Stop:
        #   0 - auto main
        #   1 - ruchno main
        #   2 - stop main
        #   3 - dbauto zerno
        #   4 - dbauto dob
        #   5 - dbauto korm
        # reg2 Empty
        # reg3Low  chastot1
        # reg3High chastot2
        # reg4 ves1
        # reg5 ves2
        # reg6 ves3
        # reg7 PLC1 (dobavki)
        self.movies.insert(0, objs(obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png")))
        self.movies.insert(1, objs(obj(self.dobavkisilos1do, "statusfalse.png", "statustrue.png")))
        self.movies.insert(2, objs(obj(self.silos1dobavkaopen, "statusminifalse.png", "statusminitrue.png"),
                                   obj(self.silos1dobavkashiber, "silosshiberclose.png", "silosshiberopen.png")))
        self.movies.insert(3, objs(obj(self.silos1dobavkaclose, "statusminifalse.png", "statusminitrue.png"),
                                   obj(self.silos1dobavkashiber, "silosshiberopen.png", "silosshiberclose.png")))
        self.movies.insert(4, objs(obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png")))
        self.movies.insert(5, objs(obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png")))
        self.movies.insert(6, objs(obj(self.silos2dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),
                                   obj(self.silos2dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(7, objs(obj(self.silos2dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),
                                   obj(self.silos2dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(8, objs(obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", "")))
        # reg7 PLC2(dobavki)
        self.movies.insert(9, objs(obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(10, objs(obj(self.silos3dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos3dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(11, objs(obj(self.silos3dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos3dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(12, objs(obj(self.dobavkisilos4up, "statusfalse.png", "statu9strue.png", "")))
        self.movies.insert(13, objs(obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(14, objs(obj(self.silos4dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos4dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(15, objs(obj(self.silos4dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos4dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        # reg8 PLC3(dobavki)
        self.movies.insert(16, objs(obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(17, objs(obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(18, objs(obj(self.silos5dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos5dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(19, objs(obj(self.silos5dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos5dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        self.movies.insert(20, objs(obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(21, objs(obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(22, objs(obj(self.silos6dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos6dobavkashiber, "silosshiberclose.png", "silosshiberopen.png", '')))
        self.movies.insert(23, objs(obj(self.silos6dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''),
                                    obj(self.silos6dobavkashiber, "silosshiberopen.png", "silosshiberclose.png", '')))
        # reg8 PLC4 dobavki
        self.movies.insert(24, objs(obj(self.flex1, "flex1stop.png", "flex1run.png", ''),
                                    obj(self.flex1_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(25, objs(obj(self.flex2, "flex2stop.png", "flex2run.png", ''),
                                    obj(self.flex2_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(26, objs(obj(self.flex3, "flex3stop.png", "flex3run.png", ''),
                                    obj(self.flex3_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(27, objs(obj(self.flex4, "flex4stop.png", "flex4run.png", ''),
                                    obj(self.flex4_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(28, objs(obj(self.flex5, "flex5stop.png", "flex5run.png", ''),
                                    obj(self.flex5_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(29, objs(obj(self.flex6, "flex6stop.png", "flex6run.png", ''),
                                    obj(self.flex6_2, "shnek_nakl_stop.gif", "", 'shnek_nakl_begin.gif')))
        self.movies.insert(30, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # Авто режим масло
        # self.movies.insert(31, objs(obj(self.maslonasos, "motor.gif", "",
        #                                 "motor_active.gif")))  # Масло насос motor.gif", "", 'motor_active.gif'
        self.movies.insert(31, objs(obj(self.masloline, "", "lineoilmixer.png",""),obj(self.maslonasos, "motor.gif", "", "motor_active.gif")))  # Масло насос motor.gif", "", 'motor_active.gif'
        # reg9 PLC5 dobavki
        self.movies.insert(32, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        self.movies.insert(33, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        self.movies.insert(34, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        self.movies.insert(35, objs(obj(self.flexload, "flexloadstop.png", "flexloadrun.png", ''),
                                    obj(self.motorflexload, "motor.gif", "", 'motor_active.gif')))
        self.movies.insert(36, objs(obj(self.bunkerloaddo, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(37, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        self.movies.insert(38, objs(obj(self.ves3sensopen, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(39, objs(obj(self.ves3sensclose, "statusminifalse.png", "statusminitrue.png", '')))
        # reg9 PLC6(mixer)
        self.movies.insert(40, objs(obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", '')))  # reserv
        self.movies.insert(41, objs(obj(self.mixersensopen, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(42, objs(obj(self.mixersensclose, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(43, objs(obj(self.mixer, "mixerstop.png", '', "mixerbegin.gif")))
        self.movies.insert(44, objs(obj(self.mixer_2, "mixer2_stop.png", "", "mixer2_run")))  # mixer2
        self.movies.insert(45, objs(obj(self.mixerbunkersens, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(46, objs(obj(self.mixershnek1, "shnek_hor_stop.gif", "", "shnek_hor_begin.gif")))
        self.movies.insert(78, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        # reg10 PLC7 (zerno)
        self.movies.insert(48, objs(obj(self.ves1sensopen, "statusminifalse.png", "statusminitrue.png", '')))  #
        self.movies.insert(49, objs(obj(self.ves1sensclose, "statusminifalse.png", "statusminitrue.png", '')))  #
        self.movies.insert(50, objs(obj(self.ves2sensopen, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(51, objs(obj(self.ves2sensclose, "statusminifalse.png", "statusminitrue.png", '')))
        self.movies.insert(52, objs(obj(self.ves1bunkersens, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(53, objs(obj(self.ves2bunkersens1, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(54, objs(obj(self.ves2bunkersens2, "statusfalse.png", "statustrue.png", '')))
        self.movies.insert(55, objs(obj(self.autokombikorm, "statusfalse.png", "statustrue.png", "")))  # reserv
        # reg10 PLC8(zerno)
        self.movies.insert(56, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv shnek1
        self.movies.insert(57, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv shnek2
        self.movies.insert(58, objs(obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", ""),
                                    obj(self.zernoshnek3_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(59, objs(obj(self.zernoshnek4, "shnek4zernostop.png", "shnek4zernorun.png", ""),
                                    obj(self.zernoshnek4_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(60, objs(obj(self.zernoshnek5, "shnek5zernostop.png", "shnek5zernorun.png", ""),
                                    obj(self.zernoshnek5_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(61, objs(obj(self.zernoshnek6, "shnek6zernostop.png", "shnek6zernorun.png", ""),
                                    obj(self.zernoshnek6_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(62, objs(obj(self.zernoshnek7, "shnek7zernostop.png", "shnek7zernorun.png", ""),
                                    obj(self.zernoshnek7_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(63, objs(obj(self.zernoshnek8, "shnek8zernostop.png", "shnek8zernorun.png", ""),
                                    obj(self.zernoshnek8_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        # reg11 PLC9 (zerno) (self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""),obj(self.zernoshnek9_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")
        self.movies.insert(64, objs(obj(self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""),
                                    obj(self.zernoshnek9_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(65, objs(obj(self.zernoshnek10, "shnek10zernostop.png", "shnek10zernorun.png", ""),
                                    obj(self.zernoshnek10_2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(66, objs(obj(self.drobilka1, "drobilka_off.png", "", "drobilkabegin"),obj(self.linedrobilka1, "", "linedrobilka1.png", "")))
        self.movies.insert(67, objs(obj(self.drobilka2, "drobilka_off.png", "", "drobilkabegin"),obj(self.linedrobilka2, "", "linedrobilka2.png", "")))
        self.movies.insert(68, objs(obj(self.ves2shnek, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"),obj(self.line2shnekmixer,"","linetomixer2.png","")))
        self.movies.insert(69, objs(obj(self.ves1shnek1, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(70, objs(obj(self.ves1shnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))
        self.movies.insert(71, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        # reg11 PLC10(kombikorm)
        self.movies.insert(72, objs(obj(self.klapan1, "klapan1false.png", "klapan1true.png", ""),obj(self.lineklapan1,"","lineklapan1.png","")))
        self.movies.insert(73, objs(obj(self.klapan2, "klapan2false.png", "", "klapan2true.png"),obj(self.lineklapan2,"","lineklapan2.png","")))
        self.movies.insert(74, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        self.movies.insert(75, objs(obj(self.noria, "noriastop.png", "", "noriabegin.gif")))
        self.movies.insert(76, objs(obj(self.terminator1, "terminator1stop.png", "", "terminator1.gif")))
        self.movies.insert(77, objs(obj(self.terminator2, "terminator2stop.png", "", "terminator2.gif")))
        self.movies.insert(78, objs( obj(self.mixershnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif")))  # Шнек наклонный перед норией
        self.movies.insert(79, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))  # reserv
        # reg12 PLC11(kombikorm)
        self.movies.insert(80, objs(obj(self.silos1shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(81, objs(obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(82, objs(obj(self.silos2shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(83, objs(obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(84, objs(obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(85, objs(obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(86, objs(obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        self.movies.insert(87, objs(obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        # reg12 PLC12(kombikorm)
        self.movies.insert(88, objs(obj(self.silos1up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(89, objs(obj(self.silos1do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(90, objs(obj(self.silos2up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(91, objs(obj(self.silos2do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(92, objs(obj(self.silos3up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(93, objs(obj(self.silos3do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(94, objs(obj(self.silos4up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(95, objs(obj(self.silos4do, "statusfalse.png", "statustrue.png", "")))
        # reg13 PLC13(kombokorm)
        self.movies.insert(96, objs(obj(self.silos5up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(97, objs(obj(self.silos5do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(98, objs(obj(self.silos6up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(99, objs(obj(self.silos6do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(100, objs(obj(self.zernosilos1, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(101, objs(obj(self.zernosilos2, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(102, objs(obj(self.zernosilos3, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(103, objs(obj(self.zernosilos4, "statusfalse.png", "statustrue.png", "")))
        # reg13 PLC14
        self.movies.insert(104, objs(obj(self.zernosilos5, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(105, objs(obj(self.zernosilos6, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(106, objs(obj(self.zernosilos7, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(107, objs(obj(self.zernosilos8, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(108, objs(obj(self.zernosilos9, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(109, objs(obj(self.zernosilos10, "statusfalse.png", "statustrue.png", "")))
        # self.movies.insert(101, obj(self.autoruchnokombikorm, "statusfalse.png","statustrue.png", ""))

        # reg14 PLC15
        # Error Warning
        #   0 ves1error
        #   1 ves2error
        #   2 ves3error
        #   3 errorlineK
        #   reserv
        #   reserv
        #   reserv
        #   reserv
        # reg14 plc16
        # empty
        # reg15
        # reg16
        # status moduls
        #   0 device2 40addr МУ11032Р
        #   1 41addr    МВ110-16Д
        #   2 42addr МВ110-16Д
        #   3 43addr    МВ110-32ДН
        #   4 15addr
        #   5 17addr
        #   6 50 1ТД Весы2
        #   7 1ТД Весы1
        # reg16High:
        #   51-32ДН
        #   52 - 16Д
        #   53 - МУ11032Р
        #   54 - СМИ2 Весы3
        #   55 - СМИ2 Весы1
        #   56 - СМИ2 ВЕСЫ2
        #   empty
        #   empty
        # reg17Low:
        #   72-1ТД Весы3
        #   73-ПР200
        #   31addr 16Д
        #   32addr
        #   33addr
        #   34addr
        #   21addr МУ110-32Р
        #   reserv
        # reg18-reg27 zerno
        # reg28-reg33 dobavka
        # reg34 maslo
        # reg35Low ?? dopdobavka
        # reg35High
        # reg36Low:
        #   status
        # reg36igh
        #   status
        # reg37-53 dbreturn zerno dobavka maslo


        self.interface_ = []
        self.interface_.append(obj(self.siloskorm1, "silos.png", "silos_active.png", "", False, True))
        self.interface_.append(obj(self.siloskorm2, "silos.png", "silos_active.png", "", False, True))
        self.interface_.append(obj(self.siloskorm3, "silos.png", "silos_active.png", "", False, True))
        self.interface_.append(obj(self.siloskorm4, "silos.png", "silos_active.png", "", False, True))
        self.interface_.append(obj(self.siloskorm5, "silos.png", "silos_active.png", "", False, True))
        self.interface_.append(obj(self.siloskorm6, "silos.png", "silos_active.png", "", False, True))
        # self.reinitmbtcp()
        self.editkorm.triggered.connect(self.kormtbtnclk)
        self.editzerno.triggered.connect(self.zernobtnclk)
        self.editrecept.triggered.connect(self.receptbtnclk)
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        self.actionexit.triggered.connect(self.exitclk)
        self.cal_action.triggered.connect(self.calclk)

        self.VES12GRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.VES12GRUOP.customContextMenuRequested.connect(self.ves12PopUp)
        self.VES3GRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.VES3GRUOP.customContextMenuRequested.connect(self.ves3PopUp)
        self.MASLOGRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.MASLOGRUOP.customContextMenuRequested.connect(self.masloPopUp)
        self.LINE1GRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.LINE1GRUOP.customContextMenuRequested.connect(self.line1PopUp)
        self.LINE2GRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.LINE2GRUOP.customContextMenuRequested.connect(self.line2PopUp)
        self.MIXERGRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.MIXERGRUOP.customContextMenuRequested.connect(self.mixerPopUp)
        self.mixershnek1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mixershnek1.customContextMenuRequested.connect(self.mixershnek1PopUp)
        self.NORIAGRUOP.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.NORIAGRUOP.customContextMenuRequested.connect(self.noriaPopUp)

        self.activethreads = []
        if DEBUGFLAG == False:
            self.startThreadVisual1Level(QThread(self), plcglobal)
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
        self.connect(self.comboBoxRecept, QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     self.comboboxchangedslot)
        self.comboBoxRecept.addItems(plcglobal.recept.receptlist.keys())
        self.comboBoxRecept.blockSignals(False)
        self.delbtn.clicked.connect(self.deleteallrow)
        # self.addtoqueuebtn.clicked.connect(self.addqueuebtnclk)
        self.tableWidget.setColumnWidth(0, 180)
        self.tableWidget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(u"Наименование комбикорма"))
        self.tableWidget.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem(u"Кол-во замесов"))
        self.currentrow = 0
        self.tableWidget.itemSelectionChanged.connect(self.getselectrow)

    def noriaPopUp(self, position):
        menu = QMenu()
        OnAction = menu.addAction(u"Включить")
        OffAction = menu.addAction(u"Выключить")
        SetupAction = menu.addAction(u"Настроить")
        InfoAction = menu.addAction(u"ИНФО")
        action = menu.exec_(self.NORIAGRUOP.mapToGlobal(position))
        if action == OnAction:
            print str(datetime.datetime.now())+"=PopUp noria On"
            plcglobal.recept.selectkormnumbanka = []
            for i in range(0, 6):
                if self.interface_[i].state is True:  # выделенную банку
                    plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
            # print plcglobal.recept.selectkormnumbanka[1]
            self.startThreadCmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
        if action == OffAction:
            print str(datetime.datetime.now())+"=PopUp noria Off"
            self.startThreadCmd(COMMAND_NORIA_STOP)
        if action == SetupAction:
            print str(datetime.datetime.now())+"=PopUp noria setup"
            plcglobal.recept.selectkormnumbanka = []
            for i in range(0, 6):
                if self.interface_[i].state is True:  # выделенную банку
                    plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
            self.startThreadCmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
        if action == InfoAction:
            print "Открыта банка №"+str(plcglobal.recept.nowkormnumbanka)
    def mixershnek1PopUp(self, position):
        menu = QMenu()
        OnAction = menu.addAction(u"Включить")
        OffAction = menu.addAction(u"Выключить")
        action = menu.exec_(self.mixershnek1.mapToGlobal(position))
        if action == OnAction:
            print str(datetime.datetime.now())+"=PopUp mixershnek1 On"
            self.startThreadCmd(COMMAND_SHNEKMIXER_ON)
        if action == OffAction:
            print str(datetime.datetime.now())+"=PopUp mixershnek1 Off"
            self.startThreadCmd(COMMAND_SHNEKMIXER_OFF)
    def mixerPopUp(self, position):
        menu = QMenu()
        OnAction = menu.addAction(u"Включить")
        OffAction = menu.addAction(u"Выключить")
        UnloadAction = menu.addAction(u"Выгрузить")
        action = menu.exec_(self.MIXERGRUOP.mapToGlobal(position))
        if action == UnloadAction:
            print "=PopUp Mixer Unload"
            self.startThreadCmd(COMMAND_MIXER_UNLOAD)
        if action == OnAction:
            print "=PopUp Mixer On"
            self.startThreadCmd(COMMAND_MIXER_ON)
        if action == OffAction:
            print "=PopUp Mixer Off"
            self.startThreadCmd(COMMAND_MIXER_OFF)
    def line1PopUp(self, position):
        menu = QMenu()
        OnAction = menu.addAction(u"Включить")
        OffAction = menu.addAction(u"Выключить")
        action = menu.exec_(self.LINE1GRUOP.mapToGlobal(position))
        if action == OnAction:
            print "=PopUp line1 On"
            self.startThreadCmd(COMMAND_LINE1_START)
        if action == OffAction:
            print "=PopUp line1 Off"
            self.startThreadCmd(COMMAND_LINE1_STOP)
    def line2PopUp(self, position):
        menu = QMenu()
        OnAction = menu.addAction(u"Включить")
        OffAction = menu.addAction(u"Выключить")
        action = menu.exec_(self.LINE2GRUOP.mapToGlobal(position))
        if action == OnAction:
            print "=PopUp line2 On"
            self.startThreadCmd(COMMAND_LINE2_START)

        if action == OffAction:
            print "=PopUp line2 Off"
            self.startThreadCmd(COMMAND_LINE2_STOP)
    def masloPopUp(self, position):
        menu = QMenu()
        LoadAction = menu.addAction(u"Загрузить")
        OffAction = menu.addAction(u"Выключить")
        action = menu.exec_(self.MASLOGRUOP.mapToGlobal(position))
        if action == LoadAction:
            print "=PopUp MASLO Load"
            mbclient.send(34, int(self.masloedit.text()))
            self.startThreadCmd(COMMAND_OIL_START_HAND)
        if action == OffAction:
            print "=PopUp MASLO Off"
            self.startThreadCmd(COMMAND_OIL_STOP)
    def ves3PopUp(self, position):
        menu = QMenu()
        LoadAction = menu.addAction(u"Загрузить")
        UnloadAction = menu.addAction(u"Выгрузить")
        action = menu.exec_(self.ves3.mapToGlobal(position))
        if action == LoadAction:
            print str(datetime.datetime.now())+"=PopUp VES3 Load"

            mbclient.send(28, int(self.dobavkaedit1.text()))
            mbclient.send(29, int(self.dobavkaedit2.text()))
            mbclient.send(30, int(self.dobavkaedit3.text()))
            mbclient.send(31, int(self.dobavkaedit4.text()))
            mbclient.send(32, int(self.dobavkaedit5.text()))
            mbclient.send(33, int(self.dobavkaedit6.text()))

            self.startThreadCmd(COMMAND_VES3_START)
        if action == UnloadAction:
            print str(datetime.datetime.now())+"=PopUp VES3 Unload"
            self.startThreadCmd(COMMAND_VES3_UNLOAD)
    def ves12PopUp(self, position):
        menu = QMenu()
        LoadAction = menu.addAction(u"Загрузить")
        UnloadAction = menu.addAction(u"Выгрузить")
        action = menu.exec_(self.VES12GRUOP.mapToGlobal(position))

        if action == LoadAction:
            print "=PopUp VES12 Load"
            mbclient.send(20, int(self.zernoedit3.text()))
            mbclient.send(21, int(self.zernoedit4.text()))
            mbclient.send(22, int(self.zernoedit5.text()))
            mbclient.send(23, int(self.zernoedit6.text()))
            mbclient.send(24, int(self.zernoedit7.text()))
            mbclient.send(25, int(self.zernoedit8.text()))
            mbclient.send(26, int(self.zernoedit9.text()))
            mbclient.send(27, int(self.zernoedit10.text()))
            self.startThreadCmd(COMMAND_VES12_START)

            # plcglobal.waitret()
            # plcglobal.send_cmd(COMMAND_VES12_START)
        if action == UnloadAction:
            print "=PopUp VES2 Unload"
            self.startThreadCmd(COMMAND_VES2_UNLOAD)
            # plcglobal.waitret()
            # plcglobal.send_cmd(COMMAND_VES2_UNLOAD)
    def zeroves1btnclk(self):
        self.startThreadCmd(COMMAND_ZERO_WEIGHT1)
    def zeroves2btnclk(self):
        self.startThreadCmd(COMMAND_ZERO_WEIGHT2)
    def zeroves3btnclk(self):
        self.startThreadCmd(COMMAND_ZERO_WEIGHT3)
    def getselectrow(self):
        # items= self.tableWidget.selectedItems()
        # print str(items[0].text())
        # selectrownum=self.tableWidget.selected
        pass
    def deleteallrow(self):
        plcglobal.nullqueue()
        # for i in range(0,self.currentrow+1):
        #     self.tableWidget.removeRow(0)
        self.currentrow = 0
        self.tableWidget.setRowCount(0)  # обнулить таблицу
        self.tableWidget.setRowCount(10)
        # indexes = table.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())
    def addqueuebtnclk(self):
        # self.tableWidget.Add ()
        plcglobal.addqueue()
        count = self.kormneedcount.text()
        plcglobal.recept.needcount = count
        # count=self.kormneedcount.Text()
        name = self.comboBoxRecept.currentText()
        if name != '' and (count != '0' and count != ''):
            newitem = QTableWidgetItem(name)
            self.tableWidget.setItem(self.currentrow, 0, newitem)
            newitem = QTableWidgetItem(count)
            self.tableWidget.setItem(self.currentrow, 1, newitem)
            self.currentrow += 1
            print self.currentrow
            if self.currentrow > 9:
                self.tableWidget.setRowCount(self.currentrow + 1)
    def comboboxchangedslot(self):
        self.loadrecept((str(self.comboBoxRecept.currentText()).encode('utf-8')))
    def loadrecept(self, name):
        namerecept = ''
        namerecept = name
        current_recept = {}
        current_recept = plcglobal.recept.receptlist.get(namerecept)
        print current_recept.items()
        print str(datetime.datetime.now())+"  Выбран рецепт " + current_recept.get('namekorm')

        self.zernoedit3.setText(current_recept.get('zerno3'))
        self.zernoedit4.setText(current_recept.get('zerno4'))
        self.zernoedit5.setText(current_recept.get('zerno5'))
        self.zernoedit6.setText(current_recept.get('zerno6'))
        self.zernoedit7.setText(current_recept.get('zerno7'))
        self.zernoedit8.setText(current_recept.get('zerno8'))
        self.zernoedit9.setText(current_recept.get('zerno9'))
        self.zernoedit10.setText(current_recept.get('zerno10'))
        self.dobavkaedit1.setText(current_recept.get('dobavka1'))
        self.dobavkaedit2.setText(current_recept.get('dobavka2'))
        self.dobavkaedit3.setText(current_recept.get('dobavka3'))
        self.dobavkaedit4.setText(current_recept.get('dobavka4'))
        self.dobavkaedit5.setText(current_recept.get('dobavka5'))
        self.dobavkaedit6.setText(current_recept.get('dobavka6'))
        self.masloedit.setText(current_recept.get('maslo'))
        somelistrecept = []
        somelistrecept = current_recept.get('selectkorm')
        print somelistrecept
        for i in range(0, 6):
            if str(i + 1) in (somelistrecept):
                self.interface_[i].switch(1)
            else:
                self.interface_[i].switch(0)

                # self.zernoedit3.setText
                # print self.plc.recept.receptlist.values()
    def reinitmbtcp(self):
        self.mbclient.checkconnect()
    def exitclk(self):
        for i in range(0, len(self.activethreads)):
            self.activethreads[i]._isRunning = False
        pass
        sys.exit()
    def calclk(self):
        dialogcal = Dialog_calibration()
        dialogcal.exec_()
    def dobavkabtnclk(self):
        dialogdobavka = Dialog_dobavka(self.dbclient, config)
        dialogdobavka.exec_()
    def zernobtnclk(self):
        dialogzerno = Dialog_zerno(self.dbclient)
        dialogzerno.exec_()
    def receptbtnclk(self):

        dialogrecept = Dialog_recept(self.dbclient)
        dialogrecept.exec_()
    def kormtbtnclk(self):
        dialogrecept = Dialog_korm(self.dbclient)
        dialogrecept.exec_()
    def stopbtnclk(self):
        self.startThreadCmd(COMMAND_STOP)
        self.workerzames._isRunning = False
        self.workerzames.session_begin= False
        plcglobal.recept.count=0
    def startbtnclk(self):
        # self.plc.recept.count = 1
        print str(datetime.datetime.now())+"START CLICK!"
        if plcglobal.countqueue>0:
        # self.workzamestimerslot(1000)
        # print "select silos for kombikorm" + str(self.plc.recept.selectkormnumbanka)
        # print self.plc.recept.count
        # plcglobal.send_cmd(41)    #Включение Нории
        # plcglobal.waitret()
        # plcglobal.send_cmd_val(101, plcglobal.recept.selectkormnumbanka[0])

        # plcglobal.send_cmd(101)  # Включение линии1
        # plcglobal.waitret()
        # plcglobal.send_cmd(201)  # Включение линии2
        # plcglobal.waitret()
        # plcglobal.send_cmd(41)  # Включение миксера
        # plcglobal.waitret()
        #
            self.startThreadWorkZames(QThread(self))
        else:
            print "<Список пуст>"
        # else:
        #     self.plc.recept.selectkormnumbanka = 0
        #     self.plc.recept.count = 0
        #     print "no select silos for kombikorm"
        # cell = self.tableWidget.item(0, 1).text()
    def pausebtnclk(self):
        mbclient.send(0, COMMAND_PAUSE)
    def vesivisuallevel1slot(self, vesi1, vesi2, vesi3):
        if vesi1 > 32768:
            vesi1 = vesi1 - 65535
        if vesi2 > 32768:
            vesi2 = vesi2 - 65535
        if vesi3 > 32768:
            vesi3 = vesi3 - 65535
        self.labelves1.setText(str(vesi1 / 10))
        self.labelves2.setText(str(vesi2 / 10))
        self.labelves3.setText(str(vesi3 / 10))

    def startThreadWeight(self,thread_):
        print  str(datetime.datetime.now()) + "Try start thread ThreadWeight"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        self.weight = ThreadWeight()
        self.weight.moveToThread(thread)
        self.weight.finished.connect(thread.quit)
        self.weight.finished.connect(self.weight.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.weight._isRunning = True
        thread.start()

    def startThreadVisual1Level(self, thread_, plc):
        print str(datetime.datetime.now())+"--Try start thread visual1level"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        # print type(self.activethreads[-1])
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
    def startThreadVizual2level(self, thread_):  # визулизация шиберов- по состоянию концевиков
        print  str(datetime.datetime.now())+"Try start thread visual2level"
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
    def startThreadGetPLC(self, thread_):
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
    def startThreadPullPLCList(self, thread_):
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
    def startThreadCmd(self, cmd):
        print str(datetime.datetime.now())+"--Try start thread ThreadCmd"
        thread_ = QThread(self)
        self.cmdthread = ThreadSendCmd(cmd)
        self.cmdthread.moveToThread(thread_)
        thread_.started.connect(self.cmdthread.process)
        self.cmdthread.finished.connect(thread_.quit)
        self.cmdthread.finished.connect(self.cmdthread.deleteLater)
        thread_.finished.connect(thread_.deleteLater)
        thread_.start()
    def startThreadWorkZames(self, thread_):
        print str(datetime.datetime.now())+"--Try start thread ThreadWorkZames"
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        # print type(self.activethreads[-1])
        self.workerzames = ThreadWorkZames(plcglobal, mbclient)
        self.workerzames.moveToThread(thread)
        self.workerzames.startcicle.connect(self.workzamesstartslot)
        self.workerzames.getrecept.connect(self.workzamesgetreceptslot)
        self.workerzames.endcicle.connect(self.workzamesendslot)
        self.workerzames.starttimer.connect(self.workzamestimerslot)
        self.workerzames.checklevelkorm.connect(self.workerzamescheckslot)
        self.workerzames.changenoria.connect(self.workerzameschangenoria)
 
        thread.started.connect(self.workerzames.process)
        self.workerzames.finished.connect(thread.quit)
        self.workerzames.finished.connect(self.workerzames.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.workerzames._isRunning = True
        thread.start()
    def workzamestimerslot(self, time_tick):
        print str(datetime.datetime.now())+"--start timer"
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerslot)
        self.timer.start(time_tick)
    def timerslot(self):
        print "Yo!"
        self.timer.stop()
        plcglobal.tick = True
    def visual1levelslot(self, index, bit):
        self.movies[index].switch(bit)
        if mbclient.okconnection == True:
            self.connectstatuslabel.setText(u"Соединение с ПЛК..Соединено")
            # if plcglobal.ret is not  0:
            #     self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК занят <" + str(plcglobal.ret)+u">")
            # if plcglobal.cmd is  0:
            #     self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК ждет команды на взвешивание <" + str(plcglobal.ret)+u">")
            # if plcglobal.cmd is  2:
            #     self.plcstatuslabel.setText(u"Cтатус ПЛК..ПЛК настроил приемку зерна <" + str(self.plc.ret)+u">")
        else:
            self.connectstatuslabel.setText(u"Соединение с ПЛК..Разорвано")
            # self.plcstatuslabel.setText(u"Статус ПЛК..Неизвестно")

        self.labelbanka3.setText(str(plcglobal.recept.listzernoneed.getelement(2)))
        self.labelbanka4.setText(str(plcglobal.recept.listzernoneed.getelement(3)))
        self.labelbanka5.setText(str(plcglobal.recept.listzernoneed.getelement(4)))
        self.labelbanka6.setText(str(plcglobal.recept.listzernoneed.getelement(5)))
        self.labelbanka7.setText(str(plcglobal.recept.listzernoneed.getelement(6)))
        self.labelbanka8.setText(str(plcglobal.recept.listzernoneed.getelement(7)))
        self.labelbanka9.setText(str(plcglobal.recept.listzernoneed.getelement(8)))
        self.labelbanka10.setText(str(plcglobal.recept.listzernoneed.getelement(9)))

        self.labelbanka11.setText(str(plcglobal.recept.listdobavkaneed.getelement(0)))
        self.labelbanka12.setText(str(plcglobal.recept.listdobavkaneed.getelement(1)))
        self.labelbanka13.setText(str(plcglobal.recept.listdobavkaneed.getelement(2)))
        self.labelbanka14.setText(str(plcglobal.recept.listdobavkaneed.getelement(3)))
        self.labelbanka15.setText(str(plcglobal.recept.listdobavkaneed.getelement(4)))
        self.labelbanka16.setText(str(plcglobal.recept.listdobavkaneed.getelement(5)))
        self.labelbanka17.setText(str(plcglobal.recept.masloneed))

        self.labelves2readyunload.setText("ves2readyunload " + str(getbit(plcglobal.status, VES2READYUNLOAD)))
        self.labelves2readyload.setText("ves2readyload " + str(getbit(plcglobal.status, VES2READYLOAD)))
        self.labelves3readyunload.setText("ves3readyunload " + str(getbit(plcglobal.status, VES3READYUNLOAD)))
        self.labelves3readyload.setText("ves3readyload " + str(getbit(plcglobal.status, VES3READYLOAD)))
        self.labelmixerreadyload.setText("mixerreadyload " + str(getbit(plcglobal.status, MIXERREADYLOAD)))
        self.labelmixerreadyunload.setText("mixerreadyunload " + str(getbit(plcglobal.status, MIXERREADYUNLOAD)))
        self.labelnoriaready.setText("noriaready " + str(getbit(plcglobal.status, NORIAREADYLOAD)))
        self.labelmasloready.setText("masloready " + str(getbit(plcglobal.status, MASLOREADY)))
        self.labelline2readyload.setText("line2readyload " + str(getbit(plcglobal.status, LINE2READYLOAD)))


        # if self.plc.state is 0 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ожидание команды")
        # if self.plc.state is 1 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Закончил загрузку весов")
        # if self.plc.state is 2 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ошибка")
    def visual2levelslot(self):  # визулизация шиберов- по состоянию концевиков
        def shiber_switch(obj1, obj2, obj3):

            if obj2.state is True and obj3.state is False:  # если включен концевик "открыто"
                obj1.switch(1)  # открыть шибер
            if obj2.state is False and obj3.state is True:  # если включен концевик "закрыто"
                obj1.switch(0)  # закрыть шибер
            if obj2.state is False and obj3.state is False: #если оба концевика выключены
                obj1.switch(1)  # открыть шибер
                pass
            if obj2.state is True and obj3.state is True:
                pass

        shiber_switch(self.moviesL2[0], self.movies[48], self.movies[49])
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
        # shiber_switch(self.movies[40], self.movies[41], self.movies[42])
        shiber_switch(self.moviesL2[13], self.movies[41], self.movies[42])
        # pass

        # self.movies.insert(80, objs(obj(self.silos1shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(81, objs(obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(82, objs(obj(self.silos2shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(83, objs(obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(84, objs(obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(85, objs(obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(86, objs(obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", "")))
        # self.movies.insert(87, objs(obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", "")))
    def workerzameschangenoria(self,num):
        self.startThreadCmd(COMMAND_NORIA_INIT + (num << 8))
    def workzamesstartslot(self):
        print('start! slot from threadPLCZames signal_  startcicle emit ')
        # self.plc.recept.selectkormnumbanka=2

        # print "select kormsilos = "+str(self.plc.recept.selectkormnumbanka)

        # self.plc.recept.selectkormnumbanka=2
        list = range(15)

        list.insert(0, int(self.zernoedit3.text()))
        list.insert(1, int(self.zernoedit4.text()))
        list.insert(2, int(self.zernoedit5.text()))
        list.insert(3, int(self.zernoedit6.text()))
        list.insert(4, int(self.zernoedit7.text()))
        list.insert(5, int(self.zernoedit8.text()))
        list.insert(6, int(self.zernoedit9.text()))
        list.insert(7, int(self.zernoedit10.text()))
        list.insert(8, int(self.dobavkaedit1.text()))
        list.insert(9, int(self.dobavkaedit2.text()))
        list.insert(10, int(self.dobavkaedit3.text()))
        list.insert(11, int(self.dobavkaedit4.text()))
        list.insert(12, int(self.dobavkaedit5.text()))
        list.insert(13, int(self.dobavkaedit6.text()))
        list.insert(14, int(self.masloedit.text()))
        # print list[12]
        plcglobal.recept.zakaz.pull(list)
        # print plcglobal.recept.zakaz.getelement(12)
        plcglobal.recept.selectkormnumbanka = []
        for i in range(0, 6):
            if self.interface_[i].state is True:  # выделенную банку
                plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма

        plcglobal.recept.getzakazcomplete = True

        # mbclient.send(20, int(self.zernoedit3.text()))
        # mbclient.send(21, int(self.zernoedit4.text()))
        # mbclient.send(22, int(self.zernoedit5.text()))
        # mbclient.send(23, int(self.zernoedit6.text()))
        # mbclient.send(24, int(self.zernoedit7.text()))
        # mbclient.send(25, int(self.zernoedit8.text()))
        # mbclient.send(26, int(self.zernoedit9.text()))
        # mbclient.send(27, int(self.zernoedit10.text()))
        # mbclient.send(28, int(self.dobavkaedit1.text()))
        # mbclient.send(29, int(self.dobavkaedit2.text()))
        # mbclient.send(30, int(self.dobavkaedit3.text()))
        # mbclient.send(31, int(self.dobavkaedit4.text()))
        # mbclient.send(32, int(self.dobavkaedit5.text()))
        # mbclient.send(33, int(self.dobavkaedit6.text()))
        # mbclient.send(34, int(self.masloedit.text()))
        # self.mbclient.send()
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
        # print('end! slot from threadPLCZames signal_')
    def workzamesendslot(self):
        print str(datetime.datetime.now())+("--Endcicle  emited")
        self.tableWidget.removeRow(0)
        plcglobal.decqueue()
        plcglobal.recept.endciclecomplete=True
        print str(datetime.datetime.now())+"--count queue = "+str(plcglobal.countqueue)
        if plcglobal.countqueue==0:
            self.deleteallrow()
    def workzamesgetreceptslot(self):
        self.loadrecept(str(self.tableWidget.item(0, 0).text()))
        plcglobal.recept.count = int(self.tableWidget.item(0, 1).text())
        plcglobal.recept.selectkormnumbanka = []
        for i in range(0, 6):
            if self.interface_[i].state is True:  # выделенную банку
                plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
    def workerzamescheckslot(self):
        print str(datetime.datetime.now()) + "--Проверка заполнености силоса готового комбикорма, силос №"+str(plcglobal.recept.selectkormnumbanka[0])
        if self.movies[plcglobal.kormbankauplevel[plcglobal.recept.selectkormnumbanka[0]]].state == True:
            plcglobal.recept.count=0
            print str(datetime.datetime.now()) + "--Выбранный силос заполнен, окончание изготовдления текущего корма!"
            logging.info(str(datetime.datetime.now()) + "--Выбранный силос заполнен, окончание изготовления текущего корма")
        else:
            print str(datetime.datetime.now())+ "--Выбранный силос не заполнен"

        newitem = QTableWidgetItem(str(int(plcglobal.recept.needcount)-plcglobal.recept.count)+u" из "+plcglobal.recept.needcount) # осталось замесов
        self.tableWidget.setItem(0, 1, newitem)
# print plcglobal.recept.receptlist.keys()
# print plcglobal.recept.receptlist.values()
logging.info('========================S T A R T===================================')

config = CONFIG()
db = DB(config.ipaddrdb, "root", "root", config.namedb)
DEBUGFLAG = True

if config.ERROR_READ_INI is False:
    # self.db = MySQLdb.coect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
    if DEBUGFLAG is False:
        # mbclient=mbclient(config.ipaddrplc,config.portplc)
        logging.info('Create modbus client object')
        mbclient = mbclient('10.0.6.10', '502')
        plcglobal = PLC(mbclient)

    else:
        mbclient = False
        plcglobal = PLC(mbclient)


def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MyApp(db)
    form.show()
    app.exec_()  # and execute the app


if __name__ == "__main__":
    main()
