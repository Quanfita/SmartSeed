# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 22:24:44 2019

@author: Quanfita
"""
import sys
from PyQt5.QtWidgets import (QDialog,QLabel,QLineEdit,QApplication,
                             QComboBox,QPushButton,QColorDialog)
from PyQt5.QtCore import Qt,QRegExp,QSettings
from PyQt5.QtGui import QIcon,QRegExpValidator,QFont,QColor

class Welcome(QDialog):
    
    def __init__(self):
        super(Welcome,self).__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.canvas_color = '#FFFFFF'
        self.canvas_width = 512
        self.canvas_height = 512
        self.resize(640, 480)
        self.setWindowTitle('New Canvas')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        
        self.main_lb = QLabel('New Canvas',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(220,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        
        self.w_lb = QLabel('width:',self)
        self.w_lb.setAlignment(Qt.AlignLeft)
        self.w_lb.setGeometry(180,120,80,30)
        
        self.h_lb = QLabel('height:',self)
        self.h_lb.setAlignment(Qt.AlignLeft)
        self.h_lb.setGeometry(180,200,80,30)
        
        self.w_line = QLineEdit(self)
        self.w_line.installEventFilter(self)
        self.w_line.setGeometry(180,160,50,30)
        self.w_line.setPlaceholderText('512')
        
        self.h_line = QLineEdit(self)
        self.h_line.installEventFilter(self)
        self.h_line.setGeometry(180,240,50,30)
        self.h_line.setPlaceholderText('512')
        
        self.color_lb = QLabel('BackGround Content:',self)
        self.color_lb.setAlignment(Qt.AlignLeft)
        self.color_lb.setGeometry(180,280,150,30)
        
        pix_info = ['px','cm','inch']
        self.pix_combox = QComboBox(self)
        self.pix_combox.addItems(pix_info)
        self.pix_combox.setGeometry(250,160,100,30)
        
        self.color_btn = QPushButton(self)
        self.color_btn.setGeometry(350,320,30,30)
        self.color_btn.setStyleSheet("QPushButton{background-color:white}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.color_btn.clicked.connect(self.changeColor)
        
        color_info = ['White','Black','Background Color']
        self.color_combox = QComboBox(self)
        self.color_combox.addItems(color_info)
        self.color_combox.setGeometry(180,320,150,30)
        self.color_combox.activated[str].connect(self.select)
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(350,400,80,30)
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
    
    def changeColor(self):
        color = QColorDialog.getColor()
        print(color.name())
        self.color_combox.setCurrentText('Background Color')
        self.color_btn.setStyleSheet("QPushButton{background-color:"+str(color.name())+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.canvas_color = color.name()
    
    def select(self,text):
        if text in ['White','Black','white','black']:
            self.color_btn.setStyleSheet("QPushButton{background-color:"+str(text)+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
            self.canvas_color = QColor(text).name()
    
    def callBack(self):
        if self.w_line.text() != '' and self.h_line.text()!='':
            self.canvas_width = int(self.w_line.text())
            self.canvas_height = int(self.h_line.text())
        return self.canvas_color,self.canvas_width,self.canvas_height
    
    def turnBack(self):
        self.info = self.callBack()
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue("width",self.canvas_width)
        settings.setValue("height", self.canvas_height)
        settings.setValue("color", self.canvas_color)
        self.accept()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Welcome()
    sys.exit(app.exec_())
        