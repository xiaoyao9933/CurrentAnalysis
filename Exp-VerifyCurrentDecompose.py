# -*- coding: utf-8 -*-
import os, cPickle
import numpy as np
import calib
import matplotlib.pyplot as plt

def GetCurrent(Status, AllVectors):
    flag = 0
    selected ={}
    print Status
    for x in Status:
        if Status[x] != 0:
            selected[x] = AllVectors[(x, Status[x])]
            if flag == 0:
                result = np.array(AllVectors[x, Status[x]])
                flag = 1
            else:
                result = result + np.array(AllVectors[x, Status[x]])
    if flag == 0:
        result = np.zeros((1, len(AllVectors[(0, 1)])))[0].tolist()
    return result,selected

def VerifyCurrent(Status):
    dirdata = "CompressedData/"
    AllVectors = {}
    if os.path.exists(dirdata) is False:
        return False
    files = os.listdir(dirdata)
    # Begin loading the data    x is like "132-1"
    for x in files:
        pid, state = x.split('-')
        pid = int(pid)
        state = int(state)
        try:
            fp = open("%s%s"%(dirdata, x), 'r')
        except:
            print 'Open file error'
        sf = cPickle.load(fp)
        AllVectors[(pid,state)] = sf[115,:].tolist()
        fp.close()
    vector, SelectedVectors =GetCurrent(Status,AllVectors)
    PCAclass = calib.PCA.PCAClass()
    DeVector = PCAclass.PCA(np.matrix(vector).transpose(), Status)
    plt.ioff()
    dims = len(AllVectors[(0, 1)])
    for pid in SelectedVectors: 
        fig=plt.figure()
        plt.bar(np.arange(0,dims,1),DeVector[pid],0.3)
        plt.bar(np.arange(0.3,dims+0.3,1),SelectedVectors[pid],0.3,color='r')
        plt.show()
    
    
