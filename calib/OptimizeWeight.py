# -*- coding: utf-8 -*-
import numpy as np
import StatusSearch,cPickle
class Optimizer:
  def GetCrossOver(self,line1,line2,index):
    #line Format: (k,b,{})
    k1=float(line1[0])
    k2=float(line2[0])
    b1=float(line1[1])
    b2=float(line2[1])
    if k1==k2:
      return None
    else:
      m=(b2-b1)/(k1-k2)
      n=(k1*b2-b1*k2)/(k1-k2)
      return (m,n,index)
  def LineCmp(self,x,y):
    if(x[0]>y[0]): return 1
    elif(x[0]==y[0] and x[1]<y[1]):return 1
    elif(x[0]==y[0] and x[1]==y[1]):return 0
    else:return -1
  def PointCmp(self,x,y):
    if(x[0]>y[0]):return 1
    else:return -1

  def CriticalCmp(self,x,y):
    if(x[2]>y[2]):return 1
    elif(x[2]==y[2]):return 0
    else:return -1

  def ComputeError(self,status1,status2):
    tsum=0
    try:
      for x in status1:
        if x not in status2:
            tsum=tsum+(status1[x]-0)**2
        else:
            tsum=tsum+(status1[x]-status2[x])**2
      return np.sqrt(tsum)
    except:
      print status1,status2

  def ComputeCriticalPoints(self,lamatas,TrainSet,dim):
    #Format
    #:[[lamatas],((hs),{pid:status,...}),....],dim int
       ##Fix one dim,and generate the lines set.
    #lines Format: (k,b,{pid:status})
    Lines=[]
    CriticalPoints=[]
    for x in TrainSet:
      k=x['h'][dim]
      b=0
      for y in range(0,len(lamatas)):
        if y!=dim:
          b=b+lamatas[y]*x['h'][y]
      Lines.append((k,b,x['status']))

      ##Sort the lines
    Lines.sort(cmp=self.LineCmp)
    LastPoint=(-np.inf,-np.inf)
    x=0
    while x<len(Lines):
      points=[]
      for y in range(x+1,len(Lines)):
        if Lines[x][0]!=Lines[y][0]:
          point=self.GetCrossOver(Lines[x],Lines[y],y)
          if point:
            points.append(point)
      ##Kick the points on left of the last crossover point
      tmp=range(0,len(points))
      tmp.sort(reverse=True)
      #Pop from the back
      for z in tmp:
        if points[z][0]<=LastPoint[0]:
          points.pop(z)
      if len(points)!=0:
        points.sort(cmp=self.PointCmp)
        CriticalPoints.append((LastPoint[0],points[0][0],Lines[x][2]))
        LastPoint=points[0][0:2]
        x=points[0][2]
      else:
        #If no more cross points,return the criticalpoints
        CriticalPoints.append((LastPoint[0],np.inf,Lines[x][2]))
        #print CriticalPoints
        return CriticalPoints

  ##This will merge the lists.
  def Merge(self,lists):
    s=[]
    for x in lists:
      s=s+x
    s=set(s)
    s=list(s)
    s.sort()
    return s
  ##This will find the status of pos in range
  def FindStatus(self,CriPoint,pos):
    for x in CriPoint:
      if pos>x[0] and pos<=x[1]:
        return x[2]
    return None


  def MergeCritical(self,CriPoints):
    lists=[]
    #Reshape the critical points
    for x in CriPoints:
      tmp=[-np.inf]
      for y in x:
        tmp.append(y[1])
      lists.append(tmp)
    #Merge the points
    MergeList=self.Merge(lists)
    #print MergeList
    MergeResult={}
    #print CriPoints
    for pos in MergeList:
      for x in CriPoints:
        if MergeResult.has_key(pos) is False:
          MergeResult[pos]=[]
        MergeResult[pos].append(self.FindStatus(x,pos)) #Merge Status
    #print MergeResult
    #Reshape to range style
    Result=[]
    last=-np.inf
    keys=MergeResult.keys()
    keys.sort()
    for x in keys:
      if x!=-np.inf:
        Result.append((last,x,MergeResult[x]))
        last=x
    return Result

  def CalScore(self,MergeResult,DevSet):
    try:
      Result=[]
      #print MergeResult
      for x in MergeResult:
        score=0
        for time in range(0,len(DevSet)):
          score=score+self.ComputeError(x[2][time],DevSet[time]['status'])
        Result.append((x[0],x[1],score))
      return Result
    except:
      print MergeResult
      exit(0)


  def SelectWeight(self,CriPoints,DevSet):
    R=10
    #1:Merge the critical points
    Result=self.MergeCritical(CriPoints)
    #2:Calculate the score
    Result=self.CalScore(Result,DevSet)
    #3:Sort and find the highest score
    Result.sort(cmp=self.CriticalCmp)
    #4:Return the result
    #print Result
    if Result[0][0]==-np.inf:
      return (Result[0][1]-R,Result[0][2])
    elif Result[0][1]==np.inf:
      return (Result[0][0]+R,Result[0][2])
    else:
      return ((Result[0][0]+Result[0][1])/2,Result[0][2])

  def Optimize(self,DevSet,TrainSet,lamatas):
    dims=len(lamatas)
    minerror=np.inf
    CriPoints=[]
    for x in range(0,dims):
      CriPoints=[]
      for y in range(0,len(TrainSet)):
        CriPoints.append(self.ComputeCriticalPoints(lamatas,TrainSet[y],x))
      lamatas[x],error=self.SelectWeight(CriPoints,DevSet)
      if error<minerror:
        minerror=error
    return (lamatas,minerror)

  def OptimizeIterator(self,DevSet,lamatas,N):
    lasterror=0
    newerror=10
    epsilon=0.1
    iternum=0
    Maxiter=100
    self.searcher=StatusSearch.Searcher()
    while iternum<Maxiter and abs(lasterror-newerror)>=epsilon:
      print "#Iterating %d:"%(iternum+1)
      print "##Generating TrainSet......"
      TrainSet=self.searcher.StatusSearch(lamatas,N,DevSet)
      print "##Optimizing Weights......"
      lamatas,minerror=self.Optimize(DevSet,TrainSet,lamatas)
      lasterror=newerror
      newerror=minerror
      iternum=iternum+1
      print "##error is :%f"%(abs(lasterror-newerror))
      print "##Lamatas:",lamatas
    if iternum>=Maxiter:print "Exit iterating for maxiter times"
    if abs(lasterror-newerror)<=epsilon:print "Iterating Success"
    try:
      fp=open("Data/lamatas.dat",'w')
      cPickle.dump(lamatas,fp)
    except:
      print 'Open file error'
    finally:
      fp.close()
    return lamatas







