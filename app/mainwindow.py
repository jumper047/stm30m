# -*- coding: utf-8 -*-
from PyQt4 import uic
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot
from app.model import Stm30Connection
from app.about import WindowAbout
from app.settings import WindowSettings

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

        self.about = WindowAbout()
        self.actionAbout.triggered.connect(self.about.show)

        self.settings = WindowSettings()
        self.actionSettings.triggered.connect(self.settings.show)
        self.settings.settingsUpdated.connect(self.reconnect)

        self.actionExit.triggered.connect(self.close)

        self.model = Stm30Connection()
        self.pushButtonRefreshData.clicked.connect(self.model.getState)
        self.model.stateUpdated.connect(self.refreshView)
        self.model.newModbusEvent.connect(self.addModbusEvent)
        self.model_thread = QThread()
        self.model.moveToThread(self.model_thread)
        self.model.connectToAnalyzer(
            self.settings.comPort, self.settings.comSpeed, self.settings.analyzerAddress)
        self.pushButtonAddress.clicked.connect(self._setAddress)
        self.pushButtonThreshold.clicked.connect(self._setThreshold)
        self.pushButtonCalibrate.clicked.connect(self._calibrate)
        self.setThreshold1.connect(self.model.setThreshold1)
        self.setThreshold2.connect(self.model.setThreshold2)
        self.calibrateZero.connect(self.model.calibrateZero)
        self.calibrateEnd.connect(self.model.calibrateEnd)
        self.setAddress.connect(self.model.setAddress)
        self.model_thread.start()

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.model.getState)
        if self.settings.pollingAnalyzer:
            self.updateTimer.start(20000)

        self.show()

    @pyqtSlot()
    def reconnect(self):
        self.model.disconnect()
        self.model.connectToAnalyzer(
            self.settings.comPort, self.settings.comSpeed, self.settings.analyzerAddress)
        if self.settings.pollingAnalyzer:
            self.updateTimer.start(20000)
        else:
            self.updateTimer.stop()

    @pyqtSlot(object)
    def refreshView(self, data):
        self.labelAddress.setText(
            u"Адрес: " + str(self.settings.analyzerAddress))
        self.labelState.setText(u"Статус: " + data[3])
        self.labelConcentration.setText(
            u"Текущие показания: " + str(data[0]) + u"% НКПР")
        self.labelThreshold1.setText(
            u"Порог 1: " + str(data[1]) + u"% НКПР")
        self.labelThreshold2.setText(
            u"Порог 2: " + str(data[2]) + u"% НКПР")

    @pyqtSlot(str, int)
    def addModbusEvent(self, event, event_type):
        event_types = {"r": u"red", "b": u"black", "g": u"green"}
        self.textEditEventLog.insertHtml(
            u"<font color=\"{0}\">{1}</font>\n".format(event_types[str(event_type)], event))
        self.textEditEventLog.insertPlainText("\n")

    def _setThreshold(self):
        block_flag = 1 if self.checkBox.isChecked() else 0
        threshold = float(self.lineEditThreshold.text())
        if self.comboBoxThreshold.currentIndex() == 0:
            self.setThreshold1.emit(threshold, block_flag)
        elif self.comboBoxThreshold.currentIndex() == 1:
            self.setThreshold2.emit(threshold, block_flag)

    def _calibrate(self):
        pgs_concentrations = float(self.lineEditPGS.text())
        if self.comboBoxPGS.currentIndex() == 0:
            self.calibrateZero.emit(pgs_concentration)
        elif self.comboboxPGS.currentIndex() == 1:
            self.calibrateEnd.emit(pgs_concentration)

    def _setAddress(self):
        self.setAddress.emit(int(self.lineEditAddress.text()))
