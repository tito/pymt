import unittest
import pymtcore
import os
from OpenGL.GL import *

__all__ = ['CoreTextTestCase']

class CoreTextTestCase(unittest.TestCase):
    def testTextTexture(self):
        # setup a window
        win = pymtcore.CoreWindow()
        win.size = 640, 480
        win.setup()

        # create a image, and get the texture
        global text
        text = pymtcore.CoreText()
        text._set_label('Hello world !!!')
        texture = text.get_texture()
        self.failUnless(texture is not None)

        def on_wid_draw(data):
            global text
            texture = text.get_texture()
            glColor3f(1, 1, 1)
            glEnable(texture.target)
            glBindTexture(texture.target, texture.id)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(0, 0)
            glTexCoord2f(1, 0)
            glVertex2f(texture.width, 0)
            glTexCoord2f(1, 1)
            glVertex2f(texture.width, texture.height)
            glTexCoord2f(0, 1)
            glVertex2f(0, texture.height)
            glEnd()
            text._set_label("Hello world !!! %f" % pymtcore.get_ticks())


        # create a widget
        wid = pymtcore.CoreWidget()
        wid.connect('on_draw', on_wid_draw)
        win.add_widget(wid)

        # start displaying for 1s
        import time
        start = time.time()
        while time.time() - start < 3:
            win.dispatch_event('on_update', [])
            win.dispatch_event('on_draw', [])
