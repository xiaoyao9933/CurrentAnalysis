# -*- coding: utf-8 -*-
'''
File: StatusSearch.py
Author: xiaoyao9933
Description: This module generates the trainset. The trainset is the result of looking for the nearest the status of the initial status and decompose the total current. 
Return: [{'status':{0:1,1:1,..},'current':[]},...]
'''
import PCA
import KnnDensityEstimator as kde
import os
import cPickle
import copy
import numpy as np


def Scorecmp(x, y):
    if (x['score'] < y['score']):
        return 1
    else:
        return -1

def SubValuecmp(x, y):
    if (x['subvalue'] > y['subvalue']):
        return 1
    else:
        return -1

class Searcher:
    kernel = None
    StatusSet = None
    Closed = []
    Tmp = []
    Open = []
    H = {}

    def Push(self):
        while len(self.Tmp) != 0:
            self.Open.append(self.Tmp.pop())

    def PushToClosed(self):
        while len(self.Tmp) != 0:
            self.Closed.append(self.Tmp.pop())

    def Expand(self):
        while len(self.Open) != 0:
            S = self.Open.pop()
            self.Find(S)
            self.Closed.append(S)

    def Find(self, node):
        status = node['status']
        for pid in status:
            self.FindNearStatus(node, status, pid)

    def FindNearStatus(self, node, status, pid):
        tmpnode = copy.deepcopy(node)
        CurStatus = status[pid]
        length = len(self.StatusSet[pid])
        if CurStatus < length - 1:
            tmpnode['status'][pid] = CurStatus + 1
            if (tmpnode['status'].__str__() in self.H) is False:
                self.Tmp.append(tmpnode)
                self.H[tmpnode['status'].__str__()] = 0
        if CurStatus > 0:
            tmpnode['status'][pid] = CurStatus - 1
            if (tmpnode['status'].__str__() in self.H) is False:
                self.Tmp.append(tmpnode)
                self.H[tmpnode['status'].__str__()] = 0

    def Compute(self, lamatas, N, Current):
        for j in range(0, len(self.Tmp)):
            node = self.Tmp[j]
            node['DeVector'],node['subvalue'] = self.PCAclass.PCA(
            np.matrix(Current).transpose(), node['status'])  # {pid:[vectors],,}
            #print node['subvalue']
        self.Tmp= filter(lambda node:node['subvalue']!= -1, self.Tmp)
            
        for j in range(0, len(self.Tmp)):
            node = self.Tmp[j]
            DeVector = node['DeVector']
            h = [0, 0, 0, 0]
            OpenedNum = 0
            for pid in node['status']:
                if node['status'][pid] is not 0:
                    OpenedNum += 1
            # Feature 0 ,every dim
            for pid in node['status']:
                curstate = node['status'][pid]
                if curstate:
                    for dim in range(0, len(DeVector[pid])):
                        value = DeVector[pid][dim]
                        h[0] += self.kernel[(
                            pid, curstate)][dim + 1].estimate([value])
            h[0]= h[0]/100
            # Feature 1 ,in all dim
            for pid in node['status']:
                curstate = node['status'][pid]
                if curstate:
                    value = DeVector[pid]
                    h[1] += self.kernel[(pid, curstate)][0].estimate(value)
            # Feature 2,discriminant
            for pid in node['status']:
                curstate = node['status'][pid]
                if curstate:
                    value = DeVector[pid]
                    for dim in range(0, len(DeVector[pid]) - 2):
                        h[2] += self.kernel3[(
                            pid, curstate)][dim].estimate(value[dim:dim + 3])
                        h[2] -= self.kernel2[(
                                pid, curstate)][dim + 1].estimate(value[dim:dim + 2])
            h[2]=h[2]/10
            Featuresum = 0
            for dim in range(0,len(h)):
                if OpenedNum:
                    h[dim] = h[dim] / OpenedNum
                    
            h[3]=node['subvalue']
            # Calculate the sum
            for dim in range(0, len(lamatas)):
                if OpenedNum:
                    Featuresum += lamatas[dim] * h[dim]
                else:
                    Featuresum = -999999
            self.Tmp[j]['h'] = h
            self.Tmp[j]['score'] = Featuresum


        self.Tmp.sort(cmp=Scorecmp)
        # Get the N-Best
        self.Tmp = self.Tmp[0:N]
        map(lambda node: node.pop('DeVector'), self.Tmp)
    def Recalculate(self, lamatas):
        self.Closed.sort(cmp=SubValuecmp)
        if len(self.Closed)>0:
            self.MinSubValue = self.Closed[0]['subvalue']
        
        for j in range(0, len(self.Closed)):
            Featuresum = 0
            node = self.Closed[j]
            node['h'][3] = np.log(self.MinSubValue/node['h'][3])
            for dim in range(0, len(lamatas)):
                Featuresum += lamatas[dim] * node['h'][dim]
            node['score'] = Featuresum
            
    def StatusSearch(self, lamatas, N, DevSet):
        for time in range(0, len(DevSet)):
            self.MinSubValue = np.inf
            self.Closed = []
            self.Tmp = []
            self.Open = []
            self.H = {}
            Node = {'status': {}, 'score': -np.inf}
            Node['status'] = DevSet[time]['status']
            for pid in self.StatusSet:
                if pid not in Node['status']:
                    Node['status'][pid] = 0
            self.Tmp.append(Node)
            self.Compute(lamatas, N, DevSet[time]['current'])
            self.H[Node['status'].__str__()] = 0
            flag = True
            while flag:
                self.Push()
                self.Expand()
                self.Compute(lamatas, N, DevSet[time]['current'])
                self.Closed.sort(cmp=Scorecmp)
                if len(self.Tmp) == 0:
                    flag = False
                elif self.Closed[0]['score'] > self.Tmp[0]['score']:
                    flag = False
                else:
                    flag = True
            # After search,push the tmp to closed
            self.PushToClosed()
            self.Recalculate(lamatas)
            #if self.Result.has_key(time):
            #    self.Closed += self.Result[time]
            self.Closed.sort(cmp=Scorecmp)
            self.Result[time]=self.Closed[0:N]
        return self.Result

    def __init__(self):
        self.kernel = {}
        self.kernel2 = {}
        self.kernel3 = {}
        self.StatusSet = {}
        self.Result = {}
        dirdata = "CompressedData/"
        if os.path.exists(dirdata) is False:
            return False
        files = os.listdir(dirdata)
        # Begin loading the data    x is like "132-1"
        for x in files:
            pid, state = x.split('-')
            pid = int(pid)
            state = int(state)
            try:
                fp = open("%s%s"%(dirdata, x), 'r')
            except:
                print 'Open file error'
            self.sf = cPickle.load(fp)
            self.sf = np.matrix(self.sf)
            fp.close()
            self.kernel[(pid, state)] = {}
            self.kernel[(pid, state)][
                0] = kde.KnnDensityEstimator(self.sf.tolist())
            # 0 is special for containing all dimensions
            for y in range(0, np.size(self.sf, 1)):
                self.kernel[(pid, state)][y + 1] = kde.KnnDensityEstimator(
                    self.sf[:, y].tolist())

            self.kernel2[(pid, state)] = {}
            for y in range(0, np.size(self.sf, 1) - 1):
                self.kernel2[(pid, state)][y] = kde.KnnDensityEstimator(
                    self.sf[:, y:y + 2].tolist())
            self.kernel3[(pid, state)] = {}
            for y in range(0, np.size(self.sf, 1) - 2):
                self.kernel3[(pid, state)][y] = kde.KnnDensityEstimator(
                    self.sf[:, y:y + 3].tolist())
        try:
            fp = open("Data/Status.dat", 'r')
        except:
            print 'Open file error'
        self.StatusSet = cPickle.load(fp)
        # self.StatusSet.pop(2)
        self.PCAclass = PCA.PCAClass()
        fp.close()
