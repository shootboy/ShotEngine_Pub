# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: stock_inds.py
@Time: 2020/4/26 10:46
@Motto：I have a bad feeling about this.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels import regression

def fillnan(array):
    idx = (~np.isnan(array))
    array[np.isnan(array)] = np.mean(array[idx])
    return array

def linreg(x,y):
    x=sm.add_constant(x)
    model = regression.linear_model.OLS(y, x).fit()
    x=x[:,1]
    #print(model.params)
    #print(model.summary())
    return model.params[0], model.params[1]

path = r"C:\Users\surface\Documents\crypto.csv"
data = pd.read_csv(path, index_col=0)
log = np.log(data.account/data.account.shift(1)).dropna()
#zz_log = np.log(data.zz500/data.zz500.shift(1)).dropna()
#hs_log = np.log(data.hs300/data.hs300.shift(1)).dropna()
if_log = np.log(data['btc_index']/data['btc_index'].shift(1)).dropna()

# if
if_alpha, if_beta = linreg(if_log.values, log.values)
# hs300
#hs_alpha, hs_beta = linreg(hs_log.values, log.values)
# zz500
#zz_alpha, zz_beta = linreg(zz_log.values, log.values)

print("="*20)
print("对标BTC指数")
print("alpha:",if_alpha, "beta:",if_beta)
#print("="*20)
#print("对标沪深300")
#print("alpha:",hs_alpha, "beta:",hs_beta)
#print("="*20)
#print("对标中证500")
#print("alpha:",zz_alpha, "beta:",zz_beta)
#print("="*20)