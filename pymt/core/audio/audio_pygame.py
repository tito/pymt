'''
AudioPygame: implementation of Sound with Pygame
'''

__all__ = ('SoundPygame', )

import pymt
from . import Sound, SoundLoader

try:
    import pygame
except:
    raise

# init pygame sound
pygame.mixer.init()

class SoundPygame(Sound):
    __slots__ = ('_data')

    @staticmethod
    def extensions():
        return ('wav', 'ogg', )

    def __init__(self, **kwargs):
        self._data = None
        super(SoundPygame, self).__init__(**kwargs)

    def play(self):
        if not self._data:
            return
        self._data.play()

    def stop(self):
        if not self._data:
            return
        self._data.stop()

    def load(self):
        self.unload()
        if self.filename is None:
            return
        self._data = pygame.mixer.Sound(self.filename)

    def unload(self):
        self.stop()
        self._data = None

    def _get_volume(self):
        if self._data is not None:
            self._volume = self._data_.get_volume()
        return super(SoundPygame, self)._get_volume()

    def _set_volume(self, volume):
        if self._data is not None:
            self._data_.set_volume(volume)
        return super(SoundPygame, self)._get_volume()

SoundLoader.register(SoundPygame)
