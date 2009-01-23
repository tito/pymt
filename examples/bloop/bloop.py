IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Blop The Game'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_EMAIL = 'sharath.patali@gmail.com'
PLUGIN_DESCRIPTION = 'This is a music game inspired by Bloom App.'

from pymt import *
from pyglet.media import *
from pyglet.gl import *
import random

pyglet.resource.path=['music']
pyglet.resource.reindex()

class PlayArea(MTWidget):
    def __init__(self, pos=(0,0), size=(500,400), scale = 1.0, **kargs):
        MTWidget.__init__(self, pos=pos, size=size)
        
        pyglet.clock.schedule_interval(self.generateBloop, 0.5)


    def generateBloop(self,dt): 
        self.redpt = random.uniform(0, 1)
        self.greenpt = random.uniform(0, 1)
        self.bluept = random.uniform(0, 1)
        self.x = int(random.uniform(100, w.width-100))
        self.y = int(random.uniform(100, w.height-100))
        self.b = bloop(music_file=random.choice('ABCDEFG')+str(random.randint(1, 3))+".mp3",pos=(self.x,self.y),color=(self.redpt,self.greenpt,self.bluept,1))
        self.add_widget(self.b)

        
class bloop(MTButton):
    def __init__(self, music_file=None,pos=(50,50), size=(100,100), scale = 1.0, color=(0.2,0.2,0.2,0.8),**kargs):
        MTButton.__init__(self, pos=pos, size=size, label="test")
        self.music_file = music_file
        self.music = pyglet.resource.media(self.music_file, streaming=False)
        self.radius = int(self.width/2)
        self.alpha = 0.00
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        anim = self.add_animation('fadein','alpha', 1.00, 1.0/60, 0.5)
        self.start_animations('fadein')
        self.showing = True
        
        pyglet.clock.schedule_once(self.BloopHide, 2)
        
        anim = self.add_animation('fadeout','radius', self.width+10, 1.0/60, 1.0)
        anim = self.add_animation('fadeout','alpha', 0.00, 1.0/60, 0.5)
        
    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.music.play()
            self.start_animations('fadeout')
            self.showing = False
            
    def draw(self):
        glPushMatrix()
        enable_blending()
        glColor4f(self.red,self.green,self.blue,self.alpha)
        drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=self.radius)
        glPopMatrix()
        
    def BloopHide(self,dt):
        self.start_animations('fadeout')
        self.showing = False
               
    def on_animation_complete(self, anim):
        if self.showing == False:
            self.parent.remove_widget(self)
            
 
       
def pymt_plugin_activate(root, ctx):
    ctx.PA = PlayArea()
    root.add_widget(ctx.PA)
    

def pymt_plugin_deactivate(root, ctx):
   root.remove_widget(ctx.PA)
    
if __name__ == '__main__':
    w = MTWindow()
    w.set_fullscreen()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)