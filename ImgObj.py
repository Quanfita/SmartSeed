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
    def __init__(self,img):
        self.Image = img
        self.__width, self.__height = self.Image.shape[1],self.Image.shape[0]
        self.__pixNum = self.__width * self.__height

    def changeImg(self,img):
        self.Image = img
        self.__width = self.Image.shape[1]
        self.__height = self.Image.shape[0]
    
    def ImgInfo(self):
        return self.__width,self.__height
    
    def width(self):
        return self.__width
    
    def height(self):
        return self.__height

class LayerStack(object):
    
    def __init__(self):
        self.layer = []
        self.mix_list = []
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        try:
            self.__width = eval(settings.value("width"))
            self.__height = eval(settings.value("height"))
        except TypeError:
            self.__width = settings.value("width")
            self.__height = settings.value("height")
        self.color = settings.value("color")
        self.Image = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        num = self.__str_to_hex(self.color[1:])
        self.pixNum = self.__width * self.__height
        self.Image[:,:,0] = num[2]
        self.Image[:,:,1] = num[1]
        self.Image[:,:,2] = num[0]
        self.addLayer(0,self.Image)
    
    def __str_to_hex(self,s):
        s = [int(c.upper(),16) for c in s]
        l = []
        for i in range(0,len(s),2):
            l.append(s[i]*16+s[i+1])
        return l
    
    def addLayer(self,idx,img=None):
        if type(img) != type(np.zeros((1,1,3))):
            img = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        tmp_layer = ImgObject(img)
        self.Image = img
        self.layer.insert(idx,tmp_layer)
        self.mix_list.insert(idx,'Normal')
        self.ReMix()
        pass
    
    def delLayer(self,idx):
        self.layer.pop(idx)
        self.mix_list.pop(idx)
        pass
    
    def exchgLayer(self,fore,sup):
        pass
    
    def sltLayer(self,idx):
        self.tmp_img = self.layer[idx].Image
        pass
    
    def cpyLayer(self,idx):
        self.addLayer(idx,self.Image)
        pass
    
    def getNum(self):
        return len(self.layer)
    
    def setMix(self,idx,mix):
        self.mix_list[idx] = mix
        pass
        
    def __mix(self,img,idx):
        if self.mix_list[idx] == "Normal":
            return img.Image
        elif self.mix_list[idx] == "LinearLight":
            return Mixed.LinearLight(self.Image,img)
        else:
            return img.Image
        
    
    def ReMix(self):
        self.Image = self.layer[0].Image
        for i in range(1,len(self.layer)):
            self.Image = self.__mix(self.layer[i],i)
    
    def changeImg(self,img):
        self.Image = img
        self.__width = self.Image.shape[1]
        self.__height = self.Image.shape[0]
    
    def ImgInfo(self):
        return self.__width,self.__height
    
    def width(self):
        return self.__width
    
    def height(self):
        return self.__height

if __name__ == '__main__':
    img = cv2.imread('./samples/26.jpg')
    Img = ImgObject(img)
    Img.AddLayer(img)
    Img.ReMix()
    cv2.imwrite('./tmp/mixed.jpg',Img.Image)