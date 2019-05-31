# -*- coding: utf-8 -*-
# coding: utf-8
import sys
import traceback
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
import time
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
from const_ import *
from database_ import DB
logging.basicConfig(format=u'%(name)s %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'cormoceh.log')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.getLogger('PyQt4.uic').setLevel(logging. CRITICAL + 10)
qtCreatorFile = "designcormoceh.ui"  # main window design ui
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

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
                               'zerno10': int(self.ui.zernoedit10.text()),
                               'dobavka1': int(self.ui.dobavkaedit1.text()),
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
           write( u"--Не выбрана банка для изготовленного комбикорма или не введено имя для комбикорма")

    def clearallbtnclk(self):
        pass
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
            print str(zerno_[i][0]) + " " + zerno_[i][1]  # zerno[i][0] - nRec zerno[i][1] - Name

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
        self.combolist.insert(10, self.ui.comboBox_10)
        for i in range(1, 11):
            self.labellist[i].setText(zerno_[i][1])
        for row in dbclient.get_zerno():
            for i in range(1, 11):
                self.combolist[i].addItem(row[1])
        self.connect(self.combolist[1], QtCore.SIGNAL("currentIndexChanged(const  QString&)"),
                     lambda: self.comboslot(1))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[2], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(2))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[3], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(3))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[4], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(4))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[5], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(5))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[6], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(6))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[7], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(7))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[8], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(8))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[9], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(9))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[10], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(10))  # lambda who=i: self.comboslot(who)

    def comboslot(self, i):
        print "Силос <ЗЕРНО>  №" + str(i)
        self.labellist[i].setText(self.combolist[i].currentText())

    def btnapplyclk(self):
        print "Сохранение изменений!"
        # print unicode(self.ui.labelbanka1.text())
        for i in range(1, 11):
            nameprod = unicode(self.labellist[i].text())
            prod = self.dbclient.get_id_product(nameprod.encode('utf8'))
            self.dbclient.save_product(i, prod)
class Dialog_dobavka(QDialog, Ui_Dialog_Dobavka):
    def __init__(self, dbclient, conf):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Dobavka()
        self.ui.setupUi(self)
        dobavka = range(12)
        self.dbclient = dbclient
        self.ui.savebankabtn.clicked.connect(self.btnapplyclk)

        for i in range(1, 7):
            dobavka[i] = self.dbclient.get_product(i + 10)
            print str(dobavka[i][0]) + " " + dobavka[i][1]  # dobavka[0] - nRec dobavka[1] - Name

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

        self.combolist = range(10)
        self.combolist.insert(1, self.ui.comboBox_1)
        self.combolist.insert(2, self.ui.comboBox_2)
        self.combolist.insert(3, self.ui.comboBox_3)
        self.combolist.insert(4, self.ui.comboBox_4)
        self.combolist.insert(5, self.ui.comboBox_5)
        self.combolist.insert(6, self.ui.comboBox_6)

        for i in range(1, 7):
            self.labellist[i].setText(dobavka[i][1])
        for row in dbclient.get_dobavka():
            for i in range(1, 7):
                self.combolist[i].addItem(row[1])
        self.connect(self.combolist[1], QtCore.SIGNAL("currentIndexChanged(const  QString&)"),
                     lambda: self.comboslot(1))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[2], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(2))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[3], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(3))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[4], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(4))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[5], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(5))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[6], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(6))  # lambda who=i: self.comboslot(who)

    def comboslot(self, i):
        print "Силос <ЗЕРНО>  №" + str(i)
        self.labellist[i].setText(self.combolist[i].currentText())

    def btnapplyclk(self):
        print "Сохранение изменений!"
        # print unicode(self.ui.labelbanka1.text())
        for i in range(1, 7):
            nameprod = unicode(self.labellist[i].text())
            prod = self.dbclient.get_id_product(nameprod.encode('utf8'))
            self.dbclient.save_product(i + 10, prod)
class Dialog_korm(QDialog, Ui_Dialog_Korm):
    def __init__(self, dbclient):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Korm()
        self.ui.setupUi(self)
        korm = range(12)
        self.dbclient = dbclient
        self.ui.savebankabtn.clicked.connect(self.btnapplyclk)

        for i in range(1, 7):
            korm[i] = self.dbclient.get_product(i + 20)
            print str(korm[i][0]) + " " + korm[i][1]  # dobavka[0] - nRec dobavka[1] - Name

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

        self.combolist = range(10)
        self.combolist.insert(1, self.ui.comboBox_1)
        self.combolist.insert(2, self.ui.comboBox_2)
        self.combolist.insert(3, self.ui.comboBox_3)
        self.combolist.insert(4, self.ui.comboBox_4)
        self.combolist.insert(5, self.ui.comboBox_5)
        self.combolist.insert(6, self.ui.comboBox_6)

        for i in range(1, 7):
            self.labellist[i].setText(korm[i][1])
        for row in dbclient.get_korm():
            for i in range(1, 7):
                self.combolist[i].addItem(row[1])
        self.connect(self.combolist[1], QtCore.SIGNAL("currentIndexChanged(const  QString&)"),
                     lambda: self.comboslot(1))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[2], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(2))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[3], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(3))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[4], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(4))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[5], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(5))  # lambda who=i: self.comboslot(who)
        self.connect(self.combolist[6], QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.comboslot(6))  # lambda who=i: self.comboslot(who)

    def comboslot(self, i):
        print u"Силос <Корм>  №" + str(i)
        self.labellist[i].setText(self.combolist[i].currentText())

    def btnapplyclk(self):
        print u"Сохранение изменений!"
        # print unicode(self.ui.labelbanka1.text())
        for i in range(1, 7):
            nameprod = unicode(self.labellist[i].text())
            prod = self.dbclient.get_id_product(nameprod.encode('utf8'))
            self.dbclient.save_product(i + 20, prod)
class Dialog_calibration(QDialog, ):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_Dialog_Cal()
        self.ui.setupUi(self)

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
    print u"Загрузка рецепта из recepts.ini"
    logging.debug(u"Загрузка рецепта из recepts.ini")

    parser_ = ConfigParser()
    parser_.read(".\\recepts.ini")
    receptlist_ = {}
    for section in parser_.sections():
        receptlist_[section] = {}
        for option in parser_.options(section):
            receptlist_[section][option] = parser_.get(section, option)
    return receptlist_
def takeover(object):
    object.busy = True
def free(object):
    object.busy = False
def wait(object):
    while (object.busy is True):
        # delay(10)
        # time.sleep(0.01)
        pass
def delay(tick):
    for i in range(0, tick):
        pass
def getbit(reg16, indexbit):
    if reg16 & (1 << indexbit) is not 0:
        return 1
    else:
        return 0
def writedebug(str_input):
    try:
        str_=unicode(str_input)
        print str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + u": " + str_
        logging.debug(str_)
    except Exception as err:
        print  str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+u"Ошибка в writedebug() -"+str(err)
        logging.error(traceback.format_exc())
def write(str_input):
    str_ = unicode(str_input)
    print str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + u": " + str_
    plcglobal.textout.append(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + u": " + str_)
    logging.debug(str_)
    try:
        # print str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+u": "+str_
        # plcglobal.textout.append(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+u": "+str_)
        # logging.debug(str_)
        pass
    except Exception as err:
        print  str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+u"Ошибка в write() -"+str(err)
        logging.error(traceback.format_exc())
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
        self.client.timeout = 2000
        self.busy = False
        self.okconnection = False
        # self.connect()
        self.disconnected = False
    def checkconnecttcp(self):
        if not self.client.is_open():
            logging.debug(' Connection status: ' + str(self.okconnection))
            logging.warning('!!!!!!!!!!!! No connection !!!!!!!!!!!!!!!')
            # logging.debug(self.client.mysocket)
            write(u'!!!!!!!!!!!! No connection !!!!!!!!!!!!!!!')
            self.disconnected = True
            self.connect()
        else:
            # print "Ok connection"
            if self.disconnected == True:
                self.disconnected = False
                write(u"Connection return")
            else:
                pass

    def connect(self):
        self.okconnection = False
        self.client = ModbusClient()
        self.client.host(self.plcaddr)
        self.client.port(self.port)
        self.client.timeout = 2000
        while not self.okconnection == True:
            try:
                self.client.close()
                self.okconnection = self.client.open()
                # self.client.auto_open()
                # wait(self)
            except Exception as err:
                writedebug(u"--Ошибка подключения "+ str(err))
                logging.error(traceback.format_exc())
        return self.okconnection

    def disconnect(self):
        return self.client.close()

    def send(self, rgadr, val):
        if DEBUGFLAG==False:
            self.checkconnecttcp()
            is_Ok=None

            while(plcglobal.pausesend==True):
                pass
            plcglobal.pauseread = True
            while(is_Ok!=True):
                try:
                    wait(self)
                    takeover(self)
                    is_Ok=self.client.write_single_register(rgadr, val)
                except Exception as err:
                    writedebug(u"--Ошибка записи регистра с номером : " + str(rgadr) + u" Ошибка:"+str(err))
                    logging.error(traceback.format_exc())
                finally:
                    free(self)
                    plcglobal.pauseread = False
            return is_Ok
    def read(self, rgadr):
        if DEBUGFLAG==False:

            self.checkconnecttcp()
            wait(self)
            takeover(self)
            result = 0
            # read_holding_registers(reg_addr, reg_nb=1)
            # result= self.client.read_holding_registers(rgadr,1,unit=1)
            try:
                result = self.client.read_holding_registers(rgadr, 1)
            except Exception as err:
                writedebug(u"--Ошибка чтения регистра " + str(err))
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

            writedebug(self.client.last_error() + u"Error read coil with number " + str(bit))
            logging.error(traceback.format_exc())
            # free(self)
            # return False
        finally:
            free(self)
            if isinstance(incoil, list):
                return incoil[0]
            else:
                return 0
        # return incoil[0]

    def getbyteL(self, word):
        HH = 0b00001111
        return word & HH

    def getbyteH(self, word):
        LL = 0b11110000
        return word & LL
class plclist(object):
    def __init__(self,count):

        self.busy = False
        self.init = False
        self.list = range(count)
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
    def add(self,elem):
        self.list.append(elem)
    def sub(self,elem):
        try:
            if elem in self.list:
                self.list.remove(elem)
        except Exception as err:
            writedebug( u"Error deleting element from plclist "+str(err))
            logging.error(traceback.format_exc())
    def has(self,elem):
        if elem in self.list:
            return True
        else:
            return False

