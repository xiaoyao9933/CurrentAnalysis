# -*- coding: utf-8 -*-
import numpy as np
from PreProcess import *
from scipy import spatial
import cPickle,mdp

print "Compressing the Vectors....."
sf=array(f)[0:1000,:]
#D=np.zeros((len(sf),len(sf)))
#for i in range(0,len(sf)):
#  for j in range(i,len(sf)):
#    D[i,j]=spatial.distance.euclidean(sf[i,:],sf[j,:])
#D=D+D.transpose()
#std_D=std(mean(D,axis=1))
#
#DistanceGate=std_D/5    #  %8 propobability 
#CountGate=10
#DeleteList=[]
#for i in range(0,len(sf)):
#    temp=D[i,i:len(sf)]
#    temp.sort()
#    count=0
#    for j in range(0,len(sf)-i):
#      if temp[j]<DistanceGate:
#        count=count+1
#        if count>CountGate:
#          DeleteList.append(j+i)
#      else:
#        break
#RemainList=[]
#for i in range(0,len(sf)):
#  if DeleteList.count(i)==0:
#    RemainList.append(i)
#sf=sf[RemainList]

###Todo: save the compressed samples
fp=open("CompressedData/%d-%d"%(pid,state),'w')
cPickle.dump(sf,fp)
fp.close()

#Generate the PCA promatrix
print "Calculating the PCA promatrix....."
fp=open("PCAData/%d-%d"%(pid,state),'w')
pcan=mdp.nodes.PCANode(svd=True)
pmean=matrix(np.mean(f[0:1000],axis=0)).transpose()
pcar=pcan.execute(np.array(f[0:1000]))
psum=0
pvar=pcan.total_variance
for i in range(0,len(f[0])):
  psum+=float(pcan.d[i])
  if (psum/pvar>0.95):
    break
pmatrix=matrix(pcan.get_projmatrix()[:,0:i+1])
cPickle.dump((pmatrix,pmean),fp)
fp.close()




          
        
    