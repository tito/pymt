'''
Pyglet: Soup on pyglet to provide multitouch interface.
'''

__all__ = [
    'TouchEventLoop', 'TouchWindow',
    'pymt_usage', 'runTouchApp', 'stopTouchApp',
    'getFrameDt', 'getAvailableTouchs',
    'getEventLoop',
    'touch_event_listeners', 'pymt_providers'
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
touch_event_listeners   = []
touch_list              = []
pymt_providers          = []
pymt_evloop             = None
frame_dt                = 0.01 # init to a non-zero value, to prevent user zero division

def getFrameDt():
    '''Return the last delta between old and new frame.'''
    global frame_dt
    return frame_dt

def getAvailableTouchs():
    global touch_list
    return touch_list

def getEventLoop():
    global pymt_evloop
    return pymt_evloop

class TouchEventLoop(pyglet.app.EventLoop):
    '''Main event loop. This loop handle update of input + dispatch event
    '''
    def __init__(self, host='127.0.0.1', port=3333):
        pyglet.app.EventLoop.__init__(self)
        self.alive2DCur = []
        self.alive2DObj = []
        self.blobs2DCur = {}
        self.blobs2DObj = {}
        self.double_tap_distance = pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time = pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0
        self.ignore_list = strtotuple(pymt.pymt_config.get('pymt', 'ignore'))

    def start(self):
        global pymt_providers
        for provider in pymt_providers:
            provider.start()

    def close(self):
        global pymt_providers
        for provider in pymt_providers:
            provider.stop()

    def collide_ignore(self, cur):
        x, y = cur.xpos, cur.ypos
        for l in self.ignore_list:
            xmin, ymin, xmax, ymax = l
            if x > xmin and x < xmax and y > ymin and y < ymax:
                return True

    def dispatch_input(self, type, touch):
        # update available list
        global touch_list
        if type == 'down':
            touch_list.append(touch)
        elif type == 'up':
            touch_list.remove(touch)

        # dispatch to listeners
        if not touch.grab_exclusive_class:
            global touch_event_listeners
            for listener in touch_event_listeners:
                if type == 'down':
                    listener.dispatch_event('on_touch_down', touch)
                elif type == 'move':
                    listener.dispatch_event('on_touch_move', touch)
                elif type == 'up':
                    listener.dispatch_event('on_touch_up', touch)

        # dispatch grabbed touch
        touch.grab_state = True
        for wid in touch.grab_list:
            root_window = wid.get_root_window()
            if wid != root_window and root_window is not None:
                touch.push()
                touch.scale_for_screen(*root_window.size)

            touch.grab_current = wid

            if type == 'down':
                # don't dispatch again touch in on_touch_down
                # a down event are nearly uniq here.
                # wid.dispatch_event('on_touch_down', touch)
                pass
            elif type == 'move':
                wid.dispatch_event('on_touch_move', touch)
            elif type == 'up':
                wid.dispatch_event('on_touch_up', touch)

            touch.grab_current = None

            if wid != root_window and root_window is not None:
                touch.pop()
        touch.grab_state = False

    def idle(self):
        # update dt
        global frame_dt
        frame_dt = pyglet.clock.tick()

        # read and dispatch input from providers
        global pymt_providers
        for provider in pymt_providers:
            provider.update(dispatch_fn=self.dispatch_input)

        # dispatch pyglet events
        for window in pyglet.app.windows:
            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()

        # don't loop if we don't have listeners !
        global touch_event_listeners
        if len(touch_event_listeners) == 0:
            self.exit()

        return 0

#any window that inherhits this or an instance will have event handlers triggered on Tuio touch events
class TouchWindow(pyglet.window.Window):
    '''Base implementation of Tuio event in top of pyglet window.

    :Events:
        `on_touch_down`
            Fired when a down event occured
        `on_touch_move`
            Fired when a move event occured
        `on_touch_up`
            Fired when a up event occured
    '''
    def __init__(self, **kwargs):
        super(TouchWindow, self).__init__(**kwargs)
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_up')
        touch_event_listeners.append(self)

    def on_close(self, *largs):
        touch_event_listeners.remove(self)
        super(TouchWindow, self).on_close(*largs)

    def on_touch_down(self, touch):
        pass

    def on_touch_move(self, touch):
        pass

    def on_touch_up(self, touch):
        pass

def pymt_usage():
    '''PyMT Usage: %s [OPTION...]

    -h, --help                  prints this mesage
    -f, --fullscreen            force run in fullscreen
    -w, --windowed              force run in window
    -p, --provider id:provider[,options] add a provider (eg: ccvtable1:tuio,192.168.0.1:3333)
    -F, --fps                   show fps in window
    -m mod, --module=mod        activate a module (use "list" to get available module)
    -s, --save                  save current PyMT configuration
    --size=640x480              size of window
    --dump-frame                dump each frame in file
    --dump-prefix               specify a prefix for each frame file
    --dump-format               specify a format for dump
    '''
    print pymt_usage.__doc__ % (os.path.basename(sys.argv[0]))


def runTouchApp():
    '''Static main function that starts the application loop'''

    global pymt_evloop
    global pymt_providers

    # Check if we show event stats
    if pymt.pymt_config.getboolean('pymt', 'show_eventstats'):
        pymt.widget.event_stats_activate()

    # Instance all configured input
    for key, value in pymt.pymt_config.items('input'):
        pymt_logger.debug('Create provider from %s' % (str(value)))

        # split value
        args = str(value).split(',', 1)
        if len(args) == 1:
            args.append('')
        provider_id, args = args
        provider = TouchFactory.get(provider_id)
        if provider is None:
            pymt_logger.warning('Unknown <%s> provider' % str(provider_id))
            continue

        # create provider
        p = provider(args)
        if p:
            pymt_providers.append(p)

    pymt_evloop = TouchEventLoop()
    pymt_evloop.start()

    while True:
        try:
            pymt_evloop.run()
            stopTouchApp()
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
    if pymt_evloop is None:
        return
    pymt_logger.info('Leaving application in progress...')
    pymt_evloop.close()
    pymt_evloop.exit()
    pymt_evloop = None

