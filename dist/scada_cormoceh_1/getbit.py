
def getbit(reg16,indexbit):

    if reg16&(1<<indexbit ) is not  0:
        print 1
    else:
        print 0

# print (1<<4 & 16)

def getbit2(reg16,indexbit):
    if reg16<<indexbit is True:
        print 1
    else:
        print 0
getbit2(1,4)