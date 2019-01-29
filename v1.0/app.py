# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:09:14 2019

@author: Quanfita
"""

import sys
import cv2
import sip
import ops
from pencil import Draw, AdjBlock
import numpy as np
from Thread import ProThread
from ImgObj import ImgObject
from Figure import MyFigure
from Stack import OpStack
from LayerView import LayerBox
from Welcome import Welcome
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, 
                             QPushButton, QMessageBox, QDesktopWidget, 
                             QMainWindow, QAction, qApp, QMenu, 
                             QSlider, QLabel, QFileDialog, 
                             QDialog, QGroupBox, QDialogButtonBox, 
                             QGridLayout, QSplitter, QDockWidget, 
                             QToolBar,QProgressDialog)
from PyQt5.QtGui import QIcon, QFont


class Example(QMainWindow,QDialog):
    
    def __init__(self):
        #super().__init__()
        super(Example,self).__init__()
        self.OS = OpStack()
        #self.setMouseTracking(False)
        self.pos_xy = []
        self.img = ImgObject()
        self.Thr = ProThread(self.img)
        self.F = MyFigure(width=3, height=2, dpi=100)
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
        
        undoAct = QAction(QIcon('./UI/undo.svg'),'Undo',self)
        undoAct.setShortcut('Ctrl+Z')
        undoAct.setStatusTip('Undo The Last Operating')
        undoAct.triggered.connect(self.Undo)
        
        filter0 = QAction('filter0',self)
        filter0.setStatusTip("filter0")
        filter0.triggered.connect(self.setTable)
        filter1 = QAction('filter1',self)
        filter1.setStatusTip("filter1")
        filter1.triggered.connect(self.setTable)
        filter2 = QAction('filter2',self)
        filter2.setStatusTip("filter2")
        filter2.triggered.connect(self.setTable)
        filter3 = QAction('filter3',self)
        filter3.setStatusTip("filter3")
        filter3.triggered.connect(self.setTable)
        filter4 = QAction('filter4',self)
        filter4.setStatusTip("filter4")
        filter4.triggered.connect(self.setTable)
        filter5 = QAction('filter5',self)
        filter5.setStatusTip("filter5")
        filter5.triggered.connect(self.setTable)
        filter6 = QAction('filter6',self)
        filter6.setStatusTip("filter6")
        filter6.triggered.connect(self.setTable)
        filter7 = QAction('filter7',self)
        filter7.setStatusTip("filter7")
        filter7.triggered.connect(self.setTable)
        filter8 = QAction('filter8',self)
        filter8.setStatusTip("filter8")
        filter8.triggered.connect(self.setTable)
        filter9 = QAction('filter9',self)
        filter9.setStatusTip("filter9")
        filter9.triggered.connect(self.setTable)
        filter10 = QAction('filter10',self)
        filter10.setStatusTip("filter10")
        filter10.triggered.connect(self.setTable)
        
        AnimeFilter = QAction('Anime',self)
        AnimeFilter.setStatusTip('Anime Filter')
        AnimeFilter.triggered.connect(self.Anime)
        
        tra_filter = QMenu('Traditional Filter',self)
        blurry_filter = QMenu('Blurry Filter',self)
        sharpen_filter = QMenu('Sharpen Filter',self)
        filter_lib = QMenu('Filter Library',self)
        filter_lib.addAction(AnimeFilter)
        
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
        self.main_toolbar.addAction(exitAct)
        
        self.toolBar.addAction(self.pencilAct)
        self.toolBar.addAction(self.lineAct)
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
        
        adjustMenu = QMenu('Adjustment',self)
        
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
        imageMenu.addMenu(adjustMenu)
        
        editMenu = menubar.addMenu('Edit')
        editMenu.addAction(undoAct)
        
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
        self.label = Draw(self.OS,self.img,self.refreshShow)
        self.label.setAlignment(Qt.AlignCenter)
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
        main_info = QDockWidget('Information')  # 实例化dockwidget类
        main_info.setWidget(self.info_lb)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        main_info.setObjectName("Info")
        main_info.setFeatures(main_info.DockWidgetFloatable|main_info.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, main_info) 
        self.layer = LayerBox()
        self.layer_dock = QDockWidget('Layer')
        self.layer_dock.setWidget(self.layer)
        self.layer_dock.setObjectName("Info")
        self.layer_dock.setFeatures(main_info.DockWidgetFloatable|main_info.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.layer_dock)
        self.refreshShow()
        #splitter  =  QSplitter(self)
        #splitter.addWidget(self.label)
        #splitter.addWidget(self.F)
        #splitter.setOpaqueResize(False)
        #splitter.setOrientation(Qt.Vertical)
        self.setCentralWidget(self.label)
        
        self.resize(1366, 768)
        self.center()
        self.setWindowTitle('SmartSeed')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))        
        #self.showMaximized()
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
    
    def showFigure(self):
        try:
            self.removeDockWidget(self.main_Fig)
            sip.delete(self.main_Fig)
            sip.delete(self.F)
        except:
            print('Initial Figure!')
        self.F = MyFigure(width=3, height=2, dpi=100)
        self.main_Fig = QDockWidget('Figure')  # 实例化dockwidget类
        self.main_Fig.setWidget(self.F)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.main_Fig.setObjectName("Figure")
        self.main_Fig.setFeatures(self.main_Fig.DockWidgetFloatable|self.main_Fig.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.main_Fig) 
        try:
            self.F.DrawHistogram(self.img.Image)
            print("Draw Histogram!")
        except:
            print('None Image!')
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
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
            self.img.reset()
            #self.F.DrawHistogram(self.img)
            self.info = 'width: {0}\nheight: {1}'.format(self.img.width,self.img.height)
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
            return
        else:
            print(imgName)
        
        self.img.changeImg(cv2.imread(imgName))
        
        if self.img.Image.size == 1:
            return
        self.OS.push([np.array(self.img.Image),'openimage'])
        self.info = 'width: {0}\nheight: {1}'.format(self.img.width,self.img.height)
        self.info_lb.setText(self.info)
        #self.F.DrawHistogram(self.img)
        self.refreshShow()
        self.resize(int(1.5*self.img.width),int(1.2*self.img.height))
        self.center()
    
    def saveSlot(self):
        # 调用存储文件dialog
        fileName, tmp = QFileDialog.getSaveFileName(
            self, 'Save Image', self.img.imgName, '*.png *.jpg *.bmp', '*.png')

        if fileName is '':
            return
        if self.img.Image.size == 1:
            return
        # 调用opencv写入图像
        cv2.imwrite(fileName, self.img.Image)
        
    def refreshShow(self):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        #height, width, channel = self.img.shape
        #bytesPerLine = 3 * width
        #self.qImg = QImage(self.img.data, width, height, bytesPerLine,
                           #QImage.Format_RGB888).rgbSwapped()
        # 将Qimage显示出来
        self.info = 'width: {0}\nheight: {1}'.format(self.img.width,self.img.height)
        self.info_lb.setText(self.info)
        self.showFigure()
        self.label.setPixmap(ops.cvtCV2Pixmap(self.img.Image))
        cv2.imwrite('./tmp/error.jpg',self.img.Image)
        #self.label.resize(self.img.shape[1],self.img.shape[0])
        #self.canvas = QPixmap.fromImage(self.qImg)
        #self.F.DrawHistogram(self.img)
        self.chgSize()
    
    '''
    def doFilters(self,tableName):
        ori = cv2.imread('./tables/lookup-table.png')
        new = cv2.imread('./tables/'+tableName)
        self.showDialog()
        self.img.changeImg(Filter().myFilter(ori,new,self.img.Image))
        print("Doing Filters Successful!")
        self.OS.push([np.array(self.img.Image),'doFilters'])
        self.refreshShow()
    '''
    def setTable(self):
        sender = self.sender()
        tm = sender.text()
        print(tm)
        if tm == 'filter0':
            tableName = 'lookup-table_1.jpg'
        elif tm == 'filter1':
            tableName = 'lookup-table_2.jpg'
        elif tm == 'filter2':
            tableName = 'lookup-table_3.jpg'
        elif tm == 'filter3':
            tableName = 'lookup-table_4.jpg'
        elif tm == 'filter4':
            tableName = 'lookup-table_5.jpg'
        elif tm == 'filter5':
            tableName = 'lookup-table_6.jpg'
        elif tm == 'filter6':
            tableName = 'lookup-table_B&W.jpg'
        elif tm == 'filter7':
            tableName = 'lookup-table_hdr.jpg'
        elif tm == 'filter8':
            tableName = 'lookup-table_li.jpg'
        elif tm == 'filter9':
            tableName = 'lookup-table_old.jpg'
        elif tm == 'filter10':
            tableName = 'lookup-table-yellow.png'
        else:
            return
        self.Thr.change('filter',tableName)
        self.Thr.start()
        self.showDialog(5)
        print("Doing Filters Successful!")
        self.OS.push([np.array(self.img.Image),'doFilters'])
        self.refreshShow()
        #self.doFilters(tableName)
    
    def AWB(self):
        self.Thr.change('AWB')
        self.Thr.start()
        self.showDialog()
        print("AWB Successful!")
        self.OS.push([np.array(self.img.Image),'AWB'])
        self.refreshShow()
        
    def ACE(self):
        self.Thr.change('ACE')
        self.Thr.start()
        self.showDialog()
        print('ACE Successful!')
        self.OS.push([np.array(self.img.Image),'ACE'])
        self.refreshShow()
    
    def Undo(self):
        if self.OS.size() >= 2:
            [img,op] = self.OS.pop()
            if self.OS.isEmpty():
                self.label = ''
                print('No Operating Has Been Done!')
                return
            else:
                [img,op] = self.OS.pop()
                self.OS.push([img,op])
                self.img.changeImg(img.astype(np.uint8))
                self.label.Clean()
                print('Undo Operating to '+op+'!')
        else:
            print('No Operating Has Been Done!')
        self.refreshShow()
    
    def showevent(self,event):
        self.chgSize()
    
    def moveEvent(self,event):
        self.chgSize()
    
    def resizeEvent(self,event):
        self.chgSize()
    
    def chgSize(self):

        self.label.lb_x = (self.label.width() - self.img.width)//2
        self.label.lb_y = (self.label.height() - self.img.height)//2
        self.label.lb_w = self.img.width
        self.label.lb_h = self.img.height
        #print(self.label.width(),self.label.height())
        #print(self.label.geometry().x(),self.label.geometry().y())
        #print(self.label.lb_x,self.label.lb_y,self.label.lb_w,self.label.lb_h)

    def disPre(self):
        if self.last_tool == 'Pencil':
            self.pencilAct.setEnabled(True)
            self.removeDockWidget(self.pencil_dock)
            sip.delete(self.pencil_dock)
        elif self.last_tool == 'Line':
            self.lineAct.setEnabled(True)
            self.removeDockWidget(self.line_dock)
            sip.delete(self.line_dock)
    
    def pencil(self):
        self.label.chgType("Pencil")
        self.disPre()
        self.pencilAct.setEnabled(False)
        self.label.setCursor(Qt.CrossCursor)
        self.adj_b = AdjBlock(self.label)
        self.pencil_dock = QDockWidget('Pencil Attributes')  # 实例化dockwidget类
        self.pencil_dock.setWidget(self.adj_b)   # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        self.pencil_dock.setObjectName("Attributes")
        self.pencil_dock.setFeatures(self.pencil_dock.DockWidgetFloatable|self.pencil_dock.DockWidgetMovable)    #  设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, self.pencil_dock)
        self.label.saveImg()
        self.last_tool = 'Pencil'
        self.refreshShow()
        
    def line(self):
        self.label.chgType('Line')
        self.disPre()
        self.lineAct.setEnabled(False)
        self.label.setCursor(Qt.CrossCursor)
        self.adj_b = AdjBlock(self.label)
        self.line_dock = QDockWidget('Line Attributes')
        self.line_dock.setWidget(self.adj_b)
        self.line_dock.setObjectName('Attributes')
        self.line_dock.setFeatures(self.line_dock.DockWidgetFloatable|self.line_dock.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.line_dock)
        self.label.saveImg()
        self.last_tool = 'Line'
        self.refreshShow()
        
    
    def showDialog(self,tar=10):
        num = self.img.pixNum*tar
        self.progress = QProgressDialog(self)
        self.progress.setWindowTitle("请稍等")  
        self.progress.setLabelText("正在操作...")
        self.progress.setCancelButtonText("取消")
        self.progress.setMinimumDuration(5)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setRange(0,num) 
        for i in range(num):
            if i >= num//2 and self.Thr.isRunning():
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
        self.showDialog(15)
        self.OS.push([np.array(self.img.Image),'Anime'])
        print('Do Anime Filter Successful!')
        self.refreshShow()
    
    def fill(self):
        pass
    
    def crop(self):
        pass
    
    def dropper(self):
        pass
    
    def eraser(self):
        pass
    
    def brush(self):
        pass
    
    def stamp(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())