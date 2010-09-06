'''
Window package: provide a window + a touch display

For windowing system, we try to use the best windowing system available for
your system. Actually, theses libraries are handled :

    * PyGame (wrapper around SDL)
    * GLUT (last solution, really buggy :/)

'''

__all__ = ('BaseWindow', 'MTWindow', 'MTDisplay')

import os
from OpenGL.GL import GL_VERSION, GL_FASTEST, GL_NICEST, GL_LINE_SMOOTH, \
        GL_LINE_SMOOTH_HINT, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, \
        GL_MODELVIEW, GL_PROJECTION, \
        glGetString, glClear, glClearColor, glEnable, glHint, \
        glViewport, glMatrixMode, glLoadIdentity, glFrustum, glScalef, \
        glTranslatef

import pymt
from pymt.utils import SafeList
from pymt.logger import pymt_logger
from pymt.base import getCurrentTouches, setWindow, touch_event_listeners
from pymt.clock import getClock
from pymt.graphx import set_color, drawCircle, drawLabel, drawRectangle, drawCSSRectangle
from pymt.modules import pymt_modules
from pymt.event import EventDispatcher
from pymt.ui.colors import css_get_style
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets import MTWidget

class BaseWindow(EventDispatcher):
    '''BaseWindow is a abstract window widget, for any window implementation.

    .. warning::

        The parameters are not working in normal case. Because at import, PyMT
        create a default OpenGL window, to add the ability to use OpenGL
        directives, texture creation.. before creating MTWindow.
        If you don't like this behavior, you can include before the very first
        import of PyMT ::

            import os
            os.environ['PYMT_SHADOW'] = '0'
            from pymt import *

        This will forbid PyMT to create the default window !


    :Parameters:
        `fullscreen`: bool
            Make window as fullscreen
        `width`: int
            Width of window
        `height`: int
            Height of window
        `vsync`: bool
            Vsync window

    :Styles:
        `bg-color`: color
            Background color of window
    '''

    __instance = None
    __initialized = False
    _wallpaper = None
    _wallpaper_position = 'norepeat'

    def __new__(cls, **kwargs):
        if cls.__instance is None:
            cls.__instance = EventDispatcher.__new__(cls)
        return cls.__instance

    def __init__(self, **kwargs):

        kwargs.setdefault('force', False)
        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)
        kwargs.setdefault('style', {})

        # don't init window 2 times,
        # except if force is specified
        if self.__initialized and not kwargs.get('force'):
            return

        super(BaseWindow, self).__init__()

        # init privates
        self._modifiers = []
        self._size = (0, 0)

        # event subsystem
        self.register_event_type('on_flip')
        self.register_event_type('on_draw')
        self.register_event_type('on_update')
        self.register_event_type('on_resize')
        self.register_event_type('on_close')
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_up')
        self.register_event_type('on_mouse_down')
        self.register_event_type('on_mouse_move')
        self.register_event_type('on_mouse_up')
        self.register_event_type('on_keyboard')
        self.register_event_type('on_key_down')
        self.register_event_type('on_key_up')

        # set out window as the main pymt window
        setWindow(self)

        # apply styles for window
        self.style = {}
        style = css_get_style(widget=self)
        self.apply_css(style)

        # apply inline css
        self._inline_style = kwargs.get('style')
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

        self.children = SafeList()
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
            params['fullscreen'] = pymt.pymt_config.get('graphics', 'fullscreen')
            if params['fullscreen'] not in ('auto', 'fake'):
                params['fullscreen'] = params['fullscreen'].lower() in \
                    ('true', '1', 'yes', 'yup')

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

        # show fps if asked
        self.show_fps = kwargs.get('show_fps')
        if pymt.pymt_config.getboolean('pymt', 'show_fps'):
            self.show_fps = True

        # configure the window
        self.create_window(params)

        # init some gl
        self.init_gl()

        # attach modules + listener event
        pymt_modules.register_window(self)
        touch_event_listeners.append(self)

        # mark as initialized
        self.__initialized = True

    def toggle_fullscreen(self):
        '''Toggle fullscreen on window'''
        pass

    def close(self):
        '''Close the window'''
        pass

    def create_window(self, params):
        '''Will create the main window and configure it'''
        pass

    def on_flip(self):
        '''Flip between buffers (event)'''
        self.flip()

    def flip(self):
        '''Flip between buffers'''
        pass

    def dispatch_events(self):
        '''Dispatch all events from windows'''
        pass

    def apply_css(self, styles):
        '''Called at __init__ time to applied css attribute in current class.
        '''
        self.style.update(styles)

    def reload_css(self):
        '''Called when css want to be reloaded from scratch'''
        self.style = {}
        style = css_get_style(widget=self)
        self.apply_css(style)
        if len(self._inline_style):
            self.apply_css(self._inline_style)

    def _get_modifiers(self):
        return self._modifiers
    modifiers = property(_get_modifiers)

    def _set_size(self, size):
        if super(BaseWindow, self)._set_size(size):
            pymt_logger.debug('Window: Resize window to %s' % str(self.size))
            self.dispatch_event('on_resize', *size)
            return True
        return False
    size = property(EventDispatcher._get_size, _set_size)

    # make some property read-only
    width = property(EventDispatcher._get_width)
    height = property(EventDispatcher._get_height)
    center = property(EventDispatcher._get_center)

    def _get_wallpaper(self):
        return self._wallpaper
    def _set_wallpaper(self, filename):
        self._wallpaper = pymt.Image(filename)
    wallpaper = property(_get_wallpaper, _set_wallpaper,
            doc='Get/set the wallpaper (must be a valid filename)')

    def _get_wallpaper_position(self):
        return self._wallpaper_position
    def _set_wallpaper_position(self, position):
        self._wallpaper_position = position
    wallpaper_position = property(
            _get_wallpaper_position, _set_wallpaper_position,
            doc='Get/set the wallpaper position (can be one of' +
                '"norepeat", "center", "repeat", "scale", "strech")')

    def init_gl(self):
        version = glGetString(GL_VERSION)
        pymt_logger.info('Window: OpenGL version <%s>' % str(version))

        line_smooth = pymt.pymt_config.getint('graphics', 'line_smooth')
        if line_smooth:
            if line_smooth == 1:
                hint = GL_FASTEST
            else:
                hint = GL_NICEST
            glHint(GL_LINE_SMOOTH_HINT, hint)
            glEnable(GL_LINE_SMOOTH)

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

    def clear(self):
        '''Clear the window with background color'''
        glClearColor(*self.style.get('bg-color'))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def draw(self):
        '''Draw the window background'''
        self.clear()
        if self.wallpaper is not None:
            self.draw_wallpaper()

    def draw_wallpaper(self):
        wallpaper = self.wallpaper
        if self.wallpaper_position == 'center':
            wallpaper.x = (self.width - wallpaper.width) / 2
            wallpaper.y = (self.height - wallpaper.height) / 2
            wallpaper.draw()
        elif self.wallpaper_position == 'repeat':
            r_x = float(self.width) / wallpaper.width
            r_y = float(self.height) / wallpaper.height
            if int(r_x) != r_x:
                r_x = int(r_x) + 1
            if int(r_y) != r_y:
                r_y = int(r_y) + 1
            for x in xrange(int(r_x)):
                for y in xrange(int(r_y)):
                    wallpaper.x = x * wallpaper.width
                    wallpaper.y = y * wallpaper.height
                    wallpaper.draw()
        elif self.wallpaper_position == 'scale':
            wallpaper.size = self.size
            wallpaper.draw()

        elif self.wallpaper_position == 'strech':
            w = self.width
            h = (self.width * wallpaper.height) / wallpaper.width
            if h < self.height:
                h = self.height
                w = (self.height * wallpaper.width) / wallpaper.height
            wallpaper.size = w, h
            wallpaper.pos = -(w - self.width) / 2, -(h - self.height) / 2
            wallpaper.draw()
        else:
            # no-repeat or any other options
            wallpaper.draw()


    def draw_mouse_touch(self):
        '''Compatibility for MouseTouch, drawing a little red circle around
        under each mouse touches.'''
        set_color(0.8, 0.2, 0.2, 0.7)
        for t in [x for x in getCurrentTouches() if x.device == 'mouse']:
            drawCircle(pos=(t.x, t.y), radius=10)

    def to_widget(self, x, y, initial=True, relative=False):
        return (x, y)

    def to_window(self, x, y, initial=True, relative=False):
        return (x, y)

    def get_root_window(self):
        return self

    def get_parent_window(self):
        return self

    def get_parent_layout(self):
        return None

    def on_update(self):
        '''Event called when window are update the widget tree.
        (Usually before on_draw call.)
        '''
        for w in self.children[:]:
            w.dispatch_event('on_update')

    def on_draw(self):
        '''Event called when window we are drawing window.
        This function are cleaning the buffer with bg-color css,
        and call children drawing + show fps timer on demand'''

        # draw our window
        self.draw()

        # then, draw childrens
        for w in self.children[:]:
            w.dispatch_event('on_draw')

        if self.show_fps:
            fps = getClock().get_fps()
            drawLabel(label='FPS: %.2f' % float(fps),
                center=False, pos=(0, 0),
                font_size=10, bold=False)

        self.draw_mouse_touch()

    def on_touch_down(self, touch):
        '''Event called when a touch is down'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        '''Event called when a touch move'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        '''Event called when a touch up'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children[:]):
            if w.dispatch_event('on_touch_up', touch):
                return True

    def on_resize(self, width, height):
        '''Event called when the window is resized'''
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(-width / 2, width / 2, -height / 2, height / 2, .1, 1000)
        glScalef(5000, 5000, 1)
        glTranslatef(-width / 2, -height / 2, -500)
        glMatrixMode(GL_MODELVIEW)

        for w in self.children:
            shw, shh = w.size_hint
            if shw and shh:
                w.size = shw * width, shh * height
            elif shw:
                w.width = shw * width
            elif shh:
                w.height = shh * height

    def on_close(self, *largs):
        '''Event called when the window is closed'''
        pymt_modules.unregister_window(self)
        if self in touch_event_listeners[:]:
            touch_event_listeners.remove(self)

    def on_mouse_down(self, x, y, button, modifiers):
        '''Event called when mouse is in action (press/release)'''
        pass

    def on_mouse_move(self, x, y, modifiers):
        '''Event called when mouse is moving, with buttons pressed'''
        pass

    def on_mouse_up(self, x, y, button, modifiers):
        '''Event called when mouse is moving, with buttons pressed'''
        pass

    def on_keyboard(self, key, scancode=None, unicode=None):
        '''Event called when keyboard is in action

        .. warning::
            Some providers can skip `scancode` or `unicode` !!
        '''
        pass

    def on_key_down(self, key, scancode=None, unicode=None):
        '''Event called when a key is down (same arguments as on_keyboard)'''
        pass

    def on_key_up(self, key, scancode=None, unicode=None):
        '''Event called when a key is up (same arguments as on_keyboard)'''
        pass


