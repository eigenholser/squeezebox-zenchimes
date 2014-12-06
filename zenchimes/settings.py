import logging
import logging.handlers
import os

from zenchimes.utilities import sockethandler


PROJECT_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.normpath(os.path.join(os.environ['PYTHON_HOME'], '..'))

PUBLIC_ROOT = '{0}/static'.format(PROJECT_ROOT)
LOG_FILE = '{0}/zenchimes.log'.format(APP_ROOT)
CHIME_DATABASE = '{0}/zenchimes.db'.format(APP_ROOT)
SERVER_HTTP_LISTEN_PORT = os.environ['SERVER_HTTP_LISTEN_PORT']
TCP_LOGGING_PORT = os.environ['TCP_LOGGING_PORT']
ZMQ_CONTROL_PORT = os.environ['ZMQ_CONTROL_PORT']
LOGGING_LEVEL = os.environ['LOGGING_LEVEL']

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
            'filename': LOG_FILE,
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
        'level': LOGGING_LEVEL,
        'handlers': ['console', 'file'],
        'propagate': False,
    },
    'loggers': {
        'zenchimes': {
            'handlers': ['socket'],
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        '__main__': {
            'handlers': ['socket'],
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
    },
}

