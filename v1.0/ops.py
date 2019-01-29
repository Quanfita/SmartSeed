# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 08:37:48 2019

@author: Quanfita
"""

from PyQt5.QtGui import QImage,QPixmap
import numpy as np
import cv2

def cvtPixmap2Image(pixmap):
    return pixmap.toImage()

def cvtImage2CV(qimage,dtype='array'):
    qimage = qimage.convertToFormat(4)

    width = qimage.width()
    height = qimage.height()

    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
    arr = cv2.cvtColor(arr,cv2.COLOR_BGRA2BGR)
    return arr

def cvtCV2Image(cvimg):
    height, width, channel = cvimg.shape
    bytesPerLine = 3 * width
    return QImage(cvimg.data, width, height, bytesPerLine,
                       QImage.Format_RGB888).rgbSwapped()

def cvtImage2Pixmap(image):
    return QPixmap.fromImage(image)

def cvtCV2Pixmap(cvimg):
    tmp = cvtCV2Image(cvimg)
    return QPixmap.fromImage(tmp)

def cvtPixmap2CV(pixmap):
    tmp = pixmap.toImage()
    return cvtImage2CV(tmp)