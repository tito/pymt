__all__ = ["Tuio2TouchProvider", "Tuio2Touch"]

from collections import deque
import osc
from pymt.input.provider import TouchProvider
from pymt.input.factory import TouchFactory
from pymt.input.touch import Touch
from pymt.input.shape import TouchShapeRect


class Tuio2TouchProvider(TouchProvider):
    def __init__(self, device, args):
        super(Tuio2TouchProvider, self).__init__(device, args)
        args = args.split(',')
        if len(args) <= 0:
            pymt_logger.error('Tuio: Invalid configuration for TUIO2 provider')
            pymt_logger.error('Tuio: Format must be ip:port (eg. 127.0.0.1:3333)')
            pymt_logger.error('Tuio: Actual TUIO2 configuration is <%s>' % (str(','.join(args))))
            return None
        ipport = args[0].split(':')
        if len(ipport) != 2:
            pymt_logger.error('Tuio: Invalid configuration for TUIO2 provider')
            pymt_logger.error('Tuio: Format must be ip:port (eg. 127.0.0.1:3333)')
            pymt_logger.error('Tuio: Actual TUIO2 configuration is <%s>' % (str(','.join(args))))
            return None
        self.ip, self.port = args[0].split(':')
        self.port = int(self.port)
        self.oscid = None
        self.tuio_event_q = deque()
        self.touches = {}
        self.last_frame_id = -1

    def start(self):
        '''Start the tuio provider'''
        self.oscid = osc.listen(self.ip, self.port)
        for command in ('alv', 'ptr', 'frm', 'ala', 'coa'):
            oscpath = '/tuio2/%s' % (command, )
            osc.bind(self.oscid, self._osc_tuio_cb, oscpath)

    def stop(self):
        '''Stop the tuio provider'''
        osc.dontListen(self.oscid)

    def update(self, dispatch_fn):
        '''Update the tuio provider (pop event from the queue)'''

        # deque osc queue
        osc.readQueue(self.oscid)

        # read the Queue with event
        while True:
            try:
                value = self.tuio_event_q.pop()
            except IndexError:
                # queue is empty, we're done for now
                return
            self._update(dispatch_fn, value)

    def _osc_tuio_cb(self, *incoming):
        message = incoming[0]
        oscpath, types, args = message[0], message[1], message[2:]
        self.tuio_event_q.appendleft([oscpath, args, types])

    def _update(self, dispatch_fn, value):
        oscpath, args, types = value
        tuio2, command = oscpath.rsplit("/")[1:]
        assert tuio2 == "tuio2"

        touches = self.touches
        if command == 'frm':
            current_frame_id = int(args[0])
            if current_frame_id < self.last_frame_id:
                # A bundle that is older than the last one we processed
                # just arrived. Discard it.
                return
            self.last_frame_id = current_frame_id
        elif command == 'alv':
            # Check if we need to remove any touches
            for s_id in touches.keys()[:]:
                if s_id not in args:
                    dispatch_fn('up', touches[s_id])
                    del touches[s_id]
        elif command == 'ala':
            for s_id in touches.keys():
                if s_id not in args:
                    touch = touches[s_id]
                    touch.elements = None
                    touch.container = None
                    touch.profile = tuple([p for p in touch.profile if p != 'container'])
        else:
            # Update the existing touch, or create a new, empty touch and
            # update it (for the first time).
            s_id = args[0]
            new_touch = False
            touch = touches.get(s_id)
            if not touch:
                new_touch = True
                # No need to pass args here. Will be set by dispatch target
                touch = Tuio2Touch(self.device, s_id)
                self.touches[s_id] = touch
            try:
                getattr(touch, 'on_%s' % command)(self, args)
            except AttributeError:
                print 'TUIO2: Not implemented: %s' % (command, )
            if new_touch:
                dispatch_fn('down', touch)
            else:
                dispatch_fn('move', touch)


class Tuio2Touch(Touch):
    def __init__(self, device, id):
        # args intentionally left out.
        self.pressure = None
        self.width = None
        self.X = None
        self.Y = None
        self.m = None
        self.elements = None
        self.container = None
        super(Tuio2Touch, self).__init__(device, id, None)

    def on_ptr(self, provider, args):
        # s_id tu_id c_id x_pos y_pos width press [x_vel y_vel m_acc]
        s = self
        s.profile = ('pos', 'shape', 'pressure')
        s.id, tu_id, c_id, s.sx, sy, width, s.pressure = args[0:7]
        s.sy = 1 - sy
        # XXX tu_id?
        # XXX c_id?
        if len(args) == 10:
            s.profile += ('mov', 'motacc')
            s.X, s.Y, s.m = args[7:]
            s.Y = -s.Y
            self.m = m_acc
        if s.shape is None:
            s.shape = TouchShapeRect()
        # TUIO2 only gives us a width as diameter
        s.shape.width = s.shape.height = width
        super(Tuio2Touch, self).depack(None)

    def on_coa(self, provider, args):
        # s_id slot s_id0 ... s_idN
        # XXX slot?
        assert args[0] == self.id
        elements = args[2:]
        assert elements
        self.profile += ('container', )
        self.elements = [provider.touches[e] for e in elements]
        for e in self.elements:
            e.container = self

    # TODO implement rest of the protocol...


TouchFactory.register('tuio2', Tuio2TouchProvider)
