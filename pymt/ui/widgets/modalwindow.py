'''
Modal window: a modal window implementation, that stop all interaction with widget on his back
'''

from __future__ import with_statement
__all__ = ['MTModalWindow']

from ...graphx import set_color, drawRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget

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
        set_color(0, 0, 0, 1)
        drawRectangle(pos=(0,0), size=w.size)


# Register all base widgets
MTWidgetFactory.register('MTModalWindow', MTModalWindow)
