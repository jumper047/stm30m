# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui

from app.mainwindow import Main

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_form = Main()
    sys.exit(app.exec_())
