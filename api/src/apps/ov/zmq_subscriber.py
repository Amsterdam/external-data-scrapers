import abc
import logging

import zmq

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


class ZmqSubscriber(object):
    def __init__(self, url):
        self.url = url
        self.context = zmq.Context()
        self.sock = None

    def __del__(self):
        if self.sock is not None:
            self.sock.close()
        if self.context is not None:
            self.context.term()

    @property
    def socket(self):
        return self.sock

    def connect(self):
        self.sock = self.context.socket(zmq.SUB)
        log.info(f'Subscribing to {self.url}')
        self.sock.connect(self.url)
        self.sock.setsockopt_string(zmq.SUBSCRIBE, "")

    def reconnect(self):
        log.info(f'Reconnecting to {self.url}')
        if self.sock is not None:
            self.sock.close()
        self.connect()

    @abc.abstractclassmethod
    def handle_message(self):
        pass
