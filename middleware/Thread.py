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
# from Op import Sharp
# from Op import Blur
from common.app import logger
 
class ProThread(QThread):
    """
    This is a thread that responsible for image processing.
    dict:{img:the image to process,method:the type of process,other:other arguements}
    """
    in_signal = pyqtSignal(dict)
    out_signal = pyqtSignal(dict)
    def __init__(self, debug=False, parent=None):
        super(ProThread, self).__init__()
        self.debug = debug
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
        logger.debug('Process thread request message: '+str(content))
        self._p_queue.append(content)
    
    def changeMode(self, img, target, content=None):
        self.tmp_img = img
        self.target = target
        self.content = content
        print(self.target)
    
    def run(self):
        #  do something
        content = self._p_queue.pop()
        self.target = content['type']
        self.tmp_img = content['data']['image']
        self.content = content['data']['filter']
        if self.debug:
        	t = time.time()
        	logger.debug('Start do '+ self.target+'.')
        self.task_dict[self.target]()

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
        if self.debug:
        	logger.debug('Process time:'+str(time.time() - t)+'.')
        self.out_signal.emit({'data':{'img':self.tmp_img},'type':'refresh','togo':None})
        content['callback'](self.tmp_img)
    
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
        ori = cv2.imread('./static/tables/lookup-table.png')
        new = cv2.imread('./static/tables/'+_dict[self.content])
        self.tmp_img = Filter().myFilter(ori,new,self.tmp_img)
        return
    
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