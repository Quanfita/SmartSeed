# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""
from PyQt5.QtWidgets import QLabel,QTabWidget,QWidget,QScrollArea,QVBoxLayout,QApplication
from PyQt5.QtGui import QPainter, QPen, QColor,QPixmap,QPalette,QBrush,QCursor
from PyQt5.QtCore import Qt,pyqtSignal,QSettings,QObject
from common.app import logger
from core import ops
from middleware.Structure import LayerStack
from common import utils

import numpy as np
import setting
import cv2

class Brush(QObject):
    signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.shape = np.zeros([1024,1024,4],dtype=np.uint8)
        self.mask = 255*np.ones([1024,1024],dtype=np.uint8)
        self.shape_list = []
        self.type = None
        self.size_ = 1024
        self.color = QColor('white')
        self.icon = cv2.resize(self.shape,(self.size_,self.size_))
        self.initShape()
    
    def initShape(self):
        if self.type is None:
            self.shape = cv2.circle(self.shape, (512,512), 512, self._getBGR(self.color), -1)
            #self.mask = cv2.cvtColor(self.shape,cv2.COLOR_BGRA2GRAY)
        self.icon = cv2.resize(self.shape,(self.size_,self.size_))
        pass
    
    def setColor(self,color):
        self.color = color
        self.initShape()
    
    def setSize(self,size):
        self.size_ = size
        self.initShape()
    
    def changeColorFromBGR(self,BGR):
        b,g,r = BGR
        self.color = QColor(r,g,b)
        #print(self.color.name())
        self.initShape()
    
    def getColor(self):
        return self.color
    
    def _getBGR(self,color):
        return (color.blue(), color.green(), color.red(), 255)
    
    def changeShape(self,type_):
        self.type = type_
        self.initShape()
        pass
    
    def draw(self,img,position):
        if img.shape[2] == 3:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        elif len(img.shape) == 2:
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGRA)
        r = (self.size_+1)//2
        imageROI = img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:]
        tmp_shape = cv2.resize(self.shape,(imageROI.shape[1],imageROI.shape[0]))
        gray = cv2.cvtColor(tmp_shape,cv2.COLOR_RGBA2GRAY)
        ret,mask = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        img1_bg = cv2.bitwise_and(imageROI,imageROI,mask = mask_inv)
        img2_fg = cv2.bitwise_and(tmp_shape,tmp_shape,mask = mask)
        img[position[1] - r:position[1] + r,position[0] - r:position[0] + r,:] = cv2.add(img1_bg,img2_fg)
        return img


