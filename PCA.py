import os
import cPickle
import numpy as np

global PCAClass
class PCAClass:
  pmatrix=None
  pmean=None
  def __init__(self):
    self.pmean={}
    self.pmatrix={}
    dirdata="PCAData/"
    if os.path.exists(dirdata) is False:
      return False
    files=os.listdir(dirdata)
    #Begin loading the data    x is like "132-1"
    
    for x in files:
      pid,state=x.split('-')
      pid=int(pid)
      state=int(state)
      try:
        fp=open("%s%s"%(dirdata,x),'r')
      except:
        print 'Open file error'
      self.pmatrix[(pid,state)],self.pmean[(pid,state)]=cPickle.load(fp)
      fp.close()
  
  def PCA(self,Current,status):
    first=True
    A=None
    b=None
    #Combine the matrix
    for x in status:
      if status[x]!=0:
        if first:
          A=self.pmatrix[(x,status[x])]
          first=False
        else:
          A=np.column_stack((A,self.pmatrix[(x,status[x])]))
    first=True
    #AX+b=Y    get X.  
    for x in status:
      if status[x]!=0:
        if first:
          b=self.pmean[(x,status[x])]
          first=False
        else:
          b=b+self.pmean[(x,status[x])]
    if A is not None and b is not None:
      result=np.linalg.lstsq(A,Current-b)
    DeVector={}
    index=0
    for x in status:
      if status[x]!=0:
        d=np.size(self.pmatrix[(x,status[x])],1)
        ijk=result[0][index:(index+d)]
        rjk=self.pmatrix[(x,status[x])]*ijk+self.pmean[(x,status[x])]
        DeVector[x]=rjk.transpose().tolist()[0]
      else:
        DeVector[x]=np.zeros((1,490))[0]
    return DeVector
    
      

    
    
  
  



#from PreProcess import *
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#pcan=mdp.nodes.PCANode(output_dim=10)
#pcar=pcan.execute(np.array(f))
#fig=plt.figure()
#plt.ioff()
#plt.clf()
#ax = fig.gca(projection='3d')
#for item in pcar:
#  ax.scatter(item[0],item[1],item[2])
#
#rem=matrix(pcan.get_recmatrix())
#rec=matrix(pcar)*matrix(rem)
#means=matrix(mean(c,0))
#for x in range(0,len(rec)):
#  rec[x,:]=rec[x,:]+means
#
#rec=array(rec)
#plt.ion()
#for x in range(0,len(rec)):
#  plt.clf()
#  plot(range(0, len(rec[x])),rec[x],'r')
#  plot(range(0, len(c[x])),c[x],'r')
#  plt.draw()
#
#plt.show()