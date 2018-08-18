# -*- coding: utf-8 -*-
from PyQt4 import uic

Ui_QWidget_about, QWidget_about = uic.loadUiType('app/about.ui')


class WindowAbout(QWidget_about, Ui_QWidget_about):

    def __init__(self):
        super(WindowAbout, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)
