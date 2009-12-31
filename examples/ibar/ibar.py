#! /usr/bin/python
# Original Ibar from kaswy 
# Website http://kaswy.free.fr

from random import random
from pymt import *

class PaintWidget(MTWidget):
    def __init__(self, **kwargs):
        super(PaintWidget, self).__init__(**kwargs)
        self.touch_positions = {}

    def on_draw(self):
        for p in self.touch_positions:
            for pos in self.touch_positions[p][len(self.touch_positions[p])-1:]:
                set_color(0.5,0,0.8)
                drawCircle((pos[0],pos[1]),25)
                for p in self.touch_positions:
                    for pos2 in self.touch_positions[p][len(self.touch_positions[p])-1:]:
                        err = 30
                        set_color(random()-0.1,0,random()+0.4)
                        drawLine((pos[0]+err*(random()-random()),pos[1]+err*(random()-random()),pos2[0]+err*(random()-random()),pos2[1]+err*(random()-random())), 15*random())

    def on_touch_down(self, touch):
        self.touch_positions[touch.id] = [(touch.x,touch.y)]

    def on_touch_move(self, touch):
        global ox
        global oy
        if (touch.x != ox) or (touch.y != oy):
            ox,oy = touch.x,touch.y
            self.touch_positions[touch.id].append((touch.x,touch.y))

    def on_touch_up(self, touch):
        del self.touch_positions[touch.id]

ox=oy=0
w = MTWindow()
w.add_widget(PaintWidget())

runTouchApp()
