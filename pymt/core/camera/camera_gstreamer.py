'''
GStreamer Camera: Implement CameraBase with GStreamer
'''

__all__ = ('CameraGStreamer', )

import pymt
from . import CameraBase

try:
    import gst
except:
    raise

class CameraGStreamer(CameraBase):
    '''Implementation of CameraBase using GStreamer
    
    :Parameters:
        `video_src` : str, default is 'v4l2src'
            Other tested options are: 'dc1394src' for firewire
            dc camera (e.g. firefly MV). Any gstreamer video source
            should potentially work.
            Theoretically a longer string using "!" can be used
            describing the first part of a gstreamer pipeline.
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('video_src', 'v4l2src')
        self._pipeline = None
        self._camerasink = None
        super(MTGstCamera, self).__init__(**kwargs)

    def init_camera(self):
        # TODO: This does not work when camera resolution is resized at runtime...
        # there must be some other way to release the camera?
        if self._pipeline:
            self._pipeline = None

        GL_CAPS = 'video/x-raw-rgb,red_mask=(int)0xff0000,green_mask=(int)0x00ff00,blue_mask=(int)0x0000ff'
        self._pipeline = gst.parse_launch('%s ! ffmpegcolorspace ! appsink name=camerasink emit-signals=True caps=%s' % (self.video_src, GL_CAPS) )
        self._camerasink = self._pipeline.get_by_name('camerasink')
        self._camerasink.connect('new-buffer', self._gst_new_buffer)

        if self._camerasink and not self.stopped:
            self.start_capture()

    def _gst_new_buffer(self):
        self._format = GL_RGB
        self._buffer = self._camerasink.emit('pull-buffer')
        if self._texture is None:
            # try to get resolution
            self._pipeline.src_pads()

    def start(self):
        self.stopped = False
        self._pipeline.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.stopped = True
        self._pipeline.set_state(gst.STATE_PAUSED)

    def update(self):
        self.frame = self._camerasink.emit('pull-buffer')
        self.format = GL_RGB

        self.buffer = self.frame.data
        self.copy_buffer_to_gpu()
