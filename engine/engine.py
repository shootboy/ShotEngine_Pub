# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: engine.py
@Time: 2020/3/17 21:59
@Motto：I have a bad feeling about this.
"""
from .context import *
import time
# from performance import *
# from tqdm import *

class Engine:
    def __init__(self,strategy,univ,start_dt,end_dt):
        self.ctx = Context(univ,start_dt,end_dt)
        self.ctx.cur_strategy = strategy
        self.s = self.ctx.cur_strategy
        self.ctx.cur_strategy.ctx = self.ctx
        self.ctx.univ = univ
        self.start_time = time.clock()

    def initialize(self):
        self.s.on_init()
        pass

    def run(self):
        self.initialize()
        for self.ctx.cur_bar_i,(self.ctx.cur_tradeday,self.ctx.cur_datetime) in enumerate(self.ctx.data_index):
            curpos = self.ctx.execute()
            self.s.on_bar(curpos)
        'performance'
        #self.s.p()
        #self.s.cal()
        self.ctx.performance()
        elapsed = (time.clock() - self.start_time)
        print("Time used:", elapsed)