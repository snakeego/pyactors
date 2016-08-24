#!/usr/bin/env python
# -*- coding: utf8 -*-


class EmptyInboxException(Exception):
    ''' The exception is raised when actor's inbox is empty '''
    pass


class QueueConnectionError(Exception):
    ''' The exception is raised when used external queue service
        and actor can't connect to queue server
    '''
    pass
