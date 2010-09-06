'''
Gesture widget: a widget with on_gesture event implementation
'''

__all__ = ('MTGestureWidget', )

from pymt.gesture import Gesture
from pymt.ui.widgets.widget import MTWidget

class MTGestureWidget(MTWidget):
    '''Detect a stroke, it in a Gesture and dispatch it in an event.

    :Events:
        `on_gesture` (Gesture g, Touch touch)
            Fired when a stroke is finished
    '''
    def __init__(self):
        super(MTGestureWidget, self).__init__()
        self.register_event_type('on_gesture')
        self.points = {}
        self.db = []

    def on_touch_down(self, touch):
        if not touch.id in self.points:
            self.points[touch.id] = []
        self.points[touch.id].append((touch.x, touch.y))

    def on_touch_move(self, touch):
        if not touch.id in self.points:
            return
        self.points[touch.id].append((touch.x, touch.y))

    def on_touch_up(self, touch):
        if not touch.id in self.points:
            return
        self.points[touch.id].append((touch.x, touch.y))

        # create Gesture from stroke
        g = Gesture()
        g.add_stroke(self.points[touch.id])
        g.normalize()
        g.touchID = touch.id

        # dispatch gesture
        self.dispatch_event('on_gesture', g, touch)

        # suppress points
        del self.points[touch.id]

    def on_gesture(self, gesture, touch):
        pass
