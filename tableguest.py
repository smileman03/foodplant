# -*- coding: utf-8 -*-
# coding: utf-8
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread
import time
from PyQt4.QtGui import *
# -*- coding: utf-8 -*-
reload(sys)
sys.setdefaultencoding('utf-8')
class tables(object):
    def __init__(self,txt):
        with open(txt) as f:
            self.lines = f.readlines()
        for i  in range(0,len(self.lines)):
            self.lines[i] =  self.lines[i].decode('cp1251').encode('utf-8')
    def out_(self):
        for item in self.lines:
            # -*- coding: utf-8 -*-
            print (item)


table = range(7)


table[1]=tables('table1.txt')
table[2]=tables('table2.txt')
table[3]=tables('table3.txt')
table[4]=tables('table4.txt')
table[5]=tables('table5.txt')
table[6]=tables('table6.txt')

name = "Бадмаев"

for i in range(1,7):
    for item in table[i].lines:
        if name in item:
            print item
            print "Стол №"+str(i)
            print "\n"
            print "\n"
        else:
            pass


# print table1.lines[0]
# table1.out_()
# name = "Бадмаев Леонид".decode('cp1251').encode('utf-8')
#
# if name in table1.lines:
#     print name
# else:
#     print "Noname"
# with open('table1.txt') as f:
#     lines = f.readlines()
# print str(lines)
