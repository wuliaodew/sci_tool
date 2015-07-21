__author__ = 'xianmin'
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from matplotlib.figure import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import re

import struct
import scom_ui
import serial
import time

serialdatabitarray =(serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS, serial.FIVEBITS)
serialstopbitarray =(serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)
serialcheckarray=(serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD , serial.PARITY_MARK, serial.PARITY_SPACE)


class MultiPlotCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.1)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.line1, = self.ax.plot([],[],color = 'blue')
        self.line2, = self.ax.plot([],[],color = 'green')
        self.line3, = self.ax.plot([],[],color = 'red')
        self.line4, = self.ax.plot([],[],color = 'black')
        self.ax.grid()
        self.ax.hold(False)

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.1)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.line1, = self.ax.plot([],[],color = 'blue')
        self.plotdatabuf =[]
        self.ax.grid()
        self.ax.hold(False)

    def matplot_updatabuf(self, newdata):
        if len(self.plotdatabuf) > 300:
            del self.plotdatabuf[0]

        self.plotdatabuf.append(newdata)


class Scom_UiCtl(scom_ui.Ui_MotorDebugTool):
    def __init__(self,MainWindow):
        super(scom_ui.Ui_MotorDebugTool, self).__init__()
        self.__index = 0

        self._serial = serial.Serial()
        self.setupUi(MainWindow)
        self.initmatplot()

        self.pushButton.connect(self.pushButton,QtCore.SIGNAL('clicked()'), self.openbutton_click)
        self.clrdata_action.triggered.connect(self.clreditdata)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.readData)

        #########################################################
        self.datadealinputfalg = True
        self.x1_low = 0
        self.x1_high = 0
        self.x2_low = 0
        self.x2_high = 0
        self.x3_low = 0
        self.x3_high = 0
        self.x4_low = 0
        self.x4_high = 0

    def initmatplot(self):
        self.canvas = MplCanvas()
        self.canvas2=MplCanvas()
        self.canvas3=MplCanvas()
        self.multicanvas = MultiPlotCanvas()
        self.horizontalLayout_11.addWidget(self.canvas)
        self.verticalLayout_13.addWidget(self.canvas2)
        self.verticalLayout_12.addWidget(self.canvas3)
        self.multplotLayout.addWidget(self.multicanvas)

    def clreditdata(self):
        self.textEdit_x1.clear()
        self.textEdit_x2.clear()
        self.textEdit_x3.clear()
        self.textEdit_x4.clear()
        self.datadealEdit.clear()
        self.distextEdit1.clear()
        self.distringEdit.clear()
        self.canvas.plotdatabuf = []
        self.canvas2.plotdatabuf = []
        self.canvas3.plotdatabuf = []
        self.matplot_refresh()

    def adjuseSize(self):
        newsize= QtCore.QSize(self.distextEdit1.width(),self.distext.height()-20)
        self.distextEdit1.resize(newsize)

    def hexshow(self,strargv):
        restr = ''
        slen = len(strargv)
        for i in range(slen):
            restr += hex(strargv[i])+' '
        return restr

    def readData(self):
        try:
            bytesToRead = self._serial.inWaiting()
        except:
            self.pushButton.setChecked(False)
            self.openbutton_click()
            bytesToRead = 0

        if bytesToRead > 50:
            readstr = self._serial.read(bytesToRead)
            if self.distext.currentIndex() == 2:
               pass
            else:
                if self.distext.currentIndex() == 0:
                    self.distextEdit1.append(self.hexshow(readstr))
                    self.chardeal_dis(readstr)
                else:
                    try:
                        self.distringEdit.append(readstr.decode("utf-8"))
                        self.datadeal_dis(readstr.decode("utf-8"))
                    except:
                        pass


    def chardeal_dis(self,p_str):
        for num in p_str:
            if self.checkBox_x1.isChecked() == True:
                if num >= self.x1_low and num < self.x1_high:
                    stradd = num-self.offsetx1_spin.value()
                  #  self.textEdit_x1.append(str(round(stradd,7)))
                    self.canvas.matplot_updatabuf(stradd)

        if self.datadealtab.currentIndex() == 1:
            self.matplot_refresh()
        elif self.datadealtab.currentIndex() == 2:
            self.multiplot_refresh()

    def datadeal_dis(self, p_str):
        if self.datadealinputfalg == True:
            rec_array = re.split('\n|,| |\r',p_str)
            for num in rec_array:
                try:
                    readdigital = float(num)
                except:
                    continue

                if self.checkBox_x1.isChecked() == True:
                    if readdigital >= self.x1_low and readdigital < self.x1_high:
                        stradd = readdigital-self.offsetx1_spin.value()
                        self.textEdit_x1.append(str(round(stradd,7)))
                        self.canvas.matplot_updatabuf(stradd)

                if self.checkBox_x2.isChecked() == True:
                    if readdigital >= self.x2_low and readdigital < self.x2_high:
                        stradd = (readdigital-self.offsetx2_spin.value())
                        self.textEdit_x2.append(str(round(stradd,7)))
                        self.canvas2.matplot_updatabuf(stradd)

                if self.checkBox_x3.isChecked() == True:
                    if readdigital >= self.x3_low and readdigital < self.x3_high:
                        stradd = (readdigital-self.offsetx3_spin.value())
                        self.textEdit_x3.append(str(round(stradd,7)))
                        self.canvas3.matplot_updatabuf(stradd)

                if self.checkBox_x4.isChecked() == True:
                    if readdigital >= self.x4_low and readdigital < self.x4_high:
                        self.textEdit_x4.append(str(readdigital-self.offsetx4_spin.value()))

            if self.datadealtab.currentIndex() == 1:
                self.matplot_refresh()
            elif self.datadealtab.currentIndex() == 2:
                self.multiplot_refresh()

    def matplot_refresh(self):
        if self.checkBox_x1.isChecked() == True:
            self.canvas.line1.set_xdata(range(len(self.canvas.plotdatabuf)))
            self.canvas.line1.set_ydata(self.canvas.plotdatabuf)
            self.canvas.ax.relim()
            self.canvas.ax.autoscale_view()
            self.canvas.draw()

        if self.checkBox_x2.isChecked() == True:
            self.canvas2.line1.set_xdata(range(len(self.canvas2.plotdatabuf)))
            self.canvas2.line1.set_ydata(self.canvas2.plotdatabuf)
            self.canvas2.ax.relim()
            self.canvas2.ax.autoscale_view()
            self.canvas2.draw()

        if self.checkBox_x3.isChecked() == True:
            self.canvas3.line1.set_xdata(range(len(self.canvas3.plotdatabuf)))
            self.canvas3.line1.set_ydata(self.canvas3.plotdatabuf)
            self.canvas3.ax.relim()
            self.canvas3.ax.autoscale_view()
            self.canvas3.draw()

    def multiplot_refresh(self):
        if self.checkBox_x1.isChecked() == True:
            self.multicanvas.line1.set_xdata(range(len(self.canvas.plotdatabuf)))
            self.multicanvas.line1.set_ydata(self.canvas.plotdatabuf)

        if self.checkBox_x2.isChecked() == True:
            self.multicanvas.line2.set_xdata(range(len(self.canvas2.plotdatabuf)))
            self.multicanvas.line2.set_ydata(self.canvas2.plotdatabuf)

        if self.checkBox_x3.isChecked() == True:
            self.multicanvas.line3.set_xdata(range(len(self.canvas3.plotdatabuf)))
            self.multicanvas.line3.set_ydata(self.canvas3.plotdatabuf)

        self.multicanvas.ax.relim()
        self.multicanvas.ax.autoscale_view()
        self.multicanvas.draw()


    #    self.canvas.ax.plot(range(len(self.plotdata1)),self.plotdata1, color='blue')

      #  self.canvas.flush_events()
       # self.canvas.restore_region(self.canvas.copy_from_bbox(self.canvas.ax.bbox))    # restore background
       # self.canvas.ax.draw_artist(self.canvas.ax.patch)
       # self.canvas.ax.draw_artist(self.canvas.line1)                   # redraw just the points
       # self.canvas.update()
     #   self.canvas.blit(self.canvas.ax.bbox)                # fill in the axes rectangle
      #  self.canvas.flush_events()


    def openbutton_click(self):
        status = self.pushButton.isChecked()
        if status:
            #得到串口的设置参数
            comread = int(self.comtext.text())-1
            bandrate = int(self.combobaudrate.currentText())
            databit = serialdatabitarray[self.combodatabit.currentIndex()]
            stopbit = serialstopbitarray[self.combostopbit.currentIndex()]
            checkbit = serialcheckarray[self.combocheckbit.currentIndex()]

            #打开串口
            try:
                self._serial = serial.Serial(comread)
                self._serial.baudrate = bandrate
                self._serial.bytesize = databit
                self._serial.parity = checkbit
                self._serial.stopbits = stopbit
            except (OSError, serial.SerialException):
                QtGui.QMessageBox.warning(None, '错误警告',"端口无效或者不存在", QtGui.QMessageBox.Ok)

            if self._serial.isOpen():
                self.timer.start(10)
                self.pushButton.setText("关闭")
                self.combobaudrate.setEnabled(False)
                self.combocheckbit.setEnabled(False)
                self.combodatabit.setEnabled(False)
                self.combostopbit.setEnabled(False)
                self.comtext.setEnabled(False)
                self.IQBox.setEnabled(False)
                self.datadealmenu_open()
            else:
                self.pushButton.setChecked(False)
        else:
            self._serial.close()
            self.timer.stop()
            self.pushButton.setText("打开")
            self.combobaudrate.setEnabled(True)
            self.combocheckbit.setEnabled(True)
            self.combodatabit.setEnabled(True)
            self.combostopbit.setEnabled(True)
            self.comtext.setEnabled(True)
            self.IQBox.setEnabled(True)
            self.datadealmenu_close()
            self.datadealinputfalg = True

    def datadealmenu_open(self):
        self.textEdit_x1.clear()
        self.textEdit_x2.clear()
        self.textEdit_x3.clear()
        self.textEdit_x4.clear()

        if self.checkBox_x1.isChecked() == True:
            try:
                self.x1_low = float(self.lowx1edit.text())
                self.x1_high = float(self.highx1edit.text())
            except :
                self.textEdit_x1.setText('the input number is invalid')
                self.datadealinputfalg = False

            if self.x1_high < self.x1_low:
                self.datadealinputfalg = False
                self.textEdit_x1.setText('the input number is invalid')

        if self.checkBox_x2.isChecked() == True:
            try:
                self.x2_low = float(self.lowx2edit.text())
                self.x2_high = float(self.highx2edit.text())
            except :
                self.datadealinputfalg = False
                self.textEdit_x2.setText('the input number is invalid')

            if self.x2_high < self.x2_low:
                self.datadealinputfalg = False
                self.textEdit_x2.setText('the input number is invalid')



        if self.checkBox_x3.isChecked() == True:
            try:
                self.x3_low = float(self.lowx3edit.text())
                self.x3_high = float(self.highx3edit.text())
            except :
                self.datadealinputfalg = False
                self.textEdit_x3.setText('the input number is invalid')

            if self.x3_high < self.x3_low:
                self.datadealinputfalg = False
                self.textEdit_x3.setText('the input number is invalid')

        if self.checkBox_x4.isChecked() == True:
            try:
                self.x4_low = float(self.lowx4edit.text())
                self.x4_high = float(self.highx4edit.text())
            except :
                self.datadealinputfalg = False
                self.textEdit_x4.setText('the input number is invalid')

            if self.x4_high < self.x4_low:
                self.datadealinputfalg = False
                self.textEdit_x4.setText('the input number is invalid')

        self.lowx1edit.setEnabled(False)
        self.highx1edit.setEnabled(False)
        self.offsetx1_spin.setEnabled(False)
        self.lowx2edit.setEnabled(False)
        self.highx2edit.setEnabled(False)
        self.offsetx2_spin.setEnabled(False)
        self.lowx3edit.setEnabled(False)
        self.highx3edit.setEnabled(False)
        self.offsetx3_spin.setEnabled(False)

        self.lowx4edit.setEnabled(False)
        self.highx4edit.setEnabled(False)
        self.offsetx4_spin.setEnabled(False)

        self.checkBox_x1.setEnabled(False)
        self.checkBox_x2.setEnabled(False)
        self.checkBox_x3.setEnabled(False)
        self.checkBox_x4.setEnabled(False)


    def datadealmenu_close(self):
        self.lowx1edit.setEnabled(True)
        self.highx1edit.setEnabled(True)
        self.lowx2edit.setEnabled(True)
        self.highx2edit.setEnabled(True)
        self.lowx3edit.setEnabled(True)
        self.highx3edit.setEnabled(True)
        self.lowx4edit.setEnabled(True)
        self.highx4edit.setEnabled(True)
        self.checkBox_x1.setEnabled(True)
        self.checkBox_x2.setEnabled(True)
        self.checkBox_x3.setEnabled(True)
        self.checkBox_x4.setEnabled(True)
        self.offsetx1_spin.setEnabled(True)
        self.offsetx2_spin.setEnabled(True)
        self.offsetx3_spin.setEnabled(True)
        self.offsetx4_spin.setEnabled(True)

