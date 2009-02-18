from pymt import *
from pyglet.gl import *

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'GL Paint'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_EMAIL = 'thomas.hansen@gmail.com'
PLUGIN_DESCRIPTION = 'This is a simple paint canvas.'

#import psyco
#psyco.profile(0.7)


class Canvas(MTWidget):
    def __init__(self, min=0, max=100, pos=(0,0), size=(640,480)):
        MTWidget.__init__(self, pos=pos, size=size)
        self.touch_positions = {}
        self.fbo = Fbo((self.width, self.height), push_viewport=False)
        self.bgcolor = (0.8,0.8,0.7,1.0)
        self.color = (0,1,0,1.0)
        try:
            setBrush('../touchtracer/particle.png')
        except:
            setBrush('touchtracer/particle.png')
        self.clear()

    def clear(self):
        self.fbo.bind()
        glClearColor(*self.bgcolor)
        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(1,0,1,1)
        self.fbo.release()

    def draw(self):
        glColor4f(1,1,1,1)
        drawTexturedRectangle( self.fbo.texture, size=(self.width, self.height))

    def on_resize(self, w, h):
        del self.fbo
        print "resizing fbo"
        self.fbo = Fbo((w, h), push_viewport=False)

    def on_touch_down(self, touches, touchID, x, y):
        self.touch_positions[touchID] = (x,y)
        self.fbo.bind()
        glColor4f(*self.color)
        paintLine((x,y,x,y))
        glColor4f(1,1,1,1)
        self.fbo.release()

    def on_touch_move(self, touches, touchID, x, y):
        if self.touch_positions.has_key(touchID):
            ox,oy = self.touch_positions[touchID]
            self.fbo.bind()
            glColor4f(*self.color)
            paintLine((ox,oy,x,y))
            self.fbo.release()
            self.touch_positions[touchID] = (x,y)

    def on_touch_up(self, touches, touchID, x, y):
        if self.touch_positions.has_key(touchID):
            del self.touch_positions[touchID]


def pymt_plugin_activate(root, ctx):

    ctx.canvas = Canvas(pos=(40,40),size=(root.width,root.height))
    def resizeCanvas(w,h):
        ctx.canvas.dispatch_event('on_resize',w,h)
    root.push_handlers(on_resize=resizeCanvas)

    root.add_widget(ctx.canvas)
    ctx.slider = MTColorPicker(size=(130,290), targets=[ctx.canvas])
    root.add_widget(ctx.slider)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.canvas)
    root.remove_widget(ctx.slider)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
