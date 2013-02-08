# -*- coding: utf-8 -*-
import calib
r=[]
for x in range(0,3):
    x=calib.PreProcess(devout=3)
    r+=x.DevResult
a=calib.Optimizer()
a.OptimizeIterator(r,[1,1,1],10)