#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import pprint
import configparser
import shutil

from classes.Database import Database
from classes.MainThread import MainThread
from classes.Config import Config

CURPATH = os.path.dirname(__file__) + "/"

config = configparser.ConfigParser()
config.read(CURPATH + 'config.ini')

Config.set_values(config['main'])

db = Database(
    config['main']['db_host'],
    config['main']['db_user'],
    config['main']['db_pass'],
    config['main']['db_name'],
)

if str(Config.get_value('always_start_clean')) == '1':
    db.q("TRUNCATE TABLE `folders`;")
    db.q("TRUNCATE TABLE `letters`;")
    db.q("TRUNCATE TABLE `attachments`;")
    db.q("TRUNCATE TABLE `filters_finds`;")
    db.q("UPDATE `accounts` SET `in_work` = '0', `active` = 1")

    if os.path.exists(Config.get_value('bodies_path')):
        shutil.rmtree(Config.get_value('bodies_path'))

    if os.path.exists(Config.get_value('attachments_dir')):
        shutil.rmtree(Config.get_value('attachments_dir'))

if not os.path.exists(Config.get_value('bodies_path')):
    os.mkdir(Config.get_value('bodies_path'))

if not os.path.exists(Config.get_value('attachments_dir')):
    os.mkdir(Config.get_value('attachments_dir'))

main_thread = MainThread(db.clone(), int(config['main']['threads_per_host_limit']))
main_thread.start()

while True:
    time.sleep(5)
