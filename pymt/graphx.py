#!/usr/bin/env python
from pyglet.gl import *
from pyglet.graphics import draw
from math import sqrt


from shader import *


RED = (1.0,0.0,0.0)
GREEN = (0.0,1.0,0.0)
BLUE = (0.0,0.0,1.0)

_brush_texture = None 
_bruch_size = 10



def setBrush(sprite, size=10):
    global _brush_texture
    point_sprite_img = pyglet.image.load(sprite)
    _brush_texture = point_sprite_img.get_texture()
    _bruch_size = size

#paint a line with current brush
def paintLine(points):
    p1 = (points[0], points[1])
    p2 = (points[2], points[3])
    glEnable(GL_BLEND);
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(_brush_texture.target)
    glBindTexture(_brush_texture.target, _brush_texture.id)
    glEnable(GL_POINT_SPRITE_ARB); 
    glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE);
    glPointSize(_bruch_size)
    dx,dy = p2[0]-p1[0], p2[1]-p1[1]
    dist = sqrt(dx*dx +dy*dy)
    numsteps = max(1, int(dist)/4)
    pointList = [0,0] * numsteps
    for i in range(numsteps):
    	pointList[i*2]   = p1[0] + dx* (float(i)/numsteps)
	pointList[i*2+1] = p1[1] + dy* (float(i)/numsteps)
    draw(numsteps,GL_POINTS, ('v2f', pointList))
    glDisable(GL_POINT_SPRITE_ARB);
    glDisable(_brush_texture.target)



def drawCircle(pos=(0,0), radius=1.0):
    x, y = pos[0], pos[1]
    glPushMatrix()
    glTranslated(x,y, 0)
    glScaled(radius, radius,1.0)
    gluDisk(gluNewQuadric(), 0, 1, 32,1)
    glPopMatrix()




def drawTriangle(points, ):
	draw(3, GL_TRIANGLES, ('v2f', points))

def drawTriangle(pos, w, h):

        points = (pos[0]-w/2,pos[1], pos[0]+w/2,pos[1], pos[0],pos[1]+h,)
	draw(3, GL_TRIANGLES, ('v2f', points))

def drawRectangle(pos=(0,0), size=(1.0,1.0), ):
        data = ( pos[0],pos[1],   pos[0]+size[0],pos[1],   pos[0]+size[0],pos[1]+size[1],  pos[0],pos[1]+size[1] )
	draw(4, GL_QUADS, ('v2f', data))


def drawTexturedRectangle(texture, pos=(0,0), size=(1.0,1.0)):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D,texture)
    pos = ( pos[0],pos[1],   pos[0]+size[0],pos[1],   pos[0]+size[0],pos[1]+size[1],  pos[0],pos[1]+size[1] )
    texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
    draw(4, GL_QUADS, ('v2f', pos), ('t2f', texcoords))
    glDisable(GL_TEXTURE_2D)

def drawLine(points, width=5.0, color=(1.0,1.0,1.0)):
	glLineWidth (width)
	draw(2,GL_LINES, ('v2f', points))
	












### FBO, PBO, opengl stuff
class Fbo:
    def __init__(self, size=(1024,1024)):
	print "creating fbo"
	self.framebuffer = c_uint(0)
	self.texture = c_uint(0)
	
	glGenFramebuffersEXT(1,byref(self.framebuffer))
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)

        glGenTextures (1, byref(self.texture))
	glBindTexture (GL_TEXTURE_2D, self.texture)
	glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexImage2D (GL_TEXTURE_2D, 0, GL_RGB, size[0], size[1], 0,GL_RGB, GL_UNSIGNED_BYTE, 0)
	glFramebufferTexture2DEXT (GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self.texture, 0)
	glBindRenderbufferEXT (GL_RENDERBUFFER_EXT, 0)
	glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, 0)
                                
	status = glCheckFramebufferStatusEXT (GL_FRAMEBUFFER_EXT);
	if status != GL_FRAMEBUFFER_COMPLETE_EXT:
	    print "Error in framebuffer activation"
	    
    def bind(self):
	glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
    def release(self):
	glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)













#some 2d vector math...there is probably a good module for this...

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
