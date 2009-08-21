'''
Animated GIF: A simple MT Widget which extends support for Pyglet's animated gif functionality.
'''

from __future__ import with_statement

__all__ = ['MTAnimatedGif']

import pyglet
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTAnimatedGif(MTWidget):
    '''MTAnimatedGif is a simple MT widget with support for Pyglet's animated gif functions.'''
    def __init__(self, **kwargs):
        super(MTAnimatedGif, self).__init__(**kwargs)
        self.animation = pyglet.image.load_animation(kwargs.get('filename'))
        self.bin = pyglet.image.atlas.TextureBin()
        self.animation.add_to_texture_bin(self.bin)
        self.image = pyglet.sprite.Sprite(self.animation)
        
        self.size = self.animation.get_max_width(), self.animation.get_max_height()
    
    def draw(self):
        self.image.draw()
        
MTWidgetFactory.register('MTAnimatedGif', MTAnimatedGif)