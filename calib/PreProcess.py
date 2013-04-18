# -*- coding: utf-8 -*-
"""
PreProcessModule

This file reads the data from two files and
Split the current with Voltage Zero points.
"""
import numpy as np
from PyQt4 import QtGui
import cPickle
import os,copy
from scipy import signal
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

    def __shape(self, x):
        f = []
        # length=int((int(self.fsample/50)-20)/2)
        for item in x:
            f.append([ele.real for ele in item[1:255:2]] + [ele.imag for ele in item[1:255:2]])
        return f

    def _filterLJJ(self,data,b,a):
        return signal.lfilter(b,a,data)
    
    def _maxPos(self,a):
        t=0;    
        for i in range(len(a)):
            if a[i]>a[t]:
                t=i
        return t;
    def _Vdaq(self,din, d,N):
        out=[]
        for t in range(N):
            x=d*t
            xf=int(x)
            xc=int(x)+1
            xd=x-xf
            out.append(din[xf]*(1-xd)+din[xc]*xd);
        return out   
    def _yipin(self,v,fs):
        fs=float(fs)
        f0=49.5
        fsign=50.0
        
        start=12000;#startpoint
        dur=10
        
        t=[v[i]*np.exp(-2j*np.pi*f0*i/fs) for i in range(len(v))]
        #print t[1]
        
        
        norm_pass = 1/(fs/2)
        
        norm_stop = 40/(fs/2)
        
        (b, a) = signal.iirdesign(wp=norm_pass, ws=norm_stop, gpass=0.50, gstop=60.0,ftype="cheby2")
        
        y = signal.lfilter(b, a, t)
        
        dx=dur*fsign;#
        
        fy=np.fft.fft([y[start+i*dx] for i in range(int(dur*fs/dx))]);
        ps=self._maxPos(np.abs(fy))
        print "max at", ps,"sf equal ",ps*1.0/dur
        f=f0+ps*1.0/dur
        d=fsign/f
        N=int((len(v)-10)//d);
        rv=self._Vdaq(v,d,N)
        return (rv,f)
    
    def _encodeMD(self,a,b):
        x=copy.deepcopy(b);
        n=np.size(a,1);
        for i in range(1,n/2):
            a[:,i]=a[:,i]/x;
            a[:,i]=a[:,i]*np.abs(x);
            x=x*b;
            x=x/abs(b);
    def _decodeMD(self,a,b):
        x=copy.deepcopy(b);
        n=np.size(a,1);
        for i in range(1,n/2):
            a[:,i]=a[:,i]*x;
            a[:,i]=a[:,i]/np.abs(x);
            x=x*b;
            x=x/abs(b);


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
                self.percircle = int (self.fsample/50)
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
                print len(self.v), len(self.a)
                rv,f1=self._yipin(self.v,self.fsample);
                ra,f2=self._yipin(self.a,self.fsample);
                print f1,f2
                del self.a
                del self.v
                nv=len(rv)//self.percircle*self.percircle
                na=len(ra)//self.percircle*self.percircle
                rv=np.array(rv[0:nv])
                ra=np.array(ra[0:na])
                rv=np.array(rv).reshape((nv/self.percircle,self.percircle))
                self.ra=np.array(ra).reshape((na/self.percircle,self.percircle))
                self.fv=-np.fft.fft(rv)/self.percircle/2
                self.fa=np.fft.fft(self.ra)/self.percircle/2
                min_len=min([len(self.fv),len(self.fa)])
                self.fv=self.fv[0:min_len]
                self.fa=self.fa[0:min_len]
                self._encodeMD(self.fa,self.fv[:,1])
                self.f = self.__shape(self.fa)
                
                print 'Generating Current Vectors By FFT......'
                #self.__FFTTrans(self.c)
                
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
                                               'current': self.f[x + 115]})
        return
