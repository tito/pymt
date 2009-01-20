import sys

from pyglet.gl import *
from pyglet import *
from pymt.mtpyglet import TouchWindow
from pymt.ui.simulator import *
from pymt.ui.widget import *

class MTWindowRoot(MTWidget):
    def draw(self):
        pass

class MTWindow(TouchWindow):
    """MTWindow is a window widget who use MTSimulator
       for generating touch event with mouse.
       Use MTWindow as main window application.
    """

    def __init__(self, view=None, fullscreen=False, config=None, color=(.3,.3,.3,1.0)):
        self.color = color
        self.root = MTWindowRoot()

        self.root.parent = self
        if view:
            self.root.add_widget(view)

        self.sim = MTSimulator(self)
        self.root.add_widget(self.sim)

        try:
            if not config:
                config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=1)
                TouchWindow.__init__(self, config)
        except:
            TouchWindow.__init__(self)
            if fullscreen:
                self.set_fullscreen()

    def add_widget(self, w):
        self.root.add_widget(w)
        self.sim.bring_to_front()

    def remove_widget(self, w):
        self.root.remove_widget(w)

    def on_draw(self):
        glClearColor(*self.color)
        self.clear()
        self.root.dispatch_event('on_draw')
        self.sim.draw()

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
    """MTDisplay is a widget that draw a circle under every touch on window"""
    def __init__(self, color=(1.0, 1.0, 1.0, 0.4), radius=10, **kargs):
        MTWidget.__init__(self, color=color)
        self.touches    = {}
        self.radius     = radius

    def draw(self):
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
