# -*- coding: utf-8 -*-
from PreProcess import *
import matplotlib.pyplot as plt


plt.ioff()

fig=plt.figure()
for i in range(0,9):
    axx=fig.add_subplot(3,3,i+1)
    x=[ele[i] for ele in f]
    plt.hist(real(x),100)

plt.show()
    


