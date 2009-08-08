__all__ = ['GestrTouchProvider']

import osc
from collections import deque
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ..shape import TouchShapeRect
from ...logger import pymt_logger

class GestrTouchProvider(TouchProvider):

    __handlers__ = {}

    def __init__(self, args):
        super(GestrTouchProvider, self).__init__(args)
        args = args.split(',')
        if len(args) <= 0:
            pymt_logger.error('Invalid configuration for TUIO provider')
            pymt_logger.error('Format must be ip:port (eg. 127.0.0.1:3333)')
            pymt_logger.error('Actual TUIO configuration is <%s>' % (str(','.join(args))))
            return None
        ipport = args[0].split(':')
        if len(ipport) != 2:
            pymt_logger.error('Invalid configuration for TUIO provider')
            pymt_logger.error('Format must be ip:port (eg. 127.0.0.1:3333)')
            pymt_logger.error('Actual TUIO configuration is <%s>' % (str(','.join(args))))
            return None
        self.ip, self.port = args[0].split(':')
        self.port = int(self.port)
        self.handlers = {}
        self.oscid = None
        self.tuio_event_q = deque()
        self.touches = {}

    @staticmethod
    def register(oscpath, classname):
        GestrTouchProvider.__handlers__[oscpath] = classname

    @staticmethod
    def unregister(oscpath, classname):
        if oscpath in GestrTouchProvider.__handlers__:
            del GestrTouchProvider.__handlers__[oscpath]

    @staticmethod
    def create(oscpath, **kwargs):
        if oscpath not in GestrTouchProvider.__handlers__:
            raise Exception('Unknown %s touch path' % oscpath)
        return GestrTouchProvider.__handlers__[oscpath](**kwargs)

    def start(self):
        osc.init()
        self.oscid = osc.listen(self.ip, self.port)
        for oscpath in GestrTouchProvider.__handlers__:
            self.touches[oscpath] = {}
            osc.bind(self.osc_tuio_cb, oscpath)

    def stop(self):
        osc.dontListen(self.oscid)

    def osc_tuio_cb(self, *incoming):
        message = incoming[0]
        oscpath, types, args = message[0], message[1], message[2:]
        self.tuio_event_q.appendleft([oscpath, args, types])

    def update(self, dispatch_fn):
        # read the Queue with event
        try:
            while True:
                value = self.tuio_event_q.pop()
                self._update(dispatch_fn, value)
        except IndexError:
            return

    def _update(self, dispatch_fn, value):
        oscpath, args, types = value
        command = args[0]

        # verify commands
        if command not in ['alive', 'set', 'recognized']: # More actions coming soon. Ex: Parameter updates after recognition
            return
        
        if command == 'recognized':
            gestureArgs = args[1:] #args[1] is the name, followed by x,y coords
            pymt_logger.info("Gesture Recognized: ", args[1:])
            dispatch_fn('gestr_recognized', gestureArgs)

        # move or create a new touch
        if command == 'set':
            id = args[1]
            if id not in self.touches[oscpath]:
                # new touch
                touch = GestrTouchProvider.__handlers__[oscpath](id, args[2:])
                self.touches[oscpath][id] = touch
                dispatch_fn('down', touch)
            else:
                # update a current touch
                touch = self.touches[oscpath][id]
                touch.move(args[2:])
                dispatch_fn('move', touch)

        # alive event, check for deleted touch
        if command == 'alive':
            alives = args[1:]
            to_delete = []
            for id in self.touches[oscpath]:
                if not id in alives:
                    # touch up
                    touch = self.touches[oscpath][id]
                    if not touch in to_delete:
                        to_delete.append(touch)

            for touch in to_delete:
                dispatch_fn('up', touch)
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
        super(Tuio2dCurTouch, self).depack(args)


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
        super(Tuio2dObjTouch, self).depack(args)

class MGestr(Touch):
    def __init__(self, id, args):
        super(MGestr, self).__init__(id, args)
        print("MGestr Started")

    def depack(self, args):
        print("Received event")
        if len(args) > 0:
            if args(0) == "recognized":
                self.action = args[1]
                self.rx, self.ry = args[2:2]
                pymt_logger.info("Recognized", args[1:])
                self.profile = 'Sxy'
        super(MGestr, self).depack(args)

# registers
GestrTouchProvider.register('/tuio/2Dcur', Tuio2dCurTouch)
GestrTouchProvider.register('/tuio/2Dobj', Tuio2dObjTouch)
GestrTouchProvider.register('/gestr/action', MGestr)

TouchFactory.register('mgestr', GestrTouchProvider)
