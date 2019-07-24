# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:15:51 2019

@author: Quanfita
"""

import cv2
import logger
import time
from Op.Filter import Filter
#from Op.Paint.Painters import Painter
from Op.Special.Sit2Anime import Sit2Anime
from Op.Image.AutoAdjust import ACE,AWB,ACA
from Op.Special.Ink import Ink
from Op.Special import Pencil
from PyQt5.QtCore import QThread, pyqtSignal
from Op import Sharp
from Op import Blur
 
class ProThread(QThread):
    """
    This is a thread that responsible for image processing.
    dict:{img:the image to process,method:the type of process,other:other arguements}
    """
    pro_signal = pyqtSignal(dict)
    def __init__(self, debug=False, parent=None):
        super(ProThread, self).__init__()
        self.debug = debug
        self.tmp_img = None
        self.content = ''
        self.target = ''
 
    def __del__(self):
        self.wait()
    
    def changeMode(self, img, target, content=None):
        self.tmp_img = img
        self.target = target
        self.content = content
        print(self.target)
    
    def run(self):
        #  do something
        if self.debug:
        	t = time.time()
        	logger.debug('Start do '+ self.target+'.')
        if self.target == 'filter':
            self.doFilter()
        elif self.target == 'AWB':
            self.AWB()
        elif self.target == 'ACE':
            self.ACE()
        elif self.target == 'ACA':
            self.ACA()
        elif self.target == 'Anime':
            self.Anime()
        elif self.target == 'Painter':
            self.Paint()
        elif self.target == 'Ink':
            self.Ink()
        elif self.target == 'Pencil':
            self.Pencil()
        elif self.target == 'Blur':
            self.blur()
        elif self.target == 'BlurMore':
            self.BlurMore()
        elif self.target == 'GaussianBlur':
            self.GaussianBlur()
        elif self.target == 'MotionBlur':
            self.MotionBlur()
        elif self.target == 'RadialBlur':
            self.RadialBlur()
        elif self.target == 'SmartBlur':
            self.SmartBlur()
        elif self.target == 'USM':
            self.USM()
        elif self.target == 'EdgeSharp':
            self.EdgeSharp()
        elif self.target == 'SmartSharp':
            self.SmartSharp()
        else:
            return
        if self.debug:
        	logger.debug('Process time:'+str(time.time() - t)+'.')
        self.pro_signal.emit({'img':self.tmp_img})
    
    def doFilter(self):
        ori = cv2.imread('./tables/lookup-table.png')
        new = cv2.imread('./tables/'+self.content)
        self.tmp_img = Filter().myFilter(ori,new,self.tmp_img)
        return
    
    def AWB(self):
        self.tmp_img = AWB(self.tmp_img)
        return
    
    def ACE(self):
        self.tmp_img = ACE().zmIceColor(self.tmp_img)
        return
    
    def ACA(self):
        self.tmp_img = ACA(self.tmp_img)
    
    def Anime(self):
        #sky = cv2.imread(self.content)
        self.tmp_img = Sit2Anime('./tables').DoProcess(self.tmp_img)
        return
    
    def Paint(self):
        #self.tmp_img = Painter(self.tmp_img))
        return
    
    def Ink(self):
        self.tmp_img = Ink().ink(self.tmp_img)
        return
    
    def Pencil(self):
        pencil = cv2.imread('./tables/pencil.jpg')
        self.tmp_img = Pencil.pencil_drawing(self.tmp_img,pencil)
        return
    
    def USM(self):
        self.tmp_img = Sharp.USM(self.tmp_img)
        return
    
    def EdgeSharp(self):
        self.tmp_img = Sharp.EdgeSharp(self.tmp_img)
        return
    
    def SmartSharp(self):
        self.tmp_img = Sharp.SmartSharp(self.tmp_img)
        return
    
    def blur(self,ksize=5):
        self.tmp_img = Blur.Blur(self.tmp_img,ksize)
        return
    
    def GaussianBlur(self,ksize=5,sigma=15):
        self.tmp_img = Blur.GaussianBlur(self.tmp_img,ksize,sigma)
        return
    
    def MotionBlur(self,length=20,angle=40):
        self.tmp_img = Blur.MotionBlur(self.tmp_img,length,angle)
        return
    
    def BlurMore(self,ksize=5):
        self.tmp_img = Blur.BlurMore(self.tmp_img,ksize)
        return
    
    def RadialBlur(self,num=20):
        self.tmp_img = Blur.RadialBlur(self.tmp_img,num)
        return
    
    def SmartBlur(self,color=100,space=5):
        self.tmp_img = Blur.SmartBlur(self.tmp_img,color,space)
        return