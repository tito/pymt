from pymt import *

class DumpListener(EventDispatcher):
    def __init__(self):
        super(DumpListener, self).__init__()
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_up')

    def on_touch_down(self, touch):
        print 'DOWN - ', repr(touch)

    def on_touch_move(self, touch):
        print 'MOVE - ', repr(touch)

    def on_touch_up(self, touch):
        print 'UP - ', repr(touch)


touch_event_listeners.append(DumpListener())

# will run with empty window
runTouchApp()
