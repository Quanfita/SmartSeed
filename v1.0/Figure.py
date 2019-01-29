# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 09:26:14 2019

@author: Quanfita
"""
import cv2
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#import matplotlib.pyplot as plt

#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #第二步：在父类中激活Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形
        #第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes = self.fig.add_subplot(111)

    def DrawHistogram(self,img):
        color = ('b','g','r')
        for i,col in enumerate(color):
            histr = cv2.calcHist([img],[i],None,[256],[0,256])
            self.axes.plot(histr,color = col)
            self.axes.set_xlim([0,256])
            self.axes.set_xticks([]), self.axes.set_yticks([])
    '''
    def update(self):
        FuncAnimation(self.fig, self.DrawHistogram)
    '''