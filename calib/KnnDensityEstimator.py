# -*- coding: utf-8 -*-
import sklearn.neighbors as skn
import numpy as np


class KnnDensityEstimator:
    def __init__(self, dataset):
        self.dataset = dataset
        self.hashtable = {}
        self.n = len(dataset)
        self.k = int(np.sqrt(self.n))
        self.knn = skn.NearestNeighbors(n_neighbors=self.k)
        self.knn = self.knn.fit(dataset)

    def maxvector(self, point, data):
        v = np.abs(np.array(point) - np.array(data))
        for x in range(0, self.dims):
            if v[x] > self.vector[x]:
                self.vector[x] = v[x]

    def estimate(self, data):
        if data.__str__() in self.hashtable:
            return self.hashtable[data.__str__()]
        else:
            self.knd = self.knn.kneighbors(data)
            self.dims = len(data)
            self.vector = [0 for x in range(0, self.dims)]
            for x in range(0, self.k):
                self.maxvector(self.dataset[self.knd[1][0][x]], data)
            volume = 1
            for x in range(0, self.dims):
                volume = volume+np.log(self.vector[x]+np.e)
            result = np.log((self.k / float(self.n)) / volume)
            self.hashtable[data.__str__()] = result
            return result
