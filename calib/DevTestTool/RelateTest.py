# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from PreProcess import *
import matplotlib.pyplot as plt

plt.ioff()
fig=plt.figure()
x=[ele[1] for ele in f]
y=[ele[7] for ele in f]
plot(x,y,'.')
plt.show()
    
