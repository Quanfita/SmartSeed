from setting import *
from common.app import logger
from common.utils import openImage
from views.testMain import MainWindow
from views.Dialog import SaveDialog
# from views.Preview import Preview
from core import ops
from PyQt5.QtWidgets import QApplication,QWidget
# from middleware.Transmission import Transmission
# from middleware.Thread import ProThread
# from middleware.Structure import LayerStackList
from views.Style2PaintsView import S2PView

import sys
import os

if __name__ == '__main__':
	debug = True
	logger.info('Start test.')
	app = QApplication(sys.argv)
	# main = MainWindow(debug=debug)
	# pth = ProThread(debug=debug,parent=main)
	# layer = LayerStackList(debug=debug)
	# trans = Transmission(main,pth,layer)
	# main.show()
	image = ops.imread('./samples/timg.jpg')
	s2p = S2PView(image,debug=debug)
	s2p.show()
	sys.exit(app.exec_())
