'''
Draw: primitive drawing
'''

from __future__ import with_statement

__all__ = [
    'drawLabel', 'drawRoundedRectangle',
    'drawCircle', 'drawPolygon',
    'drawTriangle', 'drawRectangle',
    'drawTexturedRectangle', 'drawLine',
    'drawRectangleAlpha', 'drawRoundedRectangleAlpha',
]

from pyglet import *
from pyglet.gl import *
from pyglet.image import Texture, TextureRegion
from pyglet.graphics import draw
from pyglet.text import Label
from paint import *
from statement import *
from colors import *
import math

def drawLabel(label, pos=(0,0), **kwargs):
    '''Draw a label on the window.

    :Parameters:
        `label` : str
            Text to be draw
        `pos` : tuple, default to (0, 0)
            Position of text
        `font_size` : int, default to 16
            Font size of label
        `center` : bool, default to True
            Indicate if pos is center or left-right of label

    .. Warning:
        Use only for debugging, it's a performance killer function.
        The label is recreated each time the function is called !
    '''
    kwargs.setdefault('font_size', 16)
    kwargs.setdefault('center', True)
    if kwargs.get('center'):
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
    else:
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
    del kwargs['center']
    temp_label = Label(label, **kwargs)
    temp_label.x, temp_label.y = pos
    temp_label.draw()
    return temp_label.content_width

def drawRoundedRectangle(pos=(0,0), size=(100,50), radius=5, color=None,
                         linewidth=1.5, precision=0.5, style=GL_POLYGON):
    '''Draw a rounded rectangle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (100, 50)
            Size of rectangle
        `radius` : int, default to 5
            Radius of corner
        `color` : tuple, default to None
            Color to be passed to set_color()
        `linewidth` : float, default to 1.5
            Line with of border
        `precision` : float, default to 0.5
            Precision of corner angle
        `style` : opengl begin, default to GL_POLYGON
            Style of the rounded rectangle (try GL_LINE_LOOP)
    '''
    x, y = pos
    w, h = size

    if size[0] < radius * 2:
        radius = size[0] / 2
    if size[1] < radius * 2:
        radius = size[1] / 2

    if color:
        set_color(*color)

    with gx_begin(style):

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

def drawCircle(pos=(0,0), radius=1.0):
    '''Draw a simple circle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of circle
        `radius` : float, default to 1.0
            Radius of circle
    '''
    x, y = pos[0], pos[1]
    with gx_matrix:
        glTranslated(x, y, 0)
        glScaled(radius, radius, 1.0)
        gluDisk(gluNewQuadric(), 0, 1, 32,1)

def drawPolygon(points, style=GL_TRIANGLES):
    '''Draw polygon from points list

    :Parameters:
        `points` : list
            List of points, length must be power of 2. (x,y,x,y...)
        `style` : opengl begin, default to GL_TRIANGLES
            Default type to draw (will be passed to glBegin)
    '''
    points = list(points)
    with gx_begin(style):
        while len(points):
            y, x = points.pop(), points.pop()
            glVertex2f(x, y)

def drawTriangle(pos, w, h, style=GL_TRIANGLES):
    '''Draw one triangle

    :Parameters:
        `pos` : tuple
            Position of triangle
        `w` : int
            Width of triangle
        `h` : int
            Height of triangle
    '''
    points = [pos[0]-w/2, pos[1], pos[0]+w/2, pos[1], pos[0], pos[1]+h]
    drawPolygon(points)

def drawRectangle(pos=(0,0), size=(1.0,1.0), style=GL_QUADS):
    '''Draw a simple rectangle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (1.0, 1.0)
            Size of rectangle
        `style` : opengl begin, default to GL_QUADS
            Style of rectangle (try GL_LINE_LOOP)
    '''
    with gx_begin(style):
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[0] + size[0], pos[1])
        glVertex2f(pos[0] + size[0], pos[1] + size[1])
        glVertex2f(pos[0], pos[1] + size[1])

def drawTexturedRectangle(texture, pos=(0,0), size=(1.0,1.0), tex_coords=None):
    '''Draw a rectangle with a texture

    :Parameters:
        `texture` : int
            OpenGL id of texture
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (1.0, 1.0)
            Size of rectangle
    '''
    with gx_enable(GL_TEXTURE_2D):
        set_texture(texture, target=GL_TEXTURE_2D)
        if type(texture) in (Texture, TextureRegion):
            t = texture.tex_coords
            texcoords = (t[0], t[1], t[3], t[4], t[6], t[7], t[9], t[10])
        else:
            texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
        if tex_coords:
            texcoords = tex_coords
        pos = ( pos[0], pos[1],
                pos[0] + size[0], pos[1],
                pos[0] + size[0], pos[1] + size[1],
                pos[0], pos[1] + size[1])
        draw(4, GL_QUADS, ('v2f', pos), ('t2f', texcoords))

