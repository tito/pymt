'''
Text Pyglet: Draw text with pyglet
'''

__all__ = ('LabelPyglet', )

import pymt
import OpenGL.GL
from . import LabelBase

try:
    import pyglet
    import pyglet.text
except:
    raise

class LabelPyglet(LabelBase):
    _fbo = None
    def update(self):
        label = pyglet.text.Label(
            self.label, font_name=self.options['font_name'],
            font_size=self.options['font_size'],
            bold=self.options['bold'],
            italic=self.options['italic']
        )

        if label.content_width == 0 or label.content_height == 0:
            self.texture = pymt.Texture.create(1, 1)
        else:
            if self._fbo is None or \
               self._fbo.size != (label.content_width, label.content_height) or True:
                self._fbo = pymt.Fbo(size=(label.content_width, label.content_height),
                           with_depthbuffer=False)
            self._fbo.bind()
            # FIXME don't known why, but seem needed ??
            OpenGL.GL.glClearColor(0, 0, 0, 0)
            OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT)
            label.draw()
            self._fbo.release()
            self.texture = self._fbo.texture

        super(LabelPyglet, self).update()

