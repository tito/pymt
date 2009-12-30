'''
Camera: Backend for acquiring camera image
'''

__all__ = ('CameraBase', 'Camera')

import pymt
from OpenGL.GL import GL_RGB
from abc import ABCMeta, abstractmethod
from .. import core_select_lib
from ...baseobject import BaseObject
from ...graphx import set_color, drawRectangle, drawTexturedRectangle, drawLabel

class CameraBase(BaseObject):
    '''Abstract Camera Widget class.
    
    Concrete camera classes must implement initializaation and
    frame capturing to buffer that can be uploaded to gpu.

    :Parameters:
        `size` : tuple (int, int)
            Size at which the image is drawn. If no size is specified,
            it defaults to resolution of the camera image.
        `resolution` : tuple (int, int)
            Resolution to try to request from the camera.
            Used in the gstreamer pipeline by forcing the appsink caps
            to this resolution. If the camera doesnt support the resolution
            a negotiation error might be thrown.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        kwargs.setdefault('stopped', False)
        kwargs.setdefault('resolution', (640,480))
        kwargs.setdefault('video_src', 0)
        kwargs.setdefault('color', (1, 1, 1, 1))

        self.color          = kwargs.get('color')
        self.stopped        = kwargs.get('stopped')
        self._resolution    = kwargs.get('resolution')
        self._video_src     = kwargs.get('video_src')
        self._buffer        = None
        self._format        = GL_RGB
        self._texture       = None
        self.capture_device = None
        kwargs.setdefault('size', self._resolution)

        super(CameraBase, self).__init__(**kwargs)

        self.init_camera()

        if not self.stopped:
            self.start()


    def _set_resolution(self, res):
        self._resolution = res
        self.init_camera()
    def _get_resolution(self):
        return self._resolution
    resolution = property(lambda self: self._get_resolution(),
                lambda self, x: self._set_resolution(x),
                doc='Resolution of camera capture (width, height)')

    def _set_video_src(self, src):
        self._video_src = src
        self.init_camera()
    def _get_video_src(self):
        return self._video_src
    video_src = property(lambda self: self._get_video_src(),
                lambda self, x: self._set_video_src(x),
                doc='Source of the camera')

    def _get_texture(self):
        return self._texture
    texture = property(lambda self: self._get_texture(),
                doc='Return the camera texture with the latest capture')

    @abstractmethod
    def init_camera(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def start(self):
        self.stopped = False

    def stop(self):
        self.stopped = True

    def _copy_to_gpu(self):
        '''Copy the the buffer into the texture'''
        if self._texture is None:
            pymt.pymt_logger.debug('Camera: copy_to_gpu() failed, _texture is None !')
            return
        self._texture.blit_buffer(self._buffer, format=self._format)
        self._buffer = None

    def draw(self):
        '''Draw the current image camera'''
        if self._texture:
            pymt.set_color(*self.color)
            pymt.drawTexturedRectangle(self._texture, pos=self.pos, size=self.size)
        else:
            pymt.drawRectangle(pos=self.pos, size=self.size)
            pymt.drawLabel('No Camera :(', pos=(self.width/2, self.height/2))

# Load the appropriate provider
Camera = core_select_lib('camera', (
    ('gstreamer', 'camera_gstreamer', 'CameraGStreamer'),
    ('opencv', 'camera_opencv', 'CameraOpenCV'),
    ('videocapture', 'camera_videocapture', 'CameraVideoCapture'),
))
