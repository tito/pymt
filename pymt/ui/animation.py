'''
Animation package: handle animation, and default alpha method
'''

__all__ = ['AnimationAlpha', 'Animation']

import pyglet
import math

class AnimationAlpha(object):
    """Collection of animation function, to be used with Animation object."""
    @staticmethod
    def ramp(value_from, value_to, length, frame):
        return (1.0 - frame / length) * value_from  +  frame / length * value_to

    @staticmethod
    def sin(value_from, value_to, length, frame):
        return math.sin(math.pi / 2 * (1.0 - frame / length)) * value_from  + \
            math.sin(math.pi / 2  * (frame / length)) * value_to

    @staticmethod
    def bubble(value_from, value_to, length, frame):
        s = -math.pi / 2
        p = math.pi
        return math.sin(s + p * (1.0 - frame / length)) * value_from  + \
            math.sin(s + p  * (frame / length)) * value_to


class Animation(object):
    """Class to animate property over the time"""
    def __init__(self, widget, label, prop, to, timestep, length,
                 func=AnimationAlpha.ramp, inner=False):
        self.widget     = widget
        self.frame      = 0.0
        self.prop       = prop
        self.value_to   = to
        self.value_from = self.get_value_from()
        self.timestep   = timestep
        self.length     = length
        self.label      = label
        self.func       = func
        self.want_stop  = False
        self.running    = False
        self.inner      = inner

    def get_current_value(self):
        l = self.length
        f = self.frame
        a = self.value_from
        b = self.value_to

        if type(a) in (list, tuple):
            if len(a) != len(b):
                raise Exception()
            return map(lambda x: self.func(a[x], b[x], l, f), xrange(len(a)))
        return self.func(a, b, l, f)

    def start(self):
        self.want_stop = False
        self.reset()
        pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        self.running = True
        self.widget.dispatch_event('on_animation_start', self)

    def reset(self):
        self.value_from = self.get_value_from()
        self.frame = 0.0
        self.widget.dispatch_event('on_animation_reset', self)

    def stop(self):
        self.want_stop = True

    def advance_frame(self, dt):
        if self.want_stop:
            return
        self.frame += self.timestep
        self.set_value_from(self.get_current_value())
        if self.frame < self.length:
            pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        else:
            self.running = False
            self.widget.dispatch_event('on_animation_complete', self)

    def get_value_from(self):
        if hasattr(self.widget, self.prop):
            return self.widget.__getattribute__(self.prop)
        return self.widget.__dict__[self.prop]

    def set_value_from(self, value):
        if hasattr(self.widget, self.prop):
            kwargs = {}
            if self.inner:
                kwargs['inner'] = True
            try:
                self.widget.__setattr__(self.prop, value, **kwargs)
            except:
                self.widget.__setattr__(self.prop, value)
        else:
            self.widget.__dict__[self.prop] = value
