# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 11:12:14 2018

@author: Quanfita
"""

import cv2
import numpy as np
import numba

def Screen(img1,img2):#滤色
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = 1 - np.multiply((1 - img1),(1 - img2))
    res = (res*255).astype(np.uint8)
    return res

def Multiply(img1,img2):
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = np.multiply(img1,img2)
    res = (res*255).astype(np.uint8)
    return res

@numba.jit
def Overlay(img1,img2):#叠加
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for row in range(height):            #遍历高
        for col in range(weight):         #遍历宽
            for c in range(channels):     #便利通道
                if img2[row, col, c] <0.5:
                    res[row, col, c] = 2*img1[row, col, c]*img2[row, col, c];
                else:
                    res[row, col, c] = 1 - 2 * (1 - img1[row, col, c]) * (1 - img2[row, col, c])
    res = (255*res).astype(np.uint8)
    return res

@numba.jit
def SoftLight(img1,img2):#柔光
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for row in range(height):            #遍历高
        for col in range(weight):         #遍历宽
            for c in range(channels):     #便利通道
                if img1[row, col, c] <0.5:
                    res[row, col, c] = (2 * img1[row, col, c] - 1)*(img2[row, col, c] - img2[row, col, c]**2) + img2[row, col, c]
                else:
                    res[row, col, c] = (2 * img1[row, col, c] - 1)*(np.sqrt(img2[row, col, c]) - img2[row, col, c]) + img2[row, col, c]
    res = (255*res).astype(np.uint8)
    return res

@numba.jit
def HardLight(img1,img2):#强光
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for row in range(height):            #遍历高
        for col in range(weight):         #遍历宽
            for c in range(channels):     #便利通道
                if img1[row, col, c] <0.5:
                    res[row, col, c] = 2*img1[row, col, c]*img2[row, col, c];
                else:
                    res[row, col, c] = 1 - 2 * (1 - img1[row, col, c])*(1 - img2[row, col, c])
    res = (255*res).astype(np.uint8)
    return res

def Linear_add(img1,img2,a=0.5):#线性叠加
    res = a*img1+(1-a)*img2
    return res.astype(np.uint8)

def ColorBurn(img1,img2):#颜色加深
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    tmp = np.zeros(img1.shape,dtype=np.float32)
    res = (img1 + img2 - 1.0) / (img2+0.01)
    res = np.maximum(tmp,res)
    res = (res*255).astype(np.uint8)
    return res

def LinearBurn(img1,img2):#线性加深
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = img1 + img2 - 1.0
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

def ColorDodge(img1,img2):#颜色减淡
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = img1 + (img2 * img1) / (1.0 - img2 + 0.01)
    res = np.maximum(0.0,res)
    res = np.minimum(1.0,res)
    res = (res*255).astype(np.uint8)
    return res

def LinearDodge(img1,img2):#线性减淡
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = img1 + img2
    res = np.minimum(1.0,res)
    res = (res*255).astype(np.uint8)
    return res

@numba.jit
def LighterColor(img1,img2):#浅色
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for i in range(height):            #遍历高
        for j in range(weight):         #遍历宽
            if np.sum(img1[i,j]) >= np.sum(img2[i,j]):
                res[i,j] = img1[i,j]
            else:
                res[i,j] = img2[i,j]   
    res = (255*res).astype(np.uint8)
    return res

@numba.jit
def VividLight(img1,img2):#亮光
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for i in range(height):            #遍历高
        for j in range(weight):         #遍历宽
            for c in range(channels):
                if img2[i,j,c] >= 0.5:
                    res[i,j,c] = 1.0 - (1.0 - img1[i,j,c]) / (2.0 * img2[i,j,c] + 0.01)
                else:
                    res[i,j,c] = img1[i,j,c] / (2.0 * (1.0 - img2[i,j,c]))
    res = (255*res).astype(np.uint8)
    return res

def LinearLight(img1,img2):#线性光
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = 2 * img1 + img2 - 1.0
    res = np.minimum(1.0,res)
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

@numba.jit
def PinLight(img1,img2):#点光
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for i in range(height):            #遍历高
        for j in range(weight):         #遍历宽
            for c in range(channels):
                if img1[i,j,c] <= 2 * img2[i,j,c] - 1.0:
                    res[i,j,c] = 2 * img2[i,j,c] - 1.0
                elif 2 * img2[i,j,c] - 1.0 < img1[i,j,c] < 2 * img2[i,j,c]:
                    res[i,j,c] = img1[i,j,c]
                else:
                    res[i,j,c] = 2 * img2[i,j,c]
    res = (255*res).astype(np.uint8)
    return res

@numba.jit
def HardMix(img1,img2):#实色混合
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    height = img1.shape[0]
    weight = img1.shape[1]
    channels = img1.shape[2]
    res = np.zeros([height,weight,channels],dtype=np.float32)
    
    for i in range(height):            #遍历高
        for j in range(weight):         #遍历宽
            for c in range(channels):
                if img1[i,j,c] + img2[i,j,c] < 1.0:
                    res[i,j,c] = 0.0
                else:
                    res[i,j,c] = 1.0
    res = (255*res).astype(np.uint8)
    return res

def Difference(img1,img2):#差色
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = np.abs(img2-img1)
    res = np.minimum(1.0,res)
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

def Exclusion(img1,img2):#排除
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = (img1 + img2) - (img1*img2)/0.5
    res = np.minimum(1.0,res)
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

def Subtract(img1,img2):#减去
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = img1 - img2
    res = np.minimum(1.0,res)
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

def Divide(img1,img2):#划分
    img1 = img1 / 255.0
    img2 = img2 / 255.0
    res = img1 / (img2+0.01)
    res = np.minimum(1.0,res)
    res = np.maximum(0.0,res)
    res = (res*255).astype(np.uint8)
    return res

def Hue(img1,img2):#色相
    pass

if __name__ == '__main__':
    img1 = cv2.imread('./tmp/noise.jpg')
    img2 = cv2.imread('./tmp/Gaussian_sigma.jpg')
    #screen = Screen(img1,img2)
    #overlay = Overlay(img1,img2)
    #softlight = SoftLight(img1,img2)
    #hardlight = HardLight(img1,img2)
    #multiply = Multiply(img1,img2)
    #colorburn = ColorBurn(img1,img2)
    #linearburn = LinearBurn(img1,img2)
    #colordodge = ColorDodge(img1,img2)
    #lineardodge = LinearDodge(img1,img2)
    #lightercolor = LighterColor(img1,img2)
    #vividlight = VividLight(img1,img2)
    #linearlight = LinearLight(img1,img2)
    #pinlight = PinLight(img1,img2)
    #hardmix = HardMix(img1,img2)
    #difference = Difference(img1,img2)
    #exclusion = Exclusion(img1,img2)
    #subtract = Subtract(img1,img2)
    divide = Divide(img1,img2)
    #cv2.imwrite('./tmp/screen.jpg',screen)
    #cv2.imwrite('./tmp/overlay.jpg',overlay)
    #cv2.imwrite('./tmp/softlight.jpg',softlight)
    #cv2.imwrite('./tmp/hardlight.jpg',hardlight)
    #cv2.imwrite('./tmp/multiply.jpg',multiply)
    #cv2.imwrite('./tmp/colorburn.jpg',colorburn)
    #cv2.imwrite('./tmp/linearburn.jpg',linearburn)
    #cv2.imwrite('./tmp/colordodge.jpg',colordodge)
    #cv2.imwrite('./tmp/lineardodge.jpg',lineardodge)
    #cv2.imwrite('./tmp/lightercolor.jpg',lightercolor)
    #cv2.imwrite('./tmp/vividlight.jpg',vividlight)
    #cv2.imwrite('./tmp/linearlight.jpg',linearlight)
    #cv2.imwrite('./tmp/pinlight.jpg',pinlight)
    #cv2.imwrite('./tmp/hardmix.jpg',hardmix)
    #cv2.imwrite('./tmp/difference.jpg',difference)
    #cv2.imwrite('./tmp/exclusion.jpg',exclusion)
    #cv2.imwrite('./tmp/subtract.jpg',subtract)
    cv2.imwrite('./tmp/divide.jpg',divide)
