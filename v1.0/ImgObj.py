# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 10:39:53 2019

@author: Quanfita
"""
import numpy as np
import cv2
import Op.Mixed as Mixed
from PyQt5.QtCore import QSettings

class ImgObject(object):
    def __init__(self):
        self.reset()
        self.layer = []
        self.layer_depth = 0
        self.pixNum = self.width * self.height
        self.imgName = 'Untitled'
        #self.AddLayer(self.Image)

    def str_to_hex(self,s):
        s = [int(c.upper(),16) for c in s]
        l = []
        for i in range(0,len(s),2):
            l.append(s[i]*16+s[i+1])
        return l
    
    def reset(self):
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        self.width = settings.value("width")
        self.height = settings.value("height")
        self.color = settings.value("color")
        self.Image = np.zeros((self.height,self.width,3),dtype=np.uint8)
        print(self.color)
        num = self.str_to_hex(self.color[1:])
        print(num)
        self.Image[:,:,0] = num[2]
        self.Image[:,:,1] = num[1]
        self.Image[:,:,2] = num[0]

    def mix(self,img):
        return Mixed.ColorBurn(self.Image,img)
    
    def changeImg(self,img):
        self.Image = img
        self.width = self.Image.shape[1]
        self.height = self.Image.shape[0]
    
    def ImgInfo(self):
        return self.width,self.height
    
    def AddLayer(self,layer=None):
        if layer == None:
            newLayer = np.zeros((self.height,self.width,3),dtype=np.uint8)
        else:
            newLayer = layer
        self.layer_depth +=1
        self.layer.append(newLayer)
        return self.mix(newLayer)
    
    def DelLayer(self,index):
        self.layer.pop(index)
    
    def ExchgLayer(self,old_index,new_index):
        tmp = self.layer.pop(old_index)
        self.layer.insert(new_index,tmp)
    
    def ReMix(self):
        self.changeImg(self.layer[0])
        for i in range(1,len(self.layer)):
            self.changeImg(self.mix(self.layer[i]))

if __name__ == '__main__':
    img = cv2.imread('./samples/26.jpg')
    Img = ImgObject(img)
    Img.AddLayer(img)
    Img.ReMix()
    cv2.imwrite('./tmp/mixed.jpg',Img.Image)