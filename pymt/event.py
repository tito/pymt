'''
Event: event class from Pyglet project

Lot of thanks to Pyglet !
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

class EventDispatcher(object):
    _event_stack = ()

    def __init__(self):
        super(EventDispatcher, self).__init__()
        self._event_types = []

    def unregister_event_type(self, event_type):
        if event_type in self._event_types:
            self._event_types.remove(event_type)

    def register_event_type(self, event_type):
        if not event_type in self._event_types:
            self._event_types.append(event_type)

    def push_handlers(self, *args, **kwargs):
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = []

        # Place dict full of new handlers at beginning of stack
        self._event_stack.insert(0, {})
        self.set_handlers(*args, **kwargs)

    def remove_handler(self, name, handler):
        for frame in self._event_stack:
            try:
                if frame[name] is handler:
                    del frame[name]
                    break
            except KeyError:
                pass

    def remove_handlers(self, *args, **kwargs):
        handlers = list(self._get_handlers(args, kwargs))

        # Find the first stack frame containing any of the handlers
        def find_frame():
            for frame in self._event_stack:
                for name, handler in handlers:
                    try:
                        if frame[name] == handler:
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
                if frame[name] == handler:
                    del frame[name]
            except KeyError:
                pass

        # Remove the frame if it's empty.
        if not frame:
            self._event_stack.remove(frame)

    def _get_handlers(self, args, kwargs):
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
        for name, handler in kwargs.items():
            # Function for handling given event (no magic)
            if name not in self._event_types:
                raise Exception('Unknown event "%s"' % name)
            yield name, handler

    def set_handlers(self, *args, **kwargs):
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]

        for name, handler in self._get_handlers(args, kwargs):
            self.set_handler(name, handler)

    def set_handler(self, name, handler):
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]
        self._event_stack[0][name] = handler

    def dispatch_event(self, event_type, *args):
        # unknown event type
        if event_type not in self._event_types:
            return

        # search handler stack for matching event handlers
        for frame in self._event_stack:
            handler = frame.get(event_type, None)
            if handler:
                try:
                    if handler(*args):
                        return True
                except TypeError:
                    self._raise_dispatch_exception(event_type, args, handler)

        # check instance for an event handler
        if hasattr(self, event_type):
            try:
                # call event
                func = getattr(self, event_type)
                if func(*args):
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
        elif type(args[0]) in (str, unicode): # @a.event('on_event')
            name = args[0]
            def decorator(func):
                self.set_handler(name, func)
                return func
            return decorator
