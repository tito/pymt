'''
Graphx: simplification of opengl pritimives
'''

from __future__ import with_statement

__all__ = [
    # settings
    'set_brush', 'set_brush_size', 'set_color',
    'set_texture',
    # draw
    'paintLine',
    'drawLabel', 'drawRoundedRectangle',
    'drawCircle', 'drawPolygon',
    'drawTriangle', 'drawRectangle',
    'drawTexturedRectangle', 'drawLine',
    # class for with statement
    'DO',
    'GlDisplayList', 'GlBlending',
    'GlMatrix', 'GlEnable', 'GlBegin',
    # aliases
    'gx_blending',
    'gx_matrix', 'gx_matrix_identity',
    'gx_enable', 'gx_begin',
    # Fbo
    'Fbo', 'HardwareFbo', 'SoftwareFbo'
]

from pyglet import *
from pyglet.gl import *
from pyglet.image import Texture, TextureRegion
from pyglet.graphics import draw
from pyglet.text import Label
from logger import pymt_logger
import math

RED = (1.0,0.0,0.0)
GREEN = (0.0,1.0,0.0)
BLUE = (0.0,0.0,1.0)

_brush_filename = ''
_brush_texture = None
_brush_size = 10

def set_brush(sprite, size=None):
    '''Define the brush to use for paint* functions

    :Parameters:
        `sprite` : string
            Filename of image brush
        `size` : int, default to None
            Size of brush
    '''
    global _brush_filename, _brush_size, _brush_texture
    if size:
        _brush_size = size
    if sprite == _brush_filename:
        return
    point_sprite_img = pyglet.image.load(sprite)
    _brush_texture = point_sprite_img.get_texture()


def set_brush_size(size):
    '''Define the size of current brush

    :Parameters:
        `size` : int
            Size of brush
    '''
    global _brush_size
    _brush_size = size


def set_color(*colors, **kwargs):
    '''Define current color to be used ::

        set_color(1, 0, 0, 1)
        drawLabel('Hello', pos=(100, 0))
        set_color(0, 1, 0, 1)
        drawLabel('World', pos=(200, 0))

    .. Note:
        Blending is activated if alpha value != 1

    :Parameters:
        `*colors` : list
            Can have 3 or 4 float value (between 0 and 1)
        `sfactor` : opengl factor, default to GL_SRC_ALPHA
            Default source factor to be used if blending is activated
        `dfactor` : opengl factor, default to GL_ONE_MINUS_SRC_ALPHA
            Default destination factor to be used if blending is activated
    '''

    kwargs.setdefault('sfactor', GL_SRC_ALPHA)
    kwargs.setdefault('dfactor', GL_ONE_MINUS_SRC_ALPHA)
    if len(colors) == 4:
        glColor4f(*colors)
        if colors[3] == 1:
            glDisable(GL_BLEND)
        else:
            glEnable(GL_BLEND)
            glBlendFunc(kwargs.get('sfactor'), kwargs.get('dfactor'))
    if len(colors) == 3:
        glColor3f(*colors)
        glDisable(GL_BLEND)

def set_texture(texture, target=None):
    '''Same as glBindTexture, except he can take integer/long or
    Texture/TextureRegion'''
    if type(texture) in (Texture, TextureRegion):
        glBindTexture(target, texture.id)
    else:
        glBindTexture(target, texture)

def drawLabel(text, pos=(0,0), center=True, font_size=16):
    '''Draw a label on the window.

    :Parameters:
        `text` : str
            Text to be draw
        `pos` : tuple, default to (0, 0)
            Position of text
        `font_size` : int, default to 16
            Font size of label
    
    .. Warning:
        Use only for debugging, it's a performance killer function.
        The label is recreated each time the function is called !
    '''
    temp_label = Label(text, font_size=font_size, bold=True)
    if center:
        temp_label.anchor_x = 'center'
        temp_label.anchor_y = 'center'
    else:
        temp_label.anchor_x = 'left'
        temp_label.anchor_y = 'bottom'
    temp_label.x = 0
    temp_label.y = 0
    with gx_matrix:
        glTranslated(pos[0], pos[1], 0.0)
        glScaled(0.6,0.6,1)
        temp_label.draw()
    return temp_label.content_width


def paintLine(points):
    '''Paint a line with current brush
    ::

        set_brush("mybrush.png", 10)
        paintLine(0, 0, 20, 50)

    '''
    global _brush_texture, _brush_size
    if not _brush_texture:
        pymt_logger.warning('No brush set to paint line, abort')
        return
    p1 = (points[0], points[1])
    p2 = (points[2], points[3])
    with DO(gx_blending, gx_enable(GL_POINT_SPRITE_ARB), gx_enable(_brush_texture.target)):
        glBindTexture(_brush_texture.target, _brush_texture.id)
        glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
        glPointSize(_brush_size)
        dx,dy = p2[0]-p1[0], p2[1]-p1[1]
        dist = math.sqrt(dx*dx +dy*dy)
        numsteps = max(1, int(dist)/4)
        pointList = [0,0] * numsteps
        for i in range(numsteps):
            pointList[i * 2]   = p1[0] + dx* (float(i)/numsteps)
            pointList[i * 2 + 1] = p1[1] + dy* (float(i)/numsteps)
        draw(numsteps, GL_POINTS, ('v2f', pointList))


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

    if color:
        set_color(*color)
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
        glTranslated(x,y, 0)
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
            glVertex2f(points.pop(), points.pop())

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

