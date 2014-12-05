import logging
import logging.handlers
import os

from zenchimes.utilities import sockethandler


PROJECT_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.normpath(os.path.join(os.environ['PYTHON_HOME'], '..'))

CONFIG_FILE = '{0}/zenchimes.cfg'.format(APP_ROOT)
LOG_FILE = '{0}/zenchimes.log'.format(APP_ROOT)
PUBLIC_ROOT = '{0}/static'.format(PROJECT_ROOT)
CHIME_DATABASE = '{0}/../extras/chimes.db'.format(PROJECT_ROOT)
SERVER_HTTP_LISTEN_PORT = os.getenv('SERVER_HTTP_LISTEN_PORT', 3031)
TCP_LOGGING_PORT = os.getenv('TCP_LOGGING_PORT', 8020)
ZMQ_CONTROL_PORT = os.getenv('ZMQ_CONTROL_PORT', 5000)
LOG_LEVEL = os.getenv('LOG_LEVEL', "DEBUG")

LOGGING_CONFIG = {
    'version': 1,
    'filters': {
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'zenchimes.log',
            'mode': 'a',
            'encoding': 'utf-8',
        },
        'socket': {
            '()': sockethandler,
            'formatter': 'default',
            'host': 'localhost',
            'port': TCP_LOGGING_PORT
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'file'],
        'propagate': False,
    },
    'loggers': {
        'zenchimes': {
            'handlers': ['socket'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        '__main__': {
            'handlers': ['socket'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

