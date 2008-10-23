#!/usr/bin/env python
from pyglet.gl import *
from pyglet.graphics import draw

RED = (1.0,0.0,0.0)
GREEN = (0.0,1.0,0.0)
BLUE = (0.0,0.0,1.0)

def drawCircle(pos=(0,0), color=(1.0,1.0,1.0), radius=1.0):
    if (color):
        if (len(color)==3):glColor3f(*color)
        elif (len(color)==4): glColor4f(*color)
    x, y = pos[0], pos[1]
    glPushMatrix()
    glTranslated(x,y, 0)
    glScaled(radius, radius,1.0)
    gluDisk(gluNewQuadric(), 0, 1, 32,1)
    glPopMatrix()


def drawTriangle(points, color=(1.0,1.0,1.0)):
	if (color):
            if (len(color)==3):glColor3f(*color)
            elif (len(color)==4): glColor4f(*color)
	draw(3, GL_TRIANGLES, ('v2f', points))

def drawTriangle(pos, w, h, color=(1.0,1.0,1.0)):
	if (color):
            if (len(color)==3):glColor3f(*color)
            elif (len(color)==4): glColor4f(*color)
        points = (pos[0]-w/2,pos[1], pos[0]+w/2,pos[1], pos[0],pos[1]+h,)
	draw(3, GL_TRIANGLES, ('v2f', points))

def drawRectangle(pos=(0,0), size=(1.0,1.0), color=(1.0,1.0,1.0)):
	if (color):
            if (len(color)==3):glColor3f(*color)
            elif (len(color)==4): glColor4f(*color)
        data = ( pos[0],pos[1],   pos[0]+size[0],pos[1],   pos[0]+size[0],pos[1]+size[1],  pos[0],pos[1]+size[1] )
	draw(4, GL_QUADS, ('v2f', data))


def drawLine(points, width=5.0, color=(1.0,1.0,1.0)):
	glLineWidth (width)
	if (color):
            if (len(color)==3):glColor3f(*color)
            elif (len(color)==4): glColor4f(*color)
	draw(2,GL_LINES, ('v2f', points))
	
        
import math
class Vector:
    'Represents a 2D vector.'
    def __init__(self, x = 0, y = 0):
        self.x = float(x)
        self.y = float(y)
        
    def __add__(self, val):
        return Point( self[0] + val[0], self[1] + val[1] )
    
    def __sub__(self,val):
        return Point( self[0] - val[0], self[1] - val[1] )
    
    def __iadd__(self, val):
        self.x = val[0] + self.x
        self.y = val[1] + self.y
        return self
        
    def __isub__(self, val):
        self.x = self.x - val[0]
        self.y = self.y - val[1]
        return self
    
    def __div__(self, val):
        return Point( self[0] / val, self[1] / val )
    
    def __mul__(self, val):
        return Point( self[0] * val, self[1] * val )
    
    def __idiv__(self, val):
        self[0] = self[0] / val
        self[1] = self[1] / val
        return self
        
    def __imul__(self, val):
        self[0] = self[0] * val
        self[1] = self[1] * val
        return self
                
    def __getitem__(self, key):
        if( key == 0):
            return self.x
        elif( key == 1):
            return self.y
        else:
            raise Exception("Invalid key to Point")
        
    def __setitem__(self, key, value):
        if( key == 0):
            self.x = value
        elif( key == 1):
            self.y = value
        else:
            raise Exception("Invalid key to Point")
        
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
Point = Vector
        
def DistanceSqrd( point1, point2 ):
    'Returns the distance between two points squared. Marginally faster than Distance()'
    return ( (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
def Distance( point1, point2 ):
    'Returns the distance between two points'
    return math.sqrt( DistanceSqrd(point1,point2) )
def LengthSqrd( vec ):
    'Returns the length of a vector sqaured. Faster than Length(), but only marginally'
    return vec[0]**2 + vec[1]**2
def Length( vec ):
    'Returns the length of a vector'
    return math.sqrt( LengthSqrd(vec) )
def Normalize( vec ):
    'Returns a new vector that has the same direction as vec, but has a length of one.'
    if( vec[0] == 0. and vec[1] == 0. ):
        return Vector(0.,0.)
    return vec / Length(vec)
def Dot( a,b ):
    'Computes the dot product of a and b'
    return a[0]*b[0] + a[1]*b[1]
