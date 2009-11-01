'''
Texture: abstraction to handle GL texture, and region
'''

__all__ = ('Texture', )

from OpenGL.GL import *
from OpenGL.GL.NV.texture_rectangle import *
from OpenGL.GL.ARB.texture_rectangle import *
from OpenGL.extensions import hasGLExtension

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
        glDeleteTextures(self.id)

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

        glTexImage2D(texture.target, 0, format,
                     im.width, im.height, 0, format,
                     GL_UNSIGNED_BYTE, im.data)

        return texture


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


