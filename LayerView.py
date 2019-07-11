# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:15:15 2019

@author: Quanfita
"""
import sys
import ops
import cv2
from PyQt5.QtCore import (Qt,QSize,pyqtSignal,QItemSelectionModel,pyqtSlot,QRectF,
                          QSettings,QMimeData)
from PyQt5.QtGui import QFont,QBrush,QIcon,QImage,QPixmap,QColor,QPalette,QDrag
from PyQt5.QtWidgets import (QListWidget,QListWidgetItem,QMenu,QAction,QGroupBox,
                             QHBoxLayout,QPushButton,QWidget,QVBoxLayout,
                             QApplication, QToolBox, QListView,QToolButton, 
                             QInputDialog, QMessageBox,QAbstractItemView,
                             QComboBox,QLabel,QLineEdit,QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsObject,
                             )

class ListWidget(QListWidget):
    signal = pyqtSignal()
    drag_signal = pyqtSignal([int,int])
    map_listwidget = []
    def __init__(self):
        super().__init__()
        #self.Data_init()
        self.list_names = []
        self.Ui_init()
        self.show()
    
    def Data_init(self,icon,randname='Layer1'):
        #self.list_names = [randname]
        settings = QSettings('tmp.ini',QSettings.IniFormat)
        if settings.value('imageName'):
            randname = settings.value('imageName')
        item = QListWidgetItem()
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setText(randname)
        item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        item.setIcon(icon)
        self.addItem(item)
        
    def Ui_init(self):
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setIconSize(QSize(60,40))
        self.setStyleSheet("QListWidget{border:1px solid #cdcdcd; color:white; background:transparent;}"
                        "QListWidget::Item{padding-top:5px; padding-bottom:5px; border:1px solid #cdcdcd;}"
                        "QListWidget::Item:hover{background:skyblue; }"
                        "QListWidget::item:selected:!active{border-width:0px; background:#cdcdcd; }"
                        )
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.connect(self.getListitems)
        self.itemDoubleClicked[QListWidgetItem].connect(self.rename)
    
    def mousePressEvent(self,event):
        QListWidget.mousePressEvent(self,event)
        self.setCurrentItem(self.itemAt(event.pos()))
        self.start_pos = event.pos()
        print('start position:'+str(self.start_pos))
        
    def mouseMoveEvent(self,event):
        QListWidget.mouseMoveEvent(self,event)
        item = QListWidgetItem(self.currentItem())
        mimeData = QMimeData()
        mimeData.setText(item.text())
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec(Qt.MoveAction)
    
    def mouseReleaseEvent(self,event):
        self.end_pos = event.pos()
        item = self.itemAt(self.start_pos)
        self.insertItem(self.row(self.itemAt(self.end_pos))+1,item)
        self.setCurrentItem(self.itemAt(self.end_pos))
    
    def dragEnterEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def dragMoveEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()
        
    def dropEvent(self,event):
        self.end_pos = event.pos()
        print('end drop position:'+str(self.end_pos))
        item = self.takeItem(self.row(self.itemAt(self.start_pos)))
        #self.removeItemWidget(self.itemAt(self.start_pos))
        print(self.row(self.itemAt(self.end_pos)))
        if self.row(self.itemAt(self.end_pos)) == -1:
            self.addItem(item)
            self.drag_signal.emit(self.row(self.itemAt(self.start_pos)),self.count()-1)
        else:
            self.insertItem(self.row(self.itemAt(self.end_pos)),item)
            self.drag_signal.emit(self.row(self.itemAt(self.start_pos)),self.row(self.itemAt(self.end_pos)))
        self.setCurrentItem(item)
        event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def getListitems(self):
        self.signal.emit()
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
    
    def addItemSlot(self,icon,ind=0,newname='Untitled'):
        newitem = QListWidgetItem()
        font = QFont()
        font.setPointSize(10)
        newitem.setFont(font)
        newitem.setText(newname)
        newitem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        newitem.setIcon(QIcon(icon))
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
        self.setStyleSheet('color:white;background-color:#535353;')
        self.refresh = refresh
        self.img = img
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setSpacing(0)
        self.lay.setAlignment(Qt.AlignCenter)
        self.list = ListWidget()
        self.list.setStyleSheet('QListWidget{color:white;background-color:#535353;border:1px solid #282828;}')
        self.list.Data_init(QIcon(ops.cvtCV2Pixmap(cv2.copyMakeBorder(cv2.resize(self.img.Image,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200]))))
        self.toolsBox = QGroupBox(self)
        self.toolsBox.setStyleSheet("QGroupBox{background-color:#535353;border:1px solid #282828;padding-left,padding-right:5px;padding-top,padding-bottom:2px;margin:0px;}"
                                    "QToolButton{background: transparent;border:none}")
        self.adjBox = QGroupBox(self)
        self.adjBox.setStyleSheet("QGroupBox{background-color:#535353;padding-left,padding-right:5px;padding-top,padding-bottom:2px;border:1px solid #282828;}")
        self.adjLayout = QHBoxLayout()
        #self.adjLayout.setContentsMargins(0,0,0,0)
        self.toolsLayout = QHBoxLayout()
        #self.toolsLayout.setContentsMargins(0,0,0,0)
        self.toolsLayout.setAlignment(Qt.AlignRight)
        self.opacity_lb = QLabel('Opacity:',self)
        self.opacity_lb.resize(50,30)
        self.opacity_val = QLineEdit(self)
        self.opacity_val.installEventFilter(self)
        self.opacity_val.resize(30,30)
        self.opacity_val.setStyleSheet('QLineEdit{color:white;border:1px solid #cdcdcd;border-radius:2px;}')
        self.opacity_val.setPlaceholderText('100%')
        mix_info = ['Normal','Screen','Multiply','Overlay','SoftLight',
                    'HardLight','LinearAdd','ColorBurn','LinearBurn',
                    'ColorDodge','LinearDodge','LighterColor','VividLight',
                    'LinearLight','PinLight','HardMix','Difference','Exclusion',
                    'Subtract','Divide','Hue']
        self.mix_combox = QComboBox(self)
        self.mix_combox.addItems(mix_info)
        self.mix_combox.resize(60,30)
        self.mix_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:20px;width: 20px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}'
            'QToolTip{color:white;background-color:#535353;}')
        self.adjLayout.addWidget(self.mix_combox)
        self.adjLayout.addWidget(self.opacity_lb)
        self.adjLayout.addWidget(self.opacity_val)
        self.adjBox.setLayout(self.adjLayout)
        self.lay.addWidget(self.adjBox)
        self.mix_combox.activated[str].connect(self.select)
        self.lay.addWidget(self.list)
        self.setWindowFlags(Qt.Dialog)
        self.setMinimumSize(270,300)
        self.setMaximumSize(300,500)
        self.del_btn = QToolButton(self)
        self.new_btn = QToolButton(self)
        self.cpy_btn = QToolButton(self)
        self.grp_btn = QToolButton(self)
        self.adj_btn = QToolButton(self)
        self.mask_btn = QToolButton(self)
        self.del_btn.resize(30,30)
        self.new_btn.resize(30,30)
        self.cpy_btn.resize(30,30)
        self.grp_btn.resize(30,30)
        self.adj_btn.resize(30,30)
        self.mask_btn.resize(30,30)
        self.del_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.new_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.cpy_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.grp_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.adj_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.mask_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.del_btn.setToolTip('Delete this layer')
        self.new_btn.setToolTip('New a layer')
        self.cpy_btn.setToolTip('Copy this layer')
        self.grp_btn.setToolTip('New a group')
        self.adj_btn.setToolTip('New a adjustment layer')
        self.mask_btn.setToolTip('Add a mask')
        self.del_btn.setIcon(QIcon('./UI/trash.svg'))
        self.new_btn.setIcon(QIcon('./UI/sticky-note.svg'))
        self.cpy_btn.setIcon(QIcon('./UI/copy.svg'))
        self.grp_btn.setIcon(QIcon('./UI/folder.svg'))
        self.adj_btn.setIcon(QIcon('./UI/adjust.svg'))
        self.mask_btn.setIcon(QIcon('./UI/mask.svg'))
        #self.new_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        #self.cpy_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        #self.del_btn.setStyleSheet("QToolButton{background: transparent;border:none}")
        self.del_btn.clicked.connect(self.delLayer)
        self.new_btn.clicked.connect(self.newLayer)
        self.cpy_btn.clicked.connect(self.cpyLayer)
        self.grp_btn.clicked.connect(self.group)
        self.adj_btn.clicked.connect(self.adjLayer)
        self.mask_btn.clicked.connect(self.addMask)
        self.toolsLayout.addWidget(self.mask_btn)
        self.toolsLayout.addWidget(self.adj_btn)
        self.toolsLayout.addWidget(self.grp_btn)
        self.toolsLayout.addWidget(self.cpy_btn)
        self.toolsLayout.addWidget(self.new_btn)
        self.toolsLayout.addWidget(self.del_btn)
        
        self.toolsBox.setLayout(self.toolsLayout)
        self.lay.addWidget(self.toolsBox)
        self.setLayout(self.lay)
        self.list.signal.connect(self.sltLayer)
        self.list.setCurrentRow(0)
        self.list.drag_signal[int,int].connect(self.chgLayer)
        self.img.signal.connect(self.refreshLayerIcon)
        self.show()
    
    def group(self):
        pass
    
    def adjLayer(self):
        pass
    
    def addMask(self):
        pass
    
    def chgLayer(self,start,end):
        lsize = len(self.list)
        print(lsize,start,end)
        self.img.exchgLayer(lsize - start - 1,lsize - end - 1)
        pass
    
    def newLayer(self):
        cur = self.list.currentItem()
        ind = self.list.row(cur)
        lsize = len(self.list)
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
                self.list.addItemSlot(QIcon(QBrush(Qt.Dense7Pattern)),ind,newname[0])
                self.img.addLayer(lsize - ind)
                self.refresh()
                break
        pass
    
    def refreshLayerIcon(self):
        cur = self.list.currentItem()
        cur.setIcon(QIcon(ops.cvtCV2Pixmap(cv2.copyMakeBorder(cv2.resize(self.img.layer[self.img.selectedLayerIndex].Image,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200]))))
    
    def addLayer(self,img,name):
        if self.list.count() == 0:
            ind = 0
        else:
            cur = self.list.currentItem()
            ind = self.list.row(cur)
        lsize = len(self.list)
        self.list.addItemSlot(QIcon(ops.cvtCV2Pixmap(cv2.copyMakeBorder(cv2.resize(img,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200]))),ind,name)
        
        self.img.addLayer(lsize - ind,img)
        self.list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
        self.refresh()
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
                lsize = len(self.list)
                self.list.deleteItemSlot()
                self.img.delLayer(lsize - ind - 1)
                self.list.setCurrentRow(ind-1,QItemSelectionModel.ClearAndSelect)
                self.refresh()
        pass
    
    def cpyLayer(self):
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
            self.list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
            self.refresh()
        pass
    
    def sltLayer(self):
        cur = self.list.currentItem()
        ind = self.list.row(cur)
        lsize = len(self.list)
        #print(self.img.mix_list[lsize - ind - 1])
        self.mix_combox.setCurrentText(self.img.mix_list[lsize - ind - 1])
        self.img.sltLayer(lsize - ind - 1)
        if ind  == lsize - 1:
            self.img.mix_list[lsize - ind - 1] = 'Normal'
            self.mix_combox.setCurrentText('Normal')
            self.mix_combox.setEnabled(False)
            self.opacity_val.setEnabled(False)
        else:
            self.mix_combox.setEnabled(True)
            self.opacity_val.setEnabled(True)
        pass
    
    def select(self,s):
        cur = self.list.currentItem()
        ind = self.list.row(cur)
        lsize = len(self.list)
        #print(lsize,ind,lsize - ind - 1)
        self.img.setMix(lsize - ind - 1,s)
        self.refresh()
        pass

class Layer(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.color = QColor(Qt.lightGray)
        self.dragOver = False
        self.setAcceptDrops(True)
        
    def dragLeaveEvent(self, event):
        self.dragOver = False
        self.update()
    
    def dropEvent(self, event):
        self.dragOver = False
        self.update()

class GraphicsScene(QGraphicsScene):
    def __init__(self,width,height):
        super().__init__()
        self.setSceneRect(QRectF(0,0,width,height))
        #palette = QPalette()
        #palette.setBrush(QPalette.Background,QBrush(Qt.Dense7Pattern))
        #self.setPalette(palette)
        self.setBackgroundBrush(QBrush(Qt.Dense7Pattern))
        img = cv2.imread('./samples/10.jpg')
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        frame = QImage(img,img.shape[1],img.shape[0],QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)
        self.addItem(self.item)

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setGeometry(250,250,750,750)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.sence = GraphicsScene(256,256)
        self.setScene(self.sence)
        self.setSceneRect(0,0,255,255)
        self.ensureVisible(0,0,256,256)
        self.show()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    img = cv2.imread('./samples/10.jpg')
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    ex = GraphicsView()
    #ex = LayerTools()
    #ex.show()
    #ex = LayerMain(None,print)
    sys.exit(app.exec_())