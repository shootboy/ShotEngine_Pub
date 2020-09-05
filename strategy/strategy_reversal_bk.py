# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy_reversal_bk.py
@Time: 2020/3/24 11:15
@Motto：I have a bad feeling about this.
"""
from engine.strategy import StrategyBase
from engine.engine import *
import pandas as pd
import numpy as np

def Cal_ewmaVol(series, LamBda=0.98):
    """历史波动率计算ewma
    LamBda:衰减因子
"""
    sampleSize = len(series)
    Average = series.mean()

    e = np.arange(sampleSize - 1, -1, -1)
    r = np.repeat(LamBda, sampleSize)
    vecLambda = np.power(r, e)

    sxxewm = (np.power(series - Average, 2) * vecLambda).sum()
    Vart = sxxewm / vecLambda.sum()
    ewmaVol = np.sqrt(Vart)
    return ewmaVol

def sigmoid(X):
    "幂函数，对阈值管理"
    return 1.0 / (1 + np.exp(-float(X)))

def MOM(series):
    '''动量指标'''
    mean = np.mean(series)
    mom = (series - mean)*1. / mean
    #if np.isinf((100. * mom / (1 + mom))):
    #    return 0
    #else:
    return (100. * mom / (1 + mom))

class ST(StrategyBase):

    def __init__(self):
        super(ST, self).__init__()

    def on_init(self):
        '''全局参数'''
        self.price_list = []
        self.tr_day = None
        new_data = self.ctx.df_data['close'].to_frame().reset_index()
        new_data['datetime'] = pd.to_datetime(new_data['datetime'], format="%Y-%m-%d %H:%M:%S")
        new_data = new_data.set_index('datetime')
        day_data = new_data[['close', 'tradedate']].resample("D").last()
        #day_data = new_data[['close', 'tradedate']]
        day_data = day_data.dropna()
        day_data['log'] = np.log(day_data['close']).diff()  # resample 1日
        day_data['annual_vol'] = day_data['log'].rolling(3).apply(Cal_ewmaVol) * np.power(365, 0.5) * 100
        day_data['tradedate'] = day_data['tradedate'].shift(-1)
        day_data = day_data.reset_index().set_index('tradedate')
        print(day_data['annual_vol'].describe())
        self.annual_dict = day_data['annual_vol'].to_dict()
        self.tradedate = self.ctx.df_data.reset_index()['tradedate']
        self.datetime = self.ctx.df_data.reset_index()['datetime']

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        min_date = self.tradedate.values[i]
        price = self.ctx.df_data['close'].values[i]
        dt = datetime.strptime(self.datetime.values[i], '%Y-%m-%d %H:%M:%S')
        annual_vol = None
        if min_date in self.annual_dict.keys():
            annual_vol = self.annual_dict[min_date]
        else:
            pass
        self.price_list.append(price)
        if len(self.price_list) > 480:
            self.price_list.pop(0)
            mom = sigmoid(MOM(self.price_list)[-1])
            kurt = pd.Series(self.price_list).kurt()
            if annual_vol != None:
                if annual_vol > 25:
                    if mom > 0.7 and kurt > 2.5:
                        self.send_pos(-1, self.tr_day)
                        self.tr_day = dt
                    elif mom < 0.3 and kurt > 2.5:
                        self.send_pos(1, self.tr_day)
                        self.tr_day = dt
            if self.tr_day != None and pos != 0:
                if (dt - self.tr_day) >= timedelta(minutes=1440):
                    self.send_pos(0, self.tr_day)

# @profile
def main():
    'setttings'
    settings.START_DT = '20160301'
    settings.END_DT = '20200801'
    settings.TRADE_PRICE = 'NextOpen'
    settings.SLIPPAGE = 0.0001    # 范围 从千分之一到万分之一
    settings.UNIV = 'm'
    settings.CAPITAL = 2e7
    settings.SILENT_DAYS = 2

    st = ST()
    bk = Engine(st, settings.UNIV, settings.START_DT, settings.END_DT)
    bk.run()

if __name__ == '__main__':
    main()