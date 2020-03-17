# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: test.py
@Time: 2020/3/15 22:21
@Motto：I have a bad feeling about this.
"""
from datetime import date
from tqsdk import TqApi, TqSim, TqBacktest, TargetPosTask

api = TqApi(backtest=TqBacktest(start_dt=date(2018,5,1), end_dt=date(2018,10,1)))
klines = api.get_kline_serial("DCE.m1901", 5*60, data_length=15)
target_pos = TargetPosTask(api, "DCE.m1901")
while True:
    api.wait_update()
    if api.is_changing(klines):
        ma = sum(klines.close.iloc[-15:])/15
        print(klines.close.iloc[-1])