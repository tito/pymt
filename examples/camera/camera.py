from pymt import *
from pyglet.gl import *
from pyglet.image import Texture

try:
    from opencv import *
except:
    pymt_logger.warning('No OpenCV available')


try:
    import gst
except:
    print "No gstreamer available!"






class MTCameraBase(MTWidget):

    '''Abstract Camer Widget class.  concrete camera widget classes must implement initializaation and frame capturing to buffer that can be uploaded to gpu'''

    def __init__(self, **kwargs):

        kwargs.setdefault('stopped', False )
        kwargs.setdefault('resolution', (640,480))
        kwargs.setdefault('capture_src', 0)

        self.stopped        = kwargs['stopped']
        self._resolution    = kwargs['resolution']
        self._capture_src   = kwargs['capture_src']
        self.capture_device = None
        kwargs.setdefault('size', self._resolution )

        super(MTCameraBase, self).__init__(**kwargs)
        self.init_camera()

    def _set_resolution(self, res):
        self._resolution = res
        self.init_camera()
    def _get_resolution(self):
        return self._resolution
    resolution = property(_get_resolution, _set_resolution, doc='resolution: resolution of camera capture')


    def _set_capture_src(self, src):
        self._capture_src = src
        self.init_camera()
    def _get_capture_src(self):
        return self._capture_src
    capture_src = property(_get_capture_src, _set_capture_src, doc='resolution: resolution of camera capture')


    def init_camera(self):
        pymt_logger.exception('MTCameraBase is an abstract class.  Use a Sub class providing a specific camera interface instead!')

    def start_capture(self):
        pymt_logger.exception('MTCameraBase is an abstract class.  Use a Sub class providing a specific camera interface instead!')

    def stop_capture(self):
        pymt_logger.exception('MTCameraBase is an abstract class.  Use a Sub class providing a specific camera interface instead!')

    def capture_frame(self):
        pymt_logger.exception('MTCameraBase is an abstract class.  Use a Sub class providing a specific camera interface instead!')


    def copy_buffer_to_gpu(self):
        '''copies the openCV image to the gpu, so we can use it as a texture'''
        glEnable(GL_TEXTURE_2D);
        glBindTexture(GL_TEXTURE_2D, get_texture_id(self.frame_texture));
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.resolution[0],self.resolution[1], 0, self.format, GL_UNSIGNED_BYTE, self.buffer);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glBindTexture(GL_TEXTURE_2D,0);


    def draw(self):
        '''draws the current camera frame. If camera initialization failed, it draws a message that no camera image is available'''
        try:
            set_color(1,1,1)
            if not self.stopped:
                self.capture_frame()
            drawTexturedRectangle(self.frame_texture, pos=self.pos, size=self.size)
        except:
            drawRectangle(pos=self.pos, size=self.size)
            drawLabel("No Camera :(", pos=(self.width/2, self.height/2))







