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
from views.Dialog import SaveDialog
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
from common import utils


class MainWindow(QMainWindow):
    in_signal = pyqtSignal(dict)
    out_signal = pyqtSignal(dict)
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
        self.initSignals()

        self.setWindowTitle('SmartSeed')
        self.setWindowIcon(QIcon('./static/UI/icon_32.png'))        
        self.showMaximized()
        self.show()
        logger.info('Init complited!')
        # self.refreshShow()
    
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

        self.filter_list = ['Portrait','Smooth','Morning','Pop','Accentuate',
                        'Art Style','Black & White','HDR','Modern','Old',
                        'Yellow']

        for i in self.filter_list:
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
        
        self.toollist = {'Vary':self.varyAct,'Pencil':self.pencilAct,'Line':self.lineAct,
                    'Rect':self.rectAct,'Circle':self.circleAct,'Fill-Drip':self.fillAct,
                    'Eraser':self.eraserAct,'Brush':self.brushAct,'Crop':self.cropAct,
                    'Dropper':self.dropperAct,'Stamp':self.stampAct,'Move':self.moveAct,
                    'Zoom':self.zoomAct}
        tl = [i for i in self.toollist.keys()]
        for i in range(len(self.toollist)):
            if i != 0:
                self.toolBar.addSeparator()
            self.toolBar.addAction(self.toollist[tl[i]])
        self.toolBar.addWidget(self.colorWidget)
        self.toolBar.setOrientation(Qt.Vertical)
        
    def initDockWidget(self):
        self.infoDock = InfoLabel()
        self.hist = Hist()
        self.layer = LayerMain(self.mcanvas,debug=self.__debug)
        dock = {'hist':self.hist, 'info':self.infoDock, 'layer':self.layer}
        for key in dock.keys():
            self.createDockWidget(key,dock[key])

    def initSignals(self):
        self.mcanvas.canvas.out_signal[dict].connect(self.sendMsg)
        self.mcanvas.out_signal[dict].connect(self.sendMsg)
        self.layer.out_signal[dict].connect(self.sendMsg)

    def createDockWidget(self, name, widget):  # 定义一个createDock方法创建一个dockwidget
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(widget)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName("selectQuote")
        dock.setFeatures(dock.DockWidgetFloatable|dock.DockWidgetMovable|dock.DockWidgetClosable)    #  设置dockwidget的各类属性
        dock.setStyleSheet('QDockWidget:QWidget{color:white;background-color:#535353;border:1px solid #282828;}'
                            'QDockWidget:title{color:#cdcdcd;background-color:#535353;}')
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def sendMsg(self, content={}):
        sender = self.sender()
        try:
            logger.debug("Sender: "+str(sender))
            name = sender.text()
        except:
            print(content)
            name = content['type']
            logger.debug('MainWindow request message: '+str(name)+', '+str(content))
        if name in ['Open','Import image']:
            if name == 'Open':
                res = utils.openImage(self)
                if res:
                    self.mcanvas.newCanvas()
                    send_data = {'data':res,'callback':self.refreshShow,'type':name,'togo':'layer'}
                    self.out_signal.emit(send_data)
            elif name == 'Import image':
                res = utils.openImage(self)
                res['index'] = len(self.layer.layer_list.list_names)
                send_data = {'data':res,'callback':self.refreshShow,'type':name,'togo':'layer'}
                self.out_signal.emit(send_data)
                # self.layer.in_signal.emit(send_data)
                # self.layer.addLayer(res['image'].image,res['image_name'])
        elif name == 'Save':
            save = SaveDialog(self)
            save.exec_()
        elif name == 'refresh':
            self.refreshShow()
        elif name in ['exchange','dellayer','cpylayer','sltlayer','newlayer']:
            content['callback'] = self.refreshShow
            self.out_signal.emit(content)
        elif name in ['vary','move','pencil','line','rect','stamp','dropper','circle','brush','eraser','fill','zoom']:
            self.perOpTools(name)
        elif name in self.filter_list:
            data = {'data':{'filter':name},'type':'filter','togo':'thread','callback':self.refreshShow}
            self.out_signal.emit(data)
        elif name == 'getRect':
            self.out_signal.emit(content)
        elif name == 'draw':
            content['callback'] = self.refreshShow
            if content['data']['mode'] == 'dropper':
                content['data']['callback'] = self.colorWidget.changeFrontColor
            self.out_signal.emit(content)
        elif name == 'color':
            self.mcanvas.setFBColor(content['data']['front'])

    def refreshShow(self,imgobj=None):
        if self.__debug:
            logger.debug('Refresh canvas.')
        # self.info = 'width: {0}\t height: {1}\n\ndpi: {2}'.format(round(imgobj.width()/imgobj.dpi,2),round(imgobj.height()/imgobj.dpi,2),imgobj.dpi)

        if imgobj is not None:
            # self.infoDock.setLabelText({'x':imgobj.width(),'y':imgobj.height()})
            # self.layer.updateCurrentLayerImage(imgobj.Image)
            self.mcanvas.canvas.draw.refresh(imgobj)
            self.hist.DrawHistogram(imgobj)

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

    def saveSlot(self):
        SaveDialog(self)

    def disPre(self):
        if self.last_tool in self.toollist.keys():
            self.toollist[self.last_tool].setEnabled(True)
        else:
            return
        # if self.last_tool == 'Pencil':
        #     self.pencilAct.setEnabled(True)
        # elif self.last_tool == 'Line':
        #     self.lineAct.setEnabled(True)
        # elif self.last_tool == 'Rect':
        #     self.rectAct.setEnabled(True)
        # elif self.last_tool == 'Circle':
        #     self.circleAct.setEnabled(True)
        # elif self.last_tool == 'Fill':
        #     self.fillAct.setEnabled(True)
        # elif self.last_tool == 'Crop':
        #     self.cropAct.setEnabled(True)
        # elif self.last_tool == 'Dropper':
        #     self.dropperAct.setEnabled(True)
        # elif self.last_tool == 'Eraser':
        #     self.eraserAct.setEnabled(True)
        # elif self.last_tool == 'Brush':
        #     self.brushAct.setEnabled(True)
        # elif self.last_tool == 'Stamp':
        #     self.stampAct.setEnabled(True)
        # elif self.last_tool == 'Vary':
        #     self.varyAct.setEnabled(True)
        # else: return
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
        # self.mcanvas.canvas.chgCursor(s)
        # self.mcanvas.canvas.draw.chgType(s)
        # self.adj_b = AdjBlock(self.mcanvas.canvas.draw)
        # self.adj_b.setColorByName(self.frontcolor.name())
        #self.mcanvas.canvas.draw.ChangePenColor(self.frontcolor)
        '''
        self.tmp_dock = QDockWidget(s+' Attributes')  # 实例化dockwidget类
        self.tmp_dock.setWidget(self.adj_b)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.tmp_dock.setObjectName("Attributes")
        self.tmp_dock.setFeatures(self.tmp_dock.DockWidgetFloatable|self.tmp_dock.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.tmp_dock)'''
        # self.main_toolbar.addWidget(self.adj_b)
        #if self.last_tool == '':self.mcanvas.canvas.draw.saveImg()
        self.last_tool = s
        self.refreshShow()
