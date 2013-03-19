# -*- coding: utf-8 -*-
import calib,sys
r=[]
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)
#x=calib.PreProcess(devout=3)
#sys.exit(app.exec_())

#calib.PreProcess()
r=calib.PreProcess(devout=3).DevResult
a=calib.Optimizer()
a.OptimizeIterator(r,[1,1,1],20)
x=calib.TestSetGenerator.TestSetGenerator(a)
