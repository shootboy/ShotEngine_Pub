#!python2
# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: strategy_futures_hand_arbi.py
@Time: 2020/9/13 23:17
@Motto：I have a bad feeling about this.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 预存数据 rb_list, j_list, jm_list, i_list, hc_list
rb_list = [3329,
3242,
3233,
3169,
3229,
3189,
3206,
3244,
3306,
3373,
3387,
3384,
3373,
3385,
3381,
3362,
3337,
3375,
3330,
3343,
3316,
3292,
3302,
3367,
3411,
3477,
3464,
3461,
3457,
3469,
3441,
3472,
3581,
3542,
3534,
3556,
3513,
3505,
3476,
3490,
3527,
3562,
3575,
3645,
3639,
3605,
3616,
3596,
3603,
3588,
3586,
3628,
3585,
3581,
3609,
3618,
3641,
3610,
3612,
3620,
3574,
3567,
3565,
3600,
3619,
3642,
3690,
3732,
3684,
3734,
3745,
3721,
3728,
3706,
3735,
3715,
3790,
3788,
3789,
3777,
3739,
3736,
3758,
3744,
3776,
3849,
3831,
3860,
3850,
3820,
3835,
3799,
3782,
3773,
3828,
3837,
3825,
3779,
3774,
3792,
3761,
3692,
3744,
3709,
3734,
3770,
3771,
3786,
3750,
3757,
3750,
3723,
3679,
3636,
3672,
3664,
3592,
3575,
3577,
3587]
j_list = [1800,
1767,
1655.5,
1594,
1665,
1617.5,
1645,
1680,
1699,
1730,
1730,
1731,
1700,
1717,
1717.5,
1708.5,
1670,
1695,
1683,
1715,
1701.5,
1638.5,
1657,
1693,
1725.5,
1759,
1741.5,
1730.5,
1726,
1733,
1772.5,
1787,
1832.5,
1825.5,
1819,
1837.5,
1854.5,
1866,
1858,
1859.5,
1868,
1896.5,
1899,
1928,
1953.5,
1967,
1955.5,
1950,
1948,
1964,
1934,
1970,
1947.5,
1928.5,
1941,
1958,
1968,
1951,
1948.5,
1955.5,
1890,
1883,
1868.5,
1876,
1851,
1875.5,
1893,
1911,
1877.5,
1892.5,
1918,
1900.5,
1882.5,
1904,
1950.5,
1952,
1971,
1978.5,
2012,
1986.5,
1970,
1972.5,
1975.5,
1960.5,
1987,
2028,
2026.5,
2042,
2067,
2058,
2029.5,
2000,
1989,
1990.5,
2013.5,
2009.5,
2000.5,
2001.5,
1952.5,
1939.5,
1934.5,
1918.5,
1923,
1886,
1942.5,
1970,
1985,
2012,
2020.5,
2036.5,
2032.5,
2015,
1997,
1964,
1978,
1991.5,
1977.5,
1936.5,
1948,
1983.5
]
jm_list = [1254,
1242,
1260.5,
1243.5,
1233,
1075,
1088,
1096.5,
1103.5,
1131,
1132,
1130.5,
1124,
1137,
1136.5,
1132,
1108,
1117,
1100.5,
1093,
1075,
1035.5,
1039.5,
1069,
1095,
1100.5,
1091.5,
1084,
1112,
1119.5,
1118,
1128.5,
1150.5,
1161,
1161,
1159.5,
1161,
1145,
1148,
1156.5,
1161.5,
1174.5,
1168,
1175.5,
1171.5,
1162.5,
1166,
1186.5,
1191,
1185.5,
1181.5,
1186,
1175.5,
1181,
1181.5,
1187.5,
1184.5,
1176,
1189,
1190,
1180,
1176.5,
1172.5,
1193,
1190.5,
1190.5,
1194,
1201.5,
1204,
1203,
1203.5,
1206.5,
1197.5,
1203,
1206,
1215.5,
1225.5,
1228,
1236,
1233,
1222,
1221,
1213.5,
1208.5,
1206.5,
1226,
1200,
1218.5,
1223,
1212,
1207,
1191.5,
1195.5,
1195.5,
1199,
1195.5,
1189.5,
1189.5,
1212,
1207.5,
1221.5,
1219.5,
1219,
1208,
1230,
1246,
1258,
1284,
1276,
1292,
1278,
1262.5,
1252.5,
1247,
1252.5,
1263,
1255.5,
1947,
1260,
1277
]
i_list = [659,
645.5,
574.5,
557.5,
577.5,
568,
569.5,
584,
597.5,
599.5,
596,
606.5,
606.5,
606,
612,
620,
602,
613,
604.5,
607,
602,
594.5,
595.5,
610,
614,
633.5,
637,
630,
639,
646.5,
647.5,
668.5,
699,
709,
704.5,
731,
722,
712.5,
687.5,
703,
720,
745,
740,
751,
752,
745.5,
760,
773,
764,
762,
756,
787.5,
771,
766.5,
768.5,
772,
767.5,
754.5,
759,
771,
743.5,
747.5,
739,
740.5,
747,
770.5,
781,
796.5,
786.5,
820,
837.5,
829,
832.5,
820.5,
824.5,
831.5,
850,
851,
838,
829,
816.5,
827,
834.5,
832.5,
849.5,
891.5,
886,
907.5,
903.5,
815.5,
841,
818.5,
820,
822,
838.5,
847.5,
856.5,
861,
847,
843.5,
824.5,
812,
826,
819.5,
836,
846,
850,
862.5,
841.5,
861,
864,
849,
839,
825,
847,
833.5,
827.5,
796.5,
790,
806.5]
hc_list = [3171,
3079,
3071,
2999,
3078,
3035,
3063,
3103,
3149,
3209,
3220,
3200,
3196,
3234,
3235,
3218,
3185,
3211,
3173,
3187,
3171,
3149,
3159,
3211,
3258,
3348,
3329,
3329,
3328,
3349,
3349,
3387,
3486,
3446,
3443,
3455,
3417,
3411,
3392,
3425,
3487,
3529,
3542,
3559,
3522,
3501,
3527,
3517,
3520,
3540,
3522,
3583,
3548,
3546,
3599,
3647,
3651,
3622,
3609,
3604,
3594,
3584,
3561,
3588,
3599,
3636,
3679,
3727,
3692,
3740,
3752,
3751,
3758,
3739,
3748,
3758,
3811,
3805,
3815,
3791,
3772,
3771,
3787,
3802,
3862,
3915,
3918,
3929,
3912,
3890,
3921,
3888,
3903,
3913,
3958,
3970,
3975,
3961,
3962,
3962,
3964,
3926,
3949,
3945,
3960,
4031,
3952,
3941,
3877,
3916,
3876,
3829,
3777,
3738,
3799,
3786,
3730,
3689,
3687,
3709]

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

