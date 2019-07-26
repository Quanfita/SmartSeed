# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 17:42:25 2019

@author: Quanfita
"""

from PyQt5.QtWidgets import QApplication,QDialog,QProgressDialog,QWidget
from PyQt5.QtCore import pyqtSignal,Qt
import sys
import time
import logger
from Thread import ProThread
from app import MainWindow
from views import Welcome
sys.setrecursionlimit(5000)
#import warnings
#warnings.filterwarnings('ignore')

class main:
    def __init__(self,debug=False):
        self.__debug = debug
        self.thr = ProThread()
        app = QApplication(sys.argv)
        self.wel = Welcome(debug=self.__debug)
        self.thr.pro_signal[dict].connect(self.commuicateToApp)
        if self.wel.exec_() == QDialog.Accepted:
            self.mainwindow = MainWindow(debug=self.__debug)
            self.mainwindow.show()
            self.hold_time = time.time()
            logger.info('Application Start!')
            self.mainwindow.send_signal[dict].connect(self.communicateToThread)
        logger.info('Application running time:'+str(time.time()-self.hold_time))
        sys.exit(app.exec_())
    
    def communicateToThread(self,content):
        if self.debug:
            logger.debug('App send signal to thread:'+str(content))
        if len(content) < 3:
            self.thr.changeMode(content['img'], content['method'])
        else:
            self.thr.changeMode(content['img'], content['method'], content['other'])
        self.thr.start()
        self.showProcessDialog()
    
    def commuicateToApp(self,content):
        self.mainwindow.refreshShow(content['img'])
        if self.debug:
            logger.debug('Thread send signal to app:'+str(content))
        pass
    
    def showProcessDialog(self):
        self.progress = QProgressDialog()
        self.progress.setStyleSheet('QProgressDialog{color:white;background-color:#535353;}')
        self.progress.setWindowTitle("请稍等")  
        self.progress.setLabelText("正在操作...")
        self.progress.setCancelButtonText("取消")
        self.progress.setMinimumDuration(5)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setRange(0,100)
        self.progress.show()
        num = 0
        while(self.thr.isRunning()):
            time.sleep(0.001)
            if self.progress.value() == 99:
                continue
            else:
                self.progress.setValue(num)
                
                num += 1
        self.progress.setValue(100)
        self.progress.close()
        del self.progress

if __name__ == '__main__':
    main(debug=True)