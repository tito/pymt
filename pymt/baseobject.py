'''
Base object: object with position and size attributes, with helpers
'''

class BaseObject(object):

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
    width = property(lambda self: self._get_width(), doc='Object width')

    def _get_height(self):
        return self._size[1]
    height = property(lambda self: self._get_height(), doc='Object height')

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
        self.pos = (y, self.y)
    y = property(lambda self: self._get_y(),
                 lambda self, x: self._set_y(x),
                 doc = 'Object Y position')
