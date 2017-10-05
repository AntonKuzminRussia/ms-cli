# -*- coding: utf-8 -*-
"""
Functions, common for all
"""
import random
import hashlib
import time

def file_put_contents(path_to_file, content, add=False):
    """ Function put content to a file (analog of php file_put_contents()) """
    fh = open(path_to_file, 'a' if add else 'w')
    fh.write(content)
    fh.close()

def md5(string):
    """ String to MD5-hash """
    m = hashlib.md5()
    #m.update(string.decode(encoding='UTF-8',errors='ignore').encode('UTF-8', errors='ignore'))
    m.update(string.encode('UTF-8'))
    return m.hexdigest()

def random_md5():
    """
    Generate random md5
    :return str:
    """
    return md5(str(time.time()) + str(random.randint(0, 9999999)))

def file_get_contents(path_to_file):
    """ Function get content of file (analog of php file_get_contents()) """
    fh = open(path_to_file, 'r')
    content = fh.read()
    fh.close()
    return content
