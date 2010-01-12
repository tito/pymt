'''
Paint: brush, texturing...
'''



__all__ = [
    # settings
    'set_brush', 'set_brush_size',
    'set_texture', 'get_texture_id', 'get_texture_target',
    # draw
    'paintLine',
]

import os
import math
import pymt
from OpenGL.GL import *
from statement import *

_brushs_cache   = {}
_brush_filename = ''
_brush_texture  = None
_brush_size     = 10

def set_brush(sprite, size=None):
    '''Define the brush to use for paint* functions

    :Parameters:
        `sprite` : string
            Filename of image brush
        `size` : int, default to None
            Size of brush
    '''
    global _brushs_cache, _brush_size, _brush_filename, _brush_texture
    if size:
        _brush_size = size
    if not sprite in _brushs_cache:
        point_sprite_img = pymt.Image.load(sprite)
        _brush_texture = point_sprite_img.texture
        _brushs_cache[sprite] = _brush_texture
    _brush_filename = sprite
    _brush_texture = _brushs_cache[sprite]

def set_brush_size(size):
    '''Define the size of current brush

    :Parameters:
        `size` : int
            Size of brush
    '''
    global _brush_size
    _brush_size = size


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
    global _brush_texture, _brush_size
    if not _brush_texture:
        pymt.pymt_logger.warning('Graphx: No brush set to paint line, abort')
        return
    if len(points) % 2 == 1:
        raise Exception('Points list must be a pair length number (not impair)')
    kwargs.setdefault('sfactor', GL_SRC_ALPHA)
    kwargs.setdefault('dfactor', GL_ONE_MINUS_SRC_ALPHA)
    blending = GlBlending(sfactor=kwargs.get('sfactor'), dfactor=kwargs.get('dfactor'))
    with DO(blending, gx_enable(GL_POINT_SPRITE_ARB), gx_enable(_brush_texture.target)):

        # prepare env
        set_texture(_brush_texture.id, target=_brush_texture.target)
        glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
        glPointSize(_brush_size)

        # initialize outputList
        outputList = []

        # extract 4 points each 2 points
        for i in xrange(0, len(points) - 2, 2):

            # extract our 2 points
            p1 = (points[i], points[i+1])
            p2 = (points[i+2], points[i+3])

            # calculate vector and distance
            dx,dy = p2[0]-p1[0], p2[1]-p1[1]
            dist = math.sqrt(dx*dx +dy*dy)

            # determine step
            steps = numsteps
            if steps is None:
                steps = max(1, int(dist)/4)

            # construct pointList
            pointList = [0,0] * steps
            for i in xrange(steps):
                pointList[i * 2]   = p1[0] + dx* (float(i)/steps)
                pointList[i * 2 + 1] = p1[1] + dy* (float(i)/steps)

            # append to the result
            outputList += pointList

        # draw !
        if len(outputList) < 2:
            return
        with gx_begin(GL_POINTS):
            for x, y in zip(outputList[::2], outputList[1::2]):
                glVertex2f(x, y)
