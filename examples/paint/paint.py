import collections
from pymt import *
from OpenGL.GL import *
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
        self.sliders = [ MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), style = {'slider-color': (1,0,0,1)}),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), style = {'slider-color': (0,1,0,1)}),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), style = {'slider-color': (0,0,1,1)}),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), style = {'slider-color': (1,1,1,.7)}),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), style = {'slider-color': (1,1,1,.7)}) ]
        for slider in self.sliders:
            slider.value = 200
        self.update_color()
        self.touch_positions = {}
        self.brush_size = (self.sliders[4].value/4) + 1
        set_brush_size(self.brush_size)

    def draw(self):
        set_color(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(self.x, self.y), size=(self.width,self.height))

        set_color(*self.current_color)
        drawRectangle(pos=(self.x+10, self.y+220), size=(110,60))

        pos = self.x + 170, self.y + 250
        set_brush_size(self.brush_size)
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

    def on_touch_down(self, touch):
        for s in self.sliders:
            if s.on_touch_down(touch):
                self.update_color()
                return True

        if self.collide_point(touch.x, touch.y):
            self.touch_positions[touch.id] = (touch.x, touch.y, touch.id)
            return True

    def on_touch_move(self, touch):
        for s in self.sliders:
            if s.on_touch_move(touch):
                self.update_color()
                return True
        if touch.id in self.touch_positions:
            self.x += touch.x - self.touch_positions[touch.id][0]
            self.y += touch.y - self.touch_positions[touch.id][1]
            self.touch_positions[touch.id] = (touch.x, touch.y, touch.id)
            return True

    def on_touch_up(self, touch):
        for s in self.sliders:
            if s.on_touch_up(touch):
                self.update_color()
                return True
        if touch.id in self.touch_positions:
            del self.touch_positions[touch.id]



class Canvas(MTWidget):
    def __init__(self, min=0, max=100, pos=(0,0), size=(640,480)):
        MTWidget.__init__(self, pos=pos, size=size)
        self.touch_positions = {}
        self.fbo = Fbo(size=(self.width, self.height), with_depthbuffer=False)
        self.bgcolor = (0,0,0,1)
        self.color = (0,1,0,1.0)
        set_brush('../paint/brushes/brush_particle.png')
        self.paint_queue = collections.deque()
        self.do_paint_queue = False
        self.clear()

    def clear(self):
        self.fbo.bind()
        glClearColor(*self.bgcolor)
        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(1,0,1,1)
        self.fbo.release()

    def draw(self):
        # draw the whole queue
        if self.do_paint_queue:
            self.fbo.bind()
            while True:
                try:
                    item = self.paint_queue.pop()
                except IndexError:
                    break
                color, positions = item
                set_color(*color)
                paintLine(positions)
            self.fbo.release()
            self.do_paint_queue = False
        set_color(1,1,1,1)
        drawTexturedRectangle(self.fbo.texture, size=(self.width, self.height))

    def on_resize(self, w, h):
        if self.fbo.size == (w, h):
            return
        del self.fbo
        self.fbo = Fbo(size=(w, h), push_viewport=False)

    def on_touch_down(self, touch):
        self.paint_queue.appendleft((self.color, (touch.x,touch.y,touch.x,touch.y)))
        self.do_paint_queue = True
        self.touch_positions[touch.id] = (touch.x, touch.y)

    def on_touch_move(self, touch):
        if self.touch_positions.has_key(touch.id):
            ox,oy = self.touch_positions[touch.id]
            self.paint_queue.appendleft((self.color, (ox,oy,touch.x,touch.y)))
            self.do_paint_queue = True
            self.touch_positions[touch.id] = (touch.x, touch.y)

    def on_touch_up(self, touch):
        if self.touch_positions.has_key(touch.id):
            del self.touch_positions[touch.id]

def update_brush(brush, size, *largs):
    set_brush(brush, size=size)

def clear_canvas(canvas, *largs):
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
        button.push_handlers(on_press=curry(update_brush, brush,
                                            ctx.slider.brush_size))
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
