# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:33:17 2020

@author: Quanfita
"""
from PyQt5.QtWidgets import (QWidget,QHBoxLayout,QLabel,QPushButton,QSlider,QSpinBox,
                            QComboBox,QToolButton,QCheckBox,QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

class ToolView(QWidget):
    def __init__(self, target, parent=None):
        super(ToolView, self).__init__()
        self.parent = parent
        self.__initView(target)
    
    def __initView(self, target):
        self.setFixedHeight(30)
        self.setStyleSheet("QWidget{background-color:#565656;color:white;}")
        self.main_layout = QHBoxLayout()
        if target in ['rect','circle']:
            self.__initRectOrCircleView(target)
        elif target in ['line','pencil']:
            self.__initLineOrPencilView(target)
        elif target == 'move':
            self.__initMoveView()
        elif target == 'zoom':
            self.__initZoomView()
        elif target == 'vary':
            self.__initVaryView()
        elif target == 'fill':
            self.__initFillView()
        elif target == 'dropper':
            self.__initDropperView()
        self.setLayout(self.main_layout)
    
    def __initDropperView(self):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap('./static/UI/fill-drip.svg').scaled(20,20))

        self.size_lb = QLabel('取样大小:',self)
        self.size_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.size_lb.setFixedSize(60,20)

        size = ["取样点","3 x 3 平均","5 x 5 平均","11 x 11 平均",
                "31 x 31 平均","51 x 51 平均","101 x 101 平均"]
        self.size_combox = QComboBox(self)
        self.size_combox.addItems(size)
        self.size_combox.setFixedSize(100,20)
        self.size_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
                    "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
                    "QComboBox QAbstractItemView::item{height:20px;width:80px;}")

        self.point_lb = QLabel('样本:',self)
        self.point_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.point_lb.setFixedSize(30,20)

        point = ["所有图层","当前图层","当前和下方图层","所有无调整图层","当前和下一个无调整图层"]
        self.point_combox = QComboBox(self)
        self.point_combox.addItems(point)
        self.point_combox.setFixedSize(150,20)
        self.point_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
                    "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
                    "QComboBox QAbstractItemView::item{height:20px;width:80px;}")

        self.show_check = QCheckBox("显示取样环",self)
        self.show_check.setFixedHeight(20)
        # self.show_check.setChecked(True)

        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.size_lb)
        self.main_layout.addWidget(self.size_combox)
        self.main_layout.addWidget(self.point_lb)
        self.main_layout.addWidget(self.point_combox)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.show_check)
        self.main_layout.addStretch()

    def __initFillView(self):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap('./static/UI/fill-drip.svg').scaled(20,20))
        
        mode = [u'前景',u'图案 ']
        self.mode_combox = QComboBox(self)
        self.mode_combox.addItems(mode)
        self.mode_combox.setFixedSize(70,20)
        # self.mode_combox.activated[str].connect(self.selectPix)
        self.mode_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
        #'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            # 'QComboBox::down-arrow{image:url(./static/UI/angle-down.svg);border:0px;}'
            "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
            "QComboBox QAbstractItemView::item{height:20px;width:80px;}")
        
        self.mix_lb = QLabel('模式:',self)
        self.mix_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.mix_lb.setFixedSize(30,20)

        mix = ['Normal','Screen','Multiply','Overlay','SoftLight',
                'HardLight','LinearAdd','ColorBurn','LinearBurn',
                'ColorDodge','LinearDodge','LighterColor','VividLight',
                'LinearLight','PinLight','HardMix','Difference','Exclusion',
                'Subtract','Divide','Hue']
        self.mix_combox = QComboBox(self)
        self.mix_combox.addItems(mix)
        self.mix_combox.setFixedSize(120,20)
        self.mix_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
                    "QComboBox QAbstractItemView{border: 0px;outline:2px;height:80px;background-color: #323232;font:24px;color:white;}"
                    "QComboBox QAbstractItemView::item{height:25px;width:80px;}")
        
        self.opacity_lb = QLabel('不透明度:',self)
        self.opacity_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.opacity_lb.setFixedSize(60,20)

        self.opacity_line = QLineEdit(self)
        self.opacity_line.setText("100%")
        self.opacity_line.setFixedSize(40,20)

        self.distance_lb = QLabel('容差:',self)
        self.distance_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.distance_lb.setFixedSize(30,20)

        self.distance_line = QLineEdit(self)
        self.distance_line.setText("32")
        self.distance_line.setFixedSize(30,20)

        self.jagged_check = QCheckBox("消除锯齿",self)
        self.jagged_check.setFixedHeight(20)
        self.jagged_check.setChecked(True)

        self.continuous_check = QCheckBox("连续的",self)
        self.continuous_check.setFixedHeight(20)
        self.continuous_check.setChecked(True)

        self.all_check = QCheckBox("所有图层",self)
        self.all_check.setFixedHeight(20)

        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.mode_combox)
        self.main_layout.addWidget(self.mix_lb)
        self.main_layout.addWidget(self.mix_combox)
        self.main_layout.addWidget(self.opacity_lb)
        self.main_layout.addWidget(self.opacity_line)
        self.main_layout.addWidget(self.distance_lb)
        self.main_layout.addWidget(self.distance_line)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.jagged_check)
        self.main_layout.addWidget(self.continuous_check)
        self.main_layout.addWidget(self.all_check)
        self.main_layout.addStretch()

    def __initVaryView(self):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap('./static/UI/arrows.svg').scaled(20,20))

        self.auto_check = QCheckBox("自动选择:",self)
        self.auto_check.setFixedHeight(20)
        self.auto_check.setChecked(True)

        mode = [u'图层',u'组']
        self.mode_combox = QComboBox(self)
        self.mode_combox.addItems(mode)
        self.mode_combox.setFixedSize(40,20)
        # self.mode_combox.activated[str].connect(self.selectPix)
        self.mode_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
        #'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            # 'QComboBox::down-arrow{image:url(./static/UI/angle-down.svg);border:0px;}'
            "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
            "QComboBox QAbstractItemView::item{height:20px;width:80px;}")
        
        self.show_check = QCheckBox("显示变换控件",self)
        self.show_check.setFixedHeight(20)
        self.show_check.setChecked(True)
        
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.auto_check)
        self.main_layout.addWidget(self.mode_combox)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.show_check)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addStretch()
    
    def __initMoveView(self):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap('./static/UI/hand-paper.svg').scaled(20,20))

        self.all_check = QCheckBox("滚动所有窗口",self)
        self.all_check.setFixedHeight(20)
        self.all_check.setChecked(True)

        self.origin_size_btn = QPushButton('100%',self)
        self.origin_size_btn.setFixedHeight(20)

        self.adjust_size_btn = QPushButton('适合屏幕',self)
        self.adjust_size_btn.setFixedHeight(20)

        self.cover_size_btn = QPushButton('填充屏幕',self)
        self.cover_size_btn.setFixedHeight(20)

        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.all_check)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.origin_size_btn)
        self.main_layout.addWidget(self.adjust_size_btn)
        self.main_layout.addWidget(self.cover_size_btn)
        self.main_layout.addStretch()

    def __initZoomView(self):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap('./static/UI/search.svg').scaled(20,20))

        self.plus = QToolButton(self)
        self.plus.setFixedSize(20,20)
        self.plus.setDown(True)
        self.plus.setIcon(QIcon(QPixmap('./static/UI/search-plus.svg').scaled(20,20)))
        self.plus.setStyleSheet("QToolButton{color:white;border:0px;}")

        self.minus = QToolButton(self)
        self.minus.setFixedSize(20,20)
        self.minus.setIcon(QIcon(QPixmap('./static/UI/search-minus.svg').scaled(20,20)))

        self.adjust_check = QCheckBox("调整窗口大小以满屏显示",self)
        self.adjust_check.setFixedHeight(20)

        self.all_check = QCheckBox("缩放所有窗口",self)
        self.all_check.setFixedHeight(20)

        self.little_check = QCheckBox("细微缩放",self)
        self.little_check.setFixedHeight(20)
        self.little_check.setChecked(True)

        self.origin_size_btn = QPushButton('100%',self)
        self.origin_size_btn.setFixedHeight(20)

        self.adjust_size_btn = QPushButton('适合屏幕',self)
        self.adjust_size_btn.setFixedHeight(20)

        self.cover_size_btn = QPushButton('填充屏幕',self)
        self.cover_size_btn.setFixedHeight(20)
        
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.plus)
        self.main_layout.addWidget(self.minus)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.adjust_check)
        self.main_layout.addWidget(self.all_check)
        self.main_layout.addWidget(self.little_check)
        self.main_layout.addWidget(self.origin_size_btn)
        self.main_layout.addWidget(self.adjust_size_btn)
        self.main_layout.addWidget(self.cover_size_btn)
        self.main_layout.addStretch()

    def __initLineOrPencilView(self,target):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        if target == 'line':
            self.icon.setPixmap(QPixmap('./static/UI/line.svg').scaled(20,20))
        elif target == 'pencil':
            self.icon.setPixmap(QPixmap('./static/UI/pen.svg').scaled(20,20))
        
        mode = [u'形状',u'路径',u'像素']
        self.mode_combox = QComboBox(self)
        self.mode_combox.addItems(mode)
        self.mode_combox.setFixedSize(70,20)
        # self.mode_combox.activated[str].connect(self.selectPix)
        self.mode_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
        #'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            # 'QComboBox::down-arrow{image:url(./static/UI/angle-down.svg);border:0px;}'
            "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
            "QComboBox QAbstractItemView::item{height:20px;width:80px;}")

        # self.color_lb = QLabel('描边:',self)
        # self.color_lb.resize(40,30)
        self.fill_lb = QLabel('颜色:',self)
        self.fill_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.fill_lb.setFixedSize(30,20)
        self.fill_btn = QPushButton('',self)
        self.fill_btn.setFixedSize(24,18)
        self.fill_btn.setStyleSheet("QPushButton{background-color:black}"
                                    "QPushButton{border:1px solid #cdcdcd;}")
        # self.fill_btn.clicked.connect(self.fillColor)
        # self.color_lb.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        # self.color_btn = QPushButton('',self)
        # self.color_btn.resize(24,20)
        # self.color_btn.setStyleSheet("QPushButton{background-color:black}"
        #                             "QPushButton{border:1px solid #cdcdcd;}")
        # self.color_btn.clicked.connect(self.chooseColor)
        
        # self.thick_lb = QLabel('Thick:',self)
        # self.thick_lb.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.thick_sp = QSpinBox(self)
        self.thick_sp.setMinimum(1)
        self.thick_sp.setMaximum(100)
        self.thick_sp.setSuffix(' 像素')
        self.thick_sp.setFixedSize(70,20)
        
        self.thick_sl = QSlider(Qt.Horizontal,self)
        self.thick_sl.setFixedSize(60,16)
        self.thick_sl.setMinimum(1)
        self.thick_sl.setMaximum(100)
        self.thick_sl.setTickInterval(1)
        self.thick_sl.setToolTip
        self.thick_sl.setTickPosition(QSlider.NoTicks)
        self.thick_sl.setStyleSheet("QSlider::groove:horizontal{height: 6px;background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(124, 124, 124), stop: 1.0 rgb(72, 71, 71));}"
                                    "QSlider::handle:horizontal{width: 8px;background: #cdcdcd;margin: -2px 0px -2px 0px;border-radius: 4px;}")
        self.thick_sl.valueChanged[int].connect(self.thick_sp.setValue)
        self.thick_sp.valueChanged[int].connect(self.thick_sl.setValue)
        
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.mode_combox)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.fill_lb)
        self.main_layout.addWidget(self.fill_btn)
        # self.main_layout.addWidget(self.color_lb)
        # self.main_layout.addWidget(self.color_btn)
        # self.main_layout.addWidget(self.thick_lb)
        self.main_layout.addWidget(self.thick_sp)
        self.main_layout.addWidget(self.thick_sl)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addStretch()
    
    def __initRectOrCircleView(self, target):
        self.icon = QLabel(self)
        self.icon.setFixedSize(20,20)
        self.icon.setAlignment(Qt.AlignCenter)
        if target == 'rect':
            self.icon.setPixmap(QPixmap('./static/UI/square.svg').scaled(20,20))
        elif target == 'circle':
            self.icon.setPixmap(QPixmap('./static/UI/circle.svg').scaled(20,20))
        
        mode = [u'形状',u'路径',u'像素']
        self.mode_combox = QComboBox(self)
        self.mode_combox.addItems(mode)
        self.mode_combox.setFixedSize(70,20)
        # self.mode_combox.activated[str].connect(self.selectPix)
        self.mode_combox.setStyleSheet("QComboBox{width:60px;color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;}"
        #'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            # 'QComboBox::down-arrow{image:url(./static/UI/angle-down.svg);border:0px;}'
            "QComboBox QAbstractItemView{border: 0px;outline:0px;height:80px;background-color: #323232;font:22px;color:white;}"
            "QComboBox QAbstractItemView::item{height:20px;width:80px;}")

        self.color_lb = QLabel('描边:',self)
        self.color_lb.setFixedSize(30,20)
        self.fill_lb = QLabel('填充:',self)
        self.fill_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.fill_lb.setFixedSize(30,20)
        self.fill_btn = QPushButton('',self)
        self.fill_btn.setFixedSize(24,18)
        self.fill_btn.setStyleSheet("QPushButton{background-color:black}"
                                    "QPushButton{border:1px solid #cdcdcd;}")
        # self.fill_btn.clicked.connect(self.fillColor)
        self.color_lb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)

        self.color_btn = QPushButton('',self)
        self.color_btn.setFixedSize(24,18)
        self.color_btn.setStyleSheet("QPushButton{background-color:black}"
                                    "QPushButton{border:1px solid #cdcdcd;}")
        # self.color_btn.clicked.connect(self.chooseColor)
        
        # self.thick_lb = QLabel('Thick:',self)
        # self.thick_lb.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.thick_sp = QSpinBox(self)
        self.thick_sp.setMinimum(1)
        self.thick_sp.setMaximum(100)
        self.thick_sp.setSuffix(' 像素')
        self.thick_sp.setFixedSize(70,20)
        
        self.thick_sl = QSlider(Qt.Horizontal,self)
        self.thick_sl.setFixedSize(60,16)
        self.thick_sl.setMinimum(1)
        self.thick_sl.setMaximum(100)
        self.thick_sl.setTickInterval(1)
        self.thick_sl.setToolTip
        self.thick_sl.setTickPosition(QSlider.NoTicks)
        self.thick_sl.setStyleSheet("QSlider::groove:horizontal{height: 6px;background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(124, 124, 124), stop: 1.0 rgb(72, 71, 71));}"
                                    "QSlider::handle:horizontal{width: 8px;background: #cdcdcd;margin: -2px 0px -2px 0px;border-radius: 4px;}")
        self.thick_sl.valueChanged[int].connect(self.thick_sp.setValue)
        self.thick_sp.valueChanged[int].connect(self.thick_sl.setValue)
        
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.mode_combox)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addWidget(self.fill_lb)
        self.main_layout.addWidget(self.fill_btn)
        self.main_layout.addWidget(self.color_lb)
        self.main_layout.addWidget(self.color_btn)
        # self.main_layout.addWidget(self.thick_lb)
        self.main_layout.addWidget(self.thick_sp)
        self.main_layout.addWidget(self.thick_sl)
        self.main_layout.addWidget(Separator(20))
        self.main_layout.addStretch()

class Separator(QLabel):
    def __init__(self, height):
        super(Separator, self).__init__()
        self.setFixedSize(1,height)
        self.setStyleSheet("QLabel{background-color:#434343;}")