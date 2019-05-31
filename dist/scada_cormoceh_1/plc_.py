# coding: utf-8
from pyModbusTCP.client import ModbusClient
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
            print str(datetime.datetime.now())+('!!!!!!!!!!!! No connection !!!!!!!!!!!!!!!')
            self.disconnected = True
            self.connect()
        else:
            # print "Ok connection"
            if self.disconnected == True:
                self.disconnected = False
                logging.debug(' Connection return')
                print str(datetime.datetime.now()) + (' Connection return')
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
                print str(datetime.datetime.now())+"--Ошибка подключения "+ str(err)
                logging.error(traceback.format_exc())

        # print self.client.__sock
        logging.debug(' Connection status: '+str(self.okconnection))
        # logging.debug(self.client.mysocket)
        return self.okconnection

    def disconnect(self):
        return self.client.close()

    def send(self, rgadr, val):
        if DEBUGFLAG==False:
            self.checkconnecttcp()
            is_Ok=None

            # rq = self.client.write_register(rgadr, val, unit=1)
            # write_single_register(reg_addr, reg_value)[source]
            while(plcglobal.pausesend==True):
                pass
            plcglobal.pauseread = True
            while(is_Ok!=True):
                try:
                    wait(self)
                    takeover(self)
                    is_Ok=self.client.write_single_register(rgadr, val)
                except Exception as err:
                    print  str(datetime.datetime.now())+"--Ошибка записи регистра с номером : " + str(rgadr) + " Ошибка:"+str(err)
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
            logging.debug(err)
            print u"Error deleting element from plclist "+err
            logging.error(traceback.format_exc())
    def has(self,elem):
        if elem in self.list:
            return True
        else:
            return False
