# -*- coding: utf-8 -*-
import sklearn.neighbors as skn
import numpy as np
class KnnDensityEstimator:
  def __init__(self,dataset):
    self.n=len(dataset)
    self.k=int(np.sqrt(self.n))
    self.knn=skn.NearestNeighbors(n_neighbors=self.k)
    self.knn=self.knn.fit(dataset)
  def Estimate(self,data):
    knd=self.knn.kneighbors(data)
    return (float(self.k)/float(self.n))/(knd[0][0][self.k-1]**3)