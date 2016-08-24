#!/usr/bin/env python
# -*- coding: utf8 -*-
import uuid
import logging

from .exceptions import EmptyInboxException

# Actor Family
AF_GENERATOR = 0
AF_GREENLET = 1
AF_THREAD = 2
AF_PROCESS = 3


class Actor(object):
    ''' Base class for creation actors '''

    def __init__(self, name=None, logger=None):
        self.logger = logger if logger else logging.getLogger('%s.Actor' % __name__)

        self._name = name if name else self.__class__.__name__
        self._family = None
        self.address = uuid.uuid4().hex
        self.parent = None
        self.inbox = None
        self._children = dict()
        self._waiting = False
        self._processing = False
        self.processing_loop = None
        self.supervise_loop = None

    def __str__(self):
        ''' represent actor as string '''
        return u'{}[{}]'.format(self._name, self.address)

    @property
    def name(self):
        ''' property get actor name '''
        return self._name

    @property
    def family(self):
        ''' propery get actor family '''
        if self._family is None:
            raise RuntimeError('Actor family is not specified, {}'.format(self._name))
        return self._family

    @property
    def waiting(self):
        ''' propery get waiting for new messages '''
        return self._waiting

    @waiting.setter
    def waiting(self, value):
        ''' propery set waiting for new messages '''
        if isinstance(value, bool):
            self._waiting = value
        else:
            raise RuntimeError('Incorrect waiting type, {}. It must be boolean'.format(type(value)))

    @property
    def processing(self):
        ''' property get actor porcessing status '''
        return self._processing

    @processing.setter
    def processing(self, value):
        ''' property set actor porcessing status '''
        if isinstance(value, bool):
            self._processing = value
        else:
            raise RuntimeError('Incorrect processing type, {}. It must be boolean'.format(type(value)))

    def add_child(self, actor):
        ''' add actor's child '''
        if actor not in self.children:
            actor.parent = self
            self._children[actor.address] = actor
        else:
            raise RuntimeError('Actor exists: %s', actor)

    def remove_child(self, address):
        ''' remove child by its address '''
        if address in self._children.keys():
            self._children.pop(address)
        else:
            raise RuntimeError('Actor does not exist, address: %s', address)

    @property
    def children(self):
        ''' return list of actor's children '''
        return self._children.values()

    def find(self, address=None, actor_class=None, actor_name=None):
        """ find children by criterias

        - if no criterias are defined, return all children addresses

        - if `address` is defined as string or unicode, return an actor by its address.
        - if `address` is defined as list or tuple, return actors by thier addresses.

        - if actor_class is defined as string or unicode, return the list of all
        existing actors of the given class, or of any subclass of the given class.
        - if actor_class is defined as list or tuple, return actors by thier actor classes.

        - if actor_name is defined, return the list of all existing actors of
        the given name.

        return existing actors by criterias.
        """
        known_actors = list()
        known_actors.extend(self.children)
        if self.parent:
            known_actors.append(self.parent)
            known_actors.extend(self.parent.find(address, actor_class, actor_name))
        known_actors = list(set(known_actors))
        result = list()

        if address:
            # when address is only one
            if isinstance(address, (str, unicode)):
                result.extend([actor for actor in known_actors if actor.address == address])
            # when address if multiple
            elif isinstance(address, (list, tuple)):
                result.extend([actor for actor in known_actors if actor.address in address])
            return result

        if actor_class:
            result.extend([actor for actor in known_actors if isinstance(actor, actor_class)])
            return result

        if actor_name:
            result.extend([actor for actor in known_actors if actor._name == actor_name])
            return result

        return known_actors

    def start(self):
        ''' start actor
        '''
        self.waiting = False
        self.processing = True

        if len(self.children) > 0:
            # start child-actors
            for child in self.children:
                child.start()

    def _stop_children(self):
        ''' stop children
        '''
        if len(self.children) == 0:
            return
        # stop child-actors
        while True:
            stopped_children = 0
            for child in self.children:
                if child.processing:
                    child.stop()
                else:
                    stopped_children += 1
            if stopped_children == len(self.children):
                break

    def stop(self):
        ''' stop actor and its children
        '''
        self._stop_children()
        self.processing = False
        self.waiting = False

    def run(self):
        ''' run actor
        '''
        raise RuntimeError('Actor.run() is not implemented')

    def run_once(self):
        ''' run actor for one iteraction (used by GeneratorActor and GreenletActor)
        '''
        raise RuntimeError('Actor.run_once() is not implemented')

    def send(self, message):
        ''' send message to actor
        '''
        self.inbox.put(message)

    def loop(self):
        ''' main loop
        '''
        raise RuntimeError('Actor.loop() is not implemented')

    def supervise(self):
        ''' supervise loop
        '''
        self.logger.debug('supervise started')
        while self.processing:
            stopped_children = 0
            for child in self.children:
                # child.processing is just a flag which give you information
                # that the actor should be stopped but it's not a fact
                # that the actor was stopped.
                if child.processing:
                    if child.family in (AF_GENERATOR, AF_GREENLET):
                        try:
                            child.run_once()
                        except Exception, err:
                            self._logger.error(err)
                else:
                    stopped_children += 1
                yield

            if len(self.children) == stopped_children:
                break
        self.logger.debug('supervise stopped')


