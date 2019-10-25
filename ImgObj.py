# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 10:39:53 2019

@author: Quanfita
"""
import numpy as np
import cv2
import ops
import logger
import Op.Mixed as Mixed
from PyQt5.QtCore import QSettings,pyqtSignal,QObject

class ImgObject(object):
    def __init__(self,img,mask=None,debug=False):
        self.__debug = debug
        self.__layerName = ''
        self._rect = None
        self.__opacity = 1.0
        if img.shape[2] == 3:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 1:
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
        self.Image = img
        self.__realImage = img
        self._offset = (0,0)
        self.__icon = ops.cvtCV2PixmapAlpha(cv2.copyMakeBorder(cv2.resize(img,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200,255]))
        
        self.__mask = self.Image[:,:,3]
        self.__width, self.__height = self.__realImage.shape[1],self.__realImage.shape[0]
        self.__pixNum = self.__width * self.__height
        self.__hasHiddenLayer = False
        self.__posOnCanvas = (-1,-1)
    
    @property
    def mask(self):
        return self.__mask
    
    @mask.setter
    def mask(self, mask):
        self.__mask = self.Image[:,:,3] = mask

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, val):
        self._offset = (self._offset[0] - val[0],self._offset[1] - val[1])
    
    @property
    def layerName(self):
        return self.__layerName

    @layerName.setter
    def layerName(self, layerName):
        self.__layerName = layerName
        if self.__debug:
            logger.debug('Set layer name:'+self.__layerName)
    
    @property
    def opacity(self):
        return self.__opacity
    
    @opacity.setter
    def opacity(self, opacity):
        self.__opacity = opacity
    
    @property
    def imageRect(self):
        return self._rect
    
    @imageRect.setter
    def imageRect(self, rect):
        self._rect = rect
    
    @property
    def layer(self):
        return self._layer
    
    @property
    def icon(self):
        return self.__icon
    
    @icon.setter
    def icon(self, icon):
        self.__icon = icon
    
    def getImage(self):
        return self.Image
    
    def changeImg(self, img):
        if img.shape[2] == 3:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 1:
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
        self.Image = img
        self.__icon = ops.cvtCV2PixmapAlpha(cv2.copyMakeBorder(cv2.resize(img,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200,255]))
        self.__width = self.__realImage.shape[1]
        self.__height = self.__realImage.shape[0]
        if self.hasHiddenLayer():
            self.selfUpdate()
        if self.__debug:
            logger.debug('Changed image, shape:'+str((self.__height,self.__width)))
    
    def ImgInfo(self):
        return self.__width,self.__height
    
    def width(self):
        return self.__width
    
    def height(self):
        return self.__height
    
    def getCenterOfImage(self):
        if self.__debug:
            logger.debug('The center of image:'+str(((self.__width+1) //2,(self.__height+1) //2)))
        return ((self.__width+1) //2,(self.__height+1) //2)
    
    def getPositionOnCanvas(self):
        if self.__debug:
            logger.debug('The position on canvas:'+str(self.__posOnCanvas))
        return self.__posOnCanvas
    
    def setPositionOnCanvas(self,pos):
        if self.__debug:
            logger.debug('Set position on canvas:'+str(pos))
        self.__posOnCanvas = pos
    
    def setPositionOnCanvasByDistance(self,distance):
        pos = (self.__posOnCanvas[0] + distance[0], self.__posOnCanvas[1] + distance[1])
        if self.__debug:
            logger.debug('Set position on canvas:'+str(pos))
        self.__posOnCanvas = pos
    
    def isPosOutOfLayer(self,pos):
        if self._rect[0] < pos[0] < self._rect[2] and self._rect[1] < pos[1] < self._rect[3]:
            return False
        else:
            return True
    
    def hasHiddenLayer(self):
        return self.__hasHiddenLayer
    
    def addHiddenLayer(self):
        self.hiddenLayer = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        self.hiddenMask = np.zeros((self.__height,self.__width),dtype=np.uint8)
    
    def selfUpdate(self):
        if self.hasHiddenLayer():
            mask_inv = cv2.bitwise_not(self.hiddenMask)
            fg = cv2.bitwise_and(self.hiddenLayer,self.hiddenLayer,mask = self.hiddenMask)
            bg = cv2.bitwise_and(self.Image,self.Image,mask = mask_inv)
            self.Image = cv2.add(bg,fg)
            self.__mask = cv2.bitwise_or(self.hiddenMask,self.__mask)

class LayerStack(QObject):
    signal = pyqtSignal()
    #updateLayer_signal = pyqtSignal()
    layNum_signal = pyqtSignal(int)
    def __init__(self,init=None,debug=False):
        super().__init__()
        self.__debug = debug
        self.__name = 'layer-1'
        self.selectedLayerIndex = 0
        self.layer = []
        self.layer_names = []
        self.mix_list = []
        if init is not None:
            self.flag = True
            self.Image = init
            self.__height, self.__width = self.Image.shape[0],self.Image.shape[1]
            self.color_num = (0,0,0)
            self.__opacity = 1.0
        else:
            self.flag = False
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            try:
                self.__width = eval(settings.value("width"))
                self.__height = eval(settings.value("height"))
                self.__opacity = eval(settings.value('alpha'))
            except TypeError:
                self.__width = settings.value("width")
                self.__height = settings.value("height")
                self.__opacity = settings.value('alpha')
            self.color = settings.value("color")
            self.Image = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
            self.color_num = self.__str_to_hex(self.color[1:])
            self.Image[:,:,0] = self.color_num[2]
            self.Image[:,:,1] = self.color_num[1]
            self.Image[:,:,2] = self.color_num[0]
            self.Image[:,:,3] = 255
        self.background = ops.drawBackground(self.__width,self.__height)
        self.pixNum = self.__width * self.__height
        tmp_layer = ImgObject(self.Image)
        tmp_layer.setPositionOnCanvas(((self.__width+1)//2,(self.__height+1)//2))
        tmp_layer.layerName = self.__name
        if self.__opacity == 0:
            self.Image = self.background
            tmp_layer.layerOpacity = 0.0
        self.tmp_img = self.Image
        self.layer_names.append(self.__name)
        self.layer.insert(0,tmp_layer)
        self.mix_list.insert(0,'Normal')
        self.__remix()
        self.selectedLayerIndex = 0
    
    def resetBackground(self,w,h):
        self.background = ops.drawBackground(w,h)
    
    def __str_to_hex(self,s):
        s = [int(c.upper(),16) for c in s]
        l = []
        for i in range(0,len(s),2):
            l.append(s[i]*16+s[i+1])
        if self.__debug:
            logger.debug('From '+str(s)+' to '+str(l))
        return l
    
    def currentImageObject(self):
        return self.layer[self.selectedLayerIndex]
    
    def setCurrentLayerOpacity(self,val):
        cur = self.currentImageObject()
        cur.setLayerOpacity(val)
        self.__remix()
    
    def getRectOfImage(self):
        img = self.currentImageObject()
        '''
        x1, y1 = img.getPositionOnCanvas()[0] - img.getCenterOfImage()[0], img.getPositionOnCanvas()[1] - img.getCenterOfImage()[1]
        x2, y2 = img.getPositionOnCanvas()[0] + img.getCenterOfImage()[0], img.getPositionOnCanvas()[1] + img.getCenterOfImage()[1]
        img.setImageRect((x1,y1,x2,y2))
        '''
        return img.getImageRect()
    
    def __getVisibleArea(self,img):
        tmp = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
        mask = np.zeros((self.__height,self.__width),dtype=np.uint8)
        if self.flag:
            tmp = self.Image
            self.flag = False
        '''
        cen_x,cen_y = (self.__width+1)//2,(self.__height+1)//2
        img_w,img_h = img.shape[1],img.shape[0]
        point_sx = max(cen_x - (img_w+1) // 2,0)
        point_sy = max(cen_y - (img_h+1) // 2,0)
        point_ix = -min(cen_x - (img_w+1) // 2,0)
        point_iy = -min(cen_y - (img_h+1) // 2,0)
        '''
        if self.__debug:
            logger.debug(str(img.getPositionOnCanvas())+', '+str(img.getCenterOfImage()))
        point_sx = max(self.__width - img.getCenterOfImage()[0] - (self.__width - img.getPositionOnCanvas()[0]), 0)
        point_sy = max(self.__height - img.getCenterOfImage()[1] - (self.__height - img.getPositionOnCanvas()[1]), 0)
        point_ix = -min(-img.getCenterOfImage()[0] + img.getPositionOnCanvas()[0], 0)
        point_iy = -min(-img.getCenterOfImage()[1] + img.getPositionOnCanvas()[1], 0)
        point_jx = min(self.__width - img.getPositionOnCanvas()[0] + img.getCenterOfImage()[0], img.width())
        point_jy = min(self.__height - img.getPositionOnCanvas()[1] + img.getCenterOfImage()[1], img.height())
        img_h = img.height() - point_iy
        img_w = img.width() - point_ix
        tmp[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width)),:3] = img.Image[point_iy:point_jy,point_ix:point_jx,:3]
        mask[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = 255
        tmp[:,:,3] = mask
        #tmp[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img.Image[point_iy:(point_iy+min(img_h,self.__height)),point_ix:(point_ix+min(img_w,self.__width))]
        #mask[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = 255
        x1, y1 = img.getPositionOnCanvas()[0] - img.getCenterOfImage()[0], img.getPositionOnCanvas()[1] - img.getCenterOfImage()[1]
        x2, y2 = img.getPositionOnCanvas()[0] + img.getCenterOfImage()[0], img.getPositionOnCanvas()[1] + img.getCenterOfImage()[1]
        img.imageRect = (x1,y1,x2,y2)
        if self.__debug:
            logger.debug('Visible area:'+str((point_sx,point_sy,min(img_w,self.__width),min(img_h,self.__height))))
        return tmp,mask
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name

    def addLayer(self,idx,name,img=None):
        if img is None:
            img = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
            img[:,:,0] = self.color_num[2]
            img[:,:,1] = self.color_num[1]
            img[:,:,2] = self.color_num[0]
            img[:,:,3] = 0
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
        tmp_layer.setPositionOnCanvas(((self.__width+1)//2,(self.__height+1)//2))
        tmp_layer.layerName = name
        self.layer_names.append(name)
        self.layer.insert(idx,tmp_layer)
        self.mix_list.insert(idx,'Normal')
        self.__remix()
        pass
    
    def newHiddenLayer(self):
        img = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        mask = np.zeros((self.__height,self.__width),dtype=np.uint8)
    
    def delLayer(self,idx):
        self.layer.pop(idx)
        self.layer_names.pop(idx)
        self.mix_list.pop(idx)
        self.__remix()
        pass
    
    def exchgLayer(self,fore,sup):
        if self.__debug:
            logger.debug('There are '+str(len(self.layer))+' layers, move from '+str(fore)+' to '+str(sup))
        item = self.layer.pop(fore)
        mix = self.mix_list.pop(fore)
        name = self.layer_names.pop(fore)
        self.layer.insert(sup,item)
        self.mix_list.insert(sup,mix)
        self.layer_names.insert(sup,name)
        self.__remix()
        self.signal.emit()
        pass
    
    def currentLayer(self):
        return self.tmp_img
    
    def updateCurrentLayerImage(self,image):
        self.tmp_img = self.layer[self.selectedLayerIndex].Image = image
        self.updateImg()
    
    def sltLayer(self,idx):
        if self.__debug:
            logger.debug('Current selected layer index:'+str(idx))
        self.tmp_img = self.layer[idx].Image
        self.selectedLayerIndex = idx
        self.layNum_signal.emit(idx)
        return idx
    
    def getSelectedLayerIndex(self):
        return self.selectedLayerIndex
    
    def currentIndex(self):
        return self.selectedLayerIndex
    
    def updateLayerImage(self,idx,image):
        self.tmp_img = self.layer[idx].Image = image
        self.updateImg()
    
    def cpyLayer(self,idx,name):
        if self.__debug:
            logger.debug('Copy '+str(idx)+' layer.')
        self.addLayer(idx,name,self.Image)
        pass
    
    def isPositionOutOfLayer(self,pos):
        if self.__debug:
            logger.debug('This position is '+
                         str('' if self.layer[self.selectedLayerIndex].isPosOutOfLayer(pos) else 'not')+
                         'out of layer.')
        return self.layer[self.selectedLayerIndex].isPosOutOfLayer(pos)
    
    def isOutOfLayer(self,ind,pos):
        return self.layer[ind].isPosOutOfLayer(pos)
    
    def getIndexOfClickPosition(self,pos):
        for i in range(len(self.layer)-1,0,-1):
            if not self.isOutOfLayer(i,pos):
                if self.__debug:
                    logger.debug('Click layer index is '+str(i)+'.')
                return i
            else:
                continue
        if self.__debug:
            logger.debug('Click layer is background.')
        return 0
    
    def autoSelectClickedLayer(self,pos):
        ind = self.getIndexOfClickPosition(pos)
        self.sltLayer(ind)
        return ind
    
    def getNum(self):
        return len(self.layer)
    
    def setMix(self,idx,mix):
        if self.__debug:
            logger.debug('Set '+str(idx)+' layer mixed mode is ' + mix +'.')
        self.mix_list[idx] = mix
        self.__remix()
        pass
    
    def __getMaskRes(self,img,mask):
        mask_inv = cv2.bitwise_not(mask)
        fg = cv2.bitwise_and(img,img,mask = mask)
        bg = cv2.bitwise_and(self.Image,self.Image,mask = mask_inv)
        return cv2.add(bg,fg)
    
    def __mix(self,img,idx):
        _img, mask = self.__getVisibleArea(img)
        if self.mix_list[idx] == "Normal":
            pass
            #_img, mask = self.__getVisibleArea(img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == "LinearLight":
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Overlay(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Overlay':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Overlay(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
            #return Mixed.Overlay(self.Image,self.__getVisibleArea(img.Image))
        elif self.mix_list[idx] == 'Screen':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Screen(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Multiply':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Multiply(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'SoftLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.SoftLight(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.HardLight(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearAdd':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Linear_add(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorBurn':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.ColorBurn(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearBurn':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LinearBurn(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorDodge':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.ColorDodge(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearDodge':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LinearDodge(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LighterColor':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LighterColor(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'VividLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.VividLight(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'PinLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.PinLight(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardMix':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.HardMix(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Difference':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Difference(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Exclusion':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Exclusion(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Subtract':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Subtract(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Divide':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Divide(self.Image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Hue':
            pass
            #_img, mask = self.__getVisibleArea(img)
            #_img = Mixed.Hue(self.Image,_img)
            #return self.__getMaskRes(_img,mask) #Mixed.Hue(self.Image,img.Image)
        else:
            #_img, mask = self.__getVisibleArea(img)
            pass
        return self.__getMaskRes(_img,mask),mask
        
    
    def __remix(self):
        self.Image,self.__mask = self.__getVisibleArea(self.layer[0])
        #self.Image = self.background
        #cv2.imwrite('./tmp_bottom.jpg',self.layer[0].Image)
        #print(len(self.layer))
        for i in range(1,len(self.layer)):
            tmp = self.Image
            self.Image,mask = self.__mix(self.layer[i],i)
            self.__mask = np.bitwise_or(self.__mask,mask)
            self.Image = cv2.addWeighted(self.Image,self.layer[i].opacity,tmp,1 - self.layer[i].opacity,0)
        #cv2.imwrite('error.jpg',self.Image)
        self.signal.emit()

    @property
    def mask(self):
        return self.__mask
    
    def updateImg(self):
        self.__remix()
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
        if self.__debug:
            logger.debug('Set image size:'+str((width,height)))
        r_w = width / self.__width
        r_h = height / self.__height
        for i in range(len(self.layer)):
            tmp_w,tmp_h = self.layer[i].width()*r_w,self.layer[i].height()*r_h
            self.layer[i].changeImg(cv2.resize(self.layer[i].Image,(int(tmp_w),int(tmp_h))))
        self.__width = width
        self.__height = height
        self.__remix()
    
    def resize(self,width,height):
        if self.__debug:
            logger.debug('Set canvas size:'+str((width,height)))
        self.__width = width
        self.__height = height
        self.__remix()

if __name__ == '__main__':
    img = cv2.imread('./samples/26.jpg')
    Img = ImgObject(img)
    Img.AddLayer(img)
    #Img.__remix()
    #cv2.imwrite('./tmp/mixed.jpg',Img.Image)