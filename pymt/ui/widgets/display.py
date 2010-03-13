__all__ = ('MTDisplay', )

from ..factory import MTWidgetFactory, MTWidget
from ...base import getCurrentTouches
from ...graphx import set_color, drawCircle

class MTDisplay(MTWidget):
    '''MTDisplay is a widget that draw a circle
    under every touch on window.

    :Parameters:
        `touch_color` : list
            Color of circle under finger
        `radius` : int
            Radius of circle under finger in pixel

    :Styles:
        `touch-color` : color
            Color of circle under finger
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('touch_color', (1,1,0))
        kwargs.setdefault('radius', 20)
        super(MTDisplay, self).__init__(**kwargs)

        self.radius = kwargs['radius']
        self.touch_color = kwargs['touch_color']
        self.touches    = {}


    def apply_css(self, styles):
        if 'touch-color' in styles:
            self.touch_color = styles.get('touch-color')

    def draw(self):
        '''Draw a circle under every touches'''
        set_color(*self.touch_color)
        for touch in getCurrentTouches():
            drawCircle(pos=(touch.x, touch.y), radius=self.radius)

MTWidgetFactory.register('MTDisplay', MTDisplay)
