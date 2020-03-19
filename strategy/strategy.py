# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy.py
@Time: 2020/3/17 22:26
@Motto：I have a bad feeling about this.
"""
from config import settings
import pandas as pd
import numpy as np
from engine.strategy import StrategyBase
from engine.engine import *
futures_path = r"C:\Users\surface\Downloads\database\futures.h5"
#dd = pd.HDFStore(futures_path)
#print(dd.keys())

def EMA(data, period=20):
    " EMA"
    data = np.asarray(data)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(data, weights, mode='full')[:len(data)]
    a[:period] = a[period]  # 按period往前shift
    return a[-1]

def sigmoid(X):
    "幂函数，对阈值管理"
    return 1.0 / (1 + np.exp(-float(X)))

def MOM(series):
    '''动量指标'''
    mean = np.mean(series)
    #print mean
    mom = (series - mean)*1. / mean
    return (100. * mom / (1 + mom))[-1]

class ST1(StrategyBase):

    def __init__(self):
        super(ST1, self).__init__()

    def on_init(self):
        '''全局参数'''
        open = self.ctx.df_data['open'].values
        high = self.ctx.df_data['high'].values
        low = self.ctx.df_data['low'].values
        self.close = self.ctx.df_data['close'].values
        n= 1000
        self.ctx.df_data['ema'] =self.ctx.df_data['close'].rolling(n).apply(EMA)
        self.ctx.df_data['mom'] = self.ctx.df_data['ema'].rolling(n).apply(MOM)
        self.ctx.df_data['kurt'] = (self.ctx.df_data['close']-self.ctx.df_data['ema']).rolling(n).kurt()

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        # shares = 100
        # cur_pos = self.ctx.pos
        # # i = self.cur_bar_i
        kurt = self.ctx.df_data['kurt'].values[i]
        mom = self.ctx.df_data['mom'].values[i]
        if kurt>=2.5:
            if mom>0.7 and pos==0:
                self.send_pos(1, 0)
            elif mom<0.3 and pos==0:
                self.send_pos(-1, 0)
        if pos!=0:
            if pos>0 and mom<0.7:
                self.send_pos(0, 0)
            if pos<0 and mom>0.3:
                self.send_pos(0, 0)

# @profile
def main():
    'setttings'
    settings.START_DT = '20190101'
    settings.END_DT = '20200101'
    settings.TRADE_PRICE = 'NextOpen'
    settings.SLIPPAGE = 0.0001    # 范围 从千分之一到万分之一
    settings.UNIV = 'rb'
    settings.CAPITAL = 2e7
    settings.SILENT_DAYS = 2

    st = ST1()
    bk = Engine(st, settings.UNIV, settings.START_DT, settings.END_DT)
    bk.run()

if __name__ == '__main__':
    main()