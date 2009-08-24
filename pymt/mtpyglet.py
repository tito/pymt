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

import lib.osc
import pyglet
import pymt
import sys, os
from logger import pymt_logger
from exceptions import pymt_exception_manager, ExceptionManager
from input import TouchFactory, pymt_postproc_modules

# All event listeners will add themselves to this
# list upon creation
touch_event_listeners   = []
touch_list              = []
pymt_providers          = []
pymt_evloop             = None
frame_dt                = 0.01 # init >0 value to prevent user zero division

def getFrameDt():
    '''Return the last delta between old and new frame.'''
    global frame_dt
    return frame_dt

def getAvailableTouchs():
    '''Return all the availables touches'''
    global touch_list
    return touch_list

def getEventLoop():
    '''Return the default event loop'''
    global pymt_evloop
    return pymt_evloop

class TouchEventLoop(pyglet.app.EventLoop):
    '''Main event loop. This loop handle update of input + dispatch event
    '''
    def __init__(self):
        pyglet.app.EventLoop.__init__(self)
        self.input_events           = []
        self.postproc_modules       = []
        self.double_tap_distance    = \
            pymt.pymt_config.getint('pymt', 'double_tap_distance') / 1000.0
        self.double_tap_time        = \
            pymt.pymt_config.getint('pymt', 'double_tap_time') / 1000.0

    def start(self):
        '''Start all input providers'''
        global pymt_providers
        for provider in pymt_providers:
            provider.start()

    def close(self):
        '''Close all input providers'''
        global pymt_providers
        for provider in pymt_providers:
            provider.stop()

    def add_postproc_module(self, mod):
        '''Add a post processing module to execute after each update
        of a input providers'''
        self.postproc_modules.append(mod)

    def remove_postproc_module(self, mod):
        '''Remove a previously added post-processing module'''
        if mod in self.postproc_modules:
            self.postproc_modules.remove(mod)

    def post_dispatch_input(self, ptype, touch):
        # update available list
        global touch_list
        if ptype == 'down':
            touch_list.append(touch)
        elif ptype == 'up':
            touch_list.remove(touch)

        # dispatch to listeners
        if not touch.grab_exclusive_class:
            global touch_event_listeners
            for listener in touch_event_listeners:
                if ptype == 'down':
                    listener.dispatch_event('on_touch_down', touch)
                elif ptype == 'move':
                    listener.dispatch_event('on_touch_move', touch)
                elif ptype == 'up':
                    listener.dispatch_event('on_touch_up', touch)

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
                    touch.x, touch.y = \
                        wid.to_parent(wid.to_widget(touch.x, touch.y))

            touch.grab_current = wid

            if ptype == 'down':
                # don't dispatch again touch in on_touch_down
                # a down event are nearly uniq here.
                # wid.dispatch_event('on_touch_down', touch)
                pass
            elif ptype == 'move':
                wid.dispatch_event('on_touch_move', touch)
            elif ptype == 'up':
                wid.dispatch_event('on_touch_up', touch)

            touch.grab_current = None

            if wid != root_window and root_window is not None:
                touch.pop()
        touch.grab_state = False

    def __dispatch_input(self, ptype, touch):
        self.input_events.append((ptype, touch))

    def dispatch_input(self):
        '''Update input providers, execute post-processing modules,
        and dispatch all inputs to listeners'''
        global pymt_providers

        # first, aquire input events
        self.input_events = []
        for provider in pymt_providers:
            provider.update(dispatch_fn=self.__dispatch_input)

        # execute post-processing modules
        for mod in self.postproc_modules:
            self.input_events = mod.process(events=self.input_events)

        # real dispatch input
        for ptype, touch in self.input_events:
            self.post_dispatch_input(ptype=ptype, touch=touch)


    def idle(self):
        '''Function called each frame. We :

        * process inputs
        * process events
        * flip the window
        '''
        # update dt
        global frame_dt
        frame_dt = pyglet.clock.tick()

        # read and dispatch input from providers
        self.dispatch_input()

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
    '''PyMT Usage: %s [OPTION...] ::

        -h, --help                  prints this mesage
        -f, --fullscreen            force run in fullscreen
        -w, --windowed              force run in window
        -p, --provider id:provider[,options] add a provider
                                        (eg: ccvtable1:tuio,192.168.0.1:3333)
        -F, --fps                   show fps in window
        -m mod, --module=mod        activate a module
                                        (use "list" to get available module)
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
    '''Stop the application loop'''
    global pymt_evloop
    if pymt_evloop is None:
        return
    pymt_logger.info('Leaving application in progress...')
    pymt_evloop.close()
    pymt_evloop.exit()
    pymt_evloop = None

