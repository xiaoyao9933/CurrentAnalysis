# -*- coding: utf-8 -*-
from PreProcess import *
import matplotlib.pyplot as plt

plt.ion()
plt.figure(1)
for x in c:
    plt.clf()
    plt.plot(range(0, len(x)), x)
    plt.draw()
    

    
