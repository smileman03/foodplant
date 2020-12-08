# coding: utf-8
import MySQLdb
import MySQLdb.cursors
class DB(object):
    def __init__(self, baseaddress_, user_, passw_, db_):
        self.db = MySQLdb.connect(host=baseaddress_, user=user_, passwd=passw_, db=db_, charset='utf8')
        # self.db = MySQLdb.connect(host="192.168.17.192", user="oper", passwd="Adelante", db="kormoceh4", charset='utf8')
        self.idlastuser = 1
        self.reinit = False
    def get_recepts(self):
        self.cursor = self.db.cursor()
        self.sql = """SELECT * FROM recept"""
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()
    def get_zerno(self):  # Получить список зерна
        self.cursor = self.db.cursor()
        self.sql = """SELECT nRec,Name FROM product where nGrp_Product=""" + str(1)  # 1-зерно 2-добавки 3 -корм
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()
    def get_listproduct(self,id):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nRec,Name FROM product where nGrp_Product=%s""",(id,))
        dict_={}
        for items in cursor.fetchall():
            dict_[str(items[0])] = (items[1])
        return dict_
    def get_listdozakaz(self):
        cursor = self.db.cursor()
        cursor.execute("""SELECT Nrec,Name,Last_Date FROM zakaz where status = 0 ORDER BY nRec""")
        dict_ = {}

        for items in cursor.fetchall():
            list_ = []
            list_.append(items[1])
            list_.append(str(items[2]))
            dict_[int(items[0])] = list_
        return dict_
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
    def getreceptnamelist(self):
        self.cursor = self.db.cursor()
        self.cursor.execute("""SELECT nRec,nProduct FROM `recept` WHERE bActive = 1 """)
        somedict = {}
        for items in self.cursor.fetchall():
            somedict[int(items[0])] = int(items[1])
        return somedict
    def getreceptlist(self,idrecept): # return id recept by name idkorm
        cursor = self.db.cursor()
            # print idkorm[0]
        cursor.execute("""SELECT nProduct,Val FROM `recept_det` WHERE nRecept = %s """,(idrecept,))
        somedict = {}
        list1 = []
        for items in cursor.fetchall():
            somedict[str(items[0])] = items[1]
        return  somedict
    def getzakazdet_list(self,nreczakaz):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nProduct,Val FROM zakaz_det WHERE nZakaz = %s""",(nreczakaz,))
        somedict = {}
        list1 = []
        for items in cursor.fetchall():
            somedict[str(items[0])] = items[1]
        return somedict
    def getzakazdet(self,nrec):
        dict_={}
        cursor = self.db.cursor()
        cursor.execute("""SELECT nProduct,Fact FROM zakaz_det WHERE nzakaz = %s""", (nrec,))
        result = cursor.fetchall()
        print ("nzakaz "+str(nrec))
        for items in result:
            dict_[int(items[0])] = items[1]
        return dict_
    def createzakaz(self,nrecrecept,numbunker,val):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO zakaz (last_User,Name, nBunker,nRecept,Val,dt) SELECT %s,Name, %s,nRec,%s,CURRENT_TIME() FROM recept WHERE nRec=%s", (self.idlastuser,numbunker,val,nrecrecept,))
        self.db.commit()
        cursor.execute("SELECT nRec FROM zakaz order by nRec DESC")
        return int(cursor.fetchall()[0][0])
    def getidrecept(self,namekorm):
        cursor = self.db.cursor()
        id_korm = self.get_id_product(namekorm)
        cursor.execute("""SELECT nRec FROM `recept` WHERE NProduct = %s and bActive = 1""", (id_korm,))
        return cursor.fetchall()[0]
    def get_bunker(self,id_ingridient):  # Получить номер банки по Id продукта(Зерно =1, Добавки=2, Комбикорм=3, Масло=4)
        self.cursor = self.db.cursor()
        # self.sql = """SELECT Name FROM bunker WHERE nGrp_Bunker=""" + str(id_ingridient)
        self.cursor.execute("""SELECT Name FROM bunker WHERE nGrp_Bunker=%s""",(id_ingridient,))
        return self.cursor.fetchall()
    def getnumbunker(self,nrecprod):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nBunker FROM prod_bunker WHERE nProduct=%s and bActive = 1 ORDER BY nBunker""",(nrecprod,))
        list_ = []
        result = cursor.fetchall()
        for item in result:
            list_.append(int(item[0]))
        # print "getnumbunker"
        # print result
        # return str(result[0][0])
        return  list_
        # return str(result[0][0])
    def get_product(self, id_banka): # продукт по номеру банки
        self.cursor = self.db.cursor()
        # self.sql = """SELECT nProduct,Name FROM `kormoceh4`.`product` a, `prod_bunker` b  WHERE a.`nRec` = b.nProduct and  b.nBunker= """ + str(id_banka)
        rows_count = self.cursor.execute("""SELECT nProduct,Name FROM `product` a, `prod_bunker` b WHERE a.`nRec` = b.`nProduct` and b.`nBunker`=%s and b.`bActive` = '1' """,(id_banka,))

        if rows_count > 0:
            row = ''
            for row in self.cursor.fetchall():
                pass
        else:
            row = [None]*2
            row[0] = " "
            row[1] = u"На ремонте"
        return row  # row[0] - nRec row[1] - Name
    def get_productname(self,nrec):
        cursor = self.db.cursor()
        cursor.execute("""SELECT NAME FROM `product` WHERE nRec = %s""",(nrec,))
        return cursor.fetchall()
    def save_product(self, id_banka, id_product):
        cursor = self.db.cursor()
        # print id_banka
        # countrow = cursor.execute("""SELECT nRec FROM `prod_bunker` WHERE `bActive` = '1' and `nBunker` = %s  """, (id_banka))
        # # nRec_Old=
        # row = ''
        # if countrow > 0:
        #     for row in self.cursor.fetchall():
        #         print row
        #         pass
        #     nRec_Old = row
        #     print "nrec old "+nRec_Old

        countrow = cursor.execute("""SELECT nRec FROM `prod_bunker` WHERE `bActive` = '1' and `nBunker` = %s  """,
                                  (id_banka,))
        if countrow:
            for row in cursor.fetchall():
                # print row
                pass
            oldrec = row[0]
            # print "oldrec "+str(old_rec)
            cursor.execute("UPDATE `prod_bunker` SET `bActive`=0 WHERE nRec=%s", (oldrec,))
            self.db.commit()
            cursor.execute(
                "INSERT INTO prod_bunker (Last_User,nBunker, nProduct)  SELECT %s,nBunker, %s FROM prod_bunker WHERE nRec=%s",
                (self.idlastuser, id_product, oldrec,))
            self.db.commit()
        else:
            cursor.execute("""SELECT nRec FROM `prod_bunker` WHERE `bActive` = '0' and `nBunker` = %s  """,(id_banka,))
            for row in cursor.fetchall():
                pass
            oldrec = row[0]
            cursor.execute("UPDATE `prod_bunker` SET `bActive`=1,nProduct =%s WHERE nRec=%s", ( id_product,oldrec,))
            self.db.commit()

            # else:
            #     print "jopa"
            # sql = """UPDATE `prod_bunker` SET `nProduct` = %s  WHERE `prod_bunker`.`nBunker` = %s """
            # sql = """UPDATE `prod_bunker` SET `nProduct` = 3  WHERE `prod_bunker`.`nBunker` = 3 """

            # sql = """INSERT INTO `oborot`(`nRec`, `Last_Date`, `Last_User`, `nProduct`, `nBunker`, `Val`) VALUES(NULL, CURRENT_TIME(), '1', %s, %s, %s); """

            # sql ="""INSERT INTO prod_bunker (nBunker, nProduct) SELECT nBunker, %s FROM prod_bunker WHERE nRec=%s"""
            # cursor.execute(sql, (id_product, id_banka))

            # sql = """INSERT INTO `prod_bunker`(`nProduct` = %s  WHERE `prod_bunker`.`nBunker` = %s """
    def get_bunkerrecept(self,nrecrecept):
        cursor = self.db.cursor()

        cursor.execute("""SELECT nProduct FROM recept where nrec = %s and bActive = 1""",(nrecrecept,))
        nrecproduct = (cursor.fetchall()[0][0])
        # print nrecproduct
        cursor.execute("""SELECT nBunker FROM prod_bunker WHERE nProduct = %s ORDER BY nBunker  """,(nrecproduct,))
        list_=[]
        for item in cursor.fetchall():
            list_.append(int(item[0])-20)
        if  list_:
            return list_
        else:
            return None
    def get_id_product(self,Name):
        cursor = self.db.cursor()
        countrows = cursor.execute("""SELECT * FROM `product` WHERE `product`.`Name` = %s """,(Name,))
        if countrows > 0:
            row = ''
            rows =  cursor.fetchall()
            for row in rows:
                pass
            return row[0]
        else:
            return None
    def registerweight(self,numbanka,val,nreczakaz,nrecrecept):
        err_ = 0
        try:
            row = self.get_product(numbanka)
            nproduct = row[0]
            cursor = self.db.cursor()
            if nreczakaz!=0:
                cursor.execute("INSERT INTO oborot (`Last_User`,nZakaz, nProduct, nBunker, Val, Rashod,dt) VALUES(%s,%s,%s,%s,%s,%s,CURRENT_TIME())",(self.idlastuser,nreczakaz,nproduct ,numbanka, -val,val,))
            else:
                cursor.execute("""INSERT INTO `oborot`(`nRec`, `Last_Date`, `Last_User`, `nProduct`, `nBunker`, `Val`,`Rashod`,`dt`) VALUES(NULL, CURRENT_TIME(), '1', %s, %s, %s,%s,CURRENT_TIME()); """, (nproduct, numbanka, -val,val,))
            self.db.commit()
            # cursor.execute("SELECT nRec FROM zakaz_det WHERE nZakaz=%s", (nreczakaz,))
            # nreczakazdet = cursor.fetchall()[0][0]
            # cursor.execute("UPDATE zakaz_det SET Fact=%s WHERE nRec=%s", (val, nreczakazdet,))
            # self.db.commit()
        except Exception as err:
            err_= err
        return err_
    def setdeactive_(self,id_banka):
        cursor = self.db.cursor()
        # print id_banka
        # countrow = cursor.execute("""SELECT nRec FROM `prod_bunker` WHERE `bActive` = '1' and `nBunker` = %s  """, (id_banka))
        # # nRec_Old=
        # row = ''
        # if countrow > 0:
        #     for row in self.cursor.fetchall():
        #         print row
        #         pass
        #     nRec_Old = row
        #     print "nrec old "+nRec_Old

        countrow = cursor.execute("""SELECT nRec FROM `prod_bunker` WHERE `bActive` = '1' and `nBunker` = %s  """,
                                  (id_banka,))
        if countrow:
            for row in cursor.fetchall():
                # print row
                pass
            oldrec = row[0]
            # print "oldrec "+str(old_rec)
            cursor.execute("UPDATE `prod_bunker` SET `bActive`=0 WHERE nRec=%s", (oldrec,))
            self.db.commit()

            return 0
        else:
            return 1
    def changerecept(self,oldnrec,receptlist):
        cursor = self.db.cursor()
        print ("oldnrec "+str(oldnrec))
        cursor.execute("""UPDATE recept SET bActive=0 WHERE nRec=%s""", (str(oldnrec),))
        self.db.commit()
        cursor.execute(("""INSERT INTO recept (Last_User,name, nProduct, val) SELECT %s,name, nProduct, val FROM recept WHERE nRec=%s"""),(1,oldnrec,))
        self.db.commit()
        cursor.execute("""SELECT nRec FROM recept order by nRec DESC LIMIT 1""")
        newnrec = cursor.fetchall()[0]
        for key in receptlist:
            print ("newnrec "+str(newnrec[0]))
            print("num product "+(key))
            print("value "+str(receptlist[key]))
            cursor.execute("INSERT INTO recept_det SET nRecept=%s, nProduct=%s, val=%s",(newnrec[0], key, receptlist[key],))
            self.db.commit()
    def register_zakaz_det(self,nreczakaz,nbunker,koef,nrecrecept,factval):
        print (u"register_zakaz nreczakaz = {nreczakaz}, nrecrecept = {nrecrecept}, koef={koef}, nbunker={nbunker}, factval={factval}".format(nreczakaz=nreczakaz,nrecrecept=nrecrecept,koef=koef, nbunker=nbunker,factval=factval))
        nprod = self.get_product(nbunker)[0]
        cursor = self.db.cursor()
        err_=0
        #1. Получить nrec продукта по номеру банки
        # 2. Записать в zakaz_det fact по nrec рецепта и nrec продукта
        # try:
        #cursor.execute("INSERT INTO zakaz_det (nZakaz, nProduct, nBunker, Val,Fact) SELECT %s, nProduct, %s, Val*%s,%s FROM recept_det WHERE nRecept=%s",(nreczakaz, nbunker, koef, factval,nrecrecept,))

        print( u"nrecproduct={nprod}".format(nprod=nprod))
        cursor.execute("INSERT INTO zakaz_det (nZakaz, nProduct, nBunker, Val,Fact) SELECT %s, nProduct, %s, Val*%s,%s FROM recept_det WHERE nRecept=%s and nProduct=%s",(nreczakaz, nbunker, koef, factval, nrecrecept, nprod,))
        self.db.commit()
        err_ = self.register_zames_fact(nreczakaz,factval)
        return err_
        # except Exception as err:
        #     err_=err
        #
        # return err_
    def register_zames_fact(self,nzakaz,val):
        cursor = self.db.cursor()
        err_=0
        cursor.execute( "SELECT Fact FROM zakaz WHERE nRec=%s",(nzakaz,))
        sumFact = int(cursor.fetchall()[0][0])
        print (u"1.sumFact = {val}".format(val=sumFact))
        sumFact += val
        print (u"2.sumFact ={vl}".format(vl=sumFact))
        try:
            cursor.execute( "UPDATE  zakaz SET Fact = %s WHERE nRec=%s",(sumFact,nzakaz,))
            self.db.commit()
        except Exception as err:
            err_=err
        finally:
            return err_
    def zakaz_complete(self,nreczakaz):

        cursor = self.db.cursor()
        cursor.execute("""UPDATE zakaz SET Status=1 WHERE nRec=%s""", (nreczakaz,))
        # cursor.execute("INSERT INTO oborot (Last_User,nZakaz, nProduct, nBunker, Val) SELECT %s,%s, %s, nBunker, %s FROM zakaz WHERE nRecept=%s",(self.idlastuser,nreczakaz, nrecproduct, val, nrecrecept))
        self.db.commit()
    def getlastzakaz_tofinish(self): # получить последний незавершенный заказ
        cursor = self.db.cursor()
        countrec = cursor.execute("""SELECT nRec FROM zakaz order by `Last_Date` desc limit 1""")
        if countrec>0:
            return cursor.fetchall()[0][0]
        else:
            return None
    def save_modbus(self,list_):
        cursor = self.db.cursor()
        err_ = 0
        countrec = cursor.execute("""SELECT nRec FROM zakaz order by `Nrec` desc limit 1""")
        nrec = cursor.fetchall()[0][0]
        try:
            for i in range(0,len(list_)):
                cursor.execute("""INSERT INTO modbus (`%s`)  VALUE(%s) WHERE Nrec = ;""",('REG'+str(i),list_[i],))
        except Exception as err:
                # print str(err)
            err_=err
        finally:
            self.db.commit()
            return err_
    def getallproducts(self):
        list_ = []
        cursor = self.db.cursor()
        try:
            cursor.execute("""SELECT nrec FROM product WHERE bActive = 1""")
            for item in cursor.fetchall():
                list_.append(item[0])
        except Exception as err:
            return None
        return list_
    def set_notactive(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("""SELECT nrec FROM product WHERE bActive = 1""")
            for item in cursor.fetchall():
                list_.append(item[0])
        except Exception as err:
            return None






    # def createmodbus(self):
    #     cursor = self.db.cursor()
    #     for i in range(8,57):
    #         cursor.execute("ALTER TABLE `modbus` ADD COLUMN `%s` INTEGER(6) DEFAULT NULL;",('REG'+str(i)))
    #     self.db.commit()
