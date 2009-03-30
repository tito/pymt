'''
Abstract layout: layout base for implementation
'''
__all__ = ['MTAbstractLayout']

from ..widget import MTWidget

class MTAbstractLayout(MTWidget):
    '''Abstract layout. Base class used to implement layout.

    :Property:
        `auto_layout` : bool, default to True
            Do layout when appropriate

    :Events:
        `on_layout`
            Fired when layout function have been called
        `on_content_resize`
            Fired when content_width or content_height have changed
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractLayout:
            raise NotImplementedError, 'class MTAbstractLayout is abstract'
        kwargs.setdefault('auto_layout', True)
        super(MTAbstractLayout, self).__init__(**kwargs)
        self.register_event_type('on_layout')
        self.register_event_type('on_content_resize')
        self.auto_layout        = kwargs.get('auto_layout')
        self.need_layout        = False
        self.need_parent_layout = False
        self._content_height    = 0
        self._content_width     = 0

    def _set_content_width(self, w):
        if self._content_width == w:
            return
        self._content_width = w
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_width(self):
        return self._content_width
    content_width = property(_get_content_width, _set_content_width)

    def _set_content_height(self, w):
        if self._content_height == w:
            return
        self._content_height = w
        self.dispatch_event('on_content_resize', self._content_height, self._content_height)
    def _get_content_height(self):
        return self._content_height
    content_height = property(_get_content_height, _set_content_height)

    def _set_content_size(self, size):
        w, h = size
        if self._content_width == w and self._content_height == h:
            return
        self._content_width = w
        self._content_height = h
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_size(self):
        return (self.content_width, self.content_height)
    content_size = property(_get_content_size, _set_content_size)

    def add_widget(self, widget, do_layout=None):
        super(MTAbstractLayout, self).add_widget(widget)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.do_layout()

    def remove_widget(self, widget, do_layout=None):
        super(MTAbstractLayout, self).remove_widget(widget)
        self.need_layout = True
        if do_layout or (not do_layout and self.auto_layout):
            self.do_layout()

    def do_layout(self):
        self.need_layout = False

    def do_parent_layout(self):
        self.need_parent_layout = False
        if self.parent:
            layout = self.parent.get_parent_layout()
            if layout:
                layout.do_layout()

    def update(self):
        if self.need_layout:
            self.do_layout()
        if self.need_parent_layout:
            self.do_parent_layout()

    def get_parent_layout(self):
        return self

    def on_layout(self):
        pass

    def on_content_resize(self, w, h):
        self.need_parent_layout = True
        if self.auto_layout:
            self.do_parent_layout()

    def on_move(self, x, y):
        self.need_layout = True
        if self.auto_layout:
            self.do_layout()
            super(MTAbstractLayout, self).on_move(x, y)

