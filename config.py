#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: config.py
@time: 2020/1/7

"""

class BaseConfig:
  #Mysql 配置
  SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root:jdgjxxchy_0820@localhost:3306/orange"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  DEBUG = True

  #以下配置不常用

  # SQLALCHEMY_POOL_SIZE = 5 #数据库连接池的大小。默认是数据库引擎的默认值 （通常是 5）。
  # SQLALCHEMY_POOL_TIMEOUT = 10 #指定数据库连接池的超时时间。默认是 10
  # SQLALCHEMY_MAX_OVERFLOW = 2 #控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃
  # SQLALCHEMY_POOL_RECYCLE = 2 #动回收连接的秒数。这对 MySQL 是必须的，默认 情况下 MySQL 会自动移除闲置 8 小时或者以上的连接。 需要注意地是如果使用 MySQL 的话，Flask-SQLAlchemy 会自动地设置这个值为2小时

  #Mongo配置

  # MONGODB_PORT = 27017
  # MONGODB_HOST = "127.0.0.1"
  # MONGODB_DB = "dbName"
  # MONGODB_USERNAME = "dbuser"
  # MONGODB_PASSWORD = "dbpasswd"

  #MQ配置 rabbitmq

  # MQ_USER_NAME = 'name'
  # MQ_USER_PAWD = 'pwd'
  # MQ_URL = 'host'
  # MQ_HOST = 5672


DEBUG = True
TIMINGDEBUG = True
REDIS = 'redis://localhost'
BASE_DIR = 'D:\\CQ\\'