# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""
from common.app import logger
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt,pyqtSignal,pyqtSlot,QObject

import sys


class Transmission(QWidget):
    """docstring for Transmission"""
    def __init__(self, view, pth, layer):
        super(Transmission, self).__init__()
        self._view = view
        self._p_thread = pth
        self._layer = layer
        self._view.out_signal[dict].connect(self.mainInterface)
        self._layer.out_signal[dict].connect(self.layerInterface)

    def mainInterface(self, content):
        if content['togo'] == 'thread':
            content['data']['image'] = self._layer._now_stack.image
            self._p_thread.in_signal.emit(content)
            self._p_thread.start()
        else:
            self._layer.in_signal.emit(content)

    def layerInterface(self, content):
        if content['togo'] == 'main':
            self._view.in_signal.emit(content)
        elif content['togo'] == 'canvas':
            self._view.mcanvas.in_signal.emit(content)
        elif content['togo'] == 'layer':
            self._view.layer.in_signal.emit(content)
        elif content['togo'] == 'all':
            self._view.mcanvas.canvas.in_signal.emit(content)
            self._view.layer.in_signal.emit(content)
        elif content['togo'] is None:
            self._layer.in_signal.emit(content)