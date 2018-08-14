# -*- coding: utf-8 -*-
from PyQt4 import uic
from PyQt4.QtCore import QThread
from app.model import Stm30Connection

Ui_MainWindow_main, QMainWindow_main = uic.loadUiType('app/mainwindow.ui')


class Main(QMainWindow_main, Ui_MainWindow_main):

    setThreshold1 = pyqtSignal(float, int)
    setThreshold2 = pyqtSignal(float, int)
    calibrateZero = pyqtSignal(float)
    calibrateEnd = pyqtSignal(float)
    setAddress = pyqtSignal(int)
    
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

        self.model = Stm30Connection()
        self.pushButtonRefreshData.clicked.connect(self.model.getState)
        self.model.stateUpdated.connect(self.refreshView)
        self.model.newModbusEvent.connect(self.addModbusEvent)
        self.model.connectToAnalyzer("/dev/ttyXRUSB0", 9600, 1)
        self.model_thread = QThread()
        self.model.moveToThread(self.model_thread)
        self.model_thread.start()

        self.show()

    def refreshView(self, data):
        self.labelAddress.setText(u"Адрес: " + "1")
        self.labelState.setText(u"Статус: " + data[3])
        self.labelConcentration.setText(
            u"Текущие показания: " + str(data[0]) + u"% НКПР")
        self.labelThreshold1.setText(u"Порог 1: " + str(data[1]) + u"% НКПР")
        self.labelThreshold2.setText(u"Порог 2: " + str(data[2]) + u"% НКПР")

    def addModbusEvent(self, event):
        self.textEditEventLog.insertPlainText(event + "\n")    
         
    def _setThreshold(self):
        block_flag = 1 if self.checkBox.isChecked() else 0
        threshold = float(self.lineEdit_2.text())
        if self.comboBox_2.currentIndex() == 0:
            self.setThreshold1.emit(threshold, block_flag)
        elif self.comboBox_2.currentIndex() == 1:
            self.setThreshold2.emit(threshold, block_flag)
    
    def _calibrate(self):
        pgs_concentrations = float(self.lineEdit_3.text())
        if self.comboBox_3.currentIndex() == 0:
            self.calibrateZero.emit(pgs_concentration)
        elif self.combobox_3.currentIndex() == 1:
            self.calibrateEnd.emit(pgs_concentration)
    
    def _setAddress(self):
        self.setAddress.emit(int(self.lineEdit_1.text()))
