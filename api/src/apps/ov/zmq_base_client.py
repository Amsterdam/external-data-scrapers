# pylint:disable=E1101
# pylint: disable=unbalanced-tuple-unpacking
import logging
import time
from datetime import datetime, timedelta

from django.db import connection

from apps.ov.zmq_poller import ZmqPoller

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
TIMEOUTMS = 60


class ZmqBaseClient(object):
    def __init__(self, publisher=None):
        self.stop = False
        self.publisher = publisher
        self.poller = ZmqPoller()
        # Add additional subscribers to the list
        self.subscribers = []
        self.next_refresh = None

    def subscribe(self):
        try:
            for sub in self.subscribers:
                sub.connect()
                self.poller.register(sub)
            return True
        except Exception as err:
            log.error(err)
            return False

    def check_refresh(self):
        if self.next_refresh is None or self.next_refresh <= datetime.now():
            for sub in self.subscribers:
                sub.handle_refreshdata()
            self.next_refresh = datetime.now() + timedelta(days=1)

    def message_loop(self):
        while True:
            try:
                self.check_refresh()
                if self.stop:
                    # we need to close the connection within the
                    # thread, else it will be kept alive
                    connection.close()
                    log.info('Stop: Terminating message loop')
                    break
                for subscr in self.poller.poll():
                    subscr.handle_message()
            except Exception as err:
                log.error(err)

    def subscribe_and_process(self):
        while True:
            if self.subscribe():
                self.message_loop()
                log.info('Timed out, trying to reconnect...')
            else:
                log.info(f'Connection failed, sleeping {0.5 * TIMEOUTMS} (ms)')
            if self.stop:
                connection.close()
                log.info('Stop: Terminating pubsub')
                break
            time.sleep(0.5 * TIMEOUTMS)
