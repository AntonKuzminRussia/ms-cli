# -*- coding: utf-8 -*-
"""
Config class
"""

class Config(object):
    """
    Config class
    """
    data = {}

    @staticmethod
    def get_value(key_name):
        """
        :param key_name:
        :return:
        """
        return Config.data[key_name]

    @staticmethod
    def set_value(key_name, key_value):
        """
        :param key_name:
        :param key_value:
        :return:
        """
        Config.data[key_name] = key_value

    @staticmethod
    def set_values(values_dict):
        """
        :param values_dict: list
        :return:
        """
        for key in values_dict:
            Config.data[key] = values_dict[key]
