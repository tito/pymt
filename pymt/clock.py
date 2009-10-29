__all__ =  ('Clock', 'getClock')

import time

class Clock(object):
    def __init__(self):
        self._last_tick = time.time()

        # initialize dt to a non-value, or it can be lead
        # to a 0 division error
        self._dt = 0.000001

        # fps timer
        self._fps = 0
        self._fps_counter = 0
        self._last_fps_tick = None

    def tick(self):
        # tick the current time
        current = time.time()
        self._dt = current - self._last_tick
        self._fps_counter += 1
        self._last_tick = current

        # calculate fps things
        if self._last_fps_tick == None:
            self._last_fps_tick = current
        elif current - self._last_fps_tick > 1:
            self._fps = self._fps_counter / float(current - self._last_fps_tick)
            self._last_fps_tick = current
            self._fps_counter = 0

        return self._dt

    def get_fps(self):
        return self._fps


# create a default clock
_default_clock = Clock()

# make it available
def getClock():
    global _default_clock
    return _default_clock

