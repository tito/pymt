# ----------------------------------------------------------------------------
#
# Accelerate module
#
# This module provide acceleration for some critical function of PyMT
#
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#
# Event part
#
# ----------------------------------------------------------------------------

def eventdispatcher_dispatch_event(self, event_type, *args):
    # unknown event type
    if event_type not in self._event_types:
        return

    _event_stack = self._event_stack
    # search handler stack for matching event handlers
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


# ----------------------------------------------------------------------------
#
# Widget part
#
# ----------------------------------------------------------------------------

def widget_on_update(self):
    for w in self.children[:]:
        w.dispatch_event('on_update')

def widget_on_draw(self):
    self.draw()
    if self.draw_children:
        for w in self.children[:]:
            w.dispatch_event('on_draw')

def widget_collide_point(self, double x, double y):
    cdef double ox, oy, ow, oh
    ox, oy = self.x, self.y
    ow, oh = self.width, self.height
    if not self.visible:
        return False
    if x > ox  and x < ox + ow and \
       y > oy and y < oy + oh:
        return True
