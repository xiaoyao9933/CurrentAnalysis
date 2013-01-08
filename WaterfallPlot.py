# -*- coding: utf-8 -*-
from PreProcess import *
import matplotlib.pyplot as plt

fig = plt.figure(1)
zs=[]
for x in c:
    zs.append(log(abs(fft(x))[0:40]))
zs = transpose(zs)
imshow(zs, interpolation = 'bilinear')
axis([0, 40, 0, 10])
grid(True)
