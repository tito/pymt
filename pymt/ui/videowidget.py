import pymt
from pymt import *
from pyglet.gl import *
from pymt.ui import *
from pyglet.media import *
from time import sleep

iconPath = os.path.dirname(pymt.__file__)+"/data/icons/"

class MTVideoPlayPause(MTImageButton):
    """MTVideoPlayPause is a dynamic play/pause button of the video widget"""
    def __init__(self,image_file=iconPath+'videoWidgetPlay.png', pos=(0, 0),size=(100, 100),player = None, opacity=100,**kargs):
        MTImageButton.__init__(self,image_file,pos, size,opacity,**kargs)
        self.vid = player
        self.playState = "Pause"

        self.images = {} #crate a python dictionary..like a hash map
        self.images['Play']  = pyglet.sprite.Sprite( image.load(iconPath+'videoWidgetPlay.png')  )
        self.images['Pause'] = pyglet.sprite.Sprite( image.load(iconPath+'videoWidgetPause.png') )

        self.scale    = 0.75

    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            if self.playState == "Pause":
                self.vid.play()
                self.playState = "Play"
            elif self.playState == "Play":
                self.vid.pause()
                self.playState = "Pause"

            #set the correct image
            self.image = self.images[self.playState]  #playState is one of the two strings that are used as keys/lookups in the dictionary


class MTVideoMute(MTImageButton):
    """MTVideoMute is a mute button class of the video widget"""
    def __init__(self,image_file=iconPath+'videoWidgetMute.png', pos=(0, 0),size=(100, 100),player = None,opacity=100,**kargs):
        MTImageButton.__init__(self,image_file,pos, size,**kargs)
        self.vid = player
        self.playState = "NotMute"
        self.scale    = 0.75

    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            if self.playState == "NotMute":
                self.vid.volume = 0.0
                self.playState = "Mute"
            elif self.playState == "Mute":
                self.vid.volume = 1.0
                self.playState = "NotMute"

class MTVideoTimeline(MTSlider):
    """MTVideoTimeline is a part of the video widget which tracks the video playback"""
    def __init__(self, min=0, max=30, pos=(5,5), size=(150,30), alignment='horizontal', padding=8, color=(0.78, 0.78, 0.78, 1.0), player=None,duration=100):
        MTSlider.__init__(self, min, max, pos, size, alignment, padding, color)
        self.value = 0
        self.vid = player
        self.max = duration
        self.x, self.y = pos[0], pos[1]
        self.width , self.height = self.vid.get_texture().width-83,30
        self.length = 0

    def draw(self):
        self.value = self.vid.time % self.max

        if self.vid.time == self.max:
            self.value = 0
            self.vid.seek(0)
            self.length = 0
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x,y,w,h = self.x,self.y,self.width+self.padding, self.height
        p2 =self.padding/2
        # draw outer rectangle
        glColor4f(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        glColor4f(*self.color)
        self.length = int(self.width*(float(self.value)/self.max))
        drawRectangle(pos=(self.x+p2,self.y+p2+11), size=(self.length,(h-self.padding)/2))
        glColor4f(0.713, 0.713, 0.713, 1.0)
        drawRectangle(pos=(self.x+p2,self.y+p2), size=(self.length,(h-self.padding)/2))


    def on_draw(self):
        if not self.visible:
            return
        self.value = self.vid.time % self.max
        if self.vid.time == self.max:
            self.value = 0
            self.vid.seek(0)
            self.length = 0
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
    """MTVideo is a Zoomable,Rotatable,Movable Video widget
       Usage: 
          video = MTVideo('source_file',(x_pos,y_pos),(scale,scale),rotation_in_degrees)
          supported file types are similar file support of pyglet player class
    """
    def __init__(self, video="none", pos=(300,200), size=(0,0), rotation=0):
        MTScatterWidget.__init__(self,pos=pos,size=size)
        self.rotation = rotation
        self.player = Player()
        self.source = pyglet.media.load(video)
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = "pause"
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.texW = self.player.get_texture().width
        self.texH = self.player.get_texture().height

        #init as subwidgest.  adding them using add_widgtes, makes it so that they get the events before MTVideo instance
        #the pos, size is relative to this parent widget...if it scales etc so will these
        self.button = MTVideoPlayPause(image_file=iconPath+'videoWidgetPlay.png',pos=(0,0), player=self.player, opacity=100)
        self.add_widget(self.button)
        self.button.hide()

        self.mutebutton = MTVideoMute(image_file=iconPath+'videoWidgetMute.png',pos=(36,0), player=self.player, opacity=100)
        self.add_widget(self.mutebutton)
        self.mutebutton.hide()

        self.timeline = MTVideoTimeline(pos=(72,3),player=self.player,duration=self.sourceDuration)
        self.add_widget(self.timeline)
        self.timeline.hide()

    def draw(self):
        glPushMatrix()
        enable_blending()
        glColor4f(1,1,1,0.5)
        drawRectangle((-10,-10),(self.texW+20,self.texH+20))
        glColor3d(1,1,1)
        self.player.get_texture().blit(0,0)
        glPopMatrix()

    def on_touch_down(self, touches, touchID, x, y):
        #if the touch isnt on teh widget we do nothing
        if not self.collide_point(x,y):
            return False
        elif self.collide_point(x,y):
            self.button.show()
            self.mutebutton.show()
            self.timeline.show()
            pyglet.clock.schedule_once(self.hideControls, 2)

        #let the child widgets handle the event if they want
        lx,ly = self.to_local(x,y)
        if MTWidget.on_touch_down(self, touches, touchID, lx, ly):
            return True

        #if teh children didnt handle it, we bring to front & keep track of touches for rotate/scale/zoom action
        self.bring_to_front()
        if not self.haveTouch(touchID) and len(self.touches) <=2:
            self.touches.append( {"id":touchID, "start_pos":Vector(x,y), "pos":Vector(x,y)} )
        return True

    def hideControls(self, dt):
        self.button.hide()
        self.mutebutton.hide()
        self.timeline.hide()

# Register all base widgets
MTWidgetFactory.register('MTVideo', MTVideo)
