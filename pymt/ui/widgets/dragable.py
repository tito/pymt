'''
Dragable widget: a moveable widget over the window
'''

__all__ = ['MTDragable']

from ..factory import MTWidgetFactory
from widget import MTWidget

class MTDragable(MTWidget):
    '''MTDragable is a moveable widget over the window'''
    def __init__(self, **kwargs):
        super(MTDragable, self).__init__(**kwargs)
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

MTWidgetFactory.register('MTDragable', MTDragable)
