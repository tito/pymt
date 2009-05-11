from pymt import *
from random import randint

class Box(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('color', (1,0,0))
        super(Box, self).__init__(**kwargs)
        self.color = kwargs.get('color')

    def draw(self):
        set_color(*self.color)
        drawRectangle(pos=self.pos, size=self.size)

if __name__ == '__main__':
    w = MTWindow()
    box = Box(pos=(300, 300), size=(100, 100))
    box.enable_inner_animation(props=('x', 'y', 'width', 'height', 'color'))
    btn = MTButton(label='Click')
    @btn.event
    def on_press(*largs):
        w, h, x, y = map(lambda x: randint(50, 400), range(4))
        r, g, b = map(lambda x: float(randint(0, 255)) / 255., range(3))
        box.x = x
        box.y = y
        box.width = w
        box.height = h
        box.color = (r, g, b)
    w.add_widget(btn)
    w.add_widget(box)
    runTouchApp()
