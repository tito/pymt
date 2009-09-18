import pymtcore
from OpenGL.GL import *

class MyWidget(pymtcore.MTWidget):
    def draw(self):
        glBegin(GL_QUADS)
        glColor3f(1., 0., 0.)
        glVertex2f(self.x, self.y)
        glColor3f(0., 1., 0.)
        glVertex2f(self.x + self.width, self.y)
        glColor3f(0., 0., 1.)
        glVertex2f(self.x + self.width, self.y + self.height)
        glColor3f(1., 0., 1.)
        glVertex2f(self.x, self.y + self.height)
        glEnd()

w = pymtcore.MTCoreWindow()
w.size = 640, 480
w.setup()
w.add_widget(MyWidget())

while True:
    w.on_update()
    w.on_draw()
