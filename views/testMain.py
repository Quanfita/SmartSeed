# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:09:14 2019

@author: Quanfita
"""

import sys
import cv2
import sip
# import logger
from PIL import Image
# from views import AdjBlock, Canvas, MutiCanvas, FrontBackColor, LayerMain, Welcome, Hist, AdjDialog
import numpy as np
# from Stack import OpStack
from views.Canvas import MutiCanvas, Canvas
from views.DockWidget import InfoLabel, Hist, FrontBackColor
from views.Layer import LayerMain
from common.app import logger
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



class MainWindow(QMainWindow):
    main_signal = pyqtSignal(dict)
    def __init__(self,debug=False):
        #super().__init__()
        super(MainWindow,self).__init__()
        self.__debug = debug
        self.setStyleSheet( 'QMainWindow{color:white;background-color:#424242;}'
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
        # self.OS = OpStack()
        #self.setMouseTracking(False)
        # self.pos_xy = []
        self.mcanvas = MutiCanvas(debug=self.__debug)
        self.mcanvas.canvas = Canvas()
        #self.mcanvas.refresh.connect(self.refreshShow)
        #self.mcanvas.added.connect(self.middleware)
        # self.mcanvas.addTab(self.mcanvas.canvas,'1')
        #self.Thr = ProThread(self.mcanvas.canvas.layers)
        # self.F = Hist()
        #self.F = MyFigure(width=3, height=2, dpi=100)
        self.last_tool = ''
        self.frontcolor = QColor('white')
        self.backcolor = QColor('black')
        self.initUI()
        
    def initUI(self):
        #self.setWindowFlags(Qt.CustomizeWindowHint)

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setCentralWidget(self.mcanvas)
        self.setDockNestingEnabled(True)
        self.setMinimumSize(800,480)
        self.resize(1366, 768)
        #self.center()

        self.initMenu()
        self.initToolBar()
        self.initDockWidget()

        self.setWindowTitle('SmartSeed')
        self.setWindowIcon(QIcon('./static/UI/icon_32.png'))        
        self.showMaximized()
        self.show()
        logger.info('Init complited!')
        self.refreshShow()
    
    def initMenu(self):
        exitAct = QAction(QIcon('./static/UI/exit.svg'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
                
        openFile = QAction(QIcon('./static/UI/open.svg'),'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new Image')
        openFile.triggered.connect(self.sendMsg)
        
        saveFile = QAction(QIcon('./static/UI/save.svg'),'Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save this Image')
        saveFile.triggered.connect(self.sendMsg)
        
        AWBAct = QAction('AWB',self)
        AWBAct.setStatusTip('Auto White Balance')
        AWBAct.triggered.connect(self.sendMsg)
        
        ACEAct = QAction('ACE',self)
        ACEAct.setStatusTip('Auto Color Equalization')
        ACEAct.triggered.connect(self.sendMsg)
        
        ACAAct = QAction('ACA',self)
        ACAAct.setStatusTip('Auto Contrast Adjustment')
        ACAAct.triggered.connect(self.sendMsg)
        
        cansizeAct = QAction('CanvasSize',self)
        cansizeAct.setStatusTip('Resize the canvas')
        cansizeAct.triggered.connect(self.sendMsg)
        
        imgsizeAct = QAction('ImageSize',self)
        imgsizeAct.setStatusTip('Resize the image')
        imgsizeAct.triggered.connect(self.sendMsg)
        
        undoAct = QAction(QIcon('./static/UI/undo.svg'),'Undo',self)
        undoAct.setShortcut('Ctrl+Z')
        undoAct.setStatusTip('Undo The Last Operating')
        undoAct.triggered.connect(self.sendMsg)
        
        redoAct = QAction(QIcon('./static/UI/redo.svg'),'Redo',self)
        redoAct.setStatusTip('Redo The Last Operating')
        redoAct.triggered.connect(self.sendMsg)
        
        AnimeFilter = QAction('Anime',self)
        AnimeFilter.setStatusTip('Anime Filter')
        AnimeFilter.triggered.connect(self.sendMsg)
        
        PainterAct = QAction('Painter',self)
        PainterAct.setStatusTip('Anime Painter')
        PainterAct.triggered.connect(self.sendMsg)
        
        InkAct = QAction('Ink',self)
        InkAct.setStatusTip('Ink Style Transfer')
        InkAct.triggered.connect(self.sendMsg)
        
        PencilDrawAct = QAction('PencilDrawing',self)
        PencilDrawAct.setStatusTip('Pencil Drawing')
        PencilDrawAct.triggered.connect(self.sendMsg)
        
        blurAct = QAction('Blur',self)
        blurAct.setStatusTip('Blur')
        blurAct.triggered.connect(self.sendMsg)
        
        blurMoreAct = QAction('BlurMore',self)
        blurMoreAct.setStatusTip('Blur More')
        blurMoreAct.triggered.connect(self.sendMsg)
        
        GaussianblurMoreAct = QAction('GaussianBlur',self)
        GaussianblurMoreAct.setStatusTip('Gaussian Blur')
        GaussianblurMoreAct.triggered.connect(self.sendMsg)
        
        MotionblurAct = QAction('MotionBlur',self)
        MotionblurAct.setStatusTip('Motion Blur')
        MotionblurAct.triggered.connect(self.sendMsg)
        
        RadialblurAct = QAction('RadialBlur',self)
        RadialblurAct.setStatusTip('Radial Blur')
        RadialblurAct.triggered.connect(self.sendMsg)
        
        SmartblurAct = QAction('SmartBlur',self)
        SmartblurAct.setStatusTip('Smart Blur')
        SmartblurAct.triggered.connect(self.sendMsg)
        
        usmAct = QAction('USM',self)
        usmAct.setStatusTip('USM')
        usmAct.triggered.connect(self.sendMsg)
        
        EdgeSharpAct = QAction('EdgeSharp',self)
        EdgeSharpAct.setStatusTip('Edge Sharp')
        EdgeSharpAct.triggered.connect(self.sendMsg)
        
        SmartSharpAct = QAction('SmartSharp',self)
        SmartSharpAct.setStatusTip('Smart Sharp')
        SmartSharpAct.triggered.connect(self.sendMsg)
        
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
        
        newAct = QAction(QIcon('./static/UI/new.svg'),'New', self)
        newAct.setShortcut('Ctrl+N')
        newAct.setStatusTip('Create A Write Block')
        newAct.triggered.connect(self.sendMsg)
                
        LightAct = QAction('Light',self)
        LightAct.triggered.connect(self.sendMsg)
        compAct = QAction('Comp',self)
        compAct.triggered.connect(self.sendMsg)
        customAct = QAction('Custom',self)
        customAct.triggered.connect(self.sendMsg)
        hueAct = QAction('Hue',self)
        hueAct.triggered.connect(self.sendMsg)
        
        adjustMenu = QMenu('Adjustment',self)
        adjustMenu.addAction(LightAct)
        adjustMenu.addAction(compAct)
        adjustMenu.addAction(customAct)
        adjustMenu.addAction(hueAct)
        
        impMenu = QMenu('Import', self)
        impAct = QAction('Import image', self)
        impAct.setShortcut('Ctrl+I')
        impAct.setStatusTip('Import new Image')
        impAct.triggered.connect(self.sendMsg)
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

        filter_list = ['Portrait','Smooth','Morning','Pop','Accentuate',
                        'Art Style','Black & White','HDR','Modern','Old',
                        'Yellow']

        for i in filter_list:
            _filter = QAction(i,self)
            _filter.setStatusTip(i)
            _filter.triggered.connect(self.sendMsg)
            tra_filter.addAction(_filter)
        
        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.sendMsg)
        
        infoViewAct = QAction('Information',self, checkable=True)
        infoViewAct.setStatusTip('View information')
        infoViewAct.setChecked(True)
        infoViewAct.triggered.connect(self.sendMsg)
        
        channelViewAct = QAction('Channel',self, checkable=True)
        channelViewAct.setStatusTip('View channel')
        channelViewAct.setChecked(True)
        channelViewAct.triggered.connect(self.sendMsg)
        
        histViewAct = QAction('Hist',self, checkable=True)
        histViewAct.setStatusTip('View hist')
        histViewAct.setChecked(True)
        histViewAct.triggered.connect(self.sendMsg)
                                      
        aboutAct = QAction(QIcon('./static/UI/info.svg'),'About',self)
        
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
        
        self.pencilAct = QAction(QIcon('./static/UI/pen.svg'),'pencil',self)
        self.pencilAct.setStatusTip('Pencil')
        self.pencilAct.triggered.connect(self.sendMsg)
        
        self.lineAct = QAction(QIcon('./static/UI/line.svg'),'line',self)
        self.lineAct.setStatusTip('Line')
        self.lineAct.triggered.connect(self.sendMsg)
        
        self.rectAct = QAction(QIcon('./static/UI/square.svg'),'rect',self)
        self.rectAct.setStatusTip('Rect')
        self.rectAct.triggered.connect(self.sendMsg)
        
        self.circleAct = QAction(QIcon('./static/UI/circle.svg'),'circle',self)
        self.circleAct.setStatusTip('Circle')
        self.circleAct.triggered.connect(self.sendMsg)
        
        self.cropAct = QAction(QIcon('./static/UI/crop.svg'),'crop',self)
        self.cropAct.setStatusTip('Crop')
        self.cropAct.triggered.connect(self.sendMsg)
        
        self.brushAct = QAction(QIcon('./static/UI/paint-brush.svg'),'brush',self)
        self.brushAct.setStatusTip('Brush')
        self.brushAct.triggered.connect(self.sendMsg)
        
        self.eraserAct = QAction(QIcon('./static/UI/eraser.svg'),'eraser',self)
        self.eraserAct.setStatusTip('Eraser')
        self.eraserAct.triggered.connect(self.sendMsg)
        
        self.dropperAct = QAction(QIcon('./static/UI/dropper.svg'),'dropper',self)
        self.dropperAct.setStatusTip('Dropper')
        self.dropperAct.triggered.connect(self.sendMsg)
        
        self.fillAct = QAction(QIcon('./static/UI/fill-drip.svg'),'fill',self)
        self.fillAct.setStatusTip('Fill-Drip')
        self.fillAct.triggered.connect(self.sendMsg)
        
        self.stampAct = QAction(QIcon('./static/UI/stamp.svg'),'stamp',self)
        self.stampAct.setStatusTip('Stamp')
        self.stampAct.triggered.connect(self.sendMsg)
        
        self.moveAct = QAction(QIcon('./static/UI/hand-paper.svg'),'move',self)
        self.moveAct.setStatusTip('Move')
        self.moveAct.triggered.connect(self.sendMsg)
        
        self.colorWidget = FrontBackColor()
        self.colorWidget.signal[dict].connect(self.sendMsg)
        
        self.varyAct = QAction(QIcon('./static/UI/arrows.svg'),'vary',self)
        self.varyAct.setStatusTip('Vary')
        self.varyAct.triggered.connect(self.sendMsg)
        
        self.zoomAct = QAction(QIcon('./static/UI/search.svg'),'zoom',self)
        self.zoomAct.setStatusTip('Zoom')
        self.zoomAct.triggered.connect(self.sendMsg)
        
        toollist = {'Vary':self.varyAct,'Pencil':self.pencilAct,'Line':self.lineAct,
                    'Rect':self.rectAct,'Circle':self.circleAct,'Fill-Drip':self.fillAct,
                    'Eraser':self.eraserAct,'Brush':self.brushAct,'Crop':self.cropAct,
                    'Dropper':self.dropperAct,'Stamp':self.stampAct,'Move':self.moveAct,
                    'Zoom':self.zoomAct}
        tl = [i for i in toollist.keys()]
        for i in range(len(toollist)):
            if i != 0:
                self.toolBar.addSeparator()
            self.toolBar.addAction(toollist[tl[i]])
        self.toolBar.addWidget(self.colorWidget)
        self.toolBar.setOrientation(Qt.Vertical)
        
    def initDockWidget(self):
        self.infoDock = InfoLabel()
        self.hist = Hist()
        self.layer = LayerMain(self.mcanvas,debug=self.__debug)
        dock = {'hist':self.hist, 'info':self.infoDock, 'layer':self.layer}
        for key in dock.keys():
            self.createDockWidget(key,dock[key])
        # self.main_Fig = QDockWidget('Hist')  # 实例化dockwidget类
        # self.main_Fig.setWidget(self.F)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        # #self.main_Fig.setObjectName("Figure")
        # self.main_Fig.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
        #                             'QDockWidget:title{color:#cdcdcd;background-color:#424242;border:1px solid #282828;}')
        # self.main_Fig.setFeatures(self.main_Fig.DockWidgetFloatable|self.main_Fig.DockWidgetMovable|self.main_Fig.DockWidgetClosable)    #  设置dockwidget的各类属性
        # self.main_Fig.setWindowFlags(Qt.FramelessWindowHint)
        #self.main_Fig.setStyleSheet('QDockWidget{border: 1px solid black;}')
        # self.addDockWidget(Qt.RightDockWidgetArea, self.main_Fig) 
        # self.main_info = QDockWidget('Information')  # 实例化dockwidget类
        # self.main_info.setWidget(self.info_lb)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        #self.main_info.setObjectName("Info")
        # self.main_info.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
        #                     'QDockWidget:title{color:#cdcdcd;background-color:#424242;border:1px solid #282828;}')
        # self.main_info.setFeatures(self.main_info.DockWidgetFloatable|self.main_info.DockWidgetMovable|self.main_info.DockWidgetClosable)    #  设置dockwidget的各类属性
        # self.addDockWidget(Qt.RightDockWidgetArea, self.main_info) 
        # self.layer = LayerMain(self.mcanvas,debug=self.__debug)
        #self.layer.refresh.connect(self.refreshShow)
        #self.mcanvas.changed[int].connect(self.layer.setCurrentLayerStack)
        #self.layer.setStyleSheet('color:white;background-color:#adadad;border:1px solid #adadad;')
        # self.layer_dock = QDockWidget('Layer',self)
        # self.layer_dock.setWidget(self.layer)
        #self.layer.setStyleSheet('border:1px solid #adadad')
        #self.layer_dock.setObjectName("Info")
        # self.layer_dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
        #                     'QDockWidget:title{color:#cdcdcd;background-color:#535353;border:1px solid #282828;}')
        # self.layer_dock.setFeatures(self.layer_dock.DockWidgetFloatable|self.layer_dock.DockWidgetMovable|self.layer_dock.DockWidgetClosable)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.layer_dock)
        # self.channel_dock = QDockWidget('Channel',self)
        # self.channel_dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
        #                     'QDockWidget:title{color:#cdcdcd;background-color:#535353;border:1px solid #282828;}')
        # self.channel_dock.setFeatures(self.channel_dock.DockWidgetFloatable|self.channel_dock.DockWidgetMovable|self.channel_dock.DockWidgetClosable)
        # tmp_widget = QWidget(self)
        # self.layer_dock.setTitleBarWidget(tmp_widget)
        # self.channel_dock.setTitleBarWidget(tmp_widget)
        # self.addDockWidget(Qt.RightDockWidgetArea,self.channel_dock)
        # self.tabifyDockWidget(self.channel_dock,self.layer_dock)

    def createDockWidget(self, name, widget):  # 定义一个createDock方法创建一个dockwidget
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(widget)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName("selectQuote")
        dock.setFeatures(dock.DockWidgetFloatable|dock.DockWidgetMovable|dock.DockWidgetClosable)    #  设置dockwidget的各类属性
        dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#535353;}')
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def sendMsg(self, connect={}):
        pass

    def sendToolMsg(self, connect={}):
        pass

    def sendMenuMsg(self, connect={}):
        pass

    def refreshShow(self,image=None):
        if self.__debug:
            logger.debug('Refresh canvas.')
        self.info = 'width: {0}\t height: {1}\n\ndpi: {2}'.format(round(self.mcanvas.canvas.layers.width()/self.mcanvas.canvas.dpi,2),round(self.mcanvas.canvas.layers.height()/self.mcanvas.canvas.dpi,2),self.mcanvas.canvas.dpi)
        self.infoDock.setText(self.info)
        if image is not None:
            self.mcanvas.canvas.layers.updateCurrentLayerImage(image)
        self.hist.DrawHistogram(self.mcanvas.canvas.layers.Image)