'''
Base: base of multitouch, osc, window management
'''

import osc
import pyglet
import pymt
import pymtcore
import sys, getopt, os
from logger import pymt_logger
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
pymt_windows            = []

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

def registerWindow(window):
    global pymt_windows
    global touch_event_listeners
    pymt_windows.append(window)
    touch_event_listeners.append(window)

def unregisterWindow(window):
    global pymt_windows
    global touch_event_listeners
    pymt_windows.remove(window)
    touch_event_listeners.remove(window)


class TouchEventLoop:
    '''Main event loop. This loop handle update of input + dispatch event
    '''
    def __init__(self, host='127.0.0.1', port=3333):
        self.input_events = []
        self.postproc_modules = []
        self.double_tap_distance = pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time = pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0
        self.do_exit = False
        self.last_tick = 0

    def start(self):
        global pymt_providers
        for provider in pymt_providers:
            provider.start()

    def close(self):
        global pymt_providers
        for provider in pymt_providers:
            provider.stop()

    def add_postproc_module(self, mod):
        self.postproc_modules.append(mod)

    def remove_postproc_module(self, mod):
        if mod in self.postproc_modules:
            self.postproc_modules.remove(mod)

    def post_dispatch_input(self, type, touch):
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
                    listener.on_touch_down(touch)
                elif type == 'move':
                    listener.on_touch_move(touch)
                elif type == 'up':
                    listener.on_touch_up(touch)

        # dispatch grabbed touch
        touch.grab_state = True
        for wid in touch.grab_list:
            root_window = wid.get_root_window()
            if wid != root_window and root_window is not None:
                touch.push()
                touch.scale_for_screen(*root_window.size)
                # and do to_local until the widget
                if wid.parent:
                    touch.x, touch.y = wid.parent.to_widget(touch.x, touch.y)
                else:
                    touch.x, touch.y = wid.to_parent(wid.to_widget(touch.x, touch.y))

            touch.grab_current = wid

            if type == 'down':
                # don't dispatch again touch in on_touch_down
                # a down event are nearly uniq here.
                wid.dispatch_event('on_touch_down', (touch, ))
            elif type == 'move':
                wid.dispatch_event('on_touch_move', (touch, ))
            elif type == 'up':
                wid.dispatch_event('on_touch_up', (touch, ))

            touch.grab_current = None

            if wid != root_window and root_window is not None:
                touch.pop()
        touch.grab_state = False

    def _dispatch_input(self, type, touch):
        self.input_events.append((type, touch))

    def dispatch_input(self):
        global pymt_providers

        # first, aquire input events
        self.input_events = []
        for provider in pymt_providers:
            provider.update(dispatch_fn=self._dispatch_input)

        # execute post-processing modules
        for mod in self.postproc_modules:
            self.input_events = mod.process(events=self.input_events)

        # real dispatch input
        for type, touch in self.input_events:
            self.post_dispatch_input(type=type, touch=touch)

    def exit(self):
        self.do_exit = True

    def run(self):
        while not self.do_exit:
            self.idle()

    def idle(self):
        # update dt
        global frame_dt
        ticks = pymtcore.get_ticks()
        frame_dt = ticks - self.last_tick
        self.last_tick = ticks

        # read and dispatch input from providers
        self.dispatch_input()

        # dispatch pyglet events
        #
        global pymt_windows
        for window in pymt_windows:
            window.dispatch_event('on_update', ())
            window.dispatch_event('on_draw', ())

        # don't loop if we don't have listeners !
        global touch_event_listeners
        if len(touch_event_listeners) == 0:
            self.exit()

        return 0

def pymt_usage():
    '''PyMT Usage: %s [OPTION...] ::

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

    # add postproc modules
    for mod in pymt_postproc_modules:
        pymt_evloop.add_postproc_module(mod)

    # start event loop
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

