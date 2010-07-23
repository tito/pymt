'''Event: Event dispatch framework.

All objects that produce events in pyglet implement `EventDispatcher`,
providing a consistent interface for registering and manipulating event
handlers.  A commonly used event dispatcher is `pyglet.window.Window`.

Event types
===========

For each event dispatcher there is a set of events that it dispatches; these
correspond with the type of event handlers you can attach.  Event types are
identified by their name, for example, ''on_resize''.  If you are creating a
new class which implements `EventDispatcher`, you must call
`EventDispatcher.register_event_type` for each event type.

Attaching event handlers
========================

An event handler is simply a function or method.  You can attach an event
handler by setting the appropriate function on the instance::

    def on_resize(width, height):
        # ...
    dispatcher.on_resize = on_resize

There is also a convenience decorator that reduces typing::

    @dispatcher.event
    def on_resize(width, height):
        # ...

You may prefer to subclass and override the event handlers instead::

    class MyDispatcher(DispatcherClass):
        def on_resize(self, width, height):
            # ...

Event handler stack
===================

When attaching an event handler to a dispatcher using the above methods, it
replaces any existing handler (causing the original handler to no longer be
called).  Each dispatcher maintains a stack of event handlers, allowing you to
insert an event handler "above" the existing one rather than replacing it.

There are two main use cases for "pushing" event handlers:

* Temporarily intercepting the events coming from the dispatcher by pushing a
  custom set of handlers onto the dispatcher, then later "popping" them all
  off at once.
* Creating "chains" of event handlers, where the event propogates from the
  top-most (most recently added) handler to the bottom, until a handler
  takes care of it.

Use `EventDispatcher.push_handlers` to create a new level in the stack and
attach handlers to it.  You can push several handlers at once::

    dispatcher.push_handlers(on_resize, on_key_press)

If your function handlers have different names to the events they handle, use
keyword arguments::

    dispatcher.push_handlers(on_resize=my_resize,
                             on_key_press=my_key_press)

After an event handler has processed an event, it is passed on to the
next-lowest event handler, unless the handler returns `EVENT_HANDLED`, which
prevents further propogation.

To remove all handlers on the top stack level, use
`EventDispatcher.pop_handlers`.

Note that any handlers pushed onto the stack have precedence over the
handlers set directly on the instance (for example, using the methods
described in the previous section), regardless of when they were set.
For example, handler ``foo`` is called before handler ``bar`` in the following
example::

    dispatcher.push_handlers(on_resize=foo)
    dispatcher.on_resize = bar

Dispatching events
==================

pyglet uses a single-threaded model for all application code.  Event
handlers are only ever invoked as a result of calling
EventDispatcher.dispatch_events`.

It is up to the specific event dispatcher to queue relevant events until they
can be dispatched, at which point the handlers are called in the order the
events were originally generated.

This implies that your application runs with a main loop that continously
updates the application state and checks for new events::

    while True:
        dispatcher.dispatch_events()
        # ... additional per-frame processing

Not all event dispatchers require the call to ``dispatch_events``; check with
the particular class documentation.

'''
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
#
# Note: this class is not comming from pyglet, but heavily copy/pasted
# handlers management at start of coding.
# Lot of kudos to Alex Holkner !
#

__all__ = ('EventDispatcher', )

import inspect
import types
from weakmethod import WeakMethod
from baseobject import BaseObject
from logger import pymt_logger

