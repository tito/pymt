'''
Color picker: a simple color picker with 3 slider
'''

__all__ = ['MTColorPicker']

from pyglet.gl import *
from ...graphx import set_color, drawRectangle
from ..factory import MTWidgetFactory
from widget import MTWidget
from slider import MTSlider

class MTColorPicker(MTWidget):
    '''MTColorPicker is a implementation of a color picker using MTWidget

    :Parameters:
        `min` : int, default is 0
            Minimum value of slider
        `max` : int, default is 255
            Maximum value of slider
        `targets` : list, default is []
            List of widget to be affected by change
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('min', 0)
        kwargs.setdefault('max', 255)
        kwargs.setdefault('target', [])
        super(MTColorPicker, self).__init__(**kwargs)
        self.targets = kwargs.get('targets')
        self.sliders = [ MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(1,0,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(0,1,0,1)),
                        MTSlider(min=kwargs.get('min'), max=kwargs.get('max'), size=(30,200), slidercolor=(0,0,1,1)) ]
        for slider in self.sliders:
            slider.value = 77
        self.update_color()
        self.touch_positions = {}

    def draw(self):
        set_color(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(self.x, self.y), size=(self.width,self.height))

        set_color(*self.current_color)
        drawRectangle(pos=(self.x+10, self.y+220), size=(110,60))

        for i in range(len(self.sliders)):
            self.sliders[i].x = 10 + self.x + i*40
            self.sliders[i].y = 10 + self.y
            self.sliders[i].draw()

    def update_color(self):
        r = self.sliders[0].value/255.0
        g = self.sliders[1].value/255.0
        b = self.sliders[2].value/255.0
        for w in self.targets:
            w.color = (r,g,b,1)
        self.current_color = (r,g,b,1.0)

    def on_touch_down(self, touches, touchID, x, y):
        for s in self.sliders:
            if s.on_touch_down(touches, touchID, x, y):
                self.update_color()
                return True

        if self.collide_point(x,y):
            self.touch_positions[touchID] = (x,y,touchID)
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

MTWidgetFactory.register('MTColorPicker', MTColorPicker)
