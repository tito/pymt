from pymt.gesture import Gesture
from pymt.ui import MTWidget

class MTGestureWidget(MTWidget):
    def __init__(self):
        super(MTGestureWidget, self).__init__()
        self.register_event_type('on_gesture')
        self.points = {}
        self.db = []

    def on_touch_down(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
            self.points[touchID] = []
        self.points[touchID].append((x, y))

    def on_touch_move(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
            return
        self.points[touchID].append((x, y))

    def on_touch_up(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
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

