#!/usr/bin/env python
# -*- coding: utf8 -*-
from redis import StrictRedis
from logging import getLogger

try:
    from ujson import loads, dumps
except ImportError:
    from json import loads, dumps

from .exceptions import EmptyInboxException, QueueConnectionError

__all__ = ['RedisInbox']


class RedisQueue(object):
    _cli = None
    _connection_parameters = dict()
    _queue = None

    logger = getLogger()

    def __init__(self, **kwargs):
        self._queue = kwargs.pop('queue', None)
        self._connection_parameters.update(kwargs)

    def connect(self, **kwargs):
        if self._cli and not kwargs:
            return self

        self._queue = kwargs.pop('queue') if kwargs.get('queue') else self._queue
        self._connection_parameters.update(kwargs)

        if not self._connection_parameters:
            raise QueueConnectionError

        self._cli = StrictRedis(**self._connection_parameters)
        return self

    def put(self, message, **kwargs):
        self.connect() if not self._cli else None
        queue = kwargs.pop('queue') if kwargs.get('queue') else self._queue
        publisher = kwargs.pop('publisher') if kwargs.get('publisher') else 'default'

        pipe = self._cli.pipeline()
        return pipe.lpush(queue, dumps(message)).publish(publisher, queue).execute()

    def get(self, **kwargs):
        self.connect() if not self._cli else None
        queue = kwargs.pop('queue') if kwargs.get('queue') else self._queue
        timeout = kwargs.pop('timeout') if isinstance(kwargs.get('timeout'), int) else 1

        try:
            return loads(self._cli.brpop(queue, timeout)[1])
        except TypeError:
            return None
        except ValueError:
            return None

    def length(self, queue=None):
        self.connect() if not self._cli else None
        queue = queue if queue else self._queue

        return self._cli.llen('{0}'.format(queue))

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value

    @queue.deleter
    def queue(self):
        self._queue = None


class RedisInbox(object):
    _channel = None

    _get_queue = None
    _put_queue = None

    def __init__(self, logger=None, get_queue=None, put_queue=None, **conn):
        self.get_queue = get_queue if get_queue is not None else self.get_queue
        self.put_queue = put_queue if put_queue is not None else self.put_queue

        self._channel = RedisQueue(**conn)

    def get(self):
        return self.get_from(self.get_queue)

    def get_from(self, queue):
        out = self._channel.get(queue=queue)
        if out is None:
            raise EmptyInboxException

        return out

    def put(self, message):
        return self.put_in(self.put_queue)

    def put_in(self, message, queue):
        return self._channel.put(message, queue=queue)

    def __len__(self):
        return self.total(self._get_queue)

    def total(self, queue):
        return self._channel.length(queue=queue)

    @property
    def get_queue(self):
        if self._get_queue is None:
            raise AttributeError("You must set queue for getting messages")

        return self._get_queue

    @get_queue.setter
    def get_queue(self, value):
        if not isinstance(value, str):
            raise ValueError("You must queue must be string")
        self._get_queue = value

    @get_queue.deleter
    def get_queue(self):
        self._get_queue = None

    @property
    def put_queue(self):
        if self._put_queue is None:
            raise AttributeError("You must set queue for putting messages")

        return self._put_queue

    @put_queue.setter
    def put_queue(self, value):
        if not isinstance(value, str):
            raise ValueError("You must queue must be string")
        self._put_queue = value

    @put_queue.deleter
    def put_queue(self):
        self._put_queue = None
