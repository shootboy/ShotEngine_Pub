#!python2
# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: test.py
@Time: 2020/3/25 16:35
@Motto：I have a bad feeling about this.
"""
import pandas as pd
import numpy as np
def Xaverage(array):
    xav_list = []
    for num in np.arange(0, len(array)):
        if num == 0:
            xa = array[num]
        else:
            xa = (array[num] - xa) * 2 / (len(array)+1)
        xav_list.append(xa)
    return xav_list
def EMA(data, period=20):
    " EMA"
    data = np.asarray(data)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(data, weights, mode='full')[:len(data)]
    a[:period] = a[period]  # 按period往前shift
    return a
a = [1,2]
b = [2,3]
print(np.convolve(a, b))
sampleSize = 10
LamBda=0.98
e = np.arange(sampleSize - 1, -1, -1)
r = np.repeat(LamBda, sampleSize)
vecLambda = np.power(r, e)
print(e)
sss = np.arange(1,50)
print(sss)
print(Xaverage(sss))
print(EMA(sss))