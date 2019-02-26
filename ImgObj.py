# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 10:39:53 2019

@author: Quanfita
"""
import numpy as np
import cv2
import Op.Mixed as Mixed
from PyQt5.QtCore import QSettings,pyqtSignal,QObject

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

class LayerStack(QObject):
    signal = pyqtSignal()
    def __init__(self):
        super().__init__()
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
        tmp_layer = ImgObject(self.Image)
        self.layer.insert(0,tmp_layer)
        self.mix_list.insert(0,'Normal')
        self.ReMix()
    
    def __str_to_hex(self,s):
        s = [int(c.upper(),16) for c in s]
        l = []
        for i in range(0,len(s),2):
            l.append(s[i]*16+s[i+1])
        return l
    
    def addLayer(self,idx,img=None):
        if type(img) != type(np.zeros((1,1,3))):
            img = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        tmp = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        cen_x,cen_y = (self.__width+1)//2,(self.__height+1)//2
        img_w,img_h = img.shape[1],img.shape[0]
        point_sx = max(cen_x - (img_w+1) // 2,0)
        point_sy = max(cen_y - (img_h+1) // 2,0)
        point_ix = -min(cen_y - (img_w+1) // 2,0)
        point_iy = -min(cen_y - (img_h+1) // 2,0)
        #print(point_sx,point_sy,point_ix,point_iy)
        tmp[point_sy:(point_sy+min(img_h,self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img[point_iy:(point_iy+min(img_h,self.__height)),point_ix:(point_ix+min(img_w,self.__width))]
        tmp_layer = ImgObject(tmp)
        self.Image = tmp
        self.layer.insert(idx,tmp_layer)
        self.mix_list.insert(idx,'Normal')
        self.ReMix()
        self.signal.emit()
        pass
    
    def delLayer(self,idx):
        self.layer.pop(idx)
        self.mix_list.pop(idx)
        self.ReMix()
        self.signal.emit()
        pass
    
    def exchgLayer(self,fore,sup):
        self.signal.emit()
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
        print(self.mix_list)
        self.ReMix()
        self.signal.emit()
        pass
        
    def __mix(self,img,idx):
        if self.mix_list[idx] == "Normal":
            return img.Image
        elif self.mix_list[idx] == "LinearLight":
            return Mixed.LinearLight(self.Image,img.Image)
        elif self.mix_list[idx] == 'Overlay':
            return Mixed.Overlay(self.Image,img.Image)
        elif self.mix_list[idx] == 'Screen':
            return Mixed.Screen(self.Image,img.Image)
        elif self.mix_list[idx] == 'Multiply':
            return Mixed.Multiply(self.Image,img.Image)
        elif self.mix_list[idx] == 'SoftLight':
            return Mixed.SoftLight(self.Image,img.Image)
        elif self.mix_list[idx] == 'HardLight':
            return Mixed.HardLight(self.Image,img.Image)
        elif self.mix_list[idx] == 'LinearAdd':
            return Mixed.Linear_add(self.Image,img.Image)
        elif self.mix_list[idx] == 'ColorBurn':
            return Mixed.ColorBurn(self.Image,img.Image)
        elif self.mix_list[idx] == 'LinearBurn':
            return Mixed.LinearBurn(self.Image,img.Image)
        elif self.mix_list[idx] == 'ColorDodge':
            return Mixed.ColorDodge(self.Image,img.Image)
        elif self.mix_list[idx] == 'LinearDodge':
            return Mixed.LinearDodge(self.Image,img.Image)
        elif self.mix_list[idx] == 'LighterColor':
            return Mixed.LighterColor(self.Image,img.Image)
        elif self.mix_list[idx] == 'VividLight':
            return Mixed.VividLight(self.Image,img.Image)
        elif self.mix_list[idx] == 'PinLight':
            return Mixed.PinLight(self.Image,img.Image)
        elif self.mix_list[idx] == 'HardMix':
            return Mixed.HardMix(self.Image,img.Image)
        elif self.mix_list[idx] == 'Difference':
            return Mixed.Difference(self.Image,img.Image)
        elif self.mix_list[idx] == 'Exclusion':
            return Mixed.Exclusion(self.Image,img.Image)
        elif self.mix_list[idx] == 'Subtract':
            return Mixed.Subtract(self.Image,img.Image)
        elif self.mix_list[idx] == 'Divide':
            return Mixed.Divide(self.Image,img.Image)
        elif self.mix_list[idx] == 'Hue':
            return img.Image #Mixed.Hue(self.Image,img.Image)
        else:
            return img.Image
        
    
    def ReMix(self):
        self.Image = self.layer[0].Image
        cv2.imwrite('./tmp_bottom.jpg',self.layer[0].Image)
        for i in range(1,len(self.layer)):
            self.Image = self.__mix(self.layer[i],i)
    
    def changeImg(self,img):
        self.Image = img
        #self.__width = self.Image.shape[1]
        #self.__height = self.Image.shape[0]
        self.signal.emit()
    
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