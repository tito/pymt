from pymt import *
from random import random

css_add_sheet('dragablelabel { draw-background: 1; }')

class DragableLabel(MTDragable):
    def __init__(self, **kwargs):
        super(DragableLabel, self).__init__()
        self.label = MTLabel(**kwargs)
        self.add_widget(self.label)

    def on_update(self):
        self.label.pos = interpolate(self.label.pos, self.pos)
        self.size = interpolate(self.size, self.label.size)
        super(DragableLabel, self).on_update()

window = getWindow()
w, h = window.size

for text in ('My dog is lazy', 'My cat is sleeping', 'Hello world'):
    # Make a label dragable
    label = DragableLabel(label=text, padding=40)

    # randomize a position
    label.center = w * random(), h * random()

    # add to window
    window.add_widget(label)

runTouchApp()

