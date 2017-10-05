# -*- coding: utf-8 -*-
"""
Main work thread. Starts other threads.
"""
import threading
import time

from classes.MailWorkerThread import MailWorkerThread
from classes.FiltersRefreshThread import FiltersRefreshThread
from classes.Logger import Logger

class MainThread(threading.Thread):

    db = None
    threads_per_host_limit = None
    threads_pool = None
    daemon = True
    filters_refresh_worker = None

    def __init__(self, db, threads_per_server_limit):
        """
        :param db classes.Database:
        :param threads_per_server_limit int:
        """
        threading.Thread.__init__(self)

        self.db = db
        self.threads_per_host_limit = threads_per_server_limit
        self.threads_pool = {}

    def run(self):
        self.filters_refresh_worker = FiltersRefreshThread(self.db.clone())
        self.filters_refresh_worker.start()

        while True:
            accounts = self.db.fetch_all(
                "SELECT * FROM accounts "
                "WHERE last_checked + check_interval < UNIX_TIMESTAMP() "
                "AND active = 1 AND in_work = 0")
            for account in accounts:
                if account['host'] not in self.threads_pool.keys():
                    self.threads_pool[account['host']] = []

                if len(self.threads_pool[account['host']]) < self.threads_per_host_limit:
                    worker = MailWorkerThread(self.db.clone(), account)
                    worker.start()
                    self.threads_pool[account['host']].append(worker)

            for host in self.threads_pool:
                for worker in self.threads_pool[host]:
                    if worker.done:
                        del self.threads_pool[host][self.threads_pool[host].index(worker)]

            if accounts and len(accounts):
                time.sleep(5)
            else:
                Logger.log_info("Not accounts for work. sleep 60s")
                time.sleep(60)
