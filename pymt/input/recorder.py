import pickle
import pymt
from time import time
from provider import TouchProvider
from pymt.clock import getClock
from pymt.base import pymt_providers

__all__ = ('pymt_touch_record', 'TouchReplay')

class TouchRecord(object):
    def __init__(self):
        super(TouchRecord, self).__init__()
        self.started = False
        self.filename = None
        self.starttime = 0
        self.touches = []

    def append(self, touch_instance):
        self.touches.append(touch_instance)

    def save(self):
        out = []
        for x in self.touches:
            out.append([
                x.__class__.__name__,
                x.device,
                x.id,
                x.record
            ])

        with open(self.filename, 'wb') as fd:
            pickle.dump((self.starttime, out), fd)

    def start(self, filename):
        self.touches = []
        self.started = True
        self.starttime = time()
        self.filename = filename

    def stop(self):
        self.started = False

pymt_touch_record = TouchRecord()


class TouchReplay(TouchProvider):
    def __init__(self, filename):
        super(TouchReplay, self).__init__('touchreplay', [])
        self.filename = filename
        self.started = False
        self.starttime = 0
        self.datatime = 0
        self.data = []
        self.instances = {}

    def start(self):
        self.started = True
        with open(self.filename, 'r') as fd:
            self.datatime, self.data = pickle.load(fd)
        self.starttime = time()
        self.instances = {}
        pymt_providers.append(self)

    def stop(self):
        self.started = False
        pymt_providers.remove(self)

    def update(self, dispatch_fn):
        if not self.started:
            return

        datatime = self.datatime
        curtime = time() - self.starttime

        deletelist = []

        for record in self.data:
            cls, device, id, records = record
            eventtype = 'move'
            if not records:
                deletelist.append(record)
                return
            if len(records) == 1:
                eventtype = 'up'
            record_time, record_args = records[0]
            if (record_time - datatime) < curtime:
                cid = (cls, device, id)
                if not cid in self.instances:
                    eventtype = 'down'
                    records.pop(0)
                    instance = getattr(pymt, cls)(device, id, record_args)
                    self.instances[cid] = instance
                else:
                    instance = self.instances[cid]
                    records.pop(0)
                    instance.depack(record_args)
                dispatch_fn(eventtype, instance)

                if eventtype == 'up':
                    deletelist.append(record)

        for x in deletelist:
            if x in self.data:
                self.data.remove(x)

        if not self.data:
            self.stop()
