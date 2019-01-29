# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:15:15 2019

@author: Quanfita
"""
import random
import sys
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QFont,QBrush,QIcon
from PyQt5.QtWidgets import (QListWidget,QListWidgetItem,QMenu,QAction,
                             QApplication, QToolBox, QListView, 
                             QInputDialog, QMessageBox,QAbstractItemView)

class ListWidget(QListWidget):

    map_listwidget = []
    def __init__(self):
        super().__init__()
        self.Data_init()
        self.Ui_init()
    
    def Data_init(self):
        randomnum = random.sample(range(26), 3)
        for i in randomnum:
            item = QListWidgetItem()
            randname = 'AAA'
            randicon = "./UI/image.svg"
            font = QFont()
            font.setPointSize(10)
            item.setFont(font)
            item.setText(randname)
            item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            item.setIcon(QIcon(randicon))
            self.addItem(item)
        
    def Ui_init(self):
        self.setIconSize(QSize(30,30))
        self.setStyleSheet("QListWidget{border:1px solid gray; color:black; }"
                        "QListWidget::Item{padding-top:20px; padding-bottom:4px; }"
                        "QListWidget::Item:hover{background:skyblue; }"
                        "QListWidget::item:selected:!active{border-width:0px; background:lightgreen; }"
                        )
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.connect(self.getListitems)
    
    def getListitems(self):
        return self.selectedItems()

    def contextMenuEvent(self, event):
        hitIndex = self.indexAt(event.pos()).column()
        if hitIndex > -1:
            pmenu = QMenu(self)
            pDeleteAct = QAction("Delete",pmenu)
            pmenu.addAction(pDeleteAct)
            pDeleteAct.triggered.connect(self.deleteItemSlot)
            if self is self.find('Default'):
                pAddItem = QAction("Add Layer",pmenu)
                pmenu.addAction(pAddItem)     
                pAddItem.triggered.connect(self.addItemSlot)
            if len(self.map_listwidget) > 1:
                pSubMenu = QMenu("Move to" ,pmenu)
                pmenu.addMenu(pSubMenu)
                for item_dic in self.map_listwidget:
                    if item_dic['listwidget'] is not self:
                        pMoveAct = QAction(item_dic['groupname'] ,pmenu)
                        pSubMenu.addAction(pMoveAct)
                        pMoveAct.triggered.connect(self.move)
            pmenu.popup(self.mapToGlobal(event.pos()))
    
    def deleteItemSlot(self):
        dellist = self.getListitems()
        for delitem in dellist:
            del_item = self.takeItem(self.row(delitem))
            del del_item 
    
    def addItemSlot(self):
        newitem = QListWidgetItem()
        newname = 'BBB'
        newicon = "./UI/image.svg"
        font = QFont()
        font.setPointSize(10)
        newitem.setFont(font)
        newitem.setText(newname)
        newitem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        newitem.setIcon(QIcon(newicon))
        self.addItem(newitem)
    
    def setListMap(self, listwidget):
        self.map_listwidget.append(listwidget)
    
    def move(self):
        tolistwidget = self.find(self.sender().text())
        movelist = self.getListitems()
        for moveitem in movelist:
            pItem = self.takeItem(self.row(moveitem))
            tolistwidget.addItem(pItem)
    
    def find(self, pmenuname):
        for item_dic in self.map_listwidget:
            if item_dic['groupname'] == pmenuname:
                return item_dic['listwidget']

class LayerBox(QToolBox):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(200,100)
        pListWidget = ListWidget()
        dic_list = {'listwidget':pListWidget, 'groupname':"Default"}
        pListWidget.setListMap(dic_list)
        self.addItem(pListWidget, "Default") 
        self.show()
    
    def contextMenuEvent(self, event):
        pmenu = QMenu(self)
        pAddGroupAct = QAction("Add Group", pmenu)
        pmenu.addAction(pAddGroupAct) 
        pAddGroupAct.triggered.connect(self.addGroupSlot)  
        pmenu.popup(self.mapToGlobal(event.pos()))
    
    def addGroupSlot(self):
        groupname = QInputDialog.getText(self, "Please Input Group Name", "")
        if groupname[0] and groupname[1]: 
            pListWidget1 = ListWidget()
            self.addItem(pListWidget1, groupname[0])
            dic_list = {'listwidget':pListWidget1, 'groupname':groupname[0]}
            pListWidget1.setListMap(dic_list)
        elif groupname[0] == '' and groupname[1]:
            QMessageBox.warning(self, "Warning", "Please Input Group Name")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LayerBox()
    sys.exit(app.exec_())