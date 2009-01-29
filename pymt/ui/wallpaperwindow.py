from pyglet import *
from pymt.ui.window import *

class MTWallpaperWindow(MTWindow):

    NOREPEAT = 0
    CENTER = 1
    REPEAT = 2

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
            self.wallpaper.x, self.wallpaper.y = (0, 0)
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
