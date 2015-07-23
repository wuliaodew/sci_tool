# -*- coding: utf-8 -*-
__author__ = 'wuliaodew'
__name__ = '__main__'

from PyQt4 import QtCore, QtGui
from matplotlib.figure import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import re

import sys, struct, sci_tool, serial, time, threading


#数据位
SERIAL_DATABIT_ARRAY = (serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS, serial.FIVEBITS)
#停止位
SERIAL_STOPBIT_ARRAY = (serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)
#校验位
SERIAL_CHECKBIT_ARRAY = (serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD , serial.PARITY_MARK, serial.PARITY_SPACE)


class SciSignalClass( QtCore.QObject):
    SciReceive =  QtCore.pyqtSignal()

class Sci_UiCtl(sci_tool.Ui_MainWindow):
    def __init__(self,MainWindow):
        super(sci_tool.Ui_MainWindow, self).__init__()
        self.__index = 0
        self.setupUi(MainWindow)#display sci tool menu

        self.portstatus_flag = False
        self._serial = serial.Serial()#init serial class
        self.sciopenButton.connect(self.sciopenButton, QtCore.SIGNAL('clicked()'), self.SciOpenButton_Click)#connect button click func
        self.clrcontentbutton.connect(self.clrcontentbutton, QtCore.SIGNAL('clicked()'), self.ClrButtonProcess)
        self.test = 0
        self.recstr = str

        self.scirec_signal = SciSignalClass()#添加一个串口数据接收成功信号
        self.scirec_signal.SciReceive.connect(self.SciWinReFresh)#产生信号连接槽
      #  self.scirec_signal.connect(self.scirec_signal, QtCore.SIGNAL('SCI RECEIVE'), self.SciWinReFresh())

        try:
            self.scithread = threading.Thread(target=self.SciReadData)
            self.scithread.setDaemon(True)
            self.scithread.start()
        except:
             QtGui.QMessageBox.warning(None, '错误警告',"SCI读取线程未创建", QtGui.QMessageBox.Ok)
             sys.exit()#创建进程异常，结束程序

    def SciOpenButton_Click(self):
         clickstatus = self.sciopenButton.isChecked()
         if clickstatus:
                #得到串口的设置参数
            comread = int(self.portcomtext.text())-1
            bandrate = int(self.baudratecombo.currentText())
            databit = SERIAL_DATABIT_ARRAY[self.databitcombo.currentIndex()]
            stopbit = SERIAL_STOPBIT_ARRAY[self.stopbitcombo.currentIndex()]
            checkbit = SERIAL_CHECKBIT_ARRAY[self.checkbitcombo.currentIndex()]

            #打开串口
            try:
                self._serial = serial.Serial(comread)
                self._serial.baudrate = bandrate
                self._serial.bytesize = databit
                self._serial.parity = checkbit
                self._serial.stopbits = stopbit
            except (OSError, serial.SerialException):
                QtGui.QMessageBox.warning(None, '端口警告',"端口无效或者不存在", QtGui.QMessageBox.Ok)

            if self._serial.isOpen():
                self.sciopenButton.setText("关闭")
                self.baudratecombo.setEnabled(False)
                self.checkbitcombo.setEnabled(False)
                self.databitcombo.setEnabled(False)
                self.stopbitcombo.setEnabled(False)
                self.portcomtext.setEnabled(False)
                self.portstatus_flag = True
            else:
                self.sciopenButton.setChecked(False)
         else:
            self._serial.close()
            self.sciopenButton.setText("打开")
            self.baudratecombo.setEnabled(True)
            self.stopbitcombo.setEnabled(True)
            self.databitcombo.setEnabled(True)
            self.checkbitcombo.setEnabled(True)
            self.portcomtext.setEnabled(True)
            self.portstatus_flag = False


    def ClrButtonProcess(self):
        if self.distext.currentIndex() == 0:
            self.dishex.clear()
        elif self.distext.currentIndex() == 1:
            self.distring.clear()
        else:
            self.disprotocol.clear()


    def HexShow(self,strargv):#转换陈十六进制格式显示
        restr = ''
        slen = len(strargv)
        for i in range(slen):
            restr += hex(strargv[i])+' '
        return restr

    @QtCore.pyqtSlot()#串口数据刷新槽
    def SciWinReFresh(self):
        if self.distext.currentIndex() == 0:
            self.dishex.appendPlainText(self.HexShow(self.recstr))#把数据按十六进制显示
        elif self.distext.currentIndex() == 1:
            self.distring.appendPlainText(self.recstr.decode("utf-8"))#数据按字符格式显示
        else:
            pass

###############################################
#数据接收线程
    def SciReadData(self):#deal sci data
        while True:
            if self.portstatus_flag == True:
                try:
                    bytesToRead = self._serial.inWaiting()
                except:
                    self.sciopenButton.setChecked(False)#出现异常，则关闭串口
                    self.SciOpenButton_Click()
                    bytesToRead = 0

                if bytesToRead > 0:
                    self.recstr = self._serial.read(bytesToRead)#读取苏三说
                    self.scirec_signal.SciReceive.emit()#发送接收数据的信号

                time.sleep(0.02)#20ms处理一次数据
            else:
                time.sleep(1)#位打开则没1s出来判断一次



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Sci_UiCtl(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())