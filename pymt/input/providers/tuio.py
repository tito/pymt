'''
Tuio: TUIO input provider implementation
'''

__all__ = ['TuioTouchProvider', 'Tuio2dCurTouch', 'Tuio2dObjTouch']

import osc
from collections import deque
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ..shape import TouchShapeRect
from ...logger import pymt_logger

class TuioTouchProvider(TouchProvider):
    '''Tuio provider listen to a socket, and handle part of OSC message

        * /tuio/2Dcur
        * /tuio/2Dobj

    Tuio provider can be configured with the `[`input`]` configuration ::

        [input]
        # name = tuio,<ip>:<port>
        multitouchtable = tuio,192.168.0.1:3333

    You can easily handle new tuio path by extending the providers like this ::

        # Create a class to handle the new touch type
        class TuioNEWPATHTouch(Touch):
            def __init__(self, id, args):
                super(TuioNEWPATHTouch, self).__init__(id, args)

            def depack(self, args):
                # Write here the depack function of args.
                # for a simple x, y, value, you can do this :
                if len(args) == 2:
                    self.sx, self.sy = args
                    self.profile = ('pos', )
                self.sy = 1 - self.sy
                super(TuioNEWPATHTouch, self).depack(args)

        # Register it to tuio touch provider
        TuioTouchProvider.register('/tuio/NEWPATH', TuioNEWPATHTouch)
    '''

    __handlers__ = {}

    def __init__(self, args):
        super(TuioTouchProvider, self).__init__(args)
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
        '''Register a new path to handle in tuio provider'''
        TuioTouchProvider.__handlers__[oscpath] = classname

    @staticmethod
    def unregister(oscpath, classname):
        '''Unregister a new path to handle in tuio provider'''
        if oscpath in TuioTouchProvider.__handlers__:
            del TuioTouchProvider.__handlers__[oscpath]

    @staticmethod
    def create(oscpath, **kwargs):
        '''Create a touch from a tuio path'''
        if oscpath not in TuioTouchProvider.__handlers__:
            raise Exception('Unknown %s touch path' % oscpath)
        return TuioTouchProvider.__handlers__[oscpath](**kwargs)

    def start(self):
        '''Start the tuio provider'''
        osc.init()
        self.oscid = osc.listen(self.ip, self.port)
        for oscpath in TuioTouchProvider.__handlers__:
            self.touches[oscpath] = {}
            osc.bind(self._osc_tuio_cb, oscpath)

    def stop(self):
        '''Stop the tuio provider'''
        osc.dontListen(self.oscid)

    def update(self, dispatch_fn):
        '''Update the tuio provider (pop event from the queue)'''
        # read the Queue with event
        try:
            while True:
                value = self.tuio_event_q.pop()
                self._update(dispatch_fn, value)
        except IndexError:
            return

    def _osc_tuio_cb(self, *incoming):
        message = incoming[0]
        oscpath, types, args = message[0], message[1], message[2:]
        self.tuio_event_q.appendleft([oscpath, args, types])

    def _update(self, dispatch_fn, value):
        oscpath, args, types = value
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
    '''A 2dCur tuio touch.  Multiple profiles are available:

        * xy
        * xyXYm
        * xyXYmh
    '''
    def __init__(self, id, args):
        super(Tuio2dCurTouch, self).__init__(id, args)

    def depack(self, args):
        if len(args) < 5:
            self.sx, self.sy = map(float, args[0:2])
            self.profile = ('pos', )
        elif len(args) == 5:
            self.sx, self.sy, self.X, self.Y, self.m = map(float, args[0:5])
            self.profile = ('pos', 'mov', 'motacc')
        else:
            self.sx, self.sy, self.X, self.Y, self.m, width, height = map(float, args[0:7])
            self.profile = ('pos', 'mov', 'motacc', 'shape')
            if self.shape is None:
                self.shape = TouchShapeRect()
            self.shape.width = width
            self.shape.height = height
        self.sy = 1 - self.sy
        super(Tuio2dCurTouch, self).depack(args)


class Tuio2dObjTouch(Touch):
    '''A 2dObj tuio touch.  Multiple profiles are available:

        * xy
        * ixyaXYAmr
        * ixyaXYAmrh
    '''
    def __init__(self, id, args):
        super(Tuio2dObjTouch, self).__init__(id, args)

    def depack(self, args):
        if len(args) < 5:
            self.sx, self.sy = args[0:2]
            self.profile = ('pos', )
        elif len(args) == 9:
            self.fid, self.sx, self.sy, self.a, self.X, self.Y, self.A, self.m, self.r = args[0:9]
            self.profile = ('markerid', 'pos', 'angle', 'mov', 'rot', 'rotacc')
        else:
            self.fid, self.sx, self.sy, self.a, self.X, self.Y, self.A, self.m, self.r, width, height = args[0:11]
            self.profile = ('markerid', 'pos', 'angle', 'mov', 'rot', 'rotacc',
                           'shape')
            if self.shape is None:
                self.shape = TouchShapeRect()
                self.shape.width = width
                self.shape.height = height
        self.sy = 1 - self.sy
        super(Tuio2dObjTouch, self).depack(args)

# registers
TuioTouchProvider.register('/tuio/2Dcur', Tuio2dCurTouch)
TuioTouchProvider.register('/tuio/2Dobj', Tuio2dObjTouch)
TouchFactory.register('tuio', TuioTouchProvider)
