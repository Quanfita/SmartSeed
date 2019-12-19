# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:12:17 2019

@author: Quanfita
"""


class ResizeDialog(QDialog):
    """
    This is the dialog of resize canvas.
    """
    def __init__(self,tar,sizeFun):
        super().__init__()
        self.target = tar
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640,480)
        self.setWindowTitle('Resize '+self.target)
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        self.canvas_width, self.canvas_height = sizeFun()
        
        self.w_lb = QLabel('width:',self)
        self.w_lb.setAlignment(Qt.AlignLeft)
        self.w_lb.setGeometry(180,120,80,20)
        
        self.h_lb = QLabel('height:',self)
        self.h_lb.setAlignment(Qt.AlignLeft)
        self.h_lb.setGeometry(180,200,80,20)
        
        self.w_line = QLineEdit(self)
        self.w_line.installEventFilter(self)
        self.w_line.setGeometry(180,150,50,30)
        self.w_line.setPlaceholderText('512')
        
        self.h_line = QLineEdit(self)
        self.h_line.installEventFilter(self)
        self.h_line.setGeometry(180,230,50,30)
        self.h_line.setPlaceholderText('512')
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(350,400,80,30)
        self.ok_btn.setFocus(True)
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.turnBack)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(250,400,80,30)
        self.cancel_btn.clicked.connect(self.close)
        
        regx = QRegExp("^[1-9][0-9]{3}$")
        validator_w = QRegExpValidator(regx, self.w_line)
        validator_h = QRegExpValidator(regx, self.h_line)
        self.w_line.setValidator(validator_w)
        self.h_line.setValidator(validator_h)
        
        self.show()
        
    def turnBack(self):
        if self.w_line.text() != '' and self.h_line.text()!='':
            self.canvas_width = int(self.w_line.text())
            self.canvas_height = int(self.h_line.text())
        elif self.w_line.text() != '':
            self.canvas_width = int(self.w_line.text())
        elif self.h_line.text()!='':
            self.canvas_height = int(self.h_line.text())
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue("width",self.canvas_width)
        settings.setValue("height", self.canvas_height)
        '''
        logger.info('Create new canvas as '+str(self.canvas_color)+
                    ' with '+str(self.canvas_width)+'x'+str(self.canvas_height))'''
        self.accept()


class Welcome(QDialog):
    """
    This is the welcome view of the app, 
    user would choose to open image or new a canvas.
    """
    def __init__(self,debug=False):
        super(Welcome,self).__init__()
        self.__debug = debug
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.canvas_color = '#FFFFFF'
        self.canvas_width = 512
        self.canvas_height = 512
        self.canvas_dpi = 72
        self.canvas_alpha = 1
        self.resize(360, 480)
        self.setFixedSize(360, 480)
        self.setWindowTitle('New Canvas')
        self.setStyleSheet("QDialog{background-color:#535353;}")
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        
        self.main_lb = QLabel('New Canvas',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(80,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        self.main_lb.setStyleSheet("color:white;");
        
        self.new_title = QLabel('File Name',self)
        self.new_title.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.new_title.setGeometry(60,80,100,25)
        self.new_title.setStyleSheet("color:white;");
        
        self.title_name = QLineEdit(self)
        self.title_name.installEventFilter(self)
        self.title_name.setGeometry(60,110,100,25)
        self.title_name.setStyleSheet("color:white;background-color:#434343;border:0px;")
        self.title_name.setPlaceholderText('Untitled-1')
        
        self.w_lb = QLabel('Width:',self)
        self.w_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.w_lb.setGeometry(60,140,80,25)
        self.w_lb.setStyleSheet("color:white;");
        
        self.h_lb = QLabel('Height:',self)
        self.h_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.h_lb.setGeometry(60,200,80,25)
        self.h_lb.setStyleSheet("color:white;")
        
        self.w_line = QLineEdit(self)
        self.w_line.installEventFilter(self)
        self.w_line.setGeometry(60,170,50,25)
        self.w_line.setPlaceholderText('512')
        self.w_line.textEdited[str].connect(self.countWidthPix)
        self.w_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.h_line = QLineEdit(self)
        self.h_line.installEventFilter(self)
        self.h_line.setGeometry(60,230,50,25)
        self.h_line.setPlaceholderText('512')
        self.h_line.textEdited[str].connect(self.countHeightPix)
        self.h_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.dpi_lb = QLabel('DPI:',self)
        self.dpi_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.dpi_lb.setGeometry(60,260,80,25)
        self.dpi_lb.setStyleSheet("color:white;")
        
        self.dpi_line = QLineEdit(self)
        self.dpi_line.installEventFilter(self)
        self.dpi_line.setGeometry(60,290,50,25)
        self.dpi_line.setPlaceholderText('72')
        self.dpi_line.textEdited[str].connect(self.countPix)
        self.dpi_line.setStyleSheet("color:white;background-color:#434343;border:0px;")
        
        self.color_lb = QLabel('BackGround Content:',self)
        self.color_lb.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.color_lb.setGeometry(60,320,150,25)
        self.color_lb.setStyleSheet("color:white;");
        
        pix_info = ['px/inch','px/cm']
        self.dpi_combox = QComboBox(self)
        self.dpi_combox.addItems(pix_info)
        self.dpi_combox.setGeometry(140,290,100,25)
        self.dpi_combox.activated[str].connect(self.selectDpiMode)
        self.dpi_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        pix_info = ['px','cm','inch']
        self.pix_combox = QComboBox(self)
        self.pix_combox.addItems(pix_info)
        self.pix_combox.setGeometry(140,170,100,25)
        self.pix_combox.activated[str].connect(self.selectPix)
        self.pix_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        self.color_btn = QPushButton(self)
        self.color_btn.setGeometry(230,350,25,25)
        self.color_btn.setStyleSheet("QPushButton{background-color:white}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.color_btn.clicked.connect(self.changeColor)
        
        color_info = ['White','Black','Background Color','Transparent']
        self.color_combox = QComboBox(self)
        self.color_combox.addItems(color_info)
        self.color_combox.setGeometry(60,350,150,25)
        self.color_combox.activated[str].connect(self.selectColor)
        self.color_combox.setStyleSheet("QComboBox{color:white;background-color:#434343;border:1px solid gray;border-radius:3px;padding:1px 2px 1px 2px;min-width:6em;}"
           'QComboBox::drop-down{height:25px;width: 25px;subcontrol-origin:padding;subcontrol-position:top right;}'
            'QComboBox::down-arrow{image:url(./UI/angle-down.svg);border:0px;}')
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(220,410,80,30)
        self.ok_btn.setFocus(True)
        self.ok_btn.setDefault(True)
        self.ok_btn.setStyleSheet("QPushButton{color:white;background-color:#1473e6;border-radius:15px;}"
                                    'QPushButton:focus{color:white;background-color:#1473e6;border:0px;}'
                                    'QPushButton:hover{color:white;background-color:#0f64d2;border:0px;}')
        self.ok_btn.clicked.connect(self.turnBack)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(100,410,80,30)
        self.cancel_btn.setStyleSheet("QPushButton{color:white;background-color:#434343;border:2px solid white;border-radius:15px;}"
                                    'QPushButton:focus{color:white;background-color:#1473e6;border:0px;}'
                                    'QPushButton:hover{color:#656565;background-color:#cdcdcd;border:0px;}')
        self.cancel_btn.clicked.connect(self.close)
        
        self.open_btn = QPushButton('Open File',self)
        self.open_btn.setGeometry(180,110,80,25)
        self.open_btn.setStyleSheet("color:white;background-color:#434343;border:1px;")
        self.open_btn.clicked.connect(self.openimage)
        
        regx = QRegExp("^[1-9][0-9]{3}$")
        validator_w = QRegExpValidator(regx, self.w_line)
        validator_h = QRegExpValidator(regx, self.h_line)
        validator_dpi = QRegExpValidator(regx, self.dpi_line)
        self.w_line.setValidator(validator_w)
        self.h_line.setValidator(validator_h)
        self.dpi_line.setValidator(validator_dpi)
        
        self.show()
    
    def selectDpiMode(self,text):
        # To set the dpi unit.
        if self.dpi_combox.currentText() == 'px/inch':
            self.dpi_line.setText(str(self.canvas_dpi))
        elif self.dpi_combox.currentText() == 'px/cm':
            self.dpi_line.setText(str(round(self.canvas_dpi/2.54,2)))
        else:
            pass
    
    def countPix(self,text):
        # To count the pixel number of width and height for canvas. 
        if self.dpi_combox.currentText() == 'px/inch':
            if text != '':
                self.canvas_dpi = int(text)
            self.selectPix(self.pix_combox.currentText())
        elif self.dpi_combox.currentText() == 'px/cm':
            if text != '':
                self.canvas_dpi = int(float(text)*2.54)
            self.selectPix(self.pix_combox.currentText())
        else:
            pass
    
    def countWidthPix(self,text):
        # To count the pixel number of width for canvas.
        if self.pix_combox.currentText() == 'px':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text()))
        elif self.pix_combox.currentText() == 'cm':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text())*self.canvas_dpi/2.54)
        elif self.pix_combox.currentText() == 'inch':
            if self.w_line.text() != '':
                self.canvas_width = int(float(self.w_line.text())*self.canvas_dpi)
        else:
            pass
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
    
    def countHeightPix(self,text):
        # To count the pixel number of height for canvas.
        if self.pix_combox.currentText() == 'px':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text()))
        elif self.pix_combox.currentText() == 'cm':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text())*self.canvas_dpi/2.54)
        elif self.pix_combox.currentText() == 'inch':
            if self.h_line.text() != '':
                self.canvas_height = int(float(self.h_line.text())*self.canvas_dpi)
        else:
            pass
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
    
    def changeColor(self):
        # To set background color of canvas.
        color = QColorDialog.getColor()
        self.color_combox.setCurrentText('Background Color')
        self.color_btn.setStyleSheet("QPushButton{background-color:"+str(color.name())+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
        self.canvas_color = color.name()
        self.canvas_alpha = 1
    
    def selectColor(self,text):
        # To set background color of canvas with perset.
        if text in ['White','Black','white','black']:
            self.color_btn.setStyleSheet("QPushButton{background-color:"+str(text)+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
            self.canvas_color = QColor(text).name()
            self.canvas_alpha = 1
        elif text == 'Transparent':
            self.color_btn.setStyleSheet("QPushButton{background-color:"+str(text)+"}"
                                    "QPushButton{border-radius:5px}"
                                     "QPushButton{border:1px}")
            self.canvas_color = QColor(0,0,0,0).name()
            self.canvas_alpha = 0
    
    def selectPix(self,text):
        # To calculate  the pixel number of canvas with different unit.
        if self.dpi_combox.currentText() == 'px/cm':
            tmp_dpi = self.canvas_dpi/2.54
        else:
            tmp_dpi = self.canvas_dpi
        if self.__debug:
            logger.debug('Info:'+str(self.w_line.text())+', '+str(self.h_line.text())+', '+str(self.canvas_width)+', '+str(self.canvas_height))
        if text == 'px':
            self.w_line.setText(str(int(self.canvas_width)))
            self.h_line.setText(str(int(self.canvas_height)))
        elif text == 'cm':
            self.w_line.setText(str(round(self.canvas_width/tmp_dpi*2.54,2)))
            self.h_line.setText(str(round(self.canvas_height/tmp_dpi*2.54,2)))
        elif text == 'inch':
            self.w_line.setText(str(round(self.canvas_width/tmp_dpi,2)))
            self.h_line.setText(str(round(self.canvas_height/tmp_dpi,2)))
    
    def callBack(self):
        # This is a callback function.
        return self.canvas_color,self.canvas_width,self.canvas_height,self.canvas_dpi
    
    def turnBack(self):
        # save the arguements to tmp.ini, and close this dialog.
        #self.info = self.callBack()
        settings = QSettings("tmp.ini", QSettings.IniFormat)
        settings.setValue('mode',0)
        settings.setValue("width",self.canvas_width)
        settings.setValue("height", self.canvas_height)
        settings.setValue("color", self.canvas_color)
        settings.setValue('alpha',self.canvas_alpha)
        settings.setValue('dpi',self.canvas_dpi)
        #settings.setValue('dpiMode',self.dpi_combox.currentText())
        settings.setValue("imagePath",None)
        settings.setValue("imageName",self.title_name.text())
        logger.info('Create new canvas as '+str(self.canvas_color)+
                    ' with '+str(self.canvas_width)+'x'+str(self.canvas_height))
        self.accept()
        
    def openimage(self):
        # If user want to open a image, this function would be done.
        # It can read the image and get some information, 
        # and save these information into tmp.ini.
        imgName,imgType = QFileDialog.getOpenFileName(self,"打开图片","",
                                                     " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
        if not imgName:
            logger.warning('None Image has been selected!')
            return
        else:
            #img = cv2.imread(imgName)
            im = Image.open(imgName)
            logger.info('Open image: '+imgName+', '+str(im.format)+str(im.size)+str(im.mode)+str(im.info))
            try:
                self.canvas_dpi = im.info['dpi'][0]
            except:
                self.canvas_dpi = 72
            self.canvas_width, self.canvas_height = im.size
            #self.canvas_dpi = int(self.dpi_line.text())
            settings = QSettings("tmp.ini", QSettings.IniFormat)
            settings.setValue('mode',1)
            settings.setValue("width",self.canvas_width)
            settings.setValue("height", self.canvas_height)
            settings.setValue("color", self.canvas_color)
            settings.setValue('alpha',0)
            settings.setValue('dpi',self.canvas_dpi)
            settings.setValue('imageMode',im.mode)
            settings.setValue('imageFormat',im.format)
            settings.setValue("imagePath",imgName)
            settings.setValue("imageName",imgName.split('/')[-1])
            del im
        self.accept()


class AdjDialog(QDialog):
    """
    The adjustment dialog of image adjustment.
    """
    def __init__(self,img,tar,debug=False):
        super(AdjDialog,self).__init__()
        self.setStyleSheet('QDialog{color:white;background-color:#535353;}'
                            "QPushButton{color:white;background-color:#434343;border:2px solid white;border-radius:15px;}"
                            'QPushButton:focus{color:white;background-color:#1473e6;border:1px;}'
                            'QPushButton:hover{color:#656565;background-color:#cdcdcd;border:1px;}'
                            'QLabel{color:white;}')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640, 480)
        self.setFixedSize(640, 480)
        self.setWindowTitle('Adjustment')
        self.setWindowIcon(QIcon('./UI/icon_32.png'))
        self.__img = img
        self.__tmp_img = np.copy(self.__img.Image)
        self.img_h,self.img_w = self.__img.height,self.__img.width
        self.__target = tar

        self.main_lb = QLabel('Adjustment',self)
        self.main_lb.setAlignment(Qt.AlignCenter)
        self.main_lb.setGeometry(self.width()//2 - 100,10,200,70)
        self.main_lb.setFont(QFont('Times New Roman',24))
        
        self.lb = QLabel('Values: 0',self)
        self.lb.setAlignment(Qt.AlignLeft)
        self.lb.setGeometry(3*self.width()//5 + 10,120,100,30)
        
        self.imgShow = QLabel('',self)
        self.imgShow.setAlignment(Qt.AlignCenter)
        self.imgShow.setGeometry(30,100,350,350)
        '''
        self.__tmp_img = cv2.resize(self.__tmp_img,(400,
                                        self.img_h*400//self.img_w) if self.img_w >= self.img_h else (self.img_w*400//self.img_h,400))
        '''
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
        
        self.sl = QSlider(Qt.Horizontal,self)
        #self.sl.resize(30,100)
        self.sl.setGeometry(3*self.width()//5 + 10,150,200,30)
        if self.__target == 'light':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'comp':
            self.sl.setMinimum(-30)
            self.sl.setMaximum(50)
        elif self.__target == 'custom':
            self.sl.setMinimum(-100)
            self.sl.setMaximum(100)
        elif self.__target == 'hue':
            self.sl.setMinimum(-180)
            self.sl.setMaximum(180)
        else:
            pass
        self.sl.setTickPosition(QSlider.TicksAbove) 
        
        self.sl.valueChanged[int].connect(self.setValue)
        #self.sl.sliderReleased.connect(self.change)
        
        self.ok_btn = QPushButton('OK',self)
        self.ok_btn.setGeometry(550,430,80,30)
        self.ok_btn.clicked.connect(self.saveImage)
        self.cancel_btn = QPushButton('Cancel',self)
        self.cancel_btn.setGeometry(450,430,80,30)
        self.cancel_btn.clicked.connect(self.close)
        
        self.show()
    
    def setTar(self,tar):
        self.__target = tar
    
    def setValue(self,value):
        self.sl.setValue(value)
        self.lb.setText('Value: '+str(value))
        self.change()
        pass
    
    def change(self):
        if self.__target == 'light':
            self.__tmp_img = light(self.__img.Image,self.sl.value())
        elif self.__target == 'comp':
            comp(self.__img.Image,self.sl.value())
            self.__tmp_img = cv2.imread('./tmp/comp.jpg')
        elif self.__target == 'custom':
            self.__tmp_img = custom(self.__img.Image,self.sl.value())
        elif self.__target == 'hue':
            self.__tmp_img = hue(self.__img.Image,self.sl.value())
        else:
            return
        self.imgShow.setPixmap(ops.cvtCV2Pixmap(self.__tmp_img))
    
    def saveImage(self):
        self.__img.changeImg(self.__tmp_img)
        self.accept()
        self.close()