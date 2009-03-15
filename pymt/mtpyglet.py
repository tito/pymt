'''
Soup on pyglet to provide multitouch interface.
'''

__all__ = [
    'Tuio2DCursor', 'Tuio2DObject', 'TouchEventLoop', 'TouchWindow',
    'pymt_usage', 'runTouchApp', 'stopTouchApp',
    'startTuio', 'stopTuio',
]

import osc
import pyglet
import pymt
import sys, getopt, os
from logger import pymt_logger
from pyglet.gl import *
from Queue import Queue
from threading import Lock
from utils import intersection, difference, strtotuple


# All event listeners will add themselves to this
# list upon creation
tuio_event_q = Queue()
tuio_listeners = []
touch_event_listeners = []

class Tuio2DCursor(object):
    '''Represent a Tuio cursor + implementation of double-tap functionnality
    '''
    def __init__(self, blobID, args, time_start=0):
        self.blobID = blobID
        self.dxpos = self.dypos = None
        self.oxpos = self.oypos = 0.0
        self.time_start = time_start
        self.is_timeout = False
        self.have_event_down = False
        self.do_event = None
        self.is_double_tap = False
        self.double_tap_time = 0
        self.no_event = False
        self.depack(args)
        self.motcalc()

    def move(self, args):
        self.oxpos, self.oypos = self.xpos, self.ypos
        self.depack(args)
        self.motcalc()

    def motcalc(self):
        #NOTE: This does not work with the mouse, but with a real Tuio stream it does
        '''Calculates the relative movement if the tracker is not providing it'''
        '''Ported from touchpy'''
        self.xmot = self.xpos - self.oxpos
        self.ymot = self.ypos - self.oypos

    def depack(self, args):
        if len(args) < 5:
            self.xpos, self.ypos = args[0:2]
        elif len(args) == 5:
            self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel = args[0:5]
        else:
            self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel, self.Width , self.Height = args[0:7]
        if self.dxpos is None:
            self.dxpos, self.dypos = self.xpos, self.ypos


class Tuio2DObject(object):
    '''Represent a Tuio object
    '''
    def __init__(self, blobID, args):
        self.blobID = blobID
        self.oxpos = self.oypos = 0.0
        self.depack(args)

    def move(self, args):
        self.oxpos, self.oypos = self.xpos, self.ypos
        self.depack(args)
        self.motcalc()

    def motcalc(self):
        '''Calculates the relative movement if the tracker is not providing it'''
        '''Ported from touchpy'''
        self.xmot = self.xpos - self.oxpos
        self.ymot = self.ypos - self.oypos

    def depack(self, args):
        if len(args) < 5:
            self.xpos, self.ypos = args[0:2]
        elif len(args) == 9:
            self.id, self.xpos, self.ypos, self.angle, self.Xvector, self.Yvector,self.Avector, self.xmot, self.ymot, = args[0:9]
        else:
            self.id, self.xpos, self.ypos, self.angle, self.Xvector, self.Yvector,self.Avector, self.xmot, self.ymot, self.Width , self.Height = args[0:11]


class TuioGetter(object):
    '''Tuio getter listen udp, and use the appropriate
    parser for 2Dcur and 2Dobj Tuio message.
    '''
    def __init__(self,  host='127.0.0.1', port=3333):
        global tuio_listeners
        tuio_listeners.append(self)
        self.host = host
        self.port = port
        self.startListening()

    def startListening(self):
        osc.init()
        osc.listen(self.host, self.port)
        osc.bind(self.osc_2dcur_Callback, '/tuio/2Dcur')
        osc.bind(self.osc_2dobj_Callback, '/tuio/2Dobj')

    def stopListening(self):
        osc.dontListen()

    def close(self):
        osc.dontListen()
        tuio_listeners.remove(self)

    def osc_2dcur_Callback(self, *incoming):
        global tuio_event_q
        message = incoming[0]
        type, types, args = message[0], message[1], message[2:]
        tuio_event_q.put([type, args, types])

    def osc_2dobj_Callback(self, *incoming):
        global tuio_event_q
        message = incoming[0]
        type, types, args = message[0], message[1], message[2:]
        tuio_event_q.put([type, args, types])


