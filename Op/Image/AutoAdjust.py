# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 09:54:02 2019

@author: Quanfita
"""

import cv2
import math
import numpy as np

class ACE(object):
    
    def __init__(self):
        self.g_para = {}
 
    def stretchImage(self,data, s=0.005, bins = 2000):    #线性拉伸，去掉最大最小0.5%的像素值，然后线性拉伸至[0,1]
        ht = np.histogram(data, bins);
        d = np.cumsum(ht[0])/float(data.size)
        lmin = 0; lmax=bins-1
        while lmin<bins:
            if d[lmin]>=s:
                break
            lmin+=1
        while lmax>=0:
            if d[lmax]<=1-s:
                break
            lmax-=1
        return np.clip((data-ht[1][lmin])/(ht[1][lmax]-ht[1][lmin]), 0,1)
     
    def getPara(self,radius = 5):                        #根据半径计算权重参数矩阵
        m = self.g_para.get(radius, None)
        if m is not None:
            return m
        size = radius*2+1
        m = np.zeros((size, size))
        for h in range(-radius, radius+1):
            for w in range(-radius, radius+1):
                if h==0 and w==0:
                    continue
                m[radius+h, radius+w] = 1.0/math.sqrt(h**2+w**2)
        m /= m.sum()
        self.g_para[radius] = m
        return m
     
    def zmIce(self, I, ratio=4, radius=300):                     #常规的ACE实现
        para = self.getPara(radius)
        height,width = I.shape
        zh,zw = [0]*radius + [x for x in range(height)] + [height-1]*radius, [0]*radius + [x for x in range(width)]  + [width -1]*radius
        Z = I[np.ix_(zh, zw)]
        res = np.zeros(I.shape)
        for h in range(radius*2+1):
            for w in range(radius*2+1):
                if para[h][w] == 0:
                    continue
                res += (para[h][w] * np.clip((I-Z[h:h+height, w:w+width])*ratio, -1, 1))
        return res
     
    def zmIceFast(self, I, ratio, radius):                #单通道ACE快速增强实现
        height, width = I.shape[:2]
        if min(height, width) <=2:
            return np.zeros(I.shape)+0.5
        Rs = cv2.resize(I, ((width+1)//2, (height+1)//2))
        Rf = self.zmIceFast(Rs, ratio, radius)             #递归调用
        Rf = cv2.resize(Rf, (width, height))
        Rs = cv2.resize(Rs, (width, height))
     
        return Rf+self.zmIce(I,ratio, radius)-self.zmIce(Rs,ratio,radius)    
                
    def zmIceColor(self, I, ratio=4, radius=3):               #rgb三通道分别增强，ratio是对比度增强因子，radius是卷积模板半径
        I = I / 255.0
        res = np.zeros(I.shape)
        for k in range(3):
            res[:,:,k] = self.stretchImage(self.zmIceFast(I[:,:,k], ratio, radius))
        return (res*255).astype(np.uint8)

def AWB(img):
    b,g,r = cv2.split(img)
    B,G,R = np.mean(b),np.mean(g),np.mean(r)
    kb,kg,kr = (R + G + B) / (3*B),(R + G + B) / (3*G),(R + G + B) / (3*R)
    b,g,r = b*kb, g*kg, r*kr
    final = cv2.merge([b,g,r])
    return final.astype(np.uint8)

def ACA(image):
    #CLAHE
    b,g,r = cv2.split(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    b = clahe.apply(b)
    g = clahe.apply(g)
    r = clahe.apply(r)
    image = cv2.merge([b,g,r])
    return image.astype(np.uint8)

def ImageSize(img,width,height):
    img = cv2.resize(img,(width,height))
    return img.astype(np.uint8)

def CanvasSize(img,width,height):
    canvas = np.ones((height,width,3),dtype=np.uint8)
    canvas *= 255
    cen_x,cen_y = (width+1)//2,(height+1)//2
    img_w,img_h = img.shape[1],img.shape[0]
    point_sx = cen_x - (img_w+1) // 2
    point_sy = cen_y - (img_h+1) // 2
    canvas[point_sy:(point_sy+img_h),point_sx:(point_sx+img_w)] = img
    return canvas.astype(np.uint8)

if __name__ == '__main__':
    image = cv2.imread('555.jpg')
    #aca = ACA(image)
    #awb = AWB(image)
    #ace = ACE().zmIceColor(image)
    #cv2.imwrite('aca.jpg',aca,[cv2.IMWRITE_JPEG_QUALITY, 50])
    #cv2.imwrite('awb.jpg',awb,[cv2.IMWRITE_JPEG_QUALITY, 50])
    #cv2.imwrite('ace.jpg',ace,[cv2.IMWRITE_JPEG_QUALITY, 50])
    cv2.imwrite('newcanvas.jpg',CanvasSize(image,1024,1024))