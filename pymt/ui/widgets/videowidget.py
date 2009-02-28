from __future__ import with_statement
import pymt
from pymt import *
from pyglet.gl import *
from pymt.ui.widgets import *
from pyglet.media import *
from button import *
from slider import *
from scatter import *
from time import sleep

iconPath = os.path.dirname(pymt.__file__) + '/data/icons/'

class MTVideoPlayPause(MTImageButton):
    '''MTVideoPlayPause is a dynamic play/pause button of the video widget'''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', iconPath + 'videoWidgetPlay.png')
        kwargs.setdefault('filename_pause', iconPath + 'videoWidgetPause.png')
        kwargs.setdefault('player', None)
        super(MTVideoPlayPause, self).__init__(**kwargs)
        self.vid        = kwargs.get('player')
        self.playState  = 'Pause'

        self.images = {} #crate a python dictionary..like a hash map
        self.images['Play']  = pyglet.sprite.Sprite(image.load(kwargs.get('filename')))
        self.images['Pause'] = pyglet.sprite.Sprite(image.load(kwargs.get('filename_pause')))

        self.scale    = 0.75

    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            if self.playState == 'Pause':
                self.vid.play()
                self.playState = 'Play'
            elif self.playState == 'Play':
                self.vid.pause()
                self.playState = 'Pause'

            #set the correct image
            self.image = self.images[self.playState]  #playState is one of the two strings that are used as keys/lookups in the dictionary


class MTVideoMute(MTImageButton):
    '''MTVideoMute is a mute button class of the video widget'''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', iconPath + 'videoWidgetMute.png')
        kwargs.setdefault('player', None)
        super(MTVideoMute, self).__init__(**kwargs)
        self.vid = kwargs.get('player')
        self.playState = 'NotMute'
        self.scale    = 0.75

    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            self.state = ('down', touchID)
            if self.playState == 'NotMute':
                self.vid.volume = 0.0
                self.playState = 'Mute'
            elif self.playState == 'Mute':
                self.vid.volume = 1.0
                self.playState = 'NotMute'

class MTVideoTimeline(MTSlider):
    '''MTVideoTimeline is a part of the video widget which tracks the video playback'''
    def __init__(self, **kwargs):
        kwargs.setdefault('player', None)
        kwargs.setdefault('duration', 100)
        kwargs.setdefault('color', (.78, .78, .78, 1.0))

        super(MTVideoTimeline, self).__init__(**kwargs)
        self.vid = kwargs.get('player')
        self.max = kwargs.get('duration')
        self.width = self.vid.get_texture().width-85
        self.height = 30
        self.length = 0

    def draw(self):
        self.value = self.vid.time % self.max

        if self.vid.time == self.max:
            self.value = 0
            self.vid.seek(0)
            self.length = 0

        with gx_blending:
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
    '''MTVideo is a video player, implemented in top of MTScatterWidget.
    You can use it like this ::

          video = MTVideo(video='source_file')

    :Parameters:
        `video` : stsize=iw.size, r
            Filename of video

    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('video', None)
        if kwargs.get('video') is None:
            raise Exception('No video given to MTVideo')

        super(MTVideo, self).__init__(**kwargs)
        self.player = Player()
        self.source = pyglet.media.load(kwargs.get('video'))
        self.sourceDuration = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = 'pause'
        self.width = self.player.get_texture().width
        self.height = self.player.get_texture().height
        self.texW = self.player.get_texture().width
        self.texH = self.player.get_texture().height

        #init as subwidgest.  adding them using add_widgtes
        #makes it so that they get the events before MTVideo instance
        #the pos, size is relative to this parent widget...if it scales etc so will these
        self.button = MTVideoPlayPause(pos=(0,0), player=self.player)
        self.add_widget(self.button)
        self.button.hide()

        self.mutebutton = MTVideoMute(pos=(36,0), player=self.player)
        self.add_widget(self.mutebutton)
        self.mutebutton.hide()

        self.timeline = MTVideoTimeline(pos=(72,3),player=self.player,duration=self.sourceDuration)
        self.add_widget(self.timeline)
        self.timeline.hide()

    def draw(self):
        with DO(gx_matrix, gx_blending):
            glColor4f(1,1,1,0.5)
            drawRectangle((-10,-10),(self.texW+20,self.texH+20))
            glColor3d(1,1,1)
            self.player.get_texture().blit(0,0)

    def on_touch_down(self, touches, touchID, x, y):
        #if the touch isnt on teh widget we do nothing
        if self.collide_point(x,y):
            self.button.show()
            self.mutebutton.show()
            self.timeline.show()
            pyglet.clock.schedule_once(self.hide_controls, 5)
        return super(MTVideo, self).on_touch_down(touches, touchID, x, y)

    def hide_controls(self, dt):
        self.button.hide()
        self.mutebutton.hide()
        self.timeline.hide()

# Register all base widgets
MTWidgetFactory.register('MTVideo', MTVideo)
