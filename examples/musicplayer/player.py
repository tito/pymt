from pymt import *
from mutagen.id3 import ID3
from cStringIO import StringIO
import glob
#change it to your mp3 folder which has mp3's with album art, lots of error checking to be done. this code is not perfect at all
# Message for xela:
file_list = glob.glob('F:\\Love Songs\\*.mp3') 
list = []
for file in file_list:
    f=ID3(file)
    list.append(f["TIT2"])



class fileList(MTKineticScrollText):
    def __init__(self, **kwargs):
        global list
        kwargs.setdefault('pos', (0,0))
        kwargs.setdefault('size', (200,400))
        kwargs.setdefault('items', list)
        kwargs.setdefault('font_size', 10)
        super(fileList, self).__init__(**kwargs)                

    def on_item_select(self,v):
        print v      
       
class MusicPlayer(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        super(MusicPlayer, self).__init__(**kwargs)  
        mms = fileList(pos=(10,10))
        self.add_widget(mms,side='back')
        self.coverart = CoverArt(pos=(10,10))
        self.add_widget(self.coverart,side='front')
        self.width =  self.coverart.width+20
        self.height =  self.coverart.height+20
        mms.height = self.coverart.height-10
        mms.width = self.coverart.width-10
        self.fbut = FlipButton(pos=(self.width-25,0))
        self.add_widget(self.fbut,side='front')
        self.add_widget(self.fbut,side='back')
        
class FlipButton(MTButton):
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '~')
        kwargs.setdefault('size', (25,25))
        kwargs.setdefault('pos', (0,0))
        kwargs.setdefault('color', (0.5,0.5,0.5,1))
        super(FlipButton, self).__init__(**kwargs) 
    
    def on_press(self,touchID, x, y):
        self.parent.flip()
        
class CoverArt(MTWidget):
    def __init__(self, **kwargs):
        global f
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('scale', 0.5)
        super(CoverArt, self).__init__(**kwargs)
        for frame in f.getall("APIC"):
            self.img                 = pyglet.image.load('Default.jpg', file=StringIO(frame.data))
        try:
            self.image          = pyglet.sprite.Sprite(self.img)
        except AttributeError:
            self.img                 = pyglet.image.load('Default.jpg')
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
    w.add_widget(MusicPlayer(size=(210,410)))
    runTouchApp()