class TouchEventLoop(pyglet.app.EventLoop):
    '''Main event loop. This loop dispatch Tuio message and pyglet event.
    '''
    def __init__(self, host='127.0.0.1', port=3333):
        pyglet.app.EventLoop.__init__(self)
        self.current_frame = self.last_frame = 0
        self.alive2DCur = []
        self.alive2DObj = []
        self.blobs2DCur = {}
        self.blobs2DObj = {}
        self.clock = pyglet.clock.Clock()
        self.double_tap_distance = pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time = pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0
        self.parser = TuioGetter(host = host, port = port)
        self.ignore_list = strtotuple(pymt.pymt_config.get('tuio', 'ignore'))

    def close(self):
        if not self.parser:
            return
        self.parser.close()
        self.parser = None

    def collide_ignore(self, cur):
        x, y = cur.xpos, cur.ypos
        for l in self.ignore_list:
            xmin, ymin, xmax, ymax = l
            if x > xmin and x < xmax and y > ymin and y < ymax:
                return True

    def find_double_tap(self, ref):
        for blobID in self.blobs2DCur:
            cur = self.blobs2DCur[blobID]
            if cur.is_timeout or cur.have_event_down or cur.do_event != 'on_touch_up':
                continue
            distance = pymt.Vector.distance(pymt.Vector(ref.xpos, ref.ypos),
                                            pymt.Vector(cur.xpos, cur.ypos))
            if distance > self.double_tap_distance:
                continue
            return cur

    def process_2dcur_events(self):
        time_current = self.clock.time()
        remove_list = []
        for blobID in self.blobs2DCur:
            # not timeout state, calculate !
            cur = self.blobs2DCur[blobID]
            if not cur.is_timeout:
                if time_current - cur.time_start > self.double_tap_time:
                    cur.is_timeout = True
                if not cur.is_timeout:
                    # at least, check double_tap_distance
                    distance = pymt.Vector.distance(pymt.Vector(cur.dxpos, cur.dypos),
                                                    pymt.Vector(cur.xpos, cur.ypos))
                    if distance < self.double_tap_distance:
                        break
                    cur.is_timeout = True

            # ok, now check event !
            event_str = None
            if not cur.have_event_down:
                event_str = 'on_touch_down'
                cur.have_event_down = True
            elif cur.do_event:
                event_str = cur.do_event
                cur.do_event = False

            # event to do ?
            if event_str:
                if not cur.no_event:
                    if event_str == 'on_touch_down':
                        xpos, ypos = cur.dxpos, cur.dypos
                    else:
                        xpos, ypos = cur.xpos, cur.ypos
                    for l in touch_event_listeners:
                        l.dispatch_event(event_str, self.blobs2DCur, cur.blobID,
                            cur.xpos * l.width, l.height - l.height * cur.ypos)
                if event_str == 'on_touch_up':
                    remove_list.append(cur.blobID)

        for blobID in remove_list:
            del self.blobs2DCur[blobID]

    def parse2dCur(self, args, types):
        global touch_event_listeners
        if args[0] == 'alive':
            touch_release   = difference(self.alive2DCur,args[1:])
            touch_down      = difference(self.alive2DCur,args[1:])
            touch_move      = intersection(self.alive2DCur,args[1:])
            self.alive2DCur = args[1:]
            for blobID in touch_release:
                if blobID in self.blobs2DCur:
                    self.blobs2DCur[blobID].do_event = 'on_touch_up'

        elif args[0] == 'set':
            blobID = args[1]
            # first time ?
            if blobID not in self.blobs2DCur:
                # create cursor
                cur = Tuio2DCursor(blobID, args[2:], self.clock.time())
                # if cursor is in the ignore box, drop it
                if self.collide_ignore(cur):
                    return
                # search for double tap
                cur_double_tap = self.find_double_tap(cur)
                if cur_double_tap:
                    cur.is_double_tap = True
                    cur.double_tap_time = cur.time_start - cur_double_tap.time_start
                    cur.time_start = cur_double_tap.time_start
                    cur_double_tap.no_event = True
                # add into list
                self.blobs2DCur[blobID] = cur
            else:
                # cursor exist, move it :)
                self.blobs2DCur[blobID].move(args[2:])
                self.blobs2DCur[blobID].do_event = 'on_touch_move'

    def parse2dObj(self, args, types):
        global touch_event_listeners

        if not args[0] in ['alive', 'set']:
            return

        if args[0] == 'alive':
            touch_release = difference(self.alive2DObj, args[1:])
            touch_down = difference(self.alive2DObj, args[1:])
            touch_move = intersection(self.alive2DObj, args[1:])
            self.alive2DObj = args[1:]

            for blobID in touch_release:
                for l in touch_event_listeners:
                    l.dispatch_event('on_object_up', self.blobs2DObj, blobID,
                        self.blobs2DObj[blobID].id,
                        self.blobs2DObj[blobID].xpos * l.width,
                        l.height - l.height*self.blobs2DObj[blobID].ypos,
                        self.blobs2DObj[blobID].angle
                    )
                    del self.blobs2DObj[blobID]

        elif args[0] == 'set':
            blobID = args[1]
            if blobID not in self.blobs2DObj:
                self.blobs2DObj[blobID] = Tuio2DObject(blobID,args[2:])
                for l in touch_event_listeners:
                    l.dispatch_event('on_object_down', self.blobs2DObj, blobID,
                        self.blobs2DObj[blobID].id,
                        self.blobs2DObj[blobID].xpos * l.width,
                        l.height - l.height*self.blobs2DObj[blobID].ypos,
                        self.blobs2DObj[blobID].angle
                    )
            else:
                self.blobs2DObj[blobID].move(args[2:])
                for l in touch_event_listeners:
                    l.dispatch_event('on_object_move', self.blobs2DObj, blobID,
                        self.blobs2DObj[blobID].id,
                        self.blobs2DObj[blobID].xpos * l.width,
                        l.height - l.height*self.blobs2DObj[blobID].ypos,
                        self.blobs2DObj[blobID].angle
                    )

    def idle(self):
        global tuio_event_q
        pyglet.clock.tick()

        # process tuio
        while not tuio_event_q.empty():
            type,args, types = tuio_event_q.get()
            if type == '/tuio/2Dcur':
                self.parse2dCur(args, types)
            if type == '/tuio/2Dobj':
                self.parse2dObj(args, types)

        # launch event ?
        self.process_2dcur_events()

        # dispatch pyglet events
        for window in pyglet.app.windows:
            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()

        return 0

