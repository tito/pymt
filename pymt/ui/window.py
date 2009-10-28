'''
Window package: provide a window + a touch display
'''

__all__ = ['MTWindow', 'MTDisplay']

import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
import pymt
from ..mtpyglet import stopTouchApp, getAvailableTouchs, setWindow, touch_event_listeners
from ..graphx import set_color, drawCircle
from ..modules import pymt_modules
from ..utils import curry
from colors import css_get_style
from factory import MTWidgetFactory
from widgets import MTWidget

glut_window = None
_event_stats_activate = False

class MTWindow(object):
    '''MTWindow is a window widget.
    Use MTWindow as main window application.

    :Parameters:
        `view` : `MTWidget`
            Default view to add on window
        `fullscreen` : bool
            Make window as fullscreen
        `width` : int
            Width of window
        `height` : int
            Height of window
        `vsync` : bool
            Vsync window
        `display` : int
            Display index to use
        `config` : `Config`
            Default configuration to pass on TouchWindow

    :Styles:
        `bg-color` : color
            Background color of window
    '''
    have_multisample = None
    _event_stack = ()
    _size = (0, 0)
    _modifiers = 0
    def __init__(self, **kwargs):
        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)
        kwargs.setdefault('style', {})
        kwargs.setdefault('shadow', False)

        # event subsystem
        self.event_types = []
        self._event_stack = []

        self.register_event_type('on_draw')
        self.register_event_type('on_update')
        self.register_event_type('on_resize')
        self.register_event_type('on_close')
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_up')
        self.register_event_type('on_mouse')
        self.register_event_type('on_mouse_motion')
        self.register_event_type('on_keyboard')

        # create window
        global glut_window
        if glut_window is None:

            # for shadow window, make it invisible
            if kwargs.get('shadow'):
                glutInitWindowPosition(0, 0)
                glutInitWindowSize(1, 1)

            # init GLUT !
            glutInit()
            glutInitDisplayMode(
                GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH |
                GLUT_MULTISAMPLE | GLUT_STENCIL | GLUT_ACCUM)

            # create the window
            glut_window = glutCreateWindow('pymt')

            # hide the shadow...
            if kwargs.get('shadow'):
                glutHideWindow()

        # set out window as the main pymt window
        setWindow(self)

        # apply styles for window
        self.cssstyle = {}
        style = css_get_style(widget=self)
        self.apply_css(style)

        # apply inline css
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

        # initialize fps clock
        # FIXME clock fps
        #self.fps_display =  pyglet.clock.ClockDisplay()

        # initialize handlers list
        self.on_key_press_handlers = []
        self.on_text_handlers = []
        self.on_text_motion_handlers = []
        self.on_text_motion_select_handlers = []

        self.children = []
        self.parent = self
        self.visible = True

        # add view
        if 'view' in kwargs:
            self.add_widget(kwargs.get('view'))

        # get window params, user options before config option
        params = {}

        if 'fullscreen' in kwargs:
            params['fullscreen'] = kwargs.get('fullscreen')
        else:
            params['fullscreen'] = pymt.pymt_config.getboolean('graphics', 'fullscreen')

        if not params['fullscreen']:
            if 'width' in kwargs:
                params['width'] = kwargs.get('width')
            else:
                params['width'] = pymt.pymt_config.getint('graphics', 'width')

            if 'height' in kwargs:
                params['height'] = kwargs.get('height')
            else:
                params['height'] = pymt.pymt_config.getint('graphics', 'height')

        if 'vsync' in kwargs:
            params['vsync'] = kwargs.get('vsync')
        else:
            params['vsync'] = pymt.pymt_config.getint('graphics', 'vsync')

        displayidx = -1
        if 'display' in kwargs:
            displayidx = kwargs.get('display')
        else:
            displayidx = pymt.pymt_config.getint('graphics', 'display')

        '''
        if displayidx >= 0:
            display = window.get_platform().get_default_display()
            screens = display.get_screens()
            i = 0
            for screen in screens:
                pymt.pymt_logger.debug('Detected display %d: %s' % (i, str(screen)))
                i += 1
            try:
                params['screen'] = screens[displayidx]
            except Exception, e:
                pymt.pymt_logger.error('Invalid display specified %d' % displayidx)
                pymt.pymt_logger.exception(e)

        # create window
        try:
            config = kwargs.get('config')
            if not config:
                config = Config()
                config.sample_buffers = 1
                config.samples = 4
                config.depth_size = 16
                config.double_buffer = True
                config.stencil_size = 1
                config.alpha_size = 8
            super(MTWindow, self).__init__(config=config, **params)
        except:
            super(MTWindow, self).__init__(**params)
        '''

        # update window size
        if not kwargs.get('shadow'):
            glutShowWindow()
            self.size = params['width'], params['height']
            if params['fullscreen']:
                glutFullScreen()

            # register all callbcaks
            glutReshapeFunc(curry(self.dispatch_event, 'on_resize'))
            glutMouseFunc(curry(self.dispatch_event, 'on_mouse'))
            glutMotionFunc(curry(self.dispatch_event, 'on_mouse_motion'))
            glutKeyboardFunc(curry(self.dispatch_event, 'on_keyboard'))

        # show fps if asked
        self.show_fps = kwargs.get('show_fps')
        if pymt.pymt_config.getboolean('pymt', 'show_fps'):
            self.show_fps = True

        # initialize dump image
        self.dump_frame     = pymt.pymt_config.getboolean('dump', 'enabled')
        self.dump_prefix    = pymt.pymt_config.get('dump', 'prefix')
        self.dump_format    = pymt.pymt_config.get('dump', 'format')
        self.dump_idx       = 0

        # init some gl
        self.init_gl()

        # init modules
        if not kwargs.get('shadow'):
            pymt_modules.register_window(self)
            touch_event_listeners.append(self)

    def close(self):
        global glut_window
        if glut_window:
            glutDestroyWindow(glut_window)
            glut_window = None

    def apply_css(self, styles):
        self.cssstyle.update(styles)

    def on_close(self, *largs):
        pymt_modules.unregister_window(self)
        if self in touch_event_listeners:
            touch_event_listeners.remove(self)

    def on_mouse(self, button, state, x, y):
        pass

    def on_mouse_motion(self, x, y, button, modifiers):
        pass

    def on_keyboard(self, key, x, y):
        self._modifiers = glutGetModifiers()

    def _get_modifiers(self):
        return self._modifiers
    modifiers = property(_get_modifiers)

    def _set_size(self, size):
        glutReshapeWindow(*size)
        self._size = tuple(size)
    def _get_size(self):
        return self._size
    size = property(_get_size, _set_size,
            doc='''Return width/height of window''')

    def _get_width(self):
        return self._size[0]
    width = property(_get_width)

    def _get_height(self):
        return self._size[1]
    height = property(_get_height)

    def init_gl(self):
        # check if window have multisample
        """
        if MTWindow.have_multisample is None:
            s = glGetIntegerv(GL_SAMPLES)
            if s > 0:
                pymt.pymt_logger.debug('Multisampling is available (%d)' % s.value)
                MTWindow.have_multisample = True
            else:
                pymt.pymt_logger.debug('Multisampling is not available')
                MTWindow.have_multisample = False
        """

        line_smooth = pymt.pymt_config.getint('graphics', 'line_smooth')
        if line_smooth:
            if line_smooth == 1:
                hint = GL_FASTEST
            else:
                hint = GL_NICEST
            glHint(GL_LINE_SMOOTH_HINT, hint)
            glEnable(GL_LINE_SMOOTH)

    def add_on_key_press(self, func):
        self.on_key_press_handlers.append(func)

    def remove_on_key_press(self, func):
        if func in self.on_key_press_handlers:
            self.on_key_press_handlers.remove(func)

    def get_on_key_press(self):
        if len(self.on_key_press_handlers) == 0:
            return None
        return self.on_key_press_handlers[-1]

    def add_on_text(self, func):
        self.on_text_handlers.append(func)

    def remove_on_text(self, func):
        if func in self.on_text_handlers:
            self.on_text_handlers.remove(func)

    def get_on_text(self):
        if len(self.on_text_handlers) == 0:
            return None
        return self.on_text_handlers[-1]

    def add_on_text_motion(self, func):
        self.on_text_motion_handlers.append(func)

    def remove_on_text_motion(self, func):
        if func in self.on_text_motion_handlers:
            self.on_text_motion_handlers.remove(func)

    def get_on_text_motion(self):
        if len(self.on_text_motion_handlers) == 0:
            return None
        return self.on_text_motion_handlers[-1]

    def add_on_text_motion_select(self, func):
        self.on_text_motion_select_handlers.append(func)

    def remove_on_text_motion_select(self, func):
        if func in self.on_text_motion_select_handlers:
            self.on_text_motion_select_handlers.remove(func)

    def get_on_text_motion_select(self):
        if len(self.on_text_motion_select_handlers) == 0:
            return None
        return self.on_text_motion_select_handlers[-1]

    def add_widget(self, w):
        '''Add a widget on window'''
        self.children.append(w)
        w.parent = self

    def remove_widget(self, w):
        '''Remove a widget from window'''
        if not w in self.children:
            return
        self.children.remove(w)
        w.parent = None

    def draw(self):
        '''Clear the window with background color'''
        glClearColor(*self.cssstyle.get('bg-color'))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def on_update(self):
        # Update children first
        for w in self.children:
            w.dispatch_event('on_update')

    def on_draw(self):
        '''Clear window, and dispatch event in root widget'''
        # Draw
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')

        '''
        if self.show_fps:
            self.fps_display.draw()

        if self.dump_frame:
            self.dump_idx = self.dump_idx + 1
            filename = '%s%05d.%s' % (self.dump_prefix, self.dump_idx,
                                       self.dump_format)
            #print pyglet.image.get_buffer_manager().get_color_buffer().get_texture()
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename=filename)
        '''

        self.draw_mouse_touch()

    def draw_mouse_touch(self):
        '''Compatibility for MouseTouch, drawing a little red circle around
        under each mouse touches.'''
        set_color(0.8, 0.2, 0.2, 0.7)
        for t in [x for x in getAvailableTouchs() if x.device == 'mouse']:
            drawCircle(pos=(t.x, t.y), radius=10)

    def to_widget(self, x, y):
        return (x, y)

    def to_window(self, x, y, initial=True):
        return (x, y)

    def get_root_window(self):
        return self

    def get_parent_window(self):
        return self

    def get_parent_layout(self):
        return None

    def on_key_press(self, symbol, modifiers):
        handler = self.get_on_key_press()
        if handler and handler(symbol, modifiers):
            return True
        if symbol == pyglet.window.key.ESCAPE:
            stopTouchApp()
            return True

    def on_text(self, text):
        handler = self.get_on_text()
        if handler and handler(text):
            return True

    def on_text_motion(self, text):
        handler = self.get_on_text_motion()
        if handler and handler(text):
            return True

    def on_text_motion_select(self, text):
        handler = self.get_on_text_motion_select()
        if handler and handler(text):
            return True

    def on_touch_down(self, touch):
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_up', touch):
                return True

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(-width/2, width/2, -height/2, height/2, 0.1, 1000)
        glScalef(5000,5000,1)
        glTranslatef(-width/2,-height/2,-500)
        glMatrixMode(GL_MODELVIEW)

    def register_event_type(self, event_type):
        self.event_types.append(event_type)

    def flip(self):
        glutSwapBuffers()

    def push_handlers(self, *args, **kwargs):
        '''Push a level onto the top of the handler stack, then attach zero or
        more event handlers.

        If keyword arguments are given, they name the event type to attach.
        Otherwise, a callable's `__name__` attribute will be used.  Any other
        object may also be specified, in which case it will be searched for
        callables with event names.
        '''
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = []

        # Place dict full of new handlers at beginning of stack
        self._event_stack.insert(0, {})
        self.set_handlers(*args, **kwargs)

    def _get_handlers(self, args, kwargs):
        '''Implement handler matching on arguments for set_handlers and
        remove_handlers.
        '''
        for object in args:
            if inspect.isroutine(object):
                # Single magically named function
                name = object.__name__
                if name not in self.event_types:
                    raise Exception('Unknown event "%s"' % name)
                yield name, object
            else:
                # Single instance with magically named methods
                for name in dir(object):
                    if name in self.event_types:
                        yield name, getattr(object, name)
        for name, handler in kwargs.items():
            # Function for handling given event (no magic)
            if name not in self.event_types:
                raise Exception('Unknown event "%s"' % name)
            yield name, handler

    def set_handlers(self, *args, **kwargs):
        '''Attach one or more event handlers to the top level of the handler
        stack.
        
        See `push_handlers` for the accepted argument types.
        '''
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]

        for name, handler in self._get_handlers(args, kwargs):
            self.set_handler(name, handler)

    def set_handler(self, name, handler):
        '''Attach a single event handler.

        :Parameters:
            `name` : str
                Name of the event type to attach to.
            `handler` : callable
                Event handler to attach.

        '''
        # Create event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]

        self._event_stack[0][name] = handler

    def dispatch_events(self):
        glutMainLoopEvent()

    def dispatch_event(self, event_type, *args):
        '''Dispatch a single event to the attached handlers.

        The event is propogated to all handlers from from the top of the stack
        until one returns `EVENT_HANDLED`.  This method should be used only by
        `EventDispatcher` implementors; applications should call
        the ``dispatch_events`` method.

        :Parameters:
            `event_type` : str
                Name of the event.
            `args` : sequence
                Arguments to pass to the event handler.

        '''

        # Don't dispatch event for visible widget if we are not visible
        if event_type in MTWidget.visible_events and not self.visible:
            return

        #assert event_type in self.event_types
        if event_type not in self.event_types:
            return

        # Search handler stack for matching event handlers
        for frame in self._event_stack:
            handler = frame.get(event_type, None)
            if handler:
                try:
                    if handler(*args):
                        return True
                except TypeError:
                    self._raise_dispatch_exception(event_type, args, handler)


        # Check instance for an event handler
        if hasattr(self, event_type):
            try:
                # Statistics
                global _event_stats_activate
                if _event_stats_activate:
                    global _event_stats
                    if not event_type in _event_stats:
                        _event_stats[event_type] = 1
                    else:
                        _event_stats[event_type] = _event_stats[event_type] + 1

                # Call event
                func = getattr(self, event_type)
                if func(*args):
                    return True

            except TypeError, e:
                #print 'error in', self, e
                self._raise_dispatch_exception(
                    event_type, args, getattr(self, event_type))


class MTDisplay(MTWidget):
    '''MTDisplay is a widget that draw a circle
    under every touch on window

    :Parameters:
        `touch_color` : list
            Color of circle under finger
        `radius` : int
            Radius of circle under finger in pixel

    :Styles:
        `touch-color` : color
            Color of circle under finger
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('touch_color', (1,1,0))
        kwargs.setdefault('radius', 20)
        super(MTDisplay, self).__init__(**kwargs)

        self.radius = kwargs['radius']
        self.touch_color = kwargs['touch_color']
        self.touches    = {}


    def apply_css(self, styles):
        if 'touch-color' in styles:
            self.touch_color = styles.get('touch-color')

    def draw(self):
        '''Draw a circle under every touches'''
        set_color(*self.touch_color)
        for touch in getAvailableTouchs():
            drawCircle(pos=(touch.x, touch.y), radius=self.radius)

# Register all base widgets
MTWidgetFactory.register('MTWindow', MTWindow)
MTWidgetFactory.register('MTDisplay', MTDisplay)
