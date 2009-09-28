import unittest
import pymtcore
import os
from OpenGL.GL import *

__all__ = ['CoreImageTestCase']

class CoreImageTestCase(unittest.TestCase):
    def testImagePNG(self):
        filename = os.path.join(os.path.dirname(__file__), 'pngtest.png')
        image = pymtcore.CoreImage(filename)
        self.failUnless(image.pixels is not None)
        self.failUnless(image._width == 91)
        self.failUnless(image._height == 69)

    def testImageTexture(self):
        filename = os.path.join(os.path.dirname(__file__), 'pngtest.png')

        # setup a window
        win = pymtcore.CoreWindow()
        win.size = 640, 480
        win.setup()

        # create a image, and get the texture
        global texture
        image = pymtcore.CoreImage(filename)
        self.failUnless(image.pixels is not None)
        texture = image.get_texture()
        self.failUnless(texture is not None)

        def on_wid_draw(data):
            global texture
            glColor3f(1, 1, 1)
            glEnable(texture.target)
            glBindTexture(texture.target, texture.id)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(0, 0)
            glTexCoord2f(1, 0)
            glVertex2f(640, 0)
            glTexCoord2f(1, 1)
            glVertex2f(640, 480)
            glTexCoord2f(0, 1)
            glVertex2f(0, 480)
            glEnd()

        # create a widget
        wid = pymtcore.CoreWidget()
        wid.connect('on_draw', on_wid_draw)
        win.add_widget(wid)

        # start displaying for 1s
        import time
        start = time.time()
        while time.time() - start < 0.1:
            win.dispatch_event('on_update', [])
            win.dispatch_event('on_draw', [])
