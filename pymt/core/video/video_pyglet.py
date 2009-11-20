
'''
VideoPyglet: implementation of VideoBase with Pyglet
'''
try:
    import pyglet
    pyglet.options['shadow_window'] = False
    pyglet.options['debug_gl'] = False
    
    #fix, because of pyglet has a bugfix which is a bad hacked, it checks for context._workaround_unpack_row_length..but actually pyglet does not require own context
    import pyglet.gl
    class FakePygletContext:
        _workaround_unpack_row_length = False
    pyglet.gl.current_context = FakePygletContext()
    
except:
    raise


import threading
import pymt
from . import VideoBase
from pymt.graphx import get_texture_target, set_texture, drawTexturedRectangle, set_color, drawRectangle
from OpenGL.GL import *



class VideoPyglet(VideoBase):
    '''VideoBase implementation using Pyglet
    '''

    def unload(self):
        self.player = None
        self._source = None
        self._fbo = None

    def load(self):
        self.unload()
        self._source = source = pyglet.media.load(self._filename)
        self._format = self._source.video_format
        self.size = (self._format.width, self._format.height)
        self._player = None
        self._player = pyglet.media.Player()
        self._player.queue(self._source)
        self.play()
        self.stop()
        self.time = self._player.time 

    def update(self):
        if self._source.duration  - self.time < 0.01 :
            self.seek(0)
            self.time = 0
        if self.state == 'playing':
            self.time += pymt.getFrameDt()
            self._player.dispatch_events(pymt.getFrameDt())
        

    def stop(self):
        self._player.pause()
        super(VideoPyglet,self).stop()

    def play(self):
        self._player.play()
        super(VideoPyglet,self).play()

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
            glDisable(GL_BLEND)
            self._player.get_texture().blit(*self.pos)
            
        
