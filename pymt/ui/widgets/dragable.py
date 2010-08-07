'''
Dragable widget: a moveable widget over the window
'''

__all__ = ('MTDragable', )

from pymt.ui.widgets.widget import MTWidget
from pymt.vector import Vector

class MTDragable(MTWidget):
    '''MTDragable is a moveable widget over the window'''
    def __init__(self, **kwargs):
        super(MTDragable, self).__init__(**kwargs)
        self.state = 'normal'

    def on_touch_down(self, touch):
        if self.state == 'dragging':
            return False
        if self.collide_point(touch.x, touch.y):
            self.state = 'dragging'
            touch.grab(self)
            touch.userdata['touch_offset'] = Vector(self.pos)-touch.pos
            return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.pos = touch.userdata['touch_offset'] + touch.pos
            return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.state = 'normal'
            touch.ungrab(self)
            return True
