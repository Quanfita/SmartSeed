from setting import *
from common.app import logger
from common.utils import openImage
from views.testMain import MainWindow
from views.ToolBar import ToolView
# from views.Preview import Preview
from core import ops
from PyQt5.QtWidgets import QApplication,QWidget
from middleware.Controller import Controller
from middleware.Thread import ProThread
from middleware.Structure import LayerStackList
# from views.Style2PaintsView import S2PView

import sys
import os

if __name__ == '__main__':
	debug = True
	logger.info('Start test.')
	# app = QApplication(sys.argv)
	# ctrl = Controller()
	# main = MainWindow(controller=ctrl,debug=debug)
	# pth = ProThread(controller=ctrl,debug=debug,parent=main)
	# layer = LayerStackList(controller=ctrl,debug=debug)
	# ctrl.init(main,pth,layer)
	# main.show()
	# pth.start()
	# # tool = ToolView('vary')
	# # tool.show()
	# # image = ops.imread('./samples/24.png')
	# # s2p = S2PView(image,debug=debug)
	# # s2p.show()
	# sys.exit(app.exec_())
	from views.ColorWidget import ColorWidget
	app = QApplication(sys.argv)
	l = ColorWidget()
	l.show()
	sys.exit(app.exec_())
