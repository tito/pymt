'''
Window package: provide a window + a touch display
'''

__all__ = ['MTWindow', 'MTDisplay']

import sys
import pyglet
from pyglet.gl import *
from pyglet import *
import pymt
from ..mtpyglet import TouchWindow, stopTouchApp, getAvailableTouchs
from ..graphx import set_color, drawCircle
from ..modules import pymt_modules
from colors import css_get_style
from factory import MTWidgetFactory
from widgets import MTWidget
from simulator import MTSimulator


class MTWindow(TouchWindow):
    '''MTWindow is a window widget who use MTSimulator
    for generating touch event with mouse.
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
    def __init__(self, **kwargs):
        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)
        kwargs.setdefault('enablemouse', True)
        kwargs.setdefault('style', {})

        # apply styles for window
        self.cssstyle = {}
        style = css_get_style(widget=self)
        self.apply_css(style)

        # apply inline css
        if len(kwargs.get('style')):
            self.apply_css(kwargs.get('style'))

        # initialize fps clock
        self.fps_display =  pyglet.clock.ClockDisplay()

        # initialize handlers list
        self.on_key_press_handlers = []
        self.on_text_handlers = []
        self.on_text_motion_handlers = []
        self.on_text_motion_select_handlers = []

        self.children = []
        self.parent = self

        # add view + simulator
        if 'view' in kwargs:
            self.add_widget(kwargs.get('view'))
            
         # Accept or don't accept mouse input.
        enablemouse = kwargs.get('enablemouse')
        
        try:
            if pymt.pymt_config.getboolean('pymt', 'enablemouse') == False:
                enablemouse = False
        except:
            pass #They probably just don't have it added to their config file.

        if enablemouse:
            self.sim = MTSimulator()
            self.add_widget(self.sim)
        else:
            self.sim = False

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
        pymt_modules.register_window(self)

    def apply_css(self, styles):
        self.cssstyle.update(styles)

    def on_close(self, *largs):
        pymt_modules.unregister_window(self)
        super(MTWindow, self).on_close(*largs)

    def _set_size(self, size):
        self.set_size(*size)
    def _get_size(self):
        return self.get_size()
    size = property(_get_size, _set_size,
            doc='''Return width/height of window''')

    def init_gl(self):
        # check if window have multisample
        if MTWindow.have_multisample is None:
            s = (GLint)()
            glGetIntegerv(GL_SAMPLES, s)
            if s.value > 0:
                pymt.pymt_logger.debug('Multisampling is available (%d)' % s.value)
                MTWindow.have_multisample = True
            else:
                pymt.pymt_logger.debug('Multisampling is not available')
                MTWindow.have_multisample = False

        polygon_smooth = pymt.pymt_config.getint('graphics', 'polygon_smooth')
        if polygon_smooth:
            if polygon_smooth == 1:
                hint = GL_FASTEST
            else:
                hint = GL_NICEST
            if MTWindow.have_multisample:
                glEnable(GL_MULTISAMPLE_ARB)
                glHint(GL_MULTISAMPLE_FILTER_HINT_NV, hint)
            else:
                glEnable(GL_POLYGON_SMOOTH)
                glHint(GL_POLYGON_SMOOTH_HINT, hint)

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
        if self.sim:
            self.sim.bring_to_front()

    def remove_widget(self, w):
        '''Remove a widget from window'''
        if not w in self.children:
            return
        self.children.remove(w)
        w.parent = None

    def draw(self):
        '''Clear the window with background color'''
        glClearColor(*self.cssstyle.get('bg-color'))
        self.clear()

    def on_draw(self):
        '''Clear window, and dispatch event in root widget + simulator'''
        # Update children first
        for w in self.children:
            w.dispatch_event('on_update')

        # Draw
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')
        
        if self.sim:
            self.sim.dispatch_event('on_draw')

        if self.show_fps:
            self.fps_display.draw()

        if self.dump_frame:
            self.dump_idx = self.dump_idx + 1
            filename = '%s%05d.%s' % (self.dump_prefix, self.dump_idx,
                                       self.dump_format)
            #print pyglet.image.get_buffer_manager().get_color_buffer().get_texture()
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename=filename)

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

    def on_mouse_press(self, x, y, button, modifiers):
        if self.sim:
            return self.sim.dispatch_event('on_mouse_press', x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.sim:
            return self.sim.dispatch_event('on_mouse_drag', x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.sim:
            return self.sim.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glFrustum(-width/2, width/2, -height/2, height/2, 0.1, 1000)
        glScalef(5000,5000,1)
        glTranslatef(-width/2,-height/2,-500)
        glMatrixMode(gl.GL_MODELVIEW)


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