def drawLine(points, width=None):
    '''Draw a line

    :Parameters:
        `points` : list
            List of point to draw, len must be power of 2
        `widget` : float, default to 5.0
            Default width of line
    '''
    style = GL_LINES
    if width is not None:
        glPushAttrib(GL_LINE_BIT)
        glLineWidth(width)

    points = list(points)
    l = len(points)
    if l < 4:
        return
    if l > 4:
        style = GL_LINE_STRIP
    with gx_begin(GL_LINE_STRIP):
        while len(points):
            glVertex2f(points.pop(0), points.pop(0))

    if width is not None:
        glPopAttrib()

def drawRoundedRectangleAlpha(pos=(0,0), size=(100,50), radius=5, alpha=(1,1,1,1),
                         linewidth=1.5, precision=0.5, style=GL_TRIANGLE_FAN):
    '''Draw a rounded rectangle alpha layer.

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (100, 50)
            Size of rectangle
        `radius` : int, default to 5
            Radius of corner
        `alpha` : list, default to (1, 1, 1, 1)
            Alpha to set in each corner (top, right, bottom, left)
        `linewidth` : float, default to 1.5
            Line with of border
        `precision` : float, default to 0.5
            Precision of corner angle
        `style` : opengl begin, default to GL_POLYGON
            Style of the rounded rectangle (try GL_LINE_LOOP)
    '''
    x, y = pos
    w, h = size

    if size[0] < radius * 2:
        radius = size[0] / 2
    if size[1] < radius * 2:
        radius = size[1] / 2

    midalpha = 0
    for a in alpha:
        midalpha += a
    midalpha /= len(alpha)

    c0 = (1,1,1,midalpha)
    c1 = (1,1,1,alpha[0]) #topleft
    c2 = (1,1,1,alpha[2]) #bottomleft
    c3 = (1,1,1,alpha[1]) #topright
    c4 = (1,1,1,alpha[3]) #bottomright

    with DO(gx_alphablending, gx_begin(style)):

        glColor4f(*c0)
        glVertex2f(x + w/2, y + h/2)
        glColor4f(*c1)
        glVertex2f(x + radius, y)
        glColor4f(*c3)
        glVertex2f(x + w-radius, y)
        t = math.pi * 1.5
        while t < math.pi * 2:
            sx = x + w - radius + math.cos(t) * radius
            sy = y + radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x + w, y + radius)
        glColor4f(*c4)
        glVertex2f(x + w, y + h - radius)
        t = 0
        while t < math.pi * 0.5:
            sx = x + w - radius + math.cos(t) * radius
            sy = y + h -radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x + w -radius, y + h)
        glColor4f(*c2)
        glVertex2f(x + radius, y + h)
        t = math.pi * 0.5
        while t < math.pi:
            sx = x  + radius + math.cos(t) * radius
            sy = y + h - radius + math.sin(t) * radius
            glVertex2f(sx, sy)
            t += precision

        glVertex2f(x, y + h - radius)
        glColor4f(*c1)
        glVertex2f(x, y + radius)
        t = math.pi
        while t < math.pi * 1.5:
            sx = x + radius + math.cos(t) * radius
            sy = y + radius + math.sin(t) * radius
            glVertex2f (sx, sy)
            t += precision
        glVertex2f(x + radius, y)

def drawRectangleAlpha(pos=(0,0), size=(1.0,1.0), alpha=(1,1,1,1), style=GL_QUADS):
    '''Draw an rectangle alpha layer.

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (1.0, 1.0)
            Size of rectangle
        `alpha` : list, default to (1, 1, 1, 1)
            Alpha to set in each corner (top, right, bottom, left)
        `style` : opengl begin, default to GL_QUADS
            Style of rectangle (try GL_LINE_LOOP)
    '''
    with DO(gx_alphablending, gx_begin(style)):
        glColor4f(1, 1, 1, alpha[0])
        glVertex2f(pos[0], pos[1])
        glColor4f(1, 1, 1, alpha[1])
        glVertex2f(pos[0] + size[0], pos[1])
        glColor4f(1, 1, 1, alpha[2])
        glVertex2f(pos[0] + size[0], pos[1] + size[1])
        glColor4f(1, 1, 1, alpha[3])
        glVertex2f(pos[0], pos[1] + size[1])

