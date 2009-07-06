'''
Simulator: generate touch event with mouse
'''

__all__ = ['MTSimulator']

from pyglet import *
from pyglet.gl import *
from pyglet.window import key
from ..graphx import drawCircle, set_color
from ..input import TouchFactory, Touch
from factory import MTWidgetFactory
from widgets.widget import MTWidget

class MTSimulator(MTWidget):
    '''MTSimulator is a widget who generate touch event from mouse event'''
    def __init__(self, output):
        super(MTSimulator, self).__init__()
        self.touches		= {}
        self.pos			= (100,100)
        self.output			= output
        self.counter		= 0
        self.current_drag	= None

    def draw(self):
        for t in self.touches.values():
            set_color(0.8,0.2,0.2,0.7)
            drawCircle(pos=(t.x, t.y), radius=10)

    def find_touch(self,x,y):
        for t in self.touches.values():
            if (abs(x-t.x) < 10 and abs(y-t.y) < 10):
                return t
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        newTouch = self.find_touch(x,y)
        if newTouch:
            self.current_drag = newTouch
        else:
            self.counter += 1
            id = 'mouse' + str(self.counter)
            rx = x / float(self.get_parent_window().width)
            ry = y / float(self.get_parent_window().height)
            self.current_drag = cur = TouchFactory.get('tuio').create('/tuio/2Dcur', id=id, args=[rx, ry])
            if modifiers & key.MOD_SHIFT:
                cur.is_float_tap = True
            self.touches[id] = cur
            cur.type = Touch.DOWN
            self.output.dispatch_event('on_input', cur)
        return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.current_drag:
            cur = self.current_drag
            rx = x / float(self.get_parent_window().width)
            ry = y / float(self.get_parent_window().height)
            cur.move([rx, ry])
            cur.type = Touch.MOVE
            self.output.dispatch_event('on_input', cur)
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        cur = self.find_touch(x, y)
        if  button == 1 and cur and not (modifiers & key.MOD_CTRL):
            rx = x / float(self.get_parent_window().width)
            ry = y / float(self.get_parent_window().height)
            cur.move([rx, ry])
            cur.type = Touch.UP
            self.output.dispatch_event('on_input', cur)
            del self.touches[cur.id]
        return True

# Register all base widgets
MTWidgetFactory.register('MTSimulator', MTSimulator)
