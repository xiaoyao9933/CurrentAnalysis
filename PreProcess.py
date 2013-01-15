# -*- coding: utf-8 -*-
##This file reads the data from two files and Split the current with Voltage Zero points.
import numpy as np
from PyQt4 import QtGui
import sys,cPickle

global c,pid,state
global tem_c,fsample
def DataSplit(a,begin,end):
    tem_c.append(a[begin:end])
    return
def CutToTheSame(temp_c):
    length=999999
    for item in temp_c:
      if len(item)<length:
        length=len(item)
    for item in temp_c:
      c.append(item[0:length-1])
    return
def FFTTrans(x):
    length=int((int(fsample/50)-20)/2)
    for item in x:
      #f.append([np.real(ele)/len(item)*2 for ele in np.fft.fft(item)[1:length]]+\
      #[np.imag(ele)/len(item)*2 for ele in np.fft.fft(item)[1:length]])
      f.append([np.real(ele)/len(item)*2 for ele in np.fft.fft(item)[1:11:2]]+\
      [np.imag(ele)/len(item)*2 for ele in np.fft.fft(item)[1:11:2]])
    return
  

      
if __name__ == '__main__':
    app=QtGui.QApplication(sys.argv)
    workdir=QtGui.QFileDialog.getExistingDirectory(directory="./Data")
    fp = open(workdir+"/A.dat")
    a = []      #the current
    tem_c=[]        #The splited current
    c=[]
    f=[]          #Current has been FFTed.
    print 'Reading Data...........'
    try:
        for line in fp:
            a.append(float(line))
    finally: 
        fp.close()
    fp = open(workdir+"/V.dat")
    
    v = []     #the voltage
    try:
        for line in fp:
            v.append(float(line))
    finally:
        fp.close()
    ###Reading the profile like sample frequency
    fp=open(workdir+"/profile.dat")
    try:    
        fsample=int(fp.readline())
        pid=int(fp.readline())
        state=int(fp.readline())
    finally:
      fp.close()
    try:
      fp=open("Data/Status.dat","r")
      StatusSet=cPickle.load(fp)
    except:
      fp=open("Data/Status.dat","w")
      StatusSet={}
      cPickle.dump(StatusSet,fp)
    finally:
      fp.close()
    if pid!=99:
      if StatusSet.has_key(pid) is False:
        StatusSet[pid]=[0,state]
      else:
        if StatusSet[pid].count(0)==0:
          StatusSet[pid].append(state)
      StatusSet[pid].sort()
      try:
        fp=open("Data/Status.dat","w")
        cPickle.dump(StatusSet,fp)
      finally:
        fp.close()
    print "The StatusSet Now:"
    print StatusSet
    print 'Split the current into pieces of periods'
    nMean = np.mean(v)
    nCount = 0
    i = 0
    if v[0] < nMean:
        flag = 0
    else:
        flag = 1
    while True:
        if flag == 1 and v[i] < nMean:
            flag = 0
            nCount = nCount + 1
            i = i + 20                       #20 is a cross step ,to avoid the unstable wave
        elif flag == 0 and v[i] >= nMean:
            flag = 1
            if nCount == 0:
                begin = i
            if nCount == 2:
                end = i
            nCount = nCount + 1
            i = i + 20
        else:
            i = i + 1
        if flag == 0 and nCount == 1:
            nCount = 0
        if nCount == 3 and flag == 1:
            nCount = 1
            DataSplit(a, begin, end)
            begin = i - 19
        if i >= len(v):
            break
    CutToTheSame(tem_c)
    print 'Generating Current Vectors By FFT'
    FFTTrans(c)
    
    ####Generate the Dev Data
    try:
      fp=open("Data/DevSet.dat","r")
      DevData=cPickle.load(fp)
    except:
      fp=open("Data/DevSet.dat","w")
      DevData={}
      cPickle.dump(DevData,fp)
    finally:
      fp.close()
    if pid!=99:
      DevData[(pid,state)]=f[10]
    try:
      fp=open("Data/DevSet.dat","w")
      cPickle.dump(DevData,fp)
    finally:
      fp.close()
    app.quit()
