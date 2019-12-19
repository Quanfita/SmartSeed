# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""
from PyQt5.QtWidgets import QLabel,QTabWidget,QWidget,QScrollArea,QPushButton
from PyQt5.QtCore import Qt,pyqtSignal,QSettings,QObject
from core import ops

import cv2
import numpy as np


class InfoLabel(QLabel):
    """docstring for InfoLabel"""
    signal = pyqtSignal(dict)
    def __init__(self):
        super(InfoLabel, self).__init__()
        self.setLabelText({'x':0,'y':0})
        self.setAlignment(Qt.AlignLeft)
        self.setStyleSheet("color:white;background-color:#535353;padding:10px;border:1px solid #282828;")

    def setLabelText(self, content):
        x, y = content['x'], content['y']
        self.text = "x: {0},  y: {1}".format(x, y)
        self.setText(self.text)


class ColorConical(QWidget):
    signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.show()
    
    def paintEvent(self,event):
        super().paintEvent(event)
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing,True)
        r = 150
        self.conicalGradient = QConicalGradient(0,0,0)
        self.conicalGradient.setColorAt(0.0,Qt.red)
        self.conicalGradient.setColorAt(60/360,Qt.yellow)
        self.conicalGradient.setColorAt(120/360,Qt.green)
        self.conicalGradient.setColorAt(180/360,Qt.cyan)
        self.conicalGradient.setColorAt(240/360,Qt.blue)
        self.conicalGradient.setColorAt(300/360,Qt.magenta)
        self.conicalGradient.setColorAt(1.0,Qt.red)
        
        self.painter.translate(r,r)
        
        self.brush = QBrush(self.conicalGradient)
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(self.brush)
        self.painter.drawEllipse(QPoint(0,0),r,r)


class FrontBackColor(QWidget):
    signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setFixedSize(40,40)
        self.backButton = QPushButton(self)
        self.backButton.setGeometry(15,15,20,20)
        self.backButton.setFixedSize(20,20)
        self.backButton.setStyleSheet("QPushButton{border:1px solid #cdcdcd;background-color:black;}")
        self.backButton.clicked.connect(self.__setBackColor)
        self.frontButton = QPushButton(self)
        self.frontButton.setGeometry(5,5,20,20)
        self.frontButton.setFixedSize(20,20)
        self.frontButton.setStyleSheet("QPushButton{border:1px solid #cdcdcd;background-color:white;}")
        self.frontButton.clicked.connect(self.__setFrontColor)
        self.show()
    
    def changeFrontColor(self,color):
        self.frontButton.setStyleSheet("QPushButton{border:1px solid #cdcdcd;background-color:"+str(color.name())+";}")
        self.front_signal.emit({'front':color.name()})
    
    def changeBackColor(self,color):
        self.backButton.setStyleSheet("QPushButton{border:1px solid #cdcdcd;background-color:"+str(color.name())+";}")
        self.back_signal.emit({'back':color.name()})
    
    def __setFrontColor(self):
        col = QColorDialog.getColor()
        self.changeFrontColor(col)
        
    def __setBackColor(self):
        col = QColorDialog.getColor()
        self.changeBackColor(col)


class ColorLinear(QWidget):
    signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.show()
    
    def paintEvent(self,event):
        super().paintEvent(event)
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing,True)
        r = 150
        self.linearGradient = QLinearGradient(0,0,0,0)
        #self.linearGradient.setColorAt(0.0,Qt.white)
        #self.linearGradient.setColorAt(1.0,Qt.black)
        #self.linearGradient
        
        self.painter.translate(r,r)
        
        self.brush = QBrush(self.conicalGradient)
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(self.brush)
        self.painter.drawEllipse(QPoint(0,0),r,r)


