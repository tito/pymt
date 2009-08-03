import random
from pymt import *

w = MTWindow()

b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))
w.add_widget(b)

l = MTLabel(label='#', font_size=200, pos=(270, 40))
w.add_widget(l)

@b.event
def on_press(touch):
    l.label = str(random.randrange(0, 100))

runTouchApp() 
