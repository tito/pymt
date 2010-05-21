def eventdispatcher_dispatch_event(self, event_type, *args):
    # unknown event type
    if event_type not in self._event_types:
        return

    _event_stack = self._event_stack
    # search handler stack for matching event handlers
    if _event_stack is not None:
        for frame in _event_stack:
            handler = frame.get(event_type, None)
            if handler:
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

def widget_on_update(self):
    for w in self.children[:]:
        w.dispatch_event('on_update')

def widget_on_draw(self):
    for w in self.children[:]:
        w.dispatch_event('on_draw')
