__all__ = ('pymt_touch_network', )

import os
import pymt
from pymt.lib.osc.oscAPI import sendMsg, init, listen, bind, readQueue
from pymt.clock import getClock

init()

class TouchNetworkManager(object):
    def __init__(self, **kwargs):
        super(TouchNetworkManager, self).__init__()
        self.mode = kwargs.get('mode', 'master')
        self.ip = kwargs.get('ip', '0.0.0.0')
        self.port = kwargs.get('port', 7968)
        self.clients = []
        self.touches = {}

        if self.mode == 'master':
            self.osc_server = listen(self.ip, self.port)
            bind(self.osc_server, self.master_receive, '/pymt/touch')
            getClock().schedule_interval(self.master_update, 0)

    def slave_send(self, event_type, touch):
        sendMsg('/pymt/touch',
                [event_type, touch.__class__.__name__, touch.device, touch.id] + touch.last_args,
                self.ip, self.port)
        print 'INPUT', event_type, touch.last_args


    def master_send(self, event_type, touch):
        sendMsg('/pymt/touch',
                [event_type, touch.__class__.__name__, touch.device, touch.id] + touch.last_args,
                self.ip, self.port)

    def master_receive(self, data, *largs):
        event_type, class_name, device, id = data[2:6]
        args = data[6:]
        print 'RAW', data
        print event_type, args

        cid = (class_name, device, id) # FIXME add ip/port of client
        if event_type == 'down':
            touch = getattr(pymt, class_name)(device, id, args)
            self.touches[cid] = touch
        else:
            touch = self.touches[cid]
            touch.depack(args)

        # dispatch
        pymt.getEventLoop().proxy_dispatch_input(event_type, touch)

        if event_type == 'up':
            del self.touches[cid]

    def master_update(self, *largs):
        readQueue(self.osc_server)


if 'SLAVE' in os.environ:
    pymt_touch_network = TouchNetworkManager(mode='slave', ip='192.168.0.139')
else:
    pymt_touch_network = TouchNetworkManager(mode='master')
    pymt_touch_network.clients.append(('192.168.0.193', 7968))
