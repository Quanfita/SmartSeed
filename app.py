# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:09:14 2019

@author: Quanfita
"""

import sys
import cv2
import sip
import logger
from pencil import AdjBlock, Canvas
import numpy as np
from Basic import AdjDialog
from Thread import ProThread
from Stack import OpStack
from LayerView import LayerMain
from Welcome import Welcome
from Hist import Hist
import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, 
                             QPushButton, QMessageBox, QDesktopWidget, 
                             QMainWindow, QAction, qApp, QMenu, 
                             QSlider, QLabel, QFileDialog, 
                             QDialog, QGroupBox, QDialogButtonBox, 
                             QGridLayout, QSplitter, QDockWidget, 
                             QToolBar,QProgressDialog)
from PyQt5.QtGui import QIcon, QFont


class Example(QMainWindow):
    signal = pyqtSignal()
    def __init__(self):
        #super().__init__()
        super(Example,self).__init__()
        self.OS = OpStack()
        #self.setMouseTracking(False)
        self.pos_xy = []
        self.canvas = Canvas()
        self.Thr = ProThread(self.canvas.layers)
        self.F = Hist()
        #self.F = MyFigure(width=3, height=2, dpi=100)
        self.last_tool = ''
        self.initUI()
        
    def initUI(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        QToolTip.setFont(QFont('SansSerif', 10))
        
        #self.setToolTip('This is a <b>QWidget</b> widget')

        exitAct = QAction(QIcon('./UI/exit.svg'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        self.pencilAct = QAction(QIcon('./UI/pen.svg'),'pencil',self)
        self.pencilAct.setStatusTip('Pencil')
        self.pencilAct.triggered.connect(self.pencil)
        
        self.lineAct = QAction(QIcon('./UI/line.svg'),'line',self)
        self.lineAct.setStatusTip('Line')
        self.lineAct.triggered.connect(self.line)
        
        self.rectAct = QAction(QIcon('./UI/square.svg'),'rect',self)
        self.rectAct.setStatusTip('Rect')
        self.rectAct.triggered.connect(self.rect)
        
        self.circleAct = QAction(QIcon('./UI/circle.svg'),'circle',self)
        self.circleAct.setStatusTip('Circle')
        self.circleAct.triggered.connect(self.circle)
        
        self.cropAct = QAction(QIcon('./UI/crop.svg'),'crop',self)
        self.cropAct.setStatusTip('Crop')
        self.cropAct.triggered.connect(self.crop)
        
        self.brushAct = QAction(QIcon('./UI/paint-brush.svg'),'brush',self)
        self.brushAct.setStatusTip('Brush')
        self.brushAct.triggered.connect(self.brush)
        
        self.eraserAct = QAction(QIcon('./UI/eraser.svg'),'eraser',self)
        self.eraserAct.setStatusTip('Eraser')
        self.eraserAct.triggered.connect(self.eraser)
        
        self.dropperAct = QAction(QIcon('./UI/dropper.svg'),'dropper',self)
        self.dropperAct.setStatusTip('Dropper')
        self.dropperAct.triggered.connect(self.dropper)
        
        self.fillAct = QAction(QIcon('./UI/fill-drip.svg'),'fill',self)
        self.fillAct.setStatusTip('Fill-Drip')
        self.fillAct.triggered.connect(self.fill)
        
        self.stampAct = QAction(QIcon('./UI/stamp.svg'),'stamp',self)
        self.stampAct.setStatusTip('Stamp')
        self.stampAct.triggered.connect(self.stamp)
        
        openFile = QAction(QIcon('./UI/open.svg'),'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new Image')
        openFile.triggered.connect(self.openimage)
        
        saveFile = QAction(QIcon('./UI/save.svg'),'Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save this Image')
        saveFile.triggered.connect(self.saveSlot)
        
        AWBAct = QAction('AWB',self)
        AWBAct.setStatusTip('Auto White Balance')
        AWBAct.triggered.connect(self.AWB)
        
        ACEAct = QAction('ACE',self)
        ACEAct.setStatusTip('Auto Color Equalization')
        ACEAct.triggered.connect(self.ACE)
        
        ACAAct = QAction('ACA',self)
        ACAAct.setStatusTip('Auto Contrast Adjustment')
        ACAAct.triggered.connect(self.ACA)
        
        cansizeAct = QAction('CanvasSize',self)
        cansizeAct.setStatusTip('Resize the canvas')
        cansizeAct.triggered.connect(self.canSize)
        
        imgsizeAct = QAction('ImageSize',self)
        imgsizeAct.setStatusTip('Resize the image')
        imgsizeAct.triggered.connect(self.imgSize)
        
        undoAct = QAction(QIcon('./UI/undo.svg'),'Undo',self)
        undoAct.setShortcut('Ctrl+Z')
        undoAct.setStatusTip('Undo The Last Operating')
        undoAct.triggered.connect(self.Undo)
        
        redoAct = QAction(QIcon('./UI/redo.svg'),'Redo',self)
        redoAct.setStatusTip('Redo The Last Operating')
        redoAct.triggered.connect(self.Redo)
        
        filter0 = QAction('Portrait',self)
        filter0.setStatusTip("Portrait")
        filter0.triggered.connect(self.setTable)
        filter1 = QAction('Smooth',self)
        filter1.setStatusTip("Smooth")
        filter1.triggered.connect(self.setTable)
        filter2 = QAction('Morning',self)
        filter2.setStatusTip("Morning")
        filter2.triggered.connect(self.setTable)
        filter3 = QAction('Pop',self)
        filter3.setStatusTip("Pop")
        filter3.triggered.connect(self.setTable)
        filter4 = QAction('Accentuate',self)
        filter4.setStatusTip("Accentuate")
        filter4.triggered.connect(self.setTable)
        filter5 = QAction('Art Style',self)
        filter5.setStatusTip("Art Style")
        filter5.triggered.connect(self.setTable)
        filter6 = QAction('Black & White',self)
        filter6.setStatusTip("Black & White")
        filter6.triggered.connect(self.setTable)
        filter7 = QAction('HDR',self)
        filter7.setStatusTip("HDR")
        filter7.triggered.connect(self.setTable)
        filter8 = QAction('Modern',self)
        filter8.setStatusTip("Modern")
        filter8.triggered.connect(self.setTable)
        filter9 = QAction('Old',self)
        filter9.setStatusTip("Old")
        filter9.triggered.connect(self.setTable)
        filter10 = QAction('Yellow',self)
        filter10.setStatusTip("Yellow")
        filter10.triggered.connect(self.setTable)
        
        AnimeFilter = QAction('Anime',self)
        AnimeFilter.setStatusTip('Anime Filter')
        AnimeFilter.triggered.connect(self.Anime)
        
        PainterAct = QAction('Painter',self)
        PainterAct.setStatusTip('Anime Painter')
        PainterAct.triggered.connect(self.Paint)
        
        InkAct = QAction('Ink',self)
        InkAct.setStatusTip('Ink Style Transfer')
        InkAct.triggered.connect(self.Ink)
        
        PencilDrawAct = QAction('PencilDrawing',self)
        PencilDrawAct.setStatusTip('Pencil Drawing')
        PencilDrawAct.triggered.connect(self.PencilDrawing)
        
        blurAct = QAction('Blur',self)
        blurAct.setStatusTip('Blur')
        blurAct.triggered.connect(self.Blur)
        
        blurMoreAct = QAction('BlurMore',self)
        blurMoreAct.setStatusTip('Blur More')
        blurMoreAct.triggered.connect(self.BlurMore)
        
        GaussianblurMoreAct = QAction('GaussianBlur',self)
        GaussianblurMoreAct.setStatusTip('Gaussian Blur')
        GaussianblurMoreAct.triggered.connect(self.GaussianBlur)
        
        MotionblurAct = QAction('MotionBlur',self)
        MotionblurAct.setStatusTip('Motion Blur')
        MotionblurAct.triggered.connect(self.MotionBlur)
        
        RadialblurAct = QAction('RadialBlur',self)
        RadialblurAct.setStatusTip('Radial Blur')
        RadialblurAct.triggered.connect(self.RadialBlur)
        
        SmartblurAct = QAction('SmartBlur',self)
        SmartblurAct.setStatusTip('Smart Blur')
        SmartblurAct.triggered.connect(self.SmartBlur)
        
        usmAct = QAction('USM',self)
        usmAct.setStatusTip('USM')
        usmAct.triggered.connect(self.USM)
        
        EdgeSharpAct = QAction('EdgeSharp',self)
        EdgeSharpAct.setStatusTip('Edge Sharp')
        EdgeSharpAct.triggered.connect(self.EdgeSharp)
        
        SmartSharpAct = QAction('SmartSharp',self)
        SmartSharpAct.setStatusTip('Smart Sharp')
        SmartSharpAct.triggered.connect(self.SmartSharp)
        
        tra_filter = QMenu('Traditional Filter',self)
        blurry_filter = QMenu('Blurry Filter',self)
        blurry_filter.addAction(blurAct)
        blurry_filter.addAction(blurMoreAct)
        blurry_filter.addAction(GaussianblurMoreAct)
        blurry_filter.addAction(MotionblurAct)
        blurry_filter.addAction(RadialblurAct)
        blurry_filter.addAction(SmartblurAct)
        sharpen_filter = QMenu('Sharpen Filter',self)
        sharpen_filter.addAction(usmAct)
        sharpen_filter.addAction(EdgeSharpAct)
        sharpen_filter.addAction(SmartSharpAct)
        filter_lib = QMenu('Filter Library',self)
        filter_lib.addAction(AnimeFilter)
        filter_lib.addAction(PainterAct)
        filter_lib.addAction(InkAct)
        filter_lib.addAction(PencilDrawAct)
        
        newAct = QAction(QIcon('./UI/new.svg'),'New', self)
        newAct.setShortcut('Ctrl+N')
        newAct.setStatusTip('Create A Write Block')
        newAct.triggered.connect(self.newBlock)
        
        self.toolBar = QToolBar()
        self.main_toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea,self.main_toolbar)
        self.addToolBar(Qt.LeftToolBarArea,self.toolBar)
        self.main_toolbar.addAction(newAct)
        self.main_toolbar.addAction(openFile)
        self.main_toolbar.addAction(saveFile)
        self.main_toolbar.addAction(undoAct)
        self.main_toolbar.addAction(redoAct)
        self.main_toolbar.addAction(exitAct)
        
        self.toolBar.addAction(self.pencilAct)
        self.toolBar.addAction(self.lineAct)
        self.toolBar.addAction(self.rectAct)
        self.toolBar.addAction(self.circleAct)
        self.toolBar.addAction(self.fillAct)
        self.toolBar.addAction(self.eraserAct)
        self.toolBar.addAction(self.brushAct)
        self.toolBar.addAction(self.cropAct)
        self.toolBar.addAction(self.dropperAct)
        self.toolBar.addAction(self.stampAct)
        self.toolBar.setOrientation(Qt.Vertical)
        
        
        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self) 
        impMenu.addAction(impAct)
        
        LightAct = QAction('Light',self)
        LightAct.triggered.connect(self.light)
        compAct = QAction('Comp',self)
        compAct.triggered.connect(self.comp)
        customAct = QAction('Custom',self)
        customAct.triggered.connect(self.custom)
        hueAct = QAction('Hue',self)
        hueAct.triggered.connect(self.hue)
        
        adjustMenu = QMenu('Adjustment',self)
        adjustMenu.addAction(LightAct)
        adjustMenu.addAction(compAct)
        adjustMenu.addAction(customAct)
        adjustMenu.addAction(hueAct)
        
        aboutAct = QAction(QIcon('./UI/info.svg'),'About',self)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newAct)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(exitAct)
        
        imageMenu = menubar.addMenu('Image')
        imageMenu.addAction(AWBAct)
        imageMenu.addAction(ACEAct)
        imageMenu.addAction(ACAAct)
        imageMenu.addMenu(adjustMenu)
        imageMenu.addAction(cansizeAct)
        imageMenu.addAction(imgsizeAct)
        
        editMenu = menubar.addMenu('Edit')
        editMenu.addAction(undoAct)
        editMenu.addAction(redoAct)
        
        filterMenu = menubar.addMenu('Filter')
        filterMenu.addMenu(tra_filter)
        filterMenu.addMenu(blurry_filter)
        filterMenu.addMenu(sharpen_filter)
        filterMenu.addMenu(filter_lib)
        tra_filter.addAction(filter0)
        tra_filter.addAction(filter1)
        tra_filter.addAction(filter2)
        tra_filter.addAction(filter3)
        tra_filter.addAction(filter4)
        tra_filter.addAction(filter5)
        tra_filter.addAction(filter6)
        tra_filter.addAction(filter7)
        tra_filter.addAction(filter8)
        tra_filter.addAction(filter9)
        tra_filter.addAction(filter10)
        
        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)
        
        viewMenu = menubar.addMenu('View')
        viewMenu.addAction(viewStatAct)
        
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(aboutAct)
        
        x = 0
        y = 0
        
        self.text = "x: {0},  y: {1}".format(x, y)
        #self._size = QSize(480,360)
        #self.canvas = QPixmap(self._size)
        #self.label = Draw(self.OS,self.canvas,self.refreshShow)
        #self.label.setAlignment(Qt.AlignCenter)
        #self.main_vbox.addWidget(menubar)
        #self.main_vbox.addWidget(self.toolbar)
        #self.main_vbox.addWidget(self.label)
        
        
        self.info_lb = QLabel('',self)
        self.info_lb.setAlignment(Qt.AlignLeft)
        #self.setMouseTracking(True)
        #self.showFigure()
        #self.setLayout(self.main_vbox)
        #self.CreateDockWidget('Figure',self.F)
        #self.CreateDockWidget('Information',self.info_lb)
        self.main_Fig = QDockWidget('Figure')  # 实例化dockwidget类
        self.main_Fig.setWidget(self.F)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.main_Fig.setObjectName("Figure")
        self.main_Fig.setFeatures(self.main_Fig.DockWidgetFloatable|self.main_Fig.DockWidgetMovable)    #  设置dockwidget的各类属性
        #self.main_Fig.setStyleSheet('QDockWidget{border: 1px solid black;}')
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_Fig) 
        main_info = QDockWidget('Information')  # 实例化dockwidget类
        main_info.setWidget(self.info_lb)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        main_info.setObjectName("Info")
        main_info.setFeatures(main_info.DockWidgetFloatable|main_info.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, main_info) 
        self.layer = LayerMain(self.canvas.layers,self.refreshShow)
        self.layer_dock = QDockWidget('Layer')
        self.layer_dock.setWidget(self.layer)
        self.layer_dock.setObjectName("Info")
        self.layer_dock.setFeatures(main_info.DockWidgetFloatable|main_info.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.layer_dock)
        logger.info('Application Start!')
        #splitter  =  QSplitter(self)
        #splitter.addWidget(self.label)
        #splitter.addWidget(self.F)
        #splitter.setOpaqueResize(False)
        #splitter.setOrientation(Qt.Vertical)
        self.setCentralWidget(self.canvas)
        self.setDockNestingEnabled(True)
        self.setMinimumSize(800,480)
        self.resize(1366, 768)
        self.center()
        self.setWindowTitle('SmartSeed')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))        
        self.showMaximized()
        self.canvas.signal.connect(self.refreshShow)
        self.show()
        
    
    def CreateDockWidget(self, name, widget):  # 定义一个createDock方法创建一个dockwidget
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(widget)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName("selectQuote")
        dock.setFeatures(dock.DockWidgetFloatable|dock.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, dock)  
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    '''
    def showFigure(self):
        try:
            self.removeDockWidget(self.main_Fig)
            sip.delete(self.main_Fig)
            sip.delete(self.F)
        except:
            logger.warning('Initial Figure!')
        self.F = MyFigure(width=3, height=2, dpi=100)
        self.main_Fig = QDockWidget('Figure')  # 实例化dockwidget类
        self.main_Fig.setWidget(self.F)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.main_Fig.setObjectName("Figure")
        self.main_Fig.setFeatures(self.main_Fig.DockWidgetFloatable|self.main_Fig.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_Fig) 
        try:
            self.F.DrawHistogram(self.canvas.Image)
            logger.info("Draw Histogram!")
        except:
            logger.warning('None Image!')
    '''
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            logger.info('Close Application!')
            event.accept()
        else:
            event.ignore()
    
    def toggleMenu(self, state):
        
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()
            
    def contextMenuEvent(self, event):
       cmenu = QMenu(self)
       
       newAct = cmenu.addAction("New")
       opnAct = cmenu.addAction("Open")
       quitAct = cmenu.addAction("Quit")
       action = cmenu.exec_(self.mapToGlobal(event.pos()))
       
       if action == quitAct:
           qApp.quit()
       elif action == opnAct:
           self.openimage()
       elif action == newAct:
           self.newBlock()
       else:
           pass
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
    '''
    def mouseMoveEvent(self, e):
        x = e.x()
        y = e.y()
        text = "x: {0},  y: {1}".format(x, y)
        self.label.setText(text)
    '''
    def newBlock(self):
        wel = Welcome()
        if wel.exec_() == QDialog.Accepted:
            #self.F.DrawHistogram(self.canvas)
            self.info = 'width: {0}\nheight: {1}'.format(self.canvas.layers.width(),self.canvas.layers.height())
            self.info_lb.setText(self.info)
            self.refreshShow()
    
    def openimage(self):
   # 打开文件路径
   #设置文件扩展名过滤,注意用双分号间隔
        imgName,imgType= QFileDialog.getOpenFileName(self,
                                    "打开图片",
                                    "",
                                    " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if imgName is '':
            logger.warning('None Image has been selected!')
            return
        else:
            logger.info('ImageName: '+imgName)
        
        self.layer.addLayer(cv2.imread(imgName),imgName.split('/')[-1])
        #self.canvas.layers.changeImg(cv2.imread(imgName))
        
        if self.canvas.layers.Image.size == 1:
            return
        self.OS.push([np.array(self.canvas.layers.Image),'openimage'])
        self.info = 'width: {0}\nheight: {1}'.format(self.canvas.layers.width(),self.canvas.layers.height())
        self.info_lb.setText(self.info)
        #self.F.DrawHistogram(self.canvas)
        self.refreshShow()
        #self.resize(int(1.5*self.canvas.width),int(1.2*self.canvas.height))
        self.center()
    
    def saveSlot(self):
        # 调用存储文件dialog
        fileName, tmp = QFileDialog.getSaveFileName(
            self, 'Save Image', 'Untitled', '*.png *.jpg *.bmp', '*.png')

        if fileName is '':
            return
        if self.canvas.layers.Image.size == 1:
            return
        # 调用opencv写入图像
        cv2.imwrite(fileName, self.canvas.layers.Image)
        
    def refreshShow(self):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        #height, width, channel = self.canvas.shape
        #bytesPerLine = 3 * width
        #self.qImg = QImage(self.canvas.data, width, height, bytesPerLine,
                           #QImage.Format_RGB888).rgbSwapped()
        # 将Qimage显示出来
        self.info = 'width: {0}\nheight: {1}'.format(self.canvas.layers.width(),self.canvas.layers.height())
        self.info_lb.setText(self.info)
        #self.showFigure()
        #self.label.setPixmap(ops.cvtCV2Pixmap(self.canvas.layers.Image))
        cv2.imwrite('./tmp/error.jpg',self.canvas.layers.Image)
        #self.label.resize(self.canvas.shape[1],self.canvas.shape[0])
        #self.canvas = QPixmap.fromImage(self.qImg)
        self.F.DrawHistogram(self.canvas.layers.Image)
        #self.chgSize()
    
    def setTable(self):
        sender = self.sender()
        tm = sender.text()
        logger.debug(tm)
        if tm == 'Portrait':
            tableName = 'lookup-table_1.jpg'
        elif tm == 'Smooth':
            tableName = 'lookup-table_2.jpg'
        elif tm == 'Morning':
            tableName = 'lookup-table_3.jpg'
        elif tm == 'Pop':
            tableName = 'lookup-table_4.jpg'
        elif tm == 'Accentuate':
            tableName = 'lookup-table_5.jpg'
        elif tm == 'Art Style':
            tableName = 'lookup-table_6.jpg'
        elif tm == 'Black & White':
            tableName = 'lookup-table_B&W.jpg'
        elif tm == 'HDR':
            tableName = 'lookup-table_hdr.jpg'
        elif tm == 'Modern':
            tableName = 'lookup-table_li.jpg'
        elif tm == 'Old':
            tableName = 'lookup-table_old.jpg'
        elif tm == 'Yellow':
            tableName = 'lookup-table-yellow.png'
        else:
            return
        self.Thr.change('filter',tableName)
        self.Thr.start()
        self.showDialog(1)
        logger.info("Doing Filters Successful!")
        self.OS.push([np.array(self.canvas.layers.Image),'doFilters'])
        self.refreshShow()
        #self.doFilters(tableName)
    
    def AWB(self):
        self.Thr.change('AWB')
        self.Thr.start()
        self.showDialog(1)
        logger.info("AWB Successful!")
        self.OS.push([np.array(self.canvas.layers.Image),'AWB'])
        self.refreshShow()
        
    def ACE(self):
        self.Thr.change('ACE')
        self.Thr.start()
        self.showDialog(1)
        logger.info('ACE Successful!')
        self.OS.push([np.array(self.canvas.layers.Image),'ACE'])
        self.refreshShow()
        
    def ACA(self):
        self.Thr.change('ACA')
        self.Thr.start()
        self.showDialog(1)
        logger.info('ACA Successful!')
        self.OS.push([np.array(self.canvas.layers.Image),'ACA'])
        self.refreshShow()
    
    def Undo(self):
        if self.OS.isEmpty():
            logger.warning('No Operating Should Be Undo!')
            return
        else:
            self.OS.re_push(self.OS.pop())
            if self.OS.isEmpty():
                logger.warning('No Operating Should Be Undo!')
                return
            else:
                [img,op] = self.OS.peek()
                self.canvas.layers.changeImg(img.astype(np.uint8))
                #self.label.Clean()
                logger.info('Undo Operating to '+op+'!')
                self.refreshShow()
    
    def Redo(self):
        if self.OS.re_isEmpty():
            logger.warning('No Operating Should Be Redo!')
            return
        else:
            self.OS.push(self.OS.re_pop())
            [img,op] = self.OS.peek()
            self.canvas.layers.changeImg(img.astype(np.uint8))
            logger.info('Redo Operating to ' + op + '!')
        self.refreshShow()
    '''
    def showevent(self,event):
        self.chgSize()
    
    def moveEvent(self,event):
        self.chgSize()
    
    def resizeEvent(self,event):
        self.chgSize()
    
    def chgSize(self):

        self.label.lb_x = (self.label.width() - self.canvas.layers.width())//2
        self.label.lb_y = (self.label.height() - self.canvas.layers.height())//2
        self.label.lb_w = self.canvas.layers.width()
        self.label.lb_h = self.canvas.layers.height()
        #print(self.label.width(),self.label.height())
        #print(self.label.geometry().x(),self.label.geometry().y())
        #print(self.label.lb_x,self.label.lb_y,self.label.lb_w,self.label.lb_h)
'''
    def disPre(self):
        if self.last_tool == 'Pencil':
            self.pencilAct.setEnabled(True)
        elif self.last_tool == 'Line':
            self.lineAct.setEnabled(True)
        elif self.last_tool == 'Rect':
            self.rectAct.setEnabled(True)
        elif self.last_tool == 'Circle':
            self.circleAct.setEnabled(True)
        elif self.last_tool == 'Fill':
            self.fillAct.setEnabled(True)
        elif self.last_tool == 'Crop':
            self.cropAct.setEnabled(True)
        elif self.last_tool == 'Dropper':
            self.dropperAct.setEnabled(True)
        elif self.last_tool == 'Eraser':
            self.eraserAct.setEnabled(True)
        elif self.last_tool == 'Brush':
            self.brushAct.setEnabled(True)
        elif self.last_tool == 'Stamp':
            self.stampAct.setEnabled(True)
        else: return
        self.removeDockWidget(self.tmp_dock)
        sip.delete(self.tmp_dock)
    
    def perOpTools(self,s):
        self.canvas.draw.chgType(s)
        self.disPre()
        self.canvas.chgCursor(s)
        self.adj_b = AdjBlock(self.canvas.draw)
        self.tmp_dock = QDockWidget(s+' Attributes')  # 实例化dockwidget类
        self.tmp_dock.setWidget(self.adj_b)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.tmp_dock.setObjectName("Attributes")
        self.tmp_dock.setFeatures(self.tmp_dock.DockWidgetFloatable|self.tmp_dock.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.tmp_dock)
        if self.last_tool == '':self.canvas.draw.saveImg()
        self.last_tool = s
        self.refreshShow()
        
    
    def showDialog(self,tar=10):
        num = self.canvas.layers.pixNum*tar
        self.progress = QProgressDialog(self)
        self.progress.setWindowTitle("请稍等")  
        self.progress.setLabelText("正在操作...")
        self.progress.setCancelButtonText("取消")
        self.progress.setMinimumDuration(5)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setRange(0,num) 
        for i in range(num):
            if i >= 3*num//4 and i % 10 == 0 and self.Thr.isRunning():
                time.sleep(0.00000001)
            elif self.Thr.isFinished():
                i += 1000
            self.progress.setValue(i) 
            if self.progress.wasCanceled():
                self.Thr.exit(0)
                QMessageBox.warning(self,"提示","操作失败") 
                break
            else:
                continue
        self.progress.setValue(num)
        #QMessageBox.information(self,"提示","操作成功")
    
    def Anime(self):
        self.Thr.change('Anime','./samples/2.jpg')
        self.Thr.start()
        self.showDialog(10)
        self.OS.push([np.array(self.canvas.layers.Image),'Anime'])
        logger.info('Do Anime Filter Successful!')
        self.refreshShow()
    
    def pencil(self):
        self.perOpTools("Pencil")
        self.pencilAct.setEnabled(False)
        pass
        
    def line(self):
        self.perOpTools('Line')
        self.lineAct.setEnabled(False)
        pass
    
    def rect(self):
        self.perOpTools("Rect")
        self.rectAct.setEnabled(False)
        pass
    
    def circle(self):
        self.perOpTools("Circle")
        self.circleAct.setEnabled(False)
        pass
    
    def fill(self):
        self.perOpTools('Fill')
        self.fillAct.setEnabled(False)
        pass
    
    def crop(self):
        self.perOpTools("Crop")
        self.cropAct.setEnabled(False)
        pass
    
    def dropper(self):
        self.perOpTools("Dropper")
        self.dropperAct.setEnabled(False)
        pass
    
    def eraser(self):
        self.perOpTools("Eraser")
        self.eraserAct.setEnabled(False)
        pass
    
    def brush(self):
        self.perOpTools("Brush")
        self.brushAct.setEnabled(False)
        pass
    
    def stamp(self):
        self.perOpTools("Stamp")
        self.stampAct.setEnabled(False)
        pass
    
    def Paint(self):
        self.Thr.change('Painter')
        self.Thr.start()
        self.showDialog(10)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'Paint'])
        logger.info('Do Anime Painter Successful!')
        self.refreshShow()
    
    def Ink(self):
        self.Thr.change('Ink')
        self.Thr.start()
        self.showDialog(10)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'Ink'])
        logger.info('Do Ink Style Transfer Successful!')
        self.refreshShow()
    
    def PencilDrawing(self):
        self.Thr.change('Pencil')
        self.Thr.start()
        self.showDialog(10)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'PencilDrawing'])
        logger.info('Do Pencil Drawing Successful!')
        self.refreshShow()
    
    def Blur(self):
        self.Thr.change('Blur')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'Blur'])
        logger.info('Do Blur Successful!')
        self.refreshShow()
    
    def GaussianBlur(self):
        self.Thr.change('GaussianBlur')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'GaussianBlur'])
        logger.info('Do Gaussian Blur Successful!')
        self.refreshShow()
    
    def MotionBlur(self):
        self.Thr.change('MotionBlur')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'MotionBlur'])
        logger.info('Do Motion Blur Successful!')
        self.refreshShow()
    
    def RadialBlur(self):
        self.Thr.change('RadialBlur')
        self.Thr.start()
        self.showDialog(5)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'RadialBlur'])
        logger.info('Do Radial Blur Successful!')
        self.refreshShow()
    
    def SmartBlur(self):
        self.Thr.change('SmartBlur')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'SmartBlur'])
        logger.info('Do Smart Blur Successful!')
        self.refreshShow()
    
    def BlurMore(self):
        self.Thr.change('BlurMore')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'BlurMore'])
        logger.info('Do More Blur Successful!')
        self.refreshShow()
    
    def USM(self):
        self.Thr.change('USM')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'USM'])
        logger.info('Do USM Successful!')
        self.refreshShow()
    
    def EdgeSharp(self):
        self.Thr.change('EdgeSharp')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'EdgeSharp'])
        logger.info('Do Edge Sharp Successful!')
        self.refreshShow()
    
    def SmartSharp(self):
        self.Thr.change('SmartSharp')
        self.Thr.start()
        self.showDialog(1)
        self.OS.push([np.array(self.canvas.tmp_img.Image),'SmartSharp'])
        logger.info('Do Smart Sharp Successful!')
        self.refreshShow()
    
    def light(self):
        l = AdjDialog(self.canvas.layers,'light')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def comp(self):
        l = AdjDialog(self.canvas.layers,'comp')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def custom(self):
        l = AdjDialog(self.canvas.layers,'custom')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def hue(self):
        l = AdjDialog(self.canvas.layers,'hue')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def canSize(self):
        self.canvas.canResize()
        pass
    
    def imgSize(self):
        self.canvas.imgResize()
        pass
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())