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
    box.enable_inner_animation(props=('x', 'y', 'width', 'height'), func=AnimationAlpha.sin)
    btn = MTButton(label='Click')
    @btn.event
    def on_press(*largs):
        w, h, x, y = map(lambda x: randint(50, 400), range(4))
        box.x = x
        box.y = y
        box.width = w
        box.height = h
    w.add_widget(btn)
    w.add_widget(box)
    runTouchApp()
