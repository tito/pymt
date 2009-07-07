'''
Pyglet: Soup on pyglet to provide multitouch interface.
'''

__all__ = [
    'TouchEventLoop', 'TouchWindow',
    'pymt_usage', 'runTouchApp', 'stopTouchApp',
    'getFrameDt', 'getAvailableTouchs',
    'touch_event_listeners'
]

import osc
import pyglet
import pymt
import sys, getopt, os
from logger import pymt_logger
from pyglet.gl import *
from exceptions import pymt_exception_manager, ExceptionManager
from Queue import Queue
from utils import intersection, difference, strtotuple
from input import *

# All event listeners will add themselves to this
# list upon creation
touch_event_listeners = []
touch_list = []
frame_dt = 0.01 # init to a non-zero value, to prevent user zero division

def getFrameDt():
    '''Return the last delta between old and new frame.'''
    global frame_dt
    return frame_dt

def getAvailableTouchs():
    global touch_list
    return touch_list

class TouchEventLoop(pyglet.app.EventLoop):
    '''Main event loop. This loop dispatch Tuio message and pyglet event.

    :Parameters:
        `host` : string, default to '127.0.0.1'
            IP to listen
        `port` : int, default to 3333
            Port to listen
    '''
    def __init__(self, host='127.0.0.1', port=3333):
        pyglet.app.EventLoop.__init__(self)
        self.alive2DCur = []
        self.alive2DObj = []
        self.blobs2DCur = {}
        self.blobs2DObj = {}
        self.double_tap_distance = pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time = pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0
        self.ignore_list = strtotuple(pymt.pymt_config.get('tuio', 'ignore'))

        # TODO change this, make it configurable
        self.providers = []
        self.providers.append(TouchFactory.get('tuio')(ip=host, port=port))

    def start(self):
        for provider in self.providers:
            provider.start()

    def close(self):
        while len(self.providers):
            provider = self.providers[0]
            del self.providers[0]
            provider.stop()

    def collide_ignore(self, cur):
        x, y = cur.xpos, cur.ypos
        for l in self.ignore_list:
            xmin, ymin, xmax, ymax = l
            if x > xmin and x < xmax and y > ymin and y < ymax:
                return True

    def dispatch_input(self, type, input):
        # update available list
        global touch_list
        if type == 'down':
            touch_list.append(input)
        elif type == 'up':
            touch_list.remove(input)

        # dispatch to listeners
        global touch_event_listeners
        for listener in touch_event_listeners:
            if type == 'down':
                listener.dispatch_event('on_touch_down', input)
            elif type == 'move':
                listener.dispatch_event('on_touch_move', input)
            elif type == 'up':
                listener.dispatch_event('on_touch_up', input)

    def idle(self):
        # update dt
        global frame_dt
        frame_dt = pyglet.clock.tick()

        # read and dispatch input from providers
        for provider in self.providers:
            provider.update(dispatch_fn=self.dispatch_input)

        # dispatch pyglet events
        for window in pyglet.app.windows:
            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()

        return 0

#any window that inherhits this or an instance will have event handlers triggered on Tuio touch events
class TouchWindow(pyglet.window.Window):
    '''Base implementation of Tuio event in top of pyglet window.

    :Events:
        `on_input`
            Fired when a input event occured
    '''
    def __init__(self, **kwargs):
        super(TouchWindow, self).__init__(**kwargs)
        self.register_event_type('on_input')
        touch_event_listeners.append(self)

    def on_input(self, touch):
        pass

def pymt_usage():
    '''PyMT Usage: %s [OPTION...]

    -h, --help                  prints this mesage
    -f, --fullscreen            force run in fullscreen
    -w, --windowed              force run in window
    -p port, --port=post        specify Tuio port (default 3333)
    -H host, --host=host        specify Tuio host (default 127.0.0.1)
    -F, --fps                   show fps in window
    -m mod, --module=mod        activate a module (use "list" to get available module)
    -s, --save                  save current PyMT configuration
    --size=640x480              size of window
    --dump-frame                dump each frame in file
    --dump-prefix               specify a prefix for each frame file
    --dump-format               specify a format for dump
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
    pymt_evloop = TouchEventLoop(host=host, port=port)
    pymt_evloop.start()

    while True:
        try:
            pymt_evloop.run()
            break
        except BaseException, inst:
            # use exception manager first
            r = pymt_exception_manager.handle_exception(inst)
            if r == ExceptionManager.RAISE:
                stopTouchApp()
                raise
            else:
                pass

    # Show event stats
    if pymt.pymt_config.getboolean('pymt', 'show_eventstats'):
        pymt.widget.event_stats_print()

def stopTouchApp():
    global pymt_evloop
    pymt_logger.info('Leaving application in progress...')
    pymt_evloop.close()
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
