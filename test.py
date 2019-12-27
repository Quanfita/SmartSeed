from setting import *
from common.app import logger
from common.utils import openImage
from views.testMain import MainWindow
from views.Dialog import SaveDialog
from views.Preview import Preview
from core import ops
from PyQt5.QtWidgets import QApplication,QWidget
from middleware.Transmission import Transmission
from middleware.Thread import ProThread
from middleware.Structure import LayerStackList

import sys
import os


if __name__ == '__main__':
	logger.info('Start test.')
	app = QApplication(sys.argv)
	main = MainWindow(debug=True)
	pth = ProThread(debug=True,parent=main)
	layer = LayerStackList(debug=True)
	trans = Transmission(main,pth,layer)
	main.show()
	sys.exit(app.exec_())
