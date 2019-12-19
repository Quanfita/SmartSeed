# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 20:49:26 2019

@author: Quanfita
"""

import cv2
import numpy as np


def USM(img,alpha=10,thresh=20):
    img = img * 1.0
    gauss_out = cv2.GaussianBlur(img, (5,5),5)
    
    # alpha 0 - 5
    alpha = alpha / 20
    img_out = (img - gauss_out) * alpha + img
    
    img_out = img_out/255.0
    
    # 饱和处理
    mask_1 = img_out  < 0 
    mask_2 = img_out  > 1
    
    img_out = img_out * (1-mask_1)
    img_out = img_out * (1-mask_2) + mask_2
    return (img_out*255).astype(np.uint8)

def EdgeSharp(img,alpha=10):
    tmp = np.copy(img)
    tmp = cv2.cvtColor(tmp,cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(thresh, 30, 70)
    cv2.imwrite('../tmp/mask.jpg',edges)
    enhan = edges * alpha
    img_out = cv2.merge([enhan,enhan,enhan]) +img
    img_out = img_out/255.0
    
    # 饱和处理
    mask_1 = img_out  < 0 
    mask_2 = img_out  > 1
    
    img_out = img_out * (1-mask_1)
    img_out = img_out * (1-mask_2) + mask_2
    return (img_out*255).astype(np.uint8)

def SmartSharp(img):
    pass

if __name__ == '__main__':
    img = cv2.imread('../samples/26.jpg')
    usm = EdgeSharp(img,100)
    cv2.imwrite('../tmp/usm.jpg',usm)