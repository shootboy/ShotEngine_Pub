# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: context.py
@Time: 2020/3/17 22:02
@Motto：I have a bad feeling about this.
"""
import pandas as pd
import numpy as np
from config import settings
import matplotlib.pyplot as plt
import datetime
from tools import tools
from datetime import datetime, timedelta
freq = settings.FREQ

path_dict ={
    '':{
    #    "tick":settings.tickCoin_data,
    #    "5min":settings.biteCoin_data,
    #    "1min":settings.biteCoin_data
    },
    'FUTU':{
        '1min':settings.futures_path,
        '60min':settings.futures_path,
        '30min':settings.futures_path
    },
    'SEC':{
    #    'day':settings.security_path
    }
}

path = path_dict[settings.ACCOUNT_TYPE][freq]

class Context:

    def __init__(self, univ, start_dt, end_dt):
        self.trade_price_mode = settings.TRADE_PRICE
        self.univ = univ

        self.start_dt = datetime.strptime(start_dt, "%Y%m%d")
        self.end_dt = datetime.strptime(end_dt, "%Y%m%d")
        '生成date index'
        if settings.ACCOUNT_TYPE == '':
            tl = self.end_dt - self.start_dt
            datelist = pd.date_range(self.start_dt, periods=tl.days).astype(str).tolist()
            datelist = [filter(str.isdigit, x) for x in datelist]
        else:
            tradecal = settings.trade_cal
            days = pd.read_csv(tradecal, index_col=0)
            days['calendarDate'] = pd.to_datetime(days['calendarDate'], format="%Y/%m/%d")
            days['datetime'] = days['calendarDate'].apply(lambda x: x.strftime("%Y%m%d"))
            days = days.set_index("datetime", drop=False)
            days = days.iloc[days.index.get_loc(start_dt):days.index.get_loc(end_dt)]
            datelist = days[days['isOpen'] == 1]['datetime'].values

        self.captial = settings.CAPITAL
        self.freq = settings.FREQ
        self.slippage_scale = settings.SLIPPAGE

        'pointers'
        self.cur_strategy = None  # 当前策略
        self.cur_bar_i = -1  # 1T bar的位置
        self.cur_tradeday = None
        self.cur_datetime = None

        'init data'
        datalist = []
        data = pd.HDFStore(path, mode='r')
        for date in datelist:
            key = "/%s/%s/%s" % (self.freq, self.univ, date)
            datalist.append(data.get(key))
        data.close()
        self.df_data = pd.concat(datalist).fillna(method='ffill').reset_index()
        print(self.df_data.columns)
        if "datetime" in self.df_data.columns:
            self.df_data['tradedate'] = self.df_data['datetime'].apply(lambda x: x.strftime('%Y%m%d'))
            self.df_data[ 'datetime'] = self.df_data[ 'datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            self.df_data = self.df_data.set_index(['tradedate', 'datetime'])
        else:
            self.df_data['tradedate'] = self.df_data['dt'].apply(lambda x: x.strftime('%Y%m%d'))
            self.df_data['datetime'] = self.df_data['dt'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            self.df_data = self.df_data.set_index(['tradedate', 'datetime'])
        if self.freq == "1min":
            # min
            self.df_data['trade_price'] = self.df_data['close'].shift(-1)

        self.df_data['transact_time'] = self.df_data.index.get_level_values(1)

        self.df_data['dt'] = self.df_data.index.get_level_values(1)  #
        self.df_data['dt'] = self.df_data['dt'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')) - timedelta(
            days=1)
        self.df_data['dt'] = self.df_data['dt'].apply(lambda x: x.strftime('%Y%m%d'))

        self.df_data['transact_time'] = self.df_data['transact_time'].shift(-1)

        # 指定格式
        self.df_data['close'] = self.df_data['close'].astype(float)
        self.df_data['open'] = self.df_data['open'].astype(float)
        self.df_data['high'] = self.df_data['high'].astype(float)
        self.df_data['low'] = self.df_data['low'].astype(float)
        self.df_data['bidprice'] = self.df_data['bidprice'].astype(float)
        self.df_data['askprice'] = self.df_data['askprice'].astype(float)

        self.df_data['vol'] = self.df_data['vol'].astype(int)
        self.df_data['bidvol'] = self.df_data['bidvol'].astype(int)
        self.df_data['askvol'] = self.df_data['askvol'].astype(int)
        self.df_data['amount'] = self.df_data['amount'].astype(int)
        self.df_data['open_interest'] = self.df_data['open_interest'].astype(int)

        self.data_index = self.df_data.index  # datetime index for loop
        self.data_cols = self.df_data.columns  # datetime index for loop
        self.col_id = dict(zip(self.data_cols, range(len(self.data_cols))))
        self.nd_data = self.df_data.values
        'blotter'
        self.cur_pos = 0
        self.order_list = []
        self.pending_orders = {}
        self.blotter = {}

    def send_pos(self, quantity, sigma):
        i = self.cur_bar_i
        j = self.col_id
        '生成单子order'
        # print self.nd_data[i,:]
        transact_time = self.nd_data[i, j['transact_time']]
        tradedate = self.data_index[i][0]
        order_time = self.data_index[i][1]
        symbol = self.univ
        target_quantity = quantity
        if "trade_price" in j.keys():
            trade_price = self.nd_data[i, j['trade_price']]
        else:
            trade_price = self.nd_data[i, j['close']]
        self.pending_orders[transact_time] = dict(
            zip(['tradedate', 'order_time', 'symbol', 'target_quantity', 'trade_price', 'sigma'],
                [tradedate, order_time, symbol, target_quantity, trade_price, sigma]))

    def execute(self):
        t = self.cur_datetime
        if self.pending_orders.get(t):
            order = self.pending_orders.get(t).copy()
            if order['target_quantity'] == self.cur_pos:
                return self.cur_pos
            else:
                self.exec_quantity = order['target_quantity'] - self.cur_pos
                self.cur_pos = order['target_quantity']
                'update'
                order['exec_quantity'] = self.exec_quantity
                order['eob_pos'] = self.cur_pos
                self.blotter[t] = order

            del self.pending_orders[t]
            return self.cur_pos
        else:
            return self.cur_pos

    def cover_order(self, order):
        order.name = self.cur_datetime
        order['exec_quantity'] = -order['eob_pos']
        order['target_quantity'] = 0
        order['order_time'] = None
        order['tradedate'] = self.cur_tradeday
        order['eob_pos'] = 0
        if self.freq == 'min1':
            # min
            order['trade_price'] = self.nd_data[-1][self.col_id['close']]
        elif self.freq == 'tick':
            # tick
            order['trade_price'] = self.nd_data[-1][self.col_id['trade_px']]
        return order

    def performance(self):
        if len(self.blotter) != 0:
            raw_result = pd.DataFrame.from_dict(self.blotter, orient='index')
            raw_result.index.name = 'transact_time'
            virtual_order = self.cover_order(raw_result.iloc[-1].copy())
            result = raw_result.append(virtual_order)
            result.to_csv(r'..\performance\blotter.csv')

            'calc pnl'
            result['gross_pnl'] = result['trade_price'].diff() * result['eob_pos'].shift(1)
            result['slippage'] = self.slippage_scale * abs(result['exec_quantity'])
            result['prop_pnl'] = result['gross_pnl'] - result['slippage'] * result['trade_price']
            result['cost'] = result['exec_quantity']
            result.index = tools._convert2Date(result.index)

            perf = result
            perf['pnl'] = result['prop_pnl'] + result['prop_pnl'].shift(-1)
            tract_time = perf.reset_index()['transact_time']

            # winrate # -2000 估算slippage
            winrate = tools._winrate(perf[perf['eob_pos'] != 0]['pnl'])
            # 盈亏比
            gainLoss = tools._gainLoss(perf[perf['eob_pos'] != 0]['pnl'])
            # maxdrawndown
            maxDD = tools._maxDD(perf['prop_pnl'].cumsum())
            # sharpe
            sharpe = tools._sharpe(perf['prop_pnl'].dropna().cumsum().resample('D').last())
            print(tools._sharpe(perf['gross_pnl'].dropna().cumsum()))
            print(perf)
            perf.to_csv(r"..\performance\perf.csv")
            print("=" * 5, "Performance", "=" * 5)
            ss = perf.reset_index()
            open = ss[ss['eob_pos'] != 0]['transact_time'].to_frame('open').reset_index()
            close = ss[ss['eob_pos'] == 0]['transact_time'].to_frame('close').reset_index()
            holdtime = pd.concat([open['open'], close['close']], axis=1).dropna()
            print("pnl_sum:", perf['pnl'].sum())
            print("Trade_Times:", perf.count())
            print("Hold Avg Time:", (holdtime['close'] - holdtime['open']).describe())
            print("Sharpe:", sharpe, '\n', "Rate(%):", winrate, '\n', "Gain/Loss:", gainLoss, '\n', "maxDD(%):", maxDD)
            print("Kelly F:", - (winrate) / gainLoss + (100 - winrate), "Kelly F2:", - (100 - winrate) / gainLoss + winrate)
            print("=" * 5, "Performance", "=" * 5)
            'plot'
            fig1 = plt.figure(figsize=(12, 12 * 0.618))
            fig1.suptitle('sharpe:' + str(sharpe))
            ax = fig1.add_subplot('111')
            ax1 = result['gross_pnl'].cumsum().plot(linestyle='-', color='green', legend=True, ax=ax)
            ax2 = result['prop_pnl'].cumsum().plot(linestyle='-.', color='blue', legend=True, ax=ax, secondary_y=True)
            plt.show()
        else:
            print("Nothing gonna change my love for you!")