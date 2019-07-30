# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 08:37:48 2019

@author: Quanfita
"""

from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import Qt
import numpy as np
import cv2
from PIL import Image

def cvtPixmap2Image(pixmap):
    return pixmap.toImage()

def cvtImage2CV(qimage):
    qimage = qimage.convertToFormat(4)

    width = qimage.width()
    height = qimage.height()

    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
    arr = cv2.cvtColor(arr,cv2.COLOR_BGRA2BGR)
    return arr

def cvtImage2CVAlpha(qimage):
    qimage = qimage.convertToFormat(4)

    width = qimage.width()
    height = qimage.height()

    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
    #arr = cv2.cvtColor(arr,cv2.COLOR_BGRA2BGR)
    return arr

def cvtCV2Image(cvimg):
    height, width, channel = cvimg.shape
    bytesPerLine = 3 * width
    return QImage(cvimg.data, width, height, bytesPerLine,
                       QImage.Format_RGB888).rgbSwapped()

def cvtCV2ImageAlpha(cvimg):
    height, width, channel = cvimg.shape
    bytesPerLine = 4 * width
    return QImage(cvimg.data, width, height, bytesPerLine,
                       QImage.Format_RGBA8888).rgbSwapped()

def cvtImage2Pixmap(image):
    return QPixmap.fromImage(image)

def cvtCV2Pixmap(cvimg):
    tmp = cvtCV2Image(cvimg)
    return QPixmap.fromImage(tmp)

def cvtCV2PixmapAlpha(cvimg):
    tmp = cvtCV2ImageAlpha(cvimg)
    return QPixmap.fromImage(tmp)

def cvtPixmap2CV(pixmap):
    tmp = pixmap.toImage()
    return cvtImage2CV(tmp)

def cvtPixmap2CVAlpha(pixmap):
    tmp = pixmap.toImage()
    return cvtImage2CVAlpha(tmp)

def cvtCV2PIL(cvimg):
    tmp = Image.fromarray(cv2.cvtColor(cvimg,cv2.COLOR_BGR2RGB)) 
    return tmp

def cvtCV2PILAlpha(cvimg):
    tmp = Image.fromarray(cv2.cvtColor(cvimg,cv2.COLOR_BGRA2RGBA),mode='RGBA') 
    return tmp

def cvtPixmap2PIL(pixmap):
    tmp = cvtCV2PIL(cvtPixmap2CV(pixmap))
    return tmp

def cvtPixmap2PILAlpha(pixmap):
    tmp = cvtCV2PILAlpha(cvtPixmap2CVAlpha(pixmap))
    return tmp

def cvtImage2PIL(qimage):
    tmp = cvtCV2PIL(cvtImage2CV(qimage))
    return tmp

def cvtImage2PILAlpha(qimage):
    tmp = cvtCV2PILAlpha(cvtImage2CVAlpha(qimage))
    return tmp

def cvtPIL2CV(pilimg):
    tmp = cv2.cvtColor(np.asarray(pilimg),cv2.COLOR_RGB2BGR)
    return tmp

def cvtPIL2CVAlpha(pilimg):
    tmp = cv2.cvtColor(np.asarray(pilimg),cv2.COLOR_RGBA2BGRA)
    return tmp

def cvtPIL2Pixmap(pilimg):
    tmp = cvtCV2Pixmap(cvtPIL2CV(pilimg))
    return tmp

def cvtPIL2PixmapAlpha(pilimg):
    tmp = cvtCV2PixmapAlpha(cvtPIL2CVAlpha(pilimg))
    return tmp

def cvtPIL2Image(pilimg):
    tmp = cvtCV2Image(cvtPIL2CV(pilimg))
    return tmp

def cvtPIL2ImageAlpha(pilimg):
    tmp = cvtCV2ImageAlpha(cvtPIL2CVAlpha(pilimg))
    return tmp

def saveImgWithPIL(image,name,dpi=72.0,quanlity=90):
    tmp = cvtCV2PIL(image)
    tmp.save(name,dpi=(dpi,dpi),quanlity=quanlity)

def zeroPositionCheck(imgPosition,imgCenter,canCenter):
    distanceX, distanceY = imgCenter[0] - canCenter[0] + imgPosition[0], imgCenter[1] - canCenter[1] + imgPosition[1]
    return (distanceX,distanceY)

def cvtCanPosAndLayerPos(pix,imgPosition,imgCenter,canCenter):
    (disX,disY) = zeroPositionCheck(imgPosition,imgCenter,canCenter)
    return (pix[0] + disX, pix[1] + disY)
'''
def cvtLayerPos2CanPos(pix,imgPosition,imgCenter,canCenter):
    (disX,disY) = zeroPositionCheck(imgPosition,imgCenter,canCenter)
    return (pix[0] + disX, pix[1] + disY)
    '''