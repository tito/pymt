from __future__ import with_statement
__all__ = ['MTLabel']

from ...graphx import drawLabel
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTLabel(MTWidget):
    '''A simple label

    :Styles:
        `font-size` : int
            Size of font
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('text', 'MTLabel')
        super(MTLabel, self).__init__(**kwargs)
        self.text = kwargs.get('text')
        if kwargs.has_key('font_size'):
            self.font_size = kwargs.get('font_size')

    def apply_css(self, styles):
        if styles.has_key('font-size'):
            self.font_size = int(styles.get('font-size'))
        super(MTLabel, self).apply_css(styles)

    def draw(self):
        drawLabel(self.text, pos=self.pos,center=False, font_size=self.font_size)

MTWidgetFactory.register('MTLabel', MTLabel)