class shnek(object):
    def __init__(self,getweight,regerror, min,timeout):

        self.statelast = 0
        self.statenow = 0
        self.timeout = timeout # максимальная работа шнека без увеличения веса
        self.weightbegin = 0
        self.weightend = 0
        # self.weightlast = 0
        # self.weightnow = 0
        self.getweight = getweight # функция получения текущего веса
        self.error = False
        self.regerror = regerror # функция регистрации и обработки ошибки
        # self.errortext = u"Too long work"
        self.timer = 0
        self.weights = []
        self.minimum = min # минимальный шаг весов в кг
        self.endwork = False
        self.started = False
        self.appends = 0
        self.max_appends = 5
    def chkstate(self):
        if self.statenow == 0:
            self.endwork = False
            self.started = False
            self.error = False

        if self.statelast != self.statenow:
            if self.statelast == 0:
                self.started = True
                self.endwork = False
                self.error = False
                self.weights[:]=[]

                self.weightbegin=self.getweight()
                self.weights.append(self.weightbegin)
                self.statelast = self.statenow
            else:
                self.weightend=self.getweight()
                self.statelast=self.statenow
                self.endwork = True
                self.started = False
                self.error = False
        else:
            if self.statelast == 1:
                self.started = False
                try:
                    if self.timer < self.timeout:
                        self.timer = self.timer + 1
                    else:
                        self.weights.append(self.getweight)
                        if len(self.weights) > 2:
                            try:
                                if (self.weights[-1]-self.weights[-2]) < self.minimum:
                                    write(u"Ошибка шнека, малая разница веса " + str(self.weights[-1] - self.weights[-2]))
                                    self.regerror(ERRORSHNEK)
                                    self.error = True
                                    write(u"Слишком долго крутит шнек")
                                else:
                                    self.timer = 0
                                    self.weights[:]=[]
                            except Exception as err:
                                writedebug(u"Error in slass shnek method chkstate: self.weights[-1]-self.weights[-2]")
                        else:
                            self.timer = 0
                    # if len(self.weights)>2:
                    #     if self.weights[-1]-self.weights[-2]< self.minimum:
                    #         self.weights.append(self.getweight())
                    #         if self.timer<self.timeout:
                    #             self.timer= self.timer+1
                    #         else:
                    #             weights1 = sorted(self.weights,key=int)
                    #             maximum_ = weights1[-1]
                    #             weights2 = sorted(weight for weight in self.weights if weight >= (maximum_-self.minimum)) # сортировка по возрастанию, с отбрас значений меньше миним
                    #             if ((weights2[-1] - weights2[0])<self.minimum):
                    #                 write(u"Ошибка шнека, малая разница веса "+ str(weights2[-1] - weights2[0]))
                    #                 self.regerror(ERRORSHNEK)
                    #                 self.error = True
                    #                 write(u"Слишком долго крутит шнек")
                    #             else:
                    #                 pass
                    #     else:
                    #         pass
                    # else:
                    #     self.weights.append(self.getweight())
                except Exception as err:
                    writedebug(u"Error in class 'shnek' method 'chkstate'" + str(err))
                    logging.error(traceback.format_exc())
    def setstate(self,newbit):
        self.statenow = newbit
class processinfo(object):
    def __init__(self):
        self.countnow = 0
        self.receptnow =''
        self.receptprev = ''
        self.countves2 = 0
        self.countves3 = 0
        self.countoil = 0
        self.countline1 = 0
        self.countline2 = 0
        self.countmixer = 0
        self.countlinek = 0
class plcrecept(object):
    def __init__(self):
        self.count = 0
        self.needcount  = 0
        self.selectkormnumbanka = range(1)
        self.nowkormnumbanka = 0
        self.masloneed = 0
        self.dopdobavka = 0
        self.step = 0
        self.zakaz = plclist(10)
        self.listzernoneed = plclist(10)
        self.listdobavkaneed = plclist(6)
        self.receptlist = {}
        self.receptlist = loadrecepts()
        self.stages = plclist(1)
        self.controlcmd = plclist(1)
        self.two_stage = False
        self.indexmuchdobavka = 0
        self.getzakazcomplete = False  # Для процедуры заполнения массива zakaz, для предотвращения рассинхрона
        self.endciclecomplete= False
        self.getstartslotcomplete=False
        self.stagenameves12 = u""
        self.stagenameves3 = u""
        self.stagenameoil = u""
        self.stagenameline12 = u""
        self.stagenamemixer = u""
        self.stagenamelinek = u""
        self.receptname=''
        self.procinfo = processinfo()
        self.stagenow = 1
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
        logging.debug(u"Декремент счетчика замесов count =" + str(self.count))
    def nullcount(self):
        self.count = 0
        logging.debug(u"Обнуление счетчика замесов count = " + str(self.count))
    def setcount(self,count):
        self.count = count
        logging.debug(u"Установка значения счетчика замесов count = " + str(self.count))
    def selectbankaisneed(self):

        if self.nowkormnumbanka==self.selectkormnumbanka[0]:
            return True
        else:
            return False

class commands(object):
    def __init__(self, cmd, name, flag,needchk):
        self.timeout = 0
        self.times = 0
        self.cmd = cmd
        self.flag = flag # index bit in dbstatus register
        self.name = name
        self.run = False
        self.exe_err = False
        self.controlexec = needchk
        self.attempts = 0
        self.MAXATTEMPTS = 3
        self.is_done = False

    def execute(self,timeout):
        if not plcglobal.recept.stages.has(self.name):
            self.register()
        # if self.name not in plcglobal.command_list:
            self.timeout = timeout #timeout
            self.run = True
            self.is_done = False
            self.attempts = 0
            self.times = 0
            plcglobal.send_cmd(self.cmd)
            # write(u"Отправлена команда: " + self.name)
        else:
            writedebug(u"Отменена избыточная отправка команды" + self.name)

    def checkexecute(self):
        if self.run == True:
            if getbit(plcglobal.status,self.flag)==0:
                self.is_done = True
                self.run = False
                self.attempts = 0
                self.times = 0
                writedebug(u"ПЛК успешно получил команду: " + self.name)
                return True
            else:
                if self.times < self.timeout:
                    self.times = self.times + 1
                else:
                    if self.attempts < self.MAXATTEMPTS:
                        self.attempts = self.attempts + 1
                        self.times = 0
                        plcglobal.send_cmd(self.cmd)
                        writedebug(u"Повторно отправлена команда("+str(self.attempts)+u"):" + self.name)
                    else:
                        self.exe_err = True
                        plcglobal.pulerrors.append(plcglobal.errors[ERROREXECUTECMD])
                        self.run = False  # останавливаем попытки отправить команду
                        write(u"ПЛК не получил команду: " + self.name + u"- рекомендуется перезапуск программы и ручное замешивание")
        else:
            pass
    def register(self):
        if not self.is_registered():
            write(u"Зарегестрирована отправка команды: "+self.name)
            plcglobal.recept.stages.add(self.name)  # зарегестрировать что началась отправка команды
    def unreg(self):
        write(u"Удаление из списка выполненных команд: "+ self.name)
        plcglobal.recept.stages.sub(self.name)
        self.is_done = False

    def is_registered(self):
        if plcglobal.recept.stages.has(self.name):
            return True
        else:
            return False
def getweight1():
    plcglobal.weight1 = plcglobal.listplcrg16.getelement(VES1INDEX)
    if plcglobal.weight1>65000:
        return plcglobal.weight1-65535
    else:
        return plcglobal.weight1
def getweight2():
    plcglobal.weight2 = plcglobal.listplcrg16.getelement(VES2INDEX)
    if plcglobal.weight2>65000:
        return plcglobal.weight2-65535
    else:
        return plcglobal.weight2
def getweight3():
    plcglobal.weight3 = plcglobal.listplcrg16.getelement(VES3INDEX)
    if plcglobal.weight3>65000:
        return plcglobal.weight3-65535
    else:
        return plcglobal.weight3
def regerror(errorid):
    plcglobal.pulerrors.append(errorid)
