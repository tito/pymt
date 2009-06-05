'''
Object: widget that handle fiducial object, and draw them
'''

from __future__ import with_statement
__all__ = ['MTObjectDisplay']

from pyglet.gl import *
from ...graphx import gx_matrix, gx_begin, set_color
from ...graphxcss import drawCSSRectangle
from ..factory import MTWidgetFactory
from math import pi
from widget import MTWidget

class MTObjectDisplay(MTWidget):
    '''MTObjectDisplay is a widget who draw objects on table'''
    def __init__(self, **kwargs):
        super(MTObjectDisplay, self).__init__(**kwargs)
        self.objects = {}

    def on_object_down(self, objects, objectID, id, x, y, angle):
        self.objects[objectID] = (x, y, -angle * 180. / pi)

    def on_object_move(self, objects, objectID, id, x, y, angle):
        if objectID in self.objects:
            self.objects[objectID] = (x, y, -angle * 180. / pi)

    def on_object_up(self, objects, objectID, id, x, y, angle):
        if objectID in self.objects:
           del self.objects[objectID]

    def draw(self):
        if not self.visible:
            return

        for objectID in self.objects:
            x, y, angle = self.objects[objectID]
            with gx_matrix:
                glTranslatef(x, y, 0.0)
                glRotatef(angle, 0.0, 0.0, 1.0)

                set_color(*self.style['bg-color'])
                drawCSSRectangle(
                    pos=(-0.5 * self.width, -0.5 * self.height),
                    size=(self.width, self.height),
                    style=self.style
                )

                set_color(*self.style['vector-color'])
                with gx_begin(GL_LINES):
                    glVertex2f(0.0,0.0)
                    glVertex2f(0, -0.5 * self.height)

MTWidgetFactory.register('MTObjectDisplay', MTObjectDisplay)
