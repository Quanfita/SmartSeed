# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:14:25 2019

@author: Quanfita
"""

import sys
import cv2
import ops
from ImgObj import LayerStack
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QScrollArea,QDialog,
                             QSlider, QVBoxLayout, QPushButton, QColorDialog,
                             QLineEdit,QTabWidget,QHBoxLayout)
from PyQt5.QtGui import (QPainter, QPen, QColor, QGuiApplication,QPixmap,
                         QIcon,QPalette,QBrush,QRegExpValidator,QCursor)
from PyQt5.QtCore import Qt,pyqtSignal,QRegExp,QSettings

class Draw(QLabel):
    signal = pyqtSignal([str,tuple,tuple,tuple,int,tuple])
    signal_ = pyqtSignal([list,int,tuple])
    drop_signal = pyqtSignal(tuple)
    color_signal = pyqtSignal([int,int,int])
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
        s = [int(c.upper(),16) for c in s]
        R,G,B = s[0]*16+s[1],s[2]*16+s[3],s[4]*16+s[5]
        return R,G,B
    
    def __str_to_BGR(self,s):
        r,g,b = self.__str_to_RGB(s)
        return b,g,r
    
    def getCenterOfCanvas(self):
        return ((self.width()+1)//2,(self.height()+1)//2)
    
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
        print(event.pos())
        if self.type in ['Line','Rect','Circle']:
            self.point_start = (event.pos().x(), event.pos().y())
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                self.drop_signal.emit((event.pos().x(), event.pos().y()))
        elif self.type == 'Pencil':
            self.pos_xy = []
            if QApplication.keyboardModifiers() == Qt.AltModifier:
                self.drop_signal.emit((event.pos().x(), event.pos().y()))
        elif self.type == 'Dropper':
            self.drop_signal.emit((event.pos().x(), event.pos().y()))
    
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
            self.update()
    
    def mouseReleaseEvent(self,event):
        if self.flag:
            if self.type in ['Line','Rect','Circle']:
                self.signal.emit(self.type,self.point_start,self.point_end,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()),self.thickness,(self.__str_to_BGR(self.brush.name()[1:]),self.brush.alpha()))
                self.point_start = (-1,-1)
                self.point_end = (-1,-1)
            elif self.type == 'Pencil':
                self.signal_.emit(self.pos_xy,self.thickness,(self.__str_to_BGR(self.pencolor.name()[1:]),self.pencolor.alpha()))
                pos_test = (-1, -1)
                self.pos_xy.append(pos_test)
                self.pos_xy = []
    
            self.flag = False
            self.update()
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
    
    def resizeSelf(self,w,h):
        self.resize(w,h)
    
    def changeBlockColor(self,b,g,r):
        self.color_signal.emit(b,g,r)

class AdjBlock(QWidget):
    def __init__(self,pencil):
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
        self.pencil.color_signal[int,int,int].connect(self.setColor)
        #self.color_sl.valueChanged[int].connect(self.setColor)
        self.thick_sl.valueChanged[int].connect(self.setThick)
        self.show()
    
    def setColor(self,b,g,r):
        col = QColor(r,g,b)
        self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
                                     "QPushButton{border:1px solid #cdcdcd;}")
        #self.color_lb.setText('Color: '+col.name())
        self.pencil.ChangePenColor(col)
        pass
    
    def setThick(self,value):
        self.thick_sl.setValue(value)
        #self.thick_lb.setText('Tickness: '+str(value))
        self.pencil.ChangePenThickness(value)
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

# =============================================================================
# class AdjBlock(QWidget):
#     def __init__(self,pencil):
#         super(AdjBlock,self).__init__()
#         self.pencil = pencil
#         self.main_layout = QVBoxLayout()
#         if self.pencil.type in ['Rect','Circle']:
#             self.color_lb = QLabel('Border Color',self)
#             self.fill_lb = QLabel('Fill Color',self)
#             self.fill_lb.setAlignment(Qt.AlignLeft)
#             self.fill_btn = QPushButton('',self)
#             self.fill_btn.setStyleSheet("QPushButton{background-color:black}"
#                                         "QPushButton{border-radius:5px}"
#                                         "QPushButton{border:1px}")
#             self.fill_btn.clicked.connect(self.fillColor)
#         else:
#             self.color_lb = QLabel('Color',self)
#         self.color_lb.setAlignment(Qt.AlignLeft)
# 
#         self.color_btn = QPushButton('',self)
#         self.color_btn.setStyleSheet("QPushButton{background-color:black}"
#                                      "QPushButton{border-radius:5px}"
#                                      "QPushButton{border:1px}")
#         self.color_btn.clicked.connect(self.chooseColor)
#         
#         self.thick_lb = QLabel('Thickness',self)
#         self.thick_lb.setAlignment(Qt.AlignLeft)
#         
#         self.thick_sl = QSlider(Qt.Horizontal,self)
#         self.thick_sl.resize(30,100)
#         self.thick_sl.setMinimum(1)
#         self.thick_sl.setMaximum(10)
#         self.thick_sl.setTickInterval(1)
#         self.thick_sl.setTickPosition(QSlider.TicksAbove)
#         
#         self.main_layout.addWidget(self.color_lb)
#         #self.main_layout.addWidget(self.color_sl)
#         self.main_layout.addWidget(self.color_btn)
#         self.main_layout.addWidget(self.thick_lb)
#         self.main_layout.addWidget(self.thick_sl)
#         if self.pencil.type in ['Rect','Circle']:
#             self.main_layout.addWidget(self.fill_lb)
#             self.main_layout.addWidget(self.fill_btn)
#         
#         self.setLayout(self.main_layout)
#         self.pencil.color_signal[int,int,int].connect(self.setColor)
#         #self.color_sl.valueChanged[int].connect(self.setColor)
#         self.thick_sl.valueChanged[int].connect(self.setThick)
#         self.show()
#     
#     def setColor(self,b,g,r):
#         col = QColor(r,g,b)
#         self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
#                                      "QPushButton{border-radius:5px}"
#                                      "QPushButton{border:1px}")
#         self.color_lb.setText('Color: '+col.name())
#         self.pencil.ChangePenColor(col)
#         pass
#     
#     def setThick(self,value):
#         self.thick_sl.setValue(value)
#         self.thick_lb.setText('Tickness: '+str(value))
#         self.pencil.ChangePenThickness(value)
#         pass
#     
#     def chooseColor(self):
#         col = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
#         self.pencil.pencolor = col
#         self.color_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
#                                     "QPushButton{border-radius:5px}"
#                                     "QPushButton{border:1px}")
#     
#     def fillColor(self):
#         col = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
#         self.pencil.brush = col
#         self.fill_btn.setStyleSheet("QPushButton{background-color:"+col.name()+"}"
#                                     "QPushButton{border-radius:5px}"
#                                     "QPushButton{border:1px}")
# =============================================================================
class MutiCanvas(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color:#282828;border:1px solid #424242;padding:0px;margin:0px;')
        self.setTabsClosable(True)
        self.setAcceptDrops(True)
        self.setContentsMargins(0,0,0,0)
        self.setAutoFillBackground(True)
        self.tabCloseRequested.connect(self.removeTab)

class Canvas(QWidget):
    signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(250, 300)
        self.setStyleSheet("background-color:#282828;border:0px;padding:0px;margin:0px;")
        self.draw = Draw()
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.draw)
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        if settings.value('mode') == 1:
            img = cv2.imread(settings.value('imagePath'))
            self.layers = LayerStack(img)
        else:
            self.layers = LayerStack()
        self.dpi = int(settings.value('dpi'))
        self.draw.resize(*self.layers.ImgInfo())
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        self.setLayout(self.vbox)
        self.draw.signal[str,tuple,tuple,tuple,int,tuple].connect(self.draw_2Pix)
        self.draw.signal_[list,int,tuple].connect(self.draw_NPix)
        self.layers.signal.connect(self.imgOperate)
        self.layers.layNum_signal[int].connect(self.chgLayerImage)
        self.layers.changeImg(self.layers.Image)
        self.draw.drop_signal[tuple].connect(self.dropColor)
    
    def chgLayerImage(self,idx):
        self.layer_idx = idx
    
    def draw_2Pix(self,mode,start,end,pencolor,thick,brush):
        '''
        pqscreen  = QGuiApplication.primaryScreen()
        pixmap2 = pqscreen.grabWindow(self.draw.winId(),0,0,
                                      #self.draw.geometry().x(),
                                      #self.draw.geometry().y(),
                                      self.draw.width(),self.draw.height())
        pixmap2.save('./tmp/sceen.jpg')
        self.draw.setPixmap(pixmap2)
        '''
        print(mode,start,end,pencolor,thick,brush)
        start = ops.cvtCanPosAndLayerPos(start,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        end = ops.cvtCanPosAndLayerPos(end,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        print(start,end)
        if mode == 'Line':
            cv2.line(self.layers.tmp_img,start,end,pencolor[0],thick)
        elif mode == 'Rect':
            if brush[-1] != 0:
                cv2.rectangle(self.layers.tmp_img,start,end,brush[0],-1)
            cv2.rectangle(self.layers.tmp_img,start,end,pencolor[0],thick)
        elif mode == 'Circle':
            if brush[-1] != 0:
                cv2.ellipse(self.layers.tmp_img,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,brush[0],-1)
            cv2.ellipse(self.layers.tmp_img,((start[0]+end[0])//2,(start[1]+end[1])//2),(abs(end[0]-start[0])//2,abs(end[1]-start[1])//2),0,0,360,pencolor[0],thick)
        #self.layers.tmp_img = 
        self.layers.layer[self.layer_idx].changeImg(self.layers.tmp_img)
        self.layers.updateImg()
        pass
    
    def dropColor(self,pos):
        #pos = ops.cvtCanPosAndLayerPos(pos,(0,0),self.layers.layer[self.layer_idx].getCenterOfImage(),self.draw.getCenterOfCanvas())
        [b,g,r] = self.layers.Image[pos[1],pos[0]]
        self.draw.changeBlockColor(b,g,r)
    
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
        cv2.imwrite('./tmp_layer.jpg',self.layers.Image)
        self.signal.emit()
        pass
    
    def chgCursor(self,tar=None):
        if tar in ['Pencil','Line','Rect','Circle']:
            self.setCursor(Qt.CrossCursor)
        elif tar == 'Dropper':
            self.setCursor(QCursor(QPixmap('./UI/dropper.png'),0,15))
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #pyqt_learn = Draw()
    pyqt_learn = Canvas()
    pyqt_learn.show()
    app.exec_()