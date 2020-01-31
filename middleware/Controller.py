# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""
from common.app import logger
from common.singleton import SingletonIns
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt,pyqtSignal,pyqtSlot,QObject

import sys

@SingletonIns
class Controller(object):
    """docstring for Transmission"""
    def __init__(self):
        # super(Controller, self).__init__()
        self.__view = None
        self.__p_thread = None
        self.__layer_list = None
    
    def init(self,view,pthread,layer_list):
        self.__view = view
        self.__p_thread = pthread
        self.__layer_list = layer_list
        self.__stack = self.__layer_list._now_stack
        self.__canvas_list = self.__view.mcanvas
        self.__canvas = self.__canvas_list.canvas
        self.__layer = self.__view.layer
        self.__p_thread.finished.connect(self.refreshView)

    @property
    def view(self):
        return self.__view

    @property
    def layerStack(self):
        return self.__stack

    @layerStack.setter
    def layerStack(self, layerStack):
        self.__stack = layerStack
    
    @property
    def layer(self):
        return self.__layer
    
    @property
    def canvas(self):
        return self.__canvas

    @canvas.setter
    def canvas(self, canvas):
        self.__canvas = canvas
    
    def initNewCanvas(self, content):
        self.__layer_list.newStack(content)
        self.__stack = self.__layer_list.now_stack
        self.__canvas_list.newCanvas(self.__stack)
        self.__canvas = self.__canvas_list.canvas
        self.refreshView()
    
    def selectCanvas(self, index):
        self.__layer_list.selectStack(index)
        self.__stack = self.__layer_list.now_stack
        self.__canvas = self.__canvas_list.canvas
        self.refreshView()

    def removeCanvas(self, index):
        self.__layer_list.removeStackByIndex(index)
        self.__stack = self.__layer_list.now_stack
        self.__canvas = self.__canvas_list.canvas
        self.refreshView()

    def selectLayer(self, index):
        self.__stack.currentIndex = index

    def removeLayer(self, index):
        self.__stack.delLayer(index)
        self.refreshView()

    def addLayer(self, content):
        self.__stack.addLayer(self.__stack.currentIndex,content['image_name'],content['image'])
        self.refreshView()
    
    def exchangeLayer(self, fore, sup):
        self.__stack.exchgLayer(fore, sup)
        self.refreshView()
    
    def setMix(self, idx, type):
        self.__stack.setMix(idx, type)
        self.refreshView()

    def refreshView(self):
        if self.__canvas is not None:
            self.__canvas.draw.refresh(self.__stack.shown_image)
            self.__view.hist.DrawHistogram(self.__stack.image)
            self.__layer.initWithLayerStack(self.__stack)
    
    def doProcess(self, content):
        content['data']['image'] = self.__stack.currentImageObject()
        self.__p_thread.addTask(content)
            