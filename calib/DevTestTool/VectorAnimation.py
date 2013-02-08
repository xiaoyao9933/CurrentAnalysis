# -*- coding: utf-8 -*-
from PreProcess import *
import matplotlib.pyplot as plt

plt.ion()
for x in f:
    plt.clf()
    plt.bar(range(1,10),[abs(j) for j in x[1:10]])
   # plt.ylim(ymin=0,ymax=100)
    plt.draw()
      
