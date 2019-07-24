# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:09:14 2019

@author: Quanfita
"""

import sys
import cv2
import sip
import logger
from PIL import Image
from views import AdjBlock, Canvas, MutiCanvas, FrontBackColor, LayerMain, Welcome, Hist, AdjDialog
import numpy as np
from Stack import OpStack
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, 
                             QPushButton, QMessageBox, QDesktopWidget, 
                             QMainWindow, QAction, qApp, QMenu, 
                             QSlider, QLabel, QFileDialog, 
                             QUndoStack, QUndoCommand,
                             QDialog, QGroupBox, QDialogButtonBox, 
                             QGridLayout, QSplitter, QDockWidget, 
                             QToolBar,QProgressDialog)
from PyQt5.QtGui import QIcon, QFont, QColor

class Edit(QUndoCommand):

    def __init__(self,debug=False):
        super().__init__()
        self.__list = []

    def redo(self):
        self.self.__list.append(0)
        pass

class MainWindow(QMainWindow):
    send_signal = pyqtSignal(dict)
    def __init__(self,debug=False):
        #super().__init__()
        super(MainWindow,self).__init__()
        self.__debug = debug
        self.setStyleSheet(''
                            'QMainWindow{color:white;background-color:#424242;}'
                            'QTabWidget::pane{color:white;border:3px solid #535353;padding:0px;}'
                            'QTabBar::pane{color:white;background-color:#535353;border:1px solid #424242;}'
                            'QTabBar::tab{color:white;background-color:#535353;border:1px solid #424242;border-bottom:0px;padding:0px;margin-top:1px;width:100px;height:25px;}'
                            #'QWidget#CentralWidget{background-color:transparent;}'
                            'QMenuBar{color:white;background-color:#535353;border-bottom:2px solid #424242;padding:5px;}'
                            'QMenuBar::item:selected{color:white;background-color:#454545;}'
                            'QMenu{color:black;background-color:#cdcdcd;border:1px solid #535353;}'
                            'QMenu::item{background-color:transparent;padding:8px 42px;margin:0px 0px;border-bottom:1px solid #dbdbdb;}'
                            'QMenu::item:selected{color:white;background-color:#0078d7;}'
                            'QMenu::icon{left:4px;}'
                            'QToolBar{color:white;background-color:#535353;border:2px solid #424242;}'
                            'QToolBar::item{color:white;background-color:transparent;}'
                            'QToolBar::separator{background-color:#535353;margin:3px;}'
                            'QStatusBar{color:white;background-color:#535353;border:2px solid #424242;border-radius:3px;}')
        self.OS = OpStack()
        #self.setMouseTracking(False)
        self.pos_xy = []
        #self.mcanvas.canvas = Canvas()
        self.mcanvas = MutiCanvas(debug=self.__debug)
        #self.mcanvas.refresh.connect(self.refreshShow)
        #self.mcanvas.added.connect(self.middleware)
        #self.mcanvas.addTab(self.mcanvas.canvas,'1')
        #self.Thr = ProThread(self.mcanvas.canvas.layers)
        self.F = Hist()
        #self.F = MyFigure(width=3, height=2, dpi=100)
        self.last_tool = ''
        self.frontcolor = QColor('white')
        self.backcolor = QColor('black')
        self.initUI()
        
    def initUI(self):
        #self.setWindowFlags(Qt.CustomizeWindowHint)
        self.initMenu()
        self.initToolBar()
        self.initDockWidget()

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setCentralWidget(self.mcanvas)
        self.setDockNestingEnabled(True)
        self.setMinimumSize(800,480)
        self.resize(1366, 768)
        self.center()

        self.setWindowTitle('SmartSeed')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))        
        self.showMaximized()
        self.show()
        logger.info('Init complited!')
        self.refreshShow()
    
    def initMenu(self):
        exitAct = QAction(QIcon('./UI/exit.svg'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
                
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
        
        impMenu = QMenu('Import', self)
        impAct = QAction('Import image', self)
        impAct.setShortcut('Ctrl+I')
        impAct.setStatusTip('Import new Image')
        impAct.triggered.connect(self.importimage)
        impMenu.addAction(impAct)
        
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
        
        infoViewAct = QAction('Information',self, checkable=True)
        infoViewAct.setStatusTip('View information')
        infoViewAct.setChecked(True)
        infoViewAct.triggered.connect(self.infoView)
        
        channelViewAct = QAction('Channel',self, checkable=True)
        channelViewAct.setStatusTip('View channel')
        channelViewAct.setChecked(True)
        channelViewAct.triggered.connect(self.channelView)
        
        histViewAct = QAction('Hist',self, checkable=True)
        histViewAct.setStatusTip('View hist')
        histViewAct.setChecked(True)
        histViewAct.triggered.connect(self.histView)
                                      
        aboutAct = QAction(QIcon('./UI/info.svg'),'About',self)
        
        viewMenu = menubar.addMenu('View')
        viewMenu.addAction(viewStatAct)
        viewMenu.addAction(infoViewAct)
        viewMenu.addAction(channelViewAct)
        viewMenu.addAction(histViewAct)
        
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(aboutAct)
    
    def initToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.setContentsMargins(0,10,0,10)
        self.main_toolbar = QToolBar()
        self.main_toolbar.setContentsMargins(5,0,5,0)
        self.addToolBar(Qt.TopToolBarArea,self.main_toolbar)
        self.addToolBar(Qt.LeftToolBarArea,self.toolBar)
        self.main_toolbar.setFixedHeight(40)
        
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
        
        self.moveAct = QAction(QIcon('./UI/hand-paper.svg'),'move',self)
        self.moveAct.setStatusTip('Move')
        self.moveAct.triggered.connect(self.movement)
        
        self.colorWidget = FrontBackColor()
        self.colorWidget.front_signal[str].connect(self.setFrontColor)
        self.colorWidget.back_signal[str].connect(self.setBackColor)
        
        self.varyAct = QAction(QIcon('./UI/arrows.svg'),'vary',self)
        self.varyAct.setStatusTip('Vary')
        self.varyAct.triggered.connect(self.vary)
        
        self.toolBar.addAction(self.varyAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.pencilAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.lineAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.rectAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.circleAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.fillAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.eraserAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.brushAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.cropAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.dropperAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.stampAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.moveAct)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.colorWidget)
        self.toolBar.setOrientation(Qt.Vertical)
        
    def initDockWidget(self):
        x = 0
        y = 0
        
        self.text = "x: {0},  y: {1}".format(x, y)
                
        self.info_lb = QLabel('',self)
        self.info_lb.setAlignment(Qt.AlignLeft)
        self.info_lb.setStyleSheet("color:white;background-color:#535353;padding:10px;border:1px solid #282828;")
        
        self.main_Fig = QDockWidget('Hist')  # 实例化dockwidget类
        self.main_Fig.setWidget(self.F)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        #self.main_Fig.setObjectName("Figure")
        self.main_Fig.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                                    'QDockWidget:title{color:#cdcdcd;background-color:#424242;border:1px solid #282828;}')
        self.main_Fig.setFeatures(self.main_Fig.DockWidgetFloatable|self.main_Fig.DockWidgetMovable|self.main_Fig.DockWidgetClosable)    #  设置dockwidget的各类属性
        self.main_Fig.setWindowFlags(Qt.FramelessWindowHint)
        #self.main_Fig.setStyleSheet('QDockWidget{border: 1px solid black;}')
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_Fig) 
        self.main_info = QDockWidget('Information')  # 实例化dockwidget类
        self.main_info.setWidget(self.info_lb)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        #self.main_info.setObjectName("Info")
        self.main_info.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#424242;border:1px solid #282828;}')
        self.main_info.setFeatures(self.main_info.DockWidgetFloatable|self.main_info.DockWidgetMovable|self.main_info.DockWidgetClosable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_info) 
        self.layer = LayerMain(self.mcanvas,debug=self.__debug)
        #self.layer.refresh.connect(self.refreshShow)
        #self.mcanvas.changed[int].connect(self.layer.setCurrentLayerStack)
        #self.layer.setStyleSheet('color:white;background-color:#adadad;border:1px solid #adadad;')
        self.layer_dock = QDockWidget('Layer',self)
        self.layer_dock.setWidget(self.layer)
        #self.layer.setStyleSheet('border:1px solid #adadad')
        #self.layer_dock.setObjectName("Info")
        self.layer_dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#535353;border:1px solid #282828;}')
        self.layer_dock.setFeatures(self.layer_dock.DockWidgetFloatable|self.layer_dock.DockWidgetMovable|self.layer_dock.DockWidgetClosable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.layer_dock)
        self.channel_dock = QDockWidget('Channel',self)
        self.channel_dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#535353;border:1px solid #282828;}')
        self.channel_dock.setFeatures(self.channel_dock.DockWidgetFloatable|self.channel_dock.DockWidgetMovable|self.channel_dock.DockWidgetClosable)
        tmp_widget = QWidget(self)
        self.layer_dock.setTitleBarWidget(tmp_widget)
        self.channel_dock.setTitleBarWidget(tmp_widget)
        self.addDockWidget(Qt.RightDockWidgetArea,self.channel_dock)
        self.tabifyDockWidget(self.channel_dock,self.layer_dock)        
    
    def middleware(self):
        self.layer.addLayerStack(self.mcanvas.canvas.layers)
        pass
    
    def CreateDockWidget(self, name, widget):  # 定义一个createDock方法创建一个dockwidget
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(widget)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName("selectQuote")
        dock.setFeatures(dock.DockWidgetFloatable|dock.DockWidgetMovable|dock.DockWidgetClosable)    #  设置dockwidget的各类属性
        dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#535353;}')
        self.addDockWidget(Qt.RightDockWidgetArea, dock)  
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def closeEvent(self, event):
        if not self.__debug:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Save | 
                QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                logger.info('Save files, and close application.')
                flag = self.saveSlot()
                if flag:
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.Discard:
                logger.info("Don\'t save files, and close application.")
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def toggleMenu(self, state):
        
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()
    
    def infoView(self, state):
        if state:
            self.main_info.show()
        else:
            self.main_info.hide()
            
    def histView(self, state):
        if state:
            self.main_Fig.show()
        else:
            self.main_Fig.hide()
    
    def channelView(self, state):
        if state:
            self.channel_dock.show()
        else:
            self.channel_dock.hide()
    
    def setFrontColor(self,colorName):
        self.frontcolor = QColor(colorName)
        
    def setBackColor(self,colorName):
        self.backcolor = QColor(colorName)
    
    def contextMenuEvent(self, event):
       cmenu = QMenu(self)
       
       newAct = cmenu.addAction("New")
       opnAct = cmenu.addAction("Open")
       quitAct = cmenu.addAction("Quit")
       action = cmenu.exec_(self.mapToGlobal(event.pos()))
       
       if action == quitAct:
           #qApp.quit()
           self.close()
       elif action == opnAct:
           self.openimage()
       elif action == newAct:
           self.newBlock()
       else:
           pass
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
    
    def newBlock(self):
        wel = Welcome()
        if wel.exec_() == QDialog.Accepted:
            #self.F.DrawHistogram(self.mcanvas.canvas)
            self.info = 'width: {0}\nheight: {1}'.format(self.mcanvas.canvas.layers.width(),self.mcanvas.canvas.layers.height())
            self.info_lb.setText(self.info)
            self.refreshShow()
    
    def importimage(self):
        imgName,imgType= QFileDialog.getOpenFileName(self,
                                    "打开图片",
                                    "",
                                    " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if imgName is '':
            logger.warning('None Image has been selected!')
            return
        else:
            logger.info('Open image: '+imgName)
        
        self.layer.addLayer(cv2.imread(imgName),imgName.split('/')[-1])
        
        if self.mcanvas.canvas.layers.Image.size == 1:
            return
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'openimage'])
        self.info_lb.setText(self.info)
        self.refreshShow()
        self.center()
        
    def openimage(self):
        imgName,imgType= QFileDialog.getOpenFileName(self,
                                    "打开图片",
                                    "",
                                    " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if imgName is '':
            logger.warning('None Image has been selected!')
            return
        else:
            logger.info('Open image: '+imgName)
        
        #self.layer.addLayer(cv2.imread(imgName),imgName.split('/')[-1])
        im = Image.open(imgName)
        try:
            canvas_dpi = im.info['dpi'][0]
        except:
            canvas_dpi = 72
        canvas_width, canvas_height = im.size
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue('mode',1)
        settings.setValue("width", canvas_width)
        settings.setValue("height", canvas_height)
        #settings.setValue("color", self.canvas_color)
        settings.setValue('dpi',canvas_dpi)
        settings.setValue('imageMode',im.mode)
        settings.setValue('imageFormat',im.format)
        settings.setValue("imagePath",imgName)
        settings.setValue("imageName",imgName.split('/')[-1])
        del im
        self.mcanvas.newCanvas()
        
        if self.mcanvas.canvas.layers.Image.size == 1:
            return
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'openimage'])
        self.info_lb.setText(self.info)
        self.refreshShow()
        self.center()
    
    def saveSlot(self):
        # 调用存储文件dialog
        fileName, tmp = QFileDialog.getSaveFileName(
            self, 'Save Image', 'Untitled', '*.png *.jpg *.bmp', '*.png')

        if fileName is '':
            return False
        if self.mcanvas.canvas.layers.Image.size == 1:
            return False
        # 调用opencv写入图像
        cv2.imwrite(fileName, self.mcanvas.canvas.layers.Image)
        return True
        
    def refreshShow(self,image=None):
        if self.__debug:
            logger.debug('Refresh canvas.')
        self.info = 'width: {0}\t height: {1}\n\ndpi: {2}'.format(round(self.mcanvas.canvas.layers.width()/self.mcanvas.canvas.dpi,2),round(self.mcanvas.canvas.layers.height()/self.mcanvas.canvas.dpi,2),self.mcanvas.canvas.dpi)
        self.info_lb.setText(self.info)
        if image is not None:
            self.mcanvas.canvas.layers.updateCurrentLayerImage(image)
        self.F.DrawHistogram(self.mcanvas.canvas.layers.Image)
    
    def sentSignalToThread(self,content):
        self.send_signal.emit(content)
    
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
        #self.Thr.change('filter',tableName)
        #self.Thr.start()
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'filter','other':tableName})
        #self.showDialog(1)
        logger.info("Doing Filters Successful!")
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'doFilters'])
        self.refreshShow()
        #self.doFilters(tableName)
    
    def AWB(self):
        #self.Thr.change('AWB')
        #self.Thr.start()
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'AWB'})
        #self.showDialog(1)
        logger.info("AWB Successful!")
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'AWB'])
        self.refreshShow()
        
    def ACE(self):
        #self.Thr.change('ACE')
        #self.Thr.start()
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'ACE'})
        #self.showDialog(1)
        logger.info('ACE Successful!')
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'ACE'])
        self.refreshShow()
        
    def ACA(self):
        #self.Thr.change('ACA')
        #self.Thr.start()
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'ACA'})
        #self.showDialog(1)
        logger.info('ACA Successful!')
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'ACA'])
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
                self.mcanvas.canvas.layers.changeImg(img.astype(np.uint8))
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
            self.mcanvas.canvas.layers.changeImg(img.astype(np.uint8))
            logger.info('Redo Operating to ' + op + '!')
        self.refreshShow()
    
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
        '''
        self.removeDockWidget(self.tmp_dock)
        sip.delete(self.tmp_dock)'''
        self.main_toolbar.clear()
        sip.delete(self.adj_b)
    
    def perOpTools(self,s):
        if self.__debug:
            logger.debug('Choose tool:'+s)
        self.mcanvas.canvas.draw.chgType(s)
        self.disPre()
        self.mcanvas.canvas.chgCursor(s)
        self.adj_b = AdjBlock(self.mcanvas.canvas.draw)
        self.adj_b.setColorByName(self.frontcolor.name())
        #self.mcanvas.canvas.draw.ChangePenColor(self.frontcolor)
        '''
        self.tmp_dock = QDockWidget(s+' Attributes')  # 实例化dockwidget类
        self.tmp_dock.setWidget(self.adj_b)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.tmp_dock.setObjectName("Attributes")
        self.tmp_dock.setFeatures(self.tmp_dock.DockWidgetFloatable|self.tmp_dock.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.tmp_dock)'''
        self.main_toolbar.addWidget(self.adj_b)
        #if self.last_tool == '':self.mcanvas.canvas.draw.saveImg()
        self.last_tool = s
        self.refreshShow()
    
    def Anime(self):
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'Anime','other':'./samples/2.jpg'})
        self.OS.push([np.array(self.mcanvas.canvas.layers.Image),'Anime'])
        logger.info('Do Anime Filter Successful!')
        self.refreshShow()
    
    def vary(self):
        self.perOpTools('Vary')
        self.varyAct.setEnabled(False)
    
    def movement(self):
        self.perOpTools("Move")
        self.moveAct.setEnabled(False)
    
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
        self.sentSignalToThread({'img':self.mcanvas.canvas.layers.currentLayer(),'method':'Painter'})
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'Paint'])
        logger.info('Do Anime Painter Successful!')
        self.refreshShow()
    
    def Ink(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'Ink'])
        logger.info('Do Ink Style Transfer Successful!')
        self.refreshShow()
    
    def PencilDrawing(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'PencilDrawing'])
        logger.info('Do Pencil Drawing Successful!')
        self.refreshShow()
    
    def Blur(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'Blur'])
        logger.info('Do Blur Successful!')
        self.refreshShow()
    
    def GaussianBlur(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'GaussianBlur'])
        logger.info('Do Gaussian Blur Successful!')
        self.refreshShow()
    
    def MotionBlur(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'MotionBlur'])
        logger.info('Do Motion Blur Successful!')
        self.refreshShow()
    
    def RadialBlur(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'RadialBlur'])
        logger.info('Do Radial Blur Successful!')
        self.refreshShow()
    
    def SmartBlur(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'SmartBlur'])
        logger.info('Do Smart Blur Successful!')
        self.refreshShow()
    
    def BlurMore(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'BlurMore'])
        logger.info('Do More Blur Successful!')
        self.refreshShow()
    
    def USM(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'USM'])
        logger.info('Do USM Successful!')
        self.refreshShow()
    
    def EdgeSharp(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'EdgeSharp'])
        logger.info('Do Edge Sharp Successful!')
        self.refreshShow()
    
    def SmartSharp(self):
        self.OS.push([np.array(self.mcanvas.canvas.tmp_img.Image),'SmartSharp'])
        logger.info('Do Smart Sharp Successful!')
        self.refreshShow()
    
    def light(self):
        l = AdjDialog(self.mcanvas.canvas.layers,'light')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def comp(self):
        l = AdjDialog(self.mcanvas.canvas.layers,'comp')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def custom(self):
        l = AdjDialog(self.mcanvas.canvas.layers,'custom')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def hue(self):
        l = AdjDialog(self.mcanvas.canvas.layers,'hue')
        if l.exec_() == QDialog.Accepted:
            self.refreshShow()
        return
    
    def canSize(self):
        self.mcanvas.canvas.canResize()
        pass
    
    def imgSize(self):
        self.mcanvas.canvas.imgResize()
        pass
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())