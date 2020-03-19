# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: data2hdf.py
@Time: 2020/3/17 20:11
@Motto：I have a bad feeling about this.
"""
import pandas as pd
import os
from datetime import datetime
from concrete.ticks import TickData

class datahandle(object):
    def __init__(self, univ, exchange, freq, filepath):
        self.univ = univ
        self.exchange = exchange
        self.freq = freq
        self.filepath = filepath

    def traverseDirByOSWalk(self, path):
        path = os.path.expanduser(path)
        for (dirname, subdir, subfile) in os.walk(path):
            for f in subfile:
                fl = os.path.join(dirname, f)
                #self.readdata(fl)
                self.read_data_chunck(fl)

    def read_data_chunck(self, csvpath):
        tick = TickData(self.univ, self.exchange)
        date = list(filter(str.isdigit, csvpath))
        date = (''.join((str(x) for x in date)))[-8:]
        key = '/%s/%s/%s' % (self.freq, self.univ, date)
        print(key)
        mylist = []
        for chunk in pd.read_csv(csvpath, chunksize=1e4):
            chunk['datetime'] = pd.to_datetime(chunk['datetime'], format="%Y%m%d %H:%M:%S.%f")
            chunk['date'] = chunk['datetime'].apply(lambda x: x.strftime("%Y%m%d"))
            chunk = chunk[chunk['date'] == date]
            chunk = chunk.set_index('datetime', drop=False)
            mylist.append(chunk)

        data = pd.concat(mylist, axis=0)
        resample_df = data[tick.last_price].resample(self.freq).last().to_frame("close")
        resample_df['bidvol'] = data[tick.bidvol].resample(self.freq).last()
        resample_df['askvol'] = data[tick.askvol].resample(self.freq).last()
        resample_df['bidprice'] = data[tick.bidprice].resample(self.freq).last()
        resample_df['askprice'] = data[tick.askprice].resample(self.freq).last()

        resample_df['vol'] = data[tick.vol].resample(self.freq).sum()
        resample_df['open'] = data[tick.last_price].resample(self.freq).first()
        resample_df['high'] = data[tick.last_price].resample(self.freq).max()
        resample_df['low'] = data[tick.last_price].resample(self.freq).min()
        resample_df['amount'] = data[tick.amount].resample(self.freq).last()
        resample_df['open_interest'] = data[tick.open_interest].resample(self.freq).last()

        print(resample_df['low'].count())

        resample_df.to_hdf(self.filepath, key=key, complevel=9, complib='zlib', format='table')
        del mylist

if __name__ == "__main__":
    univ = "rb"
    exchange = "SHFE"
    freq = "30min"
    path = r"C:\Users\surface\Downloads\database\rb"
    target_file = r"C:\Users\surface\Downloads\database\futures.h5"
    dd = datahandle(univ, exchange, freq, target_file)
    dd.traverseDirByOSWalk(path)