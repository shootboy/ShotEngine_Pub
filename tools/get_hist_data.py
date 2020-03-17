# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: get_hist_data.py
@Time: 2020/3/17 13:07
@Motto：I have a bad feeling about this.
"""
from datetime import date, datetime, timedelta
from tqsdk.tools import DataDownloader
from tqsdk import TqApi, TqSim
from contextlib import closing
from subscription_manager import SubscriptionsManager
import pandas as pd
import numpy as np

class Get_hist_data:

    def __init__(self, subs_path, cal_path, start_dt, end_dt):
        self.subs_path = subs_path
        self.cal_path = cal_path
        self.start_dt = start_dt
        self.end_dt = end_dt

    def get_trade_cal(self):
        cal_df = pd.read_csv(self.cal_path, index_col=0)
        cal_df['calendarDate'] = pd.to_datetime(cal_df['calendarDate'], format="%Y/%m/%d")
        trade_cal_list = cal_df[cal_df['isOpen']==1]['calendarDate']
        return trade_cal_list

    def get_hist(self):
        api = TqApi(TqSim())
        download_tasks = {}
        trade_cal = self.get_trade_cal().to_frame("dt")
        trade_cal['end_dt'] = trade_cal['dt'] + timedelta(days=1)
        for i in SubscriptionsManager(self.subs_path).get_subscriptions():
            code = "KQ.{}@{}.{}".format(i.instmt_type, i.exchange_name, i.instmt_code)
            trade_cal['code1'] = code
            trade_cal['filename'] = "{}".format(i.instmt_code)+trade_cal['dt'].apply(lambda x:x.strftime("%Y_%Y%m%d"))
            trade_cal['filepath'] = "./"+trade_cal['filename']+".csv"
        trade_cal_dict = trade_cal.to_dict(orient='dict')
        for k, v in trade_cal_dict['dt'].items():
            start_dt = datetime.fromtimestamp((v - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))
            start_dt = datetime(year=start_dt.year, month=start_dt.month, day=start_dt.day)
            end_dt = start_dt + timedelta(days=1)
            csv_filename = trade_cal_dict['filename'][k]
            filepath = trade_cal_dict['filepath'][k]
            code = trade_cal['code1'][k]
            print(csv_filename, filepath)
            download_tasks[csv_filename] = DataDownloader(api, symbol_list=code, dur_sec=0,
                                                      start_dt=start_dt, end_dt=end_dt,
                                                      csv_file_name=filepath)
        with closing(api):
            while not all([v.is_finished() for v in download_tasks.values()]):
                api.wait_update()
                print("progress:", {k: ("%.2f%%" % v.get_progress()) for k, v in download_tasks.items()})

if __name__ == "__main__":
    subs_path = './subscriptions.ini'
    cal_path = './trade_calendar.csv'

    start_dt = datetime(2019, 1, 4)
    end_dt = datetime(2019, 1, 4)
    get_data = Get_hist_data(subs_path, cal_path, start_dt, end_dt)
    get_data.get_hist()