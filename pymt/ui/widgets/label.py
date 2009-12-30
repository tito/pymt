'''
Label: a simple text label
'''

from __future__ import with_statement
__all__ = ['MTLabel']

import pymt
from ...graphx import drawLabel, set_color, drawCSSRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label ::

        label = MTLabel(label='Plop world')

    :Parameters:
        `autowidth`: bool, default to True
            Update width information with the label content width
        `autoheight`: bool, default to True
            Update height information with the label content height
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('autowidth', False)
        kwargs.setdefault('autoheight', False)
        kwargs.setdefault('label', '')

        self.autowidth  = kwargs.get('autowidth')
        self.autoheight = kwargs.get('autoheight')
        self.label = kwargs.get('label')
        del kwargs['autowidth']
        del kwargs['autoheight']
        del kwargs['label']

        super(MTLabel, self).__init__(**kwargs)

        if 'size' in kwargs:
            del kwargs['size']
        self.kwargs = kwargs

    def draw(self):
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        w, h = drawLabel(label=self.label, pos=self.center, **self.kwargs)
        if self.autoheight:
            self.height = h
        if self.autowidth:
            self.width = w


MTWidgetFactory.register('MTLabel', MTLabel)
