# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""
from common.app import logger
from core import ops
from PyQt5.QtWidgets import (QListWidget,QListWidgetItem,QToolBox,QWidget,QLabel,
							QVBoxLayout,QAbstractItemView,QGroupBox,QHBoxLayout,
							QLineEdit,QComboBox,QToolButton,QInputDialog,QMessageBox,QMenu,QAction)
from PyQt5.QtGui import QIcon,QFont,QDrag
from PyQt5.QtCore import Qt,pyqtSignal,QSettings,QObject,QSize,QMimeData,QItemSelectionModel

import sys

class ListWidget(QListWidget):
    """
    This is layer list widget, it based on QListWidget, 
    and it has add, delete, move, copy and select functions.
    """
    signal = pyqtSignal()
    drag_signal = pyqtSignal([int,int])
    map_listwidget = []
    out_signal = pyqtSignal(dict)
    def __init__(self,debug=False):
        super().__init__()
        self.__debug = debug
        #self.Data_init()
        self.list_names = []
        self.Ui_init()
        self.show()
    '''
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
    '''
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
        if self.__debug:
            logger.debug('start position:'+str(self.start_pos))
        
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
        if self.__debug:
            logger.debug('end drop position:'+str(self.end_pos)+',row:'+str(self.row(self.itemAt(self.end_pos))))
        item = self.takeItem(self.row(self.itemAt(self.start_pos)))
        #self.removeItemWidget(self.itemAt(self.start_pos))
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
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
            if self.__debug:
                logger.debug('Function name:'+str(f.f_code.co_name)+', '+str(f.f_lineno))
        if f.f_lineno != 1367:self.signal.emit()
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
            if self.__debug:
                logger.debug('List name:'+str(self.list_names))
                logger.debug('Delete row:'+str(self.row(delitem)))
            self.out_signal.emit({'data':{'index':self.row(delitem)},'type':'delete','togo':None})
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
    
    def insertItemSlot(self,ind,newitem):
        self.list_names.insert(ind,newitem.text())
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
    """
    """
    def __init__(self,debug=False):
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
'''
class LinkedCanvasAndLayers(QObject):
    refresh = pyqtSignal()
    def __init__(self,canvas,layers,debug=False):
        self.__debug = debug
        self.__layers = layers
        self.__canvas = canvas
        self.__layers.signal[dict].connect(self.requestSignal)
        self.__canvas.changed[dict].connect(self.requestSignal)
        self.__canvas.added[dict].connect(self.requestSignal)
        self.__canvas.deleted[dict].connect(self.requestSignal)
    
    def requestSignal(self,content):
        if content['mode'] in ['add','new']:
            self.__layers.addLayerStack(self.__canvas.canvas)
        elif content['mode'] == 'delete':
            self.__layers.removeLayerStack(self.__canvas.currentCanvasIndex())
        pass'''

