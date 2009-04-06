# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Pyzzle a multitouch video puzzle'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_EMAIL = 'sharath.patali@gmail.com'


from pymt import *
from pyglet import *
from pyglet.media import *
from pyglet.gl import *
import random

class PyzzleEngine(MTWidget):
    def __init__(self, max=16, **kargs):
        MTWidget.__init__(self, **kargs)
        self.max        = max
        self.pieces  = {}
        self.gridHolders = {}
        self.player = Player()
        self.player.volume = 0.0
        self.source = pyglet.media.load('../videoplayer/super-fly.avi')
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = 'loop'
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.player.play()
        #puzzle_texture = pyglet.image.load('simpson.jpg')
        puzzle_seq = pyglet.image.ImageGrid(self.player.get_texture(),4,4)
        
        self.griddy = MTGridLayout(rows=4,cols=4,spacing=1)
        for i in range(self.max):
            self.gridHolders[i] = gridHolder(size=(puzzle_seq[i].width,puzzle_seq[i].height))
            self.griddy.add_widget(self.gridHolders[i])
              
        self.griddy.x = int((self.griddy.width))
        self.griddy.y = int((self.griddy.height))
        self.add_widget(self.griddy) 
        self.griddy.pos = (int(w.width/2-self.griddy._get_content_width()/2),int(w.height/2-self.griddy._get_content_height()/2))
        self.griddy._get_content_width()
        
        for i in range(self.max):
            self.pieces[i] = PyzzleObject(image=puzzle_seq[i],grid=self.griddy)
            self.add_widget(self.pieces[i])
        
class gridHolder(MTRectangularWidget):
    def __init__(self, **kwargs):
        super(gridHolder, self).__init__(**kwargs)

            
class PyzzleObject(MTWidget):
    def __init__(self, **kwargs):
        super(PyzzleObject, self).__init__(**kwargs)
        self.image = kwargs.get('image')
        self.x = int(random.uniform(100, 1000))
        self.y = int(random.uniform(100, 800))
        self.width = self.image.width
        self.height = self.image.height
        self.state = ('normal', None)
        self.grid = kwargs.get('grid')

    def draw(self):
        glPushMatrix()
        glColor4f(1,1,1,1)
        self.image.blit(self.x,self.y,0)
        glPopMatrix()
        
    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.bring_to_front()
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self.state[0] == 'dragging' and self.state[1] == touchID:
            self.x, self.y = (self.x + (x - self.state[2]) , self.y + y - self.state[3])
            self.state = ('dragging', touchID, x, y)
            return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.state[1] == touchID:
            self.state = ('normal', None)
            for i in range(4):
                for j in range(4):
                    if(((self.center[0]>=int(self.grid.x+self.image.width*i)) & \
                    (self.center[0]<=int(self.grid.x+self.image.width+self.image.width*i))) &\
                    ((self.center[1]>=int(self.grid.y+self.image.height*j)) & \
                    (self.center[1]<=int(self.grid.y+self.image.height+self.image.height*j)))
                    ):
                        #print "inside ",int(self.grid.x+self.image.width*i),int(self.grid.y+self.image.height*j)
                        self.center = int(self.grid.x+self.image.width*i+self.image.width/2),int(self.grid.y+self.image.height*j+self.image.height/2)
            return True

if __name__ == '__main__':
    w = MTWindow()
    pyzzle = PyzzleEngine(max=16)
    w.add_widget(pyzzle)
    runTouchApp()
 
