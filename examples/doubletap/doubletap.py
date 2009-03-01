from pymt import *

w = MTWindow()
@w.event
def on_touch_down(touches, touchID, x, y):
    print 'touch %s down (%f, %f), doubletap(%s, %.3fms)' % ([touchID], x, y,
        str(touches[touchID].is_double_tap),
        touches[touchID].double_tap_time)

@w.event
def on_touch_move(touches, touchID, x, y):
    print 'touch %s move (%f, %f), doubletap(%s, %.3fms)' % ([touchID], x, y,
        str(touches[touchID].is_double_tap),
        touches[touchID].double_tap_time)

@w.event
def on_touch_up(touches, touchID, x, y):
    print 'touch %s up   (%f, %f), doubletap(%s, %.3fms)' % ([touchID], x, y,
        str(touches[touchID].is_double_tap),
        touches[touchID].double_tap_time)

runTouchApp()
