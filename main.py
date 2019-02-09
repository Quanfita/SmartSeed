# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 17:42:25 2019

@author: Quanfita
"""

from PyQt5.QtWidgets import QApplication,QDialog
import sys
from app import Example
from Welcome import Welcome

def main():
    app = QApplication(sys.argv)
    wel = Welcome()
    if wel.exec_() == QDialog.Accepted:
        Example()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()