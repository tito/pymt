'''
Modal window: stop all interaction with background widget
'''


__all__ = ['MTModalWindow']

from ...graphx import set_color
from ...graphx import drawCSSRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTModalWindow(MTWidget):
    '''A static window, non-movable, with a dark background.
    Ideal to add popup or some other things. ModalWindow capture
    all touchs events.
    '''
    def __init__(self, **kwargs):
        super(MTModalWindow, self).__init__(**kwargs)

    def on_touch_down(self, *largs):
        super(MTModalWindow, self).on_touch_down(*largs)
        return True

    def on_touch_move(self, *largs):
        super(MTModalWindow, self).on_touch_move(*largs)
        return True

    def on_touch_up(self, *largs):
        super(MTModalWindow, self).on_touch_up(*largs)
        return True

    def draw(self):
        w = self.get_parent_window()
        if not w:
            return
        set_color(*self.style['bg-color'])
        drawCSSRectangle(pos=(0,0), size=w.size, style=self.style)


# Register all base widgets
MTWidgetFactory.register('MTModalWindow', MTModalWindow)
