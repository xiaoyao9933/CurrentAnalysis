# -*- coding: utf-8 -*-
import calib,sys
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)
#x=calib.PreProcess(devout=3)
#sys.exit(app.exec_())

#s=calib.PreProcess()
r=calib.PreProcess(devout=3)
s= r.DevResult
a=calib.Optimizer()
a.OptimizeIterator(s,[1,1,1,1],20)
x=calib.TestSetGenerator.TestSetGenerator(a)
#s=calib.PreProcess()
#import matplotlib.pyplot as plt
#
#plt.ion()
#plt.figure(1)
#for x in s.ra:
#    plt.clf()a
#    plt.plot(range(0, len(x)), x)
#    plt.draw()