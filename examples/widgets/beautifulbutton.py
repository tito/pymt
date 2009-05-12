from __future__ import with_statement
from pyglet.gl import *
from pymt import *
import math


class MTBeautifulSlider(MTSlider):
    def __init__(self, **kwargs):
        kwargs.setdefault('do_border', False)
        kwargs.setdefault('do_backshadow', True)
        kwargs.setdefault('do_textshadow', True)
        super(MTBeautifulSlider, self).__init__(**kwargs)
        self.do_border = kwargs.get('do_border')
        self.do_backshadow = kwargs.get('do_backshadow')
        self.do_textshadow = kwargs.get('do_textshadow')

    def draw(self):
        x, y, w, h = self.x, self.y, self.width, self.height
        p2 = self.padding / 2
        # draw outer rectangle
        set_color(*self.bgcolor)
        drawRoundedRectangle(pos=(x,y), size=(w,h))
        drawRoundedRectangleAlpha(pos=(x,y), size=(w,h), alpha=(1,1,.5,.5))

        # draw inner rectangle
        set_color(*self.slidercolor)
        if self.orientation == 'vertical':
            length = int((self._value - self.min) * (self.height - self.padding) / (self.max - self.min))
            drawRoundedRectangle(pos=(x+p2,y+p2), size=(w - self.padding, length))
            if self.do_backshadow:
                drawRoundedRectangleAlpha(pos=(x+p2,y+p2), size=(w - self.padding, length), alpha=(1,1,.5,.5))
        else:
            length = int((self._value - self.min) * (self.width - self.padding) / (self.max - self.min))
            drawRoundedRectangle(pos=(x+p2,y+p2), size=(length, h - self.padding))
            if self.do_backshadow:
                drawRoundedRectangleAlpha(pos=(x+p2,y+p2), size=(length, h - self.padding), alpha=(1,1,.5,.5))



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

m.add_widget(MTSlider(pos=(10, 230), orientation='horizontal'))
m.add_widget(MTBeautifulSlider(pos=(10, 280), orientation='horizontal'))

runTouchApp()
