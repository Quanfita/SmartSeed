from setting import *
from common.app import logger
from common.utils import saveHistoryCfg
from views.testMain import MainWindow
from PyQt5.QtWidgets import QApplication

import sys
import os


if __name__ == '__main__':
	logger.info('Start test.')
	saveHistoryCfg({})
	# app = QApplication(sys.argv)
	# main = MainWindow(debug=True)
	# main.show()
	# sys.exit(app.exec_())