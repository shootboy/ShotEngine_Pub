# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: day_volatility.py
@Time: 2020/3/19 17:02
@Motto：I have a bad feeling about this.
计算每日历史波动率
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

class ST(StrategyBase):

    def __init__(self):
        super(ST, self).__init__()

    def on_init(self):
        '''全局参数'''
        new_data = self.ctx.df_data['close'].to_frame().reset_index()
        new_data['datetime'] = pd.to_datetime(new_data['datetime'], format="%Y-%m-%d %H:%M:%S")
        new_data = new_data.set_index('datetime')
        day_data = new_data[['close', 'tradedate']].resample("D").last()
        day_data = day_data.dropna()
        day_data['log'] = np.log(day_data['close']).diff()  # resample 1日
        day_data['annual_vol_3'] = day_data['log'].rolling(3).apply(Cal_ewmaVol) * np.power(365, 0.5) * 100
        day_data['annual_vol_7'] = day_data['log'].rolling(7).apply(Cal_ewmaVol) * np.power(365, 0.5) * 100
        day_data['annual_vol_20'] = day_data['log'].rolling(20).apply(Cal_ewmaVol) * np.power(365, 0.5) * 100
        day_data['annual_vol_60'] = day_data['log'].rolling(60).apply(Cal_ewmaVol) * np.power(365, 0.5) * 100
        day_data = day_data.reset_index().set_index('tradedate')
        self.annual_dict = day_data['annual_vol_20'].to_dict()
        self.tradedate = self.ctx.df_data.reset_index()['tradedate']
        self.datetime = self.ctx.df_data.reset_index()['datetime']
        path = r'..\performance\{}_day_volatility.csv'.format('m')
        day_data.to_csv(path)

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        # shares = 100
        # cur_pos = self.ctx.pos
        # # i = self.cur_bar_i
        pass

# @profile
def main():
    'setttings'
    settings.START_DT = '20160201'
    settings.END_DT = '20200809'
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