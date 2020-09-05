# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy_rsi__bk.py
@Time: 2020/8/11 11:16
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
        self.ema_list = []
        self.ema_list2 = []

    def on_init(self):
        '''全局参数'''
        open = self.ctx.df_data['open'].values
        high = self.ctx.df_data['high'].values
        low = self.ctx.df_data['low'].values
        self.close = self.ctx.df_data['close'].values
        n=24
        self.ctx.df_data['wma'] = ((self.ctx.df_data['close']*self.ctx.df_data['vol'])/self.ctx.df_data['vol'].rolling(n).sum()).fillna(method="ffill")
        self.ctx.df_data['ema'] =self.ctx.df_data['wma'].rolling(n).apply(EMA).fillna(method="ffill")
        #self.ctx.df_data['ema2'] = self.ctx.df_data['close'].rolling(n2).apply(EMA).fillna(method="ffill")
        self.ctx.df_data['mom'] = self.ctx.df_data['ema'].rolling(n).apply(MOM)
        self.ctx.df_data['kurt'] = (self.ctx.df_data['close']-self.ctx.df_data['ema']).rolling(n).kurt()
        #print(self.ctx.df_data['ema2'])

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        # shares = 100
        # cur_pos = self.ctx.pos
        # # i = self.cur_bar_i
        kurt = self.ctx.df_data['kurt'].values[i]
        close = self.ctx.df_data['wma'].values[i]
        self.ema_list.append(close)
        self.ema_list.append(close)
        n = 12
        n2 = 24
        ema = close
        ema2 = close
        if len(self.ema_list)>n:
            ema=EMA(self.ema_list, n)
            self.ema_list.pop(0)
        if len(self.ema_list2)>n2:
            ema2=EMA(self.ema_list2, n2)
            self.ema_list2.pop(0)
        signal_up = ema2>ema
        signal_down = ema2<ema

        if kurt>=2.5:
            if signal_up and pos==0:
                self.send_pos(-1, 0)
            elif signal_down and pos==0:
                self.send_pos(1, 0)
        if pos!=0:
            if pos>0 and signal_up:
                self.send_pos(0, 0)
            if pos<0 and signal_down:
                self.send_pos(0, 0)

# @profile
def main():
    'setttings'
    settings.START_DT = '20160101'
    settings.END_DT = '20200801'
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