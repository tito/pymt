'''
Double Tap: search touch for a double tap
'''

__all__ = ['InputPostprocDoubleTap']

import pymt
from ...clock import getClock

class InputPostprocDoubleTap(object):
    '''
    InputPostProcDoubleTap is a post-processor to check if a touch is a double tap or not.
    Double tap can be configured in the PyMT config file ::

        [pymt]
            double_tap_time = 250
            double_tap_distance = 20

    Distance parameter is in 0-1000, and time is in millisecond.
    '''
    def __init__(self):
        self.double_tap_distance = pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time = pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0
        self.touches = {}

    def find_double_tap(self, ref):
        '''Find a double tap touch within self.touches.
        The touch must be not a previous double tap, and the distance must be
        ok'''
        for touchid in self.touches:
            if ref.id == touchid:
                continue
            type, touch = self.touches[touchid]
            if touch.is_double_tap:
                continue
            distance = pymt.Vector.distance(
                pymt.Vector(ref.sx, ref.sy),
                pymt.Vector(touch.oxpos, touch.oypos))
            if distance > self.double_tap_distance:
                continue
            touch.double_tap_distance = distance
            return touch
        return None


    def process(self, events):
        # first, check if a touch down have a double tap
        for type, touch in events:
            if type == 'down':
                touch_double_tap = self.find_double_tap(touch)
                if touch_double_tap:
                    touch.is_double_tap = True
                    touch.double_tap_time = touch.time_start - touch_double_tap.time_start
                    touch.double_tap_distance = touch_double_tap.double_tap_distance

            # add the touch internaly
            self.touches[touch.id] = (type, touch)

        # second, check if up-touch is timeout for double tap
        to_remove = []
        time_current = getClock().get_time()
        for touchid in self.touches:
            type, touch = self.touches[touchid]
            if type != 'up':
                continue
            if time_current - touch.time_start < self.double_tap_time:
                continue
            to_remove.append(touch.id)

        # third, remove expired internal touches
        for touchid in to_remove:
            if touchid in self.touches:
                del self.touches[touchid]

        return events
