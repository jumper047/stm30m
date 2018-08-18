# -*- coding: utf-8 -*-
from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal

Ui_QWidget_settings, QWidget_settings = uic.loadUiType('app/settings.ui')


class WindowSettings(QWidget_settings, Ui_QWidget_settings):

    settingsUpdated = pyqtSignal()

    def __init__(self):
        super(WindowSettings, self).__init__()
        self.setupUi(self)

        self.comPort = "/dev/ttyXRUSB0"
        self.comSpeed = 9600
        self.analyzerAddress = 1
        self.pollingAnalyzer = False

    def accept(self):
        changed = False
        if self.comPort != self.lineEditCom.text():
            self.comPort = self.lineEditCom.text()
            changed = True
        if self.comSpeed != self.lineEditSpeed.text():
            self.comSpeed = int(self.lineEditSpeed.text())
            changed = True
        if self.analyzerAddress != self.lineEditAddress.text():
            self.analyzerAddress = int(self.lineEditAddress.text())
            changed = True
        if self.checkBox.isChecked() != self.pollingAnalyzer:
            self.pollingAnalyzer = self.checkBox.isChecked()
            changed = True
        if changed:
            self.settingsUpdated.emit()
        super(WindowSettings, self).accept()
