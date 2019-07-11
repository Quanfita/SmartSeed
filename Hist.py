# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 17:45:38 2019

@author: Quanfita
"""
from PyQt5.QtWidgets import QLabel
import cv2
import numpy as np
import ops

class Hist(QLabel):
    
    def __init__(self):
        super().__init__()
        self.setMaximumSize(300,200)
        self.setMinimumSize(270,180)
        self.setStyleSheet('QLabel{color:white;background-color:#535353;border:1px solid #282828;}')
    
    def calcAndDrawHist(self, image, color):  
        hist= cv2.calcHist([image], [0], None, [256], [0.0,255.0])  
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)  
        histImg = np.zeros([256,256,3], np.uint8)  
        hpt = int(0.9* 256)
        if maxVal <1:
            maxVal = 1.0
        for h in range(256):  
            intensity = int(hist[h]*hpt/maxVal)  
            cv2.line(histImg,(h,256), (h,256-intensity), color)  
              
        return histImg
    
    def DrawHistogram(self,img):
        b,g,r = cv2.split(img)
        h_b = self.calcAndDrawHist(b,(255,0,0))
        h_g = self.calcAndDrawHist(g,(0,255,0))
        h_r = self.calcAndDrawHist(r,(0,0,255))
        res = h_b + h_g + h_r
        '''
        for i in range(res.shape[0]):
            for j in range(res.shape[1]):
                if res[i,j].any() == 0:
                    res[i,j,:] = 83'''
        res = cv2.resize(res,(self.width(),self.height()))
        res = cv2.cvtColor(res,cv2.COLOR_BGR2RGB)
        self.setPixmap(ops.cvtCV2Pixmap(res))
        