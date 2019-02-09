# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:14:25 2019

@author: Quanfita
"""

import sys
import ops
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, 
                             QSlider, QVBoxLayout, QPushButton, QColorDialog)
from PyQt5.QtGui import (QPainter, QPen, QColor, QGuiApplication)
from PyQt5.QtCore import Qt

class Draw(QLabel):
    
    def __init__(self, stack, img, fig):
        super(Draw,self).__init__()
        self.setMouseTracking(False)
        self.pos_xy = []
        self.pos_tmp = []
        self.point_start,self.point_end = (-1,-1),(-1,-1)
        self.pencolor = QColor('black')
        self.thickness = 1
        self.linestyle = Qt.SolidLine
        self.lb_x,self.lb_y,self.lb_w,self.lb_h = 0,0,0,0
        self.OS = stack
        self.super_img = img
        self.flag = False
        self.fig = fig
        self.type = None
    
    def chgType(self,tp):
        self.type = tp
        if self.type == 'Line':
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
            self.painter.drawLine(self.point_start[0],self.point_start[1],self.point_end[0],self.point_end[1])
        self.painter.end()
        pass
    
    def mousePressEvent(self,event):
        self.flag = True
        if self.type == 'Line':
            self.point_start = (event.pos().x(), event.pos().y())
        elif self.type == 'Pencil':
            self.pos_xy = []
    
    def mouseMoveEvent(self,event):
        if self.flag:
            if self.type == 'Line':
                self.point_end = (event.pos().x(), event.pos().y())
            elif self.type == 'Pencil':
                pos_tmp = (event.pos().x(), event.pos().y())
                self.pos_xy.append(pos_tmp)
            self.update()
    
    def mouseReleaseEvent(self,event):
        if self.type == 'Line':
            self.flag = False
            self.update()
            self.saveImg()
            self.point_start = (-1,-1)
            self.point_end = (-1,-1)
        elif self.type == 'Pencil':
            self.flag = False
            pos_test = (-1, -1)
            self.pos_xy.append(pos_test)
            self.pos_xy = []
        self.update()
        self.saveImg()
    
    def ChangePenColor(self, color):
        self.penColor = color
    
    def ChangePenThickness(self, thickness=10):
        self.thickness = thickness
    
    def Clean(self):
        self.pos_xy = []
        self.pos_tmp = []
        self.point_start = (-1,-1)
        self.point_end = (-1,-1)
    
    def saveImg(self):
        pqscreen  = QGuiApplication.primaryScreen()
        pixmap2 = pqscreen.grabWindow(self.winId(), self.lb_x,
                                      self.lb_y,self.lb_w,self.lb_h)
        pixmap2.save('./tmp/sceen.jpg')
        self.super_img.changeImg(ops.cvtPixmap2CV(pixmap2))
        self.OS.push([self.super_img.Image,self.type])
        if self.fig == None:
            return
        else:
            self.fig()

class AdjBlock(QWidget):
    def __init__(self,pencil):
        super(AdjBlock,self).__init__()
        self.pencil = pencil
        self.main_layout = QVBoxLayout()
        self.color_lb = QLabel('Color',self)
        self.color_lb.setAlignment(Qt.AlignLeft)
        
        #self.color_sl = QSlider(Qt.Horizontal,self)
        #self.color_sl.resize(30,100)
        #self.color_sl.setMinimum(0)
        #self.color_sl.setMaximum(256)
        #self.color_sl.setTickPosition(QSlider.TicksAbove)
        
        self.color_btn = QPushButton('Choose Color',self)
        self.color_btn.clicked.connect(self.chooseColor)
        
        self.thick_lb = QLabel('Thickness',self)
        self.thick_lb.setAlignment(Qt.AlignLeft)
        
        self.thick_sl = QSlider(Qt.Horizontal,self)
        self.thick_sl.resize(30,100)
        self.thick_sl.setMinimum(1)
        self.thick_sl.setMaximum(10)
        self.thick_sl.setTickPosition(QSlider.TicksAbove)
        
        self.main_layout.addWidget(self.color_lb)
        #self.main_layout.addWidget(self.color_sl)
        self.main_layout.addWidget(self.color_btn)
        self.main_layout.addWidget(self.thick_lb)
        self.main_layout.addWidget(self.thick_sl)
        
        self.setLayout(self.main_layout)
        
        #self.color_sl.valueChanged[int].connect(self.setColor)
        self.thick_sl.valueChanged[int].connect(self.setThick)
        self.show()
    
    def setColor(self,value):
        self.color_sl.setValue(value)
        self.color_lb.setText('Color: '+str(value))
        self.pencil.ChangePenColor('red')
        pass
    
    def setThick(self,value):
        self.thick_sl.setValue(value)
        self.thick_lb.setText('Tickness: '+str(value))
        self.pencil.ChangePenThickness(value)
        pass
    
    def chooseColor(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pencil.pencolor = col
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pyqt_learn = Draw()
    pyqt_learn.show()
    app.exec_()