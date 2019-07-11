# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 22:24:44 2019

@author: Quanfita
"""
import sys
from PIL import Image
from PIL.ExifTags import TAGS
import cv2
import logger
from PyQt5.QtWidgets import (QDialog,QLabel,QLineEdit,QApplication,
                             QComboBox,QPushButton,QColorDialog,
                             QFileDialog)
from PyQt5.QtCore import Qt,QRegExp,QSettings
from PyQt5.QtGui import QIcon,QRegExpValidator,QFont,QColor

class Welcome(QDialog):
    
    def __init__(self):
        super(Welcome,self).__init__()
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
        if self.dpi_combox.currentText() == 'px/inch':
            self.dpi_line.setText(str(self.canvas_dpi))
        elif self.dpi_combox.currentText() == 'px/cm':
            self.dpi_line.setText(str(round(self.canvas_dpi/2.54,2)))
        else:
            pass
    
    def countPix(self,text):
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
        print(self.w_line.text(),self.h_line.text(),float(self.w_line.text()))
        print(self.canvas_width,self.canvas_height)
    
    def countHeightPix(self,text):
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
        print(self.w_line.text(),self.h_line.text())
        print(self.canvas_width,self.canvas_height)
    
    def changeColor(self):
        color = QColorDialog.getColor()
        self.color_combox.setCurrentText('Background Color')
        self.color_btn.setStyleSheet("QPushButton{background-color:"+str(color.name())+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.canvas_color = color.name()
    
    def selectColor(self,text):
        if text in ['White','Black','white','black']:
            self.color_btn.setStyleSheet("QPushButton{background-color:"+str(text)+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
            self.canvas_color = QColor(text).name()
    
    def selectPix(self,text):
        if self.dpi_combox.currentText() == 'px/cm':
            tmp_dpi = self.canvas_dpi/2.54
        else:
            tmp_dpi = self.canvas_dpi
        print(self.canvas_width,self.canvas_height)
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
        return self.canvas_color,self.canvas_width,self.canvas_height,self.canvas_dpi
    
    def turnBack(self):
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
        imgName,imgType = QFileDialog.getOpenFileName(self,"打开图片","",
                                                     " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if imgName is '':
            logger.warning('None Image has been selected!')
            return
        else:
            logger.info('ImageName: '+imgName)
        #img = cv2.imread(imgName)
        im = Image.open(imgName)
        logger.info(str(im.format)+str(im.size)+str(im.mode)+str(im.info))
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
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Welcome()
    sys.exit(app.exec_())
        