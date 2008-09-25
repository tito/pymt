#!/usr/bin/env python
from pyglet.gl import *
from pyglet.graphics import draw

def drawCircle(pos=(0,0), color=(1.0,1.0,1.0)):
    x, y = pos
    glPushMatrix()
    glTranslated(x,y, 0)
    glColor3d(*color)
    gluDisk(gluNewQuadric(), 0, 10, 32,1)
    glPopMatrix()



def drawTriangle(points, color=(1.0,1.0,1.0)):
	pass
	draw(3, GL_TRIANGLES, ('v2f', points))


def drawRectangle(points, color=(1.0,1.0,1.0)):
	draw(4, GL_QUADS, ('v2f', points))


def drawLine(points, width=5.0, color=(1.0,1.0,1.0)):
	glLineWidth (width)
	if (color):
		glColor3f(*color)
	draw(2,GL_LINES, ('v2f', points))
	