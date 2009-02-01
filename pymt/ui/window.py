import sys

from pyglet.gl import *
from pyglet import *
import pymt
from pymt.mtpyglet import TouchWindow
from pymt.ui.simulator import *
from pymt.ui.widget import *

class MTWindowRoot(MTWidget):
    def __init__(self, **kwargs):
        super(MTWindowRoot, self).__init__(**kwargs)

    def draw(self):
        pass

    def get_parent_window(self):
        return self


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
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('color', (.3, .3, .3, 1.0))
        kwargs.setdefault('view', None)
        kwargs.setdefault('fullscreen', None)
        kwargs.setdefault('config', None)
        kwargs.setdefault('show_fps', False)

        self.fps_display =  pyglet.clock.ClockDisplay()

        self.color = kwargs.get('color')
        self.root = MTWindowRoot()

        self.root.parent = self
        if kwargs.get('view'):
            self.root.add_widget(kwargs.get('view'))

        self.sim = MTSimulator(self)
        self.root.add_widget(self.sim)

        try:
            config = kwargs.get('config')
            if not config:
                config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=1)
            super(MTWindow, self).__init__(config)
        except:
            super(MTWindow, self).__init__()

        # use user-options before local options
        if pymt.options.has_key('fullscreen'):
            self.set_fullscreen(pymt.options.get('fullscreen'))
        elif kwargs.get('fullscreen'):
            self.set_fullscreen(kwargs.get('fullscreen'))

        self.show_fps = kwargs.get('show_fps')
        if pymt.options.has_key('show_fps'):
            self.show_fps = True

    def _set_size(self, size):
        self.set_size(*size)
    def _get_size(self):
        return self.get_size()
    size = property(_get_size, _set_size,
            doc='''Return width/height of window''')

    def add_widget(self, w):
        '''Add a widget on window'''
        self.root.add_widget(w)
        self.sim.bring_to_front()

    def remove_widget(self, w):
        '''Remove a widget from window'''
        self.root.remove_widget(w)

    def draw(self):
        '''Clear the window with background color'''
        glClearColor(*self.color)
        self.clear()

    def on_draw(self):
        '''Clear window, and dispatch event in root widget + simulator'''
        self.draw()
        self.root.dispatch_event('on_draw')
        self.sim.draw()
        if self.show_fps:
            self.fps_display.draw()

    def on_touch_down(self, touches, touchID, x, y):
        return self.root.dispatch_event('on_touch_down', touches, touchID, x, y)

    def on_touch_move(self, touches, touchID, x, y):
        return self.root.dispatch_event('on_touch_move', touches, touchID, x, y)

    def on_touch_up(self, touches, touchID, x, y):
        return self.root.dispatch_event('on_touch_up', touches, touchID, x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.root.dispatch_event('on_mouse_press', x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.root.dispatch_event('on_mouse_drag', x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.root.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_object_down(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_down', touches, touchID, id, x, y,angle)

    def on_object_move(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_move', touches, touchID, id, x, y,angle)

    def on_object_up(self, touches, touchID, id, x, y,angle):
        self.root.dispatch_event('on_object_up', touches, touchID, id, x, y,angle)


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
