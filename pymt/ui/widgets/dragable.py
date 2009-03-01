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

class MTDragableWidget(MTWidget):
    '''MTDragableWidget is a moveable widget over the window'''
    def __init__(self, **kwargs):
        super(MTDragableWidget, self).__init__(**kwargs)
        self.state = ('normal', None)

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[0] == 'dragging' and self.state[1] == touchID:
            self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID:
            self.state = ('normal', None)
            return True

MTWidgetFactor.register('MTWidgetFactory', MTWidgetFactory)
