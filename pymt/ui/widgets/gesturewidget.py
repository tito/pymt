'''
Gesture widget: a widget with on_gesture event implementation
'''

__all__ = ['MTGestureWidget']

from ...gesture import Gesture
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTGestureWidget(MTWidget):
    '''Detect a stroke, it in a Gesture and dispatch it in an event.

    :Events:
        `on_gesture` (Gesture g, int x, int y)
            Fired when a stroke is finished
    '''
    def __init__(self):
        super(MTGestureWidget, self).__init__()
        self.register_event_type('on_gesture')
        self.points = {}
        self.db = []

    def on_touch_down(self, touches, touchID, x, y):
        if not touchID in self.points:
            self.points[touchID] = []
        self.points[touchID].append((x, y))

    def on_touch_move(self, touches, touchID, x, y):
        if not touchID in self.points:
            return
        self.points[touchID].append((x, y))

    def on_touch_up(self, touches, touchID, x, y):
        if not touchID in self.points:
            return
        self.points[touchID].append((x, y))

        # create Gesture from stroke
        g = Gesture()
        g.add_stroke(self.points[touchID])
        g.normalize()

        # dispatch gesture
        self.dispatch_event('on_gesture', g, x, y)

        # suppress points
        del self.points[touchID]

    def on_gesture(self, gesture, x, y):
        pass

# Register all base widgets
MTWidgetFactory.register('MTGestureWidget', MTGestureWidget)
