# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 21:05:53 2019

@author: Quanfita
"""

import cv2
import numpy as np
import ops
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QDialog,
                             QSlider, QVBoxLayout, QPushButton, QColorDialog)
from PyQt5.QtGui import (QPainter, QPen, QColor, QGuiApplication, QIcon, QFont)
from PyQt5.QtCore import Qt


def comp(img,adj):
    adj = adj / 100 + 1.0
    tmp = np.copy(img)
    tmp = (tmp - 127.5)*adj + 127.5
    cv2.imwrite('./tmp/comp.jpg',tmp)
    return #tmp.astype(np.uint8)
    
def custom(img,adj):
    hlsCopy = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    hlsCopy = hlsCopy / 255.0
    hlsCopy[:, :, 2] = (1.0 + adj / 100.0) * hlsCopy[:, :, 2]
    hlsCopy[:, :, 2][hlsCopy[:, :, 2] > 1] = 1
    hlsCopy = (hlsCopy * 255).astype(np.uint8)
    tmp = cv2.cvtColor(hlsCopy,cv2.COLOR_HLS2BGR)
    return tmp

def hue(img,adj):
    hls = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    hls = hls / 180
    hls[:, :, 0] = (1.0 + adj / 360.0) * hls[:, :, 0]
    hls[:, :, 0][hls[:, :, 0] > 1] -= 1
    hls = (hls * 180).astype(np.uint8)
    tmp = cv2.cvtColor(hls,cv2.COLOR_HLS2BGR)
    return tmp

def light(img,adj):
    hls = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    hls = hls / 255
    hls[:, :, 1] = (1.0 + adj / 100.0) * hls[:, :, 1]
    hls[:, :, 2] = (1.0 + adj / 100.0) * hls[:, :, 2]
    hls[:, :, 2][hls[:, :, 2] > 1] = 1
    hls[:, :, 1][hls[:, :, 1] > 1] = 1
    hls[:, :, 1][hls[:, :, 1] < 0] = 0
    hls = (hls * 255).astype(np.uint8)
    tmp = cv2.cvtColor(hls,cv2.COLOR_HLS2BGR)
    return tmp.astype(np.uint8)

class AdjDialog(QDialog):
    def __init__(self,img,tar):
        super(AdjDialog,self).__init__()
        self.setStyleSheet('QDialog{color:white;background-color:#535353;}'
                            "QPushButton{color:white;background-color:#434343;border:2px solid white;border-radius:15px;}"
                            'QPushButton:focus{color:white;background-color:#1473e6;border:1px;}'
                            'QPushButton:hover{color:#656565;background-color:#cdcdcd;border:1px;}'
                            'QLabel{color:white;}')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640, 480)
        self.setFixedSize(640, 480)
        self.setWindowTitle('Adjustment')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        self.__img = img
        self.__tmp_img = np.copy(self.__img.Image)
        self.img_h,self.img_w = self.__img.height,self.__img.width
        self.__target = tar

        self.main_lb = QLabel('Adjustment',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(self.width()//2 - 100,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        
        self.lb = QLabel('Values: 0',self)
        self.lb.setAlignment(Qt.AlignLeft)
        self.lb.setGeometry(3*self.width()//5 + 10,120,100,30)
        
        self.imgShow = QLabel('',self)
        self.imgShow.setAlignment(Qt.AlignCenter)
        self.imgShow.setGeometry(30,100,350,350)
        '''
        self.__tmp_img = cv2.resize(self.__tmp_img,(400,
                                        self.img_h*400//self.img_w) if self.img_w >= self.img_h else (self.img_w*400//self.img_h,400))
        '''
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
        
        self.sl = QSlider(Qt.Horizontal,self)
        #self.sl.resize(30,100)
        self.sl.setGeometry(3*self.width()//5 + 10,150,200,30)
        if self.__target == 'light':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'comp':
            self.sl.setMinimum(-30)
            self.sl.setMaximum(50)
        elif self.__target == 'custom':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'hue':
            self.sl.setMinimum(-180)
            self.sl.setMaximum(180)
        else:
            pass
        self.sl.setTickPosition(QSlider.TicksAbove) 
        
        self.sl.valueChanged[int].connect(self.setValue)
        #self.sl.sliderReleased.connect(self.change)
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(550,430,80,30)
        self.ok_btn.clicked.connect(self.saveImage)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(450,430,80,30)
        self.cancel_btn.clicked.connect(self.close)
        
        self.show()
    
    def setTar(self,tar):
        self.__target = tar
    
    def setValue(self,value):
        self.sl.setValue(value)
        self.lb.setText('Value: '+str(value))
        self.change()
        pass
    
    def change(self):
        if self.__target == 'light':
            self.__tmp_img = light(self.__img.Image,self.sl.value())
        elif self.__target == 'comp':
            comp(self.__img.Image,self.sl.value())
            self.__tmp_img = cv2.imread('./tmp/comp.jpg')
        elif self.__target == 'custom':
            self.__tmp_img = custom(self.__img.Image,self.sl.value())
        elif self.__target == 'hue':
            self.__tmp_img = hue(self.__img.Image,self.sl.value())
        else:
            return
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
    
    def saveImage(self):
        self.__img.changeImg(self.__tmp_img)
        self.accept()
        self.close()

if __name__ == '__main__':
    '''
    img = cv2.imread('./samples/26.jpg')
    app = QApplication(sys.argv)
    ex = AdjDialog(img,'hue')
    sys.exit(app.exec_())
'''
    img = cv2.imread('./samples/26.jpg')
    res = comp(img,50)
    #res = custom(img,100)
    #res = hue(img,-50)
    #res = light(img,50)
    cv2.imwrite('./tmp/comp.jpg',res)
