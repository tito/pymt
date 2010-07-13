'''
Base: Main event loop, provider creation, window management...
'''

__all__ = [
    'pymt_usage',
    'runTouchApp', 'stopTouchApp',
    'getFrameDt', 'getCurrentTouches',
    'getEventLoop',
    'pymt_event_listeners', 'touch_event_listeners',
    'pymt_providers',
    'getWindow', 'setWindow'
]

import pymt
import sys
import os
import weakref
from logger import pymt_logger
from exceptions import pymt_exception_manager, ExceptionManager
from clock import getClock
from input import *
from utils import deprecated

# private vars
touch_list              = []
pymt_window             = None
pymt_providers          = []
pymt_evloop             = None
frame_dt                = 0.01 # init to a non-zero value, to prevent user zero division

#: List of event listeners
pymt_event_listeners    = []

#: .. deprecated:: 0.5
#:      This symbol have been renamed to pymt_event_listeners 
touch_event_listeners   = pymt_event_listeners

def getFrameDt():
    '''Return the last delta between old and new frame.'''
    global frame_dt
    return frame_dt

def getCurrentTouches():
    '''Return the list of all current touches'''
    global touch_list
    return touch_list

def getWindow():
    '''Return the MTWindow'''
    global pymt_window
    return pymt_window

def setWindow(win):
    global pymt_window
    pymt_window = win

def getEventLoop():
    '''Return the default TouchEventLoop object'''
    global pymt_evloop
    return pymt_evloop

class TouchEventLoop(object):
    '''Main event loop. This loop handle update of input + dispatch event
    '''
    def __init__(self):
        super(TouchEventLoop, self).__init__()
        self.quit = False
        self.input_events = []
        self.postproc_modules = []
        self.status = 'idle'

    def start(self):
        '''Must be call only one time before run().
        This start all configured input providers.'''
        self.status = 'started'
        global pymt_providers
        for provider in pymt_providers:
            provider.start()

    def close(self):
        '''Exit from the main loop, and stop all configured
        input providers.'''
        global pymt_providers
        self.quit = True
        self.stop()
        self.status = 'closed'

    def stop(self):
        '''Stop all input providers'''
        #stop in reverse order that we started them!! (liek push pop),
        #very important becasue e.g. wm_touch and WM_PEN both store
        #old window proc and teh restore, if order is messed big problem
        #happens, crashing badly without error
        for provider in reversed(pymt_providers):
            provider.stop()
        self.status = 'stopped'

    def add_postproc_module(self, mod):
        '''Add a postproc input module (DoubleTap, RetainTouch are default)'''
        self.postproc_modules.append(mod)

    def remove_postproc_module(self, mod):
        '''Remove a postproc module'''
        if mod in self.postproc_modules:
            self.postproc_modules.remove(mod)

    def post_dispatch_input(self, type, touch):
        '''This function is called by dispatch_input() when we want to dispatch
        a input event. The event is dispatched into all listeners, and if
        grabbed, it's dispatched through grabbed widgets'''
        # update available list
        global touch_list
        if type == 'down':
            touch_list.append(touch)
        elif type == 'up':
            if touch in touch_list:
                touch_list.remove(touch)

        # dispatch to listeners
        if not touch.grab_exclusive_class:
            for listener in pymt_event_listeners:
                if type == 'down':
                    listener.dispatch_event('on_touch_down', touch)
                elif type == 'move':
                    listener.dispatch_event('on_touch_move', touch)
                elif type == 'up':
                    listener.dispatch_event('on_touch_up', touch)

        # dispatch grabbed touch
        touch.grab_state = True
        for _wid in touch.grab_list[:]:

            # it's a weakref, call it!
            wid = _wid()
            if wid is None:
                # object is gone, stop.
                touch.grab_list.remove(_wid)
                continue

            root_window = wid.get_root_window()
            if wid != root_window and root_window is not None:
                touch.push()
                touch.scale_for_screen(*root_window.size)
                # and do to_local until the widget
                try:
                    if wid.parent:
                        touch.x, touch.y = wid.parent.to_widget(touch.x, touch.y)
                        touch.dxpos, touch.dypos = wid.parent.to_widget(touch.dxpos, touch.dypos)
                    else:
                        touch.x, touch.y = wid.to_parent(wid.to_widget(touch.x, touch.y))
                        touch.dxpos, touch.dypos = wid.to_parent(wid.to_widget(touch.dxpos, touch.dypos))
                except AttributeError:
                    # when using innerwindow, an app have grab the touch
                    # but app is removed. the touch can't access
                    # to one of the parent. (ie, self.parent will be None)
                    # and BAM the bug happen.
                    touch.pop()
                    continue

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

    def _dispatch_input(self, type, touch):
        ev = (type, touch)
        # remove the save event for the touch if exist
        if ev in self.input_events:
            self.input_events.remove(ev)
        self.input_events.append(ev)

    def dispatch_input(self):
        '''Called by idle() to read events from input providers,
        pass event to postproc, and dispatch final events'''
        global pymt_providers

        # first, aquire input events
        for provider in pymt_providers:
            provider.update(dispatch_fn=self._dispatch_input)

        # execute post-processing modules
        for mod in self.postproc_modules:
            self.input_events = mod.process(events=self.input_events)

        # real dispatch input
        for type, touch in self.input_events:
            self.post_dispatch_input(type=type, touch=touch)

        self.input_events = []

    def idle(self):
        '''This function is called every frames. By default :
        * it "tick" the clock to the next frame
        * read all input and dispatch event
        * dispatch on_update + on_draw + on_flip on window
        '''
        # update dt
        global frame_dt
        frame_dt = getClock().tick()

        # read and dispatch input from providers
        self.dispatch_input()

        if pymt_window:
            pymt_window.dispatch_events()
            pymt_window.dispatch_event('on_update')
            pymt_window.dispatch_event('on_draw')
            pymt_window.dispatch_event('on_flip')

        # don't loop if we don't have listeners !
        if len(pymt_event_listeners) == 0:
            self.exit()
            return False

        return self.quit

    def run(self):
        '''Main loop'''
        while not self.quit:
            self.idle()
        self.exit()

    def exit(self):
        '''Close the main loop, and close the window'''
        self.close()
        if pymt_window:
            pymt_window.close()


