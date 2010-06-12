__all__ = ('pymt_touch_network', )

import os
from pymt.lib.osc.oscAPI import sendMsg, init, listen, bind, readQueue
from pymt.clock import getClock
from pprint import pprint

init()

class TouchNetworkManager(object):
    def __init__(self, **kwargs):
        super(TouchNetworkManager, self).__init__()
        self.mode = kwargs.get('mode', 'master')
        self.ip = kwargs.get('ip', '127.0.0.1')
        self.port = kwargs.get('port', 7968)
        self.clients = []

        if self.mode == 'master':
            self.osc_server = listen(self.ip, self.port)
            bind(self.osc_server, '/pymt/touch', self.master_receive)
            getClock().schedule_interval(self.master_update, 0)

    def slave_send(self, event_type, touch):
        sendMsg('/pymt/touch',
                [event_type, touch.__class__.__name__, touch.last_args],
                self.ip, self.port)
        print 'INPUT', event_type, touch.last_args


    def master_send(self, event_type, touch):
        sendMsg('/pymt/touch',
                [event_type, touch.__class__.__name__, touch.last_args],
                self.ip, self.port)

    def master_receive(self, event_type, touch):
        print event_type, touch

    def master_update(self, *largs):
        readQueue(self.osc_server)


if 'SLAVE' in os.environ:
    pymt_touch_network = TouchNetworkManager(mode='slave', ip='192.168.0.139')
else:
    pymt_touch_network = TouchNetworkManager(mode='master')
    pymt_touch_network.clients.append(('192.168.0.193', 7968))
