# -*- coding: utf-8 -*-
import numpy as np
from PreProcess import *
import scipy
kernel=scipy.stats.kde.gaussian_kde(fsample.T)
