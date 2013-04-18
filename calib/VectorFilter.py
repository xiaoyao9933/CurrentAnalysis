# -*- coding: utf-8 -*-
import numpy as np
from scipy import spatial
import cPickle
import mdp
import os

class VectorFilter:
    def __init__(self, processer):

        # Generate the PCA promatrix
        print "Calculating the PCA promatrix....."
        try:
            os.mkdir("PCAData")
        except:
            pass
        fp = open("PCAData/%d-%d" % (processer.pid, processer.state), 'w')
        pcan = mdp.nodes.PCANode(svd=True)
        pmean = np.matrix(np.mean(processer.f[0:1000], axis=0)).transpose()
        pcar = pcan.execute(np.array(processer.f[0:1000]))
        psum = 0
        pvar = pcan.total_variance
        for i in range(0, len(processer.f[0])):
            psum += float(pcan.d[i])
            if (psum / pvar >0.95 ):
                break
        print i
        pmatrix = np.matrix(pcan.get_projmatrix()[:, 0:i + 1])
        cPickle.dump((pmatrix, pmean), fp)
        fp.close()

        print "Compressing the Vectors....."
        sf = np.array(processer.f)[0:1000, :]
        try:
            os.mkdir("CompressedData")
        except:
            pass
        fp = open(
            "CompressedData/%d-%d" % (processer.pid, processer.state), 'w')
        cPickle.dump(sf, fp)
        fp.close()