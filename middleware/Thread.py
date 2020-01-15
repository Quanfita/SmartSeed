# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:15:51 2019

@author: Quanfita
"""

import cv2
import time
from core.Filter.Filter import Filter
# #from Op.Paint.Painters import Painter
# from Op.Special.Sit2Anime import Sit2Anime
# from Op.Image.AutoAdjust import ACE,AWB,ACA
# from Op.Special.Ink import Ink
# from Op.Special import Pencil
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor
# from Op import Sharp
# from Op import Blur
from core import ops
from common.app import logger
from setting import TABLE_PATH
import numpy as np
 
class ProThread(QThread):
    """
    This is a thread that responsible for image processing.
    dict:{img:the image to process,method:the type of process,other:other arguements}
    """
    in_signal = pyqtSignal(dict)
    out_signal = pyqtSignal(dict)
    def __init__(self, debug=False, parent=None):
        super(ProThread, self).__init__()
        self.__debug = debug
        self.tmp_img = None
        self._p_queue = []
        self.task_dict = {
                        'filter': self.doFilter,
                        # 'AWB': AWB,
                        # 'ACE': ACE().zmIceColor,
                        # 'ACA': ACA,
                        # 'Anime': Sit2Anime('./tables').DoProcess,
                        # 'Painter': "",
                        # 'Ink': Ink().ink,
                        # "USM": Sharp.USM,
                        # "EdgeSharp": Sharp.EdgeSharp,
                        # "SmartSharp": Sharp.SmartSharp,
                    }
        self.content = ''
        self.target = ''
        self.in_signal[dict].connect(self.addTask)
 
    def __del__(self):
        self.wait()

    def addTask(self, content):
        if self.__debug:
            logger.debug('Process thread request message: '+str(content))
        self._p_queue.append(content)
    
    def changeMode(self, img, target, content=None):
        self.tmp_img = img
        self.target = target
        self.content = content
        # print(self.target)
    
    def run(self):
        #  do something
        content = self._p_queue.pop()
        self.target = content['type']
        self.tmp_img = content['data']['image']
        self.layer_stack = content['data']['layer_stack']
        if self.target == 'draw':
            if content['data']['mode'] in ['line','rect','circle']:
                self.draw_2Pix(content['data']['mode'],content['data']['point_start'],content['data']['point_end'],content['data']['pen_color'],content['data']['thick'],content['data']['brush_color'],content['data']['center'])
            elif content['data']['mode'] == 'pencil':
                self.draw_NPix(content['data']['point_list'],content['data']['thick'],content['data']['color'],content['data']['center'])
            elif content['data']['mode'] == 'fill':
                self.fillColor(content['data']['position'],content['data']['color'],content['data']['center'])
            elif content['data']['mode'] == 'dropper':
                self.dropColor(content['data']['position'],content['data']['callback'])
            elif content['data']['mode'] == 'vary':
                self.varyImage(content['data']['start_position'],content['data']['end_position'],content['data']['enter'])
        else:
            self.content = content['data']['filter']
            self.task_dict[self.target]()
        if self.__debug:
        	t = time.time()
        	logger.debug('Start do '+ self.target+'.')

        # if self.target == 'filter':
        #     self.doFilter()
        # elif self.target == 'AWB':
        #     self.AWB()
        # elif self.target == 'ACE':
        #     self.ACE()
        # elif self.target == 'ACA':
        #     self.ACA()
        # elif self.target == 'Anime':
        #     self.Anime()
        # elif self.target == 'Painter':
        #     self.Paint()
        # elif self.target == 'Ink':
        #     self.Ink()
        # elif self.target == 'Pencil':
        #     self.Pencil()
        # elif self.target == 'Blur':
        #     self.blur()
        # elif self.target == 'BlurMore':
        #     self.BlurMore()
        # elif self.target == 'GaussianBlur':
        #     self.GaussianBlur()
        # elif self.target == 'MotionBlur':
        #     self.MotionBlur()
        # elif self.target == 'RadialBlur':
        #     self.RadialBlur()
        # elif self.target == 'SmartBlur':
        #     self.SmartBlur()
        # elif self.target == 'USM':
        #     self.USM()
        # elif self.target == 'EdgeSharp':
        #     self.EdgeSharp()
        # elif self.target == 'SmartSharp':
        #     self.SmartSharp()
        # else:
        #     return
        if self.__debug:
        	logger.debug('Process time:'+str(time.time() - t)+'.')
        self.out_signal.emit({'data':{'img':self.tmp_img},'type':'refresh','togo':None})
        self.layer_stack.updateImg()
        content['callback'](self.layer_stack.image)
    
    def doFilter(self):
        _dict = {
            'Portrait':'lookup-table_1.jpg',
            'Smooth':'lookup-table_2.jpg',
            'Morning':'lookup-table_3.jpg',
            'Pop':'lookup-table_4.jpg',
            'Accentuate':'lookup-table_5.jpg',
            'Art Style':'lookup-table_6.jpg',
            'Black & White':'lookup-table_B&W.jpg',
            'HDR':'lookup-table_hdr.jpg',
            'Modern':'lookup-table_li.jpg',
            'Old':'lookup-table_old.jpg',
            'Yellow':'lookup-table-yellow.png',
        }
        # print(TABLE_PATH+'/lookup-table.png')
        ori = cv2.imread(TABLE_PATH+'/lookup-table.png')
        new = cv2.imread(TABLE_PATH+'/'+_dict[self.content])
        self.tmp_img.image = Filter().myFilter(ori,new,self.tmp_img.image)
        return
    
    def draw_2Pix(self,mode,start,end,pencolor,thick,brush,center):
        #print(mode,start,end,pencolor,thick,brush)
        imgObj = self.tmp_img
        start = ops.cvtCanPosAndLayerPos(start,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        end = ops.cvtCanPosAndLayerPos(end,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        #print(start,end)
        if mode == 'line':
            cv2.line(imgObj.image,start,end,pencolor,thick)
        elif mode == 'rect':
            if brush[-1] != 0:
                cv2.rectangle(imgObj.image,start,end,brush,-1)
            cv2.rectangle(imgObj.image,start,end,pencolor,thick)
        elif mode == 'circle':
            if brush[-1] != 0:
                cv2.ellipse(imgObj.image,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,brush,-1)
            cv2.ellipse(imgObj.image,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,pencolor,thick)

    def draw_NPix(self,pos_list,thick,color,center):
        imgObj = self.tmp_img
        if pos_list:
            tmp = ops.cvtCanPosAndLayerPos(pos_list[0],(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
            # print(pos_list)
            for pos in pos_list:
                pos = ops.cvtCanPosAndLayerPos(pos,(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
                cv2.line(imgObj.image,tmp,pos,color[0],thick)
                tmp = pos
                #cv2.circle(self.layers.tmp_img,pos,thick,color[0],-1)

    def dropColor(self,pos,callback):
        #pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        # if self.tmp_img.mask[pos[1],pos[0]] == 0:
        #     return
        [b,g,r,a] = self.tmp_img.image[pos[1],pos[0]]
        callback(QColor(r,g,b,a))
        
    def fillColor(self,pos,color,center,r=50):
        #print(pos)
        logger.debug('Position:'+str(pos)+', color:'+str(color)+', r:'+str(r))
        imgObj = self.tmp_img
        (x,y) = ops.cvtCanPosAndLayerPos((pos[0],pos[1]),(0,0),imgObj.getCenterOfImage(),center,imgObj.offset)
        [b,g,r,_] = imgObj.image[y,x]
        h,w = imgObj.image.shape[:2]
        mask=np.zeros([h+2,w+2],np.uint8)
        tmp = cv2.cvtColor(imgObj.image,cv2.COLOR_BGRA2BGR)
        cv2.floodFill(tmp,mask,(x,y),color,(50,50,50),(50,50,50),cv2.FLOODFILL_FIXED_RANGE)
        tmp = cv2.cvtColor(tmp,cv2.COLOR_BGR2BGRA)
        tmp[:,:,3] = imgObj.image[:,:,3]
        imgObj.image = tmp

    # def zoom(self,isplus):
    #     if isplus:
    #         if int(self.scale) >= 100:
    #             self.scale = min(self.scale + 100,1000)
    #         else:
    #             self.scale = min(self.scale*2,100)
    #     else:
    #         if int(self.scale) >= 200:
    #             self.scale -= 100
    #         elif int(self.scale) > 100:
    #             self.scale = 100.0
    #         else:
    #             self.scale -= 0.5*self.scale
    #     self.draw.setScale(self.scale/100.0)
    #     self.scroll.setContentScale(self.scale/100.0)
    #     self.imgOperate()
    
    def varyImage(self,start,end,enter):
        last = self.tmp_img.getPositionOnCanvas()
        self.tmp_img.setPositionOnCanvasByDistance((end[0] - start[0], end[1] - start[1]))
        self.layer_stack.updateImg()
        if not enter:
            self.tmp_img.setPositionOnCanvas(last)
        else:
            self.tmp_img.offset = (end[0] - start[0], end[1] - start[1])
        self.out_signal.emit({"data":{'rect':self.layer_stack.getRectOfImage()},'type':'getRect','togo':'canvas'})

    # def AWB(self):
    #     self.tmp_img = AWB(self.tmp_img)
    #     return
    
    # def ACE(self):
    #     self.tmp_img = ACE().zmIceColor(self.tmp_img)
    #     return
    
    # def ACA(self):
    #     self.tmp_img = ACA(self.tmp_img)
    
    # def Anime(self):
    #     #sky = cv2.imread(self.content)
    #     self.tmp_img = Sit2Anime('./tables').DoProcess(self.tmp_img)
    #     return
    
    # def Paint(self):
    #     #self.tmp_img = Painter(self.tmp_img))
    #     return
    
    # def Ink(self):
    #     self.tmp_img = Ink().ink(self.tmp_img)
    #     return
    
    # def Pencil(self):
    #     pencil = cv2.imread('./tables/pencil.jpg')
    #     self.tmp_img = Pencil.pencil_drawing(self.tmp_img,pencil)
    #     return
    
    # def USM(self):
    #     self.tmp_img = Sharp.USM(self.tmp_img)
    #     return
    
    # def EdgeSharp(self):
    #     self.tmp_img = Sharp.EdgeSharp(self.tmp_img)
    #     return
    
    # def SmartSharp(self):
    #     self.tmp_img = Sharp.SmartSharp(self.tmp_img)
    #     return
    
    # def blur(self,ksize=5):
    #     self.tmp_img = Blur.Blur(self.tmp_img,ksize)
    #     return
    
    # def GaussianBlur(self,ksize=5,sigma=15):
    #     self.tmp_img = Blur.GaussianBlur(self.tmp_img,ksize,sigma)
    #     return
    
    # def MotionBlur(self,length=20,angle=40):
    #     self.tmp_img = Blur.MotionBlur(self.tmp_img,length,angle)
    #     return
    
    # def BlurMore(self,ksize=5):
    #     self.tmp_img = Blur.BlurMore(self.tmp_img,ksize)
    #     return
    
    # def RadialBlur(self,num=20):
    #     self.tmp_img = Blur.RadialBlur(self.tmp_img,num)
    #     return
    
    # def SmartBlur(self,color=100,space=5):
    #     self.tmp_img = Blur.SmartBlur(self.tmp_img,color,space)
    #     return