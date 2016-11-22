#!/usr/bin/env python
# -*- coding: utf8 -*-
import gevent
from multiprocessing import Event
from multiprocessing import Process

from .base import Actor, BaseActor, AF_GREENLET, AF_PROCESS
from .inbox import DequeInbox, ProcessInbox


class GreenletActor(Actor):
    ''' Greenlet Actor
    '''

    def __init__(self, name=None, logger=None):
        ''' __init__
        '''
        super(GreenletActor, self).__init__(name=name, logger=logger)

        # inbox
        self.inbox = DequeInbox()

        # Actor Family
        self._family = AF_GREENLET

    def sleep(self, timeout=0):
        ''' actor sleep for timeout
        '''
        gevent.sleep(timeout)

    def start(self):
        ''' start actor
        '''
        super(GreenletActor, self).start()
        if len(self.children) > 0:
            self.supervise_loop = self.supervise()
        else:
            self.processing_loop = gevent.spawn(self.loop)

    def stop(self):
        ''' stop actor
        '''
        super(GreenletActor, self).stop()

    def run_once(self):
        ''' one actor iteraction (processing + supervising)
        '''
        self.sleep()

        # processing
        if self.processing_loop is not None:
            if self.processing_loop.ready():
                self.processing_loop = None

        # children supervising
        if self.supervise_loop is not None:
            try:
                self.supervise_loop.next()
            except StopIteration:
                self.supervise_loop = None

        if self.processing_loop is not None or self.supervise_loop is not None:
            return True
        else:
            self.stop()
            return False

    def run(self):
        ''' run actor
        '''
        while self.processing:
            try:
                if not self.run_once():
                    break
            except Exception as err:
                self._logger.error(err)
                break


class ForkedGreenletActor(GreenletActor):
    ''' Forked GreenletActor
    '''

    def __init__(self, name=None, logger=None):
        ''' __init__
        '''
        super(ForkedGreenletActor, self).__init__(name=name, logger=logger)

        # Actor Family
        self._family = AF_PROCESS
        self._subfamily = AF_GREENLET

        self.inbox = ProcessInbox()

        self._processing = Event()
        self._waiting = Event()

        self._process = Process(name=self._name, target=self.run)
        self._process.daemon = False

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
        super(ForkedGreenletActor, self).start()
        self._process.start()


class BaseGreenletActor(GreenletActor, BaseActor):
    pass


class BaseForkedGreenletActor(ForkedGreenletActor, BaseActor):
    pass
