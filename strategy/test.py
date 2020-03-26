#!python2
# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: test.py
@Time: 2020/3/25 16:35
@Motto：I have a bad feeling about this.
"""

def main():
    coin1 = exchanges[0]
    coin2 = exchanges[1]
    coin1.SetContractType("quarter")
    coins_dict = {}
    code1 = "ETH"
    code2 = "ETHUSD"
    coins_dict[code1] = coin1
    coins_dict[code2] = coin2
    while True:
        ticker1 = coin1.GetTicker()
        ticker2 = coin2.GetTicker()
        Log(ticker2.Last)
        Sleep(456)