def stopTuio():
    '''Stop Tuio listening'''
    global tuio_listeners
    for listener in tuio_listeners:
        listener.stopListening()

def startTuio():
    '''Start Tuio listening'''
    global tuio_listeners
    for listener in tuio_listeners:
        listener.startListening()

#any window that inherhits this or an instance will have event handlers triggered on Tuio touch events
class TouchWindow(pyglet.window.Window):
    '''Base implementation of Tuio event in top of pyglet window.

    :Events:
        `on_touch_down`
            Fired when a blob is detected
        `on_touch_move`
            Fired when the blob is moving
        `on_touch_up`
            Fired when the blob is gone
        `on_object_down`
            Fired when the object is detected
        `on_object_move`
            Fired when the object is moving
        `on_object_up`
            Fired when the object is gone
    '''
    def __init__(self, config=None):
        pyglet.window.Window.__init__(self, config=config)
        self.register_event_type('on_touch_up')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_down')
        self.register_event_type('on_object_up')
        self.register_event_type('on_object_move')
        self.register_event_type('on_object_down')
        touch_event_listeners.append(self)

    def on_touch_down(self, touches, touchID, x, y):
        pass

    def on_touch_move(self, touches, touchID, x, y):
        pass

    def on_touch_up(self, touches, touchID, x, y):
        pass

    def on_object_down(self, touches, touchID,id, x, y, angle):
        pass

    def on_object_move(self, touches, touchID,id, x, y, angle):
        pass

    def on_object_up(self, touches, touchID,id, x, y, angle):
        pass


def pymt_usage():
    '''PyMT Usage: %s [OPTION...]
  -h, --help                        prints this mesage
  -f, --fullscreen                  force run in fullscreen
  -w, --windowed                    force run in window
  -p, --port=x                      specify Tuio port (default 3333)
  -H, --host=xxx.xxx.xxx.xxx        specify Tuio host (default 127.0.0.1)
  -F, --fps                         show fps in window
      --dump-frame                  dump each frame in file
      --dump-prefix                 specify a prefix for each frame file
      --dump-format                 specify a format for dump
    '''
    print pymt_usage.__doc__ % (os.path.basename(sys.argv[0]))


pymt_evloop = None
def runTouchApp():
    '''Static main function that starts the application loop'''

    global pymt_evloop

    # Check if we show event stats
    if pymt.pymt_config.getboolean('pymt', 'show_eventstats'):
        pymt.widget.event_stats_activate()

    host = pymt.pymt_config.get('tuio', 'host')
    port = pymt.pymt_config.getint('tuio', 'port')
    pymt_logger.info('listening for Tuio on %s:%d' % (host, port))
    pymt_evloop = TouchEventLoop(host=host, port=port)

    try:
        pymt_evloop.run()
    except:
        stopTouchApp()
        raise

    # Show event stats
    if pymt.pymt_config.getboolean('pymt', 'show_eventstats'):
        pymt.widget.event_stats_print()

def stopTouchApp():
    global pymt_evloop
    pymt_logger.info('Leaving application in progress...')
    pymt_evloop.exit()


#a very simple test
if __name__ == '__main__':

    from graphx import *
    touchPositions = {}
    crosshair = pyglet.sprite.Sprite(pyglet.image.load('crosshair.png'))
    crosshair.scale = 0.6

    w = TouchWindow()
    #    w.set_fullscreen()
    @w.event
    def on_touch_down(touches, touchID, x,y):
        touchPositions[touchID] = [(touchID,x,y)]
    @w.event
    def on_touch_up(touches, touchID,x,y):
        del touchPositions[touchID]
    @w.event
    def on_touch_move(touches, touchID, x, y):
        touchPositions[touchID].append((x,y))
    @w.event
    def on_draw():
        w.clear()
        for p in touchPositions:
            touchID,x,y = touchPositions[p][0]
            for pos in touchPositions[p][1:]:
                x, y = pos
                crosshair.x = x
                crosshair.y = y
                crosshair.draw()

    runTouchApp()

tuio_event_q.join()
