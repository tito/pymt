'''
Video widget: provide a video container

.. warning::
    Library avbin is needed for using MTVideoPlayer.
    Check http://code.google.com/p/avbin/ for more information.
'''

from __future__ import with_statement
__all__ = ['MTVideo','MTVideoView','MTSimpleVideo']

import os
import pyglet
import pymt
from OpenGL.GL import *
from pyglet.media import *
from ....image import Image
from ....utils import boundary
from ....graphx import set_color, drawRectangle, drawTexturedRectangle, DO, gx_matrix
from ...factory import MTWidgetFactory
from ..button import MTImageButton
from ..slider import MTSlider
from ..scatter import MTScatterWidget
from ..widget import MTWidget
from time import sleep

iconPath = os.path.dirname(pymt.__file__) + '/data/icons/'

class MTVideoView(MTWidget):
    def __init__(self,**kwargs):
        '''Basic view of a video widgets, it just contains the playing video with no control buttons.

        :Parameters:
            `filename`: str, default to None
                Path to the video file
            `on_playback_end`: str, default to 'pause'
                Specifies what has to be done after video playback ends. options 'pause','loop','next'
            `volume`: float, default to 1.0
                Video playback volume. Value ranges from 0.0 to 1.0

        :Events:
            `on_playback_end`
                Fired when the video reaches the end of one loop.
        '''

        kwargs.setdefault('on_playback_end', 'pause')
        kwargs.setdefault('volume', 1.0) 
        if 'filename' in kwargs:
            kwargs['filename'] = kwargs.get('filename')
        if kwargs.get('filename') is None:
            raise Exception('No video given to MTVideo')
        super(MTVideoView, self).__init__(**kwargs)
        self.player            = Player()
        self.source            = pyglet.media.load(kwargs.get('filename'))
        self.source_duration   = self.source.duration
        self.player.queue(self.source)
        self.player.eos_action = kwargs.get('on_playback_end')
        self.player.volume     = kwargs.get('volume')
        video_texture          = self.player.get_texture()
        self.width             = video_texture.width
        self.height            = video_texture.height
        self.state             = 'paused'

        self.register_event_type('on_playback_end')
        self.player.seek(0)
        @self.player.event
        def on_eos(*largs):
            self.dispatch_event('on_playback_end')

    def __del__(self):
        self.player.stop()

    def draw(self):
        set_color(1,1,1)
        drawTexturedRectangle(texture=self.get_texture(),pos=self.pos,size=(self.width,self.height))

    def play(self):
        '''Start the video'''
        self.state = 'playing'
        self.player.play()

    def stop(self):
        '''Stop the video'''
        self.state = 'stopped'
        self.player.pause()
        self.player.next()

    def pause(self):
        '''Pause the video'''
        self.state = 'pause'
        self.player.pause()

    def rewind(self):
        '''Rewinds the video'''
        self.player.seek(0)
        self.state = 'pause'

    def set_volume(self, value):
        '''Set the video audio playback volume'''
        self.player.volume = boundary(value, 0.0, 1.0)

    def get_volume(self, value):
        '''returns the video audio playback volume'''
        return self.player.volume

    def get_current_time(self):
        '''Returns current playback time'''
        return self.player.time

    def get_texture(self):
        '''Returns current video frame texture'''
        return self.player.get_texture()

    def on_playback_end(self):
        pass


