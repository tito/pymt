'''
Paint: brush, texturing...
'''

__all__ = (
    # settings
    'set_brush', 'set_brush_size',
    'set_texture', 'get_texture_id', 'get_texture_target',
    # draw
    'paintLine',
)

import pymt
from math import sqrt
from OpenGL.GL import GL_POINTS, GL_TEXTURE_2D, GL_SRC_ALPHA, \
        GL_ONE_MINUS_SRC_ALPHA, GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, \
        GL_TRUE, glPointSize, glVertex2f, glBindTexture, glTexEnvi
from pymt.graphx.statement import gx_enable, gx_begin, DO, GlBlending

__brushs_cache   = dict()
__brush_filename = ''
__brush_texture  = None
__brush_size     = 10

def set_brush(sprite, size=None):
    '''Define the brush to use for paint* functions

    :Parameters:
        `sprite` : string
            Filename of image brush
        `size` : int, default to None
            Size of brush
    '''
    global __brush_size, __brush_filename, __brush_texture
    if size:
        __brush_size = size
    if not sprite in __brushs_cache:
        point_sprite_img = pymt.Image.load(sprite)
        __brush_texture = point_sprite_img.texture
        __brushs_cache[sprite] = __brush_texture
    __brush_filename = sprite
    __brush_texture = __brushs_cache[sprite]

def set_brush_size(size):
    '''Define the size of current brush

    :Parameters:
        `size` : int
            Size of brush
    '''
    global __brush_size
    __brush_size = size


def get_texture_id(texture):
    '''Return the openid of texture'''
    if isinstance(texture, pymt.TextureRegion):
        return texture.owner.id
    elif isinstance(texture, pymt.Texture):
        return texture.id
    else:
        return texture

def get_texture_target(texture):
    '''Return the target of texture. If none, return GL_TEXTURE_2D'''
    if isinstance(texture, pymt.TextureRegion):
        return texture.owner.target
    elif isinstance(texture, pymt.Texture):
        return texture.target
    else:
        return GL_TEXTURE_2D

def set_texture(texture, target=None):
    '''Same as glBindTexture, except he can take integer/long or
    Texture/TextureRegion'''
    if target is None:
        target = get_texture_target(texture)
    glBindTexture(target, get_texture_id(texture))

def paintLine(points, numsteps=None, **kwargs):
    '''Paint a line with current brush
    ::

        set_brush("mybrush.png", 10)
        paintLine((0, 0, 20, 50))
        paintLine((1, 2, 1, 5, 4, 6, 8, 7))

    '''
    if not __brush_texture:
        pymt.pymt_logger.warning('Graphx: No brush set to paint line, abort')
        return
    if len(points) % 2 == 1:
        raise Exception('Points list must be a pair length number (not impair)')
    kwargs.setdefault('sfactor', GL_SRC_ALPHA)
    kwargs.setdefault('dfactor', GL_ONE_MINUS_SRC_ALPHA)
    blending = GlBlending(sfactor=kwargs.get('sfactor'),
                          dfactor=kwargs.get('dfactor'))
    with DO(blending, gx_enable(GL_POINT_SPRITE_ARB),
            gx_enable(__brush_texture.target)):

        # prepare env
        set_texture(__brush_texture.id, target=__brush_texture.target)
        glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
        glPointSize(__brush_size)

        # initialize outputList
        outputList = []

        # extract 4 points each 2 points
        for x1, y1, x2, y2 in zip(points[::2], points[1::2],
                                  points[2::2], points[3::2]):

            # calculate vector and distance
            dx, dy = x2 - x1, y2 - y1
            dist = sqrt(dx * dx + dy * dy)

            # determine step
            steps = numsteps
            if steps is None:
                steps = max(1, int(dist) / 4)

            # construct pointList
            for i in xrange(steps):
                outputList.extend([x1 + dx * (float(i) / steps),
                                   y1 + dy * (float(i) / steps)])

        # draw !
        if len(outputList) < 2:
            return
        with gx_begin(GL_POINTS):
            for x, y in zip(outputList[::2], outputList[1::2]):
                glVertex2f(x, y)
