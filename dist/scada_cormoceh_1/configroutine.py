# -*- coding: utf-8 -*-
from  ConfigParser import *
import MySQLdb

############  INI ###############
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
############ END class INI ENDENDENDENDENDENDENDENDEND

############ class SQL ###############
##
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

##
############ END class SQL ENDENDENDENDENDENDENDENDEND

