# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 16:02:41 2019

@author: Quanfita
"""
import cv2
import numpy as np
import numpy.matlib as nm
import math

def genaratePsf(length,angle):
    half = length // 2
    EPS=np.finfo(float).eps                                 
    alpha = (angle-math.floor(angle/ 180) *180) /180* math.pi
    cosalpha = math.cos(alpha)  
    sinalpha = math.sin(alpha)  
    if cosalpha < 0:
        xsign = -1
    elif angle == 90:
        xsign = 0
    else:  
        xsign = 1
    psfwdt = 1;  
    #模糊核大小
    sx = int(math.fabs(length*cosalpha + psfwdt*xsign - length*EPS))  
    sy = int(math.fabs(length*sinalpha + psfwdt - length*EPS))
    psf1=np.zeros((sy,sx))
     
    #psf1是左上角的权值较大，越往右下角权值越小的核。
    #这时运动像是从右下角到左上角移动
    for i in range(0,sy):
        for j in range(0,sx):
            psf1[i][j] = i*math.fabs(cosalpha) - j*sinalpha
            rad = math.sqrt(i*i + j*j) 
            if  rad >= half and math.fabs(psf1[i][j]) <= psfwdt:  
                temp = half - math.fabs((j + psf1[i][j] * sinalpha) / cosalpha)  
                psf1[i][j] = math.sqrt(psf1[i][j] * psf1[i][j] + temp*temp)
            psf1[i][j] = psfwdt + EPS - math.fabs(psf1[i][j]);  
            if psf1[i][j] < 0:
                psf1[i][j] = 0
    #运动方向是往左上运动，锚点在（0，0）
    anchor=(0,0)
    #运动方向是往右上角移动，锚点一个在右上角
    #同时，左右翻转核函数，使得越靠近锚点，权值越大
    if angle<90 and angle>0:
        psf1=np.fliplr(psf1)
        anchor=(psf1.shape[1]-1,0)
    elif angle>-90 and angle<0:#同理：往右下角移动
        psf1=np.flipud(psf1)
        psf1=np.fliplr(psf1)
        anchor=(psf1.shape[1]-1,psf1.shape[0]-1)
    elif anchor<-90:#同理：往左下角移动
        psf1=np.flipud(psf1)
        anchor=(0,psf1.shape[0]-1)
    psf1=psf1/psf1.sum()
    return psf1,anchor

def GaussianBlur(img,ksize=5,sigma=15):
    tmp = cv2.GaussianBlur(img,(ksize,ksize),sigma)
    return tmp

def MotionBlur(img,length=20,angle=40):
    kernel,anchor=genaratePsf(length,angle)
    tmp=cv2.filter2D(img,-1,kernel,anchor=anchor)
    return tmp

def Blur(img,ksize=5):
    tmp = cv2.blur(img,(ksize,ksize))
    return tmp

def BlurMore(img,ksize=5):
    tmp = img
    for i in range(4):
        tmp = cv2.blur(tmp,(ksize,ksize))
    return tmp

def RadialBlur(img,num=20):
    img_out = np.array(img)
    row, col, channel = img.shape

    xx = np.arange (col) 
    yy = np.arange (row)
    
    x_mask = nm.repmat (xx, row, 1)
    y_mask = nm.repmat (yy, col, 1)
    y_mask = np.transpose(y_mask)
    
    center_y = (row -1) / 2.0
    center_x = (col -1) / 2.0
    
    R = np.sqrt((x_mask - center_x) **2 + (y_mask - center_y) ** 2)
    
    angle = np.arctan2(y_mask - center_y , x_mask - center_x)
    arr = np.arange(num)
    
    for i in range (row):
        for j in range (col):
            R_arr = R[i, j] - arr   
            R_arr[R_arr < 0] = 0
            
            new_x = R_arr * np.cos(angle[i,j]) + center_x
            new_y = R_arr * np.sin(angle[i,j]) + center_y
    
            int_x = new_x.astype(int)
            int_y = new_y.astype(int)
    
            int_x[int_x > col-1] = col - 1
            int_x[int_x < 0] = 0
            int_y[int_y < 0] = 0
            int_y[int_y > row -1] = row -1
    
            img_out[i,j,0] = img[int_y, int_x, 0].sum()/num
            img_out[i,j,1] = img[int_y, int_x, 1].sum()/num
            img_out[i,j,2] = img[int_y, int_x, 2].sum()/num
    return img_out

def SmartBlur(img,c=100,s=5):
    tmp = cv2.bilateralFilter(src=img, d=0, sigmaColor=c, sigmaSpace=s)
    return tmp

if __name__ == '__main__':
    img = cv2.imread('F:\\SmartSeed\\samples\\4.jpg')
    #GB = GaussianBlur(img)
    #MB = MotionBlur(img)
    #B = Blur(img)
    #RB = RadialBlur(img)
    SB = SmartBlur(img)
    #cv2.imwrite('../tmp/GB.jpg',GB)
    #cv2.imwrite('../tmp/MB.jpg',MB)
    #cv2.imwrite('../tmp/B.jpg',B)
    #cv2.imwrite('../tmp/RB.jpg',RB)
    cv2.imwrite('../tmp/SB.jpg',SB)