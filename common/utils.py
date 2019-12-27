from PyQt5.QtCore import QSettings
from PIL import Image
from setting import USER_CONF_FILE, TEMP_CONF_FILE, HISTORY_FILE, CONFIG_PATH
from core import ops
from middleware.Structure import ImgObject
from PyQt5.QtWidgets import QFileDialog

import configparser
import time
import os

def readUserIni():
    settings = QSettings(os.path.join(CONFIG_PATH, USER_CONF_FILE), QSettings.IniFormat)
    res = {}
    for key in settings.allKeys():
        res[key] = settings.value(key)
    return res

def readTempIni():
    settings = QSettings(os.path.join(CONFIG_PATH, TEMP_CONF_FILE), QSettings.IniFormat)
    res = {}
    for key in settings.allKeys():
        res[key] = settings.value(key)
    return res

def saveTempIni(dic):
    settings = QSettings(os.path.join(CONFIG_PATH, TEMP_CONF_FILE), QSettings.IniFormat)
    for key in dic.keys():
        settings.setValue(key,dic[key])
    
def saveUserIni(dic):
    settings = QSettings(os.path.join(CONFIG_PATH, USER_CONF_FILE), QSettings.IniFormat)
    for key in dic.keys():
        settings.setValue(key,dic[key])

def readHistoryCfg():
    cf = configparser.ConfigParser()
    history = cf.read(os.path.join(CONFIG_PATH, HISTORY_FILE))
    sessions = cf.sections()
    for key in history['bitbucket.org']:
        pass

def saveHistoryCfg(dic):
    cf = configparser.ConfigParser()
    date = time.strftime("%Y-%m-%d", time.localtime()) 
    cf.add_section(date)
    cf[date] = dic
    # print(os.path.join(CONFIG_PATH, HISTORY_FILE))
    with open(os.path.join(CONFIG_PATH, HISTORY_FILE),'w') as f:
        cf.write(f)

def openImage(parent):
    imgName,imgType= QFileDialog.getOpenFileName(
                                parent,
                                "打开图片",
                                "",
                                " *.jpg;;*.png;;*.jpeg;;*.bmp;;All Files (*)")
    if imgName is '':
        return None
    else:
        im = Image.open(imgName)
        image = ImgObject(ops.imread(imgName),imgName.split('/')[-1])
        info = {'image':image,'size':im.size,'mode':im.mode,'format':im.format,'image_path':imgName,'image_name':imgName.split('/')[-1]}
        return info

def saveImage(parent, image, name, depth=8, dpi=72.0, quanlity=80):
    # 调用存储文件dialog
    fileName, tmp = QFileDialog.getSaveFileName(
                                parent,
                                'Save Image',
                                name,
                                '*.png *.jpg *.bmp', '*.png')
    if fileName is '':
        return False
    else:
        ops.imsave(image, fileName, depth=depth, dpi=dpi, quanlity=quanlity)
        return True

if __name__ == '__main__':
    saveHistoryCfg({})