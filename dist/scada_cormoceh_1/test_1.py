# list1 = []
# list1.append(12)
# list1.append(14)
# list1.append(14)
# list1.append(14)
#
# for item in list1:
#     print item
#
# dict = {}
# dict[1]=2
# dict[4]=1
# # print dict
# list_ = []
#
# class list_flag(object):
#     def __init__(self,flag):
#
#         self.flag = flag
#         print self.flag
#     def ready(self):
#         return self.flag
#
# list_.append(list_flag(False))
# list_.append(list_flag(False))
# list_.append(list_flag(True))
# list_.append(list_flag(False))
#
#
# def load(list_):
#     for i in range(0, len(list_)):
#         if list_[i].ready():
#             print "ready="+str(i)
#             return True
#         else:
#             print "not ready "
#             continue
#     return False
#
# print load(list_)
#
# somedict = {}
# somedict[1] = 9
# somedict[2] = 8
# somedict[3] = 7
# somedict[55] = 6
# somedict[6] = 5
# print somedict
# list_ = []
# for key,elem in somedict.iteritems():
#     list_.append(somedict[key])
#
# print list_
#
# class bunker(object):
#     def __init__(self,flag):
#         self.flag = flag
#     def send_val(self,val):
#         print self.flag
#         print val
#
#
# bunkers = []
# bunkers.append(bunker(False))
# bunkers.append(bunker(True))
# bunkers.append(bunker(False))
# bunkers.append(bunker(False))
#
# def load(bunkers,val):
#     for i in range(0, len(bunkers)):
#         print i
#         if bunkers[i].flag == True:
#             bunkers[i].send_val(val)
#             return True
#         else:
#             continue
#     return False
#
# print load(bunkers,100)

class somecl(object):
    def __init__(self,list_):
        self.list_= list_
    def reglistelem(self,elem):
        self.list_.append(elem)
        print "list_ "
        print self.list_

somelist = []
somelist.append(1)
somelist.append(10)
somelist.append(3)
print "somelist "
print somelist
sm = somecl(somelist)
sm.reglistelem(33)
sm.reglistelem(31)
sm.reglistelem(330)
print "somelist "
print somelist
min = -100
print (somelist[-2]-somelist[-1])
if (somelist[-2]-somelist[-1])<min:
    print min




