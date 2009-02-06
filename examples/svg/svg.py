#!/usr/bin/env python

from pymt import *
import squirtle.squirtle as squirtle
class MTSquirtle(MTScatterWidget):
    def __init__(self, **kwargs):
        super(MTSquirtle, self).__init__(**kwargs)
        squirtle.setup_gl()
        self.sun = squirtle.SVG("squirtle/svgs/sun.svg", anchor_x='center', anchor_y= 'center')
    
    def draw(self):
        self.sun.draw(self.x + self.width/2, self.y + self.height/2)

if __name__ == '__main__':
    w = MTWindow()
    mts = MTSquirtle()
    w.add_widget(mts)
    runTouchApp()
