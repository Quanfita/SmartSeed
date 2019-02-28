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
    def __init__(self,img,mask=None):
        self.Image = img
        if mask == None:
            mask = np.zeros(self.Image.shape,dtype=np.uint8)
            mask = 255
        self.mask = mask
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
    def __init__(self,init=None):
        super().__init__()
        self.layer = []
        self.mix_list = []
        if init == None:
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            try:
                self.__width = eval(settings.value("width"))
                self.__height = eval(settings.value("height"))
            except TypeError:
                self.__width = settings.value("width")
                self.__height = settings.value("height")
            self.color = settings.value("color")
            self.Image = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
            self.color_num = self.__str_to_hex(self.color[1:])
            self.pixNum = self.__width * self.__height
            self.Image[:,:,0] = self.color_num[2]
            self.Image[:,:,1] = self.color_num[1]
            self.Image[:,:,2] = self.color_num[0]
        else:
            self.Image = init
        tmp_layer = ImgObject(self.Image)
        self.layer.insert(0,tmp_layer)
        self.mix_list.insert(0,'Normal')
        self.__remix()
    
    def __str_to_hex(self,s):
        s = [int(c.upper(),16) for c in s]
        l = []
        for i in range(0,len(s),2):
            l.append(s[i]*16+s[i+1])
        return l
    
    def __getVisibleArea(self,img):
        tmp = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        mask = np.zeros((self.__height,self.__width),dtype=np.uint8)
        
        tmp[:,:,0] = self.color_num[2]
        tmp[:,:,1] = self.color_num[1]
        tmp[:,:,2] = self.color_num[0]
        
        cen_x,cen_y = (self.__width+1)//2,(self.__height+1)//2
        img_w,img_h = img.shape[1],img.shape[0]
        point_sx = max(cen_x - (img_w+1) // 2,0)
        point_sy = max(cen_y - (img_h+1) // 2,0)
        point_ix = -min(cen_x - (img_w+1) // 2,0)
        point_iy = -min(cen_y - (img_h+1) // 2,0)
        tmp[point_sy:(point_sy+min(img_h,self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img[point_iy:(point_iy+min(img_h,self.__height)),point_ix:(point_ix+min(img_w,self.__width))]
        mask[point_sy:(point_sy+min(img_h,self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = 255
        return tmp,mask
    
    def addLayer(self,idx,img=None):
        if type(img) != type(np.zeros((1,1,3))):
            img = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
            img[:,:,0] = self.color_num[2]
            img[:,:,1] = self.color_num[1]
            img[:,:,2] = self.color_num[0]
        '''
        tmp = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        cen_x,cen_y = (self.__width+1)//2,(self.__height+1)//2
        img_w,img_h = img.shape[1],img.shape[0]
        point_sx = max(cen_x - (img_w+1) // 2,0)
        point_sy = max(cen_y - (img_h+1) // 2,0)
        point_ix = -min(cen_y - (img_w+1) // 2,0)
        point_iy = -min(cen_y - (img_h+1) // 2,0)
        #print(point_sx,point_sy,point_ix,point_iy)
        tmp[point_sy:(point_sy+min(img_h,self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img[point_iy:(point_iy+min(img_h,self.__height)),point_ix:(point_ix+min(img_w,self.__width))]
        '''
        tmp_layer = ImgObject(img)
        self.layer.insert(idx,tmp_layer)
        self.mix_list.insert(idx,'Normal')
        self.__remix()
        pass
    
    def delLayer(self,idx):
        self.layer.pop(idx)
        self.mix_list.pop(idx)
        self.__remix()
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
        self.__remix()
        pass
    
    def __getMaskRes(self,img,mask):
        mask_inv = cv2.bitwise_not(mask)
        fg = cv2.bitwise_and(img,img,mask = mask)
        bg = cv2.bitwise_and(self.Image,self.Image,mask = mask_inv)
        return cv2.add(bg,fg)
    
    def __mix(self,img,idx):
        if self.mix_list[idx] == "Normal":
            _img, mask = self.__getVisibleArea(img.Image)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == "LinearLight":
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Overlay(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Overlay':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Overlay(self.Image,_img)
            return self.__getMaskRes(_img,mask)
            #return Mixed.Overlay(self.Image,self.__getVisibleArea(img.Image))
        elif self.mix_list[idx] == 'Screen':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Screen(self.Image,)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Multiply':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Multiply(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'SoftLight':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.SoftLight(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardLight':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.HardLight(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearAdd':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Linear_add(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorBurn':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.ColorBurn(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearBurn':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.LinearBurn(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorDodge':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.ColorDodge(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearDodge':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.LinearDodge(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LighterColor':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.LighterColor(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'VividLight':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.VividLight(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'PinLight':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.PinLight(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardMix':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.HardMix(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Difference':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Difference(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Exclusion':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Exclusion(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Subtract':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Subtract(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Divide':
            _img, mask = self.__getVisibleArea(img.Image)
            _img = Mixed.Divide(self.Image,_img)
            return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Hue':
            _img, mask = self.__getVisibleArea(img.Image)
            #_img = Mixed.Hue(self.Image,_img)
            return self.__getMaskRes(_img,mask) #Mixed.Hue(self.Image,img.Image)
        else:
            _img, mask = self.__getVisibleArea(img.Image)
            return self.__getMaskRes(_img,mask)
        
    
    def __remix(self):
        self.Image,mask = self.__getVisibleArea(self.layer[0].Image)
        cv2.imwrite('./tmp_bottom.jpg',self.layer[0].Image)
        for i in range(1,len(self.layer)):
            self.Image = self.__mix(self.layer[i],i)
        self.signal.emit()
    
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
    
    def reset(self,width,height):
        r_w = width / self.__width
        r_h = height / self.__height
        for i in range(len(self.layer)):
            tmp_w,tmp_h = self.layer[i].width()*r_w,self.layer[i].height()*r_h
            self.layer[i].changeImg(cv2.resize(self.layer[i].Image,(int(tmp_w),int(tmp_h))))
        self.__width = width
        self.__height = height
        self.__remix()
    
    def resize(self,width,height):
        self.__width = width
        self.__height = height
        self.__remix()

if __name__ == '__main__':
    img = cv2.imread('./samples/26.jpg')
    Img = ImgObject(img)
    Img.AddLayer(img)
    #Img.__remix()
    cv2.imwrite('./tmp/mixed.jpg',Img.Image)