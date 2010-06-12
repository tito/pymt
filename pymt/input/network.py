__all__ = ('pymt_touch_network', )

from pymt.lib.osc.oscAPI import sendMsg, init

init()

class TouchNetworkManager(object):
    def __init__(self, **kwargs):
        super(TouchNetworkManager, self).__init__()
        self.mode = kwargs.get('mode', 'master')
        self.ip = kwargs.get('ip', '127.0.0.1')
        self.port = kwargs.get('port', 7968)

    def dispatch_input(self, event_type, touch):
        sendMsg('/pymt/event/send',
                [event_type, touch.__class__.__name__, touch.last_args],
                self.ip, self.port)
        print 'INPUT', event_type, touch.last_args

pymt_touch_network = TouchNetworkManager(mode='slave', ip='192.168.0.193')
