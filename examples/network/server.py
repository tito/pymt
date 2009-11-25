import os
os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt.logger import pymt_logger
import threading
import socket
import struct
import time

class SerializationServer(threading.Thread):
    def __init__(self, host='127.0.0.1', port=12000):
        super(SerializationServer, self).__init__()
        self.host = host
        self.port = port
        self.isRunning = True

    def run(self):
        self.haveSocket = self.isRunning = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name in ('posix', 'mac') and hasattr(socket, 'SO_REUSEADDR'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while not self.haveSocket and self.isRunning:
            try:
                self.socket.bind((self.host, self.port))
                self.socket.settimeout(0.5)
                self.haveSocket = True
                pymt_logger.notice('Listen on %s:%d' % (self.host, self.post))
            except socket.error, e:
                error, message = e.args

                # special handle for EADDRINUSE
                if error == errno.EADDRINUSE:
                    pymt_logger.error('Address %s:%i already in use, retry in 2 second' % (self.ipAddr, self.port))
                else:
                    pymt_logger.exception(e)
                self.haveSocket = False

                time.sleep(2)

            while self.isRunning:
                try:
                    header = self.socket.recv(8)
                    print header
                except Exception, e:
                    if type(e) == socket.timeout:
                        continue
                    pymt_logger.error('Error in SerializationServer recv()')
                    pymt_logger.exception(e)

if __name__ == '__main__':
    s = SerializationServer()
    s.start()
    while True:
        time.sleep(1)
