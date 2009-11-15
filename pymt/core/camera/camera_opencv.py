'''
OpenCV Camera: Implement CameraBase with OpenCV
'''

#
# TODO: make usage of thread !!!
#

__all__ = ('CameraOpenCV', )

import pymt
from . import CameraBase
from OpenGL.GL import GL_RGB, GL_BGR_EXT

try:
    import opencv as cv
    import opencv.highgui
except:
    raise

class CameraOpenCV(CameraBase):
    '''Implementation of CameraBase using OpenCV
    
    :Parameters:
        `video_src` : str, default is 'v4l2src'
            Other tested options are: 'dc1394src' for firewire
            dc camera (e.g. firefly MV). Any OpenCV video source
            should potentially work.
            Theoretically a longer string using "!" can be used
            describing the first part of a OpenCV pipeline.
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('video_src', 0)
        self._device = None
        super(CameraOpenCV, self).__init__(**kwargs)

    def init_camera(self):
        self._device = opencv.highgui.cvCreateCameraCapture(self.video_src)
        try:
            cv.opencv.highgui(self._device, cv.CV_CAP_PROP_FRAME_WIDTH,
                              self.resolution[0])
            cv.opencv.highgui(self._device, cv.CV_CAP_PROP_FRAME_HEIGHT,
                              self.resolution[1])
            frame  = opencv.highgui.cvQueryFrame(self._device)
            if not int(frame.width) == self.resolution[0]:
                raise Exception('Resolution not supported')
        except:
            w = int(opencv.highgui.cvGetCaptureProperty(self._device,
                    opencv.highgui.CV_CAP_PROP_FRAME_WIDTH))
            h = int(opencv.highgui.cvGetCaptureProperty(self._device,
                    opencv.highgui.CV_CAP_PROP_FRAME_HEIGHT))
            frame  = opencv.highgui.cvQueryFrame(self._device)
            pymt.pymt_logger.warning('Warning: Camera resolution %s not possible!  Defaulting to %s.' % (self.resolution, (w,h)))
            self._resolution = (w,h)

        self._texture = pymt.Texture.create(*self._resolution)
        self._texture.flip_vertical()

        if not self.stopped:
            self.start()

    def start(self):
        self.stopped = False

    def stop(self):
        self.stopped = True

    def update(self):
        if self.stopped:
            return
        try:
            frame = opencv.highgui.cvQueryFrame(self._device)
            self._format = GL_BGR_EXT
            self._buffer = frame.imageData
            self._copy_to_gpu()
        except:
            pymt.pymt_logger.exception('Couldnt get image from Camera')

