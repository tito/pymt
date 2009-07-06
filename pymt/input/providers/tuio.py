__all__ = ['TuioTouchProvider']

import osc
from Queue import Queue
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ..shape import TouchShapeRect
from ...logger import pymt_logger

class TuioTouchProvider(TouchProvider):

    __handlers__ = {}

    def __init__(self, **kwargs):
        super(TuioTouchProvider, self).__init__()
        kwargs.setdefault('ip', '127.0.0.1')
        kwargs.setdefault('port', '9001')
        self.ip = kwargs.get('ip')
        self.port = kwargs.get('port')
        self.handlers = {}
        self.oscid = None
        self.tuio_event_q = Queue()
        self.touches = {}

    @staticmethod
    def register(oscpath, classname):
        TuioTouchProvider.__handlers__[oscpath] = classname

    @staticmethod
    def unregister(oscpath, classname):
        if oscpath in TuioTouchProvider.__handlers__:
            del TuioTouchProvider.__handlers__[oscpath]

    @staticmethod
    def create(oscpath, **kwargs):
        if oscpath not in TuioTouchProvider.__handlers__:
            raise Exception('Unknown %s touch path' % oscpath)
        return TuioTouchProvider.__handlers__[oscpath](**kwargs)

    def start(self):
        osc.init()
        pymt_logger.info('Listening to %s:%s' % (self.ip, self.port))
        self.oscid = osc.listen(self.ip, self.port)
        for oscpath in TuioTouchProvider.__handlers__:
            self.touches[oscpath] = {}
            osc.bind(self.osc_tuio_cb, oscpath)

    def stop(self):
        pymt_logger.info('Stop listening to %s:%s' % (self.ip, self.port))
        osc.dontListen(self.oscid)

    def osc_tuio_cb(self, *incoming):
        message = incoming[0]
        oscpath, types, args = message[0], message[1], message[2:]
        self.tuio_event_q.put([oscpath, args, types])

    def update(self, dispatch_fn):
        # read the Queue with event
        while not self.tuio_event_q.empty():
            oscpath, args, types = self.tuio_event_q.get()
            command = args[0]

            # verify commands
            if command not in ['alive', 'set']:
                return

            # move or create a new touch
            if command == 'set':
                id = args[1]
                if id not in self.touches[oscpath]:
                    # new touch
                    touch = TuioTouchProvider.__handlers__[oscpath](id, args[2:])
                    self.touches[oscpath][id] = touch
                    dispatch_fn(touch)
                else:
                    # update a current touch
                    touch = self.touches[oscpath][id]
                    touch.type = Touch.MOVE
                    touch.move(args[2:])
                    dispatch_fn(touch)

            # alive event, check for deleted touch
            if command == 'alive':
                alives = args[1:]
                to_delete = []
                for id in self.touches[oscpath]:
                    if not id in alives:
                        # touch up
                        touch = self.touches[oscpath][id]
                        if not touch in to_delete:
                            touch.type = Touch.UP
                            to_delete.append(touch)

                for touch in to_delete:
                    dispatch_fn(touch)
                    del self.touches[oscpath][touch.id]

class Tuio2dCurTouch(Touch):
    def __init__(self, id, args):
        super(Tuio2dCurTouch, self).__init__(id, args)

    def depack(self, args):
        if len(args) < 5:
            self.sx, self.sy = map(float, args[0:2])
            self.profile = 'xy'
        elif len(args) == 5:
            self.sx, self.sy, self.X, self.Y, self.m = map(float, args[0:5])
            self.profile = 'xyXYm'
        else:
            self.sx, self.sy, self.X, self.Y, self.m, width, height = map(float, args[0:7])
            self.profile = 'xyXYmh'
            if self.shape is None:
                self.shape = TouchShapeRect()
                self.shape.width = width
                self.shape.height = height
        self.sy = 1 - self.sy
        if self.oxpos is None:
            self.oxpos, self.oypos = self.x, self.y
            self.dxpos, self.dypos = self.x, self.y


class Tuio2dObjTouch(Touch):
    def __init__(self, id, args):
        super(Tuio2dObjTouch, self).__init__(id, args)

    def depack(self, args):
        if len(args) < 5:
            self.sx, self.sy = args[0:2]
            self.profile = 'xy'
        elif len(args) == 9:
            self.id, self.sx, self.sy, self.a, self.X, self.Y, self.A, self.m, self.r = args[0:9]
            self.profile = 'ixyaXYAmr'
        else:
            self.id, self.sx, self.sy, self.a, self.X, self.Y, self.A, self.m, self.r, width, height = args[0:11]
            self.profile = 'ixyaXYAmrh'
            if self.shape is None:
                self.shape = TouchShapeRect()
                self.shape.width = width
                self.shape.height = height
        self.sy = 1 - self.sy

# registers
TuioTouchProvider.register('/tuio/2Dcur', Tuio2dCurTouch)
TuioTouchProvider.register('/tuio/2Dobj', Tuio2dObjTouch)
TouchFactory.register('tuio', TuioTouchProvider)
