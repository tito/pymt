from pyglet import *
from pymt.ui.window import *

class MTWallpaperWindow(MTWindow):

    NOREPEAT = 0
    CENTER = 1

    def __init__(self, wallpaper=None, **kargs):
        MTWindow.__init__(self, **kargs)
        self.wallpaper = wallpaper
        self.position = MTWallpaperWindow.CENTER

    def draw(self):
        MTWindow.draw(self)
        if self.position == MTWallpaperWindow.NOREPEAT:
            self.wallpaper.x, self.wallpaper.y = (0, 0)
            self.wallpaper.draw()
        elif self.position == MTWallpaperWindow.CENTER:
            self.wallpaper.x = (self.size[0] - self.wallpaper.width) / 2
            self.wallpaper.y = (self.size[1] - self.wallpaper.height) / 2
            self.wallpaper.draw()

    def _set_wallpaper(self, image):
        if not image:
            return
        try:
            img = pyglet.image.load(image)
            self._image = pyglet.sprite.Sprite(img)
        except Exception, e:
            print 'Desktop: error while loading wallpaper', e
    def _get_wallpaper(self):
        return self._image
    wallpaper = property(_get_wallpaper, _set_wallpaper)


