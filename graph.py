# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:05:05 2019

@author: Quanfita
"""
import ops
import sys
import numpy as np
from PyQt5.QtWidgets import (QGraphicsView,QGraphicsScene,QApplication,
                             QGraphicsItem,QGraphicsObject)
from PyQt5.QtCore import QRectF,Qt
from PyQt5.QtGui import QColor

class Canvas(QGraphicsItem):
    
    def __init__(self,img=None):
        super(Canvas,self).__init__()
        self.shape = (0,0)
        if img != None:
            self.img = img
            self.shape = img.shape
        else:
            self.img = np.zeros((256,256,3),dtype=np.uint8)
            self.img +=255
            self.shape = (256,256,3)
        
    
    def boundingRect(self):
        return QRectF(0,0,self.shape[1],self.shape[0])
    
    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawEllipse(0, 0, self.shape[1], self.shape[0])
        image = ops.cvtCV2Image(self.img)
        painter.drawImage(QRectF(0, 0, self.shape[1], self.shape[0]), image)
    
    def mousePressEvent(self, event):
        self.shape = (512,512,3)
        pass
    
    def mouseMoveEvent(self, event):
        pass
    
    def mouseReleaseEvent(self, event):
        pass
        
class Layer(QGraphicsObject):
    
    def __init__(self):
        super(Layer,self).__init__()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    layer = Canvas()
    scene = QGraphicsScene(0, 0, 960, 540)
    scene.addItem(layer)
    view = QGraphicsView(scene)
    view.setBackgroundBrush(QColor('#555555'))
    view.show()
    sys.exit(app.exec_())