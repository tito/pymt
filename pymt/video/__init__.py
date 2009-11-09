'''
VideoBase: base for implementing a video reader
'''

__all__ = ('VideoBase', 'Video')

from ..baseobject import BaseObject
from ..logger import pymt_logger

class VideoBase(BaseObject):
    '''VideoBase, a class to implement a video reader.
    
    :Parameters:
        `filename` : str
            Filename of the video. Can be a file or an URI.
        `color` : list
            Color filter of the video (usually white.)
    '''

    __slots__ = ('_wantplay', '_buffer', '_filename', '_texture', 'color',
                 '_volume')

    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        kwargs.setdefault('color', (1, 1, 1, 1))

        super(VideoBase, self).__init__(**kwargs)

        self._wantplay      = False
        self._buffer        = None
        self._filename      = None
        self._texture       = None
        self._volume        = 1.

        self.color          = kwargs.get('color')
        self.filename       = kwargs.get('filename')

    def __del__(self):
        self.unload()

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
            doc='Get/set the filename/uri of current video')

    def _get_position(self):
        return 0
    def _set_position(self, pos):
        self.seek(pos)
    position = property(lambda self: self._get_position(),
            lambda self, x: self._set_position(x),
            doc='Get/set the position in the video (in seconds)')

    def _get_volume(self):
        return self._volume
    def _set_volume(self, volume):
        self._volume = volume
    volume = property(lambda self: self._get_volume(),
            lambda self, x: self._set_volume(x),
            doc='Get/set the volume in the video (1.0 = 100%)')

    def _get_duration(self):
        return 0
    duration = property(lambda self: self._get_duration(),
            doc='Get the video duration (in seconds)')

    def _get_texture(self):
        return self._texture
    texture = property(lambda self: self._get_texture(),
            doc='Get the video texture')

    def seek(self, percent):
        '''Move on percent position'''
        pass

    def stop(self):
        '''Stop the video playing'''
        pass

    def play(self):
        '''Play the video'''
        pass

    def load(self):
        '''Load the video from the current filename'''
        pass

    def unload(self):
        '''Unload the actual video'''
        pass

    def draw(self):
        '''Draw the current video on screen'''
        pass

Video = None
try:
    import video_gstreamer
    Video = video_gstreamer.VideoGStreamer
    pymt_logger.info('Video: use GStreamer as video provider.')
except:
    pymt_logger.debug('Video: Unable to use GStreamer as video provider.')
    pymt_logger.exception('azpdok')

if Video is None:
    pymt_logger.error('No video provider found')
