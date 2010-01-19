from pymt import *
from random import randint

class Box(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('color', (1,0,0,1))
        self.color = kwargs.get('color')
        self.radius = 5
        super(Box, self).__init__(**kwargs)

    def draw(self):
        set_color(*self.color)
        drawRoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

if __name__ == '__main__':
    w = MTWindow()
    box = Box(pos=(300, 300), size=(100, 100), inner_animation=('pos', 'size', 'radius', 'color'))
    btn = MTButton(label='Click')
    @btn.event
    def on_press(*largs):
        w, h, x, y = map(lambda x: randint(50, 400), range(4))
        r, g, b, a = map(lambda x: float(randint(0, 255)) / 255., range(4))
        box.pos = x, y
        box.size = w, h
        box.color = (r, g, b, a)
        box.radius = randint(1, 50)
    w.add_widget(btn)
    w.add_widget(box)
    runTouchApp()
