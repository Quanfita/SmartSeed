# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 14:08:49 2019

@author: quanfita

This is the interface code that interacts with the user, 
and each part is a component of the main interface.
"""

from functools import singledispatch
import sys
import cv2
import numpy as np
import ops
import logger
from PIL import Image
from Basic import comp,light,hue,custom
from ImgObj import LayerStack
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QScrollArea,QDialog,
                             QSlider, QVBoxLayout, QPushButton, QColorDialog,
                             QLineEdit,QTabWidget,QHBoxLayout,QComboBox,
                             QListWidget,QListWidgetItem,QMenu,QAction,QGroupBox,
                             QToolBox, QListView,QToolButton,QFileDialog,
                             QInputDialog, QMessageBox,QAbstractItemView)
from PyQt5.QtGui import (QPainter, QPen, QColor, QGuiApplication,QPixmap,
                         QIcon,QPalette,QBrush,QRegExpValidator,QCursor,
                         QConicalGradient,QLinearGradient,QFont,QImage,QDrag)
from PyQt5.QtCore import (Qt,pyqtSignal,QRegExp,QItemSelectionModel,pyqtSlot,
                          QRectF,QSettings,QPoint,QMimeData,QSize,QObject)

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
    
    def __init__(self,debug=False):
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
        self.pencolor = QColor(0,0,0,255)
        self.thickness = 1
        self.linestyle = Qt.SolidLine
        self.lb_x,self.lb_y,self.lb_w,self.lb_h = 0,0,0,0
        #self.OS = stack
        #self.super_img = img
        self.flag = False
        #self.fig = fig
        self.type = None
    
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
        return ((self.width()+1)//2,(self.height()+1)//2)
    
    def chgType(self,tp):
        # This function set a flag of the operation that would be done, 
        # and change the status of mouse tracking.
        self.type = tp
        if self.type in ['Line','Rect','Circle']:
            self.setMouseTracking(True)
        else:
            self.setMouseTracking(False)
    
    def paintEvent(self,event):
        # There overload the paintEvent Function, 
        # different drawing according to different flags,
        # it just shows to the user.
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
        #print(event.pos())
        if self.type in ['Line','Rect','Circle']:
            self.point_start = (event.pos().x(), event.pos().y())
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                #self.drop_signal.emit((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':'Dropper','position':(event.pos().x(), event.pos().y())})
        elif self.type == 'Pencil':
            self.pos_xy = []
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                #self.drop_signal.emit((event.pos().x(), event.pos().y()))
                self.send_signal.emit({'mode':'Dropper','position':(event.pos().x(), event.pos().y())})
        elif self.type == 'Dropper':
            #self.drop_signal.emit((event.pos().x(), event.pos().y()))
            self.send_signal.emit({'mode':'Dropper','position':(event.pos().x(), event.pos().y())})
        elif self.type == 'Fill':
            #self.fill_signal.emit((event.pos().x(), event.pos().y(),(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha())))
            self.send_signal.emit({'mode':'Fill','position':(event.pos().x(), event.pos().y()),'color':(self.__str_to_BGR(self.pencolor.name()[1:]))})
        elif self.type == 'Vary':
            self.point_start = (event.pos().x(), event.pos().y())
            self.point_end = (event.pos().x(), event.pos().y())
            self.send_signal.emit({'mode':'Vary','start_position':self.point_start,'end_position':self.point_end,'enter':False})
    
    def mouseMoveEvent(self,event):
        if self.flag:
            if self.type in ['Line','Rect','Circle']:
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    if self.type == 'Line':
                        self.point_end = (event.pos().x(),self.point_start[1])
                    else:
                        tmp = min([event.pos().x() - self.point_start[0],event.pos().y() - self.point_start[1]])
                        self.point_end = (self.point_start[0] + tmp,self.point_start[1]+tmp)
                else:
                    self.point_end = (event.pos().x(), event.pos().y())
            elif self.type == 'Pencil':
                pos_tmp = (event.pos().x(), event.pos().y())
                self.pos_xy.append(pos_tmp)
            elif self.type == 'Vary':
                self.point_end = (event.pos().x(), event.pos().y())
                self.send_signal.emit({'mode':'Vary','start_position':self.point_start,'end_position':self.point_end,'enter':False})
            self.update()
    
    def mouseReleaseEvent(self,event):
        if self.flag:
            if self.type in ['Line','Rect','Circle']:
                self.send_signal.emit({'mode':self.type,'point_start':self.point_start,'point_end':self.point_end,'pen_color':(self.__str_to_BGR(self.pencolor.name()[1:])),'thick':self.thickness,'brush_color':(self.__str_to_BGR(self.brush.name()[1:]))})
                #self.signal.emit(self.type,self.point_start,self.point_end,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()),self.thickness,(self.__str_to_BGR(self.brush.name()[1:]),self.brush.alpha()))
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
            elif self.type == 'Pencil':
                self.send_signal.emit({'mode':self.type,'point_list':self.pos_xy,'thick':self.thickness,'color':(self.__str_to_BGR(self.pencolor.name()[1:]))})
                #self.signal_.emit(self.pos_xy,self.thickness,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()))
                pos_test = (-1, -1)
                self.pos_xy.append(pos_test)
                self.pos_xy = []
            elif self.type == 'Vary':
                self.send_signal.emit({'mode':'Vary','start_position':self.point_start,'end_position':self.point_end,'enter':True})
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
    
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
    
    def resizeSelf(self,w,h):
        # Reset the size of canvas
        self.resize(w,h)
    
    def changeBlockColor(self,b,g,r):
        # This function used to change pushbutton color which is in the toolbar widget.
        self.color_signal.emit(b,g,r)

class AdjBlock(QWidget):
    """
    This class is a common widget,
    it is used to set the Attributes of pencil or shapes.
    """
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

class MutiCanvas(QTabWidget):
    """
    This class is to achieve the task of user uses multiple canvas,
    it inherit from QTabWidget, and still being trimmed.
    """
    #changed = pyqtSignal(dict)
    #added = pyqtSignal(dict)
    #deleted = pyqtSignal(dict)
    refresh = pyqtSignal()
    def __init__(self,debug=False):
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
        self.newCanvas()
    
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
        self.canvas = Canvas(debug=self.__debug)
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
        self.refresh.emit()
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
        

class Canvas(QWidget):
    """
    This is a drawing board class in which the data structure of the layer is connected.
    """
    signal = pyqtSignal()
    def __init__(self,debug=False):
        super().__init__()
        self.__debug = debug
        self.setMinimumSize(250, 300)
        self.setStyleSheet("background-color:#282828;border:0px;padding:0px;margin:0px;")
        self.draw = Draw(debug=self.__debug)
        self.canvasName = 'Untitled - 1'
        self.layer_idx = 0
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.draw)
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        if settings.value('mode') == 1:
            img = cv2.imread(settings.value('imagePath'))
            self.canvasName = settings.value('imageName')
            self.layers = LayerStack(img,debug=self.__debug)
            self.layers.setName(self.canvasName)
        else:
            self.layers = LayerStack(debug=self.__debug)
            self.layers.setName(self.canvasName)
        self.dpi = int(settings.value('dpi'))
        self.draw.resize(*self.layers.ImgInfo())
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        self.setLayout(self.vbox)
        #self.draw.signal[str,tuple,tuple,tuple,int,tuple].connect(self.draw_2Pix)
        #self.draw.signal_[list,int,tuple].connect(self.draw_NPix)
        self.layers.signal.connect(self.imgOperate)
        self.layers.layNum_signal[int].connect(self.chgLayerImage)
        self.layers.changeImg(self.layers.Image)
        self.draw.send_signal[dict].connect(self.taskDistribution)
        #self.draw.drop_signal[tuple].connect(self.dropColor)
        #self.draw.fill_signal[tuple].connect(self.fillColor)
    
    def taskDistribution(self,content):
        mode = content['mode']
        if mode in ['Line','Rect','Circle']:
            self.draw_2Pix(mode,content['point_start'],content['point_end'],content['pen_color'],content['thick'],content['brush_color'])
        elif mode == 'Pencil':
            self.draw_NPix(content['point_list'],content['thick'],content['color'])
        elif mode == 'Dropper':
            self.dropColor(content['position'])
        elif mode == 'Fill':
            self.fillColor(content['position'],content['color'])
        elif mode == 'Vary':
            self.varyImage(content['start_position'],content['end_position'],content['enter'])
        else:
            return
    
    def varyImage(self,start,end,enter):
        last = self.layers.layer[self.layer_idx].getPositionOnCanvas()
        self.layers.layer[self.layer_idx].setPositionOnCanvasByDistance((end[0] - start[0], end[1] - start[1]))
        self.layers.updateImg()
        if not enter:
            self.layers.layer[self.layer_idx].setPositionOnCanvas(last)
        pass
    
    def chgLayerImage(self,idx):
        self.layer_idx = idx
    
    def draw_2Pix(self,mode,start,end,pencolor,thick,brush):
        #print(mode,start,end,pencolor,thick,brush)
        start = ops.cvtCanPosAndLayerPos(start,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        end = ops.cvtCanPosAndLayerPos(end,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
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
        self.layers.layer[self.layer_idx].changeImg(self.layers.tmp_img)
        self.layers.updateImg()
        pass
    
    def dropColor(self,pos):
        #pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        [b,g,r] = self.layers.Image[pos[1],pos[0]]
        self.draw.changeBlockColor(b,g,r)
        
    def fillColor(self,pos,color,r=50):
        #print(pos)
        if self.__debug:
            logger.debug('Position:'+str(pos)+', color:'+str(color)+', r:'+str(r))
        (x,y) = ops.cvtCanPosAndLayerPos((pos[0],pos[1]),(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        if self.layers.isPositionOutOfLayer((x,y)):
            return
        [b,g,r] = self.layers.tmp_img[y,x]
        h,w = self.layers.tmp_img.shape[:2]
        mask=np.zeros([h+2,w+2],np.uint8)
        cv2.floodFill(self.layers.tmp_img,mask,(x,y),color,(50,50,50),(50,50,50),cv2.FLOODFILL_FIXED_RANGE)
        self.layers.layer[self.layer_idx].changeImg(self.layers.tmp_img)
        self.layers.updateImg()
    
    def draw_NPix(self,pos_list,thick,color):
        if pos_list:
            tmp = ops.cvtCanPosAndLayerPos(pos_list[0],(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
            for pos in pos_list:
                pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
                cv2.line(self.layers.tmp_img,tmp,pos,color[0],thick)
                tmp = pos
                #cv2.circle(self.layers.tmp_img,pos,thick,color[0],-1)
            self.layers.layer[self.layer_idx].changeImg(self.layers.tmp_img)
            self.layers.updateImg()
        pass
    
    def imgOperate(self):
        self.draw.setPixmap(ops.cvtCV2Pixmap(self.layers.Image))
        #cv2.imwrite('./tmp_layer.jpg',self.layers.Image)
        self.signal.emit()
        pass
    
    def chgCursor(self,tar=None):
        if tar in ['Pencil','Line','Rect','Circle']:
            self.setCursor(Qt.CrossCursor)
        elif tar == 'Dropper':
            self.setCursor(QCursor(QPixmap('./UI/dropper.png'),0,31))
        elif tar == 'Fill':
            self.setCursor(QCursor(QPixmap('./UI/fill-drip.png'),0,0))
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def imgResize(self):
        rd = ResizeDialog('Canvas',self.layers.ImgInfo)
        if rd.exec_() == QDialog.Accepted:
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            try:
                w = eval(settings.value("width"))
                h = eval(settings.value("height"))
            except TypeError:
                w = settings.value("width")
                h = settings.value("height")
            self.layers.reset(w,h)
            self.draw.resizeSelf(w,h)
            self.signal.emit()
        rd.close()
        pass
    
    def canResize(self):
        rd = ResizeDialog('Canvas',self.layers.ImgInfo)
        if rd.exec_() == QDialog.Accepted:
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            try:
                w = eval(settings.value("width"))
                h = eval(settings.value("height"))
            except TypeError:
                w = settings.value("width")
                h = settings.value("height")
            self.layers.resize(w,h)
            self.draw.resizeSelf(w,h)
            self.signal.emit()
        rd.close()
        pass

class ResizeDialog(QDialog):
    """
    This is the dialog of resize canvas.
    """
    def __init__(self,tar,sizeFun):
        super().__init__()
        self.target = tar
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640,480)
        self.setWindowTitle('Resize '+self.target)
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        self.canvas_width, self.canvas_height = sizeFun()
        
        self.w_lb = QLabel('width:',self)
        self.w_lb.setAlignment(Qt.AlignLeft)
        self.w_lb.setGeometry(180,120,80,20)
        
        self.h_lb = QLabel('height:',self)
        self.h_lb.setAlignment(Qt.AlignLeft)
        self.h_lb.setGeometry(180,200,80,20)
        
        self.w_line = QLineEdit(self)
        self.w_line.installEventFilter(self)
        self.w_line.setGeometry(180,150,50,30)
        self.w_line.setPlaceholderText('512')
        
        self.h_line = QLineEdit(self)
        self.h_line.installEventFilter(self)
        self.h_line.setGeometry(180,230,50,30)
        self.h_line.setPlaceholderText('512')
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(350,400,80,30)
        self.ok_btn.setFocus(True)
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.turnBack)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(250,400,80,30)
        self.cancel_btn.clicked.connect(self.close)
        
        regx = QRegExp("^[1-9][0-9]{3}$")
        validator_w = QRegExpValidator(regx, self.w_line)
        validator_h = QRegExpValidator(regx, self.h_line)
        self.w_line.setValidator(validator_w)
        self.h_line.setValidator(validator_h)
        
        self.show()
        
    def turnBack(self):
        if self.w_line.text() != '' and self.h_line.text()!='':
            self.canvas_width = int(self.w_line.text())
            self.canvas_height = int(self.h_line.text())
        elif self.w_line.text() != '':
            self.canvas_width = int(self.w_line.text())
        elif self.h_line.text()!='':
            self.canvas_height = int(self.h_line.text())
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue("width",self.canvas_width)
        settings.setValue("height", self.canvas_height)
        '''
        logger.info('Create new canvas as '+str(self.canvas_color)+
                    ' with '+str(self.canvas_width)+'x'+str(self.canvas_height))'''
        self.accept()

class ColorConical(QWidget):
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
    front_signal = pyqtSignal(str)
    back_signal = pyqtSignal(str)
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
        self.front_signal.emit(color.name())
    
    def changeBackColor(self,color):
        self.backButton.setStyleSheet("QPushButton{border:1px solid #cdcdcd;background-color:"+str(color.name())+";}")
        self.back_signal.emit(color.name())
    
    def __setFrontColor(self):
        col = QColorDialog.getColor()
        self.changeFrontColor(col)
        
    def __setBackColor(self):
        col = QColorDialog.getColor()
        self.changeBackColor(col)

class ColorLinear(QWidget):
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
        b,g,r = cv2.split(img)
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

class Welcome(QDialog):
    """
    This is the welcome view of the app, 
    user would choose to open image or new a canvas.
    """
    def __init__(self,debug=False):
        super(Welcome,self).__init__()
        self.__debug = debug
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.canvas_color = '#FFFFFF'
        self.canvas_width = 512
        self.canvas_height = 512
        self.canvas_dpi = 72
        self.resize(360, 480)
        self.setFixedSize(360, 480)
        self.setWindowTitle('New Canvas')
        self.setStyleSheet("QDialog{background-color:#535353;}")
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        
        self.main_lb = QLabel('New Canvas',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(80,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        self.main_lb.setStyleSheet("color:white;");
        
        self.new_title = QLabel('File Name',self)
        self.new_title.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.new_title.setGeometry(60,80,100,25)
        self.new_title.setStyleSheet("color:white;");
        
        self.title_name = QLineEdit(self)
        self.title_name.installEventFilter(self)
        self.title_name.setGeometry(60,110,100,25)
        self.title_name.setStyleSheet("color:white;background-color:#434343;border:0px;")
        self.title_name.setPlaceholderText('Untitled-1')
        
        self.w_lb = QLabel('Width:',self)
        self.w_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.w_lb.setGeometry(60,140,80,25)
        self.w_lb.setStyleSheet("color:white;");
        
        self.h_lb = QLabel('Height:',self)
        self.h_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.h_lb.setGeometry(60,200,80,25)
        self.h_lb.setStyleSheet("color:white;")
        
        self.w_line = QLineEdit(self)
        self.w_line.installEventFilter(self)
        self.w_line.setGeometry(60,170,50,25)
        self.w_line.setPlaceholderText('512')
        self.w_line.textEdited[str].connect(self.countWidthPix)
        self.w_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.h_line = QLineEdit(self)
        self.h_line.installEventFilter(self)
        self.h_line.setGeometry(60,230,50,25)
        self.h_line.setPlaceholderText('512')
        self.h_line.textEdited[str].connect(self.countHeightPix)
        self.h_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.dpi_lb = QLabel('DPI:',self)
        self.dpi_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.dpi_lb.setGeometry(60,260,80,25)
        self.dpi_lb.setStyleSheet("color:white;")
        
        self.dpi_line = QLineEdit(self)
        self.dpi_line.installEventFilter(self)
        self.dpi_line.setGeometry(60,290,50,25)
        self.dpi_line.setPlaceholderText('72')
        self.dpi_line.textEdited[str].connect(self.countPix)
        self.dpi_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.color_lb = QLabel('BackGround Content:',self)
        self.color_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.color_lb.setGeometry(60,320,150,25)
        self.color_lb.setStyleSheet("color:white;");
        
        pix_info = ['px/inch','px/cm']
        self.dpi_combox = QComboBox(self)
        self.dpi_combox.addItems(pix_info)
        self.dpi_combox.setGeometry(140,290,100,25)
        self.dpi_combox.activated[str].connect(self.selectDpiMode)
        self.dpi_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        pix_info = ['px','cm','inch']
        self.pix_combox = QComboBox(self)
        self.pix_combox.addItems(pix_info)
        self.pix_combox.setGeometry(140,170,100,25)
        self.pix_combox.activated[str].connect(self.selectPix)
        self.pix_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        self.color_btn = QPushButton(self)
        self.color_btn.setGeometry(230,350,25,25)
        self.color_btn.setStyleSheet("QPushButton{background-color:white}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.color_btn.clicked.connect(self.changeColor)
        
        color_info = ['White','Black','Background Color']
        self.color_combox = QComboBox(self)
        self.color_combox.addItems(color_info)
        self.color_combox.setGeometry(60,350,150,25)
        self.color_combox.activated[str].connect(self.selectColor)
        self.color_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(220,410,80,30)
        self.ok_btn.setFocus(True)
        self.ok_btn.setDefault(True)
        self.ok_btn.setStyleSheet("QPushButton{color:white;background-color:#1473e6;border-radius:15px;}"
                                    'QPushButton:focus{color:white;background-color:#1473e6;border:0px;}'
                                    'QPushButton:hover{color:white;background-color:#0f64d2;border:0px;}')
        self.ok_btn.clicked.connect(self.turnBack)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(100,410,80,30)
        self.cancel_btn.setStyleSheet("QPushButton{color:white;background-color:#434343;border:2px solid white;border-radius:15px;}"
                                    'QPushButton:focus{color:white;background-color:#1473e6;border:0px;}'
                                    'QPushButton:hover{color:#656565;background-color:#cdcdcd;border:0px;}')
        self.cancel_btn.clicked.connect(self.close)
        
        self.open_btn = QPushButton('Open File',self)
        self.open_btn.setGeometry(180,110,80,25)
        self.open_btn.setStyleSheet("color:white;background-color:#434343;border:1px;")
        self.open_btn.clicked.connect(self.openimage)
        
        regx = QRegExp("^[1-9][0-9]{3}$")
        validator_w = QRegExpValidator(regx, self.w_line)
        validator_h = QRegExpValidator(regx, self.h_line)
        validator_dpi = QRegExpValidator(regx, self.dpi_line)
        self.w_line.setValidator(validator_w)
        self.h_line.setValidator(validator_h)
        self.dpi_line.setValidator(validator_dpi)
        
        self.show()
    
    def selectDpiMode(self,text):
        # To set the dpi unit.
        if self.dpi_combox.currentText() == 'px/inch':
            self.dpi_line.setText(str(self.canvas_dpi))
        elif self.dpi_combox.currentText() == 'px/cm':
            self.dpi_line.setText(str(round(self.canvas_dpi/2.54,2)))
        else:
            pass
    
    def countPix(self,text):
        # To count the pixel number of width and height for canvas. 
        if self.dpi_combox.currentText() == 'px/inch':
            if text != '':
                self.canvas_dpi = int(text)
            self.selectPix(self.pix_combox.currentText())
        elif self.dpi_combox.currentText() == 'px/cm':
            if text != '':
                self.canvas_dpi = int(float(text)*2.54)
            self.selectPix(self.pix_combox.currentText())
        else:
            pass
    
    def countWidthPix(self,text):
        # To count the pixel number of width for canvas.
        if self.pix_combox.currentText() == 'px':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text()))
        elif self.pix_combox.currentText() == 'cm':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text())*self.canvas_dpi/2.54)
        elif self.pix_combox.currentText() == 'inch':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text())*self.canvas_dpi)
        else:
            pass
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
    
    def countHeightPix(self,text):
        # To count the pixel number of height for canvas.
        if self.pix_combox.currentText() == 'px':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text()))
        elif self.pix_combox.currentText() == 'cm':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text())*self.canvas_dpi/2.54)
        elif self.pix_combox.currentText() == 'inch':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text())*self.canvas_dpi)
        else:
            pass
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
    
    def changeColor(self):
        # To set background color of canvas.
        color = QColorDialog.getColor()
        self.color_combox.setCurrentText('Background Color')
        self.color_btn.setStyleSheet("QPushButton{background-color:"+str(color.name())+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.canvas_color = color.name()
    
    def selectColor(self,text):
        # To set background color of canvas with perset.
        if text in ['White','Black','white','black']:
            self.color_btn.setStyleSheet("QPushButton{background-color:"+str(text)+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
            self.canvas_color = QColor(text).name()
    
    def selectPix(self,text):
        # To calculate  the pixel number of canvas with different unit.
        if self.dpi_combox.currentText() == 'px/cm':
            tmp_dpi = self.canvas_dpi/2.54
        else:
            tmp_dpi = self.canvas_dpi
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
        if text == 'px':
            self.w_line.setText(str(int(self.canvas_width)))
            self.h_line.setText(str(int(self.canvas_height)))
        elif text == 'cm':
            self.w_line.setText(str(round(self.canvas_width/tmp_dpi*2.54,2)))
            self.h_line.setText(str(round(self.canvas_height/tmp_dpi*2.54,2)))
        elif text == 'inch':
            self.w_line.setText(str(round(self.canvas_width/tmp_dpi,2)))
            self.h_line.setText(str(round(self.canvas_height/tmp_dpi,2)))
    
    def callBack(self):
        # This is a callback function.
        return self.canvas_color,self.canvas_width,self.canvas_height,self.canvas_dpi
    
    def turnBack(self):
        # save the arguements to tmp.ini, and close this dialog.
        #self.info = self.callBack()
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue('mode',0)
        settings.setValue("width",self.canvas_width)
        settings.setValue("height", self.canvas_height)
        settings.setValue("color", self.canvas_color)
        settings.setValue('dpi',self.canvas_dpi)
        #settings.setValue('dpiMode',self.dpi_combox.currentText())
        settings.setValue("imagePath",None)
        settings.setValue("imageName",self.title_name.text())
        logger.info('Create new canvas as '+str(self.canvas_color)+
                    ' with '+str(self.canvas_width)+'x'+str(self.canvas_height))
        self.accept()
        
    def openimage(self):
        # If user want to open a image, this function would be done.
        # It can read the image and get some information, 
        # and save these information into tmp.ini.
        imgName,imgType = QFileDialog.getOpenFileName(self,"打开图片","",
                                                     " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if imgName is '':
            logger.warning('None Image has been selected!')
            return
        else:
            #img = cv2.imread(imgName)
            im = Image.open(imgName)
            logger.info('Open image: '+imgName+', '+str(im.format)+str(im.size)+str(im.mode)+str(im.info))
            try:
                self.canvas_dpi = im.info['dpi'][0]
            except:
                self.canvas_dpi = 72
            self.canvas_width, self.canvas_height = im.size
            #self.canvas_dpi = int(self.dpi_line.text())
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            settings.setValue('mode',1)
            settings.setValue("width",self.canvas_width)
            settings.setValue("height", self.canvas_height)
            settings.setValue("color", self.canvas_color)
            settings.setValue('dpi',self.canvas_dpi)
            settings.setValue('imageMode',im.mode)
            settings.setValue('imageFormat',im.format)
            settings.setValue("imagePath",imgName)
            settings.setValue("imageName",imgName.split('/')[-1])
            del im
        self.accept()

class ListWidget(QListWidget):
    """
    This is layer list widget, it based on QListWidget, 
    and it has add, delete, move, copy and select functions.
    """
    signal = pyqtSignal()
    drag_signal = pyqtSignal([int,int])
    map_listwidget = []
    def __init__(self,debug=False):
        super().__init__()
        self.__debug = debug
        #self.Data_init()
        self.list_names = []
        self.Ui_init()
        self.show()
    
    def Data_init(self,icon,randname='Layer1'):
        #self.list_names = [randname]
        settings = QSettings('tmp.ini',QSettings.IniFormat)
        if settings.value('imageName'):
            randname = settings.value('imageName')
        item = QListWidgetItem()
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setText(randname)
        item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        item.setIcon(icon)
        self.addItem(item)
        
    def Ui_init(self):
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setIconSize(QSize(60,40))
        self.setStyleSheet("QListWidget{border:1px solid #cdcdcd; color:white; background:transparent;}"
                        "QListWidget::Item{padding-top:5px; padding-bottom:5px; border:1px solid #cdcdcd;}"
                        "QListWidget::Item:hover{background:skyblue; }"
                        "QListWidget::item:selected:!active{border-width:0px; background:#cdcdcd; }"
                        )
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.connect(self.getListitems)
        self.itemDoubleClicked[QListWidgetItem].connect(self.rename)
    
    def mousePressEvent(self,event):
        QListWidget.mousePressEvent(self,event)
        self.setCurrentItem(self.itemAt(event.pos()))
        self.start_pos = event.pos()
        if self.__debug:
            logger.debug('start position:'+str(self.start_pos))
        
    def mouseMoveEvent(self,event):
        QListWidget.mouseMoveEvent(self,event)
        item = QListWidgetItem(self.currentItem())
        mimeData = QMimeData()
        mimeData.setText(item.text())
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec(Qt.MoveAction)
    
    def mouseReleaseEvent(self,event):
        self.end_pos = event.pos()
        item = self.itemAt(self.start_pos)
        self.insertItem(self.row(self.itemAt(self.end_pos))+1,item)
        self.setCurrentItem(self.itemAt(self.end_pos))
    
    def dragEnterEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def dragMoveEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()
        
    def dropEvent(self,event):
        self.end_pos = event.pos()
        if self.__debug:
            logger.debug('end drop position:'+str(self.end_pos)+',row:'+str(self.row(self.itemAt(self.end_pos))))
        item = self.takeItem(self.row(self.itemAt(self.start_pos)))
        #self.removeItemWidget(self.itemAt(self.start_pos))
        if self.row(self.itemAt(self.end_pos)) == -1:
            self.addItem(item)
            self.drag_signal.emit(self.row(self.itemAt(self.start_pos)),self.count()-1)
        else:
            self.insertItem(self.row(self.itemAt(self.end_pos)),item)
            self.drag_signal.emit(self.row(self.itemAt(self.start_pos)),self.row(self.itemAt(self.end_pos)))
        self.setCurrentItem(item)
        event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def getListitems(self):
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
            if self.__debug:
                logger.debug('Function name:'+str(f.f_code.co_name)+', '+str(f.f_lineno))
        if f.f_lineno != 1367:self.signal.emit()
        return self.selectedItems()

    def contextMenuEvent(self, event):
        hitIndex = self.indexAt(event.pos()).column()
        if hitIndex > -1:
            pmenu = QMenu(self)
            pDeleteAct = QAction("Delete",pmenu)
            pmenu.addAction(pDeleteAct)
            pDeleteAct.triggered.connect(self.deleteItemSlot)
            if self is self.find('Default'):
                pAddItem = QAction("Add Layer",pmenu)
                pmenu.addAction(pAddItem)     
                pAddItem.triggered.connect(self.addItemSlot)
            if len(self.map_listwidget) > 1:
                pSubMenu = QMenu("Move to" ,pmenu)
                pmenu.addMenu(pSubMenu)
                for item_dic in self.map_listwidget:
                    if item_dic['listwidget'] is not self:
                        pMoveAct = QAction(item_dic['groupname'] ,pmenu)
                        pSubMenu.addAction(pMoveAct)
                        pMoveAct.triggered.connect(self.move)
            pmenu.popup(self.mapToGlobal(event.pos()))
    
    def deleteItemSlot(self):
        dellist = self.getListitems()
        for delitem in dellist:
            self.list_names.pop(self.row(delitem))
            del_item = self.takeItem(self.row(delitem))
            del del_item 
    
    def addItemSlot(self,icon,ind=0,newname='Untitled'):
        newitem = QListWidgetItem()
        font = QFont()
        font.setPointSize(10)
        newitem.setFont(font)
        newitem.setText(newname)
        newitem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        newitem.setIcon(QIcon(icon))
        self.list_names.insert(ind,newname)
        #self.addItem(newitem)
        self.insertItem(ind,newitem)
    
    def setListMap(self, listwidget):
        self.map_listwidget.append(listwidget)
    
    def move(self):
        tolistwidget = self.find(self.sender().text())
        movelist = self.getListitems()
        for moveitem in movelist:
            pItem = self.takeItem(self.row(moveitem))
            tolistwidget.addItem(pItem)
    
    def find(self, pmenuname):
        for item_dic in self.map_listwidget:
            if item_dic['groupname'] == pmenuname:
                return item_dic['listwidget']
    
    def rename(self):
        while True:
            newname = QInputDialog.getText(self, "Please Input New Name", "")
            if newname[0] != '' and newname[1] == True:
                self.currentItem().setText(newname[0])
                break
            elif newname[1] == False:
                break
            else:
                QMessageBox.warning(self, 'Warning',
                                    "Name is Null, please input Name", QMessageBox.Yes)
                continue

class LayerBox(QToolBox):
    """
    """
    def __init__(self,debug=False):
        super().__init__()
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(200,100)
        pListWidget = ListWidget()
        dic_list = {'listwidget':pListWidget, 'groupname':"Default"}
        pListWidget.setListMap(dic_list)
        self.addItem(pListWidget, "Default") 
        #self.show()
    
    def contextMenuEvent(self, event):
        pmenu = QMenu(self)
        pAddGroupAct = QAction("Add Group", pmenu)
        pmenu.addAction(pAddGroupAct) 
        pAddGroupAct.triggered.connect(self.addGroupSlot)  
        pmenu.popup(self.mapToGlobal(event.pos()))
    
    def addGroupSlot(self):
        groupname = QInputDialog.getText(self, "Please Input Group Name", "")
        if groupname[0] and groupname[1]: 
            pListWidget1 = ListWidget()
            self.addItem(pListWidget1, groupname[0])
            dic_list = {'listwidget':pListWidget1, 'groupname':groupname[0]}
            pListWidget1.setListMap(dic_list)
        elif groupname[0] == '' and groupname[1]:
            QMessageBox.warning(self, "Warning", "Please Input Group Name")

class LinkedCanvasAndLayers(QObject):
    """
    """
    refresh = pyqtSignal()
    def __init__(self,canvas,layers,debug=False):
        self.__debug = debug
        self.__layers = layers
        self.__canvas = canvas
        self.__layers.signal[dict].connect(self.requestSignal)
        self.__canvas.changed[dict].connect(self.requestSignal)
        self.__canvas.added[dict].connect(self.requestSignal)
        self.__canvas.deleted[dict].connect(self.requestSignal)
    
    def requestSignal(self,content):
        if content['mode'] in ['add','new']:
            self.__layers.addLayerStack(self.__canvas.canvas)
        elif content['mode'] == 'delete':
            self.__layers.removeLayerStack(self.__canvas.currentCanvasIndex())
        pass

class LayerMain(QWidget):
    """
    This class is an main component of layer widget, 
    it can change mixed functions for each layer, 
    and it can also set opacity for each layer.
    """
    signal = pyqtSignal(dict)
    refresh = pyqtSignal()
    def __init__(self,tabCanvas,debug=False):
        super().__init__()
        self.__debug = debug
        self.setStyleSheet('color:white;background-color:#535353;')
        self.tab_canvas = tabCanvas
        self.currentIndex = 0
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setSpacing(0)
        self.lay.setAlignment(Qt.AlignCenter)
        self.layer_list = ListWidget(debug=self.__debug)
        self.layer_list.setStyleSheet('QListWidget{color:white;background-color:#535353;border:1px solid #282828;}')
        #self.layer_list.Data_init(QIcon(ops.cvtCV2Pixmap(cv2.copyMakeBorder(cv2.resize(self.tab_canvas.canvas.layers.Image,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200]))))
        self.initWithLayerStack()
        self.toolsBox = QGroupBox(self)
        self.toolsBox.setStyleSheet("QGroupBox{background-color:#535353;border:1px solid #282828;padding-left,padding-right:5px;padding-top,padding-bottom:2px;margin:0px;}"
                                    "QToolButton{background: transparent;border:none}")
        self.adjBox = QGroupBox(self)
        self.adjBox.setStyleSheet("QGroupBox{background-color:#535353;padding-left,padding-right:5px;padding-top,padding-bottom:2px;border:1px solid #282828;}")
        self.adjLayout = QHBoxLayout()
        #self.adjLayout.setContentsMargins(0,0,0,0)
        self.toolsLayout = QHBoxLayout()
        #self.toolsLayout.setContentsMargins(0,0,0,0)
        self.toolsLayout.setAlignment(Qt.AlignRight)
        self.opacity_lb = QLabel('Opacity:',self)
        self.opacity_lb.resize(50,30)
        self.opacity_val = QLineEdit(self)
        self.opacity_val.installEventFilter(self)
        self.opacity_val.resize(30,30)
        self.opacity_val.setStyleSheet('QLineEdit{color:white;border:1px solid #cdcdcd;border-radius:2px;}')
        self.opacity_val.setPlaceholderText('100%')
        mix_info = ['Normal','Screen','Multiply','Overlay','SoftLight',
                    'HardLight','LinearAdd','ColorBurn','LinearBurn',
                    'ColorDodge','LinearDodge','LighterColor','VividLight',
                    'LinearLight','PinLight','HardMix','Difference','Exclusion',
                    'Subtract','Divide','Hue']
        self.mix_combox = QComboBox(self)
        self.mix_combox.addItems(mix_info)
        self.mix_combox.resize(60,30)
        self.mix_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}'
            'QToolTip{color:white;background-color:#535353;}')
        self.adjLayout.addWidget(self.mix_combox)
        self.adjLayout.addWidget(self.opacity_lb)
        self.adjLayout.addWidget(self.opacity_val)
        self.adjBox.setLayout(self.adjLayout)
        self.lay.addWidget(self.adjBox)
        self.mix_combox.activated[str].connect(self.select)
        self.lay.addWidget(self.layer_list)
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(270,300)
        self.setMaximumSize(300,500)
        self.del_btn = QToolButton(self)
        self.new_btn = QToolButton(self)
        self.cpy_btn = QToolButton(self)
        self.grp_btn = QToolButton(self)
        self.adj_btn = QToolButton(self)
        self.mask_btn = QToolButton(self)
        self.del_btn.resize(30,30)
        self.new_btn.resize(30,30)
        self.cpy_btn.resize(30,30)
        self.grp_btn.resize(30,30)
        self.adj_btn.resize(30,30)
        self.mask_btn.resize(30,30)
        self.del_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.new_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.cpy_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.grp_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.adj_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.mask_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.del_btn.setToolTip('Delete this layer')
        self.new_btn.setToolTip('New a layer')
        self.cpy_btn.setToolTip('Copy this layer')
        self.grp_btn.setToolTip('New a group')
        self.adj_btn.setToolTip('New a adjustment layer')
        self.mask_btn.setToolTip('Add a mask')
        self.del_btn.setIcon(QIcon('./UI/trash.svg'))
        self.new_btn.setIcon(QIcon('./UI/sticky-note.svg'))
        self.cpy_btn.setIcon(QIcon('./UI/copy.svg'))
        self.grp_btn.setIcon(QIcon('./UI/folder.svg'))
        self.adj_btn.setIcon(QIcon('./UI/adjust.svg'))
        self.mask_btn.setIcon(QIcon('./UI/mask.svg'))
        #self.new_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        #self.cpy_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        #self.del_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        self.del_btn.clicked.connect(self.delLayer)
        self.new_btn.clicked.connect(self.newLayer)
        self.cpy_btn.clicked.connect(self.cpyLayer)
        self.grp_btn.clicked.connect(self.group)
        self.adj_btn.clicked.connect(self.adjLayer)
        self.mask_btn.clicked.connect(self.addMask)
        self.toolsLayout.addWidget(self.mask_btn)
        self.toolsLayout.addWidget(self.adj_btn)
        self.toolsLayout.addWidget(self.grp_btn)
        self.toolsLayout.addWidget(self.cpy_btn)
        self.toolsLayout.addWidget(self.new_btn)
        self.toolsLayout.addWidget(self.del_btn)
        
        self.toolsBox.setLayout(self.toolsLayout)
        self.lay.addWidget(self.toolsBox)
        self.setLayout(self.lay)
        self.layer_list.signal.connect(self.sltLayer)
        self.layer_list.setCurrentRow(0)
        self.layer_list.drag_signal[int,int].connect(self.chgLayer)
        self.tab_canvas.canvas.layers.signal.connect(self.refreshLayerIcon)
        self.tab_canvas.refresh.connect(self.initWithLayerStack)
        self.show()
    '''
    def check(self):
        layers = self.tab_canvas.canvas.layers.layer_names
        if self.__debug:
            logger.debug('Layerlist count:'+str(self.layer_list.count())+', layers count:'+str(len(layers)))
        assert self.layer_list.count() == len(layers), 'ListWidget count is different from layers count.'
        for i in range(self.layer_list.count()):
            if self.__debug:
                logger.debug('listwidget name:'+self.layer_list.item(i).text()+', layer name:'+layers[-i])
            assert self.layer_list.item(i).text() == layers[-i], 'layer name is different.'
    
    def setCurrentLayerStack(self,idx):
        try:
            self.tab_canvas.canvas.layers = self.stack_list[idx]
            self.currentIndex = idx
            self.initWithLayerStack()
        except Exception as e:
            logger.error('There is an error when set current layerstack:'+str(e))
    
    def currentLayerStack(self):
        return self.currentIndex
    
    def addLayerStack(self,stack):
        if self.__debug:
            logger.debug('Add layerstack.')
        try:
            self.stack_list.append(stack)
            self.setCurrentLayerStack(len(self.stack_list)-1)
        except Exception as e:
            logger.error('There is an error when add a layerstack:'+str(e))
    
    def removeLayerStack(self,idx):
        if self.__debug:
            logger.debug('Remove layerstack.')
        try:
            self.stack_list.pop(idx)
            self.setCurrentLayerStack(idx if idx < len(self.stack_list) else idx - 1)
    '''
    def group(self):
        pass
    
    def adjLayer(self):
        pass
    
    def addMask(self):
        pass
    
    def initWithLayerStack(self):
        self.layer_list.clear()
        for item in self.tab_canvas.canvas.layers.layer[::-1]:
            try:
                font = QFont()
                font.setPointSize(10)
                tmp_item = QListWidgetItem(self.layer_list)
                tmp_item.setIcon(QIcon(item.getIcon()))
                tmp_item.setFont(font)
                if item.getLayerName() == '':
                    item.setLayerName('layer-1')
                tmp_item.setText(item.getLayerName())
                tmp_item.setTextAlignment(Qt.AlignCenter)
                #self.layer_list.addItem(tmp_item)
                #self.check()
            except Exception as e:
                logger.error('There is an error when initial with layerstack:'+str(e))
                break
        lsize = len(self.tab_canvas.canvas.layers.layer)
        if self.__debug:
            logger.debug('Set current row:'+str(lsize - self.tab_canvas.canvas.layers.selectedLayerIndex - 1))
        self.layer_list.setCurrentRow(lsize - self.tab_canvas.canvas.layers.selectedLayerIndex - 1)
        pass
    
    def chgLayer(self,start,end):
        lsize = len(self.layer_list)
        if self.__debug:
            logger.debug('Change layer from '+str(start)+' to '+str(end)+', total '+str(lsize)+' layers.')
        self.tab_canvas.canvas.layers.exchgLayer(lsize - start - 1,lsize - end - 1)
        pass
    
    def newLayer(self):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        while True:
            newname = QInputDialog.getText(self, "Please Input Name", "")
            if newname[0] in self.layer_list.list_names:
                reply = QMessageBox.warning(self, 'Message',
                "This name is already used in previous layers, please change another one!", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    continue
                else:
                    break
            elif newname[0] == '':
                break
            else:
                self.layer_list.addItemSlot(QIcon(QBrush(Qt.Dense7Pattern)),ind,newname[0])
                self.tab_canvas.canvas.layers.addLayer(lsize - ind,newname[0])
                self.refresh.emit()
                break
        pass
    
    def refreshLayerIcon(self):
        try:
            cur = self.layer_list.currentItem()
            ind = self.layer_list.row(cur)
            lsize = len(self.layer_list)
            if self.__debug:
                logger.debug('current item:'+str(cur)+', index:'+str(ind)+', total length:'+str(lsize))
            cur.setIcon(QIcon(self.tab_canvas.canvas.layers.layer[lsize - ind - 1].getIcon()))
        except Exception as e:
            logger.error('There is an error:'+str(e))
    
    def addLayer(self,img,name):
        if self.layer_list.count() == 0:
            ind = 0
        else:
            cur = self.layer_list.currentItem()
            ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        try:
            self.tab_canvas.canvas.layers.addLayer(lsize - ind,name,img)
            if self.__debug:
                logger.debug('Add Layer to:'+str(lsize-ind)+', view index:'+str(ind)+', name:'+name+', total '+str(len(self.tab_canvas.canvas.layers.layer))+' layers.')
                logger.debug([x.getLayerName() for x in self.tab_canvas.canvas.layers.layer])
            self.layer_list.addItemSlot(QIcon(self.tab_canvas.canvas.layers.layer[lsize - ind].getIcon()),ind,name)
            self.layer_list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
            self.refresh.emit()
        except Exception as e:
            logger.error('There is an error:'+str(e))
        pass
    
    def delLayer(self):
        if not self.layer_list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to delete this layer?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
    
            if reply == QMessageBox.Yes:
                cur = self.layer_list.currentItem()
                ind = self.layer_list.row(cur)
                lsize = len(self.layer_list)
                self.layer_list.deleteItemSlot()
                self.tab_canvas.canvas.layers.delLayer(lsize - ind - 1)
                self.layer_list.setCurrentRow(ind-1,QItemSelectionModel.ClearAndSelect)
                self.refresh.emit()
        pass
    
    def cpyLayer(self):
        if not self.layer_list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            cur = self.layer_list.currentItem()
            ind = self.layer_list.row(cur)
            name = self.layer_list.list_names[ind] + '-copy'
            i = 0
            while True:
                if name in self.layer_list.list_names:
                    name = name + '_' + str(i)
                    continue
                else:
                    break
            self.layer_list.addItemSlot(ind,name)
            self.tab_canvas.canvas.layers.cpyLayer(ind,name)
            self.layer_list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
            self.refresh.emit()
        pass
    
    def sltLayer(self):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        
        #print(self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1])
        try:
            if self.__debug:
                logger.debug('Select layer index:'+str(lsize-ind-1)+', lsize:'+str(lsize)+', ind:'+str(ind))
            self.mix_combox.setCurrentText(self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1])
            self.tab_canvas.canvas.layers.sltLayer(lsize - ind - 1)
            if ind  == lsize - 1:
                self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1] = 'Normal'
                self.mix_combox.setCurrentText('Normal')
                self.mix_combox.setEnabled(False)
                self.opacity_val.setEnabled(False)
            else:
                self.mix_combox.setEnabled(True)
                self.opacity_val.setEnabled(True)
        except Exception as e:
            logger.error('There is an error:'+str(e))
        pass
    
    def select(self,s):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        #print(lsize,ind,lsize - ind - 1)
        self.tab_canvas.canvas.layers.setMix(lsize - ind - 1,s)
        #self.refresh.emit()
        pass

class AdjDialog(QDialog):
    """
    The adjustment dialog of image adjustment.
    """
    def __init__(self,img,tar,debug=False):
        super(AdjDialog,self).__init__()
        self.setStyleSheet('QDialog{color:white;background-color:#535353;}'
                            "QPushButton{color:white;background-color:#434343;border:2px solid white;border-radius:15px;}"
                            'QPushButton:focus{color:white;background-color:#1473e6;border:1px;}'
                            'QPushButton:hover{color:#656565;background-color:#cdcdcd;border:1px;}'
                            'QLabel{color:white;}')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640, 480)
        self.setFixedSize(640, 480)
        self.setWindowTitle('Adjustment')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        self.__img = img
        self.__tmp_img = np.copy(self.__img.Image)
        self.img_h,self.img_w = self.__img.height,self.__img.width
        self.__target = tar

        self.main_lb = QLabel('Adjustment',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(self.width()//2 - 100,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        
        self.lb = QLabel('Values: 0',self)
        self.lb.setAlignment(Qt.AlignLeft)
        self.lb.setGeometry(3*self.width()//5 + 10,120,100,30)
        
        self.imgShow = QLabel('',self)
        self.imgShow.setAlignment(Qt.AlignCenter)
        self.imgShow.setGeometry(30,100,350,350)
        '''
        self.__tmp_img = cv2.resize(self.__tmp_img,(400,
                                        self.img_h*400//self.img_w) if self.img_w >= self.img_h else (self.img_w*400//self.img_h,400))
        '''
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
        
        self.sl = QSlider(Qt.Horizontal,self)
        #self.sl.resize(30,100)
        self.sl.setGeometry(3*self.width()//5 + 10,150,200,30)
        if self.__target == 'light':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'comp':
            self.sl.setMinimum(-30)
            self.sl.setMaximum(50)
        elif self.__target == 'custom':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'hue':
            self.sl.setMinimum(-180)
            self.sl.setMaximum(180)
        else:
            pass
        self.sl.setTickPosition(QSlider.TicksAbove) 
        
        self.sl.valueChanged[int].connect(self.setValue)
        #self.sl.sliderReleased.connect(self.change)
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(550,430,80,30)
        self.ok_btn.clicked.connect(self.saveImage)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(450,430,80,30)
        self.cancel_btn.clicked.connect(self.close)
        
        self.show()
    
    def setTar(self,tar):
        self.__target = tar
    
    def setValue(self,value):
        self.sl.setValue(value)
        self.lb.setText('Value: '+str(value))
        self.change()
        pass
    
    def change(self):
        if self.__target == 'light':
            self.__tmp_img = light(self.__img.Image,self.sl.value())
        elif self.__target == 'comp':
            comp(self.__img.Image,self.sl.value())
            self.__tmp_img = cv2.imread('./tmp/comp.jpg')
        elif self.__target == 'custom':
            self.__tmp_img = custom(self.__img.Image,self.sl.value())
        elif self.__target == 'hue':
            self.__tmp_img = hue(self.__img.Image,self.sl.value())
        else:
            return
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
    
    def saveImage(self):
        self.__img.changeImg(self.__tmp_img)
        self.accept()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #pyqt_learn = Draw()
    pyqt_learn = Canvas()
    pyqt_learn.show()
    app.exec_()