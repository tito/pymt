from pyglet import *
from pyglet.gl import *
from pyglet.window import key
from pymt.graphx import *
from pymt.mtpyglet import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widget import MTWidget

class MTSimulator(MTWidget):
    """MTSimulator is a widget who generate touch event from mouse event"""
    def __init__(self, output, parent=None):
        MTWidget.__init__(self, parent)
        self.touches = {}
        self.pos=(100,100)
        self.output = output
        self.counter = 0
        self.current_drag = None

    def draw(self):
        for t in self.touches.values():
            p = (t.xpos,t.ypos)
            glColor4f(0.8,0.2,0.2,0.7)
            drawCircle(pos=p, radius=10)

    def find_touch(self,x,y):
        for t in self.touches.values():
            if (abs(x-t.xpos) < 10 and abs(y-t.ypos) < 10):
                return t
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        newTouch = self.find_touch(x,y)
        if newTouch:
            self.current_drag = newTouch
        else: #new touch is added 
            self.counter += 1
            id = 'mouse'+str(self.counter)
            self.current_drag = cursor = Tuio2DCursor(id, [x,y])
            self.touches[id] = cursor
            self.output.dispatch_event('on_touch_down', self.touches, id, x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        cur = self.current_drag
        cur.xpos, cur.ypos = x,y
        self.output.dispatch_event('on_touch_move', self.touches, cur.blobID, x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        t = self.find_touch(x,y)
        if  button == 1 and t and not(modifiers & key.MOD_CTRL):
            self.output.dispatch_event('on_touch_up', self.touches, self.current_drag.blobID, x, y)
            del self.touches[self.current_drag.blobID]

# Register all base widgets
MTWidgetFactory.register('MTSimulator', MTSimulator)
