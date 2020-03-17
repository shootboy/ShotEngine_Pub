# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy.py
@Time: 2020/3/17 21:58
@Motto：I have a bad feeling about this.
"""
import numpy as np
import pandas as pd
from config import settings

class StrategyBase(object):
    def __init__(self):
        self.initial_cap = 1e8
        self.ctx = None         # 在engine 初始化后被赋值


    def on_init(self):
        """初始化全部数据"""
        return


    def on_bar(self, pos):
        """ 逐个时间点运行 """
        return

############ 执行 ###########
    def send_pos(self,quantity, sigma):
        self.ctx.send_pos(quantity, sigma)

    def cal(self):
        "画图"
        return