class Draw(QLabel):
    """
    The purpose of this class is to present 
    the results to the user, and all operations 
    done on the canvas are received through this class.
    """
    #signal = pyqtSignal([str,tuple,tuple,tuple,int,tuple])
    #signal_ = pyqtSignal([list,int,tuple])
    #drop_signal = pyqtSignal(tuple)
    #fill_signal = pyqtSignal(tuple)
    color_signal = pyqtSignal([int,int,int])
    send_signal = pyqtSignal(dict)
    typechanged = pyqtSignal(dict)
    def __init__(self,debug=False):
        super(Draw,self).__init__()
        self.__debug = debug
        self.setAutoFillBackground(True)
        self.setMouseTracking(False)
        palette = QPalette()
        palette.setBrush(QPalette.Window,QBrush(Qt.Dense7Pattern))
        self.setPalette(palette)
        self._rect = (0,0,0,0)
        self.setAlignment(Qt.AlignCenter)
        self.__scale = 1.0
        self.pos_xy = []
        self.pos_tmp = []
        self.brush = QColor(0,0,0,0)
        self.point_start,self.point_end = (-1,-1),(-1,-1)
        self.pencolor = QColor(0,0,0,255)
        self.thickness = 1
        self.linestyle = Qt.SolidLine
        self.lb_x,self.lb_y,self.lb_w,self.lb_h = 0,0,0,0
        self.flag = False
        self._flag = False
        self.type = None
    
    def setScale(self,scale):
        self.__scale = scale
    
    def __str_to_RGB(self,s):
        # This is a translation fuction from string of hex like to RGB values.
        s = [int(c.upper(),16) for c in s]
        R,G,B = s[0]*16+s[1],s[2]*16+s[3],s[4]*16+s[5]
        return R,G,B
    
    def __str_to_BGR(self,s):
        # This is a translation fuction from string of hex like to BGR values.
        r,g,b = self.__str_to_RGB(s)
        return b,g,r
    
    def getCenterOfCanvas(self):
        # Return the center coordinate of this canvas, 
        # it has been used in coordinate transformation.
        #print(self.width(),self.height())
        return ((self.width()+1)//2,(self.height()+1)//2)
    
    def chgType(self,tp):
        # This function set a flag of the operation that would be done, 
        # and change the status of mouse tracking.
        self.type = tp
        if self.type == 'vary':
            self._flag = True
        else:
            self._flag = False
        self.typechanged.emit({'type':self.type,'content':None})
        '''
        if self.type in ['Line','Rect','Circle']:
            self.setMouseTracking(True)
        else:
            self.setMouseTracking(False)'''
    
    def setImageRect(self,rect):
        self._rect = rect
    
    def redraw(self):
        if self._flag:
            self.repaint()

    def refresh(self, img):
        logger.debug('refresh')
        self.setStyleSheet('QLabel{border:1px solid #c00;}')
        self.setPixmap(ops.cvtCV2PixmapAlpha(img))
    
    def paintEvent(self,event):
        # There overload the paintEvent Function, 
        # different drawing according to different flags,
        # it just shows to the user.
        super().paintEvent(event)
        self.painter = QPainter()
        #self.painter.setRenderHint(QPainter.Antialiasing, True)
        if not self.painter.isActive():
            self.painter.begin(self)
        self.pen = QPen(self.pencolor, self.thickness*self.__scale, self.linestyle)
        self.painter.setPen(self.pen)
        if self.type == 'pencil':
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
        elif self.type == 'line':
            self.painter.drawLine(self.point_start[0],self.point_start[1],
                                  self.point_end[0],self.point_end[1])
        elif self.type == 'rect':
            self.painter.setBrush(self.brush)
            self.painter.drawRect(self.point_start[0],self.point_start[1],
                                  self.point_end[0] - self.point_start[0],
                                  self.point_end[1] - self.point_start[1])
        elif self.type == 'circle':
            self.painter.setBrush(self.brush)
            self.painter.drawEllipse(self.point_start[0],self.point_start[1],
                                  self.point_end[0] - self.point_start[0],
                                  self.point_end[1] - self.point_start[1])
        elif self.type == 'brush':
            pass
        elif self.type == 'vary':
            #print(self._rect)
            #tmp = [self.pencolor, self.thickness, self.linestyle]
            if self._flag:
                self.painter.setPen(QPen(QColor('black'), 1, Qt.SolidLine))
                self.painter.drawRect(*self._rect)
                self.painter.drawRect(self._rect[0] - 3,self._rect[1] - 3,7,7)
                self.painter.drawRect(self._rect[0] + self._rect[2] - 3,self._rect[1] - 3,7,7)
                self.painter.drawRect(self._rect[0] - 3,self._rect[1] + self._rect[3] - 3,7,7)
                self.painter.drawRect(self._rect[0] + self._rect[2] - 3,self._rect[1] + self._rect[3] - 3,7,7)
                self.painter.drawRect(self._rect[0] + self._rect[2]//2 - 3,self._rect[1] - 3,7,7)
                self.painter.drawRect(self._rect[0] - 3,self._rect[1] + self._rect[3]//2 - 3,7,7)
                self.painter.drawRect(self._rect[0] + self._rect[2]//2 - 3,self._rect[1] + self._rect[3] - 3,7,7)
                self.painter.drawRect(self._rect[0] + self._rect[2] - 3,self._rect[1] + self._rect[3]//2 - 3,7,7)
                self.painter.drawEllipse(self._rect[0] + self._rect[2]//2 - 3,self._rect[1] + self._rect[3]//2 - 3,7,7)
                self.painter.drawLine(self._rect[0] + self._rect[2]//2,self._rect[1] + self._rect[3]//2 - 5,self._rect[0] + self._rect[2]//2,self._rect[1] + self._rect[3]//2 + 5)
                self.painter.drawLine(self._rect[0] + self._rect[2]//2 - 5,self._rect[1] + self._rect[3]//2,self._rect[0] + self._rect[2]//2 + 5,self._rect[1] + self._rect[3]//2)
                self.painter.setPen(self.pen)
            #self.painter.drawRect()
        self.painter.end()
        pass
    
    def mousePressEvent(self,event):
        super().mousePressEvent(event)
        self.flag = True
        #print(event.pos())
        if self.type in ['line','rect','circle']:
            self.point_start = self.transform((event.pos().x(), event.pos().y()))
            self.point_end = self.transform((event.pos().x(), event.pos().y()))
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                #self.drop_signal.emit((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':'dropper','position':self.transform((event.pos().x(), event.pos().y()))})
        elif self.type == 'pencil':
            self.pos_xy = []
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                #self.drop_signal.emit((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':self.type,'position':self.transform((event.pos().x(), event.pos().y()))})
        elif self.type == 'dropper':
            #self.drop_signal.emit((event.pos().x(), event.pos().y()))
            self.send_signal.emit({'mode':self.type,'position':self.transform((event.pos().x(), event.pos().y()))})
        elif self.type == 'fill':
            #self.fill_signal.emit((event.pos().x(), event.pos().y(),(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha())))
            self.send_signal.emit({'mode':self.type,'position':self.transform((event.pos().x(), event.pos().y())),'color':(self.__str_to_BGR(self.pencolor.name()[1:]))})
        elif self.type == 'vary':
            self.point_start = self.transform((event.pos().x(), event.pos().y()))
            self.point_end = self.transform((event.pos().x(), event.pos().y()))
            self.typechanged.emit({'type':self.type,'content':self.point_start})
            #self.send_signal.emit({'mode':'Vary','start_position':self.point_start,'end_position':self.point_end,'enter':False})
        elif self.type == 'brush':
            self.send_signal.emit({'mode':self.type,'type':None,'color':(self.__str_to_BGR(self.pencolor.name()[1:])),'size':self.thickness,'position':self.transform((event.pos().x(), event.pos().y())),'is_start':True})
        elif self.type == 'zoom':
            self.send_signal.emit({'mode':self.type,'isplus':True})
        elif self.type == 'move':
            self.point_start = self.transform((event.pos().x(), event.pos().y()))
            self.point_end = self.transform((event.pos().x(), event.pos().y()))
            self.send_signal.emit({'mode':self.type,'start':self.point_start,'end':self.point_end,'enter':False})
    
    def mouseMoveEvent(self,event):
        super().mouseMoveEvent(event)
        if self.flag:
            if self.type in ['line','rect','circle']:
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    if self.type == 'line':
                        self.point_end = self.transform((event.pos().x(),self.point_start[1]))
                    else:
                        tmp = min([int(event.pos().x()/self.__scale) - self.point_start[0],int(event.pos().y()/self.__scale) - self.point_start[1]])
                        self.point_end = (self.point_start[0] + tmp,self.point_start[1]+tmp)
                else:
                    self.point_end = self.transform((event.pos().x(), event.pos().y()))
            elif self.type == 'pencil':
                pos_tmp = self.transform((event.pos().x(), event.pos().y()))
                self.pos_xy.append(pos_tmp)
            elif self.type == 'vary':
                self.point_end = self.transform((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':self.type,'start_position':self.point_start,'end_position':self.point_end,'enter':False})
            elif self.type == 'brush':
                self.send_signal.emit({'mode':self.type,'type':None,'color':(self.__str_to_BGR(self.pencolor.name()[1:])),'size':self.thickness,'position':self.transform((event.pos().x(), event.pos().y())),'is_start':False})
            elif self.type == 'move':
                self.point_end = self.transform((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':self.type,'start':self.point_start,'end':self.point_end,'enter':False})
            self.update()
    
    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event)
        if self.flag:
            if self.type in ['line','rect','circle']:
                self.send_signal.emit({'mode':self.type,'point_start':self.point_start,'point_end':self.point_end,'pen_color':(self.__str_to_BGR(self.pencolor.name()[1:])),'thick':self.thickness,'brush_color':(self.__str_to_BGR(self.brush.name()[1:]))})
                #self.signal.emit(self.type,self.point_start,self.point_end,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()),self.thickness,(self.__str_to_BGR(self.brush.name()[1:]),self.brush.alpha()))
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
            elif self.type == 'pencil':
                self.send_signal.emit({'mode':self.type,'point_list':self.pos_xy,'thick':self.thickness,'color':(self.__str_to_BGR(self.pencolor.name()[1:]))})
                #self.signal_.emit(self.pos_xy,self.thickness,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()))
                pos_test = (-1, -1)
                self.pos_xy.append(pos_test)
                self.pos_xy = []
            elif self.type == 'vary':
                self.send_signal.emit({'mode':self.type,'start_position':self.point_start,'end_position':self.point_end,'enter':True})
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
            elif self.type == 'brush':
                self.send_signal.emit({'mode':self.type,'type':None,'color':(self.__str_to_BGR(self.pencolor.name()[1:])),'size':self.thickness,'position':self.transform((event.pos().x(), event.pos().y())),'is_start':False})
            elif self.type == 'move':
                self.point_end = self.transform((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':self.type,'start':self.point_start,'end':self.point_end,'enter':True})
            
            self.flag = False
            self.update()
            self.cleanAllPoints()
    
    def changePenColor(self, color):
        self.penColor = color
    
    def changePenThickness(self, thickness=10):
        self.thickness = thickness
    
    def cleanAllPoints(self):
        # When the Painter end, clear all points
        self.flag = False
        self.pos_xy = []
        self.pos_tmp = []
        self.point_start = (-1,-1)
        self.point_end = (-1,-1)
    
    def setRealSize(self,w,h):
        self.__width,self.__height = self.width(),self.height()
    
    def transform(self,pos):
        return (int(pos[0]/self.__scale),int(pos[1]/self.__scale))
    
    def transformT(self,pos):
        return (int(pos[0]*self.__scale),int(pos[1]*self.__scale))
    
    def resizeSelf(self,w,h):
        # Reset the size of canvas
        self.resize(w,h)
    
    def changeBlockColor(self,b,g,r):
        # This function used to change pushbutton color which is in the toolbar widget.
        self.color_signal.emit(b,g,r)

class MutiCanvas(QTabWidget):
    """
    This class is to achieve the task of user uses multiple canvas,
    it inherit from QTabWidget, and still being trimmed.
    """
    #changed = pyqtSignal(dict)
    #added = pyqtSignal(dict)
    #deleted = pyqtSignal(dict)
    out_signal = pyqtSignal(dict)
    in_signal = pyqtSignal(dict)
    def __init__(self,parent=None,debug=False):
        super().__init__()
        self.__debug = debug
        self.canvasList = []
        self.setStyleSheet('QTabWidget{background-color:#282828;border:1px solid #424242;padding:0px;margin:0px;}'
                            'QTabBar::tab{width:120px;height:30px;alignment:left;}')
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setAcceptDrops(True)
        self.setContentsMargins(0,0,0,0)
        self.setAutoFillBackground(True)
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.selectCanvas)
        # self.newCanvas()

    def sendMsg(self, content):
        logger.debug('Multiple Canvas request message: '+str(content))
        self.out_signal.emit(content)

    def addCanvas(self,canvas):
        self.canvas = canvas
        self.addTab(self.canvas,self.canvas.canvasName)
        self.canvasList.append(self.canvas)
        #self.added.emit({'mode':'add'})
        self.setCurrentIndex(len(self.canvasList)-1)
        if self.__debug:
            logger.debug('Add canvas:'+self.canvas.canvasName+', total '+str(len(self.canvasList))+' canvas.')
    
    def insertCanvas(self,canvas,idx):
        self.canvas = canvas
        self.canvasList.insert(idx,self.canvas)
        self.insertTab(idx,self.canvas,self.canvas.canvasName)
        #self.added.emit({'mode':'insert','index':idx})
        self.setCurrentIndex(idx)
        if self.__debug:
            logger.debug('Insert canvas:'+self.canvas.canvasName+', index:'+str(idx)+', total '+str(len(self.canvasList))+' canvas.')
    
    def newCanvas(self):
        self.canvas = Canvas(parent=self,debug=self.__debug)
        self.canvas.out_signal[dict].connect(self.sendMsg)
        self.canvasList.append(self.canvas)
        self.addTab(self.canvas,self.canvas.canvasName)
        #self.added.emit({'mode':'new'})
        self.setCurrentIndex(len(self.canvasList)-1)
        if self.__debug:
            logger.debug('New canvas:'+self.canvas.canvasName+', total '+str(len(self.canvasList))+' canvas.')
            logger.debug('Current index:'+str(self.currentCanvasIndex())+', length of list:'+str(len(self.canvasList)))
    
    def currentCanvas(self):
        return self.currentWidget()
    
    def currentCanvasIndex(self):
        return self.currentIndex()
    
    def selectCanvas(self):
        if self.__debug:
            logger.debug('Select canvas index:'+str(self.currentCanvasIndex()))
        self.canvas = self.canvasList[self.currentCanvasIndex()]
        # self.out_signal.emit({'type':'refresh'})
        #self.changed.emit({'mode':'change','index':self.currentCanvasIndex()})
    
    def delCanvas(self):
        idx = self.currentCanvasIndex()
        if self.count() == 1:
            self.removeTab(idx)
            self.canvasList.pop(idx)
        elif idx < self.count() - 1:
            self.canvas = self.canvasList[idx+1]
            self.removeTab(idx)
            self.canvasList.pop(idx)
            self.setCurrentIndex(idx)
        else:
            self.canvas = self.canvasList[idx-1]
            self.removeTab(idx)
            self.canvasList.pop(idx)
            self.setCurrentIndex(idx-1)
        #self.deleted.emit({'mode':'delete','index':idx})
        if self.__debug:
            logger.debug('Delete Canvas index:'+str(idx)+'total '+str(len(self.canvasList))+' canvas.')

class CanvasScroll(QScrollArea):
    signal = pyqtSignal(dict)
    def __init__(self,debug=False):
        self.__debug = debug
        super().__init__()
        self._rect = (0,0,0,0)
        self._clicked = False
        self.content_scale = 1.0
        self.last_scale = 1.0
        self.disX, self.disY = 0,0
        self.currentPosition = ((self.width()+1)//2,(self.height()+1)//2)
        self.setContentsMargins(50,50,50,50)
        self.start_pos = (-1,-1)
        self.end_pos = (-1,-1)
        self.is_show = False
        self.hor = self.horizontalScrollBar()
        self.ver = self.verticalScrollBar()
    
    def draw(self,rect):
        self._rect = rect
    
    def showRect(self):
        self.is_show = True
    
    def notShowRect(self):
        self.is_show = False
    
    def setContentScale(self,scale):
        self.last_scale = self.content_scale
        self.content_scale = scale
        
    def getCenterPosition(self):
        return (self.width()//2, self.height()//2)
    
    def getDistance(self,pos1,pos2):
        return (pos2[0] - pos1[0], pos2[1] - pos1[1])
    
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if not self._clicked:
            self.currentPosition = (self.width(),self.height())
        else:
            self._clicked = False
        centerX,centerY = self.getCenterPosition()
        margin = int(50*self.content_scale)
        self.setContentsMargins(margin,margin,margin,margin)
        if self.__debug:
            logger.debug(str(centerX)+','+str(centerY)+','+str(self.disX)+','+str(self.disY)+','+str(self.content_scale)+','+str(self.last_scale))
            logger.debug(str(centerX + int(self.disX*self.content_scale/self.last_scale))+','+str(centerY + int(self.disY*self.content_scale/self.last_scale)))
        self.ensureVisible(*self.getCenterPosition())
        '''
    def mousePressEvent(self,event):
        super().mousePressEvent(event)
        self.currentPosition = (event.pos().x(),event.pos().y())
        self.disX,self.disY = self.getDistance(self.getCenterPosition(),self.currentPosition)
        self.start_pos = (event.pos().x(), event.pos().y())
        self.end_pos = (event.pos().x(), event.pos().y())
        self.hVal = self.hor.value()
        self.vVal = self.ver.value()
        if self.__debug:
            logger.debug(str(event.pos().x())+','+str(event.pos().y())+','+str(self.getCenterPosition()))
        self._clicked = True
    
    def mouseMoveEvent(self,event):
        super().mouseMoveEvent(event)
        self.end_pos = (event.pos().x(), event.pos().y())
        self.hor.setValue(self.hVal - self.end_pos[0] + self.start_pos[0])
        self.ver.setValue(self.vVal - self.end_pos[1] + self.start_pos[1])
    
    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event)
        self.end_pos = (event.pos().x(), event.pos().y())
        self.hor.setValue(self.hVal - self.end_pos[0] + self.start_pos[0])
        self.ver.setValue(self.vVal - self.end_pos[1] + self.start_pos[1])
        '''
    def paintEvent(self,event):
        # There overload the paintEvent Function, 
        # different drawing according to different flags,
        # it just shows to the user.
        super().paintEvent(event)
        if self.is_show:
            self.painter = QPainter(self.viewport())
            #self.painter.setRenderHint(QPainter.Antialiasing, True)
            if not self.painter.isActive():
                self.painter.begin(self)
            self.pen = QPen(QColor('black'), 1, Qt.SolidLine)
            self.painter.setPen(self.pen)
            #print(self._rect)
            w, h = self._rect[2] - self._rect[0], self._rect[3] - self._rect[1]
            self.painter.drawRect(self._rect[0],self._rect[1],w,h)
            self.painter.drawRect(self._rect[0] - 3,self._rect[1] - 3,7,7)
            self.painter.drawRect(self._rect[2] - 3,self._rect[1] - 3,7,7)
            self.painter.drawRect(self._rect[0] - 3,self._rect[3] - 3,7,7)
            self.painter.drawRect(self._rect[2] - 3,self._rect[3] - 3,7,7)
            self.painter.drawRect((self._rect[0] + self._rect[2])//2 - 3,self._rect[1] - 3,7,7)
            self.painter.drawRect(self._rect[0] - 3,(self._rect[1] + self._rect[3])//2 - 3,7,7)
            self.painter.drawRect((self._rect[0] + self._rect[2])//2 - 3,self._rect[3] - 3,7,7)
            self.painter.drawRect(self._rect[2] - 3,(self._rect[1] + self._rect[3])//2 - 3,7,7)
            self.painter.drawEllipse((self._rect[0] + self._rect[2])//2 - 3,(self._rect[1] + self._rect[3])//2 - 3,7,7)
            self.painter.drawLine((self._rect[0] + self._rect[2])//2,(self._rect[1] + self._rect[3])//2 - 5,(self._rect[0] + self._rect[2])//2,(self._rect[1] + self._rect[3])//2 + 5)
            self.painter.drawLine((self._rect[0] + self._rect[2])//2 - 5,(self._rect[1] + self._rect[3])//2,(self._rect[0] + self._rect[2])//2 + 5,(self._rect[1] + self._rect[3])//2)
            self.painter.end()

class Canvas(QWidget):
    """
    This is a drawing board class in which the data structure of the layer is connected.
    """
    out_signal = pyqtSignal(dict)
    in_signal = pyqtSignal(dict)
    signal = pyqtSignal()
    changeRow = pyqtSignal(int)
    def __init__(self,parent=None,debug=False):
        super().__init__()
        self.__debug = debug
        self.parent = parent
        self.setMinimumSize(250, 300)
        self.setStyleSheet("background-color:#282828;border:0px;padding:0px;margin:0px;")
        self.draw = Draw(debug=self.__debug)
        self.canvasName = 'Untitled-1'
        self.layer_idx = 0
        self._flag = False
        self.scale = 100.0
        self.center_point = ((self.width()+1)//2, (self.height()+1)//2)
        self.brush = Brush()
        self.scroll = CanvasScroll(debug=self.__debug)
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.draw)
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.setContentsMargins(0,0,0,0)
        self.vbox.addWidget(self.scroll)
        self.setLayout(self.vbox)
        self.draw.send_signal[dict].connect(self.taskDistribution)
        self.draw.typechanged[dict].connect(self.toolsInit)
        self.in_signal[dict].connect(self.doMsg)

    def doMsg(self, content):
        logger.debug('Canvas request message: '+str(content))
        if content['type'] == 'resize':
            self.brush.resize(*content['data'])
        elif content['type'] == 'getRect':
            x1,y1,x2,y2 = content['data']['rect']
            self._rect = self.getPosition((x1,y1))+self.getPosition((x2,y2))
            self.draw.setImageRect((x1,y1,x2-x1,y2-y1))
            self.draw.repaint()
            self.scroll.draw(self._rect)
            self.scroll.repaint()
        else:
            layer = content['data']['layer']
            self.draw.resize(layer.width(),layer.height())
            self.draw.refresh(layer.image)
        pass

    def getCenterPoint(self):
        return ((self.scroll.width()+1)//2, (self.scroll.height()+1)//2)
    
    def getPosition(self,pos):
        #print(self.getCenterPoint(), self.draw.getCenterOfCanvas())
        x,y = self.getCenterPoint()[0] - self.draw.getCenterOfCanvas()[0] + pos[0], self.getCenterPoint()[1] - self.draw.getCenterOfCanvas()[1] + pos[1]
        return (x,y)
    
    def movement(self,start,end,enter):
        disX,disY = end[0] - start[0], end[1] - start[1]
        hVal = self.scroll.hor.value()
        vVal = self.scroll.ver.value()
        self.scroll.hor.setValue(hVal - disX)
        self.scroll.ver.setValue(vVal - disY)
        if not enter:
            self.scroll.hor.setValue(hVal)
            self.scroll.ver.setValue(vVal)
    
    def toolsInit(self,content):
        if self.__debug:
            logger.debug('Tool inital: ' + str(content))
        _type = content['type']
        self.scroll.notShowRect()
        self.scroll.repaint()
        if _type == 'vary':
            self.scroll.showRect()
            # if content['content'] is not None:
            #     self.changeRow.emit(self.layers.autoSelectClickedLayer(content['content']))
            self.out_signal.emit({'data':{},'type':'getRect','togo':'layer'})
            # x1,y1,x2,y2 = self.layers.getRectOfImage()
            # self._rect = self.getPosition((x1,y1))+self.getPosition((x2,y2))
            # self.draw.setImageRect((x1,y1,x2-x1,y2-y1))
            # self.draw.repaint()
            # self.scroll.draw(self._rect)
            # self.scroll.repaint()
        elif _type == 'move':
            pass
        elif _type == 'brush':
            self.brush.setSize(self.draw.thickness)
        self.chgCursor(_type)
    
    def taskDistribution(self,content):
        if self.__debug:
            logger.debug('Content:'+str(content))
        self.out_signal.emit(content)

        # mode = content['mode']
        # if mode in ['Line','Rect','Circle']:
        #     self.draw_2Pix(mode,content['point_start'],content['point_end'],content['pen_color'],content['thick'],content['brush_color'])
        # elif mode == 'Pencil':
        #     self.draw_NPix(content['point_list'],content['thick'],content['color'])
        # elif mode == 'Dropper':
        #     self.dropColor(content['position'])
        # elif mode == 'Fill':
        #     self.fillColor(content['position'],content['color'])
        # elif mode == 'Vary':
        #     x1,y1,x2,y2 = self.layers.getRectOfImage()
        #     self._rect = self.getPosition((x1,y1))+self.getPosition((x2,y2))
        #     self.draw.setImageRect((x1,y1,x2-x1,y2-y1))
        #     self.scroll.draw(self._rect)
        #     self.scroll.repaint()
        #     self.varyImage(content['start_position'],content['end_position'],content['enter'])
        # elif mode == 'Brush':
        #     self.brushDraw(content['position'],content['type'],content['color'],content['size'],content['is_start'])
        # elif mode == 'Zoom':
        #     self.zoom(content['isplus'])
        # elif mode == 'Move':
        #     self.movement(content['start'],content['end'],content['enter'])
        # else:
        #     return
    
    def zoom(self,isplus):
        if isplus:
            if int(self.scale) >= 100:
                self.scale = min(self.scale + 100,1000)
            else:
                self.scale = min(self.scale*2,100)
        else:
            if int(self.scale) >= 200:
                self.scale -= 100
            elif int(self.scale) > 100:
                self.scale = 100.0
            else:
                self.scale -= 0.5*self.scale
        self.draw.setScale(self.scale/100.0)
        self.scroll.setContentScale(self.scale/100.0)
        self.imgOperate()
    
    def varyImage(self,start,end,enter):
        last = self.layers.layer[self.layer_idx].getPositionOnCanvas()
        self.layers.layer[self.layer_idx].setPositionOnCanvasByDistance((end[0] - start[0], end[1] - start[1]))
        self.layers.updateImg()
        if not enter:
            self.layers.layer[self.layer_idx].setPositionOnCanvas(last)
        else:
            self.layers.layer[self.layer_idx].setOffset((end[0] - start[0], end[1] - start[1]))
        pass
    
    def BezierCurve(self,p1,p2,p3,p4):
        t = np.linspace(0,1,5)
        res = (p1*(1-t)**3)+(3*p2*t*(1-t)**2)+(3*p3*(1-t)*t**2)+(p4*t**3)
        return res
    
    def brushDraw(self,pos,type_,color,size,is_start):
        pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        if is_start:
            if type_ is not None:
                self.brush.changeShape(type_)
            self.brush.changeColorFromBGR(color)
            self.brush.setSize(size)
            self.tmp_pos = pos
            self.layers.tmp_img = self.brush.draw(self.layers.tmp_img, pos)
            return
        point_list = self._get_points(pos)
        for point in point_list:
            self.layers.tmp_img = self.brush.draw(self.layers.tmp_img, point)
        self.layers.layer[self.layer_idx].changeImg(self.layers.tmp_img)
        self.layers.updateImg()
        self.tmp_pos = pos
        pass
    
    def _get_points(self, pos):
        """ Get all points between last_point ~ now_point. """
        points = [self.tmp_pos]
        len_x = pos[0] - self.tmp_pos[0]
        len_y = pos[1] - self.tmp_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        if length == 0: return points
        step_x = len_x / length
        step_y = len_y / length
        for i in range(int(length)):
            points.append((points[-1][0] + step_x, points[-1][1] + step_y))
        points = map(lambda x:(int(0.5+x[0]), int(0.5+x[1])), points)
        # return light-weight, uniq list
        return list(set(points))
    
    def chgLayerImage(self,idx):
        self.layer_idx = idx
    
    def draw_2Pix(self,mode,start,end,pencolor,thick,brush):
        #print(mode,start,end,pencolor,thick,brush)
        imgObj = self.layers.layer[self.layer_idx]
        start = ops.cvtCanPosAndLayerPos(start,(0,0),imgObj.getCenterOfImage(),self.draw.getCenterOfCanvas(),imgObj.offset)
        end = ops.cvtCanPosAndLayerPos(end,(0,0),imgObj.getCenterOfImage(),self.draw.getCenterOfCanvas(),imgObj.offset)
        #print(start,end)
        if mode == 'Line':
            cv2.line(self.layers.tmp_img,start,end,pencolor,thick)
        elif mode == 'Rect':
            if brush[-1] != 0:
                cv2.rectangle(self.layers.tmp_img,start,end,brush,-1)
            cv2.rectangle(self.layers.tmp_img,start,end,pencolor,thick)
        elif mode == 'Circle':
            if brush[-1] != 0:
                cv2.ellipse(self.layers.tmp_img,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,brush,-1)
            cv2.ellipse(self.layers.tmp_img,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,pencolor,thick)
        #self.layers.tmp_img = 
        imgObj.changeImg(self.layers.tmp_img)
        self.layers.updateImg()
        pass
    
    def dropColor(self,pos):
        #pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        if self.layers.mask[pos[1],pos[0]] == 0:
            return
        [b,g,r,_] = self.layers.Image[pos[1],pos[0]]
        self.draw.changeBlockColor(b,g,r)
        
    def fillColor(self,pos,color,r=50):
        #print(pos)
        if self.__debug:
            logger.debug('Position:'+str(pos)+', color:'+str(color)+', r:'+str(r))
        imgObj = self.layers.layer[self.layer_idx]
        (x,y) = ops.cvtCanPosAndLayerPos((pos[0],pos[1]),(0,0),imgObj.getCenterOfImage(),self.draw.getCenterOfCanvas(),imgObj.offset)
        if self.layers.isPositionOutOfLayer((x,y)):
            return
        [b,g,r,_] = self.layers.tmp_img[y,x]
        h,w = self.layers.tmp_img.shape[:2]
        mask=np.zeros([h+2,w+2],np.uint8)
        tmp = cv2.cvtColor(self.layers.tmp_img,cv2.COLOR_BGRA2BGR)
        cv2.floodFill(tmp,mask,(x,y),color,(50,50,50),(50,50,50),cv2.FLOODFILL_FIXED_RANGE)
        tmp = cv2.cvtColor(tmp,cv2.COLOR_BGR2BGRA)
        tmp[:,:,3] = self.layers.tmp_img[:,:,3]
        self.layers.tmp_img = tmp
        imgObj.changeImg(self.layers.tmp_img)
        self.layers.updateImg()
    
    def draw_NPix(self,pos_list,thick,color):
        imgObj = self.layers.layer[self.layer_idx]
        if pos_list:
            tmp = ops.cvtCanPosAndLayerPos(pos_list[0],(0,0),imgObj.getCenterOfImage(),self.draw.getCenterOfCanvas(),imgObj.offset)
            for pos in pos_list:
                pos = ops.cvtCanPosAndLayerPos(pos,(0,0),imgObj.getCenterOfImage(),self.draw.getCenterOfCanvas(),imgObj.offset)
                cv2.line(self.layers.tmp_img,tmp,pos,color[0],thick)
                tmp = pos
                #cv2.circle(self.layers.tmp_img,pos,thick,color[0],-1)
            imgObj.changeImg(self.layers.tmp_img)
            self.layers.updateImg()
        pass
    
    def imgOperate(self):
        '''
        tmp = cv2.cvtColor(self.layers.Image,cv2.COLOR_BGR2BGRA)
        if self.layers.getNum() == 1:
            tmp[:,:,3] = self.layers.mask
        self.draw.setPixmap(ops.cvtCV2PixmapAlpha(tmp))
        '''
        def getResultImage(img,background,mask):
            mask_inv = cv2.bitwise_not(mask)
            fg = cv2.bitwise_and(img,img,mask = mask)
            bg = cv2.bitwise_and(background,background,mask = mask_inv)
            return cv2.add(fg,bg)
        tmp = cv2.resize(self.layers.Image,
                         (0,0),fx=self.scale/100, fy=self.scale/100,
                         interpolation=cv2.INTER_NEAREST)
        mask = cv2.resize(self.layers.mask,
                          (0,0),fx=self.scale/100, fy=self.scale/100,
                         interpolation=cv2.INTER_NEAREST)
        self.layers.resetBackground(int(self.layers.width()*(self.scale//100)),int(self.layers.height()*(self.scale//100)))
        self.draw.resize(self.layers.width()*(self.scale//100),self.layers.height()*(self.scale//100))
        tmp = getResultImage(tmp,self.layers.background,mask)
        if tmp.shape[2] == 3:
            tmp = cv2.cvtColor(tmp,cv2.COLOR_BGR2BGRA)
        self.draw.setPixmap(ops.cvtCV2PixmapAlpha(tmp))
        # cv2.imwrite('./tmp_layer.jpg',self.layers.Image)
        self.signal.emit()
        pass
    
    def chgCursor(self,tar=None):
        if tar in ['pencil','line','rect','circle']:
            self.setCursor(Qt.CrossCursor)
        elif tar == 'dropper':
            self.setCursor(QCursor(QPixmap('./static/UI/dropper.png'),0,31))
        elif tar == 'fill':
            self.setCursor(QCursor(QPixmap('./static/UI/fill-drip.png'),0,0))
        elif tar == 'brush':
            self.setCursor(QCursor(ops.cvtCV2PixmapAlpha(self.brush.icon)))
        elif tar == 'vary':
            self.setCursor(Qt.SizeAllCursor)
        elif tar == 'move':
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def imgResize(self):
        rd = ResizeDialog('Canvas',self.layers.ImgInfo)
        if rd.exec_() == QDialog.Accepted:
            settings = utils.readTempIni()
            w = int(settings["width"])
            h = int(settings["height"])
            self.layers.reset(w,h)
            self.draw.resizeSelf(w,h)
            self.signal.emit()
        rd.close()
        pass
    
    def canResize(self):
        rd = ResizeDialog('Canvas',self.layers.ImgInfo)
        if rd.exec_() == QDialog.Accepted:
            settings = utils.readTempIni()
            w = int(settings["width"])
            h = int(settings["height"])
            self.layers.resize(w,h)
            self.draw.resizeSelf(w,h)
            self.signal.emit()
        rd.close()
        pass