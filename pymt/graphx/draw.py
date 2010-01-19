'''
Draw: primitive drawing
'''



__all__ = (
    'drawLabel', 'drawRoundedRectangle',
    'drawCircle', 'drawPolygon',
    'drawTriangle', 'drawRectangle',
    'drawTexturedRectangle', 'drawLine',
    'drawRectangleAlpha', 'drawRoundedRectangleAlpha',
    'drawSemiCircle', 'drawStippledCircle',
    'getLastLabel', 'getLabel',
)

import os
import math
import pymt
from pymt.cache import Cache
from OpenGL.GL import *
from OpenGL.GLU import gluNewQuadric, gluDisk, gluPartialDisk
from paint import *
from statement import *
from colors import *

# create a cache for label
_temp_label = None
if not 'PYMT_DOC' in os.environ:
    Cache.register('drawlabel', timeout=1., limit=100)

def getLabel(label, **kwargs):
    '''Get a cached label object

    :Parameters:
        `label` : str
            Text to be draw
        `font_size` : int, default to 12
            Font size of label
        `center` : bool, default to True
            Indicate if pos is center or left-right of label

    Used by drawLabel()
    '''
    kwargs.setdefault('font_size', 12)
    kwargs.setdefault('center', True)
    if kwargs.get('center'):
        kwargs.setdefault('anchor_x', 'center')
        kwargs.setdefault('anchor_y', 'center')
    else:
        kwargs.setdefault('anchor_x', 'left')
        kwargs.setdefault('anchor_y', 'bottom')
    del kwargs['center']

    # create an uniq id for this label
    id = '%s##%s' % (label, str(kwargs))

    # get or store
    obj = pymt.Cache.get('drawlabel', id)
    if not obj:
        obj = pymt.Label(label, **kwargs)
        pymt.Cache.append('drawlabel', id, obj)

    return obj

def drawLabel(label, pos=(0,0), **kwargs):
    '''Draw a label on the window.

    :Parameters:
        `label` : str
            Text to be draw
        `pos` : tuple, default to (0, 0)
            Position of text
        `font_size` : int, default to 12
            Font size of label
        `center` : bool, default to True
            Indicate if pos is center or left-right of label

    If you want to get the label object, use getLastLabel() just after your
    drawLabel().
    '''
    global _temp_label
    _temp_label = getLabel(label, **kwargs)
    _temp_label.x, _temp_label.y = pos
    _temp_label.draw()
    return _temp_label.content_size

def getLastLabel():
    global _temp_label
    return _temp_label

def drawRoundedRectangle(pos=(0,0), size=(100,50), radius=5, color=None,
                         linewidth=None, precision=0.5, style=GL_POLYGON):
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

    if linewidth is not None:
        glPushAttrib(GL_LINE_BIT)
        glLineWidth(linewidth)

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

    if linewidth is not None:
        glPopAttrib()


def drawCircle(pos=(0,0), radius=1.0, linewidth=None):
    '''Draw a simple circle

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Position of circle
        `radius` : float, default to 1.0
            Radius of circle
    '''
    x, y = pos[0], pos[1]
    with gx_matrix:
        glTranslatef(x, y, 0)
        glScalef(radius, radius, 1.0)
        if linewidth:
            gluDisk(gluNewQuadric(), 1-linewidth/float(radius), 1, 32,1)
        else:
            gluDisk(gluNewQuadric(), 0, 1, 32,1)

def drawPolygon(points, style=GL_POLYGON):
    '''Draw polygon from points list

    :Parameters:
        `points` : list
            List of points, length must be power of 2. (x,y,x,y...)
        `style` : opengl begin, default to GL_POLYGON
            Default type to draw (will be passed to glBegin)
    '''
    points = list(points)
    with gx_begin(style):
        for x, y in zip(points[::2], points[1::2]):
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

