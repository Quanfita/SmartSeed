# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 10:39:53 2019

@author: Quanfita
"""
import numpy as np
import cv2
import math
from core import ops
from common.app import logger
from core.Mixed import Mixed
from PyQt5.QtCore import QSettings,pyqtSignal,QObject
from PyQt5.QtGui import QColor
from common import utils

class ImgObject(object):
    def __init__(self,img,name='Untitled',mask=None,icon=None,debug=False):
        self.__debug = debug
        self.__layerName = ''
        self._rect = None
        self.__opacity = 1.0
        if img.shape[2] == 3:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 1:
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
        self.image = img
        self.__name = name
        self.__realImage = img
        self._offset = (0,0)
        if icon is not None:
            self.__icon = ops.makeIcon(icon)
        else:
            self.__icon = ops.makeIcon(img)
        
        self.__mask = self.image[:,:,3]
        self.__width, self.__height = self.__realImage.shape[1],self.__realImage.shape[0]
        self.__pixNum = self.__width * self.__height
        self.__hasHiddenLayer = False
        self.__posOnCanvas = (-1,-1)
        self.setPositionOnCanvas((self.__width//2,self.__height//2))
    
    @property
    def mask(self):
        return self.__mask
    
    @mask.setter
    def mask(self, mask):
        self.__mask = self.image[:,:,3] = mask

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

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
            logger.debug('Set layer name:'+str(self.__layerName))
    
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
    def icon(self):
        return self.__icon
    
    @icon.setter
    def icon(self, icon):
        self.__icon = icon
    
    def getImage(self):
        return self.image
    
    def changeImg(self, img):
        if img.shape[2] == 3:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 1:
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
        self.image = img
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
        # if self.__debug:
        #     logger.debug('The center of image:'+str(((self.__width+1) //2,(self.__height+1) //2)))
        return ((self.__width+1) //2,(self.__height+1) //2)
    
    def getPositionOnCanvas(self):
        # if self.__debug:
        #     logger.debug('The position on canvas:'+str(self.__posOnCanvas))
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
            bg = cv2.bitwise_and(self.image,self.image,mask = mask_inv)
            self.image = cv2.add(bg,fg)
            self.__mask = cv2.bitwise_or(self.hiddenMask,self.__mask)

class LayerStackList(object):
    # in_signal = pyqtSignal(dict)
    # out_signal = pyqtSignal(dict)
    def __init__(self,controller,debug=False):
        # super().__init__()
        self.__debug = debug
        self.__controller = controller
        self.stack_list = []
        self._now_stack = None
        self._now_idx = 0
        # self.in_signal[dict].connect(self.doMsg)

    # def doMsg(self, content):
    #     if self.__debug:
    #         logger.debug('LayerList request message: '+str(content))
    #     if content['type'] == 'Open':
    #         self.newStack(content)
    #         self.out_signal.emit({'data':{'layer':self._now_stack},'type':'new','togo':'all'})
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'Import image':
    #         self._now_stack.addLayer(-1, content['data']['image_name'], content['data']['image'].image)
    #     elif content['type'] == 'exchange':
    #         self._now_stack.exchgLayer(content['data']['start'],content['data']['end'])
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'dellayer':
    #         self._now_stack.delLayer(content['data']['index'])
    #         content['data']['callback'](self._now_stack)
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'newlayer':
    #         self._now_stack.addLayer(content['data']['index'],content['data']['name'])
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'cpylayer':
    #         self._now_stack.cpyLayer(content['data']['index'],content['data']['name'])
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'sltlayer':
    #         self._now_stack.sltLayer(content['data']['index'])
    #         # content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'refresh':
    #         self._now_stack.shown_image = content['data']['image']
    #     elif content['type'] == 'getRect':
    #         self.sendMsg({"data":{'rect':self._now_stack.getRectOfImage()},'type':'getRect','togo':'canvas'})
    #     elif content['type'] == 'mix':
    #         self._now_stack.setMix(content['data']['index'],content['data']['mode'])
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'draw':
    #         if content['data']['mode'] in ['line','rect','circle']:
    #             self._now_stack.draw_2Pix(content['data']['mode'],content['data']['point_start'],content['data']['point_end'],content['data']['pen_color'],content['data']['thick'],content['data']['brush_color'],content['data']['center'])
    #         elif content['data']['mode'] == 'pencil':
    #             self._now_stack.draw_NPix(content['data']['point_list'],content['data']['thick'],content['data']['color'],content['data']['center'])
    #         elif content['data']['mode'] == 'fill':
    #             self._now_stack.fillColor(content['data']['position'],content['data']['color'],content['data']['center'])
    #         elif content['data']['mode'] == 'dropper':
    #             self._now_stack.dropColor(content['data']['position'],content['data']['callback'])
    #         elif content['data']['mode'] == 'vary':
    #             self._now_stack.varyImage(content['data']['start_position'],content['data']['end_position'],content['data']['enter'])
    #         elif content['data']['mode'] in ['brush','eraser']:
    #             self._now_stack.brushDraw(content['data']['position'],content['data']['brush'],content['data']['center'],content['data']['is_start'])
    #         elif content['data']['mode'] == 'zoom':
    #             self._now_stack.scale = content['data']['scale']
    #             self._now_stack.updateImg()
    #             content['data']['callback'](self._now_stack.shown_image)
    #         content['callback'](self._now_stack.shown_image)
    #     elif content['type'] == 'select_canvas':
    #         self._now_stack = self.stack_list[content['data']['index']]
    #         content['callback'](self._now_stack)
    #     if self.__debug:
    #         logger.debug('method: '+content['type']+','+str(self._now_stack.layer_names))
    #         # ops.imsave()

    # def sendMsg(self, content):
    #     self.out_signal.emit(content)
    
    @property
    def now_stack(self):
        return self._now_stack
    
    @now_stack.setter
    def now_stack(self, stack):
        self._now_stack = stack

    def newStack(self, content):
        if self.__debug:
            logger.debug('Create new stack')
        stack = LayerStack(content,debug = self.__debug)
        self.stack_list.append(stack)
        self._now_stack = stack
        # self._now_stack.out_signal[dict].connect(self.sendMsg)
        self._now_idx = len(self.stack_list) - 1

    def addStack(self, stack):
        if self.__debug:
            logger.debug('Add stack: '+str(stack))
        self.stack_list.append(stack)
        self._now_stack = stack
        self._now_idx = len(self.stack_list) - 1

    def removeStackByIndex(self, idx):
        if self.__debug:
            logger.debug('Remove stack by index: '+str(idx)+', '+str(self.stack_list[idx]))
        self.stack_list.pop(idx)
        if len(self.stack_list) > idx:
            self._now_stack = self.stack_list[idx]
            self._now_idx = idx
        elif len(self.stack_list) == 0:
            self._now_stack = None
            self._now_idx = 0
        else:
            self._now_stack = self.stack_list[idx - 1]
            self._now_idx = idx - 1

    def removeStack(self, stack):
        idx = self.stack.index(stack)
        if self.__debug:
            logger.debug('Remove stack: '+str(self.stack_list[idx]))
        self.stack.remove(stack)
        if len(self.stack_list) > idx:
            self._now_stack = self.stack_list[idx]
            self._now_idx = idx
        elif len(self.stack_list) == 0:
            self._now_stack = None
            self._now_idx = 0
        else:
            self._now_stack = self.stack_list[idx - 1]
            self._now_idx = idx - 1

    def insertStack(self, idx, stack):
        if self.__debug:
            logger.debug('Insert stack: '+str(idx)+', '+str(stack))
        self.stack_list.insert(idx, stack)
        self._now_stack = stack
        self._now_idx = idx

    def isLast(self):
        return self.stack_list[-1] == self._now_stack

    def isEmpty(self):
        return len(self.stack_list) == 0

    def currentStackIndex(self):
        return self._now_idx

    def currentStack(self):
        return self._now_stack

    def selectStack(self, idx):
        if self.__debug:
            logger.debug('Select stack: '+str(idx)+', '+str(self.stack_list[idx]))
        self._now_stack = self.stack_list[idx]
        self._now_idx = idx

class LayerStack(object):
    # signal = pyqtSignal()
    # in_signal = pyqtSignal(dict)
    # out_signal = pyqtSignal(dict)
    # updateLayer_signal = pyqtSignal()
    # layNum_signal = pyqtSignal(int)
    def __init__(self, content, debug=False):
        # super().__init__()
        self.__debug = debug
        self.__name = 'layer-1'
        self.__currentIndex = 0
        self.layer = []
        self.layer_names = []
        self.mix_list = []
        self.__scale = 100.0
        # if init is not None:
        #     self.flag = True
        #     self.image = init
        #     self.__height, self.__width = self.image.shape[0],self.image.shape[1]
        #     self.color_num = (0,0,0)
        #     self.__opacity = 1.0
        # else:
        #     self.flag = False
        #     settings = utils.readTempIni()
        #     self.__width = int(settings["width"])
        #     self.__height = int(settings["height"])
        #     self.__opacity = int(settings['alpha'])
        #     self.color = settings["color"]
        #     self.image = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
        #     self.color_num = self.__str_to_hex(self.color[1:])
        #     self.image[:,:,0] = self.color_num[2]
        #     self.image[:,:,1] = self.color_num[1]
        #     self.image[:,:,2] = self.color_num[0]
        #     self.image[:,:,3] = 255
        # self.background = ops.drawBackground(self.__width,self.__height)
        # self.pixNum = self.__width * self.__height
        # tmp_layer = ImgObject(self.image)
        # tmp_layer.setPositionOnCanvas(((self.__width+1)//2,(self.__height+1)//2))
        # tmp_layer.layerName = self.__name
        # if self.__opacity == 0:
        #     self.image = self.background
        #     tmp_layer.layerOpacity = 0.0
        # self.tmp_img = self.image
        # self.layer_names.append(self.__name)
        # self.layer.insert(0,tmp_layer)
        # self.mix_list.insert(0,'Normal')
        # self.__remix()
        # self.__currentIndex = 0
        self.init(content)
    
    def length(self):
        return len(self.layer)

    def init(self, content):
        self.image = content['data']['image'].image
        self.tmp_img = self.image
        self.shown_image = np.copy(self.image)
        self.__width,self.__height = content['data']['size']
        self.__name = content['data']['image_name']
        self.background = ops.drawBackground(self.__width,self.__height)
        self.pixNum = self.__width * self.__height
        self.color_num = (0,0,0)
        self.__opacity = 1.0
        self.layer.insert(0,content['data']['image'])
        self.layer_names.append(self.__name)
        self.mix_list.insert(0,'Normal')
        self.__remix()
        self.__currentIndex = 0

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, scale):
        self.__scale = scale

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
        return self.layer[self.__currentIndex]
    
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
        return img.imageRect
    
    def __str__(self):
        return self.__name

    def __getVisibleArea(self,img):
        tmp = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
        mask = np.zeros((self.__height,self.__width),dtype=np.uint8)
        if self.__debug:
            logger.debug('Position of Canvas: '+str(img.getPositionOnCanvas())+', Center of image: '+str(img.getCenterOfImage()))
        point_sx = max(self.__width - img.getCenterOfImage()[0] - (self.__width - img.getPositionOnCanvas()[0]), 0)
        point_sy = max(self.__height - img.getCenterOfImage()[1] - (self.__height - img.getPositionOnCanvas()[1]), 0)
        point_ix = -min(-img.getCenterOfImage()[0] + img.getPositionOnCanvas()[0], 0)
        point_iy = -min(-img.getCenterOfImage()[1] + img.getPositionOnCanvas()[1], 0)
        point_jx = min(self.__width - img.getPositionOnCanvas()[0] + img.getCenterOfImage()[0], img.width())
        point_jy = min(self.__height - img.getPositionOnCanvas()[1] + img.getCenterOfImage()[1], img.height())
        img_h = img.height() - point_iy
        img_w = img.width() - point_ix
        tmp[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width)),:3] = img.image[point_iy:point_jy,point_ix:point_jx,:3]
        mask[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img.image[point_iy:point_jy,point_ix:point_jx,3]
        tmp[:,:,3] = mask
        #tmp[point_sy:(point_sy+min(img_h, self.__height)),point_sx:(point_sx+min(img_w,self.__width))] = img.image[point_iy:(point_iy+min(img_h,self.__height)),point_ix:(point_ix+min(img_w,self.__width))]
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
        if idx == -1:
            idx == len(self.layer)
        if img is None:
            img = np.zeros((self.__height,self.__width,4),dtype=np.uint8)
            img[:,:,0] = self.color_num[2]
            img[:,:,1] = self.color_num[1]
            img[:,:,2] = self.color_num[0]
            img[:,:,3] = 0
            tmp_layer = ImgObject(img, name, icon=self.background, debug=self.__debug)
        else:
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
            tmp_layer = img #ImgObject(img, name, debug=self.__debug)
        tmp_layer.setPositionOnCanvas(((self.__width+1)//2,(self.__height+1)//2))
        tmp_layer.layerName = name
        self.layer_names.append(name)
        self.layer.insert(idx,tmp_layer)
        self.mix_list.insert(idx,'Normal')
        self.__remix()
        # self.out_signal.emit({'data':{'layer':self,'index':idx},'type':'add','togo':'all'})
    
    def newHiddenLayer(self):
        img = np.zeros((self.__height,self.__width,3),dtype=np.uint8)
        mask = np.zeros((self.__height,self.__width),dtype=np.uint8)
    
    def delLayer(self,idx):
        self.layer.pop(idx)
        self.layer_names.pop(idx)
        self.mix_list.pop(idx)
        self.__remix()
        # self.out_signal.emit({'data':{'layer':self,'index':idx},'type':'del','togo':'canvas'})
    
    def exchgLayer(self,fore,sup):
        if self.__debug:
            logger.debug('There are '+str(len(self.layer))+' layers, move from '+str(fore)+' to '+str(sup))
        item = self.layer.pop(fore)
        mix = self.mix_list.pop(fore)
        name = self.layer_names.pop(fore)
        self.layer.insert(sup,item)
        self.mix_list.insert(sup,mix)
        self.layer_names.insert(sup,name)
        self.__currentIndex = sup
        self.__remix()
        # self.signal.emit()
        # self.out_signal.emit({'data':{'layer':self},'type':'exchange','togo':'canvas'})
    
    def currentLayerImage(self):
        return self.tmp_img
    
    def updateCurrentLayerImage(self,image):
        self.tmp_img = self.layer[self.__currentIndex].Image = image
        self.updateImg()
    
    def sltLayer(self,idx):
        if self.__debug:
            logger.debug('Current selected layer index:'+str(idx))
        self.tmp_img = self.layer[idx].image
        self.__currentIndex = idx
        # self.layNum_signal.emit(idx)
        # self.out_signal.emit({'data':{'layer':self},'type':'slt','togo':'canvas'})
        return idx
    
    # def getSelectedLayerIndex(self):
    #     return self.__currentIndex
    
    @property
    def currentIndex(self):
        return self.__currentIndex
    
    @currentIndex.setter
    def currentIndex(self, index):
        self.__currentIndex = index
    
    def updateLayerImage(self,idx,image):
        self.tmp_img = self.layer[idx].image = image
        self.updateImg()
    
    def cpyLayer(self,idx,name):
        if self.__debug:
            logger.debug('Copy '+str(idx)+' layer.')
        self.addLayer(idx,name,np.copy(self.layer[idx].image))
        # self.out_signal.emit({'data':{'layer':self},'type':'slt','togo':'canvas'})
        pass
    
    def isPositionOutOfLayer(self,pos):
        if self.__debug:
            logger.debug('This position is '+
                         str('' if self.layer[self.__currentIndex].isPosOutOfLayer(pos) else 'not')+
                         'out of layer.')
        return self.layer[self.__currentIndex].isPosOutOfLayer(pos)
    
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
        self.updateImg()
    
    def __getMaskRes(self,img,mask):
        mask_inv = cv2.bitwise_not(mask)
        fg = cv2.bitwise_and(img,img,mask = mask)
        bg = cv2.bitwise_and(self.image,self.image,mask = mask_inv)
        # ops.imsave(fg,'./tmp/error_fg.png')
        # ops.imsave(fg,'./tmp/error_bg.png')
        return cv2.add(bg,fg)
    
    def __mix(self,img,idx):
        _img, mask = self.__getVisibleArea(img)
        if self.mix_list[idx] == "Normal":
            pass
            # _img, mask = self.__getVisibleArea(img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == "LinearLight":
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Overlay(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Overlay':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Overlay(self.image,_img)
            #return self.__getMaskRes(_img,mask)
            #return Mixed.Overlay(self.image,self.__getVisibleArea(img.image))
        elif self.mix_list[idx] == 'Screen':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Screen(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Multiply':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Multiply(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'SoftLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.SoftLight(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.HardLight(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearAdd':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Linear_add(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorBurn':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.ColorBurn(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearBurn':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LinearBurn(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'ColorDodge':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.ColorDodge(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LinearDodge':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LinearDodge(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'LighterColor':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.LighterColor(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'VividLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.VividLight(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'PinLight':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.PinLight(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'HardMix':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.HardMix(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Difference':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Difference(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Exclusion':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Exclusion(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Subtract':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Subtract(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Divide':
            #_img, mask = self.__getVisibleArea(img)
            _img = Mixed.Divide(self.image,_img)
            #return self.__getMaskRes(_img,mask)
        elif self.mix_list[idx] == 'Hue':
            pass
            #_img, mask = self.__getVisibleArea(img)
            #_img = Mixed.Hue(self.image,_img)
            #return self.__getMaskRes(_img,mask) #Mixed.Hue(self.image,img.image)
        else:
            #_img, mask = self.__getVisibleArea(img)
            pass
        return self.__getMaskRes(_img,mask),mask
        
    
    def __remix(self):
        self.image,self.__mask = self.__getVisibleArea(self.layer[-1])
        # self.image = self.background
        #cv2.imwrite('./tmp_bottom.jpg',self.layer[0].Image)
        #print(len(self.layer))
        for i in range(len(self.layer)-1,-1,-1):
            tmp = self.image
            self.image,mask = self.__mix(self.layer[i],i)
            self.__mask = np.bitwise_or(self.__mask,mask)
            # self.image = self.image[:,:,:3]*self.__mask+tmp*cv2.bitwise_not(mask)
            self.image = cv2.addWeighted(self.image,self.layer[i].opacity,tmp,1 - self.layer[i].opacity,0)
        # self.image = cv2.addWeighted(self.image,self.layer[-1].opacity,self.background,1 - self.layer[-1].opacity,0)
        
        self.showImage()

    def showImage(self):
        image = cv2.resize(self.image,
                    (0,0),fx=self.scale/100, fy=self.scale/100,
                    interpolation=cv2.INTER_NEAREST)
        mask = cv2.resize(self.__mask,
                    (0,0),fx=self.scale/100, fy=self.scale/100,
                    interpolation=cv2.INTER_NEAREST)
        self.resetBackground(image.shape[1],image.shape[0])
        mask_inv = cv2.bitwise_not(mask)
        fg = cv2.bitwise_and(image,image,mask = mask)
        # print(image.shape,mask.shape,self.background.shape,mask_inv.shape,type(self.background),type(mask_inv))
        bg = cv2.bitwise_and(self.background,self.background,mask = mask_inv)
        self.shown_image = cv2.add(fg,bg)
        cv2.imwrite('error.jpg',self.image)
        cv2.imwrite('error_show.jpg',self.shown_image)
        # print(self.image.shape,self.__mask.shape,self.tmp_img.shape,self.shown_image.shape)
        # self.signal.emit()

    @property
    def mask(self):
        return self.__mask
    
    def updateImg(self):
        self.__remix()
        # self.signal.emit()
    
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

    def draw_2Pix(self,mode,start,end,pencolor,thick,brush,center,callback=None):
        #print(mode,start,end,pencolor,thick,brush)
        imgObj = self.currentImageObject()
        start = ops.cvtCanPosAndLayerPos(start,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        end = ops.cvtCanPosAndLayerPos(end,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        #print(start,end)
        if mode == 'line':
            cv2.line(imgObj.image,start,end,pencolor,thick,cv2.LINE_AA)
        elif mode == 'rect':
            if brush[-1] != 0:
                cv2.rectangle(imgObj.image,start,end,brush,-1,cv2.LINE_AA)
            cv2.rectangle(imgObj.image,start,end,pencolor,thick,cv2.LINE_AA)
        elif mode == 'circle':
            if brush[-1] != 0:
                cv2.ellipse(imgObj.image,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,brush,-1,cv2.LINE_AA)
            cv2.ellipse(imgObj.image,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,pencolor,thick,cv2.LINE_AA)
        self.updateImg()
        if callback is not None:
            callback(self.shown_image)

    def draw_NPix(self,pos_list,thick,color,center,callback=None):
        imgObj = self.currentImageObject()
        if pos_list:
            tmp = ops.cvtCanPosAndLayerPos(pos_list[0],(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
            # print(pos_list)
            for pos in pos_list:
                pos = ops.cvtCanPosAndLayerPos(pos,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
                cv2.line(imgObj.image,tmp,pos,color,thick,cv2.LINE_AA)
                tmp = pos
                #cv2.circle(self.layers.tmp_img,pos,thick,color[0],-1)
        self.updateImg()
        if callback is not None:
            callback(self.shown_image)

    def dropColor(self,pos,callback):
        #pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        # if self.tmp_img.mask[pos[1],pos[0]] == 0:
        #     return
        [b,g,r,a] = self.shown_image[pos[1],pos[0]]
        callback(QColor(r,g,b,a))
        
    def fillColor(self,pos,color,center,r=50,callback=None):
        #print(pos)
        # logger.debug('Position:'+str(pos)+', color:'+str(color)+', r:'+str(r))
        imgObj = self.currentImageObject()
        (x,y) = ops.cvtCanPosAndLayerPos((pos[0],pos[1]),(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        [b,g,r,_] = imgObj.image[y,x]
        h,w = imgObj.image.shape[:2]
        mask=np.zeros([h+2,w+2],np.uint8)
        tmp = cv2.cvtColor(imgObj.image,cv2.COLOR_BGRA2BGR)
        cv2.floodFill(tmp,mask,(x,y),color,(50,50,50),(50,50,50),cv2.FLOODFILL_FIXED_RANGE)
        tmp = cv2.cvtColor(tmp,cv2.COLOR_BGR2BGRA)
        tmp[:,:,3] = imgObj.image[:,:,3]
        imgObj.image = tmp
        self.updateImg()
        callback(self.shown_image)

    def varyImage(self,start,end,enter,callback=None):
        last = self.currentImageObject().getPositionOnCanvas()
        self.currentImageObject().setPositionOnCanvasByDistance((end[0] - start[0], end[1] - start[1]))
        self.updateImg()
        if not enter:
            self.currentImageObject().setPositionOnCanvas(last)
        else:
            self.currentImageObject().offset = (end[0] - start[0], end[1] - start[1])
        # self.out_signal.emit({"data":{'rect':self.getRectOfImage()},'type':'getRect','togo':'canvas'})
        # self.updateImg()
        if callback is not None:
            callback(self.shown_image)

    def brushDraw(self,pos,brush,center,is_start,callback=None):
        def draw(img,position,brush):
            if img.shape[2] == 3:
                img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
            elif len(img.shape) == 2:
                img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
            r = (brush.size+1)//2
            img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:] = brush.veins + cv2.bitwise_and(img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:],img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:],mask = cv2.bitwise_not(brush.veins_mask))
            # tmp_shape = cv2.resize(brush.veins,(imageROI.shape[1],imageROI.shape[0]))
            # gray = cv2.cvtColor(tmp_shape,cv2.COLOR_RGBA2GRAY)
            # ret,mask = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
            # mask_inv = cv2.bitwise_not(mask)
            # img1_bg = cv2.bitwise_and(imageROI,imageROI,mask = mask_inv)
            # img2_fg = cv2.bitwise_and(tmp_shape,tmp_shape,mask = mask)
            # img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:] = cv2.add(img1_bg,img2_fg)
            return img
        imgObj = self.currentImageObject()
        pos = ops.cvtCanPosAndLayerPos(pos,(0,0),imgObj.getCenterOfImage(),center)
        if not is_start:
            point_list = self._get_points(pos)
            for point in point_list:
                imgObj.image = draw(imgObj.image, point, brush)
        self.updateImg()
        self.tmp_pos = pos
        if callback is not None:
            callback(self.shown_image)

    def _get_points(self, pos):
        """ Get all points between last_point ~ now_point. """
        points = [self.tmp_pos]
        len_x = pos[0] - self.tmp_pos[0]
        len_y = pos[1] - self.tmp_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        if length == 0: return points
        step_x = len_x / length
        step_y = len_y / length
        for _ in range(int(length)):
            points.append((points[-1][0] + step_x, points[-1][1] + step_y))
        points = map(lambda x:(int(0.5+x[0]), int(0.5+x[1])), points)
        # return light-weight, uniq list
        return list(set(points))

if __name__ == '__main__':
    img = cv2.imread('./samples/26.jpg')
    Img = ImgObject(img)
    Img.AddLayer(img)
    #Img.__remix()
    #cv2.imwrite('./tmp/mixed.jpg',Img.Image)