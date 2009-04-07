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


#A snappable grid layout which produces a container to hold the snappable objects            
class MTSnappableGrid(MTGridLayout):
    def __init__(self, **kwargs):
        super(MTSnappableGrid, self).__init__(**kwargs)
        self.block_size = kwargs.get('block_size')
        self.gridHolders = {}
        for i in range(self.rows*self.cols):
            self.gridHolders[i] = MTRectangularWidget(size=(self.block_size[0],self.block_size[1]),bgcolor=(0.5,0.5,0.5))
            self.add_widget(self.gridHolders[i])    

#A snappable object which snaps into position in the grid            
class MTSnappableWidget(MTWidget):
    def __init__(self, **kwargs):
        super(MTSnappableWidget, self).__init__(**kwargs)       
        self.state = ('normal', None)
        self.grid = kwargs.get('grid')
        
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
            for i in range(self.grid.rows):
                for j in range(self.grid.cols):
                    if(((self.center[0]>=int(self.grid.x+self.width*j)) & \
                    (self.center[0]<=int(self.grid.x+self.width+self.width*j))) &\
                    ((self.center[1]>=int(self.grid.y+self.height*i)) & \
                    (self.center[1]<=int(self.grid.y+self.height+self.height*i)))
                    ):
                        self.center = int(self.grid.x+self.width*j+self.width/2),int(self.grid.y+self.height*i+self.height/2)
            return True       
            
class PyzzleEngine(MTWidget):
    def __init__(self, max=16, **kwargs):
        MTWidget.__init__(self, **kwargs)
        self.pieces  = {}
        self.player = Player()
        self.player.volume = 0.0
        self.source = pyglet.media.load('../videoplayer/super-fly.avi')
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = 'loop'
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.player.play()
        puzzle_seq = pyglet.image.ImageGrid(self.player.get_texture(),4,3)
        
        self.griddy = MTSnappableGrid(rows=4,cols=3,spacing=0,block_size=(puzzle_seq[0].width,puzzle_seq[1].height))
        self.add_widget(self.griddy) 
        
        self.griddy.pos = (int(w.width/2-self.griddy._get_content_width()/2),int(w.height/2-self.griddy._get_content_height()/2))
        
        for i in range(self.griddy.rows*self.griddy.cols):
            self.pieces[i] = PyzzleObject(image=puzzle_seq[i],grid=self.griddy)
            self.add_widget(self.pieces[i])

class PyzzleObject(MTSnappableWidget):
    def __init__(self, **kwargs):
        super(PyzzleObject, self).__init__(**kwargs)
        self.image = kwargs.get('image')
        self.x = int(random.uniform(100, 1000))
        self.y = int(random.uniform(100, 800))
        self.width = self.image.width
        self.height = self.image.height

    def draw(self):
        glPushMatrix()
        glColor4f(1,1,1,1)
        self.image.blit(self.x,self.y,0)
        glPopMatrix()
       

if __name__ == '__main__':
    w = MTWindow()
    pyzzle = PyzzleEngine(max=12)
    w.add_widget(pyzzle)
    runTouchApp()
 
