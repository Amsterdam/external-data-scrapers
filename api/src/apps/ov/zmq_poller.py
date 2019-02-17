import logging

import zmq

from apps.ov.zmq_subscriber import ZmqSubscriber

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
DEFAULT_ZMQ_TIMEOUT = 5 * 1000 * 60


class ZmqPoller(object):
    def __init__(self):
        self.poller = zmq.Poller()
        self.sockets = {}

    def __delf__(self):
        pass

    def register(self, subscriber: ZmqSubscriber):
        if subscriber not in self.sockets:
            self.sockets[subscriber.socket] = subscriber
            self.poller.register(subscriber.socket, zmq.POLLIN)

    def unregister(self, subscriber: ZmqSubscriber):
        if subscriber.socket in self.sockets:
            self.poller.unregister(subscriber.socket)
            del self.sockets[subscriber.socket]

    def poll(self):
        log.info('About to poll')
        polled_sockets = self.poller.poll(DEFAULT_ZMQ_TIMEOUT)
        for sock, event in polled_sockets:
            log.info(f'Processing socket {sock} {event}')
            if event == zmq.POLLIN:
                log.info(f'yielding {self.sockets[sock]}')
                yield self.sockets[sock]
            else:
                # socket timed out
                self.sockets[sock].reconnect()
