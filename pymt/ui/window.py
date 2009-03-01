import sys

from pyglet.gl import *
from pyglet import *
import pymt
from pymt.mtpyglet import TouchWindow
from pymt.ui.simulator import *
from pymt.ui.widgets.widget import *


class MTWindow(TouchWindow):
    '''MTWindow is a window widget who use MTSimulator
    for generating touch event with mouse.
    Use MTWindow as main window application.

    :Parameters:
        `color` : list
            Background color of window
        `view` : `MTWidget`
            Default view to add on window
        `fullscreen` : bool
            Make window as fullscreen
        `config` : `Config`
            Default configuration to pass on TouchWindow

    :Styles:
        `bg-color` : color
            Background color of window
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('view', None)
        kwargs.setdefault('fullscreen', None)
        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)

        styles = colors.css_get_style(widget=self)
        self.apply_css(styles)

        self.fps_display =  pyglet.clock.ClockDisplay()

        self.on_key_press_handlers = []
        self.on_text_handlers = []
        self.on_text_motion_handlers = []
        self.on_text_motion_select_handlers = []

        self.children = []
        if kwargs.has_key('color'):
            self.color = kwargs.get('color')

        self.parent = self
        if kwargs.get('view'):
            self.add_widget(kwargs.get('view'))

        self.sim = MTSimulator(self)
        self.add_widget(self.sim)

        try:
            config = kwargs.get('config')
            if not config:
                config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=1)
            super(MTWindow, self).__init__(config)
        except:
            super(MTWindow, self).__init__()

        # use user-options before local options
        if kwargs.get('fullscreen') is None:
            self.set_fullscreen(pymt.pymt_config.getboolean('pymt', 'fullscreen'))
        else:
            self.set_fullscreen(kwargs.get('fullscreen'))

        self.show_fps = kwargs.get('show_fps')
        if pymt.pymt_config.getboolean('pymt', 'show_fps'):
            self.show_fps = True

        # initialize dump image
        self.dump_frame     = pymt.pymt_config.getboolean('dump', 'enabled')
        self.dump_prefix    = pymt.pymt_config.get('dump', 'prefix')
        self.dump_format    = pymt.pymt_config.get('dump', 'format')
        self.dump_idx       = 0

    def _set_size(self, size):
        self.set_size(*size)
    def _get_size(self):
        return self.get_size()
    size = property(_get_size, _set_size,
            doc='''Return width/height of window''')

    def apply_css(self, styles):
        if styles.has_key('bg-color'):
            self.color = styles.get('bg-color')

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
        self.sim.bring_to_front()

    def remove_widget(self, w):
        '''Remove a widget from window'''
        self.children.remove(w)
        w.parent = None

    def draw(self):
        '''Clear the window with background color'''
        glClearColor(*self.color)
        self.clear()

    def on_draw(self):
        '''Clear window, and dispatch event in root widget + simulator'''
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')

        self.sim.dispatch_event('on_draw')

        if self.show_fps:
            self.fps_display.draw()

        if self.dump_frame:
            self.dump_idx = self.dump_idx + 1
            filename = '%s%05d.%s' % (self.dump_prefix, self.dump_idx,
                                       self.dump_format)
            #print pyglet.image.get_buffer_manager().get_color_buffer().get_texture()
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename=filename)

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

    def on_touch_down(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_down', touches, touchID, x, y):
                return True

    def on_touch_move(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_move', touches, touchID, x, y):
                return True

    def on_touch_up(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_up', touches, touchID, x, y):
                return True

    def on_mouse_press(self, x, y, button, modifiers):
        for w in reversed(self.children):
            if w.dispatch_event('on_mouse_press',x, y, button, modifiers):
                return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for w in reversed(self.children):
            if w.dispatch_event('on_mouse_drag',x, y, dx, dy, button, modifiers):
                return True

    def on_mouse_release(self, x, y, button, modifiers):
        for w in reversed(self.children):
            if w.dispatch_event('on_mouse_release', x, y, button, modifiers):
                return True

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_down', touches, touchID,id, x, y, angle):
                return True

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_move', touches, touchID,id, x, y, angle):
                return True

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            if w.dispatch_event('on_object_up', touches, touchID,id, x, y,angle):
                return True

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
        `color` : list
            Color of circle under finger
        `radius` : int
            Radius of circle under finger in pixel
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('radius', 10)
        kwargs.setdefault('color', (1.0, 1.0, 1.0, 0.4))
        super(MTDisplay, self).__init__(**kwargs)
        self.touches    = {}
        self.radius     = kwargs.get('radius')

    def draw(self):
        '''Draw a circle under every touches'''
        glColor4f(*self.color)
        for id in self.touches:
            drawCircle(pos=self.touches[id], radius=self.radius)

    def on_touch_down(self, touches, touchID, x, y):
        self.touches[touchID] = (x,y)

    def on_touch_move(self, touches, touchID, x, y):
        self.touches[touchID] = (x,y)

    def on_touch_up(self, touches, touchID, x, y):
        if self.touches.has_key(touchID):
            del self.touches[touchID]


# Register all base widgets
MTWidgetFactory.register('MTWindow', MTWindow)
MTWidgetFactory.register('MTDisplay', MTDisplay)
