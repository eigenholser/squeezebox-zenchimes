#!/usr/bin/env python

import atexit
from bottle import route, run, template, static_file, get, post, put, request, Bottle
import ConfigParser
import json
import logging
import multiprocessing
import os
import signal
import sqlite3
import sys
from time import sleep

from zenchimes.client import LMSCommandLineInterface
from zenchimes.scheduler import ChimeScheduler
from zenchimes import settings


#config = ConfigParser.ConfigParser()
#config.read("{0}".format(settings.CONFIG_FILE))

# TODO: Temporary
config = ConfigParser.ConfigParser()
config_file = "{0}/extras/zenchimes.cfg".format(os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
config.read(config_file)

# There is no logging yet so let's just make it work.
try:
    loglevel = config.get('zenchimes', 'loglevel')
except:
    loglevel = "INFO"

logging.basicConfig(filename=settings.LOG_FILE,
        level=eval("logging.{0}".format(loglevel)),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger()

## Fetch some configuration settings
HTTP_LISTEN_IP_ADDR = config.get('server', 'http_listen_ip_addr')
HTTP_LISTEN_PORT = config.get('server', 'http_listen_port')

app = application = Bottle()


class StripPathMiddleware(object):
    '''
    Get that slash out of the request
    '''
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)


@app.route('/')
def index():
    """
    Return Zen Chimes app.
    """
    return static_file('index.html', root=settings.PUBLIC_ROOT)


@app.route('<filepath:path>')
def serve_static(filepath):
    """
    Fetch arbitrary static files in PUBLIC_ROOT.
    """
    return static_file(filepath, root=settings.PUBLIC_ROOT)


@app.put('/chimes/<id:int>')
def chime_update(id):
    """
    API endpoint to set new active chime.
    """
    # Only one chime may be active. Set all to inactive, then set <id> to
    # active.
    conn = sqlite3.connect(settings.CHIME_DATABASE)
    c = conn.cursor()
    c.execute('UPDATE chime SET is_active = 0');
    c.execute('UPDATE chime SET is_active = 1 WHERE id = ?', (str(id)))
    conn.commit()

    return {'status': 'ok'}


@app.get('/chimes')
def chimes_collection():
    """
    API endpoint returns all chimes in the database.
    """
    chime_list = []
    conn = sqlite3.connect(settings.CHIME_DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for row in c.execute('SELECT * FROM chime'):
        row_dict = {}
        row_dict['id'] = row['id']
        row_dict['is_active'] = row['is_active']
        row_dict['description'] = row['description']
        row_dict['filename'] = row['filename']
        chime_list.append(row_dict)
    return json.dumps(chime_list)


@app.get('/config')
@app.put('/config')
def config_data():
    """
    Experimental API endpoint to get and set select config data using Python's
    ConfigParser and our configuration file.
    """
    config = ConfigParser.ConfigParser()

    if request.method == 'GET':
        config.read(settings.CONFIG_FILE)
        # TODO: Probably ought to do some exception handling so a bad edit
        # doesn't crash the server.
        config_data = {
            'zenchimes': {
                'loglevel': config.get('zenchimes', 'loglevel'),
            },
            'server': {
                'http_listen_ip_addr': config.get('server',
                    'http_listen_ip_addr'),
                'http_listen_port': config.get('server', 'http_listen_port'),
            },
            'scheduler': {
                'timezone': config.get('scheduler', 'timezone'),
                'starttime': config.get('scheduler', 'starttime'),
                'endtime': config.get('scheduler', 'endtime'),
                'chime_interval': config.get('scheduler', 'chime_interval'),
            },
            'player': {
                'lms_hostname': config.get('player', 'lms_hostname'),
                'lms_port': config.get('player', 'lms_port'),
                'mixer_volume': config.get('player', 'mixer_volume'),
                'lms_chime_path': config.get('player', 'lms_chime_path'),
            },
        }
        return json.dumps(config_data)

    # TODO: Not implemented yet. Need JavaScript code...
    if request.method == 'PUT':
        return {'status': 'ok'}


if __name__ == '__main__':
    run(app=StripPathMiddleware(app),
        host=HTTP_LISTEN_IP_ADDR, port=HTTP_LISTEN_PORT)
