import logging
import logging.handlers
import pickle
import struct

from tornado.tcpserver import TCPServer


def logged_class(cls):
    """Class Decorator to add a class level logger to the class with module and
    name."""
    cls.logger = logging.getLogger("{0}.{1}".format(cls.__module__, cls.__name__))
    return cls


def sockethandler(host, port):
    """Create a SocketHandler instance for logging setup."""
    return logging.handlers.SocketHandler(host, port)


class LogServer(TCPServer):
    """TCP logging server for SocketHandler."""

    logger_name = 'root'
    stream = None

    def __init__(self, *args, **kwargs):
        """Override just to set our logger."""
        super(LogServer, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.logger_name)

    def handle_stream(self, stream, address):
        """Required handle_stream override."""
        self.logger.info("Incoming connection from {}".format(address))
        self.stream = stream
        self.read()

    def read(self):
        """Initiate read from start of log record."""
        self.logger.debug("Read initiated on log record.")
        self.stream.read_bytes(4, callback=self.set_data_size)

    def set_data_size(self, data):
        """Set the log record size by reading the first 4 bytes."""
        slen = struct.unpack('>L', data)[0]
        self.logger.debug("set_data_size: slen is {} bytes.".format(slen))
        self.stream.read_bytes(slen, callback=self.read_log_msg)

    def read_log_msg(self, data):
        """Read, unpack, and handle the log record."""
        obj = pickle.loads(data)
        record = logging.makeLogRecord(obj)
        name = self.logger_name
        logger = logging.getLogger(name)
        logger.handle(record)
        self.read()

