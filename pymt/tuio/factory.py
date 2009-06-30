'''
Tuio factory: register and dispatch creation of touch object from TUIO data
'''

__all__ = ['MTTouchFactory', 'MTTouchAbstract']

import pyglet
from ..logger import pymt_logger

touch_clock = pyglet.clock.Clock()

class MTTouchShapeRect(object):
    pass

class MTTouchAbstract(object):
    def __init__(self, id, args):

        if self.__class__ == MTTouchAbstract:
            raise NotImplementedError, 'class MTTouchAbstract is abstract'

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

    # facility
    pos = property(lambda: (self.x, self.y))
    dpos = property(lambda: (self.dxpos, self.dypos))
    opos = property(lambda: (self.oxpos, self.oypos))

    # compatibility bridge
    xpos = property(lambda: self.x)
    ypos = property(lambda: self.y)
    blobID = property(lambda: self.id)
    xmot = property(lambda: self.X)
    ymot = property(lambda: self.Y)
    zmot = property(lambda: self.Z)
    mot_accel = property(lambda: self.m)
    rot_accel = property(lambda: self.r)
    angle = property(lambda: self.a)


class MTTouchFactory:
    '''TUIO Touch factory. You can create new TUIO handler, and create new touch object.'''

    _class = {}

    @staticmethod
    def register(type, touchclass):
        '''Register a new type / touchclass ::

            MTTouchFactory.register('/tuio/2DCur', MTTouch2dCur)

        :Parameters:
            `type` : str
                This is the type of TUIO message (eg: /tuio/2DCur)
            `touchclass` : class
                Touch class to instanciate
        '''
        MTTouchFactory._class[type] = touchclass

    @staticmethod
    def create(type, id, args):
        '''Create a new touch from a type ::

            touchobject = MTTouchFactory.create('/tuio/2DCur', '25', args)
        
        :Parameters:
            `type` : str
                Type of TUIO message
            `id` : str
                Id of the touch
            `args` : list
                Touch Arguments
        '''
        if type in MTTouchFactory._class:
            return MTTouchFactory._class(id, args)
        pymt_logger.warning('Unhandled <%s> type in MTTouchFactory' % id)


