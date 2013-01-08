# -*- coding: utf-8 -*-
from PreProcess import *
from PCA import *
from scipy import stats
import os,cPickle,copy
import numpy as np
global Searcher
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
      h=[0,0]
      Featuresum=0

      ####Feature 0 ,every dim 
      for pid in node['status']:
        curstate=node['status'][pid]
        for dim in range(0,len(DeVector[pid])):
          if curstate!=0:
            k=self.kernel[(pid,curstate)][dim+1](DeVector[pid][dim])
            if k!=0:
              h[0]+=np.log(k)
            else:
              h[0]+=(-999999)
      ####Feature 1 ,in all dim
      for pid in node['status']:
        curstate=node['status'][pid]
        if curstate!=0:
          k=self.kernel[(pid,curstate)][0](DeVector[pid])
          if k!=0:
            h[1]+=np.log(k)
          else:
            h[1]+=(-999999)
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
      Result.append(self.Closed[0:N])
    return Result
      
     
      
  def __init__(self):
    self.kernel={}
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
      sf=cPickle.load(fp)
      fp.close()
      self.kernel[(pid,state)]={}
      self.kernel[(pid,state)][0]=stats.kde.gaussian_kde(sf.T)
      #0 is special for containing all dimensions
      for y in range(0,np.size(sf,1)):
        self.kernel[(pid,state)][y+1]=stats.kde.gaussian_kde(sf[:,y].T)
    try:
      fp=open("Data/Status.dat",'r')
    except:
      print 'Open file error'
    self.StatusSet=cPickle.load(fp)
    self.PCAclass=PCAClass()
    fp.close()
  
  
    
     