class PLC(object):
    def __init__(self, mbclient):
        self.cmd = 0  # регистр команд
        self.ret = 0  # регистр return ответа ПЛК
        self.mbclient = mbclient
        self.listplccoils = plclist(112)
        self.listplcrg16 = plclist(LASTREGADDR)
        self.recept = plcrecept()
        self.countqueue = 0
        self.steptext = ''
        self.needstate = 1
        self.status = 0
        self.tick = False
        self.kormbankauplevel=[88,90,92,94,96,98]
        self.chastotaves1=0
        self.chastotaves2=0

        self.shibers = range(4)
        self.newerror = 0
        self.lasterror = 0
        self.weight1 = 0
        self.weight2 = 0
        self.weight3 = 0
        self.pauseread = False
        self.pausesend = False
        self.needcountlist = []
        self.receptnamelist = []
        self.pulerrors = []
        self.errors = {ERRORWEIGHT1: u"Error weight1", ERRORWEIGHT2: u"Error weight2",ERRORWEIGHT3:u"Error weight3",ERRORLINEK:u"Error LINEK" ,ERRORPERKLAPAN:u"Error PerKlapan", ERRORMIXER:u"Error Mixer",ERRORLINE1:u"Error Line1",ERRORLINE2:u"Error Line2", ERRORAWILA:"Error Awila",
                       ERRORMIXERNOTOPEN: u"Error mixer not open", ERRORMIXERNOTUNLOAD:u"Error mixer not unload", ERROREXECUTECMD:u"Command not execute" ,ERRORSHNEK: u"Error shnek" }
        self.errordetails = {ERRORWEIGHT1: u"Слишком большое значение в заказе весы1", ERRORWEIGHT2: u"Слишком большое значение в заказе весы2",ERRORWEIGHT3:u"Слишком большое значение в заказе весы3",
                             ERRORLINEK:u"получена ошибка от ПЛК управляющего норией, возможно сбой связи, проверьте соединение и удостоверьтесь, что плк Нории переведен в Режим АВТО" ,ERRORPERKLAPAN:u"Слишком долго переключается перекидной клапан(больше минуты)",
                             ERRORMIXER:u"Возмозможно выключено тепловое реле",ERRORLINE1:u"Возмозможно выключено тепловое реле двигателя ",ERRORLINE2:u"Возмозможно выключено тепловое реле двигателя",
                             ERRORAWILA :u" Ошибка шкафа управления Awila, возможны проблемы с частотниками, также возможы проблемы с автом выключателями", ERRORMIXERNOTOPEN:u"Смеситель не будет ывгружаться, пока бункер под смесителем не опустошится",
                             ERRORMIXERNOTUNLOAD:u"Смечитель не выгружался, необходимо выгрузить смеситель перед разгрузкой весов",  ERROREXECUTECMD:u"Команда не исполнена", ERRORSHNEK: u"Слишком долго работает шнек" }
        self.command_list = []
        # comms =[]
        # comms.append(commands(COMMAND_VES12_START,u"COMMAND_VES12_START",VES2READYLOAD,True))
        # comms.append(commands(COMMAND_VES3_START, u"COMMAND_VES3_START", VES3READYLOAD, True))
        # comms.append(commands(COMMAND_VES2_UNLOAD, u"COMMAND_VES2_UNLOAD", VES2READYUNLOAD, True))
        # comms.append(commands(COMMAND_VES3_UNLOAD, u"COMMAND_VES3_UNLOAD", VES3READYUNLOAD, True))
        # comms.append(commands(COMMAND_MIXER_UNLOAD, u"COMMAND_MIXER_UNLOAD", MIXERREADYUNLOAD, True))
        # comms.append(commands(COMMAND_OIL_START, u"COMMAND_OIL_START", MASLOREADY, False))
        #
        # self.commands = {COMMAND_VES12_START:comms[0],COMMAND_VES3_START:comms[1],COMMAND_VES2_UNLOAD:comms[2],COMMAND_VES3_UNLOAD:comms[3],COMMAND_MIXER_UNLOAD:comms[4], COMMAND_OIL_START:comms[5]}

        self.commands = {COMMAND_VES12_START: commands(COMMAND_VES12_START,u"COMMAND_VES12_START",VES2READYLOAD,True), COMMAND_VES3_START: commands(COMMAND_VES3_START, u"COMMAND_VES3_START", VES3READYLOAD, True),
                         COMMAND_VES2_UNLOAD: commands(COMMAND_VES2_UNLOAD, u"COMMAND_VES2_UNLOAD", VES2READYUNLOAD, True),COMMAND_VES3_UNLOAD: commands(COMMAND_VES3_UNLOAD, u"COMMAND_VES3_UNLOAD", VES3READYUNLOAD, True),
                         COMMAND_MIXER_UNLOAD: commands(COMMAND_MIXER_UNLOAD, u"COMMAND_MIXER_UNLOAD", MIXERREADYUNLOAD, True), COMMAND_OIL_START:commands(COMMAND_OIL_START, u"COMMAND_OIL_START", MASLOREADY, False),
                         COMMAND_NORIA_INIT: commands(COMMAND_NORIA_INIT+(self.recept.selectkormnumbanka[0] << 8), u"COMMAND_NORIA_INIT", NORIAREADYLOAD, False)}

        self.textout = []
        self.readytostart = True
        self.timerenable = False
        self.timer = 0 #seconds
        self.pause = False
        self.shnekszerno = {ISHNEK1:shnek(getweight1,regerror,50,60),ISHNEK2:shnek(getweight1,regerror,50,60),
                            ISHNEK3:shnek(getweight1,regerror,50,60),ISHNEK4:shnek(getweight1,regerror,50,60),
                            ISHNEK5:shnek(getweight2,regerror,50,60),ISHNEK6:shnek(getweight2,regerror,50,60),
                            ISHNEK7:shnek(getweight2,regerror,50,60),ISHNEK8:shnek(getweight2,regerror,50,60),
                            ISHNEK9:shnek(getweight2,regerror,50,60),ISHNEK10:shnek(getweight2,regerror,50,60)}
        self.shneksdobavka = {IFLEX1:shnek(getweight3,regerror,5,90),IFLEX2:shnek(getweight3,regerror,1,90),
                              IFLEX3: shnek(getweight3, regerror, 1,90), IFLEX4: shnek(getweight3, regerror, 1,90),
                              IFLEX5: shnek(getweight3, regerror, 1,90), IFLEX6: shnek(getweight3, regerror, 1,90)}

        # ISHNEK1 = 56
        # ISHNEK2 = 57
        # ISHNEK3 = 58
        # ISHNEK4 = 59
        # ISHNEK5 = 60
        # ISHNEK6 = 61
        # ISHNEK7 = 62
        # ISHNEK8 = 63
        # ISHNEK9 = 64
        # ISHNEK10 = 65

    def getnumbanka(self,idshnek):
        if idshnek in self.shnekszerno:
            return idshnek - 55
        if idshnek in self.shneksdobavka:
            return idshnek - 13
    def ticktimerrecept(self):
        if self.timerenable == True:
            self.timer=self.timer+1
        return self.timer
    def starttimerecept(self):
        # plcglobal.recept.stages.sub("STOPTIMERECEPT")
        writedebug(u"Включение таймера замеса")
        self.timer = 0
        self.timerenable = True
    def stoptimerrecept(self):
        writedebug(u"Таймер замеса остановлен")
        self.timerenable = False
    def send_cmd(self, cmd):
        if DEBUGFLAG==False:
            self.waitret()
            # self.send_ret(0)
            # wreg = self.listplcrg16.getelement(0)
            wreg = mbclient.read(0)
            breg = wreg & 0xFF00
            if DEBUGFLAG == False:
                mbclient.send(0, cmd | breg)


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
        writedebug(u"Ожидание готовности ПЛК к получению команды")
        while (True):
            # answer = mbclient.read(0) & 0x00FF
            # delay(10000)
            answer = plcglobal.cmd & 0x00FF
            time.sleep(0.01)
            if answer == 0:
                writedebug(u"ПЛК готов")
                break

    def addqueue(self,count,name):
        self.countqueue += 1
        self.needcountlist.append(count)
        self.receptnamelist.append(name)
    def decqueue(self):
        self.countqueue -= 1

    def nullqueue(self):
        self.countqueue = 0
        del self.needcountlist[:]
        del self.receptnamelist[:]

class ThreadGetPLC(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)

    def process(self):
        writedebug(u"--+thread ThreadGetPLC started")
        while self._isRunning is True:
            # mbclient.checkconnecttcp()
            listrg16local_ = range(LASTREGADDR + 1)

            time.sleep(0.6)
            if plcglobal.pauseread != True:
                plcglobal.pausesend = True
                plcglobal.cmd = mbclient.read(REG_CMD)
                plcglobal.status = mbclient.read(REG_STATUS)
                for i in range(0, LASTREGADDR + 1):
                    # delay(1000)
                    time.sleep(0.005)
                    try:
                        listrg16local_.insert(i, mbclient.read(i))
                    except Exception as err:
                        writedebug(u"--Error in ThreadGetPLC "+str(err))
                        logging.error(traceback.format_exc())

                plcglobal.pausesend = False
                plcglobal.listplcrg16.pull(listrg16local_)
        writedebug(u"---thread ThreadGetPLC done")

    def stop(self):
        self._isRunning = False

class ThreadPullPLCList(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self):
        QtCore.QObject.__init__(self)

    def process(self):
        writedebug(u"--+thread ThreadPullPLCList started")
        while self._isRunning is True:
            time.sleep(0.7)
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
                    listcoillocal_.insert(i * 16 + j, getbit(plcglobal.listplcrg16.getelement(i + OFFSETflagstate), j))
            plcglobal.listplccoils.pull(listcoillocal_)

            # plcglobal.get_state()
            # for i in range(0,10):
            #     plcglobal.shnekszerno[i]=plcglobal.listplccoils.list[i+56]
            # for i in range(0,6):
            #     plcglobal.shneksdobavka[i]=plcglobal.listplccoils.list[i+24]
            for i in range(ISHNEK1,ISHNEK10+1): # получение состояния шнеков
                plcglobal.shnekszerno[i].setstate(plcglobal.listplccoils.getelement(i))
            for i in range(IFLEX1,IFLEX6+1): # получение состояния флексов
                plcglobal.shneksdobavka[i].setstate(plcglobal.listplccoils.getelement(i))

        writedebug(u"---thread ThreadPullPLCList done")
        self.finished.emit()

        def stop(self):
            self._isRunning = False

