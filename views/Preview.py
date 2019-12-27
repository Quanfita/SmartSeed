# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""

from PyQt5.QtWidgets import QWidget,QLabel,QHBoxLayout,QGroupBox,QSlider,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from core import ops

import setting

class Preview(QWidget):
    """docstring for Preview"""
    def __init__(self, parent):
        super(Preview, self).__init__()
        self.parent = parent
        self.test_img = ops.imread(setting.BASE_PATH+'/samples/10.jpg')

        self.resize(360,240)
        self.setStyleSheet("QWidget{background-color:#535353;}")

        self.label = QLabel('main',self)
        self.setMinimumSize(120,80)
        self.label.setAlignment(Qt.AlignCenter)
        w,h = int(self.width()*0.8), int(self.height()*0.6)
        x,y = self.width()//2 - w//2,self.height()//2 - h//2
        self.label.setGeometry(x,y,w,h-30)
        self.label.setPixmap(ops.cvtCV2PixmapAlpha(ops.resizeAdjustment(self.test_img,self.label.width(),self.label.height())))

        self.tool = QGroupBox(self)
        self.tool.setGeometry(0,self.height()-30,80,30)
        self.tool.setStyleSheet("QGroupBox{border-top:1px solid #424242;}")

        self.sl = QSlider(Qt.Horizontal,self)
        self.sl.resize(25,50)
        self.sl.setMinimum(0)
        self.sl.setMaximum(100)
        # self.sl.setTickPosition(QSlider.TicksAbove)
        self.sl.setValue(70)
        # self.sl.valueChanged[int].connect(self.setQuanlityValue)

        self.s_line = QLineEdit(self)
        self.s_line.installEventFilter(self)
        self.s_line.resize(30,25)
        self.s_line.setPlaceholderText(str(self.test_img.shape[0]))
        self.s_line.setText(str(self.test_img.shape[0]))
        self.s_line.setStyleSheet("QLineEdit{background-color:#535353;border:none;}"
                                "QLineEdit:focus{background-color:#424242;border:none;}")
        # self.s_line.textEdited[str].connect(self.setScaleValue)

        tool_layout = QHBoxLayout()
        tool_layout.setAlignment(Qt.AlignLeft)
        tool_layout.addWidget(self.s_line,1)
        tool_layout.addWidget(self.sl,4)

        self.tool.setLayout(tool_layout)

        self.show()

    def resizeEvent(self, event):
        w,h = int(self.width()*0.8), int(self.height()*0.6)
        x,y = self.width()//2 - w//2,self.height()//2 - h//2
        self.label.setGeometry(x,y,w,h-30)
        self.label.setPixmap(ops.cvtCV2PixmapAlpha(ops.resizeAdjustment(self.test_img,self.label.width(),self.label.height())))
        self.tool.setGeometry(0,self.height()-30,self.width(),30)
