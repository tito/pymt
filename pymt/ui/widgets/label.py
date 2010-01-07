'''
Label: a simple text label
'''


__all__ = ['MTLabel']

import pymt
from ...graphx import drawLabel, set_color, drawCSSRectangle, getLabel
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
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('autosize', False)
        kwargs.setdefault('label', '')

        self.autowidth  = kwargs.get('autowidth')
        self.autoheight = kwargs.get('autoheight')
        self.autosize   = kwargs.get('autosize')
        self.label = kwargs.get('label')
        del kwargs['autowidth']
        del kwargs['autoheight']
        del kwargs['autosize']
        del kwargs['label']

        super(MTLabel, self).__init__(**kwargs)

        if 'size' in kwargs:
            del kwargs['size']
        if 'pos' in kwargs:
            del kwargs['pos']

        self.kwargs = kwargs

        # update this label size
        label = getLabel(label=self.label, **self.kwargs)
        self._update_size(*label.size)

    def draw(self):
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        w, h = drawLabel(label=self.label, pos=self.center, **self.kwargs)
        self._update_size(w, h)

    def _update_size(self, w, h):
        if (self.autoheight and self.autowidth) or self.autosize:
            self.size = (w, h)
        elif self.autoheight:
            self.height = h
        elif self.autowidth:
            self.width = w

MTWidgetFactory.register('MTLabel', MTLabel)
