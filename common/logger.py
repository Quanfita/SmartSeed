# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""

from colorama import Fore, Style, init
from termcolor import *
from .singleton import SingletonIns

import logging
import sys


@SingletonIns
class Logger(object):

    def __init__(self):
        init()

        # 关于日志的书写只要有四个步骤：
        # （1）Loggers: 创建
        # （2）Handlers:把日志传送给合适的目标
        # （3）Filters: 过滤出想要的内容
        # （4）Formatters: 格式化

        # 日志等级（从小到大）：
        # debug()-->info()-->warning()-->error()-->critical()
        # Step 1: Loggers, 并设置全局level
        self.logger = logging.getLogger('logging_blog')
        self.logger.setLevel(logging.DEBUG)

        self.printer = logging.getLogger('log')
        self.printer.setLevel(logging.DEBUG)

        # Step 2: Handler
        # print to screen
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # write to file
        fh = logging.FileHandler('../log_file.log')
        fh.setLevel(logging.DEBUG)

        # Step 3: Formatter
        my_formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        formatter = logging.Formatter('[%(asctime)s]%(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(my_formatter)

        self.printer.addHandler(ch)
        self.logger.addHandler(fh)

    def debug(self,log):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        
        pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
        self.printer.debug("["+colored('DEBUG','magenta')+"]"+pos+str(log))
        self.logger.debug(pos+str(log))
        return

    def info(self,log):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        
        pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
        self.printer.info("["+colored('INFO','cyan')+"]"+pos+str(log))
        self.logger.info(pos+str(log))
        return

    def warning(self,log):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        
        pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
        self.printer.warning("["+colored('WARNING','yellow')+"]"+pos+str(log))
        self.logger.warning(str(log))
        return

    def error(self,log):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        
        pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
        self.printer.error("["+colored('ERROR','red')+"]"+pos+str(log))
        self.logger.error(pos+str(log))
        return

    def critical(self,log):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        
        pos = '['+str(f.f_code.co_filename).split('\\')[-1]+']['+str(f.f_code.co_name)+']['+str(f.f_lineno)+']'
        self.printer.critical("["+colored('CRITICAL','green')+"]"+pos+str(log))
        self.logger.critical(pos+str(log))
        return

if __name__ == '__main__':
    # 开始使用：不同等级会写入到屏幕和文件中
    logger = Logger()
    logger.debug('This is a debug log.')
    logger.info('This is a info log.')
    logger.warning('This is a warning log.')
    logger.error('This is a error log.')
    logger.critical('This is a critial log.')