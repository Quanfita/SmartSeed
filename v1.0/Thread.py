# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:15:51 2019

@author: Quanfita
"""

import cv2
from Op.Filter import Filter
from Op.Special.Sit2Anime import Sit2Anime
from Op.Image.AWB import whiteBalance
from Op.Image.ACE import ACE
from PyQt5.QtCore import QThread
 
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
            self.ACE_()
        elif self.target == 'Anime':
            self.Anime()
        else:
            return
    
    def doFilter(self):
        ori = cv2.imread('./tables/lookup-table.png')
        new = cv2.imread('./tables/'+self.content)
        self.img.changeImg(Filter().myFilter(ori,new,self.img.Image))
        return
    
    def AWB(self):
        self.img.changeImg(whiteBalance(self.img.Image))
        return
    
    def ACE_(self):
        self.img.changeImg(ACE().automatic_color_equalization(self.img.Image))
        return
    
    def Anime(self):
        sky = cv2.imread(self.content)
        self.img.changeImg(Sit2Anime().DoProcess(self.img.Image,sky,'./tables'))
        return
        