'''
Wallpaper window: a window with background wallpaper
'''

__all__ = ['MTWallpaperWindow']

import pyglet.image
from pyglet.gl import glClearColor
from ..logger import pymt_logger
from ..image import Image
from window import MTWindow

class MTWallpaperWindow(MTWindow):
    '''Wallpaper window can draw a wallpaper as background.

    :Parameters:
        `wallpaper` : string, default is None
            Filename of wallpaper
        `position` : const, default to MTWallpaperWindow.CENTER
            Default position of wallpaper. Can be one of :
            * MTWallpaperWindow.NOREPEAT
            * MTWallpaperWindow.CENTER
            * MTWallpaperWindow.REPEAT
            * MTWallpaperWindow.SCALE
        '''

        NOREPEAT = 0
        CENTER = 1
        REPEAT = 2
        SCALE = 3

        def __init__(self, **kwargs):
            kwargs.setdefault('wallpaper', None)
        kwargs.setdefault('position', MTWallpaperWindow.CENTER)
        super(MTWallpaperWindow, self).__init__(**kwargs)
        self.wallpaper  = kwargs.get('wallpaper')
        self.position   = kwargs.get('position')

    def draw(self):
        glClearColor(0,0,0,0)
        self.clear()
        if self.position == MTWallpaperWindow.NOREPEAT:
            super(MTWallpaperWindow, self).draw()
            self.wallpaper.draw()
        elif self.position == MTWallpaperWindow.CENTER:
            super(MTWallpaperWindow, self).draw()
            self.wallpaper.x = (self.size[0] - self.wallpaper.width) / 2
            self.wallpaper.y = (self.size[1] - self.wallpaper.height) / 2
            self.wallpaper.draw()
        elif self.position == MTWallpaperWindow.REPEAT:
            r_x = float(self.size[0]) / self.wallpaper.width
            r_y = float(self.size[1]) / self.wallpaper.height
            if int(r_x) != r_x:
                r_x = int(r_x) + 1
            if int(r_y) != r_y:
                r_y = int(r_y) + 1
            for x in range(0, int(r_x)):
                for y in range(0, int(r_y)):
                    self.wallpaper.x = x * self.wallpaper.width
                    self.wallpaper.y = y * self.wallpaper.height
                    self.wallpaper.draw()
        elif self.position == MTWallpaperWindow.SCALE:
            self.wallpaper.size = self.size
            self.wallpaper.draw()

    def _set_wallpaper(self, image):
        if not image:
            return
        try:
            self._image = Image(image)
        except Exception, e:
            pymt_logger.error('error while loading wallpaper : %s', e)
    def _get_wallpaper(self):
        return self._image
    wallpaper = property(_get_wallpaper, _set_wallpaper)