class LayerMain(QWidget):
    """
    This class is an main component of layer widget, 
    it can change mixed functions for each layer, 
    and it can also set opacity for each layer.
    """
    in_signal = pyqtSignal(dict)
    out_signal = pyqtSignal(dict)
    # refresh = pyqtSignal()
    def __init__(self,tabCanvas,debug=False):
        super().__init__()
        self.__debug = debug
        self.setStyleSheet('color:white;background-color:#535353;')
        self.currentIndex = 0
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setSpacing(0)
        self.lay.setAlignment(Qt.AlignCenter)
        self.layer_list = ListWidget(debug=self.__debug)
        self.layer_list.setStyleSheet('QListWidget{color:white;background-color:#535353;border:1px solid #282828;}')
        #self.layer_list.Data_init(QIcon(ops.cvtCV2Pixmap(cv2.copyMakeBorder(cv2.resize(self.tab_canvas.canvas.layers.Image,(40,30)),3,3,3,3,borderType=cv2.BORDER_CONSTANT,dst=None,value=[200,200,200]))))
        # self.initWithLayerStack()
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
            'QComboBox::down-arrow{image:url(./static/UI/angle-down.svg);border:0px;}'
            'QToolTip{color:white;background-color:#535353;}')
        self.adjLayout.addWidget(self.mix_combox)
        self.adjLayout.addWidget(self.opacity_lb)
        self.adjLayout.addWidget(self.opacity_val)
        self.adjBox.setLayout(self.adjLayout)
        self.lay.addWidget(self.adjBox)
        self.mix_combox.activated[str].connect(self.select)
        self.lay.addWidget(self.layer_list)
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
        self.del_btn.setIcon(QIcon('./static/UI/trash.svg'))
        self.new_btn.setIcon(QIcon('./static/UI/sticky-note.svg'))
        self.cpy_btn.setIcon(QIcon('./static/UI/copy.svg'))
        self.grp_btn.setIcon(QIcon('./static/UI/folder.svg'))
        self.adj_btn.setIcon(QIcon('./static/UI/adjust.svg'))
        self.mask_btn.setIcon(QIcon('./static/UI/mask.svg'))
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
        self.layer_list.signal.connect(self.sltLayer)
        self.layer_list.setCurrentRow(0)
        self.layer_list.drag_signal[int,int].connect(self.chgLayer)
        self.opacity_val.textChanged[str].connect(self.setOpacity)
        self.in_signal[dict].connect(self.doMsg)
        self.layer_list.out_signal[dict].connect(self.listwidgetMsg)
        self.show()

    def listwidgetMsg(self, content):
        logger.debug('LayerWidget send message: '+str(content))
        if not content['togo']:
            if content['type'] == 'new':
                self.newLayer()
            elif content['type'] == 'delete':
                self.delLayer()
            # elif content['type'] == ''
        else:
            pass

    def doMsg(self, content):
        logger.debug('LayerView request message: '+str(content))
        self.initWithLayerStack(content['data']['layer'])
    '''
    def check(self):
        layers = self.tab_canvas.canvas.layers.layer_names
        if self.__debug:
            logger.debug('Layerlist count:'+str(self.layer_list.count())+', layers count:'+str(len(layers)))
        assert self.layer_list.count() == len(layers), 'ListWidget count is different from layers count.'
        for i in range(self.layer_list.count()):
            if self.__debug:
                logger.debug('listwidget name:'+self.layer_list.item(i).text()+', layer name:'+layers[-i])
            assert self.layer_list.item(i).text() == layers[-i], 'layer name is different.'
    
    def setCurrentLayerStack(self,idx):
        try:
            self.tab_canvas.canvas.layers = self.stack_list[idx]
            self.currentIndex = idx
            self.initWithLayerStack()
        except Exception as e:
            logger.error('There is an error when set current layerstack:'+str(e))
    
    def currentLayerStack(self):
        return self.currentIndex
    
    def addLayerStack(self,stack):
        if self.__debug:
            logger.debug('Add layerstack.')
        try:
            self.stack_list.append(stack)
            self.setCurrentLayerStack(len(self.stack_list)-1)
        except Exception as e:
            logger.error('There is an error when add a layerstack:'+str(e))
    
    def removeLayerStack(self,idx):
        if self.__debug:
            logger.debug('Remove layerstack.')
        try:
            self.stack_list.pop(idx)
            self.setCurrentLayerStack(idx if idx < len(self.stack_list) else idx - 1)
    '''
    
    def setOpacity(self,val):
        if val == '':
            val = 1.0
        elif val[-1] == '%':
            val = float(val[:-1])
        else:
            val = float(val)/100.0
        # self.tab_canvas.canvas.layers.setCurrentLayerOpacity(val)
    
    def group(self):
        pass
    
    def adjLayer(self):
        pass
    
    def addMask(self):
        pass
    
    def initWithLayerStack(self, layer):
        self.layer_list.clear()
        for item in layer.layer:
            font = QFont()
            font.setPointSize(10)
            tmp_item = QListWidgetItem(self.layer_list)
            tmp_item.setIcon(QIcon(item.icon))
            tmp_item.setFont(font)
            if not item.name:
                item.name = 'layer-1'
            tmp_item.setText(item.name)
            tmp_item.setTextAlignment(Qt.AlignCenter)
            self.layer_list.insertItemSlot(0,tmp_item)
        lsize = len(layer.layer)
        if self.__debug:
            logger.debug('The layers name:'+str(self.layer_list.list_names))
            logger.debug('Set current row:'+str(layer.selectedLayerIndex))
        self.layer_list.setCurrentRow(layer.selectedLayerIndex)
        pass
    
    def chgLayer(self,start,end):
        lsize = len(self.layer_list)
        if self.__debug:
            logger.debug('Change layer from '+str(start)+' to '+str(end)+', total '+str(lsize)+' layers.')
        # self.tab_canvas.canvas.layers.exchgLayer(lsize - start - 1,lsize - end - 1)
        self.out_signal.emit({'data':{'start':start,'end':end},'type':'exchange','togo':'layer'})
        pass
    
    def changeRow(self,ind):
        lsize = len(self.layer_list)
        self.layer_list.setCurrentRow(ind)
    
    def newLayer(self):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        while True:
            newname = QInputDialog.getText(self, "Please Input Name", "")
            if newname[0] in self.layer_list.list_names:
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
                # self.layer_list.addItemSlot(QIcon(ops.cvtCV2PixmapAlpha(self.tab_canvas.canvas.layers.background)),ind,newname[0])
                # self.tab_canvas.canvas.layers.addLayer(lsize - ind,newname[0])
                self.out_signal.emit({'data':{'index':ind,'name':newname[0]},'type':'newlayer','togo':'layer'})
                break
        pass
    
    # def refreshLayerIcon(self):
    #     cur = self.layer_list.currentItem()
    #     ind = self.layer_list.row(cur)
    #     lsize = len(self.layer_list)
    #     if self.__debug:
    #         logger.debug('current item:'+str(cur)+', index:'+str(ind)+', total length:'+str(lsize))
    #     cur.icon = QIcon(self.tab_canvas.canvas.layers.layer[lsize - ind - 1].icon)
    
    # def addLayer(self,img,name):
    #     if self.layer_list.count() == 0:
    #         ind = 0
    #     else:
    #         cur = self.layer_list.currentItem()
    #         ind = self.layer_list.row(cur)
    #     lsize = len(self.layer_list)

    #     # self.tab_canvas.canvas.layers.addLayer(lsize - ind,name,img)
    #     if self.__debug:
    #         logger.debug('Add Layer to:'+str(lsize-ind)+', view index:'+str(ind)+', name:'+name+', total '+str(len(self.layer_list.list_names))+' layers.')
    #         # logger.debug([x.layerName for x in self.tab_canvas.canvas.layers.layer])
    #     self.layer_list.addItemSlot(QIcon(self.tab_canvas.canvas.layers.layer[lsize - ind].icon),ind,name)
    #     self.layer_list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
    #     self.refresh.emit()

    def addLayer(self, layer):
        if self.layer_list.count() == 0:
            ind = 0
        else:
            cur = self.layer_list.currentItem()
            ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)

        # self.tab_canvas.canvas.layers.addLayer(lsize - ind,name,img)
        if self.__debug:
            logger.debug('Add Layer to:'+str(lsize-ind)+', view index:'+str(ind)+', name:'+layer.layer[lsize - ind].name+', total '+str(len(self.layer_list.list_names))+' layers.')
            # logger.debug([x.layerName for x in self.tab_canvas.canvas.layers.layer])
        self.layer_list.addItemSlot(QIcon(layer.layer[lsize - ind].icon),ind,name)
        self.layer_list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
        self.refresh.emit()
    
    def delLayer(self):
        if not self.layer_list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to delete this layer?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
    
            if reply == QMessageBox.Yes:
                cur = self.layer_list.currentItem()
                ind = self.layer_list.row(cur)
                lsize = len(self.layer_list)
                # self.layer_list.deleteItemSlot()
                # self.tab_canvas.canvas.layers.delLayer(lsize - ind - 1)
                self.out_signal.emit({'data':{'index':ind},'type':'dellayer','togo':'layer'})
                # self.layer_list.setCurrentRow(ind-1,QItemSelectionModel.ClearAndSelect)
        pass
    
    def cpyLayer(self):
        if not self.layer_list.selectedItems():
            QMessageBox.warning(self, 'Warning',
            "No selected layer!", QMessageBox.Yes)
        else:
            cur = self.layer_list.currentItem()
            ind = self.layer_list.row(cur)
            name = self.layer_list.list_names[ind] + '-copy'
            i = 0
            while True:
                if name in self.layer_list.list_names:
                    name = name + '_' + str(i)
                    continue
                else:
                    break
            lsize = len(self.layer_list)
            # self.layer_list.addItemSlot(QIcon(self.tab_canvas.canvas.layers.layer[lsize - ind - 1].icon),ind,name)
            # self.tab_canvas.canvas.layers.cpyLayer(ind,name)
            self.out_signal.emit({'data':{'index':ind,'name':name},'type':'cpylayer','togo':'layer'})
            # self.layer_list.setCurrentRow(ind,QItemSelectionModel.ClearAndSelect)
            # self.refresh.emit()
        pass
    
    def sltLayer(self):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        
        #print(self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1])
        if self.__debug:
            logger.debug('Select layer index:'+str(ind)+', lsize:'+str(lsize)+', ind:'+str(ind))
        # self.mix_combox.setCurrentText(self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1])
        # self.tab_canvas.canvas.layers.sltLayer(lsize - ind - 1)
        # self.tab_canvas.canvas.draw.setImageRect(self.tab_canvas.canvas.layers.currentImageObject().imageRect)
        # self.tab_canvas.canvas.draw.redraw()
        self.out_signal.emit({'data':{'index':ind},'type':'sltlayer','togo':'layer'})
        if ind  == lsize - 1:
            # self.tab_canvas.canvas.layers.mix_list[lsize - ind - 1] = 'Normal'
            self.mix_combox.setCurrentText('Normal')
            self.mix_combox.setEnabled(False)
            self.opacity_val.setEnabled(False)
        else:
            self.mix_combox.setEnabled(True)
            self.opacity_val.setEnabled(True)
    
    def select(self,s):
        cur = self.layer_list.currentItem()
        ind = self.layer_list.row(cur)
        lsize = len(self.layer_list)
        #print(lsize,ind,lsize - ind - 1)
        if self.__debug:
            logger.debug('Set mix:'+str(s)+'index:'+str(ind))
        # self.tab_canvas.canvas.layers.setMix(lsize - ind - 1,s)
        self.out_signal.emit({'data':{'index': ind, 'mode':s},'type':'mix','togo':'layer'})