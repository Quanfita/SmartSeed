import os
import sys
sys.path.append(os.path.dirname(__file__))

USER_CONF_FILE = 'user.ini'
TEMP_CONF_FILE = 'tmp.ini'
HISTORY_FILE = 'history.cfg'

BASE_PATH = os.path.dirname(__file__)
UI_PATH = os.path.join(os.path.dirname(__file__),'static/UI')
TABLE_PATH = os.path.join(os.path.dirname(__file__),'static/tables')
CONFIG_PATH = os.path.join(os.path.dirname(__file__),'conf')