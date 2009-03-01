from pymt import *
from mutagen.id3 import ID3
from cStringIO import StringIO

class CoverArt(MTWidget):
    def __init__(self, **kwargs):
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('scale', 1.0)
        super(CoverArt, self).__init__(**kwargs)
        f = ID3('test.mp3')
        for frame in f.getall("APIC"):
            self.img                 = pyglet.image.load('unknown.jpg', file=StringIO(frame.data))
        self.image          = pyglet.sprite.Sprite(self.img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.size           = (self.image.width, self.image.height)

    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.size           = (self.image.width, self.image.height)
        self.image.draw()
        
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1.0), fullscreen=True)
    w.add_widget(CoverArt())
    runTouchApp()