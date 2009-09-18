import pymtcore
from OpenGL.GL import *

class MyWidget(pymtcore.MTWidget):
    def draw(self):
        glPushMatrix(GL_MODELVIEW)
        glTranslatef(self.x, self.y, 0)
        glBegin(GL_POLYGON)
        glColor(1, 0, 0)
        glVertex2f(self.x, self.y, 0)
        glColor(0, 1, 0)
        glVertex2f(self.x + self.width, self.y, 0)
        glColor(0, 0, 1)
        glVertex2f(self.x + self.width, self.y + self.height, 0)
        glColor(1, 0, 1)
        glVertex2f(self.x, self.y + self.height, 0)
        glEnd()
        glPopMatrix(GL_MODELVIEW)

w = pymtcore.MTCoreWindow()
w.size = 640, 480
w.setup()
w.add_widget(MyWidget())

while True:
    w.on_update()
    w.on_draw()
