#!/usr/bin/env python
# -*- coding: utf8 -*-
import threading

from .base import BaseActor, AF_THREAD
from .generator import GeneratorActor


class ThreadedGeneratorActor(GeneratorActor):
    ''' Threaded GeneratorActor
    '''

    def __init__(self, name=None, logger=None):
        ''' __init__
        '''
        super(ThreadedGeneratorActor, self).__init__(name=name, logger=logger)

        # Actor Family
        self._family = AF_THREAD

        self._processing = threading.Event()
        self._waiting = threading.Event()

        self._thread = threading.Thread(name=self._name, target=self.run)
        self._thread.daemon = True

    @property
    def processing(self):
        ''' return True if actor is processing
        '''
        if self._processing.is_set():
            return True
        return False

    @processing.setter
    def processing(self, value):
        ''' set processing status
        '''
        if not isinstance(value, bool):
            raise RuntimeError('Incorrect processing type, %s. It must be boolean' % value)
        if value:
            self._processing.set()
        else:
            self._processing.clear()

    @property
    def waiting(self):
        ''' return True if actor is waiting for new messages
        '''
        if self._waiting.is_set():
            return True
        return False

    @waiting.setter
    def waiting(self, value):
        ''' set waiting status
        '''
        if not isinstance(value, bool):
            raise RuntimeError('Incorrect waiting type, %s. It must be boolean' % value)
        if value:
            self._waiting.set()
        else:
            self._waiting.clear()

    def start(self):
        ''' start actor
        '''
        super(ThreadedGeneratorActor, self).start()

        self._thread.start()


class BaseThreadedGeneratorActor(ThreadedGeneratorActor, BaseActor):
    pass
