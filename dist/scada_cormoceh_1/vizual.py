# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QObject, pyqtSignal,QThread, pyqtSlot
DEBUGFLAG=False

class obj(QtCore.QObject):
    qtobj = 0
    movie = ''
    numbit = 0
    imgtrue = ''
    imgfalse = ''
    state = False
    instate = False

    def __init__(self, object, imgfalse, imgtrue, gif):
        self.imgfalse = imgfalse
        self.imgtrue = imgtrue
        self.qtobj = object
        if gif is not '':
            self.movie = QtGui.QMovie(gif)
        if DEBUGFLAG is True:
            self.qtobj.mousePressEvent = self.onclicked_

    def onclicked_(self, event):
        if self.state is False:
            self.switch(1)
        else:
            self.switch(0)
    def start(self):
        if self.movie is not '':
            self.qtobj.setMovie(self.movie)
            self.movie.start()
        else:
            self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgtrue))
        self.state = True

    def stop(self):
        self.qtobj.setPixmap(QtGui.QPixmap("./" + self.imgfalse))
        self.state = False

    def switch(self, bit):
        if bit is 1:
            if self.state is False:
                self.start()
                #print("start " + str(bit))
        else:
            if self.state is True:
                self.stop()
                #print("stop "+str(bit))

class vizual2level(QtCore.QObject):# визулизация шиберов- по состоянию концевиков
    finished = pyqtSignal()
    singal_= pyqtSignal()
    _isRunning=False
    @pyqtSlot()
    def process(self):
        while  self._isRunning is True:
            self.singal_.emit()
            for i in range(0,500):
                pass
            # print 'FINISHED'
        # self.finished.emit()
    def stop(self):
        self._isRunning = False
