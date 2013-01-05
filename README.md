pyactors
========

Simple implementation actors on python

## The actor model

An actor has the following characteristics:

 * It does not share state with anybody else.
 * It can have its own state.
 * It can only communicate with other actors by sending and receiving messages.
 * It can only send messages to actors whose address it has.
 * When an actor receives a message it may take actions like:
    - altering its own state, e.g. so that it can react differently to a future message,
    - sending messages to other actors, or
    - starting new actors.
 * None of the actions are required, and they may be applied in any order.
 * It only processes one message at a time. In other words, a single actor does not give you any concurrency, and it does not need to use e.g. locks to protect its own state.

## Documentation

- [Introduction](http://https://github.com/ownport/pyactors/tree/master/docs/introduction.md)
- [PyActors API](http://https://github.com/ownport/pyactors/tree/master/docs/api.md)
- [For developers](http://https://github.com/ownport/pyactors/tree/master/docs/development.md)

## Similar projects

- [Pykka](http://pykka.readthedocs.org/en/latest/) is easy to use concurrency for Python using the actor model

