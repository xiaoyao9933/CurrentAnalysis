# -*- coding: utf-8 -*-
"""
PreProcessModule

This file reads the data from two files and
Split the current with Voltage Zero points.
"""
import numpy as np
from PyQt4 import QtGui
import cPickle
import os
import xml.etree.ElementTree as ET
import VectorFilter as VF


class PreProcess:

    def __CutToTheSame(self, temp_c):
        length = 999999
        for item in temp_c:
            if len(item) < length:
                length = len(item)
        for item in temp_c:
            self.c.append(item[0:length - 1])
        return

    def __FFTTrans(self, x):
        # length=int((int(self.fsample/50)-20)/2)
        for item in x:
            self.f.append(
                [np.real(ele) / len(item) * 2
                    for ele in np.fft.fft(item)[1:11:2]] +
                [np.imag(ele) / len(item) * 2
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
        files = QtGui.QFileDialog.getOpenFileNames(
            None,
            "Select one or more files to open",
            "Data/",
            "XML files (*.xml)")
        self.DevResult = []
        for profile in files:
            filedir = os.path.split(profile.__str__())[0]
            tree = ET.parse(profile)
            root = tree.getroot()
            for sample in root.findall('sample'):
                self.fsample = int(sample.find('frequency').text)
                date = sample.find('date').text
                cfile = filedir + '/' + sample.find('cfile').text
                vfile = filedir + '/' + sample.find('vfile').text
                stype = sample.find('type').text
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
                    fp = open(cfile)
                    for line in fp:
                        self.a.append(float(line))
                finally:
                    fp.close()

                """
                Read the voltage
                """
                try:
                    fp = open(vfile)
                    for line in fp:
                        self.v.append(float(line))
                finally:
                    fp.close()
                """
                Read the profile
                """
                ele_devices = sample.find('devices')
                if 'single' in stype:
                    self.pid = int(ele_devices.find('device').get('pid'))
                    self.state = int(
                        ele_devices.find('device').find('state').text)
                else:
                    for device in ele_devices.findall('device'):
                        self.Status[int(device.get(
                            'pid'))] = int(device.find('state').text)

                try:
                    fp = open("Data/Status.dat", "r")
                    self.StatusSet = cPickle.load(fp)
                except:
                    fp = open("Data/Status.dat", "w")
                    self.StatusSet = {}
                    cPickle.dump(self.StatusSet, fp)
                finally:
                    fp.close()
                if 'single' in stype:
                    if self.pid not in self.StatusSet:
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
                if 'single' in stype:
                    VF.VectorFilter(self)
                else:
                    """
                    Generate the Dev Data
                    """
                    for x in range(0, devout):
                        # sample = np.array(self.f).mean(axis=0).tolist()
                        pos = int(np.random.rand() * len(self.f))
                        self.DevResult.append({'status': self.Status,
                                               'current': self.f[x + 5]})
        return
