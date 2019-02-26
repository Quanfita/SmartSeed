# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:14:25 2019

@author: Quanfita
"""

import sys
import cv2
import ops
from ImgObj import LayerStack
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QScrollArea,
                             QSlider, QVBoxLayout, QPushButton, QColorDialog)
from PyQt5.QtGui import (QPainter, QPen, QColor, QGuiApplication,QPalette,QBrush)
from PyQt5.QtCore import Qt,pyqtSignal

class Draw(QLabel):
    signal = pyqtSignal()
    def __init__(self):
        super(Draw,self).__init__()
        self.setAutoFillBackground(True)
        self.setMouseTracking(False)
        palette = QPalette()
        palette.setBrush(QPalette.Window,QBrush(Qt.Dense7Pattern))
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        self.pos_xy = []
        self.pos_tmp = []
        self.brush = QColor(0,0,0,0)
        self.point_start,self.point_end = (-1,-1),(-1,-1)
        self.pencolor = QColor('black')
        self.thickness = 1
        self.linestyle = Qt.SolidLine
        self.lb_x,self.lb_y,self.lb_w,self.lb_h = 0,0,0,0
        #self.OS = stack
        #self.super_img = img
        self.flag = False
        #self.fig = fig
        self.type = None
    
    def chgType(self,tp):
        self.type = tp
        if self.type in ['Line','Rect','Circle']:
            self.setMouseTracking(True)
        else:
            self.setMouseTracking(False)
    
    def paintEvent(self,event):
        super().paintEvent(event)
        self.painter = QPainter()
        self.painter.begin(self)
        self.pen = QPen(self.pencolor, self.thickness, self.linestyle)
        self.painter.setPen(self.pen)
        if self.type == 'Pencil':
            if len(self.pos_xy) > 1:
                self.point_start = self.pos_xy[0]
                for pos_tmp in self.pos_xy:
                    self.point_end = pos_tmp
    
                    if self.point_end == (-1, -1):
                        self.point_start = (-1, -1)
                        continue
                    if self.point_start == (-1, -1):
                        self.point_start = self.point_end
                        continue
    
                    self.painter.drawLine(self.point_start[0], self.point_start[1], 
                                          self.point_end[0], self.point_end[1])
                    self.point_start = self.point_end
        elif self.type == 'Line':
            self.painter.drawLine(self.point_start[0],self.point_start[1],
                                  self.point_end[0],self.point_end[1])
        elif self.type == 'Rect':
            self.painter.setBrush(self.brush)
            self.painter.drawRect(self.point_start[0],self.point_start[1],
                                  self.point_end[0] - self.point_start[0],
                                  self.point_end[1] - self.point_start[1])
        elif self.type == 'Circle':
            self.painter.setBrush(self.brush)
            self.painter.drawEllipse(self.point_start[0],self.point_start[1],
                                  self.point_end[0] - self.point_start[0],
                                  self.point_end[1] - self.point_start[1])
        self.painter.end()
        pass
    
    def mousePressEvent(self,event):
        self.flag = True
        if self.type in ['Line','Rect','Circle']:
            self.point_start = (event.pos().x(), event.pos().y())
        elif self.type == 'Pencil':
            self.pos_xy = []
    
    def mouseMoveEvent(self,event):
        if self.flag:
            if self.type in ['Line','Rect','Circle']:
                self.point_end = (event.pos().x(), event.pos().y())
            elif self.type == 'Pencil':
                pos_tmp = (event.pos().x(), event.pos().y())
                self.pos_xy.append(pos_tmp)
            self.update()
    
    def mouseReleaseEvent(self,event):
        if self.flag:
            if self.type in ['Line','Rect','Circle']:
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
            elif self.type == 'Pencil':
                pos_test = (-1, -1)
                self.pos_xy.append(pos_test)
                self.pos_xy = []
    
            self.flag = False
            self.update()
            self.saveImg()
            self.Clean()
    
    def ChangePenColor(self, color):
        self.penColor = color
    
    def ChangePenThickness(self, thickness=10):
        self.thickness = thickness
    
    def Clean(self):
        self.flag = False
        self.pos_xy = []
        self.pos_tmp = []
        self.point_start = (-1,-1)
        self.point_end = (-1,-1)
    
    def saveImg(self):
        self.signal.emit()
        '''
        pqscreen  = QGuiApplication.primaryScreen()
        pixmap2 = pqscreen.grabWindow(self.winId(), self.lb_x,
                                      self.lb_y,self.lb_w,self.lb_h)
        pixmap2.save('./tmp/sceen.jpg')
        
        #self.super_img.changeImg(ops.cvtPixmap2CV(pixmap2))
        #self.OS.push([self.super_img.Image,self.type])
        if self.fig == None:
            return
        else:
            self.fig()'''

class AdjBlock(QWidget):
    def __init__(self,pencil):
        super(AdjBlock,self).__init__()
        self.pencil = pencil
        self.main_layout = QVBoxLayout()
        if self.pencil.type in ['Rect','Circle']:
            self.color_lb = QLabel('Border Color',self)
            self.fill_lb = QLabel('Fill Color',self)
            self.fill_lb.setAlignment(Qt.AlignLeft)
            self.fill_btn = QPushButton('',self)
            self.fill_btn.setStyleSheet("QPushButton{background-color:black}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{border:1px}")
            self.fill_btn.clicked.connect(self.fillColor)
        else:
            self.color_lb = QLabel('Color',self)
        self.color_lb.setAlignment(Qt.AlignLeft)

        self.color_btn = QPushButton('',self)
        self.color_btn.setStyleSheet("QPushButton{background-color:black}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.color_btn.clicked.connect(self.chooseColor)
        
        self.thick_lb = QLabel('Thickness',self)
        self.thick_lb.setAlignment(Qt.AlignLeft)
        
        self.thick_sl = QSlider(Qt.Horizontal,self)
        self.thick_sl.resize(30,100)
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
        
        #self.color_sl.valueChanged[int].connect(self.setColor)
        self.thick_sl.valueChanged[int].connect(self.setThick)
        self.show()
    '''
    def setColor(self,value):
        self.color_sl.setValue(value)
        self.color_lb.setText('Color: '+str(value))
        self.pencil.ChangePenColor('red')
        pass
    '''
    def setThick(self,value):
        self.thick_sl.setValue(value)
        self.thick_lb.setText('Tickness: '+str(value))
        self.pencil.ChangePenThickness(value)
        pass
    
    def chooseColor(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pencil.pencolor = col
            self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{border:1px}")
    
    def fillColor(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pencil.brush = col
            self.fill_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{border:1px}")

class Canvas(QWidget):
    signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setMinimumSize(250, 300)
        self.draw = Draw()
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.draw)
        self.layers = LayerStack()
        self.draw.resize(*self.layers.ImgInfo())
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        self.setLayout(self.vbox)
        self.draw.signal.connect(self.img_update)
        self.layers.signal.connect(self.imgOperate)
        self.layers.changeImg(self.layers.Image)
    
    def img_update(self):
        pqscreen  = QGuiApplication.primaryScreen()
        pixmap2 = pqscreen.grabWindow(self.draw.winId(),0,0,
                                      #self.draw.geometry().x(),
                                      #self.draw.geometry().y(),
                                      self.draw.width(),self.draw.height())
        pixmap2.save('./tmp/sceen.jpg')
        self.draw.setPixmap(pixmap2)
        pass
    
    def imgOperate(self):
        self.draw.setPixmap(ops.cvtCV2Pixmap(self.layers.Image))
        cv2.imwrite('./tmp_layer.jpg',self.layers.Image)
        self.signal.emit()
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #pyqt_learn = Draw()
    pyqt_learn = Canvas()
    pyqt_learn.show()
    app.exec_()