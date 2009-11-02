# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Touch Tracer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = ''

from OpenGL.GL import *
from pymt import *
from random import random

label = Label('', font_size=12, anchor_x='left', anchor_y='bottom')
label2 = Label('', font_size=10, anchor_x='left', anchor_y='top')
crosshair = Image.load('../touchtracer/crosshair.png')
crosshair.scale = 0.6


def drawLabel(x,y, ID):
    label.text = 'ID: %s' % str(ID)
    label2.text = 'x:%d y:%d' % (int(x), int(y))
    label.x = label2.x = x + 30
    label.y = label2.y = y
    label.draw()
    label2.draw()
    crosshair.x = x - crosshair.width / 2.
    crosshair.y = y - crosshair.height / 2.
    crosshair.draw()


class TouchTracer(MTWidget):
    def __init__(self, **kwargs):
        super(TouchTracer, self).__init__(**kwargs)
        self.touchPositions = {}

    def on_touch_down(self, touch):
        color = (random(), random(), random())
        self.touchPositions[touch.id] = [(touch.id,color,touch.x,touch.y)]


    def on_touch_up(self, touch):
        if touch.id in self.touchPositions:
            del self.touchPositions[touch.id]


    def on_touch_move(self, touch):
        if touch.id in self.touchPositions:
            self.touchPositions[touch.id].append((touch.x,touch.y))


    def draw(self):
        set_brush('../touchtracer/particle.png', 10)
        w = self.get_parent_window()
        set_color(.2, .2, .2)
        drawRectangle(size=w.size)
        for p in self.touchPositions:
            lines = []
            touchID,color,x,y = self.touchPositions[p][0]
            glColor3d(*color)
            lines += [x, y]
            for pos in self.touchPositions[p][1:]:
                lines += pos
            if len(lines) > 2:
                paintLine(lines)
            x, y = lines[-2:]
            drawLabel(x,y, touchID)

def pymt_plugin_activate(w, ctx):
    ctx.c = TouchTracer()
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
