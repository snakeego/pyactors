#!/usr/bin/env python
# -*- coding: utf8 -*-
import Queue
import logging
import collections
import multiprocessing

from .exceptions import EmptyInboxException

__all__ = ['DequeInbox', 'QueueInbox', 'ProcessInbox']


class DequeInbox(object):
    ''' Inbox from collections.deque
    '''
    def __init__(self, logger=None):
        ''' __init__
        '''
        self.__inbox = collections.deque()
        if logger is None:
            self._logger = logging.getLogger('%s.DequeInbox' % __name__)
        else:
            self._logger = logger

    def get(self):
        ''' get data from inbox
        '''
        try:
            result = self.__inbox.popleft()
        except IndexError:
            raise EmptyInboxException
        return result

    def put(self, message):
        ''' put message to inbox
        '''
        self.__inbox.append(message)

    def __len__(self):
        ''' return length of inbox
        '''
        return len(self.__inbox)


class QueueInbox(object):
    ''' Inbox from Queue.Queue
    '''
    def __init__(self, logger=None):
        ''' __init__
        '''
        self.__inbox = Queue.Queue()

        if logger is None:
            self._logger = logging.getLogger('%s.QueueInbox' % __name__)
        else:
            self._logger = logger

    def get(self):
        ''' get data from inbox
        '''
        try:
            result = self.__inbox.get_nowait()
            self.__inbox.task_done()
        except Queue.Empty:
            raise EmptyInboxException
        return result

    def put(self, message):
        ''' put message to inbox
        '''
        self.__inbox.append(message)

    def __len__(self):
        ''' return length of inbox
        '''
        return len(self.__inbox)


class ProcessInbox(object):
    ''' Inbox from multiprocessing.Queue
    '''
    def __init__(self, logger=None):
        ''' __init__
        '''
        self.__inbox = multiprocessing.Queue()

        if logger is None:
            self._logger = logging.getLogger('%s.ProcessInbox' % __name__)
        else:
            self._logger = logger

    def get(self):
        ''' get data from inbox
        '''
        try:
            result = self.__inbox.get_nowait()
        except Queue.Empty:
            raise EmptyInboxException
        return result

    def put(self, message):
        ''' put message to inbox
        '''
        self.__inbox.put_nowait(message)

    def __len__(self):
        ''' return length of inbox
        '''
        return self.__inbox.qsize()
