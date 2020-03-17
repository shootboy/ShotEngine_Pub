# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: settings.py
@Time: 2020/3/17 21:56
@Motto：I have a bad feeling about this.
"""
import pandas as pd
'setttings'
START_DT = None
END_DT = None
TRADE_PRICE = 'NextOpen'
SLIPPAGE_LEVEL = 1
TRADEFEE_LEVEL = 1
SLIPPAGE = 0.0003
UNIV = 'DXI'
CAPITAL = 4e6
SILENT_DAYS = 2
STYLE = None
# ACCOUNT_TYPE
#ACCOUNT_TYPE = ''
ACCOUNT_TYPE = 'FUTU'
#ACCOUNT_TYPE = 'SEC'
# tick
FREQ = 'tick'
#min1
FREQ = '1min'
#FREQ = '60min'
#day
#FREQ = 'day'

'data'
futures_path = r"C:\Users\surface\Downloads\database\futures.h5"

trade_cal = r"..\libraries\trade_calendar.csv"