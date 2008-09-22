#!/usr/bin/env python
from pyglet.gl import *


def drawCircle(pos=(0,0), color=(1.0,1.0,1.0)):
    x, y = pos
    glPushMatrix()
    glTranslated(x,y, 0)
    glColor3d(*color)
    gluDisk(gluNewQuadric(), 0, 10, 32,1)
    glPopMatrix()

def drawLine(points, color=(1.0,1.0,1.0)):
       p1, p2 = points[0], points[1]
       glLineWidth (20.0)
       if (color):
	       glColor3f(*color)
       glBegin(GL_LINES)
       glVertex2f( p1[0], p1[1] )
       glVertex2f( p2[0], p2[1] )
       glEnd()
       glLineWidth (1.0)