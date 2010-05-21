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
    size = property(_get_size, _set_size,
                    doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        return True
    width = property(_get_width, _set_width,
                     doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        return True
    height = property(_get_height, _set_height,
                      doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        return True
    pos = property(_get_pos, _set_pos,
                   doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        return True
    x = property(_get_x, _set_x,
                 doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        return True
    y = property(_get_y, _set_y,
                 doc = 'Object Y position')

    def _get_center(self):
        return (self._pos[0] + self._size[0] / 2., self._pos[1] + self._size[1] / 2.)
    def _set_center(self, center):
        return self._set_pos((center[0] - self._size[0] / 2.,
                              center[1] - self._size[1] / 2.))
    center = property(_get_center, _set_center,
                      doc='Object center (cx, cy)')

    def update(self):
        pass

    def draw(self):
        pass
