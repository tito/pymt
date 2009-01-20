from pymt import *
import os
import random
from pyglet.media import *

class MTVideoPlayPause(MTImageButton):
    def __init__(self,image_file='play.png', pos=(0, 0),size=(100, 100),player = None,**kargs):
        MTImageButton.__init__(self,image_file,pos, size,**kargs)
        self.vid = player
        self.playState = "Pause"
        self.imageState = 'play.png'
    
    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            if self.playState == "Pause":
                self.vid.play()
                self.playState = "Play"
                self.imageState = 'pause.png'
            elif self.playState == "Play":
                self.vid.pause()
                self.playState = "Pause"
                self.imageState = 'play.png'
            print "Button touched"
	
    def draw(self):
        img                 = pyglet.image.load(self.imageState)
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.width          = self.image.width
        self.height         = self.image.height
        self.image.draw()
        
class MTVideoTimeline(MTSlider):
    def __init__(self, min=0, max=30, pos=(5,5), size=(150,30), alignment='horizontal', padding=8, color=(0.78, 0.78, 0.78, 1.0), player=None,duration=100):
        MTSlider.__init__(self, min, max, pos, size, alignment, padding, color)
        self.value = 0
        self.vid = player
        self.max = duration
        self.x, self.y = pos[0], pos[1]
        self.width , self.height = self.vid.get_texture().width, 30
        
    def draw(self):
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x,y,w,h = self.x,self.y,self.width+self.padding, self.height
        p2 =self.padding/2
        # draw outer rectangle
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        glColor4f(*self.color)
        length = int(self.width*(float(self.value)/self.max))
        drawRectangle(pos=(self.x+p2,self.y+p2+11), size=(length,(h-self.padding)/2))
        glColor4f(0.713, 0.713, 0.713, 1.0)
        drawRectangle(pos=(self.x+p2,self.y+p2), size=(length,(h-self.padding)/2))
        
    def on_draw(self):
        self.value = self.vid.time
        self.draw()
        
    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x,y):
            self.touchstarts.append(touchID)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        pass

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touchstarts:
            self.touchstarts.remove(touchID)
            
class MTVideo(MTScatterWidget):
    """MTVideo is a Zoomable,Rotatable,Movable Video widget"""
    def __init__(self, pos=(300,200), size=(0,0), rotation=0):
        MTScatterWidget.__init__(self,pos=pos,size=size)
        self.rotation = rotation
        self.player = Player()
        self.source = pyglet.media.load('video.avi')
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = "pause" 
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.texW = self.player.get_texture().width
        self.texH = self.player.get_texture().height

    def draw(self):
        #print "Time:",self.player.time
        glPushMatrix()
        enable_blending()
        glColor4f(0,0,0,0.5)
        drawRectangle((-10,-10),(self.texW+20,self.texH+20))
        glColor3d(1,1,1)
        self.player.get_texture().blit(0,0)
        glPopMatrix()   

if __name__ == '__main__':
    w = MTWindow()
    #w.set_fullscreen()
    video = MTVideo()
    w.add_widget(video)
    butt = MTVideoPlayPause(image_file='play.png',pos=(100,100), player=video.player)
    w.add_widget(butt)
    w.add_widget(MTVideoTimeline(player=video.player,duration=video.sourceDuration))
    runTouchApp()

