#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging
import logging.handlers


def file_logger(name, filename):
    ''' returns file logger
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(filename)
    logger.addHandler(file_handler)
    formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    return logger


def network_logger(name=__name__, level=logging.DEBUG,
                   host='127.0.0.1', port=logging.handlers.DEFAULT_TCP_LOGGING_PORT):
    ''' return network logger
    '''
    logger = logging.getLogger(name)
    logger.setLevel(level)
    socketHandler = logging.handlers.SocketHandler(host, port)
    formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
    socketHandler.setFormatter(formatter)
    logger.addHandler(socketHandler)
    return logger
