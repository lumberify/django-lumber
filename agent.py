#!/usr/bin/env python
import pickle
import logging
import logging.handlers
import select
import socketserver
import struct
import sys
import os
import requests
import queue

from threading import Thread
from optparse import OptionParser

class Sender(Thread):
    def __init__(self, dsn, queue, timeout=5, threshold=100):
        Thread.__init__(self)
        self.dsn = dsn
        self.queue = queue
        self.pending = []
        self.timeout = timeout
        self.threshold = threshold

    def run(self):
        while True:
            try:
                record = self.queue.get(timeout=self.timeout)
                self.pending.append(record)
                if len(self.pending) > self.threshold:
                    self.flush()
            except queue.Empty:
                if len(self.pending) > 0:
                    self.flush()

    def flush(self):
        payload = {'records':[]}
        while len(self.pending) > 0:
            record = self.pending.pop(0)
            payload['records'].append({
                'args': record.args,
                'created': record.created,
                'exc_info': record.exc_info,
                'funcName': record.funcName,
                'level': record.levelno,
                'lineno': record.lineno,
                'message': record.message if hasattr(record, 'message') else None, # interpreted
                'msg': record.msg,
                'name': record.name,
                'pathname': record.pathname,
                'process': record.process,
                'processName': record.processName,
                'sinfo': record.stack_info,
                'thread': record.thread,
                'threadName': record.threadName,
            })
        self.pending = []
        if len(payload['records']) > 0:
            requests.post(self.dsn, json=payload)

class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)
        self.server.queue.put(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self,
                 host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler,
                 dsn=None):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.dsn = dsn
        self.queue = queue.Queue()
        self.sender = Sender(self.dsn, self.queue)
        self.sender.start()

    def serve_until_stopped(self):
        abort = 0
        while not abort:
            read, _, _ = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if read:
                self.handle_request()
            abort = self.abort


def main():
    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--host', action='store', type='str',
                      dest='host', help='Host to listen to', default='localhost')
    parser.add_option('-p', '--port', action='store', type='int', dest='port',
                      help='Port to listen to', default=logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    parser.add_option('-d', '--dsn', action='store', type='str',
                      dest='dsn', help="The Lumber's DSN to use for this instance")
    parser.add_option('-f', '--file', action='store', type='str', dest='filename',
                      help='Path to an optional file where to store log entries')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

    (options, args) = parser.parse_args()
    if not options.dsn:
        parser.error('DNS is required')

    short = logging.Formatter(
        '[%(relativeCreated)5d][%(name)-15s][%(levelname)-8s] %(message)s')
    long = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s][%(pathname)s:%(lineno)d] %(message)s')

    handlers = []
    if options.verbose:
        print('Logging to standart output')
        console = logging.StreamHandler()
        console.setFormatter(short)
        console.setLevel(logging.INFO)
        handlers.append(console)
    if options.filename:
        file = logging.FileHandler(filename=options.filename)
        file.setFormatter(long)
        file.setLevel(logging.DEBUG)
        handlers.append(file)

    logging.basicConfig(
        handlers=handlers,
    )
    tcpserver = LogRecordSocketReceiver(
        host=options.host,
        port=options.port,
        dsn=options.dsn,
    )
    print('Starting agent on {}:{} for DSN {}'.format(
        options.host, options.port, options.dsn))
    tcpserver.serve_until_stopped()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
