# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 12:34:17 2020

@author: Quanfita
"""

from PyQt5.QtWidgets import QLabel,QTabWidget,QWidget,QScrollArea,QPushButton,QColorDialog
from PyQt5.QtCore import Qt,pyqtSignal,QSettings,QObject
from PyQt5.QtGui import QPixmap,QIcon,QPainter,QPen,QColor
from views.DockWidget import FrontBackColor
from core import ops

import cv2
import numpy as np
import time

class ColorWidget(QWidget):
    def __init__(self, callbacks, parent=None):
        super(ColorWidget, self).__init__(parent)
        self.setMinimumHeight(150)
        self.setMinimumWidth(150)
        self.setMaximumHeight(400)
        self.setMaximumWidth(250)
        self.resize(250,200)
        
        self.setStyleSheet("QWidget{background:#565656;}")
        
        self.target = 'hue'
        self.FBC = FrontBackColor(callbacks,self)
        self.FBC.setGeometry(5,5,40,40)
        # self.FBC.frontColorChanged.connect(self.calculate)

        self.color_slider = LineSlider(self)
        self.color_slider.setGeometry(self.width()-50,0,40,self.height())
        self.color_slider.colorChanged[tuple].connect(self.changeColorPicker)

        self.main_label = TouchLabel(self)
        self.main_label.setColorPicker((0,0,255))
        self.main_label.setGeometry(50,5,self.width()-105,self.height()-10)
        self.main_label.colorChanged[tuple].connect(self.changeColor)
        # self.calculate()
    
    def changeColorPicker(self, color):
        self.main_label.setColorPicker(color)
    
    def changeColor(self, color):
        print('change color:'+str(color))
        self.FBC.changeFrontColor(QColor(*ops.cvtBGR2RGB(color)))
    
    def calculate(self):
        r,g,b,_ = self.FBC.frontColor.getRgb()
        index = np.argmax([r,g,b])
        pure_color = [b,g,r]
        pure_color[2 - index] = 255
        index = np.argmin([r,g,b])
        pure_color[2 - index] = 0
        print([b,g,r])
        self.color_slider.autoFindColorPosition(pure_color)
        self.main_label.autoFindColorPosition((b,g,r))
        self.FBC.changeFrontColor(QColor(r,g,b))

class LineLabel(QLabel):
    clicked = pyqtSignal(tuple)
    def __init__(self,parent=None):
        super(LineLabel, self).__init__(parent)
        self.__color_line = cv2.imread('./static/UI/hueline.png')

        self.setFixedWidth(20)
        self.setPixmap(QPixmap('./static/UI/hueline.png').scaled(self.width(),self.height()))

    @property
    def colorLine(self):
        return self.__color_line

    def resizeEvent(self, event):
        self.setPixmap(QPixmap('./static/UI/hueline.png').scaled(self.width(),self.height()))

    def getPositionPercentOnReal(self, pos_y):
        return pos_y / self.height()
    
    def getPositionPercentOnShow(self, pos_y):
        return pos_y / self.__color_line.shape[0]
    
    def getPositionColor(self, pos_y):
        precent = self.getPositionPercentOnReal(pos_y)
        index = min(int(self.__color_line.shape[0] * precent),self.__color_line.shape[0]-1)
        return self.__color_line[index,0]

    def mousePressEvent(self, event):
        self.__click_position = event.pos()
        if (event.pos().x() >= -10 and event.pos().y() >= 0) and (event.pos().x() <= self.width() and event.pos().y() <= self.height()):
            self.clicked.emit((event.pos().x(),event.pos().y()))
    
    def mouseMoveEvent(self, event):
        if self.__click_position != event.pos():
            if (event.pos().y() >= 0) and (event.pos().y() <= self.height()):
                self.clicked.emit((event.pos().x(),event.pos().y()))
    
    def mouseReleaseEvent(self, event):
        if self.__click_position != event.pos():
            if (event.pos().y() >= 0) and (event.pos().y() <= self.height()):
                self.clicked.emit((event.pos().x(),event.pos().y()))

class LineSlider(QWidget):
    colorChanged = pyqtSignal(tuple)
    def __init__(self,parent=None):
        super(LineSlider, self).__init__(parent)
        self.setFixedWidth(40)
        self.setStyleSheet("QWidget{background:#565656;}")
        self.__now_color = None
        self.color_line = LineLabel(self)
        self.color_line.setGeometry(15,5,20,self.height()-10)
        self.__tmp_pos = (-1,-1)

        self.handle = HandleButton(self)
        self.handle.setGeometry(5,5,10,10)
        self.handle.show()

        self.color_line.clicked[tuple].connect(self.setHandlePosition)
        self.handle.clicked.connect(self.setHandlePosition)
    
    def autoFindColorPosition(self, color):
        self.__now_color = color
        index = np.argwhere(np.all(self.color_line.colorLine == color,axis=-1))
        print(color)
        if len(index) != 0:
            index = index[0][0]
            precent = self.color_line.getPositionPercentOnShow(index)
            index = min(int(self.height()*precent),self.height())
            self.setHandlePosition((0,index))

    def setHandlePosition(self, pos=None):
        if pos is None:
            pos = self.__tmp_pos
        self.handle.setGeometry(5,pos[1],10,10)
        color = self.color_line.getPositionColor(pos[1])
        self.colorChanged.emit((color[0],color[1],color[2]))
    
    def resizeEvent(self, event):
        self.color_line.setGeometry(15,5,20,self.height()-10)
        self.autoFindColorPosition(self.__now_color)
    
    def mousePressEvent(self, event):
        if event.pos().y() >= 0 and event.pos().y() <= self.color_line.height():
            self.setHandlePosition((event.pos().x(),event.pos().y()))
    
    def mouseMoveEvent(self, event):
        if event.pos().y() >= 0 and event.pos().y() <= self.color_line.height():
            self.setHandlePosition((event.pos().x(),event.pos().y()))
    
    def mouseReleaseEvent(self, event):
        if event.pos().y() >= 0 and event.pos().y() <= self.color_line.height():
            self.setHandlePosition((event.pos().x(),event.pos().y()))

class HandleButton(QPushButton):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(HandleButton, self).__init__(parent)
        self.setFixedSize(10,10)
        self.setStyleSheet("QPushButton{border:0px;}")
        self.setIcon(QIcon(QPixmap('./static/UI/caret-right-solid.svg').scaled(10,12)))

class TouchLabel(QLabel):
    colorChanged = pyqtSignal(tuple)
    def __init__(self, parent=None):
        super(TouchLabel, self).__init__(parent)
        self.setMinimumHeight(100)
        self.setMinimumWidth(100)
        self.setMaximumHeight(350)
        self.setMaximumWidth(200)

        self.__color_picker = None
        self.__now_color = None

        self.__click_position = None

    def autoFindColorPosition(self, color):
        self.__now_color = color
        index = np.argwhere(np.all(self.__color_picker == color, axis=-1))
        if len(index) != 0:
            percent_x, percent_y = self.getPositionPercentOnShow((index[0][1],index[0][0]))
            y,x = int(self.height() * percent_y), int(self.width() * percent_x)
            self.__click_position = (x,y)
            self.repaint()
        else:
            self.__click_position = None
    
    def resizeEvent(self, event):
        self.setPixmap(ops.cvtCV2Pixmap(self.__color_picker).scaled(self.width(),self.height()))
        self.autoFindColorPosition(self.__now_color)

    def setColor(self, color):
        self.__now_color = (color[0],color[1],color[2])
        self.colorChanged.emit(self.__now_color)

    def setColorPicker(self, color):
        self.__color_picker = ops.generateHueColorPicker(color)
        self.setPixmap(ops.cvtCV2Pixmap(self.__color_picker).scaled(self.width(),self.height()))
        if self.__click_position is not None:
            percent_x, percent_y = self.getPositionPercentOnReal(self.__click_position)
            y,x = int(self.__color_picker.shape[0] * percent_y), int(self.__color_picker.shape[1] * percent_x)
            self.setColor(self.__color_picker[y,x])
            self.repaint()

    def getPositionPercentOnShow(self, pos):
        return pos[0] / self.__color_picker.shape[1],pos[1] / self.__color_picker.shape[0]

    def getPositionPercentOnReal(self, pos):
        return pos[0] / self.width(),pos[1] / self.height()

    def mousePressEvent(self, event):
        if self.__color_picker is not None:
            x,y = event.pos().x(),event.pos().y()
            self.__click_position = (x,y)
            percent_x, percent_y = self.getPositionPercentOnReal((x,y))
            y,x = int(self.__color_picker.shape[0] * percent_y), int(self.__color_picker.shape[1] * percent_x)
            self.setColor(self.__color_picker[y,x])
            self.repaint()
    
    def mouseMoveEvent(self, event):
        if self.__color_picker is not None:
            x,y = event.pos().x(),event.pos().y()
            self.__click_position = (x,y)
            percent_x, percent_y = self.getPositionPercentOnReal((x,y))
            y,x = int(self.__color_picker.shape[0] * percent_y), int(self.__color_picker.shape[1] * percent_x)
            if y >= 0 and y < self.__color_picker.shape[0] and x >= 0 and x < self.__color_picker.shape[1]:
                self.setColor(self.__color_picker[y,x])
                self.repaint()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.__click_position is not None:
            painter = QPainter()
            painter.begin(self)
            pen = QPen(QColor('black'),1,Qt.SolidLine)
            painter.setPen(pen)
            painter.drawEllipse(self.__click_position[0]-5,self.__click_position[1]-5,10,10)
            painter.end()
