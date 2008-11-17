#!/usr/bin/env python

from flowchart import *
from pymt import *

from random import randint

c = Container(layers=2)

def createElement(style='Box',text='Flowchart Element', color=(0.5,0.5,0.3,1.0)):
    w = None
    x,y = randint(50, 1000), randint(50, 1000)
    if style == 'Box':
        w = Box(text=text, pos=(x,y),color=color)
    elif style == 'Rhombus':
        w = Rhombus(text=text,pos=(x,y),color=color)
    c.add_widget(w,z=1)

createElement('Box', 'Lamp doesnt work', color=(0.6,0.3,0.3,1.0))
createElement('Rhombus', 'Lamp is plugged in?')
createElement('Rhombus', 'Bulb burned out?')
createElement('Box', 'plug in lamp!', color=(0.3,0.6,0.3,1.0))
createElement('Box', 'buy new bulb!', color=(0.3,0.6,0.3,1.0))
createElement('Box', 'buy new lamp!', color=(0.3,0.6,0.3,1.0))

win = UIWindow(c)
win.set_fullscreen()
runTouchApp()