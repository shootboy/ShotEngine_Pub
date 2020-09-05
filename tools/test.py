# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: test.py
@Time: 2020/8/13 16:52
@Motto：I have a bad feeling about this.
"""
import numpy as np
import pandas as pd

def ar_least_square(array, p=1):
    """自相关"""
    matrix = np.matrix(np.zeros((array.size-p, p)))
    matriy = np.matrix(np.array(array[p:array.size]).reshape(array.size -p, 1))
    array = array.reshape(array.size)
    a = matrix
    # 一阶
    a[:, 0] = array[:-1*p].reshape(array[:-1*p].size, 1)
    # 参数序列
    fi = np.dot(np.dot((np.dot(matrix.T, matrix)).I, matrix.T), matriy)
    matriy_pre = np.row_stack((array[:p].reshape(p,1), np.dot(matrix, fi)))
    a = matriy_pre-array.reshape(array.size, 1) # 含eta
    variance = np.var(a)/(array.size - 1)
    miu = a*1./(1-fi)
    theta = 1-fi # 回归速率 theta小于0为回归倾向
    return miu.A[-1][0], variance, array.size, theta.A[-1][0]

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
        df['rs'] = df['bb'].rolling(period).mean() * 1. / df['ff'].rolling(period).mean()
        df['rs'] = df['rs'].fillna(method='pad').fillna(method='bfill').fillna(0).apply(
            lambda x: 99 if x == np.inf else x)
        df['rsi'] = 100. * df['rs'] / (1 + df['rs'])
        return df['rsi'].fillna(50)

    def MOM(self, series):
        '''动量指标'''
        mean = series.mean()
        mom = (series - mean) * 1. / mean
        return 100. * mom / (1 + mom)

    def Kurt(self, series):
        if len(series) > 3:
            kk = (series - series.mean()).kurt()
            if kk >= 2.5:
                return 1
            else:
                return 0
        else:
            return series

    def KAMA(self, datas, period=20, pow1=2, pow2=30):
        "考夫曼自适应均线"
        if len(datas) > period:
            data = np.asarray(datas)
            change = np.abs(data - np.roll(data, period))[period:]
            dif = np.abs(data - np.roll(data, 1))[1:]
            volatility = np.sum(self.rolling_window(dif, period), axis=1)
            er = change * 1. / volatility  # 位移和累计路程之比
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

def fillnan(array):
    idx = (~np.isnan(array))
    array[np.isnan(array)] = np.mean(array[idx])
    return array

ind = Indicators()
filepath = r"C:\Users\surface\Downloads\data.csv"
df = pd.read_csv(filepath, index_col=0)
df['a_log']=np.log(df['eth'].shift(-1) / df['eth']).fillna(np.mean(df['eth']))
df['b_log']=np.log(df['btc'].shift(-1) / df['btc']).fillna(np.mean(df['btc']))
n = 51
print(df['a_log'].count())
a_reshape = ind.rolling_window(df['a_log'].values,n)
b_reshape = ind.rolling_window(df['b_log'].values,n)

residual_list = []
cumsum_residual = []
print(len(a_reshape))
for i in range(len(a_reshape)):
    print(i)
    xlist = b_reshape[i]
    ylist = a_reshape[i]
    coef = np.polyfit(xlist, ylist, 1)  # (BTC, ETH, 1)
    p1 = np.poly1d(coef)
    pre = p1(xlist[-1])
    residual_RR = ylist[-1] - pre  # 残差收益率
    residual_list.append(residual_RR)
    cumsum = np.cumsum(residual_list)[-1]
    cumsum_residual.append(cumsum)
cumsum_reshape = ind.rolling_window(np.asarray(cumsum_residual),n)
print(cumsum_reshape[:, -1])
params_array = np.apply_along_axis(ar_least_square, 1, cumsum_reshape)
params_df = pd.DataFrame(params_array, columns=['miu', 'var', 'size', 'theta'])
params_df['cumsum'] = cumsum_reshape[:, -1]
params_df['upper'] = params_df['miu'] + 2 * np.power(params_df['var'], 0.5) / np.power(2 * params_df['theta'] - np.power(params_df['theta'], 2), 0.5)
params_df['lower'] = params_df['miu'] - 2 * np.power(params_df['var'], 0.5) / np.power(2 * params_df['theta'] - np.power(params_df['theta'], 2), 0.5)
params_df['close_range_up'] = params_df['miu'] + 0.67 * np.power(params_df['var'], 0.5) / np.power(2 * params_df['theta'] - np.power(params_df['theta'], 2), 0.5)
params_df['close_range_down'] = params_df['miu'] - 0.67 * np.power(params_df['var'], 0.5) / np.power(2 * params_df['theta'] - np.power(params_df['theta'], 2), 0.5)
to_path = r"C:\Users\surface\Downloads\params3.csv"
params_df.to_csv(to_path)