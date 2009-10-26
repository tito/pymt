'''
Simulator: generate touch event with mouse
'''

__all__ = ['MTSimulator']

from pyglet import *
from pyglet.gl import *
from pyglet.window import key
from ..graphx import drawCircle, set_color
from ..input import Touch
from ..mtpyglet import getEventLoop
from factory import MTWidgetFactory
from widgets.widget import MTWidget

class SimulatorTouch(Touch):
    def __init__(self, id, args):
        super(SimulatorTouch, self).__init__(id, args)

    def depack(self, args):
        self.sx, self.sy = args

class MTSimulator(MTWidget):
    '''MTSimulator is a widget who generate touch event from mouse event'''
    def __init__(self, **kwargs):
        super(MTSimulator, self).__init__(**kwargs)
        self.touches		= {}
        self.pos			= (100,100)
        self.counter		= 0
        self.current_drag	= None

    def draw(self):
        for t in self.touches.values():
            set_color(0.8, 0.2, 0.2, 0.7)
            drawCircle(pos=(t.x, t.y), radius=10)

    def find_touch(self,x,y):
        factor = 10. / self.get_parent_window().width
        for t in self.touches.values():
            if abs(x-t.sx) < factor and abs(y-t.sy) < factor:
                return t
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        rx = x / float(self.get_parent_window().width)
        ry = y / float(self.get_parent_window().height)
        newTouch = self.find_touch(rx, ry)
        if newTouch:
            self.current_drag = newTouch
        else:
            self.counter += 1
            id = 'mouse' + str(self.counter)
            self.current_drag = cur = SimulatorTouch(id=id, args=[rx, ry])
            if modifiers & key.MOD_SHIFT:
                cur.is_double_tap = True
            self.touches[id] = cur
            getEventLoop()._dispatch_input('down', cur)
        return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        rx = x / float(self.get_parent_window().width)
        ry = y / float(self.get_parent_window().height)
        if self.current_drag:
            cur = self.current_drag
            cur.move([rx, ry])
            getEventLoop()._dispatch_input('move', cur)
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        rx = x / float(self.get_parent_window().width)
        ry = y / float(self.get_parent_window().height)
        cur = self.find_touch(rx, ry)
        print cur
        if  button == 1 and cur and not (modifiers & key.MOD_CTRL):
            cur.move([rx, ry])
            del self.touches[cur.id]
            getEventLoop()._dispatch_input('up', cur)
        return True

# Register all base widgets
MTWidgetFactory.register('MTSimulator', MTSimulator)
