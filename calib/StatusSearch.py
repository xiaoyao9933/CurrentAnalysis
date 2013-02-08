# -*- coding: utf-8 -*-
import PCA
import KnnDensityEstimator as kde
import os,cPickle,copy
import numpy as np
def Scorecmp(x,y):
    if (x['score']<y['score']):return 1
    elif (x['score']<y['score']):return 0
    else:return -1

class Searcher:
  kernel=None
  StatusSet=None
  Closed=[]
  Tmp=[]
  Open=[]
  H={}


  def Push(self):
    while len(self.Tmp)!=0:
      self.Open.append(self.Tmp.pop())
  def PushToClosed(self):
    while len(self.Tmp)!=0:
      self.Closed.append(self.Tmp.pop())
  def Expand(self):
    while len(self.Open)!=0:
      S=self.Open.pop()
      self.Find(S)
      self.Closed.append(S)
  def Find(self,node):
    status=node['status']
    for pid in status:
      self.FindNearStatus(node,status,pid)

  def FindNearStatus(self,node,status,pid):
    tmpnode=copy.deepcopy(node)
    CurStatus=status[pid]
    length=len(self.StatusSet[pid])
    if CurStatus<length-1:
      tmpnode['status'][pid]=CurStatus+1
      if self.H.has_key(tmpnode['status'].__str__()) is False:
        self.Tmp.append(tmpnode)
        self.H[tmpnode['status'].__str__()]=0
    if CurStatus>0:
      tmpnode['status'][pid]=CurStatus-1
      if self.H.has_key(tmpnode['status'].__str__()) is False:
        self.Tmp.append(tmpnode)
        self.H[tmpnode['status'].__str__()]=0

  def Compute(self,lamatas,N,Current):
    for j in range(0,len(self.Tmp)):
      node=self.Tmp[j]
      DeVector=self.PCAclass.PCA(Current,node['status']) #  {pid:[vectors],,}
      h=[0,0,0]
      Featuresum=0

      ####Feature 0 ,every dim
      for pid in node['status']:
        curstate=node['status'][pid]
        if curstate!=0:
          for dim in range(0,len(DeVector[pid])):
            value=DeVector[pid][dim]
            h[0]+=self.kernel[(pid,curstate)][dim+1].estimate([value])
#            k=self.kernel[(pid,curstate)][dim+1].integrate_box_1d(value-5,value+5)
#            if k!=0:
#              h[0]+=np.log(k)
#              print k,'0'
#            else:
#              print '0 alert'
#              h[0]+=(-253)
      ####Feature 1 ,in all dim
      for pid in node['status']:
        curstate=node['status'][pid]
        if curstate!=0:
          value=DeVector[pid]
          h[1]+=self.kernel[(pid,curstate)][0].estimate(value)
          #lowbound=np.array([t-1 for t in value])
          #highbound=np.array([t+1 for t in value])
          #k=self.kernel[(pid,curstate)][0].integrate_box(lowbound,highbound,maxpts=5)
#          k=self.kernel[(pid,curstate)][0](value)[0]
#          if k!=0:
#            h[1]+=np.log(k)
#            print k,'1'
#          else:
#            print '1 alert'
#            h[1]+=(-253)
      ####Feature 2,discriminant
      for pid in node['status']:
        curstate=node['status'][pid]
        if curstate!=0:
          value=DeVector[pid]
          for dim in range(0,len(DeVector[pid])-2):
            h[2]+=self.kernel3[(pid,curstate)][dim].estimate(value[dim:dim+3])
            h[2]-=self.kernel2[(pid,curstate)][dim+1].estimate(value[dim:dim+2])
      for w in range(0,len(h)):
        h[w]=float(h[w])
      #Calculate the sum
      for k in range(0,len(lamatas)):
        Featuresum+=lamatas[k]*h[k]
      self.Tmp[j]['h']=h
      self.Tmp[j]['score']=Featuresum
    self.Tmp.sort(cmp=Scorecmp)
    #Get the N-Best
    self.Tmp=self.Tmp[0:N]

  def StatusSearch(self,lamatas,N,DevSet):
    Result=[]
    for time in range(0,len(DevSet)):
      self.Closed=[]
      self.Tmp=[]
      self.Open=[]
      self.H={}
      Node={'status':{},'score':-np.inf}
      for x in self.StatusSet:
        Node['status'][x]=1
      self.Tmp.append(Node)
      self.Compute(lamatas,N,DevSet[time]['current'])
      self.H[Node['status'].__str__()]=0
      flag=True
      while flag:
        self.Push()
        self.Expand()
        self.Compute(lamatas,N,DevSet[time]['current'])
        self.Closed.sort(cmp=Scorecmp)
        if len(self.Tmp)==0:flag=False
        elif self.Closed[0]['score']>self.Tmp[0]['score']:flag=False
        else:flag=True
      ##After search,push the tmp to closed
      self.PushToClosed()
      self.Closed.sort(cmp=Scorecmp)
      Result.append(self.Closed[0:N])
    return Result



  def __init__(self):
    self.kernel={}
    self.kernel2={}
    self.kernel3={}
    self.StatusSet={}
    dirdata="CompressedData/"
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
      self.sf=cPickle.load(fp)
      self.sf=np.matrix(self.sf)
      fp.close()
      self.kernel[(pid,state)]={}
      self.kernel[(pid,state)][0]=kde.KnnDensityEstimator(self.sf.tolist())
      #0 is special for containing all dimensions
      for y in range(0,np.size(self.sf,1)):
        self.kernel[(pid,state)][y+1]=kde.KnnDensityEstimator(self.sf[:,y].tolist())

      self.kernel2[(pid,state)]={}
      for y in range(0,np.size(self.sf,1)-1):
        self.kernel2[(pid,state)][y]=kde.KnnDensityEstimator(self.sf[:,y:y+2].tolist())
      self.kernel3[(pid,state)]={}
      for y in range(0,np.size(self.sf,1)-2):
        self.kernel3[(pid,state)][y]=kde.KnnDensityEstimator(self.sf[:,y:y+3].tolist())
    try:
      fp=open("Data/Status.dat",'r')
    except:
      print 'Open file error'
    self.StatusSet=cPickle.load(fp)
    self.PCAclass=PCA.PCAClass()
    fp.close()







