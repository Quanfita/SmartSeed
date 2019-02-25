# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:15:15 2019

@author: Quanfita
"""
import sys
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QFont,QBrush,QIcon
from PyQt5.QtWidgets import (QListWidget,QListWidgetItem,QMenu,QAction,QGroupBox,
                             QHBoxLayout,QPushButton,QWidget,QVBoxLayout,
                             QApplication, QToolBox, QListView,QToolButton, 
                             QInputDialog, QMessageBox,QAbstractItemView)

class ListWidget(QListWidget):

    map_listwidget = []
    def __init__(self):
        super().__init__()
        self.Data_init()
        self.Ui_init()
        self.show()
    
    def Data_init(self,randname='Untitled'):
        self.list_names = [randname]
        item = QListWidgetItem()
        randicon = "./UI/image.svg"
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setText(randname)
        item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        item.setIcon(QIcon(randicon))
        self.addItem(item)
        
    def Ui_init(self):
        self.setIconSize(QSize(20,20))
        self.setStyleSheet("QListWidget{border:1px solid gray; color:black; }"
                        "QListWidget::Item{padding-top:20px; padding-bottom:4px; }"
                        "QListWidget::Item:hover{background:skyblue; }"
                        "QListWidget::item:selected:!active{border-width:0px; background:lightgreen; }"
                        )
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.connect(self.getListitems)
        self.itemDoubleClicked[QListWidgetItem].connect(self.rename)
    
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
            self.list_names.pop(self.row(delitem))
            del_item = self.takeItem(self.row(delitem))
            del del_item 
    
    def addItemSlot(self,ind=0,newname='Untitled'):
        newitem = QListWidgetItem()
        newicon = "./UI/image.svg"
        font = QFont()
        font.setPointSize(10)
        newitem.setFont(font)
        newitem.setText(newname)
        newitem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        newitem.setIcon(QIcon(newicon))
        self.list_names.insert(ind,newname)
        #self.addItem(newitem)
        self.insertItem(ind,newitem)
    
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
    
    def rename(self):
        while True:
            newname = QInputDialog.getText(self, "Please Input New Name", "")
            if newname[0] != '' and newname[1] == True:
                self.currentItem().setText(newname[0])
                break
            elif newname[1] == False:
                break
            else:
                QMessageBox.warning(self, 'Warning',
                                    "Name is Null, please input Name", QMessageBox.Yes)
                continue

class LayerBox(QToolBox):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(200,100)
        pListWidget = ListWidget()
        dic_list = {'listwidget':pListWidget, 'groupname':"Default"}
        pListWidget.setListMap(dic_list)
        self.addItem(pListWidget, "Default") 
        #self.show()
    
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


class LayerMain(QWidget):
    
    def __init__(self,img,refresh):
        super().__init__()
        self.refresh = refresh
        self.img = img
        self.lay = QVBoxLayout(self)
        self.lay.setAlignment(Qt.AlignCenter)
        self.list = ListWidget()
        self.toolsBox = QGroupBox(self)
        self.toolsLayout = QHBoxLayout()
        self.toolsLayout.setAlignment(Qt.AlignRight)
        self.lay.addWidget(self.list)
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(100,30)
        self.del_btn = QToolButton(self)
        self.new_btn = QToolButton(self)
        self.cpy_btn = QToolButton(self)
        self.del_btn.resize(30,30)
        self.new_btn.resize(30,30)
        self.cpy_btn.resize(30,30)
        self.del_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.new_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.cpy_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.del_btn.setToolTip('Delete this layer')
        self.new_btn.setToolTip('New a layer')
        self.cpy_btn.setToolTip('Copy this layer')
        self.del_btn.setIcon(QIcon('./UI/trash.svg'))
        self.new_btn.setIcon(QIcon('./UI/new.svg'))
        self.cpy_btn.setIcon(QIcon('./UI/copy.svg'))
        self.del_btn.clicked.connect(self.delLayer)
        self.new_btn.clicked.connect(self.newLayer)
        self.cpy_btn.clicked.connect(self.cpyLayer)
        self.toolsLayout.addWidget(self.del_btn)
        self.toolsLayout.addWidget(self.new_btn)
        self.toolsLayout.addWidget(self.cpy_btn)
        self.toolsBox.setLayout(self.toolsLayout)
        self.lay.addWidget(self.toolsBox)
        self.setLayout(self.lay)
        self.show()
        
    def newLayer(self):
        cur = self.list.currentItem()
        ind = self.list.row(cur)
        while True:
            newname = QInputDialog.getText(self, "Please Input Name", "")
            if newname[0] in self.list.list_names:
                reply = QMessageBox.warning(self, 'Message',
                "This name is already used in previous layers, please change another one!", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    continue
                else:
                    break
            elif newname[0] == '':
                break
            else:
                self.list.addItemSlot(ind,newname[0])
                self.img.addLayer(len(self.list) - ind - 1)
                self.refresh()
                break
        pass
    
    def delLayer(self):
        if not self.list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to delete this layer?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
    
            if reply == QMessageBox.Yes:
                cur = self.list.currentItem()
                ind = self.list.row(cur)
                self.list.deleteItemSlot()
                self.img.delLayer(len(self.list) - ind - 1)
                self.refresh()
        pass
    
    def cpyLayer(self,layer):
        if not self.list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            cur = self.list.currentItem()
            ind = self.list.row(cur)
            name = self.list.list_names[ind] + '-copy'
            i = 0
            while True:
                if name in self.list.list_names:
                    name = name + '_' + str(i)
                    continue
                else:
                    break
            self.list.addItemSlot(ind,name)
            self.img.cpyLayer(ind)
            self.refresh()
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #ex = LayerTools()
    #ex.show()
    ex = LayerMain(None)
    sys.exit(app.exec_())