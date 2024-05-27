#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: config.py
@time: 2020/1/7

"""

from environs import Env

env = Env()
env.read_env()

DEBUG = False
TIMINGDEBUG = True
REDIS = env.str('REDIS_URL')
MYSQL = env.str('MYSQL_URL')
BASE_DIR = 'D:\\CQ\\'