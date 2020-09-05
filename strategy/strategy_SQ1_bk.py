# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy_SQ1_bk.py
@Time: 2020/6/30 17:02
@Motto：I have a bad feeling about this.
"""
from engine.strategy import StrategyBase
from engine.engine import *
import pandas as pd
import numpy as np

def CCI(dataframe, LamBda=0.015, period = 20):
    """
    :param LamBda: 衰减因子
    :return:
    """
    tp = 1.*(dataframe['high']+dataframe['low']+dataframe['close'])/3
    mean = dataframe['close'].rolling(period).mean()
    std = dataframe['close'].rolling(period).std()
    dataframe['cci'] = 1.*(tp-mean)#/(1.*std*LamBda)
    return dataframe['cci']

def BBandWithRatio(df, period=6, multiple = 2.):
    mean = df['close'].rolling(period).mean()
    std = df['close'].rolling(period).std()
    df['BB_ratio'] = multiple*2.*std/mean
    return df['BB_ratio']

def TR(df, period=20):
    high = df['high'].rolling(period).max()
    low = df['low'].rolling(period).max()
    preClose = df['close'].shift(1)
    tr1 = abs(high - low).values
    tr2 = abs(high-preClose).values
    tr3 = abs(low-preClose).values
    array = np.asarray([tr1, tr2, tr3])
    aa = np.lib.stride_tricks.as_strided(array, shape=(len(tr1), 3))
    return pd.Series(np.max(aa, axis=1))

def ATR(tr_array):
    return np.mean(tr_array)

def MACD(df, short_period, long_period, period):
    df['diff'] = df['close'].ewm(adjust=False, alpha=2/(short_period+1),ignore_na=True).mean()-\
        df['close'].ewm(adjust=False, alpha=2/(long_period+1),ignore_na=True).mean()
    df['dea'] = df['diff'].ewm(adjust=False, alpha=2/(period+1),ignore_na=True).mean()
    df['macd']=2*(df['diff']-df['dea'])
    return df

def EMA(data, period=20):
    " EMA"
    data = np.asarray(data)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(data, weights, mode='full')[:len(data)]
    a[:period] = a[period] #按period往前shift
    return a

def Xaverage(array):
    xav_list = []
    for num in np.arange(0, len(array)):
        if num == 0:
            xa = array[num]
        else:
            xa = (array[num] - xa) * 2 / (len(array)+1)
        xav_list.append(xa)
    return xav_list

def RSI(priceArray, period=7):
    df = pd.DataFrame(priceArray, columns=['data'])
    df['diff1'] = df['data'].diff()
    df['diff2'] = df['data'].diff(-1)
    df = df.fillna(0)
    df['bb'] = df['diff1'].apply(lambda x: max(float(x), 0))
    df['ff'] = df['diff2'].apply(lambda x: max(float(x), 0))
    df['rs'] = df['bb'].rolling(period).mean() / df['ff'].rolling(period).mean()
    df['rs'] = df['rs'].fillna(method='pad').fillna(method='bfill').fillna(0).apply(lambda x: 99 if x==np.inf else x)
    df['rsi'] = 100 * df['rs'] / (1 + df['rs'])
    return df['rsi'].fillna(50)

class ST(StrategyBase):

    def __init__(self):
        super(ST, self).__init__()

    def on_init(self):
        '''全局参数'''
        self.array = []
        self.high_array = []
        self.low_array = []

        self.OpenDaily = 0
        self.barNum = 0
        self.holdPrice = 0

        self.LongEntryCondition = False
        self.ShortEntryCondition = False

        self.datetime = self.ctx.df_data.reset_index()['datetime']
        self.time = self.datetime.apply(lambda x:x[-8:])

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        close = self.ctx.df_data['close'].values[i]
        high = self.ctx.df_data['high'].values[i]
        low = self.ctx.df_data['low'].values[i]
        dt = self.time.values[i]
        self.array.append(close)
        self.high_array.append(high)
        self.low_array.append(low)

        if dt == "09:00:00":
            self.OpenDaily = close

        if len(self.array)>1000:
            self.array.pop(0)
            self.high_array.pop(0)
            self.low_array.pop(0)
            price_dict = {
                'close':self.array,
                'high':self.high_array,
                'low':self.low_array
            }
            data = pd.DataFrame(price_dict)
            data['cci'] = CCI(data, period=120)
            data['BB_ratio'] = BBandWithRatio(data, period=36)
            data['highest'] = data['close'].rolling(270).max()
            data['lowest'] = data['close'].rolling(270).min()
            data['tr'] = TR(data, period=504)
            data['atr'] = data['tr'].rolling(270).mean()
            StopLoss = 0.64*data['atr'].values[-1]
            ProfitTarget = 95.
            macd_signal = MACD(data, short_period=78, long_period=42, period=42)['dea'].values[-1]
            #print(data['cci'].values[-1], close, data['highest'].values[-1]+data['BB_ratio'].values[-1]*2, data['lowest'].values[-1]+data['BB_ratio'].values[-1]*-2)
            if data['cci'].values[-1]<0 and close>(self.OpenDaily-100*data['tr'].values[-1]):
                if pos==0 and self.barNum==0 and close>(data['highest'].values[-1]+data['BB_ratio'].values[-1]*0.2):
                    self.send_pos(1, 1)
                    self.holdPrice = close
                    #print('long', self.datetime.values[i])

            if data['cci'].values[-1]>0 and close<(self.OpenDaily+100*data['tr'].values[-1]):
                if pos==0 and self.barNum==0 and close<(data['lowest'].values[-1]+data['BB_ratio'].values[-1]*-0.2):
                    self.send_pos(-1, -1)
                    self.holdPrice = close
                    #print('short', self.datetime.values[i])

            if pos!=0:
                self.barNum += 1  # 代替时间
                if pos>0:
                    # 时间平仓
                    if self.barNum > 318:
                        self.send_pos(0, 1)
                        self.barNum=0
                        #print('ltime', self.datetime.values[i])
                    # 信号平仓
                    #if qqe_signal>macd_signal:
                    # 止赢
                    if close>self.holdPrice+ProfitTarget:
                        self.send_pos(0, 1)
                        self.barNum = 0
                        #print('lprofit', self.datetime.values[i])
                    # 止损
                    if close<self.holdPrice-StopLoss:
                        self.send_pos(0, 1)
                        self.barNum = 0
                        #print('lloss1', self.datetime.values[i])
                    if close<(self.OpenDaily-100*data['tr'].values[-1]):
                        self.send_pos(0, 1)
                        self.barNum = 0
                        #print('lloss2', self.datetime.values[i])

                if pos<0:
                    # 时间平仓
                    if self.barNum > 318:
                        self.send_pos(0, -1)
                        self.barNum = 0
                        #print('time', self.datetime.values[i])
                    # 信号平仓
                    # if qqe_signal<macd_signal:
                    # 止赢
                    if close < self.holdPrice - ProfitTarget:
                        self.send_pos(0, -1)
                        self.barNum = 0
                        #print('profit', self.datetime.values[i])
                    # 止损
                    if close > self.holdPrice + StopLoss:
                        self.send_pos(0, -1)
                        self.barNum = 0
                        #print('loss1', self.datetime.values[i])
                    if close>(self.OpenDaily+100*data['tr'].values[-1]):
                        self.send_pos(0, -1)
                        self.barNum = 0
                        #print('loss2', self.datetime.values[i])

# @profile
def main():
    'setttings'
    settings.START_DT = '20170301'
    settings.END_DT = '20170401'
    settings.TRADE_PRICE = 'NextOpen'
    settings.SLIPPAGE = 0.0005    # 范围 从千分之一到万分之一
    settings.UNIV = 'rb'
    settings.CAPITAL = 2e7
    settings.SILENT_DAYS = 2

    st = ST()
    bk = Engine(st, settings.UNIV, settings.START_DT, settings.END_DT)
    bk.run()

if __name__ == '__main__':
    main()