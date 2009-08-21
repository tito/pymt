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
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('opacity', 150)
        kwargs.setdefault('rotation', 0)
        
        super(MTAnimatedGif, self).__init__(**kwargs)
        
        self.scale = kwargs.get('scale')
        self.opacity = kwargs.get('opacity')
        self.rotation = kwargs.get('rotation')
        
        #Check to see if we're loading a file or an image sequence.
        if(kwargs.get('filename') != None):
            self.animation = pyglet.image.load_animation(kwargs.get('filename'))
        else:
            self.animation = pyglet.image.Animation.from_image_sequence(sequence=kwargs.get('sequence'), period=kwargs.get('delay'), loop=True)
        self.bin = pyglet.image.atlas.TextureBin()
        self.animation.add_to_texture_bin(self.bin)
        self.image = pyglet.sprite.Sprite(self.animation)
        
        self.size = self.animation.get_max_width(), self.animation.get_max_height()
    
    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.size           = self.image.width, self.image.height
        self.image.opacity  = self.opacity
        self.image.rotation = self.rotation
        self.image.draw()
        
MTWidgetFactory.register('MTAnimatedGif', MTAnimatedGif)