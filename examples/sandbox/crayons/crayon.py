from __future__ import with_statement
from pymt import *
from pyglet.gl import *

picking_buffer = None

class Crayon(MTWidget):

    def __init__(self, **kwargs):
        super(Crayon, self).__init__(**kwargs)
        self.model = OBJ('crayon.obj')
        self.pos = (100,100)

    def on_draw(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)

        self.draw()
        self.draw_picking()
        drawTexturedRectangle(picking_buffer.texture, size=(256,256))


    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScaled(30,30,30)
        glRotated(110, 1,0,0)
        glColor3f(0,1,0)
        self.model.draw()
        glPopMatrix()

    def draw_picking(self):
        with picking_buffer:
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            self.draw()

    def on_touch_move(self, touch):
        self.pos = touch.x, touch.y

if __name__ == '__main__':

    w = MTWindow()
    picking_buffer  = Fbo()
    c = Crayon()
    w.add_widget(c)
    runTouchApp()
