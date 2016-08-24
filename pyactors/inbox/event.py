from logging import getLogger
from eventlet.queue import Queue as EventletQueue
from eventlet.queue import Empty as EventletEmpty

from .exceptions import EmptyInboxException


class EventletInbox(object):
    def __init__(self, logger=None):
        ''' __init__ '''

        self.__inbox = EventletQueue()

        if logger is None:
            self._logger = getLogger('%s.EventletInbox' % __name__)
        else:
            self._logger = logger

    def get(self):
        ''' get data from inbox '''
        try:
            result = self.__inbox.get_nowait()
        except EventletEmpty:
            raise EmptyInboxException
        return result

    def put(self, message):
        ''' put message to inbox '''

        self.__inbox.put(message)

    def __len__(self):
        ''' return length of inbox '''

        return self.__inbox.qsize()
