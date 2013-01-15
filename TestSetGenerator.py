# -*- coding: utf-8 -*-
import cPickle
import numpy as np
from StatusSearch import *

def GetCurrent(Status,DevData):
  flag=0
  print Status
  for x in Status:
    if Status[x]!=0:
      if flag==0:
        result=np.array(DevData[x,Status[x]])
        flag=1
      else:
        result=result+np.array(DevData[x,Status[x]])
  return result
      
  
if __name__ == '__main__':
  try:
    fp=open("Data/DevSet.dat","r")
    DevData=cPickle.load(fp)
  finally:
    fp.close()
    
  try:
    fp=open("Data/Status.dat",'r')
    StatusSet=cPickle.load(fp)
  except:
    print 'Open file error'
  finally:
    fp.close()
    
  try:
    fp=open("Data/lamatas.dat",'r')
    lamatas=cPickle.load(fp)
  except:
    print 'Open file error'
  finally:
    fp.close()
  DevSet=[]
  Status={}
  for x in StatusSet:
    Status[x]=1
  Status[2]=0
  DevSet.append({'status':Status,'current':GetCurrent(Status,DevData)})
  #DevSet.append({'status':Status,'current':f[0]})
  searcher=Searcher()
  print searcher.StatusSearch(lamatas,5,DevSet)