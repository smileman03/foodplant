import sys
from PyQt4 import QtCore, QtGui, uic
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from PyQt4.QtCore import QThread
import time
import threading
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtCore import QTimer
qtCreatorFile = "design.ui"  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    trigger = pyqtSignal()
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.startbtn.clicked.connect(self.startbtnclk)
        self.stopbtn.clicked.connect(self.stopbtnclk)
        #self.drobilka1.mousePressEvent = self.startanim
        self.client=0
        self.goreadsensor=False
        self.trigger.connect(self.readsensor)

        self.worker = WorkerObject()
        
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        # self.mpotok = TThread()
        class obj(QtCore.QObject):
            qtobj=0
            movie=''
            numbit=0
            imgtrue=''
            imgfalse=''
            state=False
            instate=False

            def __init__(self,object,imgfalse,imgtrue,gif):

                self.imgfalse=imgfalse
                self.imgtrue=imgtrue
                self.qtobj=object
                self.trigger=pyqtSignal()

                #print self.signal
               # QtCore.QObject.connect(self.potok, QtCore.SIGNAL("PotokValue(PyQt_PyObject)"+self.qtobject), self.qtobject)
                if gif is not '':
                    self.movie=QtGui.QMovie(gif)
            def start(self):
                if self.movie is not '':
                    self.qtobj.setMovie(self.movie)
                    self.movie.start()
                else:
                    self.qtobj.setPixmap(QtGui.QPixmap("./"+self.imgtrue))
                self.state=True
            def stop(self):
                self.qtobj.setPixmap(QtGui.QPixmap("./"+self.imgfalse))
                self.state=False
            def switch(self,bit):
                if bit is True:
                    if self.state is False:
                        self.start()
                else:
                    if self.state is True:
                        self.stop()
        # self.movie = QtGui.QMovie("drobilka.gif")
        # self.drobilka1.setMovie(self.movie)
        self.movies=[]

        self.movies.insert(0,obj(self.dobavkisilos1up,"statusfalse.png","statustrue.png",""))
        self.movies.insert(1, obj(self.dobavkisilos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(2, obj(self.silos1dobavkaopen, "statusminifalse.png","", "statusminitrue.png"))
        self.movies.insert(3, obj(self.silos1dobavkaclose, "statusminifalse.png", "", "statusminitrue.png"))
        #self.movies.insert(100, obj(self.silos1dobavkashiber, "silosshiberclose.png", "", "silosshiberopen.png"))
        # self.movies.insert(4, obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", ""))
        self.movies.insert(4, obj(self.dobavkisilos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(5, obj(self.dobavkisilos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(6, obj(self.silos2dobavkaopen, "statusminifalse.png",  "statusminitrue.png",''))
        self.movies.insert(7, obj(self.silos2dobavkaclose, "statusminifalse.png",  "statusminitrue.png",''))
        self.movies.insert(8, obj(self.dobavkisilos3up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(9, obj(self.dobavkisilos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(10, obj(self.silos3dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(11, obj(self.silos3dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(12, obj(self.dobavkisilos4up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(13, obj(self.dobavkisilos4do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(14, obj(self.silos4dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(15, obj(self.silos4dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))

        self.movies.insert(16, obj(self.dobavkisilos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(17, obj(self.dobavkisilos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(18, obj(self.silos5dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(19, obj(self.silos5dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(20, obj(self.dobavkisilos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(21, obj(self.dobavkisilos6do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(22, obj(self.silos6dobavkaopen, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(23, obj(self.silos6dobavkaclose, "statusminifalse.png", "statusminitrue.png", ''))

        self.movies.insert(24, obj(self.flex1, "flex1stop.png", "flex1run.png", ''))
        self.movies.insert(25, obj(self.flex2, "flex2stop.png", "flex2run.png", ''))
        self.movies.insert(26, obj(self.flex3, "flex3stop.png", "flex3run.png", ''))
        self.movies.insert(27, obj(self.flex4, "flex4stop.png", "flex4run.png", ''))
        self.movies.insert(28, obj(self.flex5, "flex5stop.png", "flex5run.png", ''))
        self.movies.insert(29, obj(self.flex6, "flex6stop.png", "flex6run.png", ''))
        self.movies.insert(30, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv
        self.movies.insert(31, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv


        self.movies.insert(32, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # button auto
        self.movies.insert(33, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # button ruchno
        self.movies.insert(34, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # button stop
        self.movies.insert(35, obj(self.flexload, "flexloadstop.png", "flexloadrun.png", ''))
        self.movies.insert(36, obj(self.bunkerloaddo, "statusminifalse.png", "statusminitrue.png", ''))
        self.movies.insert(37, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # open shiber vesi knopka
        self.movies.insert(38, obj(self.ves3sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(39, obj(self.ves3sensclose, "statusfalse.png", "statustrue.png", ''))

        self.movies.insert(40, obj(self.mixershiber, "mixershiberclose.png", "mixershiberopen.png", ''))
        self.movies.insert(41, obj(self.mixersensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(42, obj(self.mixersensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(43, obj(self.mixer, "mixerstop.png", '', "mixerbegin.gif"))
        self.movies.insert(44, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # mixer2
        self.movies.insert(45, obj(self.mixerbunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(46, obj(self.mixershnek1, "shnek_hor_stop.gif", "", "shnek_hor_begin.gif"))
        self.movies.insert(47, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv

        self.movies.insert(48, obj(self.ves1sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(49, obj(self.ves1sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(50, obj(self.ves2sensopen, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(51, obj(self.ves2sensclose, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(52, obj(self.ves1bunkersens, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(53, obj(self.ves2bunkersens1, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(54, obj(self.ves2bunkersens2, "statusfalse.png", "statustrue.png", ''))
        self.movies.insert(55, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv

        self.movies.insert(56, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv
        self.movies.insert(57, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv
        self.movies.insert(58, obj(self.zernoshnek3, "shnek3zernostop.png", "shnek3zernorun.png", ""))
        self.movies.insert(59, obj(self.zernoshnek4, "shnek4zernostop.png", "shnek4zernorun.png", ""))
        self.movies.insert(60, obj(self.zernoshnek5, "shnek5zernostop.png", "shnek5zernorun.png", ""))
        self.movies.insert(61, obj(self.zernoshnek6, "shnek6zernostop.png", "shnek6zernorun.png", ""))
        self.movies.insert(62, obj(self.zernoshnek7, "shnek7zernostop.png", "shnek7zernorun.png", ""))
        self.movies.insert(63, obj(self.zernoshnek8, "shnek8zernostop.png", "shnek8zernorun.png", ""))

        self.movies.insert(64, obj(self.zernoshnek9, "shnek9zernostop.png", "shnek9zernorun.png", ""))
        self.movies.insert(65, obj(self.zernoshnek10, "shnek10zernostop.png", "shnek10zernorun.png", ""))
        self.movies.insert(66, obj(self.drobilka1, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(67, obj(self.drobilka2, "drobilka_off.png", "", "drobilkabegin"))
        self.movies.insert(68, obj(self.ves2shnek, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(69, obj(self.ves1shnek1, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(70, obj(self.ves1shnek2, "shnek_nakl_stop.gif", "", "shnek_nakl_begin.gif"))
        self.movies.insert(71, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) # reserv

        self.movies.insert(72, obj(self.klapan1, "klapan1false.png","klapan1true.png",""))
        self.movies.insert(73, obj(self.klapan2, "klapan2false.gif", "", "klapan2true.gif"))
        self.movies.insert(74, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) #stop
        self.movies.insert(75, obj(self.noria, "noriastop.png", "", "noriabegin.gif"))
        self.movies.insert(76, obj(self.terminator1, "terminator1stop.png", "", "terminator1.gif"))
        self.movies.insert(77, obj(self.terminator2, "terminator2stop.png", "", "terminator2.gif"))
        self.movies.insert(78, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) #reserve
        self.movies.insert(79, obj(self.silos_zerno, "siloszerno.png","siloszerno.png", "")) #reserve

        self.movies.insert(80, obj(self.silos1shiberopen, "statusminifalse.png","statusminitrue.png", ""))
        self.movies.insert(81, obj(self.silos1shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(82, obj(self.silos2shiberopen, "statusminifalse.png","statusminitrue.png", ""))
        self.movies.insert(83, obj(self.silos2shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(84, obj(self.silos4shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(85, obj(self.silos4shiberclose, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(86, obj(self.silos5shiberopen, "statusminifalse.png", "statusminitrue.png", ""))
        self.movies.insert(87, obj(self.silos5shiberclose, "statusminifalse.png", "statusminitrue.png", ""))

        self.movies.insert(88, obj(self.silos1up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(89, obj(self.silos1do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(90, obj(self.silos2up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(91, obj(self.silos2do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(92, obj(self.silos3up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(93, obj(self.silos3do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(94, obj(self.silos4up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(95, obj(self.silos4do, "statusfalse.png", "statustrue.png", ""))

        self.movies.insert(95, obj(self.silos5up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(96, obj(self.silos5do, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(97, obj(self.silos6up, "statusfalse.png", "statustrue.png", ""))
        self.movies.insert(98, obj(self.silos6do, "statusfalse.png", "statustrue.png", ""))

        # self.mpotok = self.TThread()
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.readsensor)
        self.Go=False
    # class TThread(QtCore.QThread):
    #     def __init__(self):
    #         QtCore.QThread.__init__(self,obj)
    #         self.obj=obj
    #     def run(self):
    #         self.obj
    def readsensor(self):
        # self.timer.stop()
        for i in range(0, 98):
            incoil = self.client.read_coils(i + 112, 1, unit=0x01)
            self.movies[i].switch(incoil.bits[0])
            # else:
            # self.movies[i].stop()
            print "reading"

    # def readbits(self):
    #     for i in range(0, 98):
    #         incoil = self.client.read_coils(i + 112, 1, unit=0x01)
    #         self.movies[i].switch(incoil.bits[0])
    #         print "reading"

    def connectclient(self):
        self.client = ModbusClient('10.0.6.98', port=502)
        self.client.connect()

    def stopbtnclk(self):
         #self.movies[24].stop()
        #self.connectclient
         self.goreadsensor = False
         self.Go=False
         # self.timer.stop()
    def startbtnclk(self):
        self.connectclient()
        self.Go=True

        #self.mpotok.start()
        #self.goreadsensor=True
        # self.threadreadbits.run()
      #  self.timer.start(1000)
    # def run(self):
    #     while self.Go is True:
    #         for i in range(0, 98):
    #             incoil = self.client.read_coils(i + 112, 1, unit=0x01)
    #             self.movies[i].switch(incoil.bits[0])
    #             # else:
    #             # self.movies[i].stop()
    #             print "reading"
    #         time.sleep(1000)



def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MyApp()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == "__main__":
    main()
    # app = QtGui.QApplication(sys.argv)
    # window = MyApp()
    # window.show()
    # sys.exit(app.exec_())