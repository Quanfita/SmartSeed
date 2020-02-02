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
import numba
import time

def imread(imagename):
    tag = imagename.split('.')[-1]
    if tag in ['jpg', 'jpeg', 'jpe', 'jfif']:
        _type = 'JPEG'
    img = cv2.imread(imagename,cv2.IMREAD_UNCHANGED)
    if img is None:
        raise Exception("Error! Image cannot be read...")
    if len(img.shape) < 3:
        if len(img.shape) == 2:
            img = cv2.merge([img, img, img, np.ones(img.shape, dtype=np.uint8)*255])
        else:
            raise Exception("ShapeError: Image shape is not right.")
    elif len(img.shape) == 3:
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 4:
            pass
        else:
            raise Exception("ShapeError: Image shape is not right.")
    else:
        raise Exception("ShapeError: Image shape is not right.")
    return img

def imsave(image, imagename, depth=8, dpi=72.0, quanlity=80):
    img = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGRA2RGBA))
    img.save(imagename, dpi=(dpi,dpi), quanlity=quanlity)

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
    if len(cvimg.shape) < 3:
        cvimg = cv2.cvtColor(cvimg,cv2.COLOR_GRAY2BGR)
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

def cvtCanPosAndLayerPos(pix,imgPosition,imgCenter,canCenter,offset=(0,0)):
    (disX,disY) = zeroPositionCheck(imgPosition,imgCenter,canCenter)
    return (pix[0] + disX + offset[0], pix[1] + disY + offset[1])

def addWithAlpha(self,imgT,imgB):
    imgT,imgB = imgT/255,imgB/255
    tmp = imgT[:,:,:3]*imgT[:,:,3] + (1 - imgT[:,:,3])*imgB[:,:,:3]*imgB[:,:,3]
    return (255*tmp).astype(np.uint8)

def drawBackground(w,h):
    img = np.ones([h,w,3],dtype=np.uint8)
    img = img*255
    for i in range(0,img.shape[0],20):
        for j in range(0,img.shape[1],20):
            if j+10 >= img.shape[1] and i+10>=img.shape[0]:
                img[i:,j:] = 204
            elif (j+10 < img.shape[1] and i+10 < img.shape[0]) and (j+20 >= img.shape[1] and i+20>=img.shape[0]):
                img[i:i+10,j:j+10] = 204
                img[i+10:,j+10:] = 204
            elif j+10 >= img.shape[1]:
                img[i:i+10,j:] = 204
            elif i+10>=img.shape[0]:
                img[i:,j:j+10] = 204
            else:
                img[i:i+10,j:j+10] = 204
                img[i+10:i+20,j+10:j+20] = 204
    img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
    return img

def resizeAdjustment(img,width,height):
    h,w = img.shape[0],img.shape[1]
    s_h,s_w = h/height,w/width
    if s_h > s_w:
        img = cv2.resize(img,(int(w/s_h),height))
    else:
        img = cv2.resize(img,(width,int(h/s_w)))
    return img

def getFitSize(shape,width,height):
    h,w,_ = shape
    s_h,s_w = h/height,w/width
    if s_h > s_w:
        return int(w/s_h),height
    else:
        return width,int(h/s_w)

def resize(img,width,height):
    return cv2.resize(img,(width,height))

def gcd(a,b):
    if b!=0:
        return gcd(b,a%b)
    else:
        return a

def makeIcon(image):
    icon = np.zeros([30,40,4],dtype=np.uint8)
    img = resizeAdjustment(image,40,30)
    c_x,c_y = img.shape[1]//2,img.shape[0]//2
    s_x,s_y = max(20-c_x,0),max(15-c_y,0)
    icon[s_y:s_y+img.shape[0],s_x:s_x+img.shape[1],:] = img
    icon = cv2.copyMakeBorder(icon,3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200,255])
    return cvtCV2PixmapAlpha(icon)

def cvtRGB2BGR(RGB):
    r,g,b = RGB
    return (b,g,r)

def cvtBGR2RGB(BGR):
    b,g,r = BGR
    return (r,g,b)

def cvtRGBA2BGRA(RGBA):
    r,g,b,a = RGBA
    return (b,g,r,a)

def cvtBGRA2RGBA(BGRA):
    b,g,r,a = BGRA
    return (r,g,b,a)

def generateHueColorPicker(BGR):
    b,g,r = BGR
    res = np.zeros([256,256,3],dtype=np.uint8)
    res[:,:] = [b,g,r]
    h,w,_ = res.shape
    @numba.jit
    def getRes(res):
        if b == 255:
            for i in range(h):
                for j in range(w):
                    res[i,j] = [b*(h-i)/h,(g+(255-g)*(w-j)/w)*(h-i)/h,(r+(255-r)*(w-j)/w)*(h-i)/h]
        elif g == 255:
            for i in range(h):
                for j in range(w):
                    res[i,j] = [(b+(255-b)*(w-j)/w)*(h-i)/h,g*(h-i)/h,(r+(255-r)*(w-j)/w)*(h-i)/h]
        elif r == 255:
            for i in range(h):
                for j in range(w):
                    res[i,j] = [(b+(255-b)*(w-j)/w)*(h-i)/h,(g+(255-g)*(w-j)/w)*(h-i)/h,r*(h-i)/h]
        return res
    return getRes(res).astype(np.uint8)

def generateHueColorLine():
    res = np.zeros([256*6,30,3],dtype=np.uint8)
    for i in range(256):
        res[i,:] = [0,i,255]
    for i in range(256):
        res[i+256,:] = [0,255,255-i]
    for i in range(256):
        res[i+256*2,:] = [i,255,0]
    for i in range(256):
        res[i+256*3,:] = [255,255-i,0]
    for i in range(256):
        res[i+256*4,:] = [255,0,i]
    for i in range(256):
        res[i+256*5,:] = [255-i,0,255]
    return res

def generateLightColorPicker():
    res = np.zeros([256,256*6,3],dtype=np.uint8)
    for j in range(256):
        for i in range(256):
            res[j,i] = [j,int(i+(255-i)*j/255),255]
        for i in range(256):
            res[j,i+256] = [j,255,int(255-i+(i)*j/255)]
        for i in range(256):
            res[j,i+256*2] = [int(i+(255-i)*j/255),255,j]
        for i in range(256):
            res[j,i+256*3] = [255,int(255-i+(i)*j/255),j]
        for i in range(256):
            res[j,i+256*4] = [255,j,int(i+(255-i)*j/255)]
        for i in range(256):
            res[j,i+256*5] = [int(255-i+(i)*j/255),j,255]
    return res

def generateLightColorLine(BGR):
    b,g,r = BGR
    res = np.zeros([256,30,3],dtype=np.uint8)
    res[:,:] = [b,g,r]
    for i in range(256):
        res[i,:] = [int(b*(1-i/255)),int(g*(1-i/255)),int(r*(1-i/255))]
    return res

'''
def cvtLayerPos2CanPos(pix,imgPosition,imgCenter,canCenter):
    (disX,disY) = zeroPositionCheck(imgPosition,imgCenter,canCenter)
    return (pix[0] + disX, pix[1] + disY)
    '''

if __name__ == '__main__':
    drawBackground(1200,800)