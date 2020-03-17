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

class ST1(StrategyBase):

    def __init__(self):
        super(ST1, self).__init__()

    def on_init(self):
        '''全局参数'''
        open = self.ctx.df_data['open'].values
        high = self.ctx.df_data['high'].values
        low = self.ctx.df_data['low'].values
        self.close = self.ctx.df_data['close'].values

    def on_bar(self, pos):
        i = self.ctx.cur_bar_i
        # shares = 100
        # cur_pos = self.ctx.pos
        # # i = self.cur_bar_i
        self.send_pos(0, 0)

# @profile
def main():
    'setttings'
    settings.START_DT = '20160104'
    settings.END_DT = '20160106'
    settings.TRADE_PRICE = 'NextOpen'
    settings.SLIPPAGE = 0.0002    # 范围 从千分之一到万分之一
    settings.UNIV = 'rb'
    settings.CAPITAL = 2e7
    settings.SILENT_DAYS = 2

    st = ST1()
    bk = Engine(st, settings.UNIV, settings.START_DT, settings.END_DT)
    bk.run()

if __name__ == '__main__':
    main()