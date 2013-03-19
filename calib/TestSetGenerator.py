# -*- coding: utf-8 -*-
import cPickle
import numpy as np
import PreProcess
import StatusSearch


class TestSetGenerator:
    """
    def GetCurrent(Status,DevData):
        flag = 0
        print Status
        for x in Status:
            if Status[x] != 0:
                if flag == 0:
                    result = np.array(DevData[x, Status[x]])
                    flag = 1
        else:
            result = result + np.array(DevData[x, Status[x]])
    return result
    """
    def ComputeError(self, status1, status2):
        tsum = 0
        try:
            for x in status1:
                if x not in status2:
                    tsum = tsum + (status1[x] - 0) ** 2
                else:
                    tsum = tsum + (status1[x] - status2[x]) ** 2
            return np.sqrt(tsum)
        except:
            print status1, status2

    def __init__(self,optimizer):
        try:
            fp = open("Data/lamatas.dat", 'r')
            lamatas = cPickle.load(fp)
        except:
            print 'Open file error'
            return
        finally:
            fp.close()
        PP = PreProcess.PreProcess(devout=1)
        searcher = optimizer.searcher
        result = searcher.StatusSearch(lamatas, 20, PP.DevResult)
        for index in range(0, len(PP.DevResult)):
            print index
            print PP.DevResult[index]['status']
            print result[index][0]['status']
            print self.ComputeError(result[index][0]['status'], PP.DevResult[index]['status'])
