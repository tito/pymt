from pymt import *
from random import random

window = getWindow()

# create 100 dragable object with random position and color
w, h = window.size
for i in xrange(100):
    x = random() * w
    y = random() * h
    window.add_widget(MTDragable(pos=(x, y),
        style={'bg-color': get_random_color(), 'draw-background': 1}))

runTouchApp()