class EventDispatcher(BaseObject):
    '''Generic event dispatcher interface.

    See the module docstring for usage.
    '''

    __slots__ = ('_event_types', '_event_stack')

    def __init__(self, **kwargs):
        super(EventDispatcher, self).__init__(**kwargs)
        self._event_types = []
        self._event_stack = None

    @property
    def event_types(self):
        return self._event_types

    def unregister_event_type(self, event_type):
        if event_type in self._event_types:
            self._event_types.remove(event_type)

    def register_event_type(self, event_type):
        '''Register an event type with the dispatcher.

        Registering event types allows the dispatcher to validate event
        handler names as they are attached, and to search attached objects for
        suitable handlers.

        :Parameters:
            `name` : str
                Name of the event to register.

        '''
        if not hasattr(self, event_type):
            raise Exception('Missing default handler <%s> in <%s>' % (
                            event_type, self.__class__.__name__))
        if not event_type in self._event_types:
            self._event_types.append(event_type)

    def push_handlers(self, *args, **kwargs):
        '''Push a level onto the top of the handler stack, then attach zero or
        more event handlers.

        If keyword arguments are given, they name the event type to attach.
        Otherwise, a callable's `__name__` attribute will be used.  Any other
        object may also be specified, in which case it will be searched for
        callables with event names.
        '''
        # Create event stack if necessary
        if self._event_stack is None:
            self._event_stack = []

        # Place dict full of new handlers at beginning of stack
        self._event_stack.insert(0, {})
        self.set_handlers(*args, **kwargs)

    def remove_handler(self, name, handler):
        '''Remove a single event handler.

        The given event handler is removed from the first handler stack frame
        it appears in.  The handler must be the exact same callable as passed
        to `set_handler`, `set_handlers` or `push_handlers`; and the name
        must match the event type it is bound to.

        No error is raised if the event handler is not set.

        :Parameters:
            `name` : str
                Name of the event type to remove.
            `handler` : callable
                Event handler to remove.
        '''
        if self._event_stack is None:
            return
        for frame in self._event_stack:
            try:
                if frame[name]() == handler:
                    del frame[name]
                    break
            except KeyError:
                pass

    def remove_handlers(self, *args, **kwargs):
        '''Remove event handlers from the event stack.

        See `push_handlers` for the accepted argument types.  All handlers
        are removed from the first stack frame that contains any of the given
        handlers.  No error is raised if any handler does not appear in that
        frame, or if no stack frame contains any of the given handlers.

        If the stack frame is empty after removing the handlers, it is
        removed from the stack.  Note that this interferes with the expected
        symmetry of `push_handlers` and `pop_handlers`.
        '''
        handlers = list(self._get_handlers(args, kwargs))

        # Find the first stack frame containing any of the handlers
        def find_frame():
            if self._event_stack is None:
                return
            for frame in self._event_stack:
                for name, handler in handlers:
                    try:
                        if frame[name]() == handler:
                            return frame
                    except KeyError:
                        pass
        frame = find_frame()

        # No frame matched; no error.
        if not frame:
            return

        # Remove each handler from the frame.
        for name, handler in handlers:
            try:
                if frame[name]() == handler:
                    del frame[name]
            except KeyError:
                pass

    def _get_handlers(self, args, kwargs):
        '''Implement handler matching on arguments for set_handlers and
        remove_handlers.
        '''
        for object in args:
            if inspect.isroutine(object):
                # Single magically named function
                name = object.__name__
                if name not in self._event_types:
                    raise Exception('Unknown event "%s"' % name)
                yield name, object
            else:
                # Single instance with magically named methods
                for name in dir(object):
                    if name in self._event_types:
                        yield name, getattr(object, name)
        for name, handler in kwargs.iteritems():
            # Function for handling given event (no magic)
            if name not in self._event_types:
                raise Exception('Unknown event "%s"' % name)
            yield name, handler

    def set_handlers(self, *args, **kwargs):
        '''Attach one or more event handlers to the top level of the handler
        stack.

        See `push_handlers` for the accepted argument types.
        '''
        # Create event stack if necessary
        if self._event_stack is None:
            self._event_stack = [{}]

        for name, handler in self._get_handlers(args, kwargs):
            self.set_handler(name, handler)

    def set_handler(self, name, handler):
        '''Attach a single event handler.

        :Parameters:
            `name` : str
                Name of the event type to attach to.
            `handler` : callable
                Event handler to attach.

        '''
        # Create event stack if necessary
        if self._event_stack is None:
            self._event_stack = [{}]

        self._event_stack[0][name] = WeakMethod(handler)

    def dispatch_event(self, event_type, *args):
        '''Dispatch a single event to the attached handlers.

        The event is propogated to all handlers from from the top of the stack
        until one returns `EVENT_HANDLED`.  This method should be used only by
        `EventDispatcher` implementors; applications should call
        the ``dispatch_events`` method.

        :Parameters:
            `event_type` : str
                Name of the event.
            `args` : sequence
                Arguments to pass to the event handler.

        '''
        # unknown event type
        if event_type not in self._event_types:
            return

        # search handler stack for matching event handlers
        _event_stack = self._event_stack
        if _event_stack is not None:
            for frame in _event_stack:
                wkhandler = frame.get(event_type, None)
                if wkhandler is None:
                    continue
                handler = wkhandler()
                if handler is None:
                    frame.remove(wkhandler)
                    continue
                try:
                    if handler(*args):
                        return True
                except TypeError:
                    self._raise_dispatch_exception(event_type, args, handler)

        # a instance always have a event handler, don't check it with hasattr.
        try:
            # call event
            if getattr(self, event_type)(*args):
                return True
        except TypeError, e:
            self._raise_dispatch_exception(
                event_type, args, getattr(self, event_type))

    def _raise_dispatch_exception(self, event_type, args, handler):
        # A common problem in applications is having the wrong number of
        # arguments in an event handler.  This is caught as a TypeError in
        # dispatch_event but the error message is obfuscated.
        #
        # Here we check if there is indeed a mismatch in argument count,
        # and construct a more useful exception message if so.  If this method
        # doesn't find a problem with the number of arguments, the error
        # is re-raised as if we weren't here.

        if not hasattr(handler, 'im_func'):
            raise
        if not isinstance(handler.im_func, types.FunctionType):
            raise

        n_args = len(args)

        # Inspect the handler
        handler_args, handler_varargs, _, handler_defaults = \
            inspect.getargspec(handler)
        n_handler_args = len(handler_args)

        # Remove "self" arg from handler if it's a bound method
        if inspect.ismethod(handler) and handler.im_self:
            n_handler_args -= 1

        # Allow *args varargs to overspecify arguments
        if handler_varargs:
            n_handler_args = max(n_handler_args, n_args)

        # Allow default values to overspecify arguments
        if (n_handler_args > n_args and
            handler_defaults and
            n_handler_args - len(handler_defaults) <= n_args):
            n_handler_args = n_args

        if n_handler_args != n_args:
            if inspect.isfunction(handler) or inspect.ismethod(handler):
                descr = '%s at %s:%d' % (
                    handler.func_name,
                    handler.func_code.co_filename,
                    handler.func_code.co_firstlineno)
            else:
                descr = repr(handler)

            raise TypeError(
                '%s event was dispatched with %d arguments, but '
                'handler %s has an incompatible function signature' %
                (event_type, len(args), descr))
        else:
            raise

    def event(self, *args):
        """
        A convenience decorator for event handlers.

        There are two ways to use this decorator. The first is to bind onto a
        defined event method::

            @a.event
            def on_event(self, *args):
                # ...

        Optionally, it can pass the event type as an argument and bind to an
        arbitrary function provided that function has the correct parameters::

            @a.event('on_event')
            def foobar(self, *args):
                # ...

        """
        if len(args) == 0: # @a.event()
            def decorator(func):
                name = func.__name__
                self.set_handler(name, func)
                return func
            return decorator
        elif inspect.isroutine(args[0]): # @a.event
            func = args[0]
            name = func.__name__
            self.set_handler(name, func)
            return args[0]
        elif isinstance(args[0], basestring): # @a.event('on_event')
            name = args[0]
            def decorator(func):
                self.set_handler(name, func)
                return func
            return decorator

    def connect(self, p1, w2, p2=None, func=lambda x: x):
        '''Connect events to a widget property'''
        def lambda_connect(*largs):
            if type(p2) in (tuple, list):
                if len(largs) != len(p2):
                    pymt_logger.exception('Widget: cannot connect with different size')
                    raise
                for p in p2:
                    if p is None:
                        continue
                    w2.__setattr__(p, type(w2.__getattribute__(p))(
                        func(largs[p2.index(p)])))
            else:
                dtype = type(w2.__getattribute__(p2))
                try:
                    if len(largs) == 1:
                        w2.__setattr__(p2, dtype(func(*largs)))
                    else:
                        w2.__setattr__(p2, dtype(func(largs)))
                except Exception, e:
                    pymt_logger.exception('Widget: cannot connect with different size')
                    raise
        if p2 is None:
            self.push_handlers(**{p1: w2})
        else:
            self.push_handlers(**{p1: lambda_connect})

# install acceleration
try:
    import types
    from accelerate import accelerate
    if accelerate is not None:
        EventDispatcher.dispatch_event = types.MethodType(
            accelerate.eventdispatcher_dispatch_event, None, EventDispatcher)
except ImportError, e:
    pymt_logger.warning('Event: Unable to use accelerate module <%s>' % e)
