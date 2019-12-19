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
	def __init__(self, view):
		super(Transmission, self).__init__()
		self._view = view
		self.signal_interface_list = []
		self.sig_list = self._view.sig_list
		for sig in self.sig_list:
			sig[dict].connect()

	def mainIf(self, content):
		pass

	def canvasIf(self, content):
		pass

	def dockIf(self, content):
		pass

	def toolbarIf(self, content):
		pass

	def menubarIf(self, content):
		pass

		