'''
XI2TouchProvider: Native support of Xorg XInputExtension
'''

__all__ = ('XI2TouchProvider', )

import os
import collections
import threading
from ..provider import TouchProvider
from ..factory import TouchFactory
from ..touch import Touch
from ..shape import TouchShapeRect

if 'PYMT_DOC' not in os.environ:
    from Xlib import X, display, Xutil
    from Xlib.protocol import rq, structs
    import _xi2 as xi2

_instance = None

class XI2Touch(Touch):
    '''Touch representing a contact point on touchpad. Support pos profile'''
    def depack(self, args):
        #self.shape = TouchShapeRect()
        self.sx, self.sy = args[0], args[1]
        #self.shape.width = args[2]
        #self.shape.height = args[2]
        #self.profile = ('pos', 'shape')
        self.profile = ('pos', )
        super(XI2Touch, self).depack(args)

    def __str__(self):
        return '<XI2Touch id=%d pos=(%f, %f) device=%s>' % (self.id, self.sx, self.sy, self.device)


class XI2TouchProvider(TouchProvider):
    def __init__(self, *largs, **kwargs):
        global _instance
        if _instance is not None:
            raise Exception('Only one XI2Touch provider is allowed.')
        _instance = self
        super(XI2TouchProvider, self).__init__(*largs, **kwargs)

    def start(self):
        self.queue = collections.deque()
        self.uid = 0
        self.thread = threading.Thread(target=self._thread_run,
                                       args=(self.queue, ))
        self.thread.daemon = True
        self.thread.start()

    def update(self, dispatch_fn):
        # dispatch all event from threads
        try:
            while True:
                event_type, touch = self.queue.popleft()
                dispatch_fn(event_type, touch)
        except:
            pass

    def stop(self):
        pass

    def _thread_run(self, *largs, **kwargs):
        queue, = largs
        disp = display.Display()
        xi2.setup(disp)

        print '=== SETUP XI2 ==='
        prop_multitouch = disp.get_atom('Evdev MultiTouch')
        print 'Atom Multitouch = ', prop_multitouch

        version = disp.xi2_query_version()
        print 'Version = %d.%d' % (version.major_version, version.minor_version)
        devices = disp.xi2_query_device(xi2.XIAllDevices)
        print 'Number of devices = %d' % len(devices.devices)

        root = disp.screen().root
        print 'Root =', root.id

        for device in devices.devices:
            props = disp.xi2_list_properties(device.device_id)
            print ''
            print '*', device.name
            print device
            for cls in device.classes:
                print 'cls', cls
            for x in props.properties:
                print ' \-', disp.get_atom_name(x)

            if prop_multitouch not in props.properties:
                continue

            print '-> Enable multitouch'

            mask = rq.DictWrapper({})
            mask.device_id = xi2.XIAllDevices #device.device_id
            mask.mask = [0,0]
            xi2.XISetMask(mask.mask, xi2.XI_Motion)
            print mask.mask

            disp.flush()
            print root.xi2_grab_device(device_id=device.device_id, masks=[mask])
            #print root.xi2_ungrab_device(device_id=device.device_id)

        print 'Starting loop...'
        disp.flush()
        mt = rq.Struct(
            xi2.Card64('x'),
            xi2.Card64('y'),
            xi2.Card64('sx'),
            xi2.Card64('sy'),
            rq.Pad(24),
            rq.Int32('id'),
            rq.Int32('_1'),
            rq.Int32('_2'),
            rq.Int32('_3'),
            rq.Int32('use'),
            rq.Int32('_5'),
        )

        touches = {}
        while 1:
            ev = root.display.next_event()
            d = ev.data[8:]

            v, d = mt.parse_binary(d, disp.display)
            args = (float(v.x) / 2048., float(v.y) / 2048.)

            try:
                touch = touches[ev.device_id]
                # if id is -1, it's a removed touch
                if v.id == -1:
                    queue.append(('up', touch))
                    del touches[ev.device_id]
                else:
                    x, y = args
                    if touch.sx == x and touch.sy == y:
                        continue
                    touch.move(args)
                    queue.append(('move', touch))
                continue
            except KeyError:
                self.uid += 1
                touch = XI2Touch(self.device, self.uid, args)
                touches[ev.device_id] = touch
                queue.append(('down', touch))
                continue

TouchFactory.register('xi2', XI2TouchProvider)
