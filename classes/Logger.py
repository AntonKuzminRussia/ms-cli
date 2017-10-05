# -*- coding: utf-8 -*-
"""
Logger class
"""

import sys
import os
import time


class Logger(object):
    """
    Logger class
    """
    logs_path = os.path.dirname(__file__) + "/../logs/"
    LOG_TYPE_INFO = 'info'
    LOG_TYPE_ERR = 'err'
    LOG_TYPE_EX = 'ex'
    LOG_TYPE_OUT = 'out'
    fhs = {
        'info': None,
        'err': None,
        'ex': None,
        'out': None,
    }

    @staticmethod
    def get_fh(log_type):
        """
        Get file handler by type (use constants upper by code)
        :param log_type: str
        :return: file
        """
        curdate = time.strftime("%Y-%m-%d", time.localtime())
        if not os.path.exists(Logger.logs_path + curdate):
            os.mkdir(Logger.logs_path + curdate)

        current_log_path = Logger.logs_path + curdate + "/" + log_type + ".log"
        if Logger.fhs[log_type] is None or not os.path.exists(current_log_path):
            if Logger.fhs[log_type] is not None:
                Logger.fhs[log_type].close()
            Logger.fhs[log_type] = open(current_log_path, 'a')

        return Logger.fhs[log_type] #type: file

    @staticmethod
    def pull_to_log(log_type, _s):
        """
        Write str to log file
        :param log_type:
        :param _s:
        :return:
        """
        Logger.get_fh(log_type).write("[{0}] {1}\n".format(time.strftime("%H:%M:%S", time.localtime()), _s))
        Logger.get_fh(log_type).flush()

    @staticmethod
    def to_out(_s):
        """
        Put str to stdout
        :param _s:
        :return:
        """
        Logger.pull_to_log(Logger.LOG_TYPE_OUT, _s)
        print(_s)
        sys.stdout.flush()

    @staticmethod
    def log_ex(ex, context):
        """
        Log exception and put it to stdout
        :param ex:
        :param context:
        :return:
        """
        _s = "[EXCEPTION]: {0} - {1} from '{2}'".format(type(ex), str(ex), context)
        Logger.pull_to_log(Logger.LOG_TYPE_EX, _s)
        Logger.to_out(_s)

    @staticmethod
    def log_err(_s):
        """
        :param _s:
        :return:
        """
        Logger.pull_to_log(Logger.LOG_TYPE_ERR, _s)
        Logger.to_out("[ERROR]: " + str(_s))

    @staticmethod
    def log_info(_s):
        """
        :param _s:
        :return:
        """
        Logger.pull_to_log(Logger.LOG_TYPE_INFO, _s)
        Logger.to_out("[INFO]: " + str(_s))
