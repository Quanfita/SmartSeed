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
