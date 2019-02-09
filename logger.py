# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""

#/usr/env/bin python
#-*- coding=utf-8 -*-

import logging

# 关于日志的书写只要有四个步骤：
# （1）Loggers: 创建
# （2）Handlers:把日志传送给合适的目标
# （3）Filters: 过滤出想要的内容
# （4）Formatters: 格式化

# 日志等级（从小到大）：
# debug()-->info()-->warning()-->error()-->critical()
# Step 1: Loggers, 并设置全局level
logger = logging.getLogger('logging_blog')
logger.setLevel(logging.DEBUG)

# Step 2: Handler
# print to screen
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# write to file
fh = logging.FileHandler('log_file.log')
fh.setLevel(logging.DEBUG)

# Step 3: Formatter
my_formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
ch.setFormatter(my_formatter)
fh.setFormatter(my_formatter)

logger.addHandler(ch)
logger.addHandler(fh)

def debug(log):
    logger.debug(log)
    return

def info(log):
    logger.info(log)
    return

def warning(log):
    logger.warning(log)
    return

def error(log):
    logger.error(log)
    return

def critical(log):
    logger.critical(log)
    return

if __name__ == '__main__':
    # 开始使用：不同等级会写入到屏幕和文件中
    logger.debug('This is a debug log.')
    logger.info('This is a info log.')
    logger.warning('This is a warning log.')
    logger.error('This is a error log.')
    logger.critical('This is a critial log.')