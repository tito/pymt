'''
Clock: a clock with scheduled events

You can add new event like this ::

    def my_callback(dt):
        pass

    # call my_callback every 0.5 seconds
    getClock().schedule_interval(my_callback, 0.5)

    # call my_callback in 5 seconds
    getClock().schedule_once(my_callback, 5)

If the callback return False, the schedule will be removed.
'''

__all__ =  ('Clock', 'getClock')

import time

class _Event(object):

    loop = False
    callback = None
    timeout = 0.
    _last_dt = 0.
    _dt = 0.

    def __init__(self, loop, callback, timeout, starttime):
        self.loop = loop
        self.callback = callback
        self.timeout = timeout
        self._last_dt = starttime

    def do(self, dt):
        self.callback(dt)

    def tick(self, curtime):
        # timeout happen ?
        if curtime - self._last_dt < self.timeout:
            return True

        # calculate current timediff for this event
        self._dt = curtime - self._last_dt
        self._last_dt = curtime

        # call the callback
        ret = self.callback(self._dt)

        # if it's a once event, don't care about the result
        # just remove the event
        if not self.loop:
            return False

        # if user return an explicit false,
        # remove the event
        if ret == False:
            return False

        return True


class Clock(object):
    '''A clock object, that support events'''
    __slots__ = ('_dt', '_last_fps_tick', '_last_tick', '_fps',
            '_fps_counter', '_events')

    def __init__(self):
        self._dt = 0
        self._last_tick = time.time()
        self._fps = 0
        self._fps_counter = 0
        self._last_fps_tick = None
        self._events = []

    def tick(self):
        '''Advance clock to the next step. Must be called every frame.
        The default clock have the tick() function called by PyMT'''
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

        # process event
        self._process_events()

        return self._dt

    def get_fps(self):
        '''Get the current FPS calculated by the clock'''
        return self._fps

    def get_time(self):
        '''Get the last tick made by the clock'''
        return self._last_tick

    def schedule_once(self, callback, timeout):
        '''Schedule an event in <timeout> seconds'''
        event = _Event(False, callback, timeout, self._last_tick)
        self._events.append(event)

    def schedule_interval(self, callback, timeout):
        '''Schedule a event to be call every <timeout> seconds'''
        event = _Event(True, callback, timeout, self._last_tick)
        self._events.append(event)

    def unschedule(callback):
        '''Remove a previous schedule event'''
        self._events = [x for x in self._events if x.callback != callback]

    def _process_events(self):
        to_remove = None

        # process event
        for event in self._events:
            if event.tick(self._last_tick) == False:
                if to_remove is None:
                    to_remove = [event]
                else:
                    to_remove.append(event)

        # event to remove ?
        if to_remove is None:
            return
        for event in to_remove:
            self._events.remove(event)




# create a default clock
_default_clock = Clock()

# make it available
def getClock():
    '''Return the clock instance used by PyMT'''
    global _default_clock
    return _default_clock

