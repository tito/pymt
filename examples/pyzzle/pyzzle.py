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
        self.player = Player()
        self.source = pyglet.media.load('../videoplayer/super-fly.avi')
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = 'loop'
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.player.play()
        #puzzle_texture = pyglet.image.load('simpson.jpg')
        puzzle_seq = pyglet.image.ImageGrid(self.player.get_texture(),4,4)

        print "COunt: ",len(puzzle_seq)    
        
        for i in range(self.max):
            self.pieces[i] = PyzzleObject(image=puzzle_seq[i])
            self.add_widget(self.pieces[i])
                        
    """def draw(self):
        glPushMatrix()
        glColor4f(0,0,0,1)
        drawLine((0,0,self.width,self.height), width=5.0)
        glPopMatrix()"""
            
class PyzzleObject(MTWidget):
    def __init__(self, **kwargs):
        super(PyzzleObject, self).__init__(**kwargs)
        self.image = kwargs.get('image')
        self.x = int(random.uniform(100, 1000))
        self.y = int(random.uniform(100, 800))
        self.width = self.image.width
        self.height = self.image.height
        self.state = ('normal', None)
        
    
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
            return True
        
def pymt_plugin_activate(root, ctx):
    ctx.pyzzle = PyzzleEngine(max=16)
    root.add_widget(ctx.pyzzle)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.pyzzle)        

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)    
