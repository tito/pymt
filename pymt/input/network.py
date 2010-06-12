__all__ = ('pymt_touch_network', )

from pymt.lib.osc.oscAPI import sendMsg, init listen, bind, readQueue
from pprint import pprint

init()

class TouchNetworkManager(object):
    def __init__(self, **kwargs):
        super(TouchNetworkManager, self).__init__()
        self.mode = kwargs.get('mode', 'master')
        self.ip = kwargs.get('ip', '127.0.0.1')
        self.port = kwargs.get('port', 7968)


        self.osc_server = listen("0.0.0.0", 7968)
        bind(self.osc.server, "/pymt/event/send", pprint)


    def dispatch_input(self, event_type, touch):
        sendMsg('/pymt/event/send',
                [event_type, touch.__class__.__name__, touch.last_args],
                self.ip, self.port)
        print 'INPUT', event_type, touch.last_args


    def broadcast_input(self, event_type, touch):
        readQueue(self.osc_server)
        sendMsg('/pymt/event/receive',
                [event_type, touch.__class__.__name__, touch.last_args],
                self.ip, self.port)
#send touch

pymt_touch_network = TouchNetworkManager(mode='master', ip='192.168.0.193')
