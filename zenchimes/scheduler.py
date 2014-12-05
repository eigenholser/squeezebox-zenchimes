import ConfigParser
import json
import logging
import logging.config
import logging.handlers
import os
import pytz
import requests
import signal
import sys
import zmq

from datetime import date, datetime, time, timedelta
from pytz import timezone
from threading import Thread
from tornado.tcpserver import TCPServer
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

from zenchimes.client import LMSCommandLineInterface
from zenchimes.utilities import logged_class, sockethandler, LogServer
from zenchimes import settings


@logged_class
class ChimeScheduler(object):
    """Initialize chime events based on configuration. Spawn a chime player
    when the chime event is due."""

    fmt = '%H:%M:%S'
    is_closing = False
    loop = None

    def __init__(self, config=None, *args, **kwargs):
        """Initialize chime scheduler."""
        # SIGINT to stop
        # SIGUSR1 to reread configuration and re-initialize schedule.
        signal.signal(signal.SIGINT, self.handler_signal)
        signal.signal(signal.SIGUSR1, self.handler_signal)

        self.loop = IOLoop.instance()
        self.config = config
        self.configure()

    def configure(self):
        """Read configuration from web server API. Initialize."""
        self.logger.info("Reading configuration.")
        config = self.config
        req = requests.get('http://localhost:3031/config')
        config = json.loads(req.text)
        self.TIMEZONE = config['scheduler']['timezone']
        self.STARTTIME = config['scheduler']['starttime']
        self.ENDTIME = config['scheduler']['endtime']
        self.CHIME_INTERVAL = int(config['scheduler']['chime_interval'])

        os.environ['TZ'] = self.TIMEZONE
        s = datetime.strptime(self.STARTTIME, self.fmt)
        e = datetime.strptime(self.ENDTIME, self.fmt)

        diff = e - s
        self.event_count = int(diff.total_seconds() / self.CHIME_INTERVAL)
        self.current_event = 0
        self.events = []

        for i in range(self.event_count + 1):
            next_event = \
                s + timedelta(seconds=self.CHIME_INTERVAL * i)
            self.events.append(next_event.time())

        self.startx = time(s.hour, s.minute, s.second)
        self.endx = time(e.hour, e.minute, e.second)
        self.advance_counter()

    def current_time(self):
        """Returns current time."""
        t = datetime.now()
        self.logger.debug("current_time: {0}".format(time(t.hour, t.minute, t.second)))
        return time(t.hour, t.minute, t.second)

    def is_event(self):
        """Check to see if current time corresponds with an event. Returns
        boolean status."""
        current_time = self.current_time()
        current_event_time = self.events[self.current_event]
        cet = current_event_time
        current_event_time = time(cet.hour, cet.minute, cet.second)
        self.logger.debug("current_event_time: {0}".format(current_event_time))
        fudge_factor = (datetime.combine(date(1,1,1),
            current_event_time) + timedelta(seconds=60)).time()
        self.logger.debug("fudge_factor: {0}".format(fudge_factor))
        status = current_event_time <= current_time <= fudge_factor
        return status

    def advance_counter(self):
        """Advance event counter to current event. Call this one time only from
        __init__()."""
        current_time = self.current_time()
        fudge_factor = (datetime.combine(date(1,1,1),
                current_time) + timedelta(seconds=60)).time()
        if current_time > fudge_factor:
            # Leave self.current_event == 0. No counter advance.
            return

        for i in range(self.event_count):
            event = self.events[i]
            if event < current_time:
                self.current_event += 1
            else:
                break

    def handle_ctrl_msg(self, event):
        msg = event[0]
        self.logger.info("Received control message {}".format(msg))
        if msg == 'CONFIG':
            self.configure()

    def stop(self):
        if self.is_closing:
            # TODO: Log a message
            self.loop.stop()

    def handler_signal(self, signum, frame):
        """Handle signals."""
        if signum == signal.SIGINT:
            loop = self.loop
            loop.add_callback_from_signal(self.stop)
            self.is_closing = True
        elif signum == signal.SIGUSR1:
            # TODO: Log a message.
            self.configure()

    def start(self):
        """Initialize and start the event loop. Listen for ZMQ control
        messages."""
        ctx = zmq.Context()
        socket = ctx.socket(zmq.PAIR)
        socket.bind("tcp://*:5000")

        loop = self.loop
        logserver = LogServer()
        logserver.listen(settings.TCP_LOGGING_PORT)

        stream = ZMQStream(socket, loop)
        stream.on_recv(self.handle_ctrl_msg)

        pc = PeriodicCallback(self.chime, 15000, loop)
        pc.start()

        loop.start()

    def chime(self):
        """Check for chime event. Handle if necessary."""
        is_event = self.is_event()
        self.logger.debug("is_event: {0}".format(is_event))
        if is_event:
            self.logger.debug("Initializing LMSCommandLineInterface.")
            sbcli = LMSCommandLineInterface()

            # LMSCommandLineInterface sets error on initialization failure.
            if sbcli.error:
                self.logger.error(
                    "Unable to initialize LMSCommandLineInterface")
            else:
                self.logger.debug(
                    "sending play command for event {0}".format(
                    self.current_event))
                thread = Thread(target=sbcli.play_chime())

            if self.current_event == self.event_count:
                # Last event of the day, rewind.
                self.current_event = 0
            else:
                self.current_event += 1


if __name__ == '__main__':
    logging.config.dictConfig(settings.LOGGING_CONFIG)

    scheduler = ChimeScheduler(config=config)
    scheduler.start()

