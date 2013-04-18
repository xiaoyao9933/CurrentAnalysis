# -*- coding: utf-8 -*-
'''
File: OptimizeWeight.py
Author: xiaoyao9933
Description: This module is used to handle a DevSet, and
    computes the best parameters after several loops.
'''
import numpy as np
import StatusSearch
import cPickle
import matplotlib.pyplot as plt
import copy

class Optimizer:
    def GetCrossOver(self, line1, line2, index):
        # line Format: (k,b,{})
        """
        Get the crossovers of two lines.
        index is the index of line2
        """
        k1 = float(line1[0])
        k2 = float(line2[0])
        b1 = float(line1[1])
        b2 = float(line2[1])
        if k1 == k2:
            return None
        else:
            m = (b2 - b1) / (k1 - k2)
            n = (k1 * b2 - b1 * k2) / (k1 - k2)
            return (m, n, index)

    def LineCmp(self, x, y):
        """
        Compare the slopes of line . Ascending order.
        """
        if(x[0] > y[0]):
            return 1
        elif(x[0] == y[0] and x[1] < y[1]):
            return 1
        elif(x[0] == y[0] and x[1] == y[1]):
            return 0
        else:
            return -1

    def PointCmp(self, x, y):
        """
        Compare the points. Ascending order.
        """
        if(x[0] > y[0]):
            return 1
        else:
            return -1

    def ScoreCmp(self, x, y):
        """
        Compare the scores. Descending order.
        """
        if(x[0] < y[0]):
            return 1
        else:
            return -1          

    def ErrorCmp(self, x, y):
        """
        Compare the errors. Ascending order.
        """
        if(x[1] > y[1]):
            return 1
        elif(x[1]==y[1]):
            if(x[2]>y[2]):
                return 1
            else:
                return -1
        else:
            return -1          

    def ComputeError(self, status1, status2):
        """
        Compute the euler distance of two statuses.
        """
        tsum = 0
        try:
            for x in status1:
                if x not in status2:
                    tsum = tsum + (status1[x] - 0) ** 2
                else:
                    tsum = tsum + (status1[x] - status2[x]) ** 2
            return np.sqrt(tsum)
        except:
            print status1, status2
            
    def ComputeTrainSetScore(self, TargetStatus, TrainSet, lamatas):
        columnerror = 0
        # ranker  -->[errors,...]
        ranker = []
        for x in TrainSet:
            score = 0
            IsAllClosed = 0 
            for pid in x['status']:
                IsAllClosed += x['status'][pid]
            if IsAllClosed > 0:
                for dim in range(0,len(lamatas)):
                    score += lamatas[dim] * x['h'][dim]
                ranker.append([score, self.ComputeError(x['status'], TargetStatus),x['status']])
        ranker.sort(cmp=self.ScoreCmp)
        # Formula columnerror = rank[i]*exp(error[i])
        #print lamatas,ranker
        rank0 = 0
        for rank in range(0, len(ranker)):
            if ranker[rank]==0:
                rank0=rank
            for rank1 in range(0,rank):
                if ranker[rank][1]<ranker[rank1][1]:
                    columnerror += np.exp(-2*ranker[rank][1])
        return rank0, columnerror
        
    def PlotCritical(self,k,b):
        x = np.arange(-100,100,1)
        y = [k*ele+b for ele in x]
        plt.plot(x,y,'b')
    def ComputeCriticalPoints(self, lamatas, TrainSet, dim):
        """
        Refered to argorithms of ML.
        Format
        Critical Points:[[lamatas],((hs),{pid:status,...}),....],dim int
        Fix one dim,and generate the lines set.
        lines Format: (k,b,{pid:status})
        """
        plt.ioff()
        plt.figure()
        Lines = []
        CriticalPoints = []
        #Get fixed dim parameters.
        for x in TrainSet:
            k = x['h'][dim]
            b = 0
            for y in range(0, len(lamatas)):
                if y != dim:
                    b = b + lamatas[y] * x['h'][y]
            Lines.append((k, b, x['status']))
            self.PlotCritical(k,b)

        # Sort the lines
        Lines.sort(cmp=self.LineCmp)
        LastPoint = (-np.inf, -np.inf)
        x = 0
        """
        Begin the algorithms of finding critical points
        1.Sort by the k
        2.choose the first line 
        3.Compute the cross points of the selected line with the followed lines.
        4.Kick the points on the left of the last cross points.
        5.Get the highest point as the critical points and  the corresponed line as the next loop's line.
        """
        while x < len(Lines):
            points = []
            for y in range(x + 1, len(Lines)):
                if Lines[x][0] != Lines[y][0]:
                    point = self.GetCrossOver(Lines[x], Lines[y], y)
                    if point:
                        points.append(point)
            # Kick the points on left of the last crossover point
            tmp = range(0, len(points))
            tmp.sort(reverse=True)
            # Pop from the back
            for z in tmp:
                if points[z][0] <= LastPoint[0]:
                    points.pop(z)
            # Sort the Points, and the the highest one in y-axis will be choose as the critical points.
            if len(points) != 0:
                points.sort(cmp=self.PointCmp)
                CriticalPoints.append(
                    (LastPoint[0], points[0][0], Lines[x][2]))
                LastPoint = points[0][0:2]
                plt.plot(points[0][0],points[0][1],'r*')
                # Choose the new selected line for new loop.
                x = points[0][2]
            else:
                # If no more cross points,return the criticalpoints
                CriticalPoints.append((LastPoint[0], np.inf, Lines[x][2]))
                # print CriticalPoints
                # plt.show()
                return CriticalPoints

    def Merge(self, lists):
        """
        This method merges the lists and unique the items.
        """
        s = []
        for x in lists:
            s = s + x
        s = set(s)
        s = list(s)
        s.sort()
        return s
    # This will find the status of pos in range

    def FindStatus(self, CriPoint, pos):
        """
        Given a pos, we find the range which the pos in.
        Result is the status corresponed with the range.
        """
        for x in CriPoint:
            if pos > x[0] and pos <= x[1]:
                return x[2]
        return None

    def MergeCritical(self, CriPoints):
        """
        This just merge the cripoints into one dataset.
        """
        lists = []
        # Reshape the critical points
        for x in CriPoints:
            tmp = [-np.inf]
            for y in x:
                tmp.append(y[1])
            lists.append(tmp)
        # Merge the points
        MergeList = self.Merge(lists)
        # print MergeList
        MergeResult = {}
        # print CriPoints
        for pos in MergeList:
            for time in CriPoints:
                if (pos in MergeResult) is False:
                    MergeResult[pos] = []
                MergeResult[pos].append(self.FindStatus(time,
pos))  # Merge Status
        # print MergeResult
        # Reshape to range style
        MergeResult2 = []
        Sum = 0
        last = -np.inf
        keys = MergeResult.keys()
        keys.sort()
        for x in keys:
            if x != -np.inf:
                MergeResult2.append((last, x, MergeResult[x]))
                scale = np.abs(last-x)
                if scale != np.inf:
                    Sum += scale
                last = x
        R = Sum / len(MergeResult2) / 2
        if R==0:
            R = 1
        # Reshape to selected point style
        Result = []
        for x in MergeResult2:
            if x[0] == -np.inf:
                Result.append((x[1] - R, x[2]))
            elif x[1] == np.inf:
                Result.append((x[0] + R, x[2]))
            else:
                Result.append(((x[0] + x[1]) / 2, x[2]))
        del MergeResult2,MergeResult
    
        return Result

    def CalError(self, MergeResult, DevSet, TrainSet, lamatas, dim):
        """
        Calculate the scores between the target status and critical status.
        """
        copy_lamatas = copy.deepcopy(lamatas)
        try:
            Result = []
            # print MergeResult
            for x in MergeResult:
                rank0_error = 0
                column_error = 0
                copy_lamatas[dim] = x[0]
                for time in range(0, len(DevSet)):
                    tmp = self.ComputeTrainSetScore(DevSet[time]['status'], TrainSet[time], copy_lamatas)
                    rank0_error += tmp[0]
                    column_error += tmp[1]
                rank0_error = rank0_error / len(DevSet)
                column_error = column_error/ len(DevSet)
                Result.append((x[0], rank0_error, column_error))
            return Result
        except:
            print MergeResult
            exit(0)
    def SelectWeight(self, CriPoints, DevSet,TrainSet, lamatas, dim):
        """
        Since we have get different cripoints from devsets. We then need merge the criPoints. And compute the scores and sort.
        """
        # R is a const num when critical points occur in the edge of two sides
        # 1:Merge the critical points
        Result = self.MergeCritical(CriPoints)
        # 2:Calculate the score
        Result = self.CalError(Result, DevSet, TrainSet, lamatas, dim)
        # print Result
        
        # 3:Sort and find the highest score
        Result.sort(cmp=self.ErrorCmp)
        # 4:Return the result
        return Result[0]

    def Optimize(self, DevSet, TrainSet, lamatas):
        """
        It runs a procedure of optimizing in every dims ofTrainSet and every dims of lamatas. 
        Result: (lamatas,minerror) minerror is the minimum error ever occurs in Optimize.
        """
        # TODO: Not use the minerror
        dims = len(lamatas)
        minerror = np.inf
        self.CriPoints = []
        for dim in range(0, dims):
            self.CriPoints = []
            for time in TrainSet:
                self.CriPoints.append(
                    self.ComputeCriticalPoints(lamatas, TrainSet[time], dim))
            lamatas[dim], rank0_error,c_error = self.SelectWeight(self.CriPoints, DevSet, TrainSet, lamatas, dim)
            #print self.CriPoints
            print rank0_error,c_error
            if rank0_error + c_error< minerror:
                minerror = rank0_error + c_error
        return (lamatas, minerror)

    def OptimizeIterator(self, DevSet, lamatas, N):
        """
        This is the entrance of Optimizer
        DevSet: [{'status':..,'current'},{...},...]
        lamatas: [a1,a2,a3]
        N: int ,the number of returned results
        """
        lasterror = 0
        newerror = 10
        epsilon = 0.001
        iternum = 0
        Maxiter = 10
        self.MergeResult = []
        #Initializing the searcher.
        self.searcher = StatusSearch.Searcher()
        while iternum < Maxiter and np.abs(newerror-lasterror)>= epsilon:
            print "#Iterating %d:"%(iternum + 1)
            print "##Generating TrainSet......"
            self.TrainSet = self.searcher.StatusSearch(lamatas, N, DevSet)
            print "##Optimizing Weights......"
            lamatas, minerror = self.Optimize(DevSet, self.TrainSet, lamatas)
            lasterror = newerror
            newerror = minerror
            iternum = iternum + 1
            print "##error is :%f"%(abs(lasterror - newerror))
            print "##Total error is :%f"%(minerror)
            print "##Lamatas:", lamatas
        if iternum >= Maxiter:
            print "Exit iterating for maxiter times"
        if abs(lasterror - newerror) <= epsilon:
            print "Iterating Success"
            self.lambdas = lamatas
        # Write the optimized result into files
        try:
            fp = open("Data/lamatas.dat", 'w')
            cPickle.dump(lamatas, fp)
        except:
            print 'Open file error'
        finally:
            fp.close()
        # del self.searcher
        return lamatas