class MTOpenCVCamera(MTCameraBase):
    '''MTCameraWidget is a widget that gets images from a webcam and draws teh image to a texture and the screen.

    :Dependencies:
        'openCV':
            This Widget relies on openCV to acquire images from a great variety of webcams with cross platform support
            You will need to have opencv and python bindings installed.

            You can get OpenCV at http://sourceforge.net/projects/opencvlibrary/
            OpenCV info and documentation can be found here: http://opencv.willowgarage.com/wiki/

        'ctypes-opencv (optional)':
            The regular openCV distribution includes python bindings made using SWIG.
            I have had better luck and much less problems using a ctypes based openCV binding for python.
            You can find those ctype-opencv python module here: http://code.google.com/p/ctypes-opencv/
            They should work if you just have openCV installed as a C library

    :Parameters:
        `camera_id` : int, default is 0
            Label of button
        `size` : tuple (int, int)
            size at which the image is drawn.  if no size is specified, it defaults to resolution of the camera image
    '''

    def __init__(self, **kwargs):
        super(MTOpenCVCamera, self).__init__(**kwargs)

    def init_camera(self):
        if self.capture_device:
            del self.capture_device

        try:
            self.capture_device = cvCaptureFromCAM(self.capture_src)
            cvSetCaptureProperty (self.capture_device, CV_CAP_PROP_FRAME_WIDTH,  self.resolution[0])
            cvSetCaptureProperty (self.capture_device, CV_CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        except:
            self.capture_device = cvCaptureFromCAM(self.capture_src)
            w = cvGetCaptureProperty (self.capture_device, CV_CAP_PROP_FRAME_WIDTH)
            h = cvGetCaptureProperty (self.capture_device, CV_CAP_PROP_FRAME_HEIGHT)
            pymt_logger.exception('Warning: Camera resolution %s not possible!  Defaulting to %s.' % (self.resolution, (w,h)) )
            self._resolution = (w,h)

        self.frame_texture  = Texture.create(*self.resolution)
        self.frame_texture.tex_coords = (1,1,0,  0,1,0,  0,0,0, 1,0,0)

    def start_capture(self):
        self.stopped = False
        self.capture_frame()

    def stop_capture(self):
        self.stopped = True

    def capture_frame(self):
        try:
            self.frame  = cvQueryFrame( self.capture_device )

            self.format = GL_RGBA
            if self.frame.channelSeq == 'BGR':
                self.format = GL_BGR_EXT

            self.buffer = self.frame.imageData
            self.copy_buffer_to_gpu()

        except Exception, e:
            print "Couldn't get Image from Camera!", e








"""


class MTCameraWidgetGST(_CameraWidget):
Comment by txprog, Yesterday (17 hours ago):

- Remove Widget in name
- Support parameter change at runtime

    '''MTCameraWidget is a widget that gets images from a webcam and draws the image to a texture and the screen.

        This camera widget uses gstreamer instead of opencv to aquire images.
        Works with a wide variety of webcams, or other video sources by using gstreamer.
        The first element in the gstreamer pipeline can be set at construction using 'video_src'

        Pulling a frame is blocking right now, need to find a way to figure out whether a new frame is ready or not.
        Not sure how to do this, callbacks require gtk main loop, so rigth now pull-buffer is blocking but working.

    :Parameters:
        `video_src` : str, default is 'v4l2src'
            other tested options are: 'dc1394src' for firewire dc camera (e.g. firefly MV)
        `resolution` : tuple (int, int)
            resolution to try to request from the camera. used in the gstreamer pipeline by forcing teh appsink caps to this resolution.
            if the camera doesnt support the resolution a negotiation error might be thrown.
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('res', (640,480))
        kwargs.setdefault('size', kwargs['res'])
        kwargs.setdefault('video_src', 'v4l2src') #other options: dc1394src, etc..
        self.resolution = kwargs['res']
        self.video_src = kwargs['video_src']
        super(MTCameraWidgetGST, self).__init__(**kwargs)

        GL_CAPS = "video/x-raw-rgb,width=%d,pixel-aspect-ratio=1/1,red_mask=(int)0xff0000,green_mask=(int)0x00ff00,blue_mask=(int)0x0000ff" % (self.resolution[0])
        pipeline = gst.parse_launch("%s ! ffmpegcolorspace ! appsink name=camera_sink emit-signals=True caps=%s" % (self.video_src, GL_CAPS) )
        self.camera_sink = pipeline.get_by_name('camera_sink')
        pipeline.set_state(gst.STATE_PLAYING)

        self.frame = self.camera_sink.emit('pull-buffer')
        self.frame_texture  = Texture.create(640,480)
        self.frame_texture.tex_coords = (1,1,0,  0,1,0,  0,0,0, 1,0,0)


    def captureFrame(self):
        self.frame = self.camera_sink.emit('pull-buffer')
        self.format = GL_RGB

        self.buffer = self.frame.data
        self.copy_frame_to_gpu()

"""





if __name__ == "__main__":
    w = MTWindow()
    c = MTOpenCVCamera(resolution=(640,480))
    s = MTScatterWidget(size=c.size)
    s.add_widget(c)
    w.add_widget(s)
    runTouchApp()

