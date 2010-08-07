'''
ObjectDisplay: widget that handle fiducial object, and draw them
'''

__all__ = ('MTObjectDisplay', )

from OpenGL.GL import glTranslatef, glRotatef, glVertex2f, GL_LINES
from pymt.graphx import gx_matrix, gx_begin, set_color, drawCSSRectangle
from pymt.ui.widgets.widget import MTWidget
from math import pi

class MTObjectDisplay(MTWidget):
    '''MTObjectDisplay is a widget who draw objects on table'''
    def __init__(self, **kwargs):
        super(MTObjectDisplay, self).__init__(**kwargs)
        self.objects = {}

    def on_touch_down(self, touch):
        if not 'markerid' in touch.profile:
            return
        self.objects[touch.id] = (touch.x, touch.y, -touch.a * 180. / pi)

    def on_touch_move(self, touch):
        if touch.id in self.objects:
            self.objects[touch.id] = (touch.x, touch.y, -touch.a * 180. / pi)

    def on_touch_up(self, touch):
        if touch.id in self.objects:
            del self.objects[touch.id]

    def draw(self):
        if not self.visible:
            return

        for objectID in self.objects:
            x, y, angle = self.objects[objectID]
            with gx_matrix:
                glTranslatef(x, y, 0.0)
                glRotatef(angle, 0.0, 0.0, 1.0)

                set_color(.5)
                drawCSSRectangle(
                    pos=(-0.5 * self.width, -0.5 * self.height),
                    size=(self.width, self.height),
                    style=self.style
                )

                set_color(*self.style['vector-color'])
                with gx_begin(GL_LINES):
                    glVertex2f(0., 0.)
                    glVertex2f(0., -0.5 * self.height)
