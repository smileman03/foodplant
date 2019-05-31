from pymodbus.client.sync import ModbusTcpClient as ModbusClient


class MBclient:

    def __init__(self,PLCaddress,PLCport):
        self.client = ModbusClient(PLCaddress, port=PLCport)

    def connect(self):
        return self.client.connect()
    def disconnect(self):
        return self.client.close()
    def send(self,rgadr,val):
        rq = self.client.write_register(rgadr, val, unit=1)
    def read(self,rgadr):
        result= self.client.read_holding_registers(rgadr,1,unit=1)
        return result.getRegister(0)


# mbclient=MBclient('10.0.6.10','502')
# mbclient.connect()
#
# mbclient.send(0,1)
# mbclient.send(18,22)
# mbclient.send(20,22)
# mbclient.send(21,22)
# mbclient.send(22,22)
# print(mbclient.read(0))
def takeoff(object):
    object.busy=True
def free(object):
    object.busy=False
def wait(object):
    while(object.busy is True):
        pass
class plclist(object):
    def __init__(self):
        self.list = []
        self.busy = False
        self.init = False

    def reinit(self):
        wait(self)
        takeoff(self)
        del self.list[:]
        free(self)

    def pull(self, list_):
        # wait(self)
        # takeoff(self)
        self.list = list_
        # free(self)
        self.init = True

    def getelement(self, index_):
        # wait(self)
        # takeoff(self)
        if self.init is True:
            # free(self)
            return self.list[index_]
        else:
            # free(self)
            return 0

class PLC(object):
    def __init__(self):
        self.step=0
        self.count=0
        self.state=0
        self.cmd=0
        self.ret=0

        self.listplccoils=plclist()
        self.listplcrg16=plclist()
        # self.liststate=[]
        # for i in range(0,98):
        #     self.liststate.append(0)
        # self.listrg16=[]
        # for i in range(0,34):
        #     self.listrg16.append(0)

listlocal=[]
plc=PLC()
for i in range(0,20):
    listlocal.append(i)
    print listlocal