class MTDisplay(MTWidget):
    '''MTDisplay is a widget that draw a circle
    under every touch on window.

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
        kwargs.setdefault('touch_color', (1, 1, 0))
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
        for touch in getCurrentTouches():
            drawCircle(pos=(touch.x, touch.y), radius=self.radius)

# Searching the best provider
MTWindow = None
if not 'PYMT_DOC' in os.environ:
    if 'pygame' in pymt.pymt_options['window']:
        try:
            import win_pygame
            MTWindow = win_pygame.MTWindowPygame
            pymt_logger.info('Window: use Pygame as window provider.')
        except ImportError:
            pymt_logger.debug('Window: Unable to use Pygame as provider.')

    if MTWindow is None and 'glut' in pymt.pymt_options['window']:
        try:
            import win_glut
            MTWindow = win_glut.MTWindowGlut
            pymt_logger.info('Window: use GLUT as window provider.')
        except ImportError:
            pymt_logger.debug('Window: Unable to use GLUT as provider.')

    # No window provider ?
    if MTWindow is None:
        pymt_logger.critical('Window: No provider found (configuration is %s)' %
            str(pymt.pymt_options['window']))

# Register all base widgets
MTWidgetFactory.register('MTWindow', MTWindow)
MTWidgetFactory.register('MTDisplay', MTDisplay)
