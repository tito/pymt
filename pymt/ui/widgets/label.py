'''
Label: a simple text label
'''


__all__ = ['MTLabel']

import pymt
from ...graphx import drawLabel, set_color, drawCSSRectangle, getLabel, getLastLabel
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label ::

        label = MTLabel(label='Plop world')

    :Parameters:
        `autosize`: bool, default to True
            Update size information with label size
        `autowidth`: bool, default to True
            Update width information with the label content width
        `autoheight`: bool, default to True
            Update height information with the label content height

    MTLabel support all parameters from the Core label. Check `LabelBase`
    class to known all availables parameters.
    '''
    __slots__ = ('autowidth', 'autoheight', 'autosize', 'label',
        '_used_label', 'kwargs', 'anchor_x', 'anchor_y')

    def __init__(self, **kwargs):
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('autosize', False)
        kwargs.setdefault('label', '')

        self.autowidth  = kwargs.get('autowidth')
        self.autoheight = kwargs.get('autoheight')
        self.autosize   = kwargs.get('autosize')
        self.anchor_x   = kwargs.get('anchor_x')
        self.anchor_y   = kwargs.get('anchor_y')
        self.label = kwargs.get('label')
        del kwargs['autowidth']
        del kwargs['autoheight']
        del kwargs['autosize']
        del kwargs['label']

        super(MTLabel, self).__init__(**kwargs)

        for item in ('size', 'pos'):
            if item in kwargs:
                del kwargs[item]

        self.kwargs = kwargs

        # update this label size
        label = getLabel(label=self.label, **self.kwargs)
        self._update_size(*label.size)
        self._used_label = label

    def draw(self):
        # because the anchor_x/anchor_y is propagated to the drawLabel,
        # we don't care about the internal label size.
        pos = list(self.center)
        if self.anchor_x == 'left':
            pos[0] = self.x
        elif self.anchor_x == 'right':
            pos[0] = self.x + self.width
        if self.anchor_y == 'top':
            pos[1] = self.y + self.height
        elif self.anchor_y == 'bottom':
            pos[1] = self.y

        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        w, h = drawLabel(label=self.label, pos=pos, **self.kwargs)
        self._used_label = getLastLabel()
        self._update_size(w, h)

    def _update_size(self, w, h):
        if (self.autoheight and self.autowidth) or self.autosize:
            self.size = (w, h)
        elif self.autoheight:
            self.height = h
        elif self.autowidth:
            self.width = w

    def __getattribute__(self, name):
        try:
            return super(MTLabel, self).__getattribute__(name)
        except:
            kw = self.kwargs
            if name in kw:
                return kw[name]
            raise

    def __setattr__(self, name, value):
        try:
            kw = super(MTLabel, self).__getattribute__('kwargs')
            if name in kw:
                kw[name] = value
                return None
        except:
            pass
        return super(MTLabel, self).__setattr__(name, value)

MTWidgetFactory.register('MTLabel', MTLabel)
