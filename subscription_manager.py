# -*- coding: utf-8 -*-
"""
@Author: ShotBoy
@File: subscription_manager.py
@Time: 2020/3/17 11:58
@Motto：I have a bad feeling about this.
"""
import configparser as ConfigParser
from concrete.instrument import Instrument

class SubscriptionsManager:
    def __init__(self, config_path):
        """
        Constructor
        """
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_path)

    def get_instrument_ids(self):
        """
        Return all the instrument ids
        """
        return self.config.sections()

    def get_instrument(self, instmt_id):
        exchange_name = self.config.get(instmt_id, "exchange")
        instmt_code = self.config.get(instmt_id, "code")
        instmt_type = self.config.get(instmt_id, "type")
        enabled = int(self.config.get(instmt_id, 'enabled'))
        params = dict(self.config.items(instmt_id))
        if enabled == 1:
            return Instrument(exchange_name, instmt_code, instmt_type,**params)
        else:
            return None

    def get_subscriptions(self):
        """
        Get all the subscriptions from the configuration file
        :return List of instrument objects
        """
        instmts = [self.get_instrument(inst) for inst in self.get_instrument_ids()]
        return [instmt for instmt in instmts if instmt is not None]

def test():
    path = './config/subscriptions.ini'
    print(["KQ.{}@{}.{}".format(i.instmt_type, i.exchange_name, i.instmt_code) for i in SubscriptionsManager(path).get_subscriptions()])

if __name__ == "__main__":
    test()