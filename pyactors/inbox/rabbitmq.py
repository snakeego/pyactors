#!/usr/bin/env python
# -*- coding: utf8 -*-
from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from logging import getLogger

try:
    from ujson import loads, dumps
except ImportError:
    from json import loads, dumps

from .exceptions import EmptyInboxException, QueueConnectionError

__all__ = ['RabbitMQInbox']


class RabbitMQQueue(object):
    _channel = None
    _connection_parameters = dict()

    def __init__(self, **kwargs):
        self._queue = kwargs.pop('queue', None)
        self._connection_parameters.update(kwargs)
        self.logger = getLogger(self.__class__.__name__)

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value

    @queue.deleter
    def queue(self):
        self._queue = None

    def connect(self, **kwargs):
        if self._channel and not kwargs:
            return self

        self._queue = kwargs.pop('queue') if kwargs.get('queue') else self._queue

        self._connection_parameters.update(kwargs)

        if not self._connection_parameters:
            raise QueueConnectionError

        connection_parameters = self._connection_parameters.copy()

        cred_args = tuple()
        if 'username' in connection_parameters:
            cred_args = cred_args + (connection_parameters.pop('username'),)
        if 'password' in connection_parameters:
            cred_args = cred_args + (connection_parameters.pop('password'),)

        credentials = PlainCredentials(*cred_args) if len(cred_args) == 2 else None
        cp = ConnectionParameters(credentials=credentials, **connection_parameters)
        connection = BlockingConnection(cp)
        self._channel = connection.channel()

        return self

    def put(self, body, queue=None, **kwargs):
        if not self._channel:
            self.connect()

        queue = self._queue if queue is None else queue
        if queue is None:
            raise QueueConnectionError("No 'queue' parameter specified")

        self._channel.queue_declare(queue)
        self.logger.debug(u"Put message [{0}] in '{1}' with kwargs: {2}".format(body, queue, kwargs))
        message = dict(exchange='', routing_key=queue, properties=BasicProperties(**kwargs.pop('properties', {})))
        message.update(kwargs)
        message['body'] = body
        message['routing_key'] = queue

        return self._channel.basic_publish(**message)

    def get(self, queue=None):
        if not self._channel:
            self.connect()

        queue = self._queue if queue is None else queue
        if queue is None:
            raise QueueConnectionError("No 'queue' parameter specified")

        self._channel.queue_declare(queue)
        method, poroperties, body = self._channel.basic_get(queue)
        if method:
            message = body
            self._channel.basic_ack(delivery_tag=method.delivery_tag)
            return message
        else:
            return None

    def length(self, queue=None):
        if not self._channel:
            self.connect()

        queue = self._queue if queue is None else queue
        if queue is None:
            raise QueueConnectionError("No 'queue' parameter specified")

        queue_attr = self._channel.queue_declare(self._queue, passive=True)
        return queue_attr.method.message_count


class RabbitMQInbox(object):
    _cli = None

    _get_queue = None
    _put_queue = None

    @property
    def get_queue(self):
        if self._get_queue is None:
            raise AttributeError("You must set queue for getting messages")

        return self._get_queue

    @get_queue.setter
    def get_queue(self, value):
        if type(value) not in str:
            raise ValueError("You must queue must be string")
        self._get_queue = value

    @get_queue.deleter
    def get_queue(self):
        self._get_queue = None

    @property
    def put_queue(self):
        if self._put_queue is None:
            raise AttributeError("You must set queue for getting messages")

        return self._put_queue

    @put_queue.setter
    def put_queue(self, value):
        if type(value) not in str:
            raise ValueError("You must queue must be string")
        self._put_queue = value

    @put_queue.deleter
    def put_queue(self):
        self._put_queue = None

    def __init__(self, logger=None, get_queue=None, put_queue=None, **conn):
        self.get_queue = get_queue if get_queue is not None else self.get_queue
        self.put_queue = put_queue if put_queue is not None else self.put_queue

        self._cli = RabbitMQQueue(**conn)

    def get(self):
        out = self._cli.get(self.get_queue)

        if out is None:
            raise EmptyInboxException

        return loads(out)

    def put(self, message):
        self._cli.put(dumps(message), self.put_queue)

    def __len__(self):
        return self._cli.length(self.get_queue)
