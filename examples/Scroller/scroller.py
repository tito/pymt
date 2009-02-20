'''
WORK UNDER PROGRESS
Please do not change anything :)

Thank You.
 Sharath Patali

'''

from pymt import *

class MTicon(MTButton):
    def __init__(self, **kwargs):        
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTicon')

        super(MTicon, self).__init__(**kwargs)
        self.fname = kwargs.get('filename')
        img                 = pyglet.image.load(kwargs.get('filename'))
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.width,self.height  = (self.image.width, self.image.height)

    def draw(self):
        if (self.parent.parent.to_parent(self.x,self.y)[0] >= (w.width/2-256)) & (self.parent.parent.to_parent(self.x,self.y)[0] <= (w.width/2)):
            self.image.scale    = 1.0
            self.width,self.height  = (self.image.width, self.image.height)
        else:
            self.image.scale    = 0.5
            self.width,self.height  = (self.image.width, self.image.height)
       
        self.image.x        = self.x
        self.image.y        = self.y
       
        self.size           = (self.image.width, self.image.height)
        self.image.draw()
        self.parent.layout()
        
    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            print "Touched"
            print "file: ",self.fname , self.parent.parent.to_parent(self.x,self.y)[0]            
            return
            
    def on_touch_move(self, touches, touchID, x, y):
        return
        
    def on_touch_up(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            return        
    


if __name__ == '__main__':
    w = MTWindow(color=(0.2,0.2,0.2,1.0))
    plane = MTScatterWidget(color=(0.2,0.2,0.2,1.0),do_rotation=False, do_scale=False, do_translation=['x'], size=(1440,300),pos=(0,w.height/2-150))
    w.add_widget(plane)
    layme = HVLayout(padding=10, spacing=10, color=(0.2,0.2,0.2,1.0))
    plane.add_widget(layme)
    layme.add_widget(MTicon(filename = "Browser.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Calculator.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Calendar.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Chat.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Settings.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Graph.png",scale=0.5))
    layme.add_widget(MTicon(filename = "iPod.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Maps.png",scale=0.5))
    layme.add_widget(MTicon(filename = "Notes.png",scale=0.5))    
    runTouchApp()