def drawTexturedRectangle(texture, pos=(0,0), size=(1.0,1.0),
                          tex_coords=None, color_coords=None):
    '''Draw a rectangle with a texture.
    The rectangle is drawed from bottom-left, bottom-right, top-right, top-left.

    :Parameters:
        `texture` : Texture
            Texture object, created with Texture().
        `pos` : tuple, default to (0, 0)
            Position of rectangle
        `size` : tuple, default to (1.0, 1.0)
            Size of rectangle
        `tex_coords` : list, default to None
            Contain a list of UV coords to use. If None, texture UV coordinates
            will be used.
        `color_coords` : list, default to None
            Specify a color for each vertex. The format is 4 colors tuples in a
            list.
    '''
    # initialize texcoords
    texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)

    # if texture is provided, use it
    if texture:
        stmt = gx_texture(texture)
        stmt.bind()
        if type(texture) in (pymt.Texture, pymt.TextureRegion):
            texcoords = texture.tex_coords

    # if tex_coords is provided, use it
    if tex_coords:
        texcoords = tex_coords

    pos = ( pos[0], pos[1],
            pos[0] + size[0], pos[1],
            pos[0] + size[0], pos[1] + size[1],
            pos[0], pos[1] + size[1])

    if color_coords:
        with gx_begin(GL_QUADS):
            glColor4f(*color_coords[0])
            glTexCoord2f(texcoords[0], texcoords[1])
            glVertex2f(pos[0], pos[1])
            glColor4f(*color_coords[1])
            glTexCoord2f(texcoords[2], texcoords[3])
            glVertex2f(pos[2], pos[3])
            glColor4f(*color_coords[2])
            glTexCoord2f(texcoords[4], texcoords[5])
            glVertex2f(pos[4], pos[5])
            glColor4f(*color_coords[3])
            glTexCoord2f(texcoords[6], texcoords[7])
            glVertex2f(pos[6], pos[7])
    else:
        with gx_begin(GL_QUADS):
            glTexCoord2f(texcoords[0], texcoords[1])
            glVertex2f(pos[0], pos[1])
            glTexCoord2f(texcoords[2], texcoords[3])
            glVertex2f(pos[2], pos[3])
            glTexCoord2f(texcoords[4], texcoords[5])
            glVertex2f(pos[4], pos[5])
            glTexCoord2f(texcoords[6], texcoords[7])
            glVertex2f(pos[6], pos[7])

    # release texture
    if texture:
        stmt.release()

def drawLine(points, width=None, colors=[]):
    '''Draw a line

    :Parameters:
        `points` : list
            List of corresponding coordinates representing the points that the
            line comprises, like [x1, y1, x2, y2]. Hence, len(points) must be
            a power of 2.
        `width` : float, defaults to 5.0
            Default width of line
        `colors` : list of tuples, defaults to []
            If you want to draw colors between the points of the line, this
            list has to be populated with a tuple for each point representing
            that point's color. Hence, len(colors) == len(points) / 2 holds.
            Turned off by default.
    '''
    style = GL_LINES
    points = list(points)
    l = len(points)
    if l < 4:
        return
    elif l > 4:
        style = GL_LINE_STRIP

    if width is not None:
        glPushAttrib(GL_LINE_BIT)
        glLineWidth(width)

    with DO(gx_attrib(GL_COLOR_BUFFER_BIT), gx_begin(style)):
        if colors:
            colors = colors[:]
            for x, y, r, g, b in zip(points[::2], points[1::2],
                                     colors[::3], colors[1::3], colors[2::3]):
                glColor3f(r, g, b)
                glVertex2f(x, y)
        else:
            for x, y in zip(points[::2], points[1::2]):
                glVertex2f(x, y)

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

def drawSemiCircle(pos=(0,0), inner_radius=100, outer_radius=120, slices=32, loops=1, start_angle=0, sweep_angle=360):
    '''Draw a semi-circle. You can choose the start angle,
    and the ending angle (from 0 to 360), and the inner/outer radius !

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Center position of the circle
        `inner_radius` : int, default to 100
            Radius of the inner circle
        `outer_radius` : int, default to 120
            Radius of the outer circle
        `slices` : int, default to 32
            Precision of circle drawing
        `start_angle` : int, default to 0
            Angle to start drawing
        `sweep_angle` : int, default to 360
            Angle to finish drawing
    '''
    with gx_matrix:
        glTranslatef(pos[0], pos[1], 0)
        gluPartialDisk(gluNewQuadric(), inner_radius, outer_radius, slices, loops, start_angle, sweep_angle)

def drawStippledCircle(pos=(0,0), inner_radius=200, outer_radius=400, segments=10):
    '''
    Draw a stippled circle. A stippled circle consists of several equally-sized
    segments, with a gap between every two segments. The gap is the size of a
    segment. The circle's position and thickness can be specified.

    :Parameters:
        `pos` : tuple, default to (0, 0)
            Center position of the circle
        `inner_radius` : int, default to 100
            Radius of the inner circle
        `outer_radius` : int, default to 120
            Radius of the outer circle
        `segments` : int, defaults to 10
            Number of visible segments
    '''
    angle_delta = (360/segments)/2
    current_angle = 0
    quadric = gluNewQuadric()
    with gx_matrix:
        glTranslatef(pos[0], pos[1], 0)
        for i in range(segments):
            next_angle = current_angle + angle_delta
            gluPartialDisk(quadric, inner_radius, outer_radius, 32, 1, current_angle, angle_delta)
            # For the stipple effect, leave a part of the Disk out
            current_angle = next_angle + angle_delta