def pymt_usage():
    '''PyMT Usage: %s [OPTION...] ::

        -h, --help                  prints this mesage
        -f, --fullscreen            force run in fullscreen
        -k, --fake-fullscreen       force run in 'fake' fullscreen (no border mode)
        -a, --auto-fullscreen       force run in 'auto' fullscreen (no resolution change)
        -w, --windowed              force run in window
        -p, --provider id:provider[,options] add a provider (eg: ccvtable1:tuio,192.168.0.1:3333)
        -F, --fps                   show fps in window
        -m mod, --module=mod        activate a module (use "list" to get available module)
        -s, --save                  save current PyMT configuration
        --size=640x480              size of window

    '''
    print pymt_usage.__doc__ % (os.path.basename(sys.argv[0]))


def _run_mainloop():
    '''If user haven't create a window, this is the executed mainloop'''
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


def runTouchApp(widget=None, slave=False):
    '''Static main function that starts the application loop.
    You got some magic things, if you are using argument like this :

    :Parameters:
        `<empty>`
            To make dispatching work, you need at least one
            input listener. If not, application will leave.
            (MTWindow act as an input listener)

        `widget`
            If you pass only a widget, a MTWindow will be created,
            and your widget will be added on the window as the root
            widget.

        `slave`
            No event dispatching are done. This will be your job.

        `widget + slave`
            No event dispatching are done. This will be your job, but
            we are trying to get the window (must be created by you before),
            and add the widget on it. Very usefull for embedding PyMT
            in another toolkit. (like Qt, check pymt-designed)

    '''

    global pymt_evloop
    global pymt_providers

    # Ok, we got one widget, and we are not in slave mode
    # so, user don't create the window, let's create it for him !
    ### Not needed, since we always create window ?!
    #if not slave and widget:
    #    global pymt_window
    #    from ui.window import MTWindow
    #    pymt_window = MTWindow()

    # Instance all configured input
    for key, value in pymt.pymt_config.items('input'):
        pymt_logger.debug('Base: Create provider from %s' % (str(value)))

        # split value
        args = str(value).split(',', 1)
        if len(args) == 1:
            args.append('')
        provider_id, args = args
        provider = TouchFactory.get(provider_id)
        if provider is None:
            pymt_logger.warning('Base: Unknown <%s> provider' % str(provider_id))
            continue

        # create provider
        p = provider(key, args)
        if p:
            pymt_providers.append(p)

    pymt_evloop = TouchEventLoop()

    # add postproc modules
    for mod in pymt_postproc_modules.values():
        pymt_evloop.add_postproc_module(mod)

    # add main widget
    if widget and getWindow():
        getWindow().add_widget(widget)

    # start event loop
    pymt_logger.info('Base: Start application main loop')
    pymt_evloop.start()

    # we are in a slave mode, don't do dispatching.
    if slave:
        return

    # in non-slave mode, they are 2 issues
    #
    # 1. if user created a window, call the mainloop from window.
    #    This is due to glut, it need to be called with
    #    glutMainLoop(). Only FreeGLUT got a gluMainLoopEvent().
    #    So, we are executing the dispatching function inside
    #    a redisplay event.
    #
    # 2. if no window is created, we are dispatching event lopp
    #    ourself (previous behavior.)
    #
    try:
        if pymt_window is None:
            _run_mainloop()
        else:
            pymt_window.mainloop()
    finally:
        stopTouchApp()

def stopTouchApp():
    '''Stop the current application by leaving the main loop'''
    global pymt_evloop
    if pymt_evloop is None:
        return
    if pymt_evloop.status != 'started':
        return
    pymt_logger.info('Base: Leaving application in progress...')
    pymt_evloop.close()
