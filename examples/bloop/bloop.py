from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Blop The Game'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_EMAIL = 'sharath.patali@gmail.com'
PLUGIN_DESCRIPTION = 'This is a music game inspired by Bloom App.'

from pymt import *
from OpenGL.GL import *
import random

class PlayArea(MTWidget):
    ''' This is a widget which spawns new bloops and also maintains and displays the scorezone widget  '''
    def __init__(self, **kwargs):
        super(PlayArea, self).__init__(**kwargs)
        self.num_bloops = 1
        self.bloop_points = 1
        self.score = ScoreZone(parent=self)
        self.add_widget(self.score)
        getClock().schedule_interval(self.generateBloop, 0.5)


    def generateBloop(self,dt):
        self.num_bloops = self.num_bloops + 1
        self.redpt = random.uniform(0, 1)
        self.greenpt = random.uniform(0, 1)
        self.bluept = random.uniform(0, 1)
        self.x = int(random.uniform(100, w.width-100))
        self.y = int(random.uniform(100, w.height-100))
        self.b = bloop(music_file=
            os.path.join('music', '%s%d.wav' % (
                random.choice('ABCDEFG'), random.randint(1,3)
            )),
            score_text=self.score,
            pos=(self.x,self.y),
            color=(self.redpt,self.greenpt,self.bluept,1)
        )
        self.add_widget(self.b)

    def show_num_bloops(self):
        return str(self.num_bloops)

    def show_bloop_points(self):
        return str(self.bloop_points)

class bloop(MTButton):
    ''' This is a bloop widget, which tells itself to play music when it is touched and animate itself  '''
    def __init__(self,**kwargs):
        super(bloop, self).__init__(**kwargs)
        kwargs.setdefault('parent', None)
        kwargs.setdefault('music_file', None)
        kwargs.setdefault('score_text', None)
        self.color = kwargs.get('color')
        self.music_file = kwargs.get('music_file')
        self.music = SoundLoader.load(filename=self.music_file)
        self.radius = int(self.width/2)
        self.alpha = 0.00
        self.red = self.color[0]
        self.green = self.color[1]
        self.blue = self.color[2]
        self.score_text = kwargs.get('score_text')
        self.touched = False

        self.highlightred = self.red * 1.25
        if(self.highlightred > 1):
            self.highlightred = 1

        self.highlightblue = self.blue * 1.25
        if(self.highlightblue > 1):
            self.highlightblue = 1

        self.highlightgreen = self.green * 1.25
        if(self.highlightgreen > 1):
            self.highlightgreen = 1

        #anim = self.add_animation('fadein','alpha', 1.00, 1.0/60, 0.5)
        self.fadein = Animation(d=1.0, alpha=1.0)
        self.do(self.fadein)
        self.showing = True
        self.highlight = False

        getClock().schedule_once(self.BloopHide, 2)        
        
        self.fadeout = Animation(d=1.0, radius=self.width+10, alpha=0.0)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.touched == False:
                self.parent.bloop_points = self.parent.bloop_points+1
                if self.music:
                    self.music.play()
                self.highlight = True
                self.red = self.highlightred
                self.green = self.highlightgreen
                self.blue = self.highlightblue
            self.touched = True
            self.showing = False
            self.do(self.fadeout)

    def draw(self):
        with DO(gx_matrix, gx_blending):
            if self.highlight:
                self.highlightalpha = self.alpha * 1.25
                if(self.highlightalpha > 1):
                   self.highlightalpha = 1
                glColor4f(self.highlightred, self.highlightgreen, self.highlightblue, self.highlightalpha)
                drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=(self.radius*1.25))
            glColor4f(self.red,self.green,self.blue,self.alpha)
            drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=self.radius)

    def BloopHide(self,dt):
        self.do(self.fadeout)
        self.showing = False

    def on_animation_complete(self, anim):
        if self.showing == False:
            self.parent.remove_widget(self)

class ScoreZone(MTWidget):
    ''' This is a widget is responsible for drawing and updating the score on the screen'''
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (200,100))
        kwargs.setdefault('parent', None)
        super(ScoreZone, self).__init__(**kwargs)
        self.label = "1/1"
        getClock().schedule_interval(self.updateScore, .5)

    def draw(self):
        glColor4f(1,0,0,1)
        drawLabel(self.label, pos=(0,w.height-90), center=False, font_size=60,
                 bold=True, color=(1, 1, 1, .5))

    def updateScore(self,dt):
        self.label = self.parent.show_bloop_points()+"/"+self.parent.show_num_bloops()



def pymt_plugin_activate(root, ctx):
    ctx.PA = PlayArea()
    root.add_widget(ctx.PA)

def pymt_plugin_deactivate(root, ctx):
   root.remove_widget(ctx.PA)

if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1))
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
