'''
InputPostproc Double Tap: search touch for a double tap
'''

__all__ = ['InputPostprocDoubleTap']

import pymt
from pyglet import clock

#
# About attribute added in a touch:
# __pp_do_event: next event we want
# __pp_have_event_down: True if event down is already dispatched
# __pp_no_event: don't generate event for him
# __pp_is_timeout: double tap timeout ?
# 

class InputPostprocDoubleTap(object):
    '''
    InputPostProcDoubleTap is a post-processor to check if a touch is a double tap or not.
    Double tap can be configurd in the PyMT config file ::

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
        for touchID in self.touches:
            touch = self.touches[touchID]
            if touch.__pp_is_timeout or \
               touch.__pp_have_event_down or \
               touch.__pp_do_event != 'up':
                continue
            distance = pymt.Vector.distance(pymt.Vector(ref.sx, ref.sy),
                                            pymt.Vector(touch.sx, touch.sy))
            if distance > self.double_tap_distance:
                continue
            return touch

    def process(self, events):
        gen_events = []
        remove_list = []

        # check old/new touches
        for type, touch in events:

            # double tap ?
            if touch.is_double_tap:
                gen_events.append((type, touch))
                continue

            # release ?
            if type == 'up':
                if touch.id in self.touches:
                    self.touches[touch.id].__pp_do_event = 'up'

            # new touch ?
            elif not touch.id in self.touches:

                # select first touch only on down state
                if type != 'down':
                    pymt.pymt_logger.warning('Ignore new touch with initial state at %s' % type)
                    continue

                # search for a double tap
                touch_double_tap = self.find_double_tap(touch)
                if touch_double_tap:
                    # ignore old double tap
                    remove_list.append(touch_double_tap.id)
                    # set new touch as double tap touch
                    touch.is_double_tap = True
                    touch.double_tap_time = touch.time_start - touch_double_tap.time_start
                    touch.time_start = touch_double_tap.time_start
                    gen_events.append((type, touch))
                    continue
                else:
                    # can be a double tap candidate, add some infos
                    touch.__pp_do_event = 'down'
                    touch.__pp_have_event_down = False
                    touch.__pp_no_event = False
                    touch.__pp_is_timeout = False

                # initialization
                self.touches[touch.id] = touch

            # just a move ?
            else:
                # update next event
                self.touches[touch.id].__pp_do_event = type

        # now, generate appropriate events
        time_current = clock.get_default().time()
        for touchID in self.touches:
            touch = self.touches[touchID]

            if touch.is_double_tap:
                continue

            # not timeout state, calculate !
            if not touch.__pp_is_timeout:
                if time_current - touch.time_start > self.double_tap_time:
                    touch.__pp_is_timeout = True
                if not touch.__pp_is_timeout:
                    # at least, check double_tap_distance
                    distance = pymt.Vector.distance(pymt.Vector(touch.oxpos, touch.oypos),
                                                    pymt.Vector(touch.sx, touch.sy))
                    if distance < self.double_tap_distance:
                        # ok, time and distance is ok, don't generate.
                        continue
                    touch.__pp_is_timeout = True

            # ok, now check event !
            event_str = None
            if not touch.__pp_have_event_down:
                touch.sx, touch.sy = touch.oxpos, touch.oypos
                event_str = 'down'
                touch.__pp_have_event_down = True
            elif touch.__pp_do_event:
                event_str = touch.__pp_do_event
                # no down 2 times!
                if event_str == 'down':
                    event_str = None
                touch.__pp_do_event = False

            # event to do ?
            if not event_str:
                continue
            if not touch.__pp_no_event:
                '''
                if event_str == 'down':
                    xpos, ypos = cur.dxpos, cur.dypos
                else:
                    xpos, ypos = cur.xpos, cur.ypos
                '''
                gen_events.append((event_str, touch))

            if event_str == 'up':
                remove_list.append(touch.id)

        for touchID in remove_list:
            if touchID in self.touches:
                del self.touches[touchID]

        return gen_events
