from PyQt5.QtCore import QSettings
from setting import USER_CONF_FILE, TEMP_CONF_FILE, HISTORY_FILE, CONFIG_PATH

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
    for key in history['bitbucket.org']

def saveHistoryCfg(dic):
    cf = configparser.ConfigParser()
    date = time.strftime("%Y-%m-%d", time.localtime()) 
    cf.add_section(date)
    cf[date] = dic
    # print(os.path.join(CONFIG_PATH, HISTORY_FILE))
    with open(os.path.join(CONFIG_PATH, HISTORY_FILE),'w') as f:
        cf.write(f)

if __name__ == '__main__':
    saveHistoryCfg({})