class Strategy(object):

    def __init__(self, rb_list, j_list, jm_list, i_list, hc_list):
        self.inds = Indicators()
        rb_array = np.array(rb_list)
        j_array = np.array(j_list)
        jm_array = np.array(jm_list)
        i_array = np.array(i_list)
        hc_array = np.array(hc_list)
        # 按照南华黑色系数确定
        self.black_index = rb_array*0.3572+i_array*0.2561+j_array*0.1909+jm_array*0.0991+hc_array*0.0967
        self.data_dict = {}
        self.data_dict['rb'] = rb_array
        self.data_dict['j'] = j_array
        self.data_dict['jm'] = jm_array
        self.data_dict['i'] = i_array
        self.data_dict['hc'] = hc_array

    def cal_indicator(self, code):
        residual_list = []
        cumsum_residual = []
        if len(self.data_dict[code]) >= _Learning_length:
            # ETH = beta*BTC + alpha
            x_series = pd.Series(self.black_index)  # 黑色指数
            y_series = pd.Series(self.data_dict[code])  # 操作的品种
            # --------- 数据滚动
            x_array = self.inds.rolling_window(fillnan(np.log(x_series.shift(-1) / x_series).values), _Rolling_period)
            y_array = self.inds.rolling_window(fillnan(np.log(y_series.shift(-1) / y_series).values), _Rolling_period)
            for i in range(len(x_array)):
                xlist = x_array[i]
                ylist = y_array[i]
                coef = np.polyfit(xlist, ylist, 1)  # (指数, 交易品种, 1)
                p1 = np.poly1d(coef)
                pre = p1(xlist[-1])
                residual_RR = ylist[-1] - pre  # 残差收益率
                residual_list.append(residual_RR)
                cumsum = np.cumsum(residual_list)[-1]
                cumsum_residual.append(cumsum)
            cumsum_reshape = self.inds.rolling_window(np.asarray(cumsum_residual), _Rolling_period)
            params_array = np.apply_along_axis(ar_least_square, 1, cumsum_reshape)
            params_df = pd.DataFrame(params_array, columns=['miu', 'var', 'size', 'theta'])
            params_df['cumsum'] = cumsum_reshape[:, -1]
            cumsum = params_df['cumsum'].values[-1]
            upper = params_df['miu'].values[-1] + 2 * np.power(params_df['var'].values[-1], 0.5) / np.power(
                2 * params_df['theta'].values[-1] - np.power(params_df['theta'].values[-1], 2), 0.5)
            lower = params_df['miu'].values[-1] - 2 * np.power(params_df['var'].values[-1], 0.5) / np.power(
                2 * params_df['theta'].values[-1] - np.power(params_df['theta'].values[-1], 2), 0.5)
            close_range_up = params_df['miu'].values[-1] + 0.67 * np.power(params_df['var'].values[-1], 0.5)
            close_range_down = params_df['miu'].values[-1] - 0.67 * np.power(params_df['var'].values[-1], 0.5)
            theta = params_df['theta'].values[-1]
            Log("指标日期：",datetime.now().strftime("%Y-%m-%d"))
            Log("交易品种：", code)
            # ----------开平仓条件
            if theta>0 and theta<1: # 具有向下的斜率
                if cumsum > upper:
                    Log("交易信号：开多")
                if cumsum < lower:
                    Log("交易信号：开空")
                if cumsum < close_range_up and cumsum > close_range_down:
                    Log("交易信号：全平")
            else:
                Log("交易信号：全平")

def main():
    strategy_run = Strategy(
        rb_list=rb_list,
        j_list=j_list,
        jm_list=jm_list,
        i_list=i_list,
        hc_list=hc_list
    )
    code_list = ["rb", "j", "jm", "i", "hc"]
    for code in code_list:
        strategy_run.cal_indicator(code)