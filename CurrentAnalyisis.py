# -*- coding: utf-8 -*-
import calib,sys
r=[]
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)
#x=calib.PreProcess(devout=3)
#sys.exit(app.exec_())


r=calib.PreProcess(devout=3).DevResult
if len(r) != 0 :
    a=calib.Optimizer()
    a.OptimizeIterator(r,[1,1,1],10)
x=calib.TestSetGenerator.TestSetGenerator()