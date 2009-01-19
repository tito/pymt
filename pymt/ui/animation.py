from pyglet import *
from pyglet.gl import *

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
                 func=AnimationAlpha.ramp):
        self.widget     = widget
        self.frame      = 0.0
        self.prop       = prop
        self.value_to   = to
        self.value_from = self.get_value_from()
        self.timestep   = timestep
        self.length     = length
        self.label      = label
        self.func       = func

    def get_current_value(self):
        return self.func(self.value_from, self.value_to,
                         self.length, self.frame)

    def start(self):
        self.reset()
        pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        self.widget.dispatch_event('on_animation_start', self)

    def reset(self):
        self.value_from = self.get_value_from()
        self.frame = 0.0
        self.widget.dispatch_event('on_animation_reset', self)

    def advance_frame(self, dt):
        self.frame += self.timestep
        self.set_value_from(self.get_current_value())
        if self.frame < self.length:
            pyglet.clock.schedule_once(self.advance_frame, 1/60.0)
        else:
            self.widget.dispatch_event('on_animation_complete', self)

    def get_value_from(self):
        if hasattr(self.widget, self.prop):
            return self.widget.__getattribute__(self.prop)
        return self.widget.__dict__[self.prop]

    def set_value_from(self, value):
        if hasattr(self.widget, self.prop):
            self.widget.__setattr__(self.prop, value)
        else:
            self.widget.__dict__[self.prop] = value

