'''
Graphx: simplification of opengl pritimives
'''

from __future__ import with_statement

__all__ = [
    # settings
    'set_brush', 'set_brush_size',
    'set_texture', 'get_texture_id', 'get_texture_target',
    # draw
    'paintLine',
]

from pyglet import *
from pyglet.gl import *
from pyglet.image import Texture, TextureRegion
from pyglet.graphics import draw
from pyglet.text import Label
from ..logger import pymt_logger
import math, os

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


def get_texture_id(texture):
    '''Return the openid of texture'''
    if isinstance(texture, TextureRegion):
        return texture.owner.id
    elif isinstance(texture, Texture):
        return texture.id
    else:
        return texture

def get_texture_target(texture):
    '''Return the target of texture. If none, return GL_TEXTURE_2D'''
    if isinstance(texture, TextureRegion):
        return texture.owner.target
    elif isinstance(texture, Texture):
        return texture.target
    else:
        return GL_TEXTURE_2D

def set_texture(texture, target=None):
    '''Same as glBindTexture, except he can take integer/long or
    Texture/TextureRegion'''
    if target is None:
        target = get_texture_target(texture)
    glBindTexture(target, get_texture_id(texture))

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
        set_texture(_brush_texture.id, target=_brush_texture.target)
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