class ActorSystem(Actor):
    ''' Actor System '''
    pass


class BaseActor(Actor):
    message = None
    steps = list()

    def __init__(self, **kwargs):
        self.allow_parent = kwargs.pop('allow_parent', getattr(self, 'allow_parent', False))
        super(BaseActor, self).__init__(name=kwargs.get('name'), logger=kwargs.get('logger'))

    def loop(self):
        self.logger.debug("{0} --- Call loop.".format(self))

        while self.processing:
            self.logger.debug("{0} --- Execute loop. Inbox: {1}".format(self, len(self.inbox)))

            try:
                self.message = self.inbox.get()
            except EmptyInboxException:
                if self.is_waiting_message:
                    self.sleep()
                    break

            self.recieve()

            if self.validate():
                self.process()
        self.end()

    def send(self, **message):
        overwrite = message.pop('overwrite') if isinstance(message.get('overwrite'), bool) else False
        allow_parent = message.pop('allow_parent') if isinstance(message.get('allow_parent'), bool) else False
        message = dict() if not isinstance(message, dict) else message

        if self.message and not overwrite:
            data = self.message.copy()
            data.update(message)
        else:
            data = message

        if self.steps:
            steps = self.steps[:]
            next_class = steps.pop(0)
            data['steps'] = steps

            actors = self.find(actor_class=next_class)
            if not actors:
                error_message = dict(message=u"Coudn't find next target in system: {0}".format(next_class))
                error_message.update(dict(sid=data.get('ssid'))) if 'ssid' in data else None
                error_message.update(dict(sid=data.get('mid'))) if 'mid' in data else None
                self.error(**error_message)

            for actor in actors:
                self.logger.debug("<{0}> - Send Message: {{{1}}} To: {2}".format(self, data.keys(), actor))
                actor.inbox.put(data)
                actor.start()
        elif self.parent and (allow_parent or self.allow_parent):
            self.parent.send(data)
        else:
            self.logger.debug(u"<{0}> - Send To Next: {1}".format(self, data))

        self.sleep()

    def error(self, message=None, **kwargs):
        self.logger.error(u"<{0}> - Got Error: {1}".format(self, message))
        allow_parent = kwargs.pop('allow_parent') if isinstance(kwargs.get('allow_parent'), bool) else False

        if (allow_parent or self.allow_parent):
            out = {'result': False, 'error': message}

            if self.message and self.message.get('ssid', None):
                out.update(dict(ssid=self.message.get('ssid')))

            if self.message and self.message.get('mid', None):
                out.update(dict(mid=self.message.get('mid')))
            out.update(kwargs)

            self.parent.send(out)
        self.stop()

    def sleep(self, timeout=None):
        if self._family == AF_GENERATOR:
            yield
        else:
            self._sleep(timeout)

    def _sleep(self, timeout=None):
        timeout = timeout if timeout else 0.01
        return super(BaseActor, self).sleep(timeout)

    def recieve(self):
        if self.message:
            source_steps = self.message.get('steps', None)
            if source_steps:
                self.steps = source_steps

        return self.after_recieve()

    def after_recieve(self):
        """ Override """
        pass

    def validate(self):
        """ Override """
        return True

    def process(self):
        """ Override """
        pass

    def end(self):
        """ Override """
        self.logger.debug("{0} --- Stop loop".format(self))
        self.steps = list()
        self.message = None
        if len(self.inbox) > 0:
            self.sleep()
        else:
            self.stop()

    @property
    def is_waiting_message(self):
        """ Override """
        return True

    def __str__(self):
        old = super(BaseActor, self).__str__()
        return "{0}".format(old)
