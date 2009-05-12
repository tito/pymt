from __future__ import with_statement
from pyglet.gl import *
from pymt import *
import math

gx_alphablending = GlBlending(sfactor=GL_DST_COLOR, dfactor=GL_ONE_MINUS_SRC_ALPHA)

def drawRoundedRectangleAlpha(pos=(0,0), size=(100,50), radius=5, alpha=(1,1,1,1),
                         linewidth=1.5, precision=0.5, style=GL_TRIANGLE_FAN):
    '''Draw a rounded rectangle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (100, 50)
            Size of rectangle
        `radius` : int, default to 5
            Radius of corner
        `linewidth` : float, default to 1.5
            Line with of border
        `precision` : float, default to 0.5
            Precision of corner angle
        `style` : opengl begin, default to GL_POLYGON
            Style of the rounded rectangle (try GL_LINE_LOOP)
    '''
    x, y = pos
    w, h = size

    midalpha = 0
    for a in alpha:
        midalpha += a
    midalpha /= len(alpha)

    c0 = (1,1,1,midalpha)
    c1 = (1,1,1,alpha[0]) #topleft
    c2 = (1,1,1,alpha[2]) #bottomleft
    c3 = (1,1,1,alpha[1]) #topright
    c4 = (1,1,1,alpha[3]) #bottomright

    with DO(gx_alphablending, gx_begin(style)):

        glColor4f(*c0)
        glVertex2f(x + w/2, y + h/2)
        glColor4f(*c1)
        glVertex2f(x + radius, y)
        glColor4f(*c3)
        glVertex2f(x + w-radius, y)
        t = math.pi * 1.5
        while t < math.pi * 2:
            sx = x + w - radius + math.cos(t) * radius
            sy = y + radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x + w, y + radius)
        glColor4f(*c4)
        glVertex2f(x + w, y + h - radius)
        t = 0
        while t < math.pi * 0.5:
            sx = x + w - radius + math.cos(t) * radius
            sy = y + h -radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x + w -radius, y + h)
        glColor4f(*c2)
        glVertex2f(x + radius, y + h)
        t = math.pi * 0.5
        while t < math.pi:
            sx = x  + radius + math.cos(t) * radius
            sy = y + h - radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x, y + h - radius)
        glColor4f(*c1)
        glVertex2f(x, y + radius)
        t = math.pi
        while t < math.pi * 1.5:
            sx = x + radius + math.cos(t) * radius
            sy = y + radius + math.sin(t) * radius
            glVertex2f (sx, sy)
            t += precision
        glVertex2f(x + radius, y)


def drawRectangleAlpha(pos=(0,0), size=(1.0,1.0), alpha=(1,1,1,1), style=GL_QUADS):
    '''Draw a simple rectangle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (1.0, 1.0)
            Size of rectangle
        `style` : opengl begin, default to GL_QUADS
            Style of rectangle (try GL_LINE_LOOP)
    '''
    with DO(gx_alphablending, gx_begin(style)):
        glColor4f(1, 1, 1, alpha[0])
        glVertex2f(pos[0], pos[1])
        glColor4f(1, 1, 1, alpha[1])
        glVertex2f(pos[0] + size[0], pos[1])
        glColor4f(1, 1, 1, alpha[2])
        glVertex2f(pos[0] + size[0], pos[1] + size[1])
        glColor4f(1, 1, 1, alpha[3])
        glVertex2f(pos[0], pos[1] + size[1])

class MTBeautifulButton(MTButton):
    def __init__(self, **kwargs):
        kwargs.setdefault('do_border', False)
        kwargs.setdefault('do_backshadow', True)
        kwargs.setdefault('do_textshadow', True)
        super(MTBeautifulButton, self).__init__(**kwargs)
        self.do_border = kwargs.get('do_border')
        self.do_backshadow = kwargs.get('do_backshadow')
        self.do_textshadow = kwargs.get('do_textshadow')

    def draw(self):
        # Select color
        if self._state[0] == 'down':
            set_color(*self.color_down)
        else:
            set_color(*self.bgcolor)

        with gx_matrix:
            glTranslatef(self.x, self.y, 0)

            # Construct display list if possible
            if not self.button_dl.is_compiled():
                with self.button_dl:
                    if self.border_radius > 0:
                        drawRoundedRectangle(size=self.size, radius=self.border_radius)
                        if self.do_border:
                            drawRoundedRectangle(size=self.size, radius=self.border_radius, style=GL_LINE_LOOP)
                        if self.do_backshadow:
                            drawRoundedRectangleAlpha(size=self.size, radius=self.border_radius, alpha=(1,1,.5,.5))
                    else:
                        drawRectangle(size=self.size)
                        if self.do_border:
                            drawRectangle(size=self.size, style=GL_LINE_LOOP)
                        if self.do_backshadow:
                            drawRectangleAlpha(size=self.size, alpha=(1,1,.5,.5))
                    if len(self._label):
                        if self.do_textshadow:
                            with gx_blending:
                                self.label_obj.x, self.label_obj.y = self.width/2, self.height/2
                                self.label_obj.color = (22, 22, 22, 63)
                                self.label_obj.draw()
                        self.label_obj.x, self.label_obj.y = self.width/2 + 1 , self.height/2 + 1
                        self.label_obj.color = (255, 255, 255, 255)
                        self.label_obj.draw()
            self.button_dl.draw()

m = MTWindow()
k = {'size': (160, 40), 'border_radius': 8, 'font_size': 13}
c = get_color_from_hex
colors = ('222222', '2daebf', 'e33100', 'ff5c00')
x = 10
for color in colors:
    m.add_widget(MTBeautifulButton(label='Normal', pos=(x, 10), bgcolor=c(color), **k))
    m.add_widget(MTBeautifulButton(label='Draw Border', pos=(x, 60), bgcolor=c(color), do_border=True, **k))
    m.add_widget(MTBeautifulButton(label='No Back Shadow', pos=(x, 110), bgcolor=c(color), do_backshadow=False, **k))
    m.add_widget(MTBeautifulButton(label='No Text Shadow', pos=(x, 160), bgcolor=c(color), do_textshadow=False, **k))
    x += 180

runTouchApp()
