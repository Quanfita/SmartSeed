from setting import *
from common.app import logger
from common.utils import openImage
from views.testMain import MainWindow
from views.Dialog import SaveDialog
from PyQt5.QtWidgets import QApplication,QWidget

import sys
import os


if __name__ == '__main__':
	logger.info('Start test.')
	app = QApplication(sys.argv)
	t = SaveDialog(None)
	t.show()
	# main = MainWindow(debug=True)
	# main.show()
	sys.exit(app.exec_())