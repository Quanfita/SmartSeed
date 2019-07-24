# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""

#/usr/env/bin python
#-*- coding=utf-8 -*-

from colorama import Fore, Style, init
import logging
import sys
from termcolor import *
init()

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

printer = logging.getLogger('log')
printer.setLevel(logging.DEBUG)

# Step 2: Handler
# print to screen
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# write to file
fh = logging.FileHandler('log_file.log')
fh.setLevel(logging.DEBUG)

# Step 3: Formatter
my_formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
formatter = logging.Formatter('[%(asctime)s]%(message)s')
ch.setFormatter(formatter)
fh.setFormatter(my_formatter)

printer.addHandler(ch)
logger.addHandler(fh)

def debug(log):
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    
    pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
    printer.debug("["+colored('DEBUG','green')+"]"+pos+str(log))
    logger.debug(pos+str(log))
    return

def info(log):
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    
    pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
    printer.info("["+colored('INFO','magenta')+"]"+pos+str(log))
    logger.info(pos+str(log))
    return

def warning(log):
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    
    pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
    printer.warning("["+colored('WARNING','yellow')+"]"+str(log))
    logger.warning(str(log))
    return

def error(log):
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    
    pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
    printer.error("["+colored('ERROR','red')+"]"+pos+str(log))
    logger.error(pos+str(log))
    return

def critical(log):
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    
    pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
    printer.critical("["+colored('CRITICAL','orange')+"]"+pos+str(log))
    logger.critical(pos+str(log))
    return

if __name__ == '__main__':
    # 开始使用：不同等级会写入到屏幕和文件中
    logger.debug('This is a debug log.')
    logger.info('This is a info log.')
    logger.warning('This is a warning log.')
    logger.error('This is a error log.')
    logger.critical('This is a critial log.')