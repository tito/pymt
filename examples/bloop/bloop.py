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
        self.num_bloops = 1
        self.bloop_points = 1
        self.score = ScoreZone(self)
        self.add_widget(self.score)
        pyglet.clock.schedule_interval(self.generateBloop, 0.5)

    
    def generateBloop(self,dt):
        self.num_bloops = self.num_bloops + 1
        self.redpt = random.uniform(0, 1)
        self.greenpt = random.uniform(0, 1)
        self.bluept = random.uniform(0, 1)
        self.x = int(random.uniform(100, w.width-100))
        self.y = int(random.uniform(100, w.height-100))
        self.b = bloop(self,music_file=random.choice('ABCDEFG')+str(random.randint(1, 3))+".mp3",score_text=self.score,pos=(self.x,self.y),color=(self.redpt,self.greenpt,self.bluept,1))
        self.add_widget(self.b)

    def show_num_bloops(self):
        return str(self.num_bloops)
    
    def show_bloop_points(self):
        return str(self.bloop_points)
        
class bloop(MTButton):
    def __init__(self,parent=None,music_file=None,score_text=None,pos=(50,50), size=(100,100), scale = 1.0, color=(0.2,0.2,0.2,0.8),**kargs):
        MTButton.__init__(self, pos=pos, size=size, label="test")
        self.parent = parent
        self.music_file = music_file
        self.music = pyglet.resource.media(self.music_file, streaming=False)
        self.radius = int(self.width/2)
        self.alpha = 0.00
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        self.score_text = score_text
        
        self.highlightred = self.red * 1.25
        if(self.highlightred > 1):
            self.highlightred = 1

        self.highlightblue = self.blue * 1.25
        if(self.highlightblue > 1):
            self.highlightblue = 1

        self.highlightgreen = self.green * 1.25
        if(self.highlightgreen > 1):
            self.highlightgreen = 1
        
        anim = self.add_animation('fadein','alpha', 1.00, 1.0/60, 0.5)
        self.start_animations('fadein')
        self.showing = True
        self.highlight = False
        
        pyglet.clock.schedule_once(self.BloopHide, 2)
        
        anim = self.add_animation('fadeout','radius', self.width+10, 1.0/60, 1.0)
        anim = self.add_animation('fadeout','alpha', 0.00, 1.0/60, 0.5)
        
    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.parent.bloop_points = self.parent.bloop_points+1
            self.music.play()
            self.highlight = True
            self.red = self.highlightred
            self.green = self.highlightgreen
            self.blue = self.highlightblue            
            self.showing = False
            self.start_animations('fadeout')            
    
            
            
    def draw(self):
        glPushMatrix()
        enable_blending()
        if self.highlight:
            self.highlightalpha = self.alpha * 1.25
            if(self.highlightalpha > 1):
               self.highlightalpha = 1
            glColor4f(self.highlightred, self.highlightgreen, self.highlightblue, self.highlightalpha)
            drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=(self.radius*1.25))
        glColor4f(self.red,self.green,self.blue,self.alpha)
        drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=self.radius)
        glPopMatrix()
        
    def BloopHide(self,dt):
        self.start_animations('fadeout')
        self.showing = False
               
    def on_animation_complete(self, anim):
        if self.showing == False:
            self.parent.remove_widget(self)

class ScoreZone(MTWidget):
    def __init__(self, parent = None, pos=(0,0), size=(200,100), scale = 1.0, **kargs):
        MTWidget.__init__(self, pos=pos, size=size)
        self.label = "1/1"
        self.parent = parent
        pyglet.clock.schedule_interval(self.drawScore, 0.5)        
        
    def draw(self):
        glColor4f(1,0,0,1)
        drawLabel(self.label,(0,w.height-80),False)    

    def drawScore(self,dt):
        self.label = self.parent.show_bloop_points()+"/"+self.parent.show_num_bloops()
        self.draw()
        
def drawLabel(text, pos=(0,0),center=True):
    _standard_label = Label(text='standard Label', font_size=200,bold=True, color=(255,255,255,75))
    _standard_label.anchor_x = 'left'
    _standard_label.anchor_y = 'bottom'
    _standard_label.x = 0
    _standard_label.y = 0
    _standard_label.text = text
    glPushMatrix()
    glTranslated(pos[0], pos[1], 0.0)
    glScaled(0.3,0.3,1)
    _standard_label.draw()
    glPopMatrix()
    
def pymt_plugin_activate(root, ctx):
    ctx.PA = PlayArea()
    root.add_widget(ctx.PA)
    

def pymt_plugin_deactivate(root, ctx):
   root.remove_widget(ctx.PA)
    
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1))
    w.set_fullscreen()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)