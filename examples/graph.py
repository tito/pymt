from random import randint
from pyglet.gl import *


def drawLine(points):
       p1, p2 = points[0], points[1]
       glLineWidth (10.0)
       glColor3f(1.0,1.0,1.0)
       glBegin(GL_LINES)
       glVertex2f( p1.x, p1.y )
       glVertex2f( p2.x, p2.y )
       glEnd()
       glLineWidth (1.0)


def drawVertex(x,y):
       glPushMatrix()
       glTranslated(x,y, 0)
       glColor3d(1.0,1.0,1.0)
       gluDisk(gluNewQuadric(), 0, 20, 32,1)
       glScaled(0.75,0.75,1.0)
       glColor3d(0.0,0.0,1.0)
       gluDisk(gluNewQuadric(), 0, 20, 32,1)
       glPopMatrix()

class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

class Graph(object):
       def __init__(self, num_verts=12, displaySize=(640,480)):
              self.verts = []
              for i in range(num_verts):
                     x = randint(100,displaySize[0]-100)
                     y = randint(100,displaySize[1]-100)
                     self.verts.append(Point(x,y))
              
              self.edges = [ [self.verts[i], self.verts[(i+1)%num_verts]] for i in range(num_verts) ]
     
       def draw(self):
              for e in self.edges:
                     drawLine(e)
              for v in self.verts:
                     drawVertex(v.x,v.y)
                     
       #returns the vertex at the position, None if no vertex there
       def collideVerts(self, x,y, regionSize=35):
              for v in self.verts:
                     dx = abs(x - v.x)
                     dy = abs(y - v.y)
                     #print x, y, v.x, v.y
                     if (dx < regionSize and dy < regionSize):
                            return v
              return None


if __name__ == "__main__":
	print "this is an implementation file only used by untabgle.py"