def drawTexturedRectangle(texture, pos=(0,0), size=(1.0,1.0)):
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
        if type(texture) in (Texture, TextureRegion):
            glBindTexture(GL_TEXTURE_2D, texture.id)
            t = texture.tex_coords
            texcoords = (t[0], t[1], t[3], t[4], t[6], t[7], t[9], t[10])
        else:
            glBindTexture(GL_TEXTURE_2D, texture)
            texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
        pos = ( pos[0], pos[1],
                pos[0] + size[0], pos[1],
                pos[0] + size[0], pos[1] + size[1],
                pos[0], pos[1] + size[1])
        draw(4, GL_QUADS, ('v2f', pos), ('t2f', texcoords))

def drawLine(points, width=5.0):
    '''Draw a line
    
    :Parameters:
        `points` : list
            List of point to draw, len must be power of 2
        `widget` : float, default to 5.0
            Default width of line
    '''
    glLineWidth(width)
    points = list(points)
    with gx_begin(GL_LINES):
        while len(points):
            glVertex2f(points.pop(0), points.pop(0))

gl_displaylist_generate = False
class GlDisplayList:
    '''Abstraction to opengl display-list usage. Here is an example of usage
    ::

        dl = GlDisplayList()
        with dl:
            # do draw function, like drawLabel etc...
        dl.draw()
    '''
    def __init__(self):
        self.dl = glGenLists(1)
        self.compiled = False
        self.do_compile = True

    def __enter__(self):
        global gl_displaylist_generate
        if gl_displaylist_generate:
            self.do_compile = False
        else:
            gl_displaylist_generate = True
            self.do_compile = True
            glNewList(self.dl, GL_COMPILE)

    def __exit__(self, type, value, traceback):
        global gl_displaylist_generate
        if self.do_compile:
            glEndList()
            self.compiled = True
            gl_displaylist_generate = False

    def clear(self):
        self.compiled = False

    def is_compiled(self):
        return self.compiled

    def draw(self):
        if not self.compiled:
            return
        glCallList(self.dl)

class DO:
    '''A way to do multiple action in with statement
    ::

        with DO(stmt1, stmt2):
            print 'something'

    '''
    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        for item in self.args:
            item.__enter__()

    def __exit__(self, type, value, traceback):
        for item in self.args:
            item.__exit__(type, value, traceback)


