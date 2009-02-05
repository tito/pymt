#!/usr/bin/env python
from pyglet import *
from pyglet.gl import *
from pyglet.graphics import draw
from pyglet.text import Label
from math import sqrt
import math
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

def enable_blending():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def disable_blending():
    glDisable(GL_BLEND)


def set_color(r,g,b,a=1.0):
    glColor4f(r,g,b,a)


def drawLabel(text, pos=(0,0),center=True, font_size=16):
    temp_label = Label(text, font_size=font_size, bold=True)
    if center:
        temp_label.anchor_x = 'center'
        temp_label.anchor_y = 'center'
    else:
        temp_label.anchor_x = 'left'
        temp_label.anchor_y = 'bottom'
    temp_label.x = 0
    temp_label.y = 0
    temp_label.text = text
    temp_label.font_size=font_size
    glPushMatrix()
    glTranslated(pos[0], pos[1], 0.0)
    glScaled(0.6,0.6,1)
    temp_label.draw()
    glPopMatrix()
    return temp_label.content_width


#paint a line with current brush
def paintLine(points):
    p1 = (points[0], points[1])
    p2 = (points[2], points[3])
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(_brush_texture.target)
    glBindTexture(_brush_texture.target, _brush_texture.id)
    glEnable(GL_POINT_SPRITE_ARB)
    glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
    glPointSize(_bruch_size)
    dx,dy = p2[0]-p1[0], p2[1]-p1[1]
    dist = sqrt(dx*dx +dy*dy)
    numsteps = max(1, int(dist)/4)
    pointList = [0,0] * numsteps
    for i in range(numsteps):
        pointList[i * 2]   = p1[0] + dx* (float(i)/numsteps)
        pointList[i * 2 + 1] = p1[1] + dy* (float(i)/numsteps)
    draw(numsteps, GL_POINTS, ('v2f', pointList))
    glDisable(GL_POINT_SPRITE_ARB)
    glDisable(_brush_texture.target)


def drawRoundedRectangle(pos=(0,0), size=(100,50), radius=5, color=None,
                         linewidth=1.5, precision=0.5):
    x, y = pos
    w, h = size

    #with smalle values the algorithm draws wierd stuff, so well make the number s bigger and do a glScale to undo

    if color:
        glColor4f(*color)
    glLineWidth(linewidth)

    glBegin(GL_POLYGON)

    glVertex2f(x + radius, y)
    glVertex2f(x + w-radius, y)
    t = math.pi * 1.5
    while t < math.pi * 2:
        sx = x + w - radius + math.cos(t) * radius
        sy = y + radius + math.sin(t) * radius
        glVertex2f(sx, sy)
        t += precision

    glVertex2f(x + w, y + radius)
    glVertex2f(x + w, y + h - radius)
    t = 0
    while t < math.pi * 0.5:
        sx = x + w - radius + math.cos(t) * radius
        sy = y + h -radius + math.sin(t) * radius
        glVertex2f(sx, sy)
        t += precision

    glVertex2f(x + w -radius, y + h)
    glVertex2f(x + radius, y + h)
    t = math.pi * 0.5
    while t < math.pi:
        sx = x  + radius + math.cos(t) * radius
        sy = y + h - radius + math.sin(t) * radius
        glVertex2f(sx, sy)
        t += precision

    glVertex2f(x, y + h - radius)
    glVertex2f(x, y + radius)
    t = math.pi
    while t < math.pi * 1.5:
        sx = x + radius + math.cos(t) * radius
        sy = y + radius + math.sin(t) * radius
        glVertex2f (sx, sy)
        t += precision

    glEnd()


def drawCircle(pos=(0,0), radius=1.0):
    x, y = pos[0], pos[1]
    glPushMatrix()
    glTranslated(x,y, 0)
    glScaled(radius, radius,1.0)
    gluDisk(gluNewQuadric(), 0, 1, 32,1)
    glPopMatrix()

def drawTriangle(points ):
    draw(3, GL_TRIANGLES, ('v2f', points))

def drawTriangle(pos, w, h):
    points = (pos[0]-w/2,pos[1], pos[0]+w/2,pos[1], pos[0],pos[1]+h,)
    draw(3, GL_TRIANGLES, ('v2f', points))

def drawRectangle(pos=(0,0), size=(1.0,1.0), ):
    #data = (pos[0],pos[1], pos[0]+size[0],pos[1], pos[0]+size[0], pos[1]+size[1], pos[0],pos[1]+size[1])
    #draw(4, GL_QUADS, ('v2f', data))
    glBegin(GL_QUADS)
    glVertex2f(pos[0], pos[1])
    glVertex2f(pos[0] + size[0], pos[1])
    glVertex2f(pos[0] + size[0], pos[1] + size[1])
    glVertex2f(pos[0], pos[1] + size[1])
    glEnd()

def drawTexturedRectangle(texture, pos=(0,0), size=(1.0,1.0)):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D,texture)
    pos = ( pos[0],pos[1],   pos[0]+size[0],pos[1],   pos[0]+size[0],pos[1]+size[1],  pos[0],pos[1]+size[1] )
    texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
    draw(4, GL_QUADS, ('v2f', pos), ('t2f', texcoords))
    glDisable(GL_TEXTURE_2D)

def drawLine(points, width=5.0):
    glLineWidth (width)
    draw(2,GL_LINES, ('v2f', points))

### FBO, PBO, opengl stuff
class Fbo:

    fbo_stack = [0]

    def bind(self):
        Fbo.fbo_stack.append(self.framebuffer)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0,0,self.size[0], self.size[1])

    def release(self):
        if self.push_viewport:
            glPopAttrib()
        Fbo.fbo_stack.pop()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, Fbo.fbo_stack[-1])

    def __init__(self, size=(1024,1024), push_viewport=False):
        self.framebuffer    = c_uint(0)
        self.depthbuffer    = c_uint(0)
        self.texture        = c_uint(0)
        self.size           = size

        glGenFramebuffersEXT(1,byref(self.framebuffer))
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)

        glGenRenderbuffersEXT(1, byref(self.depthbuffer));
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self.depthbuffer)
        glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT, size[0], size[1])
        glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, self.depthbuffer)

        glGenTextures(1, byref(self.texture))
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0,GL_RGB, GL_UNSIGNED_BYTE, 0)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self.texture, 0)
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT);
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            print 'Error in framebuffer activation'

        self.push_viewport = push_viewport

    def __del__(self):
        glDeleteFramebuffersEXT(1, byref(self.framebuffer))
        glDeleteRenderbuffersEXT(1, byref(self.depthbuffer))
