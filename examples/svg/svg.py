from pymt import *
import squirtle.squirtle as squirtle

class MTSquirtle(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSquirtle')
        super(MTSquirtle, self).__init__(**kwargs)
        self.filename = kwargs.get('filename')
        
        squirtle.setup_gl()
        self.svg = squirtle.SVG(self.filename)
        
        self.height = self.svg.height
        self.width = self.svg.width
    
    def draw(self):      
        self.svg.draw(0, 0)

if __name__ == '__main__':
    w = MTWindow()
    sun = MTSquirtle(filename = 'squirtle/svgs/sun.svg', pos = (200,200))
    cloud = MTSquirtle(filename = 'squirtle/svgs/cloud.svg', pos = (50,100))
    ship = MTSquirtle(filename = 'squirtle/svgs/ship.svg', pos = (280,100))
    w.add_widget(sun)
    w.add_widget(cloud)
    w.add_widget(ship)
    runTouchApp()
