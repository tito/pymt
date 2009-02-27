from __future__ import with_statement
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.factory import MTWidgetFactory
from pymt.graphx import *

class MTModalWindow(MTWidget):
    '''A static window, non-movable, with a dark background.
    Ideal to add popup or some other things. ModalWindow capture
    all touchs events.
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('color', (0,0,0,1))
        super(MTModalWindow, self).__init__(**kwargs)

    def on_touch_down(self, touches, touchID, x, y):
        super(MTModalWindow, self).on_touch_down(touches, touchID, x, y)
        return True

    def on_touch_move(self, touches, touchID, x, y):
        super(MTModalWindow, self).on_touch_move(touches, touchID, x, y)
        return True

    def on_touch_up(self, touches, touchID, x, y):
        super(MTModalWindow, self).on_touch_up(touches, touchID, x, y)
        return True

    def draw(self):
        w = self.get_parent_window()
        with gx_blending:
            set_color(0, 0, 0, 1)
            drawRectangle(pos=(0,0), size=w.size)


# Register all base widgets
MTWidgetFactory.register('MTModalWindow', MTModalWindow)
