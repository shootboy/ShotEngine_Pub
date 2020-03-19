# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: tools.py
@Time: 2020/3/17 22:05
@Motto：I have a bad feeling about this.
"""
import pandas as pd

_convert2Date = lambda df: pd.to_datetime(df, format="%Y-%m-%d %H:%M:%S") # object to datetime
_days = lambda eqd: eqd.resample('D').last().dropna() # 换算成日期
_sharpe = lambda df: (df.mean() / df.std() if df.std()!=0 else 0) * (252 ** 0.5)
_winrate = lambda ser: len(ser[ser > 0]) * 100 / len(ser) - 1
_gainLoss = lambda ser: abs(ser[ser > 0].mean() / ser[ser < 0].mean())
_maxDD = lambda ser: 1*(ser / ser.expanding().max()- 1).min()