class ThreadVisual1Level(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    vesisignal = QtCore.pyqtSignal(int, int, int, int)
    s1 = QtCore.pyqtSignal(int, int)
    _isRunning = False

    @QtCore.pyqtSlot()
    def __init__(self, plc):
        QtCore.QObject.__init__(self)
        self.plc = plc

    def process(self):
        writedebug(u"--+thread ThreadVisual1Level started")
        while self._isRunning is True:
            time.sleep(0.5)
            for i in range(0, 109 + 1):
                # delay(10000)
                time.sleep(0.003)
                self.s1.emit(i, plcglobal.listplccoils.getelement(i))
                self.vesisignal.emit(plcglobal.listplcrg16.getelement(VES1INDEX),
                                     plcglobal.listplcrg16.getelement(VES2INDEX),
                                     plcglobal.listplcrg16.getelement(VES3INDEX),
                                     plcglobal.listplcrg16.getelement(VESCHASTOTAINDEX)
                                     )

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

        writedebug(u'---thread ThreadVisual1Level FINISHED')
        self.finished.emit()

    def stop(self):
        self._isRunning = False

class ThreadVizual2level(QtCore.QObject):  # визулизация шиберов- по состоянию концевиков
    finished = QtCore.pyqtSignal()
    s3 = QtCore.pyqtSignal()
    _isRunning = False

    @QtCore.pyqtSlot()
    def process(self):
        writedebug(u"--+thread ThreadVizual2level started")
        while self._isRunning is True:

            self.s3.emit()
            # delay(10000)
            time.sleep(0.5)
            # print 'FINISHED'

        writedebug(u"--+thread ThreadVizual2level done")
        self.finished.emit()

    def stop(self):
        self._isRunning = False

class ThreadControlRecept(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    outerror = QtCore.pyqtSignal()
    showtime = QtCore.pyqtSignal(int)
    showerror = QtCore.pyqtSignal(int)
    _isRunning = False
    lasterror = 0
    allerrors = 0
    ves1 = 0
    ves2 = 0
    ves3 = 0
    tick=0
    ves1last=0
    ves2last=0
    ves3last=0
    tick30sec = []
    def __init__(self):
        QtCore.QObject.__init__(self)

    @QtCore.pyqtSlot()
    def process(self):

        while(self._isRunning == True):
            time.sleep(1)
            self.showtime.emit(plcglobal.ticktimerrecept())
            for cmd,command in plcglobal.commands.iteritems(): # контроль исполнения команд ПЛК
                if command.controlexec == True:
                    command.checkexecute()


            # print plcglobal.listplcrg16.getelement(REG_ERROR)
            # rg0 = mbclient.client.read_holding_registers(0,1)
            # if tick!=0:
            #     tick=tick+1
            # self.ves1 = plcglobal.listplcrg16.list[VES1INDEX]
            # self.ves2 = plcglobal.listplcrg16.list[VES2INDEX]
            # self.ves3 = plcglobal.listplcrg16.list[VES3INDEX]

                # Error Warning
                #   0 ves1error (слишком большое значение в заказе) -> не грузится
                #   1 ves2error (слишком большое значение в заказе) ->
                #   2 ves3error (слишком большое значение в заказе)->
                #   3 errorlineK (ошибка при команде на включение шнека смесителя при  выключенной нории) -> не включается шнек смеситель
                #   4 errorperklapan (перекидование клапана нории происходит больше 1 минуты) ->
                #   5  errormixer( выключено тепловое реле)
                #   6 errorline1  выключено тепловое реле
                #   7 errorline2 выключено тепловое реле
                # reg14 plc16
                #   0 AWILA ERR (Загорелась лампа fault)
                #   1 mixer not unload
                #   2 миксер не открывается, так как бункер под миксером не пустой
            # if plcglobal.pulerrors:
            #     self.showerror.emit(plcglobal.pulerrors.pop(0))
            shneknow_=0
            try:
                for ishnek_,shnek_ in plcglobal.shnekszerno.iteritems():
                    shneknow_ = ishnek_
                    shnek_.chkstate()
                    if shnek_.started:
                        write(u"Запущен шнек " + str(ishnek_-55))
                    if shnek_.endwork == True:
                        write(u"Шнек закончил работу" + str(ishnek_-55))
                        try:
                            write(u"Шнек "+str(ishnek_-55) + u" загрузил " + str((shnek_.weightend - shnek_.weightbegin) / 10.0) + u"кг")
                            db.registerweight(plcglobal.getnumbanka(ishnek_), shnek_.weightend - shnek_.weightbegin)
                        except Exception as err:
                            write(u" Ошибка записи веса в БД" + str(err))
                            logging.error(traceback.format_exc())
                    if shnek_.error:
                        write(u"Слишком долго работает шнек " + str(ishnek_))
                for ishnek_,shnek_ in plcglobal.shneksdobavka.iteritems():
                    shneknow_=ishnek_
                    shnek_.chkstate()
                    if shnek_.started:
                        write(u"Запущен флэксвэй "+ str(ishnek_-23))
                    if shnek_.endwork == True:
                        write(u"Флэксвэй закончил работу" + str(ishnek_-23))
                        try:
                            write(u"Флэксвэй " + str(ishnek_ - 23) + u" загрузил " + str((shnek_.weightend - shnek_.weightbegin) / 10.0) + u"кг")
                            db.registerweight(plcglobal.getnumbanka(ishnek_),shnek_.weightend - shnek_.weightbegin)
                        except Exception as err:
                            write(u" Ошибка записи веса в БД" + str(err))
                            logging.error(traceback.format_exc())
                    if shnek_.error:
                        write(u"Слишком долго работает флэксвэй "+str(ishnek_))
            except Exception as err:
                write(u" Ошибка обработки состояния шнека(флэксвэя)("+str(shneknow_)+u")" + str(err))
                logging.error(traceback.format_exc())
            error = 0
            if (plcglobal.pulerrors):
                error = plcglobal.pulerrors.pop(0)
                write(u" Зарегистрирована ошибка ПЛК: " + plcglobal.errors[error])
                self.showerror.emit(error)
            error = 0
            for i in range(0,16):
                try:
                    error = getbit(plcglobal.listplcrg16.getelement(REG_ERROR),i)
                except Exception as err:
                    logging.error(traceback.format_exc())
                    writedebug(u"--Ошибка чтения регистра REGERROR" + str(err))
                if error==1 and i!=ERRORLINEK and i!=ERRORAWILA:
                # if error == 1:
                    self.lasterror = 1<<i
                    # if(self.allerrors and (0xFFFF-(1<<self.lasterror)))==0:
                    #     self.allerrors = self.allerrors or 1<<i
                    if plcglobal.newerror != self.lasterror:
                        writedebug(u"Зарегистрирована ошибка ПЛК: " + plcglobal.errors[i])
                        plcglobal.newerror = self.lasterror
                        # self.showerror.emit(i)

                # else:
                #     plcglobal.newerror = self.lasterror
                #     logging.debug(u"Ошибки сброшены: " + plcglobal.errors[i])
                #     print str(datetime.datetime.now()) + u" Ошибки сброшены: " + plcglobal.errors[i]


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
        # print str(datetime.datetime.now())+"--+thread ThreadSendCmd started  cmd= " + str(self.cmd)
        writedebug(u"--+thread ThreadSendCmd started  cmd= " + str(self.cmd))
        plcglobal.send_cmd(self.cmd)
        self.finished.emit()

    def stop(self):
        self._isRunning = False

class ThreadWorkZames(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    startsession = QtCore.pyqtSignal()
    getrecept = QtCore.pyqtSignal()
    endcicle = QtCore.pyqtSignal()
    endsession = QtCore.pyqtSignal()
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
        writedebug(u"--+thread ThreadWorkZames started")
        # f = open('c:\\stages.txt', 'w')
        # >> > f.write('HelloWorld!')
        # >> > f.()
        while self._isRunning is True:
            write(u"=========Сессия началась=========")
            self.startsession.emit()
            ves1 = plcglobal.listplcrg16.getelement(VES1INDEX)
            ves2 = plcglobal.listplcrg16.getelement(VES2INDEX)
            ves3 = plcglobal.listplcrg16.getelement(VES3INDEX)
            if ves2 > VESMAX | ves3 > VESMAX:
                write(u"--Достигнуто максимальное значение весов, обнулите")
            write(u"Ожидание обнуления весов")
            while ves2 > VESMAX and ves3 > VESMAX:
                ves1 = plcglobal.listplcrg16.getelement(VES1INDEX)
                ves2 = plcglobal.listplcrg16.getelement(VES2INDEX)
                ves3 = plcglobal.listplcrg16.getelement(VES3INDEX)
            write(u"--весы обнулены")

            # plcglobal.send_cmd(COMMAND_MIXER_UNLOAD)
            plcglobal.send_cmd(COMMAND_INIT)
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT1)
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT2)
            plcglobal.send_cmd(COMMAND_ZERO_WEIGHT3)
            plcglobal.send_cmd(COMMAND_LINE2_START)

            dbstatus = mbclient.read(REG_STATUS)
            mbclient.send(REG_STATUS, dbstatus & (65535 - (1 << DOPDOBAVKAREADY)))
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
            writedebug(u"--while session_begin == True:")
            self.newcicle=True
            while self.session_begin == True:
                time.sleep(0.5)
                if self.newcicle==True :    # Если текущий счетчик замесов обнулен
                    writedebug(u"--Заполняем editы согласно очереди")
                    plcglobal.recept.getzakazcomplete = False
                    self.getrecept.emit()  # Взять текущий рецепт из очереди и заполнить все edit'ы согласно текущему рецепту и заполнить массив
                    while plcglobal.recept.getzakazcomplete != True:
                        pass
                    plcglobal.recept.getzakazcomplete = False
                    writedebug(u"--Отправка рецепта добавка и зерно(все)")
                    for i in range(0, 8):
                        print plcglobal.recept.zakaz.getelement(i)
                        mbclient.send(i + 20, plcglobal.recept.zakaz.getelement(i))  # Отправка рецепта зерна
                    for i in range(8, 14):
                        print plcglobal.recept.zakaz.getelement(i)
                        mbclient.send(i + 20,plcglobal.recept.zakaz.getelement(i))  # Отправка рецепта добавок с 28 по 33
                    mbclient.send(34, plcglobal.recept.zakaz.getelement(14))
                    self.newcicle=False
                if dbstatus !=plcglobal.status:
                    dbstatus = plcglobal.status
                if plcglobal.lasterror != plcglobal.newerror:
                    plcglobal.lasterror = plcglobal.newerror
                    error = plcglobal.lasterror
                    lasterror = 1
                    if error == (1 << ERRORPERKLAPAN):

                        write( u" Ожидание устранения неисправности перекидного клапана")
                        while (lasterror == 1):
                            lasterror = getbit(plcglobal.listplcrg16.list[REG_ERROR], ERRORPERKLAPAN)

                    # if error == (1 << ERRORLINEK):
                    #     logging.debug(u"Ожидание устранения неисправности перекидного клапана")
                    #     plcglobal.textout.append(
                    #         str(datetime.datetime.now()) + u" Ожидание устранения неисправности ERRORLINEK")
                    #     while (lasterror == 1):
                    #         lasterror = getbit(plcglobal.listplcrg16.list[REG_ERROR], ERRORLINEK)
                    if error == (1 << ERRORLINEK):
                        write(u" Ожидание устранения неисправности линии нории")
                        while (lasterror == 1):
                            lasterror = getbit(plcglobal.listplcrg16.list[REG_ERROR], ERRORLINEK)
                    if error == (1 << ERRORMIXER):
                        logging.debug(u"Прерывание изготовления рецепта в связи с ошибкой миксера(возможно выключено тепловое реле)")
                        self.session_begin = False
                        self._isRunning = False
                        dbstatus = 0
                    if error == (1 << ERRORLINE1):
                        logging.debug(u"Прерывание изготовления рецепта в связи с ошибкой линии весов1(возможно выключено тепловое реле)")
                        self.session_begin = False
                        self._isRunning = False
                        dbstatus =0
                    if error == (1 << ERRORWEIGHT1) or error == (1 << ERRORWEIGHT2) or error == (1 << ERRORWEIGHT3):
                        write(u"Прерывание изготовления рецепта в связи с ошибкой загрузки весов")
                        self.session_begin = False
                        self._isRunning = False
                        dbstatus =0
                    if error == (1 << ERRORLINE2):
                        write(u"Прерывание изготовления рецепта в связи с ошибкой линии весов2(возможно выключено тепловое реле)")
                        self.session_begin = False
                        self._isRunning = False
                        dbstatus = 0
                    if error == (1<<ERRORMIXERNOTUNLOAD):
                        write( u" Ожидание устранения ошибки ERRORMIXERNOTUNLOAD ")
                        while (lasterror == 1):
                            lasterror = getbit(plcglobal.listplcrg16.list[REG_ERROR], ERRORMIXERNOTUNLOAD)
                    if error == (1<<ERRORMIXERNOTOPEN):
                        write(u" Ожидание устранения ошибки ERRORMIXERNOTOPEN")
                        while (lasterror == 1):
                            lasterror = getbit(plcglobal.listplcrg16.list[REG_ERROR], ERRORMIXERNOTOPEN)

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
                dobdobavkaready = getbit(dbstatus,DOPDOBAVKAREADY)
                time.sleep(0.5)
                if plcglobal.pause == True:
                    while(plcglobal.pause == True):
                        time.sleep(0.5)
                        pass
                if plcglobal.recept.dopdobavka == False:
                    dobdobavkaready = 1

                if ves2readyload == 1 and  not plcglobal.commands[COMMAND_VES12_START].is_registered():
                    time.sleep(0.5)
                    if plcglobal.recept.count == plcglobal.recept.needcount:
                        write(u"-------СТАРТ изготовления рецепта---: " + str(plcglobal.recept.receptname))
                    if plcglobal.recept.count<=0 and self.session_end==False:
                        writedebug(u"--Счетчик <Количество замесов> достиг нуля- изготовление цикла(рецепта) завершено! Переход к следующему циклу")
                        writedebug(u"--Ожидание исполнения endcicle.emit")
                        plcglobal.recept.endciclecomplete = False
                        self.endcicle.emit()  # следующий цикл замесов (следующий рецепт)
                        while(plcglobal.recept.endciclecomplete==False):
                            pass
                        writedebug(u"endcicle.emit завершено")
                        plcglobal.recept.endciclecomplete = False
                        write(u"Изготовление рецепта  " + plcglobal.recept.procinfo.receptprev + u"завершается")

                        if plcglobal.countqueue > 0:  # если очередь не пуста
                            writedebug(u"--<Количество замесов>  равно 0 И <Количество циклов> больше 1, готовим следующий цикл")
                            write(u"Очередь не пуста, подготовка к следующему рецепту")
                            self.newcicle = True  # готовим следующий цикл
                            self.session_end = False
                        else:  # если очередь пуста # не готовим следующий цикл
                            writedebug(u"--<Количество замесов>  равно 1 И <Количество циклов> меньше или равно 1, НЕ готовим следующий цикл")
                            write(u"Очередь пуста, после изготовления рецепта(выгрузки из миксера), окончание работы")
                            self.newcicle = False
                            self.session_end = True
                            plcglobal.recept.procinfo.receptnow=u"Нет заказа"
                    if plcglobal.recept.count>0:
                        self.checklevelkorm.emit()
                        plcglobal.commands[COMMAND_VES12_START].execute(timeout = 10)
                        plcglobal.recept.deccount()
                        plcglobal.recept.procinfo.countves2 = plcglobal.recept.needcount - plcglobal.recept.count
                        plcglobal.recept.stagenameves12 = plcglobal.recept.procinfo.receptnow + u" " + str(plcglobal.recept.procinfo.countves2)+u" из "+  str(plcglobal.recept.needcount)
                        write(u"Загрузка весов2 - Рецепт " + unicode(plcglobal.recept.procinfo.receptnow) + u" номер замеса " + str(plcglobal.recept.procinfo.countves2))
                # if noriaready == 1:
                #     plcglobal.recept.stagenamelinek = u" Линия нории пуста "
                #     if plcglobal.recept.selectkormnumbanka[0] != plcglobal.recept.nowkormnumbanka:
                #         plcglobal.waitret()
                #         plcglobal.send_cmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
                #         logging.debug(u"COMMAND_NORIA_INIT" + str(plcglobal.recept.selectkormnumbanka[0]))
                #         plcglobal.textout.append(u"Настройка линии нории на банку №"+str(plcglobal.recept.selectkormnumbanka[0]))
                # stateves3shiber = getbit(plcglobal.listplcrg16.list[9],)
                if ves3readyload == 1 and plcglobal.commands[COMMAND_VES12_START].is_registered() and  not  plcglobal.commands[COMMAND_VES3_START].is_registered() and self.session_end!=True:
                    time.sleep(0.01)
                    plcglobal.commands[COMMAND_VES3_START].execute(timeout=10)
                    plcglobal.recept.procinfo.countves3 = plcglobal.recept.procinfo.countves2
                    plcglobal.recept.stagenameves3 = plcglobal.recept.procinfo.receptnow + u" " + str(plcglobal.recept.procinfo.countves3) + u" из " + str(plcglobal.recept.needcount)
                    write(u"Загрузка весов3 - Рецепт " + (plcglobal.recept.procinfo.receptnow) + u" номер замеса " + str(plcglobal.recept.procinfo.countves3))
                if ves2readyunload == 1 and line2readyload == 1 and mixerreadyload == 1 and not plcglobal.commands[COMMAND_VES2_UNLOAD].is_registered():
                    time.sleep(0.01)
                    plcglobal.recept.procinfo.countline2 = plcglobal.recept.procinfo.countves2
                    plcglobal.recept.procinfo.countmixer = plcglobal.recept.procinfo.countves2
                    plcglobal.recept.procinfo.countoil = plcglobal.recept.procinfo.countves2
                    plcglobal.recept.stagenameline12 = unicode(plcglobal.recept.procinfo.receptnow) + u" " + str(plcglobal.recept.procinfo.countline2) +u" из "+  str(plcglobal.recept.needcount)
                    plcglobal.recept.stagenamemixer = plcglobal.recept.receptname + u" " + str(plcglobal.recept.procinfo.countmixer)+u" из "+  str(plcglobal.recept.needcount)
                    plcglobal.commands[COMMAND_VES2_UNLOAD].execute(timeout=10)
                    plcglobal.commands[COMMAND_VES12_START].unreg()
                    plcglobal.tick = False
                    write(u"Выгрузка весов2 - Рецепт " + unicode(plcglobal.recept.procinfo.receptnow) + u" номер замеса " + str(plcglobal.recept.procinfo.countves2))
                    self.starttimer.emit(60000)  # таймер 1 минута 60000 милисекунд
                    time.sleep(3)
                    # write(u"Ожидание завершения выгрузки весов2 и начала дробления")
                    # while(plcglobal.commands[COMMAND_VES2_UNLOAD].is_done!=True):
                    #     pass
                    plcglobal.starttimerecept()

                if ves3readyunload == 1 and plcglobal.tick == True and plcglobal.commands[COMMAND_VES12_START].is_registered() and not plcglobal.commands[COMMAND_VES3_UNLOAD].is_registered():
                    plcglobal.tick = False
                    time.sleep(0.01)
                    plcglobal.commands[COMMAND_VES3_UNLOAD].execute(timeout=10)
                    plcglobal.commands[COMMAND_OIL_START].execute(timeout=10)
                    plcglobal.send_cmd(COMMAND_DOPDOBAVKA_START)
                    # logging.debug(u"COMMAND_DOPDOBAVKA_START")
                    plcglobal.commands[COMMAND_VES3_START].unreg()
                    plcglobal.commands[COMMAND_MIXER_UNLOAD].unreg()
                    plcglobal.recept.procinfo.countoil = plcglobal.recept.procinfo.countves3
                    plcglobal.recept.stagenameoil = plcglobal.recept.procinfo.receptprev + u" " + str(plcglobal.recept.procinfo.countoil) + u" из " + str(plcglobal.recept.needcount)
                    write(u"Выгрузка весов3 - Рецепт " + plcglobal.recept.procinfo.receptprev + u" номер замеса " + str(plcglobal.recept.procinfo.countves3))
                    write(u"Загрузка масла - Рецепт " + plcglobal.recept.procinfo.receptprev + u" номер замеса " + str(plcglobal.recept.procinfo.countves3))
                if mixerreadyunload == 1 and not plcglobal.commands[COMMAND_MIXER_UNLOAD].is_registered() and oilready == 1 and plcglobal.commands[COMMAND_VES3_UNLOAD].is_registered() and dobdobavkaready == 1:
                    write(u"Проверка линии комбикорма(Нория)")
                    if plcglobal.recept.selectbankaisneed()!=True:
                        time.sleep(3)
                        write(u"Открыт силос " + str(plcglobal.recept.nowkormnumbanka))
                        write(u"Необходим "+str(plcglobal.recept.selectkormnumbanka[0]))
                        write(u"Открытый силос комбикорма не соответсвует выбранному ")
                        write(u"Ожидание перевода на нужный силос ")
                        plcglobal.commands[COMMAND_NORIA_INIT].execute(10)
                    else:
                        write(u"Открыт необходимый силос")
                        write(u"Выгрузка миксера - Рецепт " + plcglobal.recept.procinfo.receptprev + u" номер замеса " + str(plcglobal.recept.procinfo.countmixer))
                        if plcglobal.recept.procinfo.receptprev!=plcglobal.recept.procinfo.receptnow:
                            write(u"----Завершено изготовление рецепта---:"+plcglobal.recept.procinfo.receptprev)
                        plcglobal.stoptimerrecept()
                        plcglobal.recept.procinfo.countlinek = plcglobal.recept.procinfo.countmixer
                        dbstatus = mbclient.read(REG_STATUS)
                        mbclient.send(REG_STATUS, dbstatus & (65535-(1<<DOPDOBAVKAREADY)))

                        plcglobal.commands[COMMAND_MIXER_UNLOAD].execute(timeout=30)
                        plcglobal.recept.stagenamemixer = plcglobal.recept.procinfo.receptprev + u" "  + str(plcglobal.recept.procinfo.countmixer)+u" из "+  str(plcglobal.recept.needcount)
                        plcglobal.recept.stagenamelinek = plcglobal.recept.procinfo.receptprev + u" "  + str(plcglobal.recept.procinfo.countlinek) +u" из "+  str(plcglobal.recept.needcount)
                        plcglobal.commands[COMMAND_VES3_UNLOAD].unreg()
                        plcglobal.commands[COMMAND_VES2_UNLOAD].unreg()
                        plcglobal.commands[COMMAND_OIL_START].unreg()


                        if self.session_end==True:
                            write(u"Счетчик <Количество циклов> достиг нуля-завершение сессии; " )
                            writedebug(u"countcicle = " +str(plcglobal.countqueue))
                            self.session_begin = False
                            self._isRunning = False
                            self.newcicle = False
                            plcglobal.readytostart= True

        # if self.session_end == True:
        #     plcglobal.waitret()
        #     plcglobal.send_cmd(COMMAND_MIXER_OFF)
        #     plcglobal.waitret()
        #     plcglobal.send_cmd(COMMAND_LINE2_STOP)
        write(u"=========Сессия завершена=========")
        self._isRunning = False
        self.finished.emit()
        writedebug(u"-thread ThreadWorkZames is done")
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
        self.zeroves1btn.clicked.connect(self.zeroves1btnclk)
        self.zeroves2btn.clicked.connect(self.zeroves2btnclk)
        self.zeroves3btn.clicked.connect(self.zeroves3btnclk)
        self.moviesL2.insert(0, objs( obj(self.ves1shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves1,"","lineves1.png","")))
        self.moviesL2.insert(1, objs( obj(self.ves2shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves2,"","lineves2.png","")))
        self.moviesL2.insert(2, objs( obj(self.ves3shiber, "vesishiberclose.png", "vesishiberopen.png", ""),obj(self.lineves3,"","line3mixer.png","")))
        self.moviesL2.insert(3, objs( obj(self.silos1shiber, "silosshiberclose.png", "silosshiberopen.png", ""))) # комбикорм
        self.moviesL2.insert(4, objs( obj(self.silos2shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(5, objs( obj(self.silos4shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(6, objs( obj(self.silos5shiber, "silosshiberclose.png", "silosshiberopen.png", "")))
        self.moviesL2.insert(7, objs( obj(self.mixershiber,  "mixershiberclose.png", "mixershiberopen.png", ''),obj(self.linemixerbunker,"","linemixerbunker.png","")))

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
        self.movies.insert(2, objs(obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png")))# reserv
        self.movies.insert(3, objs(obj(self.dobavkisilos1up, "statusfalse.png", "statustrue.png")))# reserv
        self.movies.insert(4, objs(obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png")))
        self.movies.insert(5, objs(obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png")))
        self.movies.insert(6, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(7, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(8, objs(obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", "")))
        # reg7 PLC2(dobavki)
        self.movies.insert(9, objs(obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(10, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(11, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(12, objs(obj(self.dobavkisilos4up, "statusfalse.png", "statu9strue.png", "")))
        self.movies.insert(13, objs(obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(14, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(15, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        # reg8 PLC3(dobavki)
        self.movies.insert(16, objs(obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(17, objs(obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(18, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(19, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))# reserv
        self.movies.insert(20, objs(obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(21, objs(obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", "")))
        self.movies.insert(22, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))
        self.movies.insert(23, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", "")))
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
        self.movies.insert(35, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))) #reserv
        self.movies.insert(36, objs(obj(self.silos_zerno, "siloszerno.png", "siloszerno.png", ""))) #reserv
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
        self.workerzames = None
        self.btnload12.hide()
        self.btnload3.hide()
        self.btnunload3.hide()
        self.btnoil.hide()
        self.btnunload1.hide()
        self.btnunload2.hide()
        self.checkboxline1.hide()
        self.checkboxline2.hide()
        self.btnunloadmixer.hide()
        self.checkboxmixer.hide()
        self.checkboxlinek.hide()
        self.btnsetuplinek.hide()
        self.btndopdobavka.hide()
        self.btnload12.clicked.connect(self.clkload12)
        self.btnload3.clicked.connect(self.clkload3)
        self.btnunload1.clicked.connect(self.clkunload1)
        self.btnunload2.clicked.connect(self.clkunload2)
        self.btnunload3.clicked.connect(self.clkunload3)
        self.btnunloadmixer.clicked.connect(self.clkunloadmixer)
        self.btnsetuplinek.clicked.connect(self.clklinek)
        self.btnoil.clicked.connect(self.clkoil)
        self.btndopdobavka.clicked.connect(self.clkdopdobavka)

        self.checkboxline1.stateChanged.connect(self.chkline1)
        self.checkboxline2.stateChanged.connect(self.chkline2)
        self.checkboxmixer.stateChanged.connect(self.chkmixer)
        self.checkboxlinek.stateChanged.connect(self.chklinek)

        self.checkboxmode.stateChanged.connect(self.statemode)
        self.labelauto.setText(u"Программа в режиме ожидания")

        # reg14 PLC15
        # Error Warning
        #   0 ves1error (слишком большое значение в заказе) -> не грузится
        #   1 ves2error (слишком большое значение в заказе) ->
        #   2 ves3error (слишком большое значение в заказе)->
        #   3 errorlineK (ошибка при команде на включение шнека смесителя при  выключенной нории) -> не включается шнек смеситель
        #   4 errorperklapan (перекидование клапана нории происходит больше 1 минуты) ->
        #   5  errormixer( выключено тепловое реле)
        #   6 errorline1  выключено тепловое реле
        #   7 errorline2 выключено тепловое реле
        # reg14 plc16
        #   0 AWILA ERR (Загорелась лампа fault)
        #   1 mixer not unload
        #   2 миксер не открывается, так как бункер под миксером не пустой
        #
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
        # reg54 weight1
        # reg55 weight2
        # reg56 weight3

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
        self.editdobavka.triggered.connect(self.dobavkabtnclk)
        self.actionexit.triggered.connect(self.exitclk)
        self.cal_action.triggered.connect(self.calclk)

        self.activethreads = []
        if DEBUGFLAG == False:
            self.startThreadVisual1Level(QThread(self), plcglobal)
            self.startThreadVizual2level(QThread(self))
            self.startThreadGetPLC(QThread(self))
            self.startThreadPullPLCList(QThread(self))
            self.startThreadControlRecept(QThread(self))
            self.pushButton.hide()
        else:
            # self.startThreadVisual1Level(QThread(self), plcglobal)
            self.startThreadVizual2level(QThread(self))
            # self.startThreadGetPLC(QThread(self))
            # self.startThreadPullPLCList(QThread(self))
            self.startThreadControlRecept(QThread(self))

        # for i in range(0,len(loadreceptnamelist())):
        #     self.comboBoxRecept.addItem(loadreceptnamelist)
        # if dbclient is not False:
        #     self.dbclient=dbclient
        # for row in self.dbclient.get_product(IDKORM):
        #     self.comboBoxRecept.addItem(row[NAMEPRODUCT])
        self.pushButton.clicked.connect(self.pushbtnclk)
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
        self.btnaddstage.clicked.connect(self.clkbtnaddstage)
        self.btnsubstage.clicked.connect(self.clkbtnsubstage)
        self.showtime(0)

    def pushbtnclk(self):
        # plcglobal.shnekszerno[ISHNEK4].weightend = 666
        # db.registerweight(plcglobal.getnumbanka(59),plcglobal.shnekszerno[ISHNEK4].weightend)
        # plcglobal.commands[COMMAND_VES12_START].execute(4)
        # plcglobal.commands[COMMAND_MIXER_UNLOAD].execute(8)
        # plcglobal.commands[COMMAND_VES3_UNLOAD].execute(100)
        # plcglobal.commands[COMMAND_VES2_UNLOAD].execute(1)
        # plcglobal.status = plcglobal.status or (1<<VES2READYLOAD)
        # plcglobal.status = plcglobal.status +  (1<<MIXERREADYUNLOAD)
        plcglobal.starttimerecept()
        pass

    def clkbtnaddstage(self):
        if  self.combostages.currentText() == u"Весы12 ЗАГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_VES12_START")
        if self.combostages.currentText() == u"Весы3 ЗАГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_VES3_START")
        if self.combostages.currentText() == u"Весы1 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_VES1_UNLOAD")
        if self.combostages.currentText() == u"Весы2 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_VES2_UNLOAD")
        if self.combostages.currentText() == u"Весы3 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_VES3_UNLOAD")
        if self.combostages.currentText() == u"МАСЛО ЗАГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_OIL_START")
        if self.combostages.currentText() == u"МИКСЕР ВЫГРУЗИТЬ":
            plcglobal.recept.stages.add(u"COMMAND_MIXER_UNLOAD")
    def clkbtnsubstage(self):
        if  self.combostages.currentText() == u"Весы12 ЗАГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_VES12_START")
        if self.combostages.currentText() == u"Весы3 ЗАГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_VES3_START")
        if self.combostages.currentText() == u"Весы1 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_VES1_UNLOAD")
        if self.combostages.currentText() == u"Весы2 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_VES2_UNLOAD")
        if self.combostages.currentText() == u"Весы3 ВЫГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_VES3_UNLOAD")
        if self.combostages.currentText() == u"МАСЛО ЗАГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_OIL_START")
        if self.combostages.currentText() == u"МИКСЕР ВЫГРУЗИТЬ":
            plcglobal.recept.stages.sub(u"COMMAND_MIXER_UNLOAD")
    def statemode(self):
        if self.checkboxmode.isChecked():
            self.btnload12.show()
            self.btnload3.show()
            self.btnunload3.show()
            self.btnoil.show()
            self.btnunload1.show()
            self.btnunload2.show()
            self.checkboxline1.show()
            self.checkboxline2.show()
            self.btnunloadmixer.show()
            self.checkboxmixer.show()
            self.checkboxlinek.show()
            self.btnsetuplinek.show()
            self.btndopdobavka.show()
        else:
            self.btnload12.hide()
            self.btnload3.hide()
            self.btnunload3.hide()
            self.btnoil.hide()
            self.btnunload1.hide()
            self.btnunload2.hide()
            self.checkboxline1.hide()
            self.checkboxline2.hide()
            self.btnunloadmixer.hide()
            self.checkboxmixer.hide()
            self.checkboxlinek.hide()
            self.btnsetuplinek.hide()
            self.btndopdobavka.hide()
    def clkload12(self):
        writedebug(u"POPUP команда Загрузить весы12 ")
        mbclient.send(20, int(self.zernoedit3.text()))
        mbclient.send(21, int(self.zernoedit4.text()))
        mbclient.send(22, int(self.zernoedit5.text()))
        mbclient.send(23, int(self.zernoedit6.text()))
        mbclient.send(24, int(self.zernoedit7.text()))
        mbclient.send(25, int(self.zernoedit8.text()))
        mbclient.send(26, int(self.zernoedit9.text()))
        mbclient.send(27, int(self.zernoedit10.text()))
        self.startThreadCmd(COMMAND_VES12_START)
    def clkload3(self):
        writedebug(u"POPUP команда Загрузить весы3 ")
        mbclient.send(28, int(self.dobavkaedit1.text()))
        mbclient.send(29, int(self.dobavkaedit2.text()))
        mbclient.send(30, int(self.dobavkaedit3.text()))
        mbclient.send(31, int(self.dobavkaedit4.text()))
        mbclient.send(32, int(self.dobavkaedit5.text()))
        mbclient.send(33, int(self.dobavkaedit6.text()))
        self.startThreadCmd(COMMAND_VES3_START)
    def clkunload1(self):
        writedebug(u"POPUP команда Выгрузить весы1 ")
        self.startThreadCmd(COMMAND_VES1_UNLOAD)
    def clkunload2(self):
        writedebug(u"POPUP команда Выгрузить весы2 ")
        self.startThreadCmd(COMMAND_VES2_UNLOAD)
    def clkunload3(self):
        writedebug(u"POPUP команда Выгрузить весы3 ")
        self.startThreadCmd(COMMAND_VES3_UNLOAD)
    def clkunloadmixer(self):
        writedebug(u"POPUP команда Выгрузка миксер ")
        self.startThreadCmd(COMMAND_MIXER_UNLOAD)
    def clklinek(self):
        writedebug(u"POPUP команда Включить Линия Комбикорм ")
        plcglobal.recept.selectkormnumbanka = []
        for i in range(0, 6):
            if self.interface_[i].state is True:  # выделенную банку
                plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
        # print plcglobal.recept.selectkormnumbanka[1]
        self.startThreadCmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
    def clkoil(self):
        writedebug(u"POPUP команда Загрузить масло ")
        mbclient.send(34, int(self.masloedit.text()))
        self.startThreadCmd(COMMAND_OIL_START_HAND)
    def chkline1(self):
        if self.checkboxline1.isChecked():
            writedebug(u"POPUP команда Включить Линия1")
            self.startThreadCmd(COMMAND_LINE1_START)
        else:
            writedebug(u"POPUP команда Включить Линия1")
            self.startThreadCmd(COMMAND_LINE1_STOP)
    def chkline2(self):
        if self.checkboxline2.isChecked():
            writedebug(u"POPUP команда Включить Линия2")
            self.startThreadCmd(COMMAND_LINE2_START)
        else:
            writedebug(u"POPUP команда Выключить Линия2")
            self.startThreadCmd(COMMAND_LINE2_STOP)
    def chkmixer(self):
        if self.checkboxmixer.isChecked():
            writedebug(u"POPUP команда Включить шнек после миксера ")
            self.startThreadCmd(COMMAND_MIXER_ON)
        else:
            writedebug(u"POPUP команда Выключить миксер ")
            self.startThreadCmd(COMMAND_MIXER_OFF)
    def chklinek(self):
        if self.checkboxlinek.isChecked():
            writedebug(u"POPUP команда Включить Линия Комбикорм ")
            plcglobal.recept.selectkormnumbanka = []
            for i in range(0, 6):
                if self.interface_[i].state is True:  # выделенную банку
                    plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
            self.startThreadCmd(COMMAND_NORIA_INIT + (plcglobal.recept.selectkormnumbanka[0] << 8))
        else:
            writedebug(u"POPUP команда Выключить Линия Комбикорм ")
            self.startThreadCmd(COMMAND_NORIA_STOP)
        # if action == InfoAction:
        #     print "Открыта банка №" + str(plcglobal.recept.nowkormnumbanka)
    def clkdopdobavka(self):
        logging.debug(u"POPUP команда Включить уведомление  допдобавка ")
        self.startThreadCmd(COMMAND_DOPDOBAVKA_START)
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
        # plcglobal.readytostart = True
        # indexes = table.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())
    def addqueuebtnclk(self):
        # self.tableWidget.Add ()

        # plcglobal.needcountlist.append()
        count = self.kormneedcount.text()
        # plcglobal.recept.needcount = count
        # count=self.kormneedcount.Text()
        name = self.comboBoxRecept.currentText()
        if name != '' and (count != '0' and count != ''):
            newitem = QTableWidgetItem(name)
            self.tableWidget.setItem(self.currentrow, 0, newitem)
            newitem = QTableWidgetItem(count)
            self.tableWidget.setItem(self.currentrow, 1, newitem)
            plcglobal.addqueue(int(count),name)
            self.currentrow += 1
            # print self.currentrow
            writedebug(u"Указатель таблицы очередь на строке "+str(self.currentrow))
            if self.currentrow > 9:
                self.tableWidget.setRowCount(self.currentrow + 1)
    def comboboxchangedslot(self):
        self.loadrecept((str(self.comboBoxRecept.currentText()).encode('utf-8')))
    def loadrecept(self, name):
        namerecept = ''
        namerecept = name
        current_recept = {}
        current_recept = plcglobal.recept.receptlist.get(namerecept)
        # print current_recept.items()
        writedebug(u"  Выбран рецепт " + current_recept.get('namekorm'))

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
        checkdopdob = current_recept.get('dopdob')
        if checkdopdob == '1':
            self.checkdopdob.setChecked(True)
        else:
            self.checkdopdob.setChecked(False)
        self.checkdopdob.setEnabled (False)
        somelistrecept = []
        somelistrecept = current_recept.get('selectkorm')

        # print somelistrecept
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
        write(u"Нажата кнопка СТОП")
        writedebug(u"workerzames = "+str(type(self.workerzames)))
        plcglobal.recept.nullcount()
        self.startThreadCmd(COMMAND_STOP)
        try:
            if self.workerzames!=None:
                write(u"СТОП сессия")
                self.workerzames.session_begin= False
                self.workerzames._isRunning = False
                self.workerzames.deleteLater()

        except Exception as err:
            logging.error(traceback.format_exc())
            writedebug(u"Error with workzames end in stopbtnclk "+str(err))

    def startbtnclk(self):
        # self.plc.recept.count = 1
        write(u"СТАРТ !")
        # if  self.checkbox.is_Checked():
        #     if plcglobal.countqueue>0:
        #         self.startThreadWorkZames(QThread(self))
        #     else:
        #         print "<Список пуст>"
        # else:
        #     plcglobal.count=1
        #     self.startThreadWorkZames(QThread(self))
        if plcglobal.countqueue > 0:
            # self.startbtn.setEnabled(False)
            # plcglobal.readytostart=False
            if self.workerzames == None:
                self.startThreadWorkZames(QThread(self))
            else:
                write(u"Невозможно запустить процесс, так как предыдущий не завершен, либо завершен некорректно, перезапустите программу")
        else:
            write(u"Игнорирование события СТАРТ, <Список пуст>")
        # else:
        #     self.plc.recept.selectkormnumbanka = 0
        #     self.plc.recept.count = 0
        #     print "no select silos for kombikorm"
        # cell = self.tableWidget.item(0, 1).text()

    def pausebtnclk(self):
        # print unicode(self.pausebtn.text())
        if unicode(self.pausebtn.text()) == u"Пауза":
            # print "Пауза"
            self.pausebtn.setText( u"Возобновить")
            plcglobal.pause = True
            write(u"Отправка команды Пауза")
            logging.debug(u"ПАУЗА")
            # plcglobal.send_cmd(COMMAND_PAUSE)
            self.startThreadCmd(COMMAND_PAUSE)
        else:
            # print "Возобновление"
            self.startThreadCmd(COMMAND_RUN)
            self.pausebtn.setText(u"Пауза")
            plcglobal.pause = False
            write(u"Возобновление")
            logging.debug(u"ВОЗОБНОВЛЕНИЕ")
    def vesivisuallevel1slot(self, vesi1, vesi2, vesi3, chast):
        if vesi1 > 32768:
            vesi1 = vesi1 - 65535
        if vesi2 > 32768:
            vesi2 = vesi2 - 65535
        if vesi3 > 32768:
            vesi3 = vesi3 - 65535

        self.labelves1.setText(str(vesi1 / 10.0))
        self.labelves2.setText(str(vesi2 / 10.0))
        self.labelves3.setText(str(vesi3 / 10.0))
        self.chastota1.setText(str(chast & 0x00FF)+' Hz')
        self.chastota2.setText(str((chast )>>8)+' Hz')
    def startThreadVisual1Level(self, thread_, plc):
        writedebug(u"--Try start thread visual1level")
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
        writedebug(u"--Try start thread visual2level")
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
        writedebug(u"--Try start thread ThreadGetPLC")
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
        writedebug(u"--Try start thread ThreadPullPLCList")
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

        writedebug(u"--Try start thread ThreadCmd")
        thread_ = QThread(self)
        self.cmdthread = ThreadSendCmd(cmd)
        self.cmdthread.moveToThread(thread_)
        thread_.started.connect(self.cmdthread.process)
        self.cmdthread.finished.connect(thread_.quit)
        self.cmdthread.finished.connect(self.cmdthread.deleteLater)
        thread_.finished.connect(thread_.deleteLater)
        thread_.start()
    def startThreadWorkZames(self, thread_):

        writedebug(u"--Try start thread ThreadWorkZames")
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        # print type(self.activethreads[-1])
        self.workerzames = ThreadWorkZames(plcglobal, mbclient)
        self.workerzames.moveToThread(thread)
        self.workerzames.startsession.connect(self.workzamesstartslot)
        self.workerzames.getrecept.connect(self.workzamesgetreceptslot)
        self.workerzames.endcicle.connect(self.workzamesendslot)
        self.workerzames.endsession.connect(self.workzamesendsession)
        self.workerzames.starttimer.connect(self.workzamestimerslot)
        self.workerzames.checklevelkorm.connect(self.workerzamescheckslot)
        self.workerzames.changenoria.connect(self.workerzameschangenoria)

        thread.started.connect(self.workerzames.process)
        self.workerzames.finished.connect(thread.quit)
        self.workerzames.finished.connect(self.workerzames.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.workerzames._isRunning = True
        thread.start()
    def startThreadControlRecept(self,thread_):

        writedebug(u"--Try start thread ThreadControlrecept")
        self.activethreads.append(thread_)
        thread = self.activethreads[-1]
        # print type(self.activethreads[-1])
        self.controlzames = ThreadControlRecept()
        self.controlzames.moveToThread(thread)

        thread.started.connect(self.controlzames.process)
        self.controlzames.showtime.connect(self.showtime)
        self.controlzames.showerror.connect(self.showerror)
        self.controlzames.finished.connect(thread.quit)
        self.controlzames.finished.connect(self.controlzames.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.controlzames._isRunning = True
        thread.start()
    def showtime(self,timesec):
        m, s = divmod(timesec, 60)
        texttime =  "%02d:%02d" % ( m, s)
        self.lcdNumber.display(texttime)
        # print texttime
    def showerror(self,errorid):
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(plcglobal.errors[errorid])
            msg.setInformativeText(u"Ошибка "+ plcglobal.errors[errorid])
            msg.setWindowTitle( plcglobal.errors[errorid])
            msg.setDetailedText(u"The details are as follows: "+ plcglobal.errordetails[errorid])
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        except Exception  as err:
            logging.error(traceback.format_exc())
            writedebug(u"Ошибка вывода в def showerror "+str(err))
    def workzamestimerslot(self, time_tick):
        writedebug(u"--start timer")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerslot)
        self.timer.start(time_tick)
    def timerslot(self):
        plcglobal.tick = True
        writedebug(u"Timer: time over")
        self.timer.stop()
    def visual1levelslot(self, index, bit):
        def shiber_switch(obj1, obj2, obj3):

            if obj2.state is True and obj3.state is False:  # если включен концевик "открыто"
                obj1.switch(1)  # открыть шибер
            if obj2.state is False and obj3.state is True:  # если включен концевик "закрыто"
                obj1.switch(0)  # закрыть шибер
            if obj2.state is False and obj3.state is False:  # если оба концевика выключены
                obj1.switch(1)  # открыть шибер
                pass
            if obj2.state is True and obj3.state is True:
                pass
        self.movies[index].switch(bit)
        if DEBUGFLAG==False:
            if mbclient.okconnection == True:
                self.connectstatuslabel.setText(u"Соединение с ПЛК..Соединено")
                self.connectstatuslabel.setStyleSheet('color: black')

            else:
                self.connectstatuslabel.setText(u"Соединение с ПЛК..Разорвано")
                self.connectstatuslabel.setStyleSheet('color: red')
                # self.plcstatuslabel.setText(u"Статус ПЛК..Неизвестно")

        banki = range(8)
        for i in range(0,8):
            banki[i] = plcglobal.recept.listzernoneed.getelement(i+2)
            if banki[i]>65000:
                banki[i]=banki[i]-65535
            banki[i]=banki[i]/10.0
        self.labelbanka3.setText(str(banki[0]))
        self.labelbanka4.setText(str(banki[1]))
        self.labelbanka5.setText(str(banki[2]))
        self.labelbanka6.setText(str(banki[3]))
        self.labelbanka7.setText(str(banki[4]))
        self.labelbanka8.setText(str(banki[5]))
        self.labelbanka9.setText(str(banki[6]))
        self.labelbanka10.setText(str(banki[7]))

        banki2 = range(6)
        for i in range(0, 6):
            banki2[i] = plcglobal.recept.listdobavkaneed.getelement(i)
            if banki2[i] > 65000:
                banki2[i] = banki2[i] - 65535
            banki2[i] = banki2[i] / 10.0

        self.labelbanka11.setText(str(banki2[0]))
        self.labelbanka12.setText(str(banki2[1]))
        self.labelbanka13.setText(str(banki2[2]))
        self.labelbanka14.setText(str(banki2[3]))
        self.labelbanka15.setText(str(banki2[4]))
        self.labelbanka16.setText(str(banki2[5]))
        maslo = plcglobal.recept.masloneed
        # if maslo > 65000:
        #     maslo = maslo - 65535
        #  maslo = maslo / 10.0

        self.labelbanka17.setText(str(maslo/10.0))

        self.labelves2readyunload.setText(u"ves2readyunload " + str(getbit(plcglobal.status, VES2READYUNLOAD)))
        if getbit(plcglobal.status, VES2READYLOAD) == 1:
            self.labelves2readyload.setText(u"Весы2 ЗАГРУЗКА__________ГОТОВ")
        else:
            self.labelves2readyload.setText(u"Весы2 ЗАГРУЗКА__________НЕ ГОТОВ")
        if getbit(plcglobal.status, VES2READYUNLOAD) == 1:
            self.labelves2readyunload.setText(u"Весы2 ВЫГРУЗКА__________ГОТОВ")
        else:
            self.labelves2readyunload.setText(u"Весы2 ВЫГРУЗКА__________НЕ ГОТОВ")
        if getbit(plcglobal.status, VES3READYLOAD) == 1:
            self.labelves3readyload.setText(u"Весы3 ЗАГРУЗКА__________ГОТОВ")
        else:
            self.labelves3readyload.setText(u"Весы3 ЗАГРУЗКА__________НЕ ГОТОВ")
        if getbit(plcglobal.status, VES3READYUNLOAD) == 1:
            self.labelves3readyunload.setText(u"Весы3 ВЫГРУЗКА__________ГОТОВ")
        else:
            self.labelves3readyunload.setText(u"Весы3 ВЫГРУЗКА__________НЕ ГОТОВ")

        if getbit(plcglobal.status, MIXERREADYUNLOAD) == 1:
            self.labelmixerreadyunload.setText(u"Миксер ВЫГРУЗКА_________ГОТОВ")
        else:
            self.labelmixerreadyunload.setText(u"Миксер ВЫГРУЗКА_________НЕ ГОТОВ")
        if getbit(plcglobal.status, MIXERREADYLOAD) == 1:
            self.labelmixerreadyload.setText(u"Миксер ЗАГРУЗКА_________ГОТОВ")
        else:
            self.labelmixerreadyload.setText(u"Миксер ЗАГРУЗКА_________НЕ ГОТОВ")
        if getbit(plcglobal.status, LINE2READYLOAD) == 1:
            self.labelline2readyload.setText(u"Линия2 Дробилки_________ГОТОВ")
        else:
            self.labelline2readyload.setText(u"Линия2 Дробилки_________НЕ ГОТОВ")

        if getbit(plcglobal.status, NORIAREADYLOAD) == 1:
            self.labelnoriaready.setText(u"Нория___________________ПУСТО")
        else:
            self.labelnoriaready.setText(u"Нория___________________ЗАНЯТО")
        if getbit(plcglobal.status, MASLOREADY) == 1:
            self.labelmasloready.setText(u"Масло ЗАГРУЖЕНО________ДА")
        else:
            self.labelmasloready.setText(u"Масло ЗАГРУЖЕНО________НЕТ")
        if getbit(plcglobal.status, DOPDOBAVKAREADY)==1:
            self.labeldopdobready.setText(u"ДОП ДОБАВКА ЗАКИНУТА__ДА")
        else:
            self.labeldopdobready.setText(u"ДОП ДОБАВКА ЗАКИНУТА__НЕТ")

        self.labeltimer.setText(u"plcglobaltick = " +str(plcglobal.tick))
        if plcglobal.listplcrg16.list[REALVES1INDEX]>65000:
            plcglobal.listplcrg16.list[REALVES1INDEX] = plcglobal.listplcrg16.list[REALVES1INDEX] - 65535
        self.labelrealweight1.setText(u"Весы1 без учета тары " + str(plcglobal.listplcrg16.list[REALVES1INDEX]/10.0))
        if plcglobal.listplcrg16.list[REALVES2INDEX]>65000:
            plcglobal.listplcrg16.list[REALVES2INDEX] = plcglobal.listplcrg16.list[REALVES2INDEX] - 65535
        self.labelrealweight2.setText(u"Весы2 без учета тары " + str(plcglobal.listplcrg16.list[REALVES2INDEX]/10.0))
        if plcglobal.listplcrg16.list[REALVES3INDEX]>65000:
            plcglobal.listplcrg16.list[REALVES3INDEX] = plcglobal.listplcrg16.list[REALVES3INDEX] - 65535
        self.labelrealweight3.setText(u"Весы3 без учета тары " + str(plcglobal.listplcrg16.list[REALVES3INDEX]/10.0))


        if plcglobal.readytostart == False:
            self.startbtn.setEnabled(False)
        else:
            self.startbtn.setEnabled(True)


        # if self.plc.state is 0 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ожидание команды")
        # if self.plc.state is 1 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Закончил загрузку весов")
        # if self.plc.state is 2 and self.mbclient.okconnection:
        #     self.plcstatuslabel.setText(u"Статус ПЛК..Ошибка")
        shiber_switch(self.moviesL2[0], self.movies[48], self.movies[49])
        shiber_switch(self.moviesL2[1], self.movies[50], self.movies[51])
        shiber_switch(self.moviesL2[2], self.movies[38], self.movies[39])
        shiber_switch(self.moviesL2[3], self.movies[80], self.movies[81])
        shiber_switch(self.moviesL2[4], self.movies[82], self.movies[83])
        shiber_switch(self.moviesL2[5], self.movies[84], self.movies[85])
        shiber_switch(self.moviesL2[6], self.movies[86], self.movies[87])
        shiber_switch(self.moviesL2[7], self.movies[41], self.movies[42])
    def visual2levelslot(self):  # визулизация шиберов- по состоянию концевиков

        while plcglobal.textout:
            self.textEdit.append(plcglobal.textout.pop(0))
        self.labelinfooil.setText(plcglobal.recept.stagenameoil)
        self.labelinfoves12.setText((plcglobal.recept.stagenameves12))
        self.labelinfonoria.setText((plcglobal.recept.stagenamelinek))
        self.labelinfoves3.setText((plcglobal.recept.stagenameves3))
        self.labelinfoline12.setText((plcglobal.recept.stagenameline12))
        self.labelcountqueue.setText(str(plcglobal.countqueue))
        self.labelcountzames.setText(str(plcglobal.recept.count))
        self.stagestext.clear()
        for stage in plcglobal.recept.stages.list:
            self.stagestext.append(str(stage))
        self.labelactivebanka.setText(u"Открыта банка №"+str(plcglobal.recept.nowkormnumbanka))
    def workerzameschangenoria(self,num):
        write(u"Авто перенастройка линии нория на банку №"+str(num))
        self.startThreadCmd(COMMAND_NORIA_INIT + (num << 8))
    def workzamesstartslot(self):
        writedebug(u"start! slot from threadPLCZames signal_  startcicle emit ")
        self.labelauto.setText(u"Программа в АВТО-режиме")
        self.labelauto.setStyleSheet('color: red')
        # self.workerzameschangenoria(plcglobal.recept.selectkormnumbanka[0])
        # self.plc.recept.selectkormnumbanka=2

        # print "select kormsilos = "+str(self.plc.recept.selectkormnumbanka)

        # self.plc.recept.selectkormnumbanka=2
    def workzamesendslot(self):
        writedebug(u"--Endcicle  emited")
        try:
            self.tableWidget.removeRow(0)
        except Exception as err:
            writedebug(u"Error in WorkZames slot endslot(def workerzamesendslot)" + str(err))
            logging.error(traceback.format_exc())

        plcglobal.decqueue()
        writedebug(u"--count queue = "+str(plcglobal.countqueue))
        if plcglobal.countqueue==0:
            self.deleteallrow()
        plcglobal.recept.endciclecomplete = True
    def workzamesendsession(self):
        writedebug(u"--Endsession  emited")
        try:
            self.labelauto.setText(u"Программа в режиме ожидания")
        except Exception as err:
            writedebug(u"Error in WorkZames slot endslot(def workerzamesendslot)" + str(err))
            logging.error(traceback.format_exc())
    def workzamesgetreceptslot(self):
        writedebug(u"getrecept emited")
        # self.loadrecept(str(self.tableWidget.item(0, 0).text()))

        plcglobal.recept.receptname = str(self.tableWidget.item(0, 0).text())
        plcglobal.recept.needcount = plcglobal.needcountlist.pop(0)
        plcglobal.recept.procinfo.receptnow =( plcglobal.receptnamelist.pop(0))
        if plcglobal.recept.procinfo.receptprev =='':
            plcglobal.recept.procinfo.receptprev = plcglobal.recept.procinfo.receptnow
        writedebug(u"Загрузка рецепта: " + str(self.tableWidget.item(0, 0).text())+u" количесвто замесов "+str(plcglobal.recept.needcount))
        plcglobal.recept.setcount(plcglobal.recept.needcount)
        writedebug(u"Количество замешиваний: " + str(plcglobal.recept.count ))
        plcglobal.recept.selectkormnumbanka = []
        for i in range(0, 6):
            if self.interface_[i].state is True:  # выделенную банку
                plcglobal.recept.selectkormnumbanka.append(i + 1)  # помещаем в список банок для комбикорма
                writedebug(u"Выгрузка комбикорма в  банку №" + str(i))
        plcglobal.recept.getzakazcomplete = True
        write(u"Заказан рецепт: "+unicode(plcglobal.recept.procinfo.receptnow))
        write(u"Количество замесов: " + str(plcglobal.recept.count))
        current_recept = {}
        current_recept = plcglobal.recept.receptlist.get(plcglobal.recept.receptname)
        checkdopdob = current_recept.get('dopdob')
        if checkdopdob == '1':
            self.checkdopdob.setChecked(True)
        else:
            self.checkdopdob.setChecked(False)
        self.checkdopdob.setEnabled(False)

        if self.checkdopdob.isChecked():
            plcglobal.recept.dopdobavka = True
        else:
            plcglobal.recept.dopdobavka = False
        list_ = range(15)

        list_.insert(0, int(current_recept.get('zerno3')))
        list_.insert(1, int(current_recept.get('zerno4')))
        list_.insert(1, int(current_recept.get('zerno4')))
        list_.insert(2, int(current_recept.get('zerno5')))
        list_.insert(3, int(current_recept.get('zerno6')))
        list_.insert(4, int(current_recept.get('zerno7')))
        list_.insert(5, int(current_recept.get('zerno8')))
        list_.insert(6, int(current_recept.get('zerno9')))
        list_.insert(7, int(current_recept.get('zerno10')))
        list_.insert(8, int(current_recept.get('dobavka1')))
        list_.insert(9, int(current_recept.get('dobavka2')))
        list_.insert(10, int(current_recept.get('dobavka3')))
        list_.insert(11, int(current_recept.get('dobavka4')))
        list_.insert(12, int(current_recept.get('dobavka5')))
        list_.insert(13, int(current_recept.get('dobavka6')))
        list_.insert(14, int(current_recept.get('maslo')))

        if current_recept.get('dopdob') == '1':
            self.checkdopdob.setChecked(True)
        else:
            self.checkdopdob.setChecked(False)
        self.checkdopdob.setEnabled(False)
        plcglobal.recept.selectkormnumbanka = []
        index_banka_ = (current_recept.get('selectkorm'))

        for i in range(0, 6):
            if str(i + 1) in (index_banka_):
                plcglobal.recept.selectkormnumbanka.append(i+1)
            else:
                pass

        plcglobal.recept.zakaz.pull(list_)
    def workerzamescheckslot(self):
        write(u"--Проверка заполнености силоса готового комбикорма, (№"+str(plcglobal.recept.selectkormnumbanka[0])+u")")
        # plcglobal.textout.append( u"Проверка заполнености силоса готового комбикорма, силос №"+str(plcglobal.recept.selectkormnumbanka[0]))
        if self.movies[plcglobal.kormbankauplevel[plcglobal.recept.selectkormnumbanka[0]-1]].state == True:
            plcglobal.recept.nullcount()
            write(u"Выбранный силос заполнен, окончание изготовления текущего корма: " + plcglobal.recept.procinfo.receptnow)
        else:
            write(u"Выбранный силос(№" +str(plcglobal.recept.selectkormnumbanka[0]) + u")не заполнен")
            # plcglobal.textout.append(u"Выбранный силос не заполнен: " + plcglobal.recept.procinfo.receptnow)
        # print str(plcglobal.recept.needcount - plcglobal.recept.count)+" из "+str(plcglobal.recept.needcount)
        newitem = QTableWidgetItem(str(plcglobal.recept.needcount - plcglobal.recept.count)+u" из "+str(plcglobal.recept.needcount)) # осталось замесов
        self.tableWidget.setItem(0, 1, newitem)
# print plcglobal.recept.receptlist.keys()
# print plcglobal.recept.receptlist.values()
writedebug('========================S T A R T===================================')

config = CONFIG()
db = DB(config.ipaddrdb, "root", "root", config.namedb)
DEBUGFLAG = False

if config.ERROR_READ_INI is False:
    # self.db = MySQLdb.coect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
    if DEBUGFLAG is False:
        # mbclient=mbclient(config.ipaddrplc,config.portplc)
        logging.info('Create modbus client object')
        mbclient = mbclient('10.0.6.98', '502')
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

