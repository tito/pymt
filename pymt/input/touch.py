__all__ = ['Touch']

import pyglet
from ..logger import pymt_logger

touch_clock = pyglet.clock.Clock()

class Touch(object):
    DOWN = 0
    MOVE = 1
    UP   = 2

    def __init__(self, id, args):
        if self.__class__ == Touch:
            raise NotImplementedError, 'class Touch is abstract'

        self.type = Touch.DOWN

        # TUIO definition
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.m = 0.0
        self.r = 0.0
        self.profile = 'ixyzabcXYZABCmrh'

        # new parameters
        self.shape = None
        self.dxpos = None
        self.dypos = None
        self.dzpos = None
        self.oxpos = None
        self.oypos = None
        self.ozpos = None
        self.time_start = touch_clock.time()
        self.is_timeout = False
        self.have_event_down = False
        self.do_event = None
        self.is_double_tap = False
        self.double_tap_time = 0
        self.no_event = False
        self.depack(args)

    def depack(self, args):
        pass

    def move(self, args):
        self.dxpos, self.dypos = self.x, self.y
        self.depack(args)

    def __str__(self):
        return str(self.__class__)

    # facility
    pos = property(lambda self: (self.x, self.y))
    dpos = property(lambda self: (self.dxpos, self.dypos))
    opos = property(lambda self: (self.oxpos, self.oypos))

    # compatibility bridge
    xpos = property(lambda self: self.x)
    ypos = property(lambda self: self.y)
    blobID = property(lambda self: self.id)
    xmot = property(lambda self: self.X)
    ymot = property(lambda self: self.Y)
    zmot = property(lambda self: self.Z)
    mot_accel = property(lambda self: self.m)
    rot_accel = property(lambda self: self.r)
    angle = property(lambda self: self.a)

