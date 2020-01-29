# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:38:17 2020

@author: Quanfita
"""

from PyQt5.QtWidgets import QWidget, QDialog, QLabel,QApplication, QToolButton, QPushButton, QSlider
from PyQt5.QtCore import Qt,pyqtSignal,QPoint
from PyQt5.QtGui import QIcon,QPixmap,QColor,QPainter,QPen,QPolygon
# from core.Style2Paints import Painters
from core import ops
from common.utils import openImage

import os
import numpy as np

class S2PView(QDialog):

    def __init__(self,controller,debug=False):
        super(S2PView, self).__init__()
        self.__controller = controller
        self.__image = controller.layerStack.image
        self.__res = np.copy(self.__image)
        self.__points = []
        self.__reference = None
        self.__alpha = 0
        self.__current_color = QColor(0,0,0)
        self.__using_color = QColor(255,255,255)
        self.__show_image = ops.resizeAdjustment(self.__image,480,480)
        self.__initView()
        # self.loadSketch()
    
    def __initView(self):
        self.setFixedSize(1040,680)
        self.setCursor(Qt.CrossCursor)
        self.setWindowModality(Qt.ApplicationModal)

        self.sketch_label = SketchCanvas(self)
        self.sketch_label.setGeometry(20+(480-self.__show_image.shape[1])//2,20+(480-self.__show_image.shape[0])//2,self.__show_image.shape[1],self.__show_image.shape[0])
        self.sketch_label.setAlignment(Qt.AlignCenter)
        self.sketch_label.setStyleSheet('QLabel{border:1px solid #ff0000;}')
        self.sketch_label.setPixmap(ops.cvtCV2PixmapAlpha(self.__show_image))
        
        self.colorful_label = QLabel(self)
        self.colorful_label.setGeometry(540+(480-self.__show_image.shape[1])//2,20+(480-self.__show_image.shape[0])//2,self.__show_image.shape[1],self.__show_image.shape[0])
        self.colorful_label.setAlignment(Qt.AlignCenter)
        self.colorful_label.setStyleSheet('QLabel{border:1px solid #ff0000;}')
        self.colorful_label.setPixmap(ops.cvtCV2PixmapAlpha(self.__show_image))
        
        self.color_label = ColorLabel(self)
        self.color_label.setGeometry(20,520,120,120)
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.changed[tuple].connect(self.colorChanged)
        self.color_label.hover[tuple].connect(self.colorHover)
        
        self.color_table = ColorTable(self)
        self.color_table.setGeometry(160,520,500,120)
        self.color_table.changed[tuple].connect(self.colorChanged)
        self.color_table.hover[tuple].connect(self.colorHover)

        self.ok_btn = QPushButton('保存',self)
        self.ok_btn.setGeometry(940, 520, 80, 30)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton('取消',self)
        self.cancel_btn.setGeometry(940, 570, 80, 30)
        self.cancel_btn.clicked.connect(self.close)

        self.paint_btn = QToolButton(self)
        self.paint_btn.setGeometry(500,260,40,40)
        self.paint_btn.setStyleSheet("QToolButton{background:url('./static/UI/right.png') no-repeat center;}")
        # self.paint_btn.clicked.connect(self.getPaintingResult)
        
        self._cur_label = QLabel(self)
        self._use_label = QLabel(self)
        self._cur_label.setGeometry(680,520,40,60)
        self._use_label.setGeometry(680,580,40,60)
        self._cur_label.setStyleSheet('QLabel{background-color:'+str(self.__current_color.name())+';}')
        self._use_label.setStyleSheet('QLabel{background-color:'+str(self.__using_color.name())+';}')
        
        self._color_pos_btn = QToolButton(self)
        self._color_pos_btn.setGeometry(740,520,40,40)
        self._color_pos_btn.setStyleSheet("QToolButton{background:url('./static/UI/vector.png') no-repeat center;}")
        self._color_pos_btn.clicked.connect(self.changeType)
        
        self._color_prompt_btn = QToolButton(self)
        self._color_prompt_btn.setGeometry(740,560,40,40)
        self._color_prompt_btn.setStyleSheet("QToolButton{background:url('./static/UI/vector2.png') no-repeat center;}")
        self._color_prompt_btn.clicked.connect(self.changeType)
        
        self._eraser_btn = QToolButton(self)
        self._eraser_btn.setGeometry(740,600,40,40)
        self._eraser_btn.setStyleSheet("QToolButton{background:url('./static/UI/eraser.png') no-repeat center;}")
        self._eraser_btn.clicked.connect(self.changeType)

        self._upload_btn = QToolButton(self)
        self._upload_btn.setGeometry(780,520,40,40)
        self._upload_btn.setStyleSheet("QToolButton{background:url('./static/UI/upload.png') no-repeat center;}")
        self._upload_btn.clicked.connect(self.setReference)

        self._clear_btn = QToolButton(self)
        self._clear_btn.setGeometry(780,560,40,40)
        self._clear_btn.setStyleSheet("QToolButton{background:url('./static/UI/clear.png') no-repeat center;}")
        self._clear_btn.clicked.connect(self.clearPoints)

        self._refer_label = QLabel(self)
        self._refer_label.setGeometry(840,520,80,100)
        self._refer_label.setAlignment(Qt.AlignCenter)
        self._refer_label.setPixmap(ops.cvtCV2PixmapAlpha(ops.resizeAdjustment(ops.imread('./static/UI/upload_reference.png'),80,80)))

        self._alpha_bar = QSlider(Qt.Horizontal,self)
        self._alpha_bar.setGeometry(840,620,80,20)
        self._alpha_bar.setMinimum(0)
        self._alpha_bar.setMaximum(100)
        self._alpha_bar.valueChanged[int].connect(self.setAlpha)

    def setAlpha(self, value):
        self.__alpha = float(value/100)
    
    def setReference(self):
        info = openImage(self)
        self.__reference = info['image'].image
        self._refer_label.setPixmap(ops.cvtCV2PixmapAlpha(ops.resizeAdjustment(self.__reference,80,100)))

    def clearPoints(self):
        self.sketch_label.clearPoints()

    def colorHover(self, color):
        self._cur_label.setStyleSheet('QLabel{background-color:'+str(QColor(*color).name())+';}')

    def colorChanged(self, color):
        tmp_color = QColor(*color)
        self._use_label.setStyleSheet('QLabel{background-color:'+str(tmp_color.name())+';}')
        self.sketch_label.setPointColor(tmp_color)
    
    def changeType(self):
        sender = self.sender()
        if sender == self._color_pos_btn:
            self.sketch_label.setType(0)
        elif sender == self._color_prompt_btn:
            self.sketch_label.setType(2)
        elif sender == self._eraser_btn:
            self.sketch_label.setType(1)
    
    def getRes(self):
        return self.__res
    
    # def loadSketch(self):
    #     if os.path.exists('./tmp/tmp.improved.jpg'):
    #         os.remove('./tmp/tmp.improved.jpg')
    #     if os.path.exists('./tmp/tmp.recolorization.jpg'):
    #         os.remove('./tmp/tmp.recolorization.jpg')
    #     if os.path.exists('./tmp/tmp.de_painting.jpg'):
    #         os.remove('./tmp/tmp.de_painting.jpg')
    #     if os.path.exists('./tmp/tmp.colorization.jpg'):
    #         os.remove('./tmp/tmp.colorization.jpg')
    #     if os.path.exists('./tmp/tmp.rendering.jpg'):
    #         os.remove('./tmp/tmp.rendering.jpg')
    #     Painters.sketch_upload(self.__image[:,:,:-1])
    
    # def getPaintingResult(self):
    #     points = [[i[0]/self.__show_image.shape[1],i[1]/self.__show_image.shape[0],i[2][0],i[2][1],i[2][2],i[-1]] for i in self.sketch_label.getPoints()]
    #     print(points)
    #     tmp = Painters.painting(self.__image[:,:,:-1],points=points,alpha=self.__alpha,reference=self.__reference)
    #     self.__res = ops.resize(tmp,self.__image.shape[1],self.__image.shape[0])
    #     tmp = ops.resize(tmp,self.__show_image.shape[1],self.__show_image.shape[0])
    #     # ops.imsave(tmp,'res.png')
    #     self.colorful_label.setPixmap(ops.cvtCV2Pixmap(tmp))

class SketchCanvas(QLabel):
    def __init__(self,parent=None):
        super(SketchCanvas, self).__init__(parent)
        # self.parent = parent
        self.__color = QColor(0,0,0)
        self.__pos = []
        self.__type = 0
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.__pos:
            painter = QPainter()
            if not painter.isActive():
                painter.begin(self)
            pen = QPen(QColor(0,0,0), 1, Qt.SolidLine)
            painter.setPen(pen)
            for pos in self.__pos:
                painter.setBrush(QColor(*pos[2]))
                if pos[-1] == 2:
                    painter.drawEllipse(pos[0]-3,pos[1]-3,7,7)
                elif pos[-1] == 0:
                    painter.drawPolygon(QPolygon([QPoint(pos[0],pos[1]-5),QPoint(pos[0]-5,pos[1]),QPoint(pos[0],pos[1]+5),QPoint(pos[0]+5,pos[1])]))
            painter.end()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.__type != 1:
            if not self.is_near((event.pos().x(),event.pos().y()),self.__pos):
                self.__pos.append([event.pos().x(),event.pos().y(),self.__color.getRgb(),self.__type])
        else:
            pos = self.getClickedPoint((event.pos().x(),event.pos().y()),self.__pos)
            if pos is not None:
                self.__pos.remove(pos)
        self.update()
    
    def is_near(self,point,poss):
        x1,y1 = point[0],point[1]
        for pos in poss:
            x2,y2 = pos[0],pos[1]
            if (x1-x2)**2+(y1-y2)**2 < 50:
                return True
        return False
    
    def getClickedPoint(self,point,poss):
        x1,y1 = point[0],point[1]
        for pos in poss:
            x2,y2 = pos[0],pos[1]
            if (x1-x2)**2+(y1-y2)**2 < 50:
                return pos
        return None
    
    def setPointColor(self, color):
        self.__color = color
    
    def setType(self, type):
        self.__type = type
    
    def getPoints(self):
        return self.__pos
    
    def clearPoints(self):
        self.__pos = []
        self.update()

class ColorLabel(QLabel):
    changed = pyqtSignal(tuple)
    hover = pyqtSignal(tuple)
    def __init__(self,parent=None):
        super(ColorLabel, self).__init__(parent)
        self.__table = ops.imread('./static/UI/ring_mini.png')
        self.setFixedSize(120,120)
        self.setPixmap(ops.cvtCV2PixmapAlpha(self.__table))
        self.setMouseTracking(True)
        self.__color = QColor(0,0,0)
    
    def mousePressEvent(self, event):
        x,y = event.pos().x(),event.pos().y()
        self.__color = QColor(*self.__table[y,x][:-1][::-1])
        self.changed.emit(self.__color.getRgb())
    
    def mouseMoveEvent(self, event):
        x,y = event.pos().x(),event.pos().y()
        self.hover.emit(QColor(*self.__table[y,x][:-1][::-1]).getRgb())

class ColorTable(QLabel):
    changed = pyqtSignal(tuple)
    hover = pyqtSignal(tuple)
    def __init__(self,parent=None):
        super(ColorTable, self).__init__(parent)
        self.__table = ops.imread('./static/UI/palette.png')
        self.setFixedSize(500,120)
        self.setPixmap(ops.cvtCV2PixmapAlpha(self.__table))
        self.setMouseTracking(True)
        self.__color = QColor(0,0,0)
    
    def mousePressEvent(self, event):
        x,y = event.pos().x(),event.pos().y()
        self.__color = QColor(*self.__table[y,x][:-1][::-1])
        self.changed.emit(self.__color.getRgb())
    
    def mouseMoveEvent(self, event):
        x,y = event.pos().x(),event.pos().y()
        self.hover.emit(QColor(*self.__table[y,x][:-1][::-1]).getRgb())