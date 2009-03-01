from __future__ import with_statement
from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget
from pymt.lib import squirtle
from pymt.vector import *
from pymt.logger import pymt_logger

class MTRectangularWidget(MTWidget):
    '''A rectangular widget that only propagates and handles events if the event was within its bounds'''
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
        set_color(*self.color)
        drawRectangle(self.pos, self.size)

MTWidgetFactory.register('MTRectangularWidget', MTRectangularWidget)
