# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scom_main.py'
#
# Created: Sun Jul 06 22:29:41 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtCore, QtGui
from scom_ui import *
from scom_class import *
import sys


app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = Scom_UiCtl(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
