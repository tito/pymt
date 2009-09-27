'''
Simulator: generate touch event with mouse
'''

__all__ = ['MTSimulator']

#from pyglet import *
#from pyglet.gl import *
#from pyglet.window import key
import pymtcore
from ..graphx import drawCircle, set_color
from ..input import TouchFactory
from ..base import getEventLoop
from factory import MTWidgetFactory
from widgets.widget import MTWidget

class MTSimulator(MTWidget):
    '''MTSimulator is a widget who generate touch event from mouse event'''
    def __init__(self, **kwargs):
        super(MTSimulator, self).__init__(**kwargs)
        self.touches		= {}
        self.pos			= (100,100)
        self.counter		= 0
        self.current_drag	= None

    def draw(self):
        set_color(0.8,0.2,0.2,0.7)
        for t in self.touches.values():
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
            ry = 1. - (y / float(self.get_parent_window().height))
            self.current_drag = cur = TouchFactory.get('tuio').create('/tuio/2Dcur', id=id, args=[rx, ry])
            #if modifiers & key.MOD_SHIFT:
            #    cur.is_double_tap = True
            self.touches[id] = cur
            getEventLoop().post_dispatch_input('down', cur)
        return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.current_drag:
            cur = self.current_drag
            rx = x / float(self.get_parent_window().width)
            ry = 1. - (y / float(self.get_parent_window().height))
            cur.move([rx, ry])
            getEventLoop().post_dispatch_input('move', cur)
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        cur = self.find_touch(x, y)
        if button == 1 and cur:# and not (modifiers & key.MOD_CTRL):
            rx = x / float(self.get_parent_window().width)
            ry = 1. - (y / float(self.get_parent_window().height))
            cur.move([rx, ry])
            del self.touches[cur.id]
            getEventLoop().post_dispatch_input('up', cur)
        self.current_drag = None
        return True

# Register all base widgets
MTWidgetFactory.register('MTSimulator', MTSimulator)
