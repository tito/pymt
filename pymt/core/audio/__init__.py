'''
Audio: Load and play sound
'''

__all__ = ('Sound', 'SoundLoader')

import pymt
from abc import ABCMeta, abstractmethod
from .. import core_register_libs


class SoundLoader:
    '''Load a sound, with usage of the best loader for a given filename.
    If you want to load an audio file ::

        sound = SoundLoader.load(filename='test.wav')
        if not sound:
            # unable to load this sound ?
            pass
        else:
            # sound loaded, let's play!
            sound.play()

    '''

    _classes = []

    @staticmethod
    def register(classobj):
        SoundLoader._classes.append(classobj)

    @staticmethod
    def load(filename):
        ext = filename.split('.')[-1].lower()
        for classobj in SoundLoader._classes:
            if ext in classobj.extensions():
                return classobj(filename=filename)
        pymt.pymt_logger.warning('Audio: Unable to found a loader for <%s>' %
                                 filename)
        return None


class Sound(object):
    '''Represent a sound to play. This class is abstract, and cannot be used
    directly.
    Use SoundLoader to load a sound !
    '''

    __metaclass__ = ABCMeta
    __slots__ = ('_filename', '_volume')

    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        kwargs.setdefault('volume', 1.)

        self._volume    = kwargs.get('volume')
        self._filename  = kwargs.get('filename')
        self.load()

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
        if filename == self._filename:
            return
        self.unload()
        self._filename = filename
        if self._filename is None:
            return
        self.load()
    filename = property(lambda self: self._get_filename(),
            lambda self, x: self._set_filename(x),
            doc='Get/set the filename/uri of the sound')

    def _get_volume(self):
        return self._volume
    def _set_volume(self, volume):
        if self._volume == volume:
            return
        self._volume = volume
    volume = property(lambda self: self._get_volume(),
            lambda self, x: self._set_volume(x),
            doc='Get/set the volume of the sound')

    def _get_length(self):
        return 0
    length = property(lambda self: self._get_length(),
            doc='Get length of the sound (in seconds)')

    @abstractmethod
    def load(self):
        '''Load the file into memory'''
        pass

    @abstractmethod
    def unload(self):
        '''Unload the file from memory'''
        pass

    @abstractmethod
    def play(self):
        '''Play the file'''
        pass

    @abstractmethod
    def stop(self):
        '''Stop playback'''
        pass


core_register_libs('audio', (
    ('pygame', 'audio_pygame'),
))
