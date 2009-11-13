'''
Texture: abstraction to handle GL texture, and region
'''

__all__ = ('Texture', 'TextureRegion')

import re
from OpenGL.GL import *
from OpenGL.GL.NV.texture_rectangle import *
from OpenGL.GL.ARB.texture_rectangle import *
from OpenGL.extensions import hasGLExtension

# for a specific bug in 3.0.0, about deletion of framebuffer.
# same hack as FBO :(
OpenGLversion = tuple(int(re.match('^(\d+)', i).groups()[0]) for i in OpenGL.__version__.split('.'))
if OpenGLversion < (3, 0, 1):
    try:
        import numpy
        have_numpy = True
    except:
        have_numpy = False


def _nearest_pow2(v):
    # From http://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    # Credit: Sean Anderson
    v -= 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    return v + 1

def _is_pow2(v):
    # http://graphics.stanford.edu/~seander/bithacks.html#DetermineIfPowerOf2
    return (v & (v - 1)) == 0

class Texture(object):
    '''Handle a OpenGL texture. This class can be used to create simple texture
    or complex texture based on ImageData.'''

    __slots__ = ('tex_coords', 'width', 'height', 'target', 'id')

    def __init__(self, width, height, target, id):
        self.tex_coords = (0., 0., 1., 0., 1., 1., 0., 1.)
        self.width = width
        self.height = height
        self.target = target
        self.id = id

    def __del__(self):
        # try/except are here to prevent an error like this :
        # Exception TypeError: "'NoneType' object is not callable"
        # in <bound method Texture.__del__ of <pymt.texture.Texture
        # object at 0x3a1acb0>> ignored
        #
        # It occured only when leaving the application.
        # So, maybe numpy or pyopengl is unloaded, and have weird things happen.
        #
        try:
            if OpenGLversion < (3, 0, 1) and have_numpy:
                glDeleteTextures(numpy.array(self.id))
            else:
                glDeleteTextures(self.id)
        except:
            pass

    def flip_vertical(self):
        '''Flip tex_coords for vertical displaying'''
        a, b, c, d, e, f, g, h = self.tex_coords
        self.tex_coords = (g, h, e, f, c, d, a, b)

    def get_region(self, x, y, width, height):
        '''Return a part of the texture, from (x,y) with (width,height)
        dimensions'''
        return TextureRegion(x, y, width, height, self)

    @staticmethod
    def create(width, height, format=GL_RGBA, rectangle=False):
        '''Create a texture based on size.'''
        target = GL_TEXTURE_2D
        if rectangle:
            if _is_pow2(width) and _is_pow2(height):
                rectangle = False
            elif GL_ARB_texture_rectangle:
                target = GL_TEXTURE_RECTANGLE_ARB
            elif GL_NV_texture_rectangle:
                target = GL_TEXTURE_RECTANGLE_NV
            else:
                pymt_logger.warning('Unable to create a rectangular texture, ' +
                                    'no GL support found.')
                rectangle = False

        if rectangle:
            texture_width = width
            texture_height = height
        else:
            texture_width = _nearest_pow2(width)
            texture_height = _nearest_pow2(height)

        id = glGenTextures(1)
        glBindTexture(target, id)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexImage2D(target, 0, format, texture_width, texture_height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)

        texture = Texture(texture_width, texture_height, target, id)
        if rectangle:
            texture.tex_coords = \
                (0., 0., width, 0., width, height, 0., height)

        glFlush()

        if texture_width == width and texture_height == height:
            return texture

        return texture.get_region(0, 0, width, height)

    @staticmethod
    def create_from_data(im):
        '''Create a texture from an ImageData class'''
        if im.mode not in ('RGBA', 'RGB'):
            pymt_logger.error('Unsupported format for texture (%s)' % im.mode)
            return None

        if im.mode == 'RGBA':
            format = GL_RGBA
        else:
            format = GL_RGB

        texture = Texture.create(im.width, im.height, format)
        if texture is None:
            return None

        glTexSubImage2D(texture.target, 0, 0, 0,
                     im.width, im.height, format,
                     GL_UNSIGNED_BYTE, im.data)

        return texture

    @property
    def size(self):
        return (self.width, self.height)

    def __str__(self):
        return '<Texture size=(%d, %d)>' % self.size


class TextureRegion(Texture):
    '''Handle a region of a Texture class. Useful for non power-of-2
    texture handling.'''

    __slots__ = ('x', 'y', 'owner')

    def __init__(self, x, y, width, height, origin):
        super(TextureRegion, self).__init__(
            width, height, origin.target, origin.id)
        self.x = x
        self.y = y
        self.owner = origin

        # recalculate texture coordinate
        origin_u1 = origin.tex_coords[0]
        origin_v1 = origin.tex_coords[1]
        origin_u2 = origin.tex_coords[2]
        origin_v2 = origin.tex_coords[5]
        scale_u = origin_u2 - origin_u1
        scale_v = origin_v2 - origin_v1
        u1 = x / float(origin.width) * scale_u + origin_u1
        v1 = y / float(origin.height) * scale_v + origin_v1
        u2 = (x + width) / float(origin.width) * scale_u + origin_u1
        v2 = (y + height) / float(origin.height) * scale_v + origin_v1
        self.tex_coords = (u1, v1, u2, v1, u2, v2, u1, v2)

    def __del__(self):
        # don't use self of owner !
        pass
