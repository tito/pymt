'''
HIDInput: Native support of HID input from linux kernel

Support start from 2.6.32-ubuntu, or 2.6.34.

To configure HIDInput, put in your configuration ::

    [input]
    # devicename = hidinput,/dev/input/eventXX
    # example with Stantum MTP4.3" screen
    stantum = hidinput,/dev/input/event2

You must have read access to the input event.

TODO:
* read name of device, and show it in log
* read descriptor of device, and get min/max of X/Y value
'''

__all__ = ('HIDInputTouchProvider', 'HIDTouch')

import os
from ..touch import Touch

class HIDTouch(Touch):
    def depack(self, args):
        self.sx = args['x']
        self.sy = args['y']
        self.profile = ('pos', )
        super(HIDTouch, self).depack(args)

    def __str__(self):
        return '<HIDTouch id=%d pos=(%f, %f) device=%s>' % (self.id, self.sx, self.sy, self.device)

if 'PYMT_DOC' in os.environ:
    # documentation hack
    HIDInputTouchProvider = None

else:
    import threading
    import collections
    import struct
    import sys
    from ..provider import TouchProvider
    from ..factory import TouchFactory
    from ...logger import pymt_logger

    #
    # This part is taken from linux-source-2.6.32/include/linux/input.h
    #

    # Event types
    EV_SYN		    = 0x00
    EV_KEY		    = 0x01
    EV_REL		    = 0x02
    EV_ABS		    = 0x03
    EV_MSC		    = 0x04
    EV_SW		    = 0x05
    EV_LED		    = 0x11
    EV_SND		    = 0x12
    EV_REP		    = 0x14
    EV_FF		    = 0x15
    EV_PWR		    = 0x16
    EV_FF_STATUS    = 0x17
    EV_MAX		    = 0x1f
    EV_CNT		    = (EV_MAX+1)

    # Synchronization events
    SYN_REPORT		= 0
    SYN_CONFIG		= 1
    SYN_MT_REPORT	= 2

    # Misc events
    MSC_SERIAL	    = 0x00
    MSC_PULSELED    = 0x01
    MSC_GESTURE	    = 0x02
    MSC_RAW		    = 0x03
    MSC_SCAN	    = 0x04
    MSC_MAX		    = 0x07
    MSC_CNT		    = (MSC_MAX+1)

    ABS_MT_TOUCH_MAJOR  = 0x30	# Major axis of touching ellipse
    ABS_MT_TOUCH_MINOR  = 0x31	# Minor axis (omit if circular)
    ABS_MT_WIDTH_MAJOR  = 0x32	# Major axis of approaching ellipse
    ABS_MT_WIDTH_MINOR  = 0x33	# Minor axis (omit if circular)
    ABS_MT_ORIENTATION  = 0x34	# Ellipse orientation
    ABS_MT_POSITION_X   = 0x35	# Center X ellipse position
    ABS_MT_POSITION_Y   = 0x36	# Center Y ellipse position
    ABS_MT_TOOL_TYPE    = 0x37	# Type of touching device
    ABS_MT_BLOB_ID	    = 0x38	# Group a set of packets as a blob
    ABS_MT_TRACKING_ID  = 0x39	# Unique ID of initiated contact
    ABS_MT_PRESSURE		= 0x3a	# Pressure on contact area

    # sizeof(struct input_event)
    struct_input_event_sz = 24

    class HIDInputTouchProvider(TouchProvider):
        def __init__(self, device, args):
            super(HIDInputTouchProvider, self).__init__(device, args)
            self.input_fn = None
            if args == '':
                pymt_logger.error('HIDInput: No filename pass to HIDInput configuration')
                pymt_logger.error('HIDInput: Use /dev/input/event0 for example')
                return None
            else:
                pymt_logger.info('HIDInput: Read event from <%s>' % args)
                self.input_fn = args

        def start(self):
            if self.input_fn is None:
                return
            self.uid = 0
            self.queue = collections.deque()
            self.thread = threading.Thread(
                target=self._thread_run, kwargs={
                'queue': self.queue,
                'input_fn': self.input_fn,
                'device': self.device})
            self.thread.daemon = True
            self.thread.start()

        def _thread_run(self, **kwargs):
            input_fn = kwargs.get('input_fn')
            queue = kwargs.get('queue')
            device = kwargs.get('device')
            touches = {}
            touches_sent = []
            point = {}
            l_points = []

            def process(points):
                actives = [args['id'] for args in points]
                for args in points:
                    tid = args['id']
                    try:
                        touch = touches[tid]
                        if touch.sx == args['x'] and touch.sy == args['y']:
                            continue
                        touch.move(args)
                        if tid not in touches_sent:
                            queue.append(('down', touch))
                            touches_sent.append(tid)
                        queue.append(('move', touch))
                    except KeyError:
                        touch = HIDTouch(device, tid, args)
                        touches[touch.id] = touch

                for tid in touches.keys():
                    if tid not in actives:
                        touch = touches[tid]
                        if tid in touches_sent:
                            queue.append(('up', touch))
                            touches_sent.remove(tid)
                        del touches[tid]

            # open the input
            fd = open(input_fn, 'rb')

            # read until the end
            while fd:

                data = fd.read(struct_input_event_sz)
                if len(data) < struct_input_event_sz:
                    break

                # extract each event
                for i in xrange(len(data) / struct_input_event_sz):
                    ev = data[i * struct_input_event_sz:]

                    # extract timeval + event infos
                    tv_sec, tv_usec, ev_type, ev_code, ev_value = \
                            struct.unpack('LLHHi', ev[:struct_input_event_sz])

                    # sync event
                    if ev_type == EV_SYN:
                        if ev_code == SYN_MT_REPORT:
                            if 'id' not in point:
                                continue
                            l_points.append(point)
                        elif ev_code == SYN_REPORT:
                            process(l_points)
                            l_points = []

                    elif ev_type == EV_MSC and ev_code in (MSC_RAW, MSC_SCAN):
                        pass

                    else:
                        # compute multitouch track
                        if ev_code == ABS_MT_TRACKING_ID:
                            point = {}
                            point['id'] = ev_value
                        elif ev_code == ABS_MT_POSITION_X:
                            point['x'] = ev_value / 2048.
                        elif ev_code == ABS_MT_POSITION_Y:
                            point['y'] = (1. - ev_value / 2048.)
                        elif ev_code == ABS_MT_ORIENTATION:
                            point['orientation'] = ev_value
                        elif ev_code == ABS_MT_BLOB_ID:
                            point['blobid'] = ev_value
                        elif ev_code == ABS_MT_PRESSURE:
                            point['pressure'] = ev_value

        def update(self, dispatch_fn):
            # dispatch all event from threads
            try:
                while True:
                    event_type, touch = self.queue.popleft()
                    dispatch_fn(event_type, touch)
            except:
                pass


    TouchFactory.register('hidinput', HIDInputTouchProvider)