class equipment(object):
    def __init__(self,staterg,indexbit):
        self.rg = staterg
        self.bit = indexbit
        self.state = 0

    def chkstate(self):
        pass


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
        self.selectkormnumbanka = []
        self.nowkormnumbanka = 0
        self.masloneed = 0
        self.dopdobavka = 0
        self.step = 0
        self.zakaz = plclist(10)
        self.listzernoneed = plclist(10)
        self.listdobavkaneed = plclist(6)
        self.receptlist = {}
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
class commands(object):
    def __init__(self, cmd, name, flag,needchk):
        self.timeout = 0
        self.cmd = cmd
        self.flag = flag # index bit in dbstatus register
        self.name = name
        self.exe_success = False
        self.exe_run = False
        self.exe_err = False
        self.controlexec = needchk
    def execute(self,timeout):
        if not plcglobal.recept.stages.has(self.name):
            self.timeout = timeout #timeout
            self.exe_run = True
            self.exe_success = False
            plcglobal.send_cmd(self.cmd)
            plcglobal.textout.append(u"Отправлена команда " + self.name)
            logging.debug(u"Отправлена команда " + self.name)
            print str(datetime.datetime.now())+(u"Отправлена команда " + self.name)
        else:
            plcglobal.textout.append(u"Отменена избыточная отправка команды" + self.name)
            logging.debug(u"Отменена избыточная отправка команды " + self.name)
            print str(datetime.datetime.now()) + (u"Отменена избыточная отправка команды " + self.name)
    def checkexecute(self):
        if self.exe_run == True:
            if getbit(plcglobal.status,self.flag)==0:
                self.exe_success = True
                self.exe_run = False
                plcglobal.textout.append(u"Команда " + self.name + u" выполнена успешно")
                logging.debug(u"Команда " + self.name + u" выполнена успешно")
                print str(datetime.datetime.now()) + (u"Команда " + self.name + u" выполнена успешно")
                self.register()
                return True
            else:
                if self.timeout>0:
                    self.timeout=self.timeout-1
                    self.execute(self.timeout)
                else:
                    self.exe_err = True
                    self.exe_run = False # останавливаем попытки отправить команду
                    plcglobal.textout.append(u"Команда " + self.name+u" не была выполнена, ОСТАНОВ  замешивания")
                    logging.debug(u"Команда " + self.name+u" не была выполнена, ОСТАНОВ  замешивания")
                    print str(datetime.datetime.now()) + (u"Команда " + self.name+u" не была выполнена, ОСТАНОВ  замешивания")
                return False
        else:
            return True
    def register(self):
        plcglobal.recept.stages.add(self.name)
    def clear(self):
        plcglobal.recept.stages.sub(self.name)

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
        self.recept.receptlist = loadrecepts()
        self.status = 0
        self.tick = False
        self.kormbankauplevel=[88,90,92,94,96,98]
        self.chastotaves1=0
        self.chastotaves2=0
        self.shnekszerno= range(10)
        self.shneksdobavka = range(6)
        self.shnekssupport = range(5)
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
        self.errors = {ERRORWEIGHT1: "Error weight1", ERRORWEIGHT2: "Error weight2",ERRORWEIGHT3:"Error weight3",ERRORLINEK:"Error LINEK" ,ERRORPERKLAPAN:"Error PerKlapan", ERRORMIXER:"Error Mixer",ERRORLINE1:"Error Line1",ERRORLINE2:"Error Line2", ERRORAWILA:"Error Awila",
                       ERRORMIXERNOTOPEN: "Error mixer not open", ERRORMIXERNOTUNLOAD:"Error mixer not unload", ERROREXECUTECMD:"Command not execute" }
        self.errordetails = {ERRORWEIGHT1: u"Слишком большое значение в заказе весы1", ERRORWEIGHT2: u"Слишком большое значение в заказе весы2",ERRORWEIGHT3:u"Слишком большое значение в заказе весы3",
                             ERRORLINEK:u"получена ошибка от ПЛК управляющего норией, возможно сбой связи, проверьте соединение и удостоверьтесь, что плк Нории переведен в Режим АВТО" ,ERRORPERKLAPAN:u"Слишком долго переключается перекидной клапан(больше минуты)",
                             ERRORMIXER:u"Возмозможно выключено тепловое реле",ERRORLINE1:u"Возмозможно выключено тепловое реле двигателя ",ERRORLINE2:u"Возмозможно выключено тепловое реле двигателя",
                             ERRORAWILA :u" Ошибка шкафа управления Awila, возможны проблемы с частотниками, также возможы проблемы с автом выключателями", ERRORMIXERNOTOPEN:u"Смеситель не будет ывгружаться, пока бункер под смесителем не опустошится",
                             ERRORMIXERNOTUNLOAD:u"Смечитель не выгружался, необходимо выгрузить смеситель перед разгрузкой весов",  ERROREXECUTECMD:u"Команда не исполнена" }
        comms =[]
        comms.append(commands(COMMAND_VES12_START,u"COMMAND_VES12_START",VES2READYLOAD,True))
        comms.append(commands(COMMAND_VES3_START, u"COMMAND_VES3_START", VES3READYLOAD, True))
        comms.append(commands(COMMAND_VES2_UNLOAD, u"COMMAND_VES2_UNLOAD", VES2READYUNLOAD, True))
        comms.append(commands(COMMAND_VES3_UNLOAD, u"COMMAND_VES3_UNLOAD", VES3READYUNLOAD, True))
        comms.append(commands(COMMAND_MIXER_UNLOAD, u"COMMAND_MIXER_UNLOAD", MIXERREADYUNLOAD, True))
        comms.append(commands(COMMAND_OIL_START, u"COMMAND_OIL_START", MASLOREADY, False))
        self.commands = {COMMAND_VES12_START:comms[0],COMMAND_VES3_START:comms[1],COMMAND_VES2_UNLOAD:comms[2],COMMAND_VES3_UNLOAD:comms[3],COMMAND_MIXER_UNLOAD:comms[4], COMMAND_OIL_START:comms[5]}


        self.textout = []
        self.readytostart = True
        self.timerenable = False
        self.timer = 0 #seconds
        self.pause = False

    def starttimerecept(self):
        logging.debug(u"Включение таймера замеса")
        self.timer = 0
        self.timerenable = True
    def stoptimerrecept(self):
        logging.debug(u"Отключение таймера замеса")
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
        while (True):
            # answer = mbclient.read(0) & 0x00FF
            # delay(10000)
            print str(datetime.datetime.now())+u"Ожидание готовности ПЛК к получению команды"
            logging.debug(u"Ожидание готовности ПЛК к получению команды")
            answer = plcglobal.cmd & 0x00FF
            time.sleep(0.01)
            if answer == 0:
                logging.debug(u"ПЛК готов")
                print str(datetime.datetime.now()) + u"ПЛК готов"
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