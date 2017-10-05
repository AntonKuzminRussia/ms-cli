# -*- coding: utf-8 -*-
"""
Thread for filters refresh. Starts when new filter been added and we need check all letters by it
"""
import time
import pprint
import threading

from classes.ImapTools import ImapTools
from classes.Logger import Logger

class FiltersRefreshThread(threading.Thread):
    """
    Thread for filters refresh. Starts when new filter been added and we need check all letters by it
    """
    db = None
    daemon = True
    filters_chunk = None
    WAIT_TIME_FOR_STEP = 60

    def __init__(self, db):
        """
        :param db classes.Database:
        """
        threading.Thread.__init__(self)
        self.db = db

    def run(self):
        while True:
            filters = self.db.fetch_all("SELECT * FROM `filters` WHERE `new` = 1")
            for _filter in filters:
                try:
                    ImapTools.refresh_filter_results(self.db, _filter)
                    self.db.update("filters", {'new': 0}, "id = {0}".format(_filter['id']))
                except BaseException as ex:
                    Logger.log_ex(str(ex), "Filters #{0} refreshing".format(_filter['id']))
            time.sleep(self.WAIT_TIME_FOR_STEP)
