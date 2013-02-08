# -*- coding: utf-8 -*-
"""
PreProcessModule

This file reads the data from two files and
Split the current with Voltage Zero points.
"""
import numpy as np
from PyQt4 import QtGui
import cPickle


class PreProcess:

    def __CutToTheSame(self, temp_c):
        length = 999999
        for item in temp_c:
            if len(item) < length:
                length = len(item)
        for item in temp_c:
            self.c.append(item[0:length-1])
        return

    def __FFTTrans(self, x):
        #length=int((int(self.fsample/50)-20)/2)
        for item in x:
            self.f.append(
                [np.real(ele)/len(item)*2
                    for ele in np.fft.fft(item)[1:11:2]] +
                [np.imag(ele)/len(item)*2
                    for ele in np.fft.fft(item)[1:11:2]]
            )
        return

    def __Split(self):
        nMean = np.mean(self.v)
        nCount = 0
        tmp_c = []
        i = 0
        if self.v[0] < nMean:
            flag = 0
        else:
            flag = 1
        while True:
            if flag == 1 and self.v[i] < nMean:
                flag = 0
                nCount = nCount + 1
                i = i + 20  # 20 is a cross step ,to avoid the unstable wave
            elif flag == 0 and self.v[i] >= nMean:
                flag = 1
                if nCount == 0:
                    begin = i
                if nCount == 2:
                    end = i
                nCount = nCount + 1
                i = i + 20
            else:
                i = i + 1
            if flag == 0 and nCount == 1:
                nCount = 0
            if nCount == 3 and flag == 1:
                nCount = 1
                tmp_c.append(self.a[begin:end])
                begin = i - 19
            if i >= len(self.v):
                break
        return tmp_c

    def __init__(self, devout=0):
        workdir = QtGui.QFileDialog.getExistingDirectory(directory="./Data")
        fp = open(workdir+"/A.dat")
        self.a = []          # The raw current
        self.c = []          # The splited current
        self.f = []          # Current has been FFTed.
        self.v = []          # The raw voltage
        self.Status = {}
        print 'Reading Data...........'

        """
        Read the current
        """
        try:
            for line in fp:
                self.a.append(float(line))
        finally:
            fp.close()
        fp = open(workdir+"/V.dat")

        """
        Read the voltage
        """
        try:
            for line in fp:
                self.v.append(float(line))
        finally:
            fp.close()
        """
        Read the profile
        """
        fp = open(workdir+"/profile.dat")
        try:
            self.fsample = int(fp.readline())
            self.pid = int(fp.readline())
            if self.pid != 99:
                self.state = int(fp.readline())
            else:
                for x in fp.readline().split():
                    self.Status[int(x)] = 1

        finally:
            fp.close()
        try:
            fp = open("Data/Status.dat", "r")
            self.StatusSet = cPickle.load(fp)
        except:
            fp = open("Data/Status.dat", "w")
            self.StatusSet = {}
            cPickle.dump(self.StatusSet, fp)
        finally:
            fp.close()
        if self.pid != 99:
            if self.pid in self.StatusSet is False:
                self.StatusSet[self.pid] = [0, self.state]
            else:
                if self.StatusSet[self.pid].count(self.state) == 0:
                    self.StatusSet[self.pid].append(self.state)
            self.StatusSet[self.pid].sort()
            try:
                fp = open("Data/Status.dat", "w")
                cPickle.dump(self.StatusSet, fp)
            finally:
                fp.close()
        print "The StatusSet Now:"
        print self.StatusSet
        print 'Spliting the current into pieces of periods......'
        self.__CutToTheSame(self.__Split())
        del self.a
        del self.v
        print 'Generating Current Vectors By FFT......'
        self.__FFTTrans(self.c)
        """
        Generate the Dev Data
        """
        self.DevResult = []
        for x in range(0, devout):
            pos = int(np.random.rand()*len(self.f))
            self.DevResult.append({'status': self.Status,
                                   'current': self.f[pos]})
        return

        """
            try:
                fp = open("Data/DevSet.dat", "r")
                DevData = cPickle.load(fp)
            except:
                fp = open("Data/DevSet.dat", "w")
                DevData = {}
                cPickle.dump(DevData, fp)
            finally:
                fp.close()


       # TODO:change the method f[10]

            if self.pid != 99:
                DevData[(self.pid, self.state)] = self.f[10]
            try:
                fp = open("Data/DevSet.dat", "w")
                cPickle.dump(DevData, fp)
            finally:
                fp.close()
    """
