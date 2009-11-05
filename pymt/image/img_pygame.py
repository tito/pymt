'''
Pygame: Pygame image loader
'''

__all__ = ('ImageLoaderPygame', )

from . import ImageLoaderBase, ImageData
from ..logger import pymt_logger

try:
    import pygame
except:
    raise

class ImageLoaderPygame(ImageLoaderBase):
    '''Image loader based on PIL library'''

    @staticmethod
    def extensions():
        '''Return accepted extension for this loader'''
        # retrieve from http://www.pygame.org/docs/ref/image.html
        return ('jpg', 'png', 'gif', 'bmp', 'pcx', 'tga', 'tiff', 'tif', 'lbm',
               'pbm', 'ppm', 'xpm')

    def load(self, filename):
        pymt_logger.debug('Load <%s>' % filename)
        try:
            im = pygame.image.load(filename)
        except:
            pymt_logger.warning('Unable to load image <%s>' % filename)
            raise

        mode = ''
        if im.get_bytesize() == 3:
            mode = 'RGB'
        elif im.get_bytesize() == 4:
            mode = 'RGBA'

        # image loader work only with rgb/rgba image
        if mode not in ('RGB', 'RGBA'):
            try:
                imc = im.convert(32)
            except:
                pymt_logger.warning(
                    'Unable to convert image <%s> to RGBA (was %s)' %
                    filename, im.mode)
                raise
            im = imc

        # update internals
        self.filename = filename
        data = pygame.image.tostring(im, mode, True)
        return ImageData(im.get_width(), im.get_height(),
            mode, data)


