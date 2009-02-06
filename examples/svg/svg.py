#!/usr/bin/env python

from pymt import *
import squirtle.squirtle as squirtle
class MTSquirtle(MTScatterWidget):
    def __init__(self, **kwargs):
        super(MTSquirtle, self).__init__(**kwargs)
        squirtle.setup_gl()
        self.sun = squirtle.SVG("squirtle/svgs/sun.svg", anchor_x= 'center', anchor_y= 'center')
        self.height = self.sun.height
        self.width = self.sun.width
        self.init_transform((250,200),0)
    
    def draw(self):      
        glColor4d(*self.color)
        self.sun.draw(self.pos[0] + self.width/2, self.pos[1] + self.height/2)

if __name__ == '__main__':
    w = MTWindow()
    mts = MTSquirtle()
    w.add_widget(mts)
    runTouchApp()