class GlBlending:
    '''Abstraction to use blending ! Don't use directly this class.
    We've got an alias you can use ::

        with gx_blending:
            # do draw function
    '''
    def __enter__(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def __exit__(self, type, value, traceback):
        glDisable(GL_BLEND)

gx_blending = GlBlending()


class GlMatrix:
    '''Statement of glPushMatrix/glPopMatrix, designed to be use with "with" keyword.

    Alias: gx_matrix, gx_matrix_identity ::

        with gx_matrix:
            # do draw function

        with gx_matrix_identity:
            # do draw function
    '''
    def __init__(self, matrixmode=GL_MODELVIEW, do_loadidentity=False):
        self.do_loadidentity = do_loadidentity
        self.matrixmode = matrixmode

    def __enter__(self):
        glMatrixMode(self.matrixmode)
        glPushMatrix()
        if self.do_loadidentity:
            glLoadIdentity()

    def __exit__(self, type, value, traceback):
        glPopMatrix()

gx_matrix = GlMatrix()
gx_matrix_identity = GlMatrix(do_loadidentity=True)

class GlEnable:
    '''Statement of glEnable/glDisable, designed to be use with "with" keyword.

    Alias: gx_enable.
    '''
    def __init__(self, flag):
        self.flag = flag

    def __enter__(self):
        glEnable(self.flag)

    def __exit__(self, type, value, traceback):
        glDisable(self.flag)

gx_enable = GlEnable

class GlBegin:
    '''Statement of glBegin/glEnd, designed to be use with "with" keyword

    Alias: gx_begin.
    '''
    def __init__(self, flag):
        self.flag = flag

    def __enter__(self):
        glBegin(self.flag)

    def __exit__(self, type, value, traceback):
        glEnd()

gx_begin = GlBegin

### FBO, PBO, opengl stuff
class AbstractFbo(object):
    '''Abstraction of Framebuffer implementation.
    It's a framebuffer you can use to draw temporary things,
    and use it as a texture.

    .. note::
        You cannot use this class, use Fbo alias.

    .. warning::
        Depend of implementation, texture can be a TextureRegion, or a long.

    :Parameters:
        `size` : tuple, default to (1024, 1024)
            Size of FBO
        `push_viewport` : bool, default to False
            Indicate if viewport must be pushed
        `with_depthbuffer` : bool, default to True
            Indicate if depthbuffer must be applied
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (1024, 1024))
        kwargs.setdefault('push_viewport', False)
        kwargs.setdefault('with_depthbuffer', True)
        self.size               = kwargs.get('size')
        self.with_depthbuffer   = kwargs.get('with_depthbuffer')
        self.push_viewport      = kwargs.get('push_viewport')

    def bind(self):
        pass

    def release(self):
        pass

    def __enter__(self):
        self.bind()

    def __exit__(self, type, value, traceback):
        self.release()


class HardwareFbo(AbstractFbo):
    '''OpenGL Framebuffer, hardware implementation.

    .. warning::
        It's not supported by all hardware, use with care !

    '''
    fbo_stack = [0]

    def __init__(self, **kwargs):
        super(HardwareFbo, self).__init__(**kwargs)
        self.framebuffer    = c_uint(0)
        self.depthbuffer    = c_uint(0)
        self.texture        = c_uint(0)

        glGenFramebuffersEXT(1, byref(self.framebuffer))
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.framebuffer.value == 0:
            raise 'Failed to initialize framebuffer'

        if self.with_depthbuffer:
            glGenRenderbuffersEXT(1, byref(self.depthbuffer));
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self.depthbuffer)
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT,
                                     self.size[0], self.size[1])
            glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, self.depthbuffer)

        glGenTextures(1, byref(self.texture))
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.size[0], self.size[1], 0,GL_RGB, GL_UNSIGNED_BYTE, 0)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self.texture, 0)
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT);
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            pymt_logger.error('error in framebuffer activation')

    def __del__(self):
        glDeleteFramebuffersEXT(1, byref(self.framebuffer))
        if self.with_depthbuffer:
            glDeleteRenderbuffersEXT(1, byref(self.depthbuffer))

    def bind(self):
        Fbo.fbo_stack.append(self.framebuffer)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

    def release(self):
        if self.push_viewport:
            glPopAttrib()
        Fbo.fbo_stack.pop()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, Fbo.fbo_stack[-1])


class SoftwareFbo(AbstractFbo):
    '''OpenGL Framebuffer, software implementation.

    .. warning::
        Poor performance, but you can use it in hardware don't support real
        Fbo extensions...

    '''
    def __init__(self, **kwargs):
        super(SoftwareFbo, self).__init__(**kwargs)
        self.texture = Texture.create(self.size[0], self.size[1])
        self.oldtexture = pyglet.image.get_buffer_manager().get_color_buffer().get_texture()

        # Hack to initialize a empty buffer.
        self.bind()
        self.release()


    def bind(self):

        # Save current buffer
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        glBindTexture(GL_TEXTURE_2D, self.oldtexture.id)
        buffer.blit_to_texture(GL_TEXTURE_2D, 0, 0, 0, 0)

        # Push current attrib
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_TEST | GL_STENCIL_BUFFER_BIT)
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_STENCIL_TEST)

        # Save viewport if asked
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

        # Draw old Framebuffer
        set_color(1,1,1)
        drawTexturedRectangle(self.texture, size=self.size)

    def release(self):
        # Restore viewport
        if self.push_viewport:
            glPopAttrib()

        # Copy current buffer into fbo texture
        glBindTexture(self.texture.target, self.texture.id)
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        glReadBuffer(buffer.gl_buffer)
        glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, self.size[0], self.size[1])

        # Restore old buffer
        glPushMatrix()
        glLoadIdentity()
        set_color(1,1,1)
        drawTexturedRectangle(self.oldtexture, size=(self.oldtexture.width,
                                                     self.oldtexture.height))
        glPopMatrix()

        glPopAttrib()


import os
if os.path.basename(sys.argv[0]).startswith('sphinx'):
    # Bad hack for sphinx
    # He don't like when Fbo is announced in __all__,
    # and not defined in source
    Fbo = HardwareFbo
else:
    # Check if Fbo is supported by gl
    from . import pymt_config
    if not 'GL_EXT_framebuffer_object' in gl_info.get_extensions():
        pymt_config.set('graphics', 'fbo', 'software')

    if not os.path.basename(sys.argv[0]).startswith('sphinx'):
        # decide what to use
        if pymt_config.get('graphics', 'fbo') == 'hardware':
            pymt_logger.info('Fbo will use hardware Framebuffer')
            Fbo = HardwareFbo
        else:
            pymt_logger.info('Fbo will use software Framebuffer')
            Fbo = SoftwareFbo
