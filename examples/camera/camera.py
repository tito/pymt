from pymt import *
from pyglet.gl import *
from pyglet.image import Texture
from opencv import *


class MTCameraWidget(MTWidget):
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
        kwargs.setdefault('camera_id', 0)
        self.capture_device = cvCaptureFromCAM(kwargs['camera_id'])
        self.frame          = cvQueryFrame( self.capture_device )

        try:
            self.frame_texture  = Texture.create(self.frame.width, self.frame.height)
            self.frame_texture.tex_coords = (1,1,0,  0,1,0,  0,0,0, 1,0,0)
            kwargs.setdefault('size', (self.frame.width, self.frame.height) )
        except Exception, e:
            print "Couldn't get Image from Camera!", e

        super(MTCameraWidget, self).__init__(**kwargs)


    def copy_cv_to_gpu(self):
        '''copies the openCV image to the gpu, so we can use it as a texture'''
        format = GL_RGBA
        if self.frame.channelSeq == "BGR":
            format = GL_BGR_EXT
        glEnable(GL_TEXTURE_2D);
        glBindTexture(GL_TEXTURE_2D, get_texture_id(self.frame_texture));
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.frame.width, self.frame.height, 0, format, GL_UNSIGNED_BYTE, self.frame.imageData);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glBindTexture(GL_TEXTURE_2D,0);


    def draw(self):
        '''draws the current camera frame. If camera initialization failed, it draws a message that no camera image is available'''
        if self.capture_device:
            glColor3f(1,1,1)
            self.frame  = cvQueryFrame( self.capture_device )
            self.copy_cv_to_gpu()
            drawTexturedRectangle(self.frame_texture, pos=self.pos, size=self.size)
        else:
            drawRectangle(pos=self.pos, size=self.size)
            drawLabel("No Camera :(", pos=(self.width/2, self.height/2))


if __name__ == "__main__":
    w = MTWindow()
    c = MTCameraWidget()
    s = MTScatterWidget(size=c.size)
    s.add_widget(c)
    w.add_widget(s)
    runTouchApp()

