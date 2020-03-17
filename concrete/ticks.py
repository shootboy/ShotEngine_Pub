# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: ticks.py
@Time: 2020/3/17 20:35
@Motto：I have a bad feeling about this.
"""
class TickData(object):

    def __init__(self, symbol, exchange):
        self.last_price = "KQ.m@{}.{}.last_price".format(exchange, symbol)
        self.high = "KQ.m@{}.{}.highest".format(exchange, symbol)
        self.low = "KQ.m@{}.{}.lowest".format(exchange, symbol)
        self.bidprice = "KQ.m@{}.{}.bid_price1".format(exchange, symbol)
        self.bidvol = "KQ.m@{}.{}.bid_volume1".format(exchange, symbol)
        self.askprice = "KQ.m@{}.{}.ask_price1".format(exchange, symbol)
        self.askvol = "KQ.m@{}.{}.ask_volume1".format(exchange, symbol)
        self.vol = "KQ.m@{}.{}.volume".format(exchange, symbol)
        self.amount = "KQ.m@{}.{}.amount".format(exchange, symbol)
        self.open_interest = "KQ.m@{}.{}.open_interest".format(exchange, symbol)