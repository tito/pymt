'''
Modal window: stop all interaction with background widget
'''

__all__ = ('MTModalWindow', )

from pymt.graphx import set_color, drawCSSRectangle
from pymt.ui.widgets.widget import MTWidget

class MTModalWindow(MTWidget):
    '''A static window, non-movable, with a dark background.
    Ideal to add popup or some other things. ModalWindow capture
    all touchs events.
    '''
    def __init__(self, **kwargs):
        super(MTModalWindow, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        super(MTModalWindow, self).on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super(MTModalWindow, self).on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super(MTModalWindow, self).on_touch_up(touch)
        return True

    def draw(self):
        w = self.get_parent_window()
        if not w:
            return
        self.size = w.size
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=self.size, style=self.style)
