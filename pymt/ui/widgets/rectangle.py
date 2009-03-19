'''
Rectangle widget: draw a rectangle of his pos/size
'''

from __future__ import with_statement
__all__ = ['MTRectangularWidget']

from ...graphx import set_color, drawRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTRectangularWidget(MTWidget):
    '''A rectangular widget that only propagates and handles events if the event was within its bounds
    
    :Properties:
        `bgcolor` : list (optional)
            Background color of widget

    :Styles:
        `bg-color` : color
            Background color of widget
    '''
    def __init__(self, **kwargs):
        super(MTRectangularWidget, self).__init__(**kwargs)
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs.get('bgcolor')

    def apply_css(self, styles):
        if 'bg-color' in styles:
            self.bgcolor = styles.get('bg-color')

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_down(touches, touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_move(touches, touchID, x, y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            super(MTRectangularWidget, self).on_touch_up(touches, touchID, x, y)
            return True

    def draw(self):
        set_color(*self.bgcolor)
        drawRectangle(self.pos, self.size)

MTWidgetFactory.register('MTRectangularWidget', MTRectangularWidget)
