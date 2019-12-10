#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
默认配置文件。
'''

__author__ = 'Kylin'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'webapp',
        'password': '123456',
        'database': 'webapp'
    },
    'session': {
        'secret': 'Awesome'
    }
}