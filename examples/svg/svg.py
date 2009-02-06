#!/usr/bin/env python

from pymt import *
import squirtle.squirtle as squirtle
class MTSquirtle(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSquirtle')
        super(MTSquirtle, self).__init__(**kwargs)
        self.position = kwargs.get('position')
        self.filename = kwargs.get('filename')
        
        squirtle.setup_gl()
        self.svg = squirtle.SVG(self.filename, anchor_x= 'center', anchor_y= 'center')
        self.height = self.svg.height
        self.width = self.svg.width
        self.init_transform(self.position,0)
    
    def draw(self):      
        glColor4d(*self.color)
        self.svg.draw(self.pos[0] + self.width/2, self.pos[1] + self.height/2)

if __name__ == '__main__':
    w = MTWindow()
    sun = MTSquirtle(filename = 'squirtle/svgs/sun.svg', position = (200,200))
    cloud = MTSquirtle(filename = 'squirtle/svgs/cloud.svg', position = (50,100))
    ship = MTSquirtle(filename = 'squirtle/svgs/ship.svg', position = (280,100))
    w.add_widget(sun)
    w.add_widget(cloud)
    w.add_widget(ship)
    runTouchApp()
