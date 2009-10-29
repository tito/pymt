'''
Window package: provide a window + a touch display
'''

__all__ = ['BaseWindow', 'MTWindow', 'MTDisplay']

import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
import pymt
from ..logger import pymt_logger
from ..base import stopTouchApp, getAvailableTouchs, setWindow, touch_event_listeners
from ..clock import getClock
from ..graphx import set_color, drawCircle, drawLabel
from ..modules import pymt_modules
from ..utils import curry
from ..event import EventDispatcher
from colors import css_get_style
from factory import MTWidgetFactory
from widgets import MTWidget

glut_window = None

class BaseWindow(EventDispatcher):
    '''BaseWindow is a abstract window widget, for any window implementation.

    :Parameters:
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

    :Styles:
        `bg-color` : color
            Background color of window
    '''
    _have_multisample = None
    _modifiers = 0
    _size = (0, 0)

    def __init__(self, **kwargs):
        if self.__class__ == BaseWindow:
            raise NotImplementedError, 'class BaseWindow is abstract'

        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)
        kwargs.setdefault('style', {})
        kwargs.setdefault('shadow', False)

        super(BaseWindow, self).__init__()

        # shadow window ?
        self.shadow = kwargs.get('shadow')

        # event subsystem
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
        self.create_window()

        # set out window as the main pymt window
        setWindow(self)

        # apply styles for window
        self.cssstyle = {}
        style = css_get_style(widget=self)
        self.apply_css(style)

        # apply inline css
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

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
        '''

        # show fps if asked
        self.show_fps = kwargs.get('show_fps')
        if pymt.pymt_config.getboolean('pymt', 'show_fps'):
            self.show_fps = True

        # initialize dump image
        self.dump_frame     = pymt.pymt_config.getboolean('dump', 'enabled')
        self.dump_prefix    = pymt.pymt_config.get('dump', 'prefix')
        self.dump_format    = pymt.pymt_config.get('dump', 'format')
        self.dump_idx       = 0

        # for shadow window, we've done !
        if self.shadow:
            return

        # configure the window
        self.configure(params)

        # init some gl
        self.init_gl()

        # attach modules + listener event
        pymt_modules.register_window(self)
        touch_event_listeners.append(self)

    def close(self):
        '''Close the window'''
        pass

    def create_window(self):
        '''Will create the main window'''
        pass

    def configure(self, params):
        '''Will adapt main window for configuration'''
        pass

    def flip(self):
        '''Flip between buffers'''
        pass

    def dispatch_events(self):
        '''Dispatch all events from windows'''
        pass

    def apply_css(self, styles):
        self.cssstyle.update(styles)

    def _get_modifiers(self):
        return self._modifiers
    modifiers = property(_get_modifiers)

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return
        self._size = size
        pymt_logger.debug('Resize window to %s' % str(self.size))
        self.dispatch_event('on_resize', *size)
    size = property(_get_size, _set_size)

    def _get_width(self):
        return self._size[0]
    width = property(_get_width)

    def _get_height(self):
        return self._size[1]
    height = property(_get_height)

    def init_gl(self):
        # check if window have multisample
        """
        if MTWindow._have_multisample is None:
            s = glGetIntegerv(GL_SAMPLES)
            if s > 0:
                pymt.pymt_logger.debug('Multisampling is available (%d)' % s.value)
                MTWindow._have_multisample = True
            else:
                pymt.pymt_logger.debug('Multisampling is not available')
                MTWindow._have_multisample = False
        """

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

    def draw(self):
        '''Clear the window with background color'''
        glClearColor(*self.cssstyle.get('bg-color'))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

    def on_update(self):
        '''Event called when window are update the widget tree.
        (Usually before on_draw call.)
        '''
        for w in self.children:
            w.dispatch_event('on_update')

    def on_draw(self):
        '''Event called when window we are drawing window.
        This function are cleaning the buffer with bg-color css,
        and call children drawing + show fps timer on demand'''

        # draw our window
        self.draw()

        # then, draw childrens
        for w in self.children:
            w.dispatch_event('on_draw')

        if self.show_fps:
            fps = getClock().get_fps()
            drawLabel(label='FPS: %.2f' % float(fps),
                center=False, pos=(4, self.height - 4),
                font_size=10, bold=False)

        '''
        if self.dump_frame:
            self.dump_idx = self.dump_idx + 1
            filename = '%s%05d.%s' % (self.dump_prefix, self.dump_idx,
                                       self.dump_format)
            #print pyglet.image.get_buffer_manager().get_color_buffer().get_texture()
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename=filename)
        '''

        self.draw_mouse_touch()

    def on_touch_down(self, touch):
        '''Event called when a touch is down'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_down', touch):
                return True

    def on_touch_move(self, touch):
        '''Event called when a touch move'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_move', touch):
                return True

    def on_touch_up(self, touch):
        '''Event called when a touch up'''
        touch.scale_for_screen(*self.size)
        for w in reversed(self.children):
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

    def on_close(self, *largs):
        '''Event called when the window is closed'''
        pymt_modules.unregister_window(self)
        if self in touch_event_listeners:
            touch_event_listeners.remove(self)

    def on_mouse(self, button, state, x, y):
        '''Event called when mouse is in action (press/release)'''
        pass

    def on_mouse_motion(self, x, y, button, modifiers):
        '''Event called when mouse is moving, with buttons pressed'''
        pass

    def on_keyboard(self, key, x, y):
        '''Event called when keyboard is in action'''
        pass


class MTWindow(BaseWindow):
    def __init__(self, **kwargs):
        super(MTWindow, self).__init__(**kwargs)

    def create_window(self):
        global glut_window
        if glut_window is None:

            # for shadow window, make it invisible
            if self.shadow:
                pymt_logger.debug('Set next window as Shadow window (1x1)')
                glutInitWindowPosition(0, 0)
                glutInitWindowSize(1, 1)

            # init GLUT !
            pymt_logger.debug('GLUT initialization')
            glutInit('')
            glutInitDisplayMode(
                GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH |
                GLUT_MULTISAMPLE | GLUT_STENCIL | GLUT_ACCUM)

            # create the window
            pymt_logger.debug('Create the window')
            glut_window = glutCreateWindow('pymt')

            # hide the shadow...
            if self.shadow:
                # FIXME seem not working... why ??
                glutHideWindow()

        super(MTWindow, self).create_window()

    def configure(self, params):
        # update window size
        glutShowWindow()
        self.size = params['width'], params['height']
        if params['fullscreen']:
            pymt_logger.debug('Set window to fullscreen mode')
            glutFullScreen()

        # register all callbcaks
        glutReshapeFunc(curry(self.dispatch_event, 'on_resize'))
        glutMouseFunc(curry(self.dispatch_event, 'on_mouse'))
        glutMotionFunc(curry(self.dispatch_event, 'on_mouse_motion'))
        glutKeyboardFunc(curry(self.dispatch_event, 'on_keyboard'))

        super(MTWindow, self).configure(params)

    def close(self):
        global glut_window
        if glut_window:
            glutDestroyWindow(glut_window)
            glut_window = None
        super(MTWindow, self).close()

    def on_keyboard(self, key, x, y):
        self._modifiers = glutGetModifiers()
        if ord(key) == 27:
            stopTouchApp()
        super(MTWindow, self).on_keyboard(key, x, y)

    def dispatch_events(self):
        glutMainLoopEvent()
        super(MTWindow, self).dispatch_events()

    def _set_size(self, size):
        glutReshapeWindow(*size)
        super(MTWindow, self)._set_size(size)

    def flip(self):
        glutSwapBuffers()
        super(MTWindow, self).flip()


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
