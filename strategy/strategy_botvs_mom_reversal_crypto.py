#!python2
# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy_botvs_mom_reversal_crypto.py
@Time: 2020/3/19 11:34
@Motto：I have a bad feeling about this.
"""
from datetime import datetime, timedelta
from time import sleep
import numpy as np
import pandas as pd

# 默认空值
EMPTY_STRING = ''
EMPTY_UNICODE = u''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0

class BarData(object):
    """K线数据"""

    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所

        self.open = EMPTY_FLOAT  # OHLC
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.close = EMPTY_FLOAT

        self.date = EMPTY_STRING  # bar开始的时间，日期
        self.time = EMPTY_STRING  # 时间
        self.datetime = None  # python的datetime时间对象

        self.volume = EMPTY_INT  # 成交量
        self.openInterest = EMPTY_INT  # 持仓量

        # 新增
        self.cumVp = EMPTY_FLOAT  # 成交量价格
        self.VwPrice = EMPTY_FLOAT  # 成交量加权平均价格

class Position(object):

    def __init__(self):
        self.long_qty = 0 #多仓数量
        self.long_avail_qty = 0 #多仓可平仓数量
        self.long_pnl_ratio = 0. #多仓盈亏比
        self.long_avg_cost = 0.  # 开仓平均价
        self.short_qty = 0 #空仓数量
        self.short_avail_qty = 0
        self.short_pnl_ratio = 0.
        self.short_avg_cost = 0.#开仓平均价
        self.instrument_id =''
        self.last = 0. #最新成交价
        self.allpos = 0
        self.creat_time = datetime.now()
        self.update_time = datetime.now()

class Ticker(object):

    def __init__(self):
        self.instrument_id = ""
        self.Last = 0.
        self.Sell = 0.
        self.Buy = 0.
        self.datetime = datetime.utcnow()

class Orders(object):

    def __init__(self):
        self.filled_qty = 0
        self.instrument_id = ""
        self.order_id = ""
        self.order_type = ""
        self.price = 0.
        self.price_avg = 0.
        self.size = 0
        self.state = ""
        self.status = ""
        self.datetime = datetime.utcnow()
        self.type = ""
        self.length = 0

class Account(object):

    def __init__(self):
        self.currency = 0.#账户余额币种
        self.margin_mode=''#账户类型逐仓：fixed
        self.fixed_balance=0.#逐仓账户余额
        self.available_qty=0.#逐仓可用余额
        self.margin_frozen=0.#持仓已用保证金
        self.margin_for_unfilled=0.#挂单冻结保证金
        self.instrument_id=''#合约ID，如BTC - USD - 180213，BTC - USDT - 191227
        self.realized_pnl=0.#已实现盈亏
        self.unrealized_pnl=0.#未实现盈亏
        self.equity=0.#账户权益（账户动态权益）
        self.total_avail_balance=0.#账户余额（账户静态权益）
        self.auto_margin=''#是否自动追加保证金1: 自动追加已开启0: 自动追加未开启
        self.liqui_mode=''#强平模式：tier（梯度强平）
        self.can_withdraw=0.#可划转数量

def utctime(cfs):
    try:
        utc_st = datetime.strptime(cfs, '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception as e:
        utc_st = datetime.strptime(cfs, '%Y-%m-%dT%H:%M:%SZ')
    return utc_st

class BarGenerator(object):

    def __init__(self, onBar, onNmBar, onNsecond, nMin, nSecond):
        self.bar = None  # 1分钟K线对象
        self.bar2 = None
        self.onBar = onBar  # 1分钟K线回调函数
        self.bardict = {}

        self.nbar = None  # n分钟
        self.onNmbar = onNmBar
        self.onNsecond = onNsecond

        self.nMin = nMin  # 分钟参数
        self.nSecond = nSecond

    def upDateNSecond(self, ticker):
        "n秒应用"
        dt = datetime.fromtimestamp(ticker[0].Time / 1000)
        if not (dt.second) % self.nSecond:
            self.onNsecond(ticker)
        else:
            pass

    def upDateTick(self, ticker):
        "1min"
        dt = datetime.fromtimestamp(ticker.Time / 1000)
        # Log(dt.minute, self.bar.datetime.minute)
        # handle
        newMinute = False
        # ================ BAR 1==========================
        if not self.bar:
            self.bar = BarData()
            newMinute = True
        # 新的一分钟
        elif self.bar.datetime.minute != dt.minute:
            # 生成上一分钟K线的时间戳
            self.bar.datetime = self.bar.datetime.replace(second=0, microsecond=0)  # 将秒和微秒设为0
            self.bar.date = self.bar.datetime.strftime('%Y%m%d')
            self.bar.time = self.bar.datetime.strftime('%H:%M:%S')
            # 推送已经结束的上一分钟K线
            if self.bar.volume == 0:
                self.bar.VwPrice = 0
            else:
                self.bar.VwPrice = self.bar.cumVp / self.bar.volume
            self.onBar(self.bar)

            # 创建新的K线对象
            self.bar = BarData()
            newMinute = True

        # 初始化新一分钟的K线数据
        if newMinute:
            self.bar.open = ticker.Last
            self.bar.high = ticker.Last
            self.bar.low = ticker.Last
            self.bar.cumVp = float(ticker.Last) * float(ticker.Volume)
            self.bar.close = ticker.Last
            self.bar.bidprice = ticker.Buy
            self.bar.askprice = ticker.Sell
            self.bar.volume = ticker.Volume
            self.bar.vol = ticker.Volume
            # Log(self.bar.high, self.bar.low, self.bar.cumVp, self.bar.volume)
        # 累加更新老一分钟的K线数据
        else:
            self.bar.high = max(self.bar.high, ticker.Last)
            self.bar.low = min(self.bar.low, ticker.Last)
            self.bar.cumVp += ticker.Last * ticker.Volume
            self.bar.volume += ticker.Volume
            self.bar.close = ticker.Last
            self.bar.bidprice = ticker.Buy
            self.bar.askprice = ticker.Sell
            self.bar.vol = ticker.Volume
            # Log(self.bar.high, self.bar.low, self.bar.cumVp, self.bar.volume)

        # 通用更新部分
        self.bar.close = ticker.Last
        self.bar.datetime = dt

    def upDateBar(self, bar):
        if not self.nbar:
            self.nbar = BarData()
            self.nbar.open = bar.open
            self.nbar.high = bar.high
            self.nbar.low = bar.low
            self.nbar.datetime = bar.datetime
            self.nbar.cumVp = bar.close * bar.volume
        else:
            self.nbar.high = max(self.nbar.high, bar.high)
            self.nbar.low = min(self.nbar.low, bar.low)
            self.nbar.cumVp += bar.close * bar.volume

        self.nbar.close = bar.close
        self.nbar.volume += bar.volume

        # n分时数据推送
        if not (bar.datetime.minute + 1) % self.nMin:
            self.nbar.datetime = self.nbar.datetime.replace(second=0, microsecond=0)  # 将秒和微秒设为0
            self.nbar.date = self.nbar.datetime.strftime('%Y%m%d')
            self.nbar.time = self.nbar.datetime.strftime('%H:%M:%S.%f')
            try:
                self.nbar.VwPrice = self.nbar.cumVp * 1. / self.nbar.volume
            except Exception:
                self.nbar.VwPrice = 0

            self.onNmbar(self.nbar)
            self.nbar = None

class Tools(object):

    def sigmoid(self, X):
        "幂函数，对阈值管理"
        return 1.0 / (1 + np.exp(-float(X)))

class Indicators(object):

    def nan_interp(self, data):
        "插值处理"
        data = np.asarray(data)
        reverse = -np.isnan(data)  # 反向判断
        location = reverse.ravel().nonzero()[0]  # True的下标位置
        getNonZero = data[-np.isnan(data)]  # 非零组合
        getZero = np.isnan(data).ravel().nonzero()[0]
        data[np.isnan(data)] = np.interp(getZero, location, getNonZero)
        return data

    def rolling_window(self, a, window):
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    def RSI(self, priceArray, period=1000):
        df = pd.DataFrame(priceArray, columns=['data'])
        df['diff1'] = df['data'].diff()
        df['diff2'] = df['data'].diff(-1)
        df = df.fillna(0)
        df['bb'] = df['diff1'].apply(lambda x: max(float(x), 0))
        df['ff'] = df['diff2'].apply(lambda x: max(float(x), 0))
        df['rs'] = df['bb'].rolling(period).mean()*1. / df['ff'].rolling(period).mean()
        df['rs'] = df['rs'].fillna(method='pad').fillna(method='bfill').fillna(0).apply(
            lambda x: 99 if x == np.inf else x)
        df['rsi'] = 100. * df['rs'] / (1 + df['rs'])
        return df['rsi'].fillna(50)

    def MOM(self, series):
        '''动量指标'''
        mean = series.mean()
        mom = (series - mean)*1. / mean
        return 100. * mom / (1 + mom)

    def Kurt(self, series):
        if len(series)>3:
            kk = (series - series.mean()).kurt()
            if kk >= 2.5:
                return 1
            else:
                return 0
        else:
            return series

    def KAMA(self, datas, period=20, pow1=2, pow2=30):
        "考夫曼自适应均线"
        if len(datas)>period:
            data = np.asarray(datas)
            change = np.abs(data - np.roll(data, period))[period:]
            dif = np.abs(data - np.roll(data, 1))[1:]
            volatility = np.sum(self.rolling_window(dif, period), axis=1)
            er = change*1. / volatility  # 位移和累计路程之比
            if True in np.isnan(er):  # 插值处理nan
                er = self.nan_interp(er)
            else:
                pass
            fast = 2. / (pow1 + 1)
            slow = 2. / (pow2 + 1)
            sc = np.power((er * (fast - slow) + slow), 2)
            answer = np.zeros(data.size)
            N = len(answer)

            for i in range(N):
                if i <= period:
                    answer[i] = data[period]
                else:
                    answer[i] = answer[i - 1] + sc[i - period - 1] * (data[i] - answer[i - 1])
            return answer
        else:
            return np.ones(len(datas))

class Strategy(object):
    def __init__(self, exchangesDict, code1, code2):
        self.bg = BarGenerator(self.onBar, self.onNmbar, self.onNsecond, nMin=59, nSecond=20)
        self.eeDict = exchangesDict
        self.code1 = code1
        self.code2 = code2
        self.ind = Indicators()
        self.tools = Tools()

        self.priceArray = []

        # params
        self.final_signal = 0
        self.dt = datetime.now()
        self.open_dt = datetime.now()
        self.length = 0

    def CancelPendingOrders(self, exchange):
        orders = exchange.GetOrders()
        if isinstance(orders, list):
            if len(orders) != 0:
                for i in range(len(orders)):
                    exchange.CancelOrder(orders[i].Id)
            else:
                pass
        else:
            pass

    def GetPos(self, ee):
        "20次/2s"
        position = Position()
        pos = ee.GetPosition()
        try:
            if len(pos) != 0:
                df = pd.DataFrame([pos[0].Info])
                position.long_qty = df["long_qty"].astype(int).values[0]  # 多仓数量
                position.long_avail_qty = df["long_avail_qty"].astype(int).values[0]  # 多仓可平仓数量
                position.long_pnl_ratio = df["long_pnl_ratio"].astype(float).values[0]  # 多仓盈亏比
                position.long_avg_cost = df["long_avg_cost"].astype(float).values[0]  # 开仓平均价
                position.short_qty = df["short_qty"].astype(int).values[0]  # 空仓数量
                position.short_avail_qty = df["short_avail_qty"].astype(int).values[0]
                position.short_pnl_ratio = df["short_pnl_ratio"].astype(float).values[0]
                position.short_avg_cost = df["short_avg_cost"].astype(float).values[0]  # 开仓平均价
                position.instrument_id = df["instrument_id"].values[0]
                position.last = df["last"].astype(float).values[0]  # 最新成交价
                position.allpos = df["long_avail_qty"].astype(int).values[0] + df["short_avail_qty"].astype(int).values[0]
                position.creat_time = utctime(df["created_at"].values[0])
                position.update_time = utctime(df["updated_at"].values[0])
                return position
            else:
                return position
        except Exception as e:
            return position

    def GetOrders(self, ee):
        order_dict = {
            "0": "Normal",
            "1": "Maker",
            "2": "FOK",  # 全部成交或立即取消（FOK）
            "3": "IOC"  # 立即成交并取消剩余
        }
        ods = Orders()
        orders = ee.GetOrders()
        try:
            if len(orders) != 0:
                for od in orders:
                    odd = od.Info
                    ods.filled_qty = int(odd["filled_qty"])
                    ods.instrument_id = odd["instrument_id"]
                    ods.order_id = odd["order_id"]
                    ods.order_type = order_dict[odd["order_type"]]
                    ods.price = float(odd["price"])
                    ods.price_avg = float(odd["price_avg"])
                    ods.size = odd["size"]  # 委托数量
                    ods.state = odd["state"]  # 订单状态 - 2：失败 -1：撤单成功 0：等待成交 1：部分成交  2：完全成交 3：下单中 4：撤单中
                    ods.datetime = utctime(odd["timestamp"])
                    ods.type = odd["type"]  # 订单类型1:开多2:开空3:平多4:平空
                    ods.length = len(orders)
                    return ods
            else:
                ods.datetime = self.dt
                return ods
        except Exception as e:
            return ods

    def GetTicker(self, ticker):
        tick = Ticker()
        if ticker != None:
            tick.datetime = utctime(ticker.Info["timestamp"])
            tick.Sell = float(ticker.Info["best_ask"])
            tick.Buy = float(ticker.Info["best_bid"])
            tick.Last = float(ticker.Info["last"])
            tick.instrument_id = ticker.Info["instrument_id"]
            self.dt = tick.datetime
            return tick
        else:
            return tick

    def GetAccount(self, ee):
        get_account = ee.GetAccount()
        account = Account()
        try:
            if len(get_account)!=0:
                df = pd.DataFrame([get_account.Info])
                account.equity = df["equity"].astype(float).values[0]
                return account
        except Exception as e:
            return account

    def Trade(self, Margin, ContractType, Direction, Amout, Price, code):
        ee = self.eeDict[code]
        ee.SetContractType(ContractType)
        #ee.SetMarginLevel(Margin)
        ee.SetDirection(Direction)
        if Direction == "closebuy":
            return ee.Sell(Price, Amout)
        elif Direction == "closesell":
            return ee.Buy(Price, Amout)
        elif Direction == "sell":
            return ee.Sell(Price, Amout)
        elif Direction == "buy":
            return ee.Buy(Price, Amout)

    def TradePart(self, code, ticker):
        ee = self.eeDict[code]
        pos = self.GetPos(ee)
        orders = self.GetOrders(ee)
        ticker = self.GetTicker(ticker)
        mid_price = 0.5 * (ticker.Buy + ticker.Sell)
        update_time = ticker.datetime  # 更新时间
        order_time = orders.datetime  # order创建时间
        contractType = "quarter"
        dt = datetime.now()
        # 超时撤单
        if (update_time - order_time) >= timedelta(seconds=10):
            order_id = "{}|".format(str(ticker.instrument_id)) + orders.order_id
            ee.CancelOrder(order_id)
        # 开单
        if self.final_signal==1:
            self.Trade(Margin=10, ContractType=contractType, Direction="buy", Price=ticker.Buy, Amout=_Amount, code=code)
            self.open_dt = dt
        elif self.final_signal==-1:
            self.Trade(Margin=10, ContractType=contractType, Direction="sell", Price=ticker.Sell, Amout=_Amount, code=code)
            self.open_dt = dt
        if pos.allpos != 0:
            # 平非信号仓位
            if self.final_signal == 1 and pos.short_avail_qty!=0: # 做多信号下存在空单
                self.Trade(Margin=10, ContractType=contractType, Direction="closesell", Price=mid_price, Amout=pos.short_avail_qty, code=code)
            if self.final_signal == -1 and pos.long_avail_qty!=0: # 做空信号下存在多单
                self.Trade(Margin=10, ContractType=contractType, Direction="closebuy", Price=mid_price, Amout=pos.long_avail_qty, code=code)

            # 补仓
            if pos.long_avail_qty !=0 and self.final_signal==1 and pos.long_avail_qty<_Amount:
                self.Trade(Margin=10, ContractType=contractType, Direction="buy", Price=ticker.Buy, Amout=(_Amount-pos.long_avail_qty), code=code)
                self.open_dt = dt
            if pos.short_avail_qty!=0 and self.final_signal==-1 and pos.short_avail_qty<_Amount:
                self.Trade(Margin=10, ContractType=contractType, Direction="sell", Price=ticker.Sell, Amout=(_Amount-pos.short_avail_qty), code=code)
                self.open_dt = dt
            # 止损
            if pos.long_pnl_ratio <= -0.6 and pos.long_avail_qty != 0:
                self.Trade(Margin=10, ContractType=contractType, Direction="closebuy", Price=mid_price, Amout=pos.long_avail_qty, code=code)
            if pos.short_pnl_ratio <= -0.6 and pos.short_avail_qty != 0:
                self.Trade(Margin=10, ContractType=contractType, Direction="closesell", Price=mid_price, Amout=pos.short_avail_qty, code=code)

            # 时间平仓
            if dt - self.open_dt >= timedelta(minutes=_Close_dt):
                if pos.long_avail_qty != 0:  # 多仓
                    self.Trade(Margin=10, ContractType=contractType, Direction="closebuy", Price=ticker.Sell, Amout=pos.long_avail_qty, code=code)
                if pos.short_avail_qty != 0:  # 空仓
                    self.Trade(Margin=10, ContractType=contractType, Direction="closesell", Price=ticker.Buy, Amout=pos.short_avail_qty, code=code)

        LogStatus(
            "  内部参数  | #483D8B",
            '\nStrategy | 仓位:', '{} #FF4500'.format(str(pos.allpos)),
            '\nStrategy | 空仓剩余仓位:', '{} #FF1493'.format(str(pos.short_avail_qty)),
            '\nStrategy | 多仓剩余仓位:', '{} #800080'.format(str(pos.long_avail_qty)),
            '\nStrategy | 信号:', '{} #006400'.format(str(self.final_signal)),
            '\nStrategy | 数据长度:', '{} #DC143C'.format(str(self.length)),
            '\nStrategy | 开仓时间:', '{}'.format(str(self.open_dt)),
            '\nStrategy | 当前价格:', '{} #DC143C'.format(str(mid_price))
        )

    def onTick(self, tick_dict):
        self.bg.upDateTick(tick_dict[self.code2])#ETHUSDT
        self.TradePart(self.code1, tick_dict[self.code1])#eth期货

    def onBar(self, bar):
        "计算指标"
        ee = self.eeDict[self.code1]#ETH期货
        account = self.GetAccount(ee)
        LogProfit(account.equity)
        self.length = len(self.priceArray)
        self.priceArray.append(bar.VwPrice)
        array = self.ind.KAMA(self.priceArray)  # ndarray
        ser_data = pd.Series(array)
        mom = self.ind.MOM(ser_data).fillna(method='pad').fillna(method='bfill')
        kurt = self.ind.Kurt(mom)
        mom_filter = mom.apply(lambda x: self.tools.sigmoid(x)).iloc[-1]

        if len(self.priceArray) > _Rolling_period:
            if kurt == 1 and mom_filter>0.7:
                self.final_signal = -1
            elif kurt == 1 and mom_filter<0.3:
                self.final_signal = 1
            else:
                 self.final_signal = 0

            self.priceArray.pop(0)


    def onNmbar(self, bars):
        pass

    def onNsecond(self, tuple_tickers):
        pass #

    def MainLoop(self):
        # 循环
        ee1 = self.eeDict[self.code1] # eth期货
        ee2 = self.eeDict[self.code2]
        self.CancelPendingOrders(ee1)
        while True:
            ticker1 = ee1.GetTicker()
            ticker2 = ee2.GetTicker()
            tick_dict = {
                self.code1:ticker1,
                self.code2:ticker2
            }
            if ticker1 != None and ticker2 != None:
                self.onTick(tick_dict)
            Sleep(456)

def main():
    coin1 = exchanges[0]
    coin2 = exchanges[1]
    coin1.SetContractType("quarter")
    coins_dict = {}
    code1 = "ETH"
    code2 = "ETHUSD"
    coins_dict[code1] = coin1
    coins_dict[code2] = coin2
    ss = Strategy(
        exchangesDict=coins_dict,
        code1=code1,
        code2=code2
    )
    ss.MainLoop()