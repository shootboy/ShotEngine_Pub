# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: instrument.py
@Time: 2020/3/17 13:02
@Motto：I have a bad feeling about this.
"""
class Instrument(object):
    def __init__(self,
                 exchange_name,
                 instmt_code,
                 instmt_type,
                 **params):
        """
        Constructor
        :param exchange: Exchange name
        :param instmt_code: Instrument code
        :param param: Options parameters, e.g. restful_order_book_link
        :return:
        """
        self.exchange_name = exchange_name
        self.instmt_code = instmt_code
        self.instmt_type = instmt_type