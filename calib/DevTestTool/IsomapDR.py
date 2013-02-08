# -*- coding: utf-8 -*-
import numpy as np
from PreProcess import *
from pysomap import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

M = numpy.array(f)
A = isodata()                                 # creates a new object A
A.load_isodata(M)                             # loads python array X (N x M) into object A
A.reduce_isodata(isomap_type="K", K=7, O=3) 
result=A.outdata
fig=plt.figure()
plt.ioff()
plt.clf()
ax = fig.gca(projection='3d')
for item in result:
  ax.scatter(item[0],item[1],item[2])
plt.show()
  