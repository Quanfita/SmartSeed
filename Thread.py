# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:15:51 2019

@author: Quanfita
"""

import cv2
from Op.Filter import Filter
#from Op.Paint.Painters import Painter
from Op.Special.Sit2Anime import Sit2Anime
from Op.Image.AutoAdjust import ACE,AWB,ACA
from Op.Special.Ink import Ink
from Op.Special import Pencil
from PyQt5.QtCore import QThread
from Op import Sharp
from Op import Blur
 
class ProThread(QThread):
 
    def __init__(self, img, parent=None):
        super(ProThread, self).__init__()
        self.content = ''
        self.target = ''
        self.img = img
 
    def __del__(self):
        self.wait()
    
    def change(self, target, content=None):
        self.target = target
        self.content = content
    
    def run(self):
        #  do something
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
    
    def doFilter(self):
        ori = cv2.imread('./tables/lookup-table.png')
        new = cv2.imread('./tables/'+self.content)
        self.img.changeImg(Filter().myFilter(ori,new,self.img.Image))
        return
    
    def AWB(self):
        self.img.changeImg(AWB(self.img.Image))
        return
    
    def ACE(self):
        self.img.changeImg(ACE().zmIceColor(self.img.Image))
        return
    
    def ACA(self):
        self.img.changeImg(ACA(self.img.Image))
    
    def Anime(self):
        sky = cv2.imread(self.content)
        self.img.changeImg(Sit2Anime().DoProcess(self.img.Image,sky,'./tables'))
        return
    
    def Paint(self):
        #self.img.changeImg(Painter(self.img.Image))
        return
    
    def Ink(self):
        self.img.changeImg(Ink().ink(self.img.Image))
        return
    
    def Pencil(self):
        pencil = cv2.imread('./tables/pencil.jpg')
        self.img.changeImg(Pencil.pencil_drawing(self.img.Image,pencil))
        return
    
    def USM(self):
        self.img.changeImg(Sharp.USM(self.img.Image))
        return
    
    def EdgeSharp(self):
        self.img.changeImg(Sharp.EdgeSharp(self.img.Image))
        return
    
    def SmartSharp(self):
        self.img.changeImg(Sharp.SmartSharp(self.img.Image))
        return
    
    def blur(self,ksize=5):
        self.img.changeImg(Blur.Blur(self.img.Image,ksize))
        return
    
    def GaussianBlur(self,ksize=5,sigma=15):
        self.img.changeImg(Blur.GaussianBlur(self.img.Image,ksize,sigma))
        return
    
    def MotionBlur(self,length=20,angle=40):
        self.img.changeImg(Blur.MotionBlur(self.img.Image,length,angle))
        return
    
    def BlurMore(self,ksize=5):
        self.img.changeImg(Blur.BlurMore(self.img.Image,ksize))
        return
    
    def RadialBlur(self,num=20):
        self.img.changeImg(Blur.RadialBlur(self.img.Image,num))
        return
    
    def SmartBlur(self,color=100,space=5):
        self.img.changeImg(Blur.SmartBlur(self.img.Image,color,space))
        return