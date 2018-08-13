# -*- coding: utf-8 -*-
from PyQt4 import uic
from PyQt4.QtCore import QThread
from app.model import Stm30Connection

Ui_MainWindow_main, QMainWindow_main = uic.loadUiType('app/mainwindow.ui')


class Main(QMainWindow_main, Ui_MainWindow_main):

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