class MTSimpleVideo(MTVideoView):
    def __init__(self,**kwargs):
        '''Provides a basic Video Widget with options on controlling the playback.
           * Double tap: Pause/Play
           * Two Finger Double tap: Rewind
        '''
        super(MTSimpleVideo, self).__init__(**kwargs)
        self.current_touches = {}

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.current_touches[touch.uid] = (touch.x, touch.y)
            if len(self.current_touches)==2 :
                if touch.is_double_tap:
                    self.rewind()
            elif touch.is_double_tap:
                if self.state == 'playing':
                    self.pause()
                else:
                    self.play()

        return super(MTSimpleVideo, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.uid in self.current_touches:
            del self.current_touches[touch.uid]
        return super(MTSimpleVideo, self).on_touch_up(touch)


class MTVideoPlayPause(MTImageButton):
    '''MTVideoPlayPause is a dynamic play/pause button of the video widget'''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', iconPath + 'videoWidgetPlay.png')
        kwargs.setdefault('filename_pause', iconPath + 'videoWidgetPause.png')
        kwargs.setdefault('player', None)
        super(MTVideoPlayPause, self).__init__(**kwargs)
        self.player          = kwargs.get('player')
        self.playState       = 'Pause'

        self.images          = {}
        self.images['Play']  = Image(kwargs.get('filename'))
        self.images['Pause'] = Image(kwargs.get('filename_pause'))

        self.scale    = 0.75

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        self.state = ('down', touch.id)

        if self.playState == 'Pause':
            self.parent.play()
            self.playState = 'Play'
        elif self.playState == 'Play':
            self.parent.pause()
            self.playState = 'Pause'
        self.image = self.images[self.playState]


class MTVideoMute(MTImageButton):
    '''MTVideoMute is a mute button class of the video widget'''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', iconPath + 'videoWidgetMute.png')
        kwargs.setdefault('player', None)
        super(MTVideoMute, self).__init__(**kwargs)
        self.vid         = kwargs.get('player')
        self.playState   = 'NotMute'
        self.scale       = 0.75
        self.prev_volume = 1.0

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = ('down', touch.id)
            if self.playState == 'NotMute':
                self.prev_volume = self.vid.volume
                self.parent.set_volume(0.0)
                self.playState = 'Mute'
            elif self.playState == 'Mute':
                self.parent.set_volume(self.prev_volume)
                self.playState = 'NotMute'

class MTVideoTimeline(MTSlider):
    '''MTVideoTimeline is a part of the video widget which tracks the video playback'''
    def __init__(self, **kwargs):
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('player', None)
        kwargs.setdefault('duration', 100)
        kwargs.setdefault('color', (.78, .78, .78, 1.0))

        super(MTVideoTimeline, self).__init__(**kwargs)
        self.vid     = kwargs.get('player')
        self.max     = kwargs.get('duration')
        self.padding = kwargs.get('padding')
        self.width   = self.vid.get_texture().width-85
        self.height  = 30
        self.length  = 0

    def draw(self):
        self.value = self.vid.time % self.max

        if self.vid.time == self.max:
            self.value = 0
            self.vid.seek(0)
            self.length = 0

        x,y,w,h = self.x,self.y,self.width+self.padding, self.height
        p2 =self.padding/2
        # draw outer rectangle
        set_color(0.2,0.2,0.2,0.5)
        drawRectangle(pos=(x,y), size=(w,h))
        # draw inner rectangle
        set_color(*self.style.get('bg-color'))
        self.length = int(self.width*(float(self.value)/self.max))
        drawRectangle(pos=(self.x+p2,self.y+p2+11), size=(self.length,(h-self.padding)/2))
        set_color(0.713, 0.713, 0.713, 1.0)
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

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.touchstarts.append(touch.id)
            return True

    def on_touch_move(self, touch):
        pass

    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)

class MTVideo(MTSimpleVideo):
    '''MTVideo is a video player, with control buttons.
    You can use it like this ::

          video = MTVideo(filename='source_file')

    :Parameters:
        `filename` : str
            Filename of video

    '''
    def __init__(self, **kwargs):
        super(MTVideo, self).__init__(**kwargs)        
        self.controls_visible = False
        self.button           = MTVideoPlayPause(pos=(0,0), player=self)
        self.add_widget(self.button)
        self.mutebutton       = MTVideoMute(pos=(36,0), player=self.player)
        self.add_widget(self.mutebutton)
        self.timeline         = MTVideoTimeline(pos=(72,3),player=self.player,duration=self.source_duration)
        self.add_widget(self.timeline)        
        self.hide_controls()

    def draw(self):
        with gx_matrix:
            set_color(1,1,1,0.5)
            drawRectangle((-10,-10),(self.width+20,self.height+20))
            super(MTVideo, self).draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if not self.controls_visible:
                self.show_controls()
                pyglet.clock.schedule_once(self.hide_controls, 5)
        return super(MTVideo, self).on_touch_down(touch)

    def show_controls(self, dt=0):
        '''Makes the video controls visible'''
        self.controls_visible = True
        self.button.show()
        self.mutebutton.show()
        self.timeline.show()

    def hide_controls(self, dt=0):
        '''Hides the video controls'''
        self.controls_visible = False
        self.button.hide()
        self.mutebutton.hide()
        self.timeline.hide()


# Register all base widgets
MTWidgetFactory.register('MTVideo', MTVideo)
MTWidgetFactory.register('MTVideoView', MTVideoView)
MTWidgetFactory.register('MTSimpleVideo', MTSimpleVideo)
