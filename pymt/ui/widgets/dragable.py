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

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = ('dragging', touch.id, touch.x, touch.y)
            return True

    def on_touch_move(self, touch):
        if self.state[0] == 'dragging' and self.state[1] == touch.id:
            self.x, self.y = (self.x + (touch.x - self.state[2]) , self.y + touch.y - self.state[3])
            self.state = ('dragging', touch.id, touch.x, touch.y)
            return True

    def on_touch_up(self, touch):
        if self.state[1] == touch.id:
            self.state = ('normal', None)
            return True

MTWidgetFactory.register('MTDragable', MTDragable)