class Hist(QLabel):
    """
    The hist to show the RGB's scatter of the image.
    """
    signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setMaximumSize(300,200)
        self.setMinimumSize(270,180)
        self.setStyleSheet('QLabel{color:white;background-color:#535353;border:1px solid #282828;}')
    
    def calcAndDrawHist(self, image, color):
        # To get one channel hist.
        hist= cv2.calcHist([image], [0], None, [256], [0.0,255.0])  
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)  
        histImg = np.zeros([256,256,3], np.uint8)  
        hpt = int(0.9* 256)
        if maxVal <1:
            maxVal = 1.0
        for h in range(256):  
            intensity = int(hist[h]*hpt/maxVal)  
            cv2.line(histImg,(h,256), (h,256-intensity), color)  
              
        return histImg
    
    def DrawHistogram(self,img):
        # To get result, and transform to pixmap.
        b,g,r,_ = cv2.split(img)
        h_b = self.calcAndDrawHist(b,(255,0,0))
        h_g = self.calcAndDrawHist(g,(0,255,0))
        h_r = self.calcAndDrawHist(r,(0,0,255))
        res = h_b + h_g + h_r
        res[np.where(res[:,:] == [0,0,0])] = 83
        '''
        for i in range(res.shape[0]):
            for j in range(res.shape[1]):
                if res[i,j].any() == 0:
                    res[i,j,:] = 83'''
        res = cv2.resize(res,(self.width(),self.height()))
        res = cv2.cvtColor(res,cv2.COLOR_BGR2RGB)
        self.setPixmap(ops.cvtCV2Pixmap(res))


class AdjBlock(QWidget):
    """
    This class is a common widget,
    it is used to set the Attributes of pencil or shapes.
    """
    signal = pyqtSignal(dict)
    def __init__(self,pencil,debug=False):
        super(AdjBlock,self).__init__()
        self.pencil = pencil
        self.setContentsMargins(5,0,5,0)
        self.main_layout = QHBoxLayout()
        if self.pencil.type in ['Rect','Circle']:
            self.color_lb = QLabel('Border:',self)
            self.color_lb.resize(40,30)
            self.fill_lb = QLabel('Fill:',self)
            self.fill_lb.setAlignment(Qt.AlignLeft)
            self.fill_lb.resize(40,30)
            self.fill_btn = QPushButton('',self)
            self.fill_btn.resize(24,18)
            self.fill_btn.setStyleSheet("QPushButton{background-color:black}"
                                        "QPushButton{border:1px solid #cdcdcd;}")
            self.fill_btn.clicked.connect(self.fillColor)
        else:
            self.color_lb = QLabel('Color',self)
        self.color_lb.setAlignment(Qt.AlignLeft)

        self.color_btn = QPushButton('',self)
        self.color_btn.resize(24,18)
        self.color_btn.setStyleSheet("QPushButton{background-color:black}"
                                     "QPushButton{border:1px solid #cdcdcd;}")
        self.color_btn.clicked.connect(self.chooseColor)
        
        self.thick_lb = QLabel('Thick',self)
        self.thick_lb.setAlignment(Qt.AlignLeft)
        
        self.thick_sl = QSlider(Qt.Horizontal,self)
        self.thick_sl.resize(30,30)
        self.thick_sl.setMinimum(1)
        self.thick_sl.setMaximum(10)
        self.thick_sl.setTickInterval(1)
        self.thick_sl.setTickPosition(QSlider.TicksAbove)
        
        self.main_layout.addWidget(self.color_lb)
        #self.main_layout.addWidget(self.color_sl)
        self.main_layout.addWidget(self.color_btn)
        self.main_layout.addWidget(self.thick_lb)
        self.main_layout.addWidget(self.thick_sl)
        if self.pencil.type in ['Rect','Circle']:
            self.main_layout.addWidget(self.fill_lb)
            self.main_layout.addWidget(self.fill_btn)
        
        self.setLayout(self.main_layout)
        self.pencil.color_signal[int,int,int].connect(self.setColorByRGB)
        #self.color_sl.valueChanged[int].connect(self.setColor)
        self.thick_sl.valueChanged[int].connect(self.setThick)
        self.show()
    
    def setColorByRGB(self,b,g,r):
        # Set color by three values of RGB.
        col = QColor(r,g,b)
        self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                     "QPushButton{border:1px solid #cdcdcd;}")
        #self.color_lb.setText('Color: '+col.name())
        self.pencil.changePenColor(col)
        pass
    
    def setColorByName(self,colorName):
        # Set color by the string of hex.
        self.color_btn.setStyleSheet("QPushButton{background-color:"+colorName+"}"
                                     "QPushButton{border:1px solid #cdcdcd;}")
        #self.color_lb.setText('Color: '+col.name())
        self.pencil.changePenColor(QColor(colorName))
        pass
    
    def setThick(self,value):
        self.thick_sl.setValue(value)
        #self.thick_lb.setText('Tickness: '+str(value))
        self.pencil.changePenThickness(value)
        pass
    
    def chooseColor(self):
        col = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        self.pencil.pencolor = col
        self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                    "QPushButton{border:1px solid #cdcdcd;}")
    
    def fillColor(self):
        col = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        self.pencil.brush = col
        self.fill_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                    "QPushButton{border:1px solid #cdcdcd;}")
