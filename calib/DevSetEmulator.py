# -*- coding: utf-8 -*-
import cPickle
import numpy as np
import copy
import OptimizeWeight


def GetCurrent(Status, DevData):
    flag = 0
    print Status
    for x in Status:
        if Status[x] != 0:
            if flag == 0:
                result = np.array(DevData[x, Status[x]])
                flag = 1
            else:
                result = result + np.array(DevData[x, Status[x]])
    if flag == 0:
        result = np.zeros((1, len(DevData[(0, 1)])))[0].tolist()
    return result


if __name__ == '__main__':
    try:
        fp = open("Data/DevSet.dat", "r")
        DevData = cPickle.load(fp)
    finally:
        fp.close()

    try:
        fp = open("Data/Status.dat", 'r')
        StatusSet = cPickle.load(fp)
    except:
        print 'Open file error'
    finally:
        fp.close()
    DevSet = []
    Status = {}
    for x in StatusSet:
        Status[x] = 1
    # DevSet.append({'status':Status,'current':GetCurrent(Status,DevData)})
    for x in StatusSet:
        Status[x] = 0
        tmpStatus = copy.deepcopy(Status)
        DevSet.append(
            {'status': tmpStatus, 'current': GetCurrent(Status, DevData)})
        Status[x] = 1
    DevSet = DevSet[0:4]
    print 'Generating DevSet Finished'
   # a=OptimizeWeight.Optimizer()
   # a.OptimizeIterator(DevSet,[1,1,1],10)
