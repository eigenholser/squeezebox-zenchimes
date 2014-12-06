#!/usr/bin/env python

import atexit
from bottle import (route, run, template, static_file, get, post, put, request,
        Bottle)
import json
import logging
import logging.config
import multiprocessing
import os
import signal
import sqlite3
import sys
from time import sleep
import zmq

from zenchimes.client import LMSCommandLineInterface
from zenchimes.scheduler import ChimeScheduler
from zenchimes import settings


logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

SERVER_HTTP_LISTEN_IP_ADDR = "0.0.0.0"
SERVER_HTTP_LISTEN_PORT = settings.SERVER_HTTP_LISTEN_PORT

context = zmq.Context()
socket = context.socket(zmq.PAIR)
url = "tcp://localhost:{}".format(settings.ZMQ_CONTROL_PORT)
socket.connect(url)

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


@app.get('/config/<parameter>')
def get_config_parameter(parameter):
    """Single configuration parameter."""

    conn = sqlite3.connect(settings.CHIME_DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    row = c.execute("SELECT * FROM config WHERE parameter = ?",
            (parameter,)).fetchone()
    row_dict = {}
    row_dict['section'] = row['section']
    row_dict['parameter'] = row['parameter']
    row_dict['value'] = row['value']
    row_dict['description'] = row['description']
    return json.dumps(row_dict)


@app.put('/config/<parameter>')
def put_config_parameter(parameter):
    """Single configuration parameter."""

    value = json.loads(request.forms.keys()[0])['value']
    conn = sqlite3.connect(settings.CHIME_DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("UPDATE config SET value = ? WHERE parameter = ?",
            (value, parameter,))
    conn.commit()
    # TODO: error handling.
    socket.send("CONFIG")
    return {'status': 'ok'}


@app.put('/chimes/<id:int>')

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

    socket.send("CONFIG")
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
def config_data():
    """
    Experimental API endpoint to get and set select config data using Python's
    ConfigParser and our configuration file.
    """

    if request.method == 'GET':
        chime_list = []
        conn = sqlite3.connect(settings.CHIME_DATABASE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        row_dict = {}
        for row in c.execute('SELECT * FROM config'):
            section = row['section']
            if not row_dict.get(section, None):
                row_dict[section] = {}
            row_dict[section][row['parameter']] = row['value']

        return json.dumps(row_dict)

    # TODO: Not implemented yet. Need JavaScript code...
    if request.method == 'PUT':
        return {'status': 'ok'}


@app.get('/<filepath:path>')
def serve_static(filepath):
    """
    Fetch arbitrary static files in PUBLIC_ROOT.
    """
    logger.debug("Request {}".format(filepath))
    return static_file(filepath, root=settings.PUBLIC_ROOT)


@app.route('/')
def index():
    """
    Return Zen Chimes app.
    """
    logger.debug("Request index.html")
    return static_file('index.html', root=settings.PUBLIC_ROOT)


if __name__ == '__main__':
    run(app=StripPathMiddleware(app),
        host=SERVER_HTTP_LISTEN_IP_ADDR, port=SERVER_HTTP_LISTEN_PORT)
