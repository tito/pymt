'''
Base object: object with position and size attributes, with helpers
'''

__all__ = ('BaseObject', )

class BaseObject(object):
    '''Represent a object with position and size information'''

    __slots__ = ('_size', '_pos')

    def __init__(self, **kwargs):
        kwargs.setdefault('size', (0, 0))
        kwargs.setdefault('pos', (0, 0))
        super(BaseObject, self).__init__()
        self._size  = kwargs.get('size')
        self._pos   = kwargs.get('pos')

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return False
        self._size = size
        return True
    size = property(lambda self: self._get_size(),
                    lambda self, x: self._set_size(x),
                    doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        return True
    width = property(lambda self: self._get_width(),
                     lambda self, x: self._set_width(x),
                     doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        return True
    height = property(lambda self: self._get_height(),
                     lambda self, x: self._set_height(x),
                      doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
    pos = property(lambda self: self._get_pos(),
                   lambda self, x: self._set_pos(x), doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        self.pos = (x, self.y)
    x = property(lambda self: self._get_x(),
                 lambda self, x: self._set_x(x),
                 doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        self.pos = (self.x, y)
    y = property(lambda self: self._get_y(),
                 lambda self, x: self._set_y(x),
                 doc = 'Object Y position')

    def update(self):
        pass

    def draw(self):
        pass
