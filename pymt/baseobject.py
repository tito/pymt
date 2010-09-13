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
        x, y = self._pos
        w, h = self._size
        return (x + w / 2., y + h / 2.)
    def _set_center(self, center):
        cx, cy = center
        w, h = self._size
        return self._set_pos((cx - w / 2., cy - h / 2.))
    center = property(_get_center, _set_center,
                      doc='Object center (cx, cy)')


    #helpfull getter setter for corners and right/top side
    def _get_top(self):
        return self.y + self.height
    def _set_top(self, top):
        self.y = top - self.height
    top = property(_get_top, _set_top,
                   doc='y coordinate of top (y + height)')

    def _get_right(self):
        return self.x+self.width
    def _set_right(self, right):
        self.x = right - self.width
    right = property(_get_right, _set_right,
                     doc='x coordinate of rigth side (x + width)')

    def _get_topleft(self):
        return (self.x, self.top)
    def _set_topleft(self, topleft):
        self.x = topleft[0]
        self.top = topleft[1]
    topleft = property(_get_topleft, _set_topleft,
                       doc='coordinate of topleft (x, y+height)')

    def _get_centerleft(self):
        return (self.x, self.y + self.height / 2.)
    def _set_centerleft(self, centerleft):
        self.pos = (centerleft[0], centerleft[1] - self.height / 2.)
    centerleft = property(_get_centerleft, _set_centerleft,
                          doc='coordinate of centerleft (x, y + height / 2)')

    def _get_topcenter(self):
        return (self.x+self.width/2., self.y+self.height)
    def _set_topcenter(self, topcenter):
        self.pos = (topcenter[0] - self.width / 2., topcenter[1] - self.height)
    topcenter = property(_get_topcenter, _set_topcenter,
                         doc='coordinate of topcenter (x+width/2, y+height)')

    def _get_bottomcenter(self):
        return (self.x+self.width/2., self.y)
    def _set_bottomcenter(self, bottomcenter):
        self.pos = (bottomcenter[0]-self.width/2., bottomcenter[1])
    bottomcenter = property(_get_bottomcenter, _set_bottomcenter,
                            doc='coordinate of bottomcenter (x+width/2, y)')

    def _get_topright(self):
        return (self.right, self.top)
    def _set_topright(self, topright):
        self.right = topright[0]
        self.top = topright[1]
    topright = property(_get_topright, _set_topright,
                        doc='coordinate of topright (x+width, y+height)')

    def _get_centerright(self):
        return (self.right, self.y+self.height/2.)
    def _set_centerright(self, centerright):
        self.right = centerright[0]
        self.y = centerright[1] - self.height/2.0
    centerright = property(_get_centerright, _set_centerright,
                           doc='coordinate of centerright (x+width, y+height/2)')

    def _get_bottomright(self):
        return (self.right, self.y)
    def _set_bottomright(self, bottomright):
        self.right = bottomright[0]
        self.y = bottomright[1] - self.height
    bottomright = property(_get_bottomright, _set_bottomright,
                           doc='coordinate of bottomright (x+width, y')


    def update(self):
        '''Placeholder to update the object'''
        pass

    def draw(self):
        '''Placeholder to draw the object'''
        pass
