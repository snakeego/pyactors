#!/usr/bin/env python
# -*- coding: utf8 -*-
from multiprocessing import Event
from multiprocessing import Process

from .base import Actor, BaseActor, AF_GENERATOR, AF_PROCESS
from .inbox import DequeInbox, ProcessInbox


class GeneratorActor(Actor):
    ''' Generator Actor
    '''

    def __init__(self, name=None, logger=None):
        ''' __init__
        '''
        super(GeneratorActor, self).__init__(name=name, logger=logger)
        self.inbox = DequeInbox()
        self._family = AF_GENERATOR

    def start(self):
        ''' start actor
        '''
        super(GeneratorActor, self).start()
        if len(self.children) > 0:
            self.supervise_loop = self.supervise()
        else:
            self.processing_loop = self.loop()

    def run_once(self):
        ''' one actor iteraction (processing + supervising)
        '''
        # processing
        if self.processing_loop:
            try:
                self.processing_loop.next()
            except StopIteration:
                self.processing_loop = None

        # children supervising
        if self.supervise_loop:
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
                self.logger.error(err)
                break


class ForkedGeneratorActor(GeneratorActor):
    ''' Forked GeneratorActor
    '''

    def __init__(self, name=None, logger=None):
        ''' __init__
        '''
        super(ForkedGeneratorActor, self).__init__(name=name, logger=logger)

        # Actor Family
        self._family = AF_PROCESS
        self._subfamily = AF_GENERATOR

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
        super(ForkedGeneratorActor, self).start()
        self._process.start()


class BaseGeneratorActor(GeneratorActor, BaseActor):
    pass


class BaseForkedGeneratorActor(ForkedGeneratorActor, BaseActor):
    pass
