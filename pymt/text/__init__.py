'''
Text: Handle drawing of text
'''

__all__ = ('Label', )

import pymt
from ..utils import deprecated
from ..logger import pymt_logger

class LabelBase(object):
    __slots__ = ('options', '_data', 'texture', '_label', 'pos', 'size')

    options = {}
    texture = None
    pos = (0, 0)
    size = (0, 0)
    _label = None

    def __init__(self, label, **kwargs):
        kwargs.setdefault('font_size', 12)
        kwargs.setdefault('font_name', 'Liberation Mono,Monospace')
        kwargs.setdefault('bold', False)
        kwargs.setdefault('italic', False)
        kwargs.setdefault('width', None)
        kwargs.setdefault('height', None)
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('size', (None, None))
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        self.options = kwargs
        self.pos = kwargs.get('pos')
        self.size = kwargs.get('size')
        self.label = label

    def update(self):
        if self.size == (None, None):
            self.size = self.texture.size

    def draw(self):
        if self.texture is None:
            return

        x, y = self.pos
        w, h = self.size
        anchor_x = self.options['anchor_x']
        anchor_y = self.options['anchor_y']

        if anchor_x == 'left':
            pass
        elif anchor_x in ('center', 'middle'):
            x -= w * 0.5
        elif anchor_x == 'right':
            x -= w

        if anchor_y == 'bottom':
            pass
        elif anchor_y in ('center', 'middle'):
            y += h * 0.5
        elif anchor_y == 'top':
            y += h

        pymt.set_color(1, 1, 1, 0.999)
        pymt.drawTexturedRectangle(
            texture=self.texture,
            pos=(x, y), size=self.texture.size)

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        if label == self._label:
            return
        self._label = label
        self.update()
    label = property(_get_label, _set_label)
    text = property(_get_label, _set_label)

    def _get_x(self):
        return self.pos[0]
    def _set_x(self, x):
        self.pos = (x, self.pos[1])
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self.pos[1]
    def _set_y(self, y):
        self.pos = (self.pos[0], y)
    y = property(_get_y, _set_y)

    @property
    def content_width(self):
        if self.texture is None:
            return 0
        return self.texture.width

    @property
    def content_height(self):
        if self.texture is None:
            return 0
        return self.texture.height


Label = None

try:
    import text_pygame
    Label = text_pygame.LabelPygame
except:
    pymt_logger.exception('')
    import sys
    sys.exit(0)
    pass
