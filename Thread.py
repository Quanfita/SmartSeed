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
        self.img.updateLayerImage(self.img.selectedLayerIndex,Filter().myFilter(ori,new,self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def AWB(self):
        self.img.updateLayerImage(AWB(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def ACE(self):
        self.img.updateLayerImage(ACE().zmIceColor(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def ACA(self):
        self.img.updateLayerImage(ACA(self.img.layer[self.img.selectedLayerIndex].Image))
    
    def Anime(self):
        #sky = cv2.imread(self.content)
        self.img.updateLayerImage(Sit2Anime('./tables').DoProcess(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def Paint(self):
        #self.img.updateLayerImage(Painter(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def Ink(self):
        self.img.updateLayerImage(Ink().ink(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def Pencil(self):
        pencil = cv2.imread('./tables/pencil.jpg')
        self.img.updateLayerImage(Pencil.pencil_drawing(self.img.layer[self.img.selectedLayerIndex].Image,pencil))
        return
    
    def USM(self):
        self.img.updateLayerImage(Sharp.USM(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def EdgeSharp(self):
        self.img.updateLayerImage(Sharp.EdgeSharp(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def SmartSharp(self):
        self.img.updateLayerImage(Sharp.SmartSharp(self.img.layer[self.img.selectedLayerIndex].Image))
        return
    
    def blur(self,ksize=5):
        self.img.updateLayerImage(Blur.Blur(self.img.layer[self.img.selectedLayerIndex].Image,ksize))
        return
    
    def GaussianBlur(self,ksize=5,sigma=15):
        self.img.updateLayerImage(Blur.GaussianBlur(self.img.layer[self.img.selectedLayerIndex].Image,ksize,sigma))
        return
    
    def MotionBlur(self,length=20,angle=40):
        self.img.updateLayerImage(Blur.MotionBlur(self.img.layer[self.img.selectedLayerIndex].Image,length,angle))
        return
    
    def BlurMore(self,ksize=5):
        self.img.updateLayerImage(Blur.BlurMore(self.img.layer[self.img.selectedLayerIndex].Image,ksize))
        return
    
    def RadialBlur(self,num=20):
        self.img.updateLayerImage(Blur.RadialBlur(self.img.layer[self.img.selectedLayerIndex].Image,num))
        return
    
    def SmartBlur(self,color=100,space=5):
        self.img.updateLayerImage(Blur.SmartBlur(self.img.layer[self.img.selectedLayerIndex].Image,color,space))
        return