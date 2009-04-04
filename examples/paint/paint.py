from pymt import *
from pyglet.gl import *
from glob import glob

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Paint Sandbox'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_EMAIL = 'thomas.hansen@gmail.com'
PLUGIN_DESCRIPTION = 'This is a simple paint canvas.'

class PaintBrushLayout(MTBoxLayout):
    def draw(self):
        set_color(0, 0, 0, 0.7)
        drawRectangle(self.pos, self.size)


class MTPaintColorPicker(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 255)
        kwargs.setdefault('target', [])
        super(MTPaintColorPicker, self).__init__(**kwargs)
        self.targets = kwargs.get('targets')
        self.sliders = [ MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(1,0,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(0,1,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(0,0,1,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(1,1,1,.7)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(1,1,1,.7)) ]
        for slider in self.sliders:
            slider.value = 200
        self.update_color()
        self.touch_positions = {}
        self.brush_size = 10

    def draw(self):
        set_color(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(self.x, self.y), size=(self.width,self.height))

        set_color(*self.current_color)
        drawRectangle(pos=(self.x+10, self.y+220), size=(110,60))

        pos = self.x + 170, self.y + 250
        paintLine(pos+pos)


        for i in range(len(self.sliders)):
            self.sliders[i].x = 10 + self.x + i*40
            self.sliders[i].y = 10 + self.y
            self.sliders[i].draw()

    def update_color(self):
        r = self.sliders[0].value/255.0
        g = self.sliders[1].value/255.0
        b = self.sliders[2].value/255.0
        a = self.sliders[3].value/255.0
        for w in self.targets:
            w.color = (r,g,b,a)
        self.current_color = (r,g,b,a)
        self.brush_size = (self.sliders[4].value/4) + 1
        set_brush_size(self.brush_size)

    def on_touch_down(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_down(touches, touchID, x, y):
                self.update_color()
                return True

        if self.collide_point(x,y):
            self.touch_positions[touchID] = (x, y, touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_move(touches, touchID, x, y):
                self.update_color()
                return True
        if touchID in self.touch_positions:
            self.x += x - self.touch_positions[touchID][0]
            self.y += y - self.touch_positions[touchID][1]
            self.touch_positions[touchID] = (x,y,touchID)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_up(touches, touchID, x, y):
                self.update_color()
                return True
        if touchID in self.touch_positions:
            del self.touch_positions[touchID]



class Canvas(MTWidget):
    def __init__(self, min=0, max=100, pos=(0,0), size=(640,480)):
        MTWidget.__init__(self, pos=pos, size=size)
        self.touch_positions = {}
        self.fbo = Fbo(size=(self.width, self.height), with_depthbuffer=False)
        self.bgcolor = (0,0,0,1)
        self.color = (0,1,0,1.0)
        set_brush('../paint/brushes/brush_particle.png')
        self.clear()

    def clear(self):
        self.fbo.bind()
        glClearColor(*self.bgcolor)
        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(1,0,1,1)
        self.fbo.release()

    def draw(self):
        set_color(1,1,1,1)
        drawTexturedRectangle(self.fbo.texture, size=(self.width, self.height))

    def on_resize(self, w, h):
        if self.fbo.size == (w, h):
            return
        del self.fbo
        self.fbo = Fbo(size=(w, h), push_viewport=False)

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

def update_brush(brush, touchID, x, y):
    set_brush(brush)

def clear_canvas(canvas, touchID, x, y):
    canvas.clear()

def pymt_plugin_activate(root, ctx):

    ctx.canvas = Canvas(pos=(40,40),size=(root.width,root.height))
    def resizeCanvas(w,h):
        ctx.canvas.size = (w, h)
        ctx.btnclear.pos = (0, root.height - 50)
    root.push_handlers(on_resize=resizeCanvas)

    root.add_widget(ctx.canvas)
    ctx.slider = MTPaintColorPicker(size=(220,290), targets=[ctx.canvas])
    root.add_widget(ctx.slider)

    ctx.btnclear = MTButton(label='Clear', size=(50,50), pos=(0, root.height-50))
    ctx.btnclear.push_handlers(on_press=curry(clear_canvas, ctx.canvas))
    root.add_widget(ctx.btnclear)

    ctx.brushes = PaintBrushLayout(pos=(300, 0))
    for brush in glob('../paint/brushes/*.png'):
        button = MTImageButton(filename=brush)
        button.push_handlers(on_press=curry(update_brush, brush))
        ctx.brushes.add_widget(button)
    root.add_widget(ctx.brushes)



def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.canvas)
    root.remove_widget(ctx.slider)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
