import os

PROJECT_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.normpath(os.path.join(os.environ['PYTHON_HOME'], '..'))

CONFIG_FILE = '{0}/zenchimes.cfg'.format(APP_ROOT)
LOG_FILE = '{0}/zenchimes.log'.format(APP_ROOT)
PUBLIC_ROOT = '{0}/static'.format(PROJECT_ROOT)
CHIME_DATABASE = '{0}/../extras/chimes.db'.format(PROJECT_ROOT)
