
'''
VideoPyglet: implementation of VideoBase with Pyglet
'''

try:
    import pyglet
except:
    raise

import pymt
from OpenGL.GL import glDisable, GL_BLEND
from . import VideoBase


#have to set these before importing pyglet.gl
#otherwise pyglet creates a seperate gl context and fails on error checks becasue we use pygame window
pyglet.options['shadow_window'] = False
pyglet.options['debug_gl'] = False
import pyglet.gl

#another pyglet fix, because pyglet has a bugfix which is a bad hacked,
#it checks for context._workaround_unpack_row_length..but we're using the implicit context form pyglet or glut window
#this means we cant have a pyglet window provider though! if we do, this will break pyglet window context
class FakePygletContext:
    _workaround_unpack_row_length = False
pyglet.gl.current_context = FakePygletContext()





class VideoPyglet(VideoBase):
    '''VideoBase implementation using Pyglet
    '''

    def unload(self):
        self.player = None
        self._source = None
        self._fbo = None

    def load(self):
        self.unload() #make sure we unload an resources

        #load media file and set size of video
        self._source = source = pyglet.media.load(self._filename)
        self._format = self._source.video_format
        self.size = (self._format.width, self._format.height)

        #load pyglet player and have it play teh video we loaded
        self._player = None
        self._player = pyglet.media.Player()
        self._player.queue(self._source)
        self.play()
        self.stop()

        #we have to keep track of tie ourselves..at least its the only way i can get pyglet player to restart,
        #_player.time does not get reset when you do seek(0) for soe reason, and is read only
        self.time = self._player.time

    def update(self):
        if self._source.duration  - self.time < 0.1 : #we are at the end
            self.seek(0)
        if self.state == 'playing':
            self.time += pymt.getFrameDt() #keep track of time into video
            self._player.dispatch_events(pymt.getFrameDt()) #required by pyglet video if not in pyglet window

    def stop(self):
        self._player.pause()
        super(VideoPyglet, self).stop()

    def play(self):
        self._player.play()
        super(VideoPyglet, self).play()

    def seek(self, percent):
        t = self._source.duration*percent
        self.time = t
        self._player.seek(t)
        self.stop()

    def _get_position(self):
        if self._player:
            return self.time

    def _get_duration(self):
        if self._source:
            return self._source.duration

    def _get_volume(self):
        if self._player:
            return self._player.volume
        return 0

    def _set_volume(self, volume):
        if self._player:
            self._player.volume = volume

    def draw(self):
        if self._player.get_texture():
            glDisable(GL_BLEND) #dont know why this is needed...but it gets very dark otherwise, even if i set color
            self._player.get_texture().blit(*self.pos)


