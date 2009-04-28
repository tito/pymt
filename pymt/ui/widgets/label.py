'''
Label: a simple text label
'''

from __future__ import with_statement
__all__ = ['MTLabel']

from pyglet.text import Label
from ...graphx import drawLabel
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label.
    ::
        label = MTLabel(label='Plop world')

    :Parameters:
        `label`: string, default is ''
            Text of label
        `anchor_x`: string
            X anchor of label, refer to pyglet.label.anchor_x documentation
        `anchor_y`: string
            Y anchor of label, refer to pyglet.label.anchor_x documentation
        `font_name`: string, default is ''
            Font name of label
        `font_size`: integer, default is 10
            Font size of label
        `bold`: bool, default is True
            Font bold of label
        `color`:  tuple, default is (1,1,1,1)
            Color of label
        `multiline`: bool, default is False
            Activate multiline
        `halign`: str, default is 'left'
            Horizontal alignment, can be 'left', 'center', 'right'.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('font_name', '')
        kwargs.setdefault('font_size', 10)
        kwargs.setdefault('bold', False)
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('color', (1,1,1,1))
        kwargs.setdefault('halign', 'left')

        super(MTLabel, self).__init__(**kwargs)

        color = kwargs.get('color')
        if len(color) == 3:
            color[3] = 1

        self.label_obj = Label(
            font_name=kwargs.get('font_name'),
            font_size=kwargs.get('font_size'),
            bold=kwargs.get('bold'),
            anchor_x=kwargs.get('anchor_x'),
            anchor_y=kwargs.get('anchor_y'),
            multiline=kwargs.get('multiline'),
            halign=kwargs.get('halign'),
            width=self.width,
            color=map(lambda x: int(x * 255), kwargs.get('color')),
            text=''
        )
        self.label = str(kwargs.get('label'))

    def on_resize(self, w, h):
        self.label_obj.width = w
        super(MTLabel, self).on_resize(w, h)

    def get_label(self):
        return self._label
    def set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self._label
    label = property(get_label, set_label)

    def draw(self):
        if len(self._label):
            self.label_obj.x, self.label_obj.y = self.pos[0], self.pos[1]
            self.label_obj.draw()

MTWidgetFactory.register('MTLabel', MTLabel)
