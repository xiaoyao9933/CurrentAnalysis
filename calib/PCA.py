import os
import cPickle
import numpy as np

global PCAClass


class PCAClass:
    pmatrix = None
    pmean = None

    def __init__(self):
        self.pmean = {}
        self.pmatrix = {}
        self.hashtable = {}
        dirdata = "PCAData/"
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

            self.pmatrix[(pid, state)], self.pmean[(pid, state)
                                                   ] = cPickle.load(fp)
            #print np.size(self.pmatrix[(pid, state)],1)
            fp.close()

    def PCA(self, Current, status):
        """
        Current is a single-column matrix
        """
        if (Current.__str__(),status.__str__()) in self.hashtable:
            return self.hashtable[Current.__str__(),status.__str__()]
        else:
            first = True
            A = None
            b = None
            length = Current.size
            DevectorSum = np.matrix(np.zeros((length,1)))
            DeviceNum=0
            
            # Combine the matrix
            for x in status:
                if status[x] != 0:
                    DeviceNum += 1
                    if first:
                        A = self.pmatrix[(x, status[x])]
                        first = False
                    else:
                        A = np.column_stack((A, self.pmatrix[(x, status[x])]))
            first = True
            if A is not None:
                cond_num = np.linalg.cond(A)
            # AX+b=Y    get X.
            for x in status:
                if status[x] != 0:
                    if first:
                        b = self.pmean[(x, status[x])]
                        first = False
                    else:
                        b = b + self.pmean[(x, status[x])]
            if A is not None and b is not None:
                result = np.linalg.lstsq(A, Current - b)
            DeVector = {}
            index = 0
            for x in status:
                if status[x] != 0:
                    d = np.size(self.pmatrix[(x, status[x])], 1)
                    ijk = result[0][index:(index + d)]
                    rjk = self.pmatrix[(x, status[x])] * ijk + \
                        self.pmean[(x, status[x])]
                    DeVector[x] = rjk.transpose().tolist()[0]
                    DevectorSum+=rjk;
                else:
                    DeVector[x] = np.zeros((1, length))[0]
            subvalue = np.abs(Current-DevectorSum).sum()
            if DeviceNum!=0:
                cond_factor = subvalue/(cond_num/DeviceNum)
            else:
                cond_factor = -1
            self.hashtable[Current.__str__(),status.__str__()] = (DeVector,cond_factor)
            return (DeVector,cond_factor)










# from PreProcess import *
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# pcan=mdp.nodes.PCANode(output_dim=10)
# pcar=pcan.execute(np.array(f))
# fig=plt.figure()
# plt.ioff()
# plt.clf()
# ax = fig.gca(projection='3d')
# for item in pcar:
#  ax.scatter(item[0],item[1],item[2])
#
# rem=matrix(pcan.get_recmatrix())
# rec=matrix(pcar)*matrix(rem)
# means=matrix(mean(c,0))
# for x in range(0,len(rec)):
#  rec[x,:]=rec[x,:]+means
#
# rec=array(rec)
# plt.ion()
# for x in range(0,len(rec)):
#  plt.clf()
#  plot(range(0, len(rec[x])),rec[x],'r')
#  plot(range(0, len(c[x])),c[x],'r')
#  plt.draw()
#
# plt.show()
