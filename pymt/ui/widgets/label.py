'''
Label: a simple text label
'''

from __future__ import with_statement
__all__ = ['MTLabel']

from pyglet.text import Label
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label ::

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
        `autoheight`: bool, default to False
            Update height information with the label content height
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
        kwargs.setdefault('autoheight', False)

        super(MTLabel, self).__init__(**kwargs)

        self.autoheight = kwargs.get('autoheight')

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
        # update height of label only in autoheight case
        if self.autoheight and self.height != self.label_obj.content_height:
            self.height = self.label_obj.content_height
    label = property(get_label, set_label)

    def set_color(self, color):
        if len(color) == 3:
            color[4] = 1
        color = map(lambda x: int(float(x) * 255.), color)
        self.label_obj.color = color
    def get_color(self):
        return map(lambda x: float(x) / 255., self.label_obj.color)
    color = property(get_color, set_color)

    def draw(self):
        if len(self._label):
            self.label_obj.x, self.label_obj.y = self.pos[0], self.pos[1]
            self.label_obj.draw()

    # maps some attribute directly on label_obj

    shared_attributes = ('font_name', 'font_size', 'bold', 'anchor_x',
                         'anchor_y', 'multiline', ) # halign not in pyglet

    def __getattribute__(self, name):
        if name in MTLabel.shared_attributes:
            return self.label_obj.__getattribute__(name)
        return super(MTLabel, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in MTLabel.shared_attributes:
            return self.label_obj.__setattr__(name, value)
        return super(MTLabel, self).__setattr__(name, value)


MTWidgetFactory.register('MTLabel', MTLabel)
