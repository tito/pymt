'''
Image: handle loading of images
'''



__all__ = ('Image', 'ImageLoader', 'ImageData')

from .. import core_register_libs
from pymt.baseobject import BaseObject
from pymt.utils import deprecated
from pymt.graphx import DO, gx_color, gx_blending, drawTexturedRectangle, set_color
from pymt.texture import Texture, TextureRegion

class ImageData(object):
    '''Container for data image : width, height, mode and data.
    ..warning ::
        Only RGB and RGBA mode are allowed.
    '''

    __slots__ = ('width', 'height', 'mode', 'data')
    _supported_modes = ('RGB', 'RGBA', 'BGR', 'BGRA')

    def __init__(self, width, height, mode, data):
        assert mode in ImageData._supported_modes
        self.width = int(width)
        self.height = int(height)
        self.mode = mode
        self.data = data

    def release_data(self):
        self.data = None


class ImageLoaderBase(object):
    '''Base to implement an image loader.'''

    __slots__ = ('_texture', '_data', 'filename', 'keep_data')

    def __init__(self, filename, keep_data=False):
        self.keep_data  = keep_data
        self.filename   = filename
        self._texture   = None
        self._data      = self.load(filename)

    def load(self, filename):
        '''Load an image'''
        return None

    def _get_width(self):
        return self._data.width
    width = property(_get_width, doc='Image width')

    def _get_height(self):
        return self._data.height
    height = property(_get_height, doc='Image height')

    def _get_size(self):
        return (self._data.width, self._data.height)
    size = property(_get_size,
                   doc='Image size (width, height)')

    def _get_texture(self):
        if self._texture is None:
            if self._data is None:
                return None
            self._texture = Texture.create_from_data(self._data)
            if not self.keep_data:
                self._data.release_data()
        return self._texture
    texture = property(_get_texture,
                      doc='Get the image texture (created on the first call)')

    @deprecated
    def get_texture(self):
        '''Retreive the texture of image
        @deprecated: use self.texture instead.'''
        return self.texture


class ImageLoader(object):
    __slots__ = ('loaders')
    loaders = []

    @staticmethod
    def register(cls):
        ImageLoader.loaders.append(cls)

    @staticmethod
    def load(filename, **kwargs):
        # extract extensions
        ext = filename.split('.')[-1].lower()
        im = None
        for loader in ImageLoader.loaders:
            if ext not in loader.extensions():
                continue
            im = loader(filename, **kwargs)
            break
        if im is None:
            raise Exception('Unsupported extension <%s>, no loader found.' % ext)
        return im


class Image(BaseObject):
    '''Load an image, and store the size and texture.

    :Parameters:
        `arg` : can be str or Texture or Image object
            A string is interpreted as a path to the image that should be loaded.
            You can also provide a texture object or an already existing image object.
            In the latter case, a real copy of the given image object will be
            returned.
        `keep_data` : bool, default to False
            Keep the image data when texture is created
        `opacity` : float, default to 1.0
            Opacity of the image
        `scale` : float, default to 1.0
            Scale of the image
        `anchor_x` : float, default to 0
            X anchor
        `anchor_y` : float, default to 0
            Y anchor
    '''

    copy_attributes = ('opacity', 'scale', 'anchor_x', 'anchor_y', '_pos',
                       '_size', 'texture', '_filename', 'color', 'texture')

    def __init__(self, arg, **kwargs):
        kwargs.setdefault('keep_data', False)

        super(Image, self).__init__(**kwargs)

        self._keep_data = kwargs.get('keep_data')
        self._filename  = None
        self.texture    = None
        self.image      = None
        self.opacity    = 1.
        self.scale      = 1.
        self.anchor_x   = 0
        self.anchor_y   = 0
        self.color      = [1, 1, 1, 1]

        if type(arg) == Image:
            for attr in Image.copy_attributes:
                self.__setattr__(attr, arg.__getattribute__(attr))
        elif type(arg) in (Texture, TextureRegion):
            self.texture    = arg.texture
            self.width      = self.texture.width
            self.height     = self.texture.height
        elif type(arg) == str:
            self.filename   = arg
        else:
            raise Exception('Unable to load image with type %s' % str(type(arg)))

        # after loading, let the user take the place
        if 'color' in kwargs:
            self.color      = list(kwargs.get('color'))
            if len(self.color) > 3:
                self.opacity    = self.color[3]
        if 'opacity' in kwargs:
            self.opacity    = kwargs.get('opacity')
        if 'scale' in kwargs:
           self.scale       = kwargs.get('scale')
        if 'anchor_x' in kwargs:
            self.anchor_x   = kwargs.get('anchor_x')
        if 'anchor_y' in kwargs:
            self.anchor_y   = kwargs.get('anchor_y')
        if 'pos' in kwargs:
            self.x, self.y  = kwargs.get('pos')
        if 'x' in kwargs:
            self.x = kwargs.get('x')
        if 'y' in kwargs:
            self.y = kwargs.get('y')

    @staticmethod
    def load(filename, **kwargs):
        '''Load an image

        :Parameters:
            `filename` : str
                Filename of the image
            `keep_data` : bool, default to False
                Keep the image data when texture is created
        '''
        kwargs.setdefault('keep_data', False)
        return Image(filename, **kwargs)

    def _get_filename(self):
        return self._filename
    def _set_filename(self, value):
        if value is None:
            return
        if value == self._filename:
            return
        self._filename = value
        self.image      = ImageLoader.load(self._filename,
                                           keep_data=self._keep_data)
        self.texture    = self.image.texture
        self.width      = self.image.width
        self.height     = self.image.height
    filename = property(_get_filename, _set_filename,
            doc='Get/set the filename of image')

    @deprecated
    def get_texture(self):
        '''Retreive the texture of image
        @deprecated: use self.texture instead.'''
        return self.texture

    def draw(self):
        '''Draw the image on screen'''
        imgpos = (int(self.x - self.anchor_x * self.scale),
                  int(self.y - self.anchor_y * self.scale))
        r, g, b = self.color[:3]
        with DO(gx_color(r, g, b, self.opacity), gx_blending):
            drawTexturedRectangle(texture=self.texture, pos=imgpos, size=(self.size[0] * self.scale, self.size[1] * self.scale))

    def read_pixel(self, x, y):
        '''For a given local x/y position, return the color at that position.

        ..warning ::
            This function can be used only with images loaded with
            keep_data=True keyword. For examples ::
                m = Image.load('

        :Parameters:
            `x` : int
                Local x coordinate of the pixel in question.
            `y` : int
                Local y coordinate of the pixel in question.
        '''
        data = self.image._data

        # can't use this fonction without ImageData
        if data.data is None:
            raise EOFError('Image data is missing, make sure that image is'
                           'loaded with keep_data=True keyword.')

        # check bounds
        x, y = int(x), int(y)
        if not (0 <= x < data.width and 0 <= y < data.height):
            raise IndexError('Position (%d, %d) is out of range.' % (x, y))

        assert data.mode in ImageData._supported_modes
        size = 3 if data.mode in ('RGB', 'BGR') else 4
        index = y * data.width * size + x * size
        raw = data.data[index:index+size]
        color = map(lambda c: ord(c) / 255.0, raw)

        # conversion for BGR->RGB, BGR->RGBA format
        if data.mode in ('BGR', 'BGRA'):
            color[0], color[2] = color[2], color[0]

        return color


def load(filename):
    '''Load an image'''
    return Image.load(filename)

# load image loaders
core_register_libs('image', (
    ('pygame', 'img_pygame'),
    ('pil', 'img_pil'),
))
