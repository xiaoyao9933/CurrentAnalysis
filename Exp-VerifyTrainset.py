# -*- coding: utf-8 -*-
import calib,sys
r=[]
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)
r=calib.PreProcess(devout=1).DevResult
searcher = calib.StatusSearch.Searcher()
trainset = searcher.StatusSearch([1,1,1], 20, r)
calib.Draw3DTrainSet.Draw3dTrainSet(trainset,{0:1,1:0,2:0,3:0})# -*- coding: utf-